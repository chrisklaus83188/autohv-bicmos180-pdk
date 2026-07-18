#!/usr/bin/env python3
"""Generate Xschem schematics for the AutoHV logic cells, straight from cells.lib.

For every .subckt in circuits/async_logic_design/cells.lib this emits
xschem/logic/<CELL>.sch containing the actual transistors, sizes and
connectivity, so 'e' on a gate symbol descends into its real implementation.

Layout: PMOS network in a row under the vdd rail, NMOS network in a row above
the gnd rail. Terminals tied to vdd/gnd are wired to the rails; every other
terminal carries a net label, so connectivity is exact by construction.

Interface rule (must match the symbol): only the SIGNAL ports are schematic
ports (ipin/opin). vdd/gnd are plain labels, because the symbols connect power
by text and expose signal pins only. Keeping the counts equal is what stops
xschem raising "symbol has N pins, its schematic has M pins".

Grid rule: every coordinate is a multiple of 10.
"""
import pathlib
import re
import sys

SD = pathlib.Path(__file__).resolve().parent
CELLS = SD.parent / "circuits" / "async_logic_design" / "cells.lib"
OUTDIR = SD / "logic"

# pin offsets, from the empirically determined xschem rot/flip transform
#   NMOS  rot=0 flip=0 : d top,    s bottom
#   PMOS  rot=2 flip=1 : s top,    d bottom   (source up to vdd)
NMOS_OFF = {"d": (20, -40), "g": (-40, 0), "s": (20, 40), "b": (20, 0)}
PMOS_OFF = {"d": (20, 40), "g": (-40, 0), "s": (20, -40), "b": (20, 0)}

COL = 200          # column pitch
PY, NY = -140, 140  # PMOS / NMOS row origins
VDD_Y, GND_Y = -240, 240

DEV_RE = re.compile(
    r"^X\S+\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+W=\{?\(?([-\d.eE+]+)\)?\*?1e-6\}?\s+L=(\S+)",
    re.I)


def parse_cells(path):
    cells, cur = {}, None
    for line in path.read_text().splitlines():
        s = line.strip()
        if s.lower().startswith(".subckt"):
            parts = s.split()
            cur = parts[1]
            cells[cur] = {"ports": parts[2:], "devs": []}
        elif s.lower().startswith(".ends"):
            cur = None
        elif cur and s.upper().startswith("X"):
            m = DEV_RE.match(s)
            if m:
                d, g, sN, b, model, w, l = m.groups()
                cells[cur]["devs"].append(
                    {"d": d, "g": g, "s": sN, "b": b, "model": model,
                     "W": f"{float(w):g}u", "L": l})
    return cells


def build(name, cell):
    devs = cell["devs"]
    pmos = [d for d in devs if d["model"].upper().startswith("PMOS")]
    nmos = [d for d in devs if d["model"].upper().startswith("NMOS")]
    ncol = max(len(pmos), len(nmos), 1)
    x0, x1 = -120, (ncol - 1) * COL + 120

    L = ["v {xschem version=3.4.8RC file_version=1.3}", "G {}", "K {}", "V {}", "S {}", "E {}"]
    L.append(f"T {{{name} - implementation generated from circuits/async_logic_design/cells.lib. "
             f"Do not hand-edit; regenerate with xschem/gen_logic_schematics.py}} "
             f"{x0} {VDD_Y - 90} 0 0 0.3 0.3 {{layer=4}}")

    # supply rails
    L.append(f"N {x0} {VDD_Y} {x1} {VDD_Y} {{}}")
    L.append(f"N {x0} {GND_Y} {x1} {GND_Y} {{}}")
    L.append(f"C {{lab_pin.sym}} {x0} {VDD_Y} 0 0 {{name=lvdd lab=vdd}}")
    L.append(f"C {{lab_pin.sym}} {x0} {GND_Y} 0 0 {{name=lgnd lab=gnd}}")

    def place(dev, idx, row_y, off, tag):
        ox = idx * COL
        rot, flip = (2, 1) if tag == "P" else (0, 0)
        L.append(f"C {{autohv/{dev['model']}.sym}} {ox} {row_y} {rot} {flip} "
                 f"{{name=M{tag}{idx + 1} W={dev['W']} L={dev['L']} M=1 MM_SIGMA=0}}")
        for term in ("d", "g", "s", "b"):
            net = dev[term]
            tx, ty = ox + off[term][0], row_y + off[term][1]
            # Only the SOURCE is drawn as a wire to a rail. The bulk pin shares
            # the source's x, so wiring it to the rail as well would run a wire
            # straight through the source pin and short a stacked (non-rail)
            # source such as n1/p1/m1/k1 to that rail. Bulk therefore always
            # connects by label, which is exact regardless of geometry.
            if term == "s" and net in ("vdd", "gnd"):
                rail = VDD_Y if net == "vdd" else GND_Y
                L.append(f"N {tx} {ty} {tx} {rail} {{}}")
            else:
                L.append(f"C {{lab_pin.sym}} {tx} {ty} 0 0 "
                         f"{{name=l{tag}{idx + 1}{term} lab={net}}}")

    for i, d in enumerate(pmos):
        place(d, i, PY, PMOS_OFF, "P")
    for i, d in enumerate(nmos):
        place(d, i, NY, NMOS_OFF, "N")

    # schematic ports: signal ports only (vdd/gnd stay plain labels)
    sig = [p for p in cell["ports"] if p not in ("vdd", "gnd")]
    ins = [p for p in sig if p != "out"]
    for k, p in enumerate(ins):
        L.append(f"C {{ipin.sym}} {x0 - 100} {(k - (len(ins) - 1) / 2) * 80:.0f} 0 0 "
                 f"{{name=pi{k} lab={p}}}")
    if "out" in sig:
        L.append(f"C {{opin.sym}} {x1 + 100} 0 0 0 {{name=po lab=out}}")
    return "\n".join(L) + "\n"


def main():
    cells = parse_cells(CELLS)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    n = 0
    for name, cell in sorted(cells.items()):
        if not cell["devs"]:
            print(f"  skip {name}: no devices parsed", file=sys.stderr)
            continue
        (OUTDIR / f"{name}.sch").write_text(build(name, cell))
        print(f"wrote {name}.sch  ({len(cell['devs'])} devices)")
        n += 1
    print(f"----\nTotal logic schematics: {n}")


if __name__ == "__main__":
    main()
