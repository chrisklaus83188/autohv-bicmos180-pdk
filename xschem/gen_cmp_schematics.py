#!/usr/bin/env python3
"""Generate Xschem schematics for the comparator cells.

Source of truth is circuits/comparators/comparators_all.lib -- these schematics
are for reading and descent only. The symbols carry a spice_sym_def comment so
xschem does NOT emit a .subckt from them; the netlist still comes from the .lib.

Layout is by net label rather than by routing: every device terminal gets a
lab_pin, except a source sitting on vdd/vss, which gets a short stub wire to a
rail label so the supply structure stays visible. The bulk pin is never wired --
it shares the source's x coordinate, so a wire to the rail would run straight
through the source pin and short a stacked source (this bit the logic-gate
generator).

Devices are grouped into rows following the "* --- section ---" comments in the
.lib, so the schematic reads in the same order as the netlist.

All coordinates are multiples of 10 by construction (see check_pin_grid.py).
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
LIB = HERE.parent / "circuits" / "comparators" / "comparators_all.lib"
OUT = HERE / "comparators"

# device symbol pin offsets, already transformed for the placement used below
NMOS_OFF = {"d": (20, -40), "g": (-40, 0), "s": (20, 40), "b": (20, 0)}
PMOS_OFF = {"d": (20, 40), "g": (-40, 0), "s": (20, -40), "b": (20, 0)}
NMOS_ROT, NMOS_FLIP = 0, 0
PMOS_ROT, PMOS_FLIP = 2, 1          # mirrors about X: source ends up on top

DX, DY = 280, 360                   # device cell pitch
COLS = 6
X0, Y0 = 0, 0
RAILS = ("vdd", "vss")

SUBCKT = re.compile(r"^\.subckt\s+(\S+)\s+(.*?)(?:\s+params:\s*(.*))?$", re.I)
DEV = re.compile(r"^(X\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*(.*)$")
SECT = re.compile(r"^\*\s*-+\s*(.*?)\s*-+\s*$")


def parse_lib(path):
    """Yield one dict per .subckt: name, ports, params, devices."""
    cells, cur = [], None
    section, cond = "", False
    for raw in path.read_text(errors="replace").splitlines():
        line = raw.split(";", 1)[0].rstrip()
        s = line.strip()
        m = SUBCKT.match(s)
        if m:
            cur = {"name": m.group(1), "ports": m.group(2).split(),
                   "params": m.group(3) or "", "devs": []}
            section, cond = "", False
            continue
        if s.lower().startswith(".ends"):
            if cur:
                cells.append(cur)
            cur = None
            continue
        if cur is None:
            continue
        if s.lower().startswith(".if"):
            cond = True
            continue
        if s.lower().startswith(".endif"):
            cond = False
            continue
        ms = SECT.match(raw.strip())
        if ms:
            section = ms.group(1)
            continue
        md = DEV.match(s)
        if md:
            cur["devs"].append({
                "name": md.group(1), "d": md.group(2), "g": md.group(3),
                "s": md.group(4), "b": md.group(5), "model": md.group(6),
                "params": md.group(7).strip(), "section": section, "cond": cond,
            })
    return cells


def esc(t):
    return t.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


def build(cell):
    name, devs = cell["name"], cell["devs"]
    ports = cell["ports"]
    bias = ports[5]                              # ibp_5uA or ibn_5uA
    sig_ports = [("inp", "ipin"), ("inn", "ipin"), ("out", "opin"),
                 (bias, "ipin"), ("EN", "ipin")]

    L = ["v {xschem version=3.4.5 file_version=1.2}", "G {}", "K {}", "V {}",
         "S {}", "E {}"]
    L.append(f'T {{{esc(name)}}} {X0 - 200} {Y0 - 320} 0 0 0.6 0.6 {{}}')
    L.append(f'T {{{esc("body: circuits/comparators/comparators_all.lib (authority)")}}} '
             f'{X0 - 200} {Y0 - 260} 0 0 0.3 0.3 {{}}')
    L.append(f'T {{{esc("supplies vdd/vss connect by net name, not by wire")}}} '
             f'{X0 - 200} {Y0 - 220} 0 0 0.3 0.3 {{}}')

    # ---- ports, stacked in a column left of the device array ----
    for i, (pname, ptype) in enumerate(sig_ports):
        py = Y0 - 160 + i * 40
        L.append(f'C {{{ptype}.sym}} {X0 - 200} {py} 0 0 {{name=p{i + 1} lab={pname}}}')

    # ---- devices, new row per section ----
    row, col, last = 0, 0, None
    for dv in devs:
        if dv["section"] != last:
            if last is not None:
                row += 1
                col = 0
            last = dv["section"]
            hy = Y0 + row * DY - 120
            L.append(f'T {{{esc("* " + dv["section"])}}} {X0 - 60} {hy} 0 0 0.4 0.4 {{}}')
        if col >= COLS:
            row += 1
            col = 0
            hy = Y0 + row * DY - 120
            L.append(f'T {{{esc("* " + dv["section"] + " (cont.)")}}} {X0 - 60} {hy} 0 0 0.4 0.4 {{}}')

        x, y = X0 + col * DX, Y0 + row * DY
        is_n = dv["model"].upper().startswith("N")
        off = NMOS_OFF if is_n else PMOS_OFF
        rot, flip = (NMOS_ROT, NMOS_FLIP) if is_n else (PMOS_ROT, PMOS_FLIP)

        inst = dv["name"][1:] or dv["name"]      # strip X; spiceprefix re-adds it
        attrs = f"name={inst} model={dv['model']}"
        if dv["params"]:
            # W={40u*FIN} must be escaped: a bare brace closes the attribute
            # block early and xschem drops the rest ("SKIPPING | L=... |").
            attrs += " " + esc(dv["params"])
        # symbol refs resolve against XSCHEM_LIBRARY_PATH (~/xschem_lib), not
        # against this file's directory -- "../autohv/..." does not resolve.
        L.append(f'C {{autohv/{dv["model"]}.sym}} {x} {y} {rot} {flip} {{{attrs}}}')

        cap = dv["name"] + ("  [HYSK>0 only]" if dv["cond"] else "")
        L.append(f'T {{{esc(cap)}}} {x - 60} {y - 110} 0 0 0.3 0.3 {{}}')
        if dv["params"]:
            L.append(f'T {{{esc(dv["params"])}}} {x - 60} {y + 90} 0 0 0.25 0.25 {{}}')

        for term in ("d", "g", "s", "b"):
            net = dv[term]
            ox, oy = off[term]
            px, py = x + ox, y + oy
            if term == "s" and net in RAILS:
                # stub away from the channel: NMOS source is low, PMOS source high
                ey = py + 40 if is_n else py - 40
                L.append(f"N {px} {py} {px} {ey} {{}}")
                L.append(f'C {{lab_pin.sym}} {px} {ey} 0 0 {{name=l{inst}{term} lab={net}}}')
            else:
                L.append(f'C {{lab_pin.sym}} {px} {py} 0 0 {{name=l{inst}{term} lab={net}}}')
        col += 1

    return "\n".join(L) + "\n"


def main():
    if not LIB.exists():
        print(f"missing {LIB}", file=sys.stderr)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    cells = parse_lib(LIB)
    if not cells:
        print("no .subckt found", file=sys.stderr)
        return 1
    for c in cells:
        (OUT / f"{c['name']}.sch").write_text(build(c))
        ncond = sum(1 for d in c["devs"] if d["cond"])
        extra = f"  ({ncond} conditional)" if ncond else ""
        print(f"  {c['name']}.sch   {len(c['devs'])} devices{extra}")
    print(f"{len(cells)} schematics written to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
