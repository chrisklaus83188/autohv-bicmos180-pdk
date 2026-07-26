#!/usr/bin/env python3
"""Draw the AutoHV delay / pulse cells as real transistor-level schematics.

Companion to gen_dly_syms.sh (which draws the black-box symbols). Here each
cell body is drawn device-for-device from its per-cell netlist in
circuits/delay_pulse_design/cells/<NAME>.lib -- which stays the netlist
authority, exactly as the comparator schematics track comparators_all.lib.

Topology of the delay core (DLYR/DLYF), left to right:
  in -> CMOS inverter (XI1/XI2) -> nIN -> R(RPOLY_HI) -> nC -> 6T Schmitt -> out
  with C(CMIM_HI) from nC to gnd and one bypass FET (XBP) on nC for the fast edge.
Pulse cells (PHI/PLO) add an inverter + a 2-input gate on the delayed node.

Connectivity is by net label (lab_pin) plus explicit rails/series wires; xschem
joins terminals that carry the same net name, so the drawing is correct by
construction from the parsed netlist. Reuses the grid-safe Sheet from
gen_cmp_sch_drawn.py.
"""
import pathlib
import sys

from gen_cmp_sch_drawn import Sheet, esc, xform   # grid-safe drawing primitives

HERE = pathlib.Path(__file__).resolve().parent
CELLS = HERE.parent / "circuits" / "delay_pulse_design" / "cells"
OUT = HERE / "delay_pulse"

MODELS_4 = {"NMOS18", "PMOS18", "NMOS33", "PMOS33", "NMOS50", "PMOS50"}
MODELS_2 = {"RPOLY_HI", "CMIM_HI"}
# raw pin offsets for the passive symbols (RPOLY_HI / CMIM_HI): p top, n bottom
RAW_PASSIVE = {"p": (0, -30), "n": (0, 30)}


def parse_cell(path):
    """Parse one per-cell .lib into {'ports':[...], 'devs':{inst:{...}}}.
    Handles 4-terminal MOS (d g s b) and 2-terminal R/C (p n)."""
    ports, devs = [], {}
    for raw in path.read_text(errors="replace").splitlines():
        s = raw.split("$", 1)[0].split(";", 1)[0].strip()
        if not s or s.startswith("*"):
            continue
        low = s.lower()
        if low.startswith(".subckt"):
            t = s.split()
            ports = t[2:]
            continue
        if low.startswith(".ends"):
            break
        if s[0] in "xX":
            t = s.split()
            inst = t[0]
            j = next((i for i, tok in enumerate(t)
                      if tok in MODELS_4 or tok in MODELS_2), None)
            if j is None:
                continue
            model, nodes, params = t[j], t[1:j], t[j + 1:]
            if model in MODELS_4:
                d = dict(kind="mos", model=model, d=nodes[0], g=nodes[1],
                         s=nodes[2], b=nodes[3], params=" ".join(params))
            else:
                d = dict(kind="pas", model=model, p=nodes[0], n=nodes[1],
                         params=" ".join(params))
            devs[inst] = d
    return {"ports": ports, "devs": devs}


def xname(inst):
    """cells.lib device 'XI1' -> xschem name 'I1' (spiceprefix X re-adds it)."""
    return inst[1:] if inst[:1] in "xX" else inst


# ---- layout constants ---------------------------------------------------
VDD_Y, GND_Y = 0, 800
PROW, NROW = 240, 560
PIN_NUM = {"in": 1, "out": 2, "vdd": 3, "gnd": 4}   # subckt port order


def port_once(S, x, y, net):
    """Place the interface pin for `net` exactly once (in=ipin, out=opin,
    vdd/gnd=iopin), with sim_pinnumber so the subckt ports come out
    `in out vdd gnd`. Returns True if it placed the pin this call."""
    if not hasattr(S, "_ported"):
        S._ported = set()
    if net in PIN_NUM and net not in S._ported:
        S._ported.add(net)
        kind = {"in": "ipin", "out": "opin"}.get(net, "iopin")
        S._grid(x, y); S.n += 1
        S.L.append(f"C {{{kind}.sym}} {x} {y} 0 0 "
                   f"{{name=pz{S.n} lab={net} sim_pinnumber={PIN_NUM[net]}}}")
        return True
    return False


def tap(S, x, y, net):
    """Name a wire node: place the interface pin once, else a small net label."""
    if not port_once(S, x, y, net):
        S.label(x, y, net)


def place_mos(S, dv, inst, x, y, mirror=False, vflip=False):
    return S.dev(dv, xname(inst), x, y, mirror=mirror, vflip=vflip)


def place_pas(S, dv, inst, x, y, rot=0):
    S._grid(x, y)
    at = f"name={xname(inst)}"
    if dv["params"]:
        at += " " + esc(dv["params"])
    S.L.append(f'C {{autohv/{dv["model"]}.sym}} {x} {y} {rot} 0 {{{at}}}')
    S.text(xname(inst), x + 30, y - 40, 0.22)
    px, py = xform(*RAW_PASSIVE["p"], rot, 0)
    nx, ny = xform(*RAW_PASSIVE["n"], rot, 0)
    return {"p": (x + px, y + py), "n": (x + nx, y + ny)}


VDDY, GNDY = 100, 860            # rails pulled in close (compressed sheet)


def _core(cell, S, bus_x):
    """Draw the delay core into Sheet S: input inverter -> nIN -> R -> nC bus ->
    6T Schmitt + hysteresis, all on the y=500 spine. The Schmitt output net
    (named 'out' in delay cells, 'dco' in pulse cells -- taken straight from the
    parsed devices) is carried on the y=500 bus out to x=bus_x. The caller draws
    the rails and terminates the bus (opin, or the pulse logic)."""
    D = cell["devs"]; RL = 120
    # input inverter -> nIN
    i1 = place_mos(S, D["XI1"], "XI1", 280, 280)   # PMOS: s up, d down, g left
    i2 = place_mos(S, D["XI2"], "XI2", 280, 720)   # NMOS: d up, s down, g left
    S.wire(i1["s"][0], VDDY, i1["s"][0], i1["s"][1])          # XI1.s -> vdd
    S.wire(i2["s"][0], i2["s"][1], i2["s"][0], GNDY)          # XI2.s -> gnd
    S.vline(i1["d"][0], i1["d"][1], i2["d"][1], taps=[500])   # nIN
    S.label(i1["d"][0], 500, "nIN")
    S.vline(i1["g"][0], i1["g"][1], i2["g"][1], taps=[500])   # in gate bus
    S.hline(500, RL, i1["g"][0]); port_once(S, RL, 500, "in")
    # R (horizontal) on the y=500 spine: nIN -> nC
    r = place_pas(S, D["XR"], "XR", 560, 500, rot=3)
    S.hline(500, i1["d"][0], r["p"][0])
    # nC bus -> Schmitt gate bus, taps for bypass (if any) & C
    has_bp = "XBP" in D
    S.hline(500, r["n"][0], 1120, taps=[700] + ([780] if has_bp else []) + [940])
    S.label(700, 500, "nC")
    S.vline(1120, 260, 740, taps=[420, 500, 580])            # gate bus (mid on 500)
    # bypass FET on nC (PMOS->vdd for DLYR/PHI, NMOS->gnd for DLYF/PLO); the
    # two-sided DLY cell omits it so BOTH edges see the RC delay.
    if has_bp:
        bp = D["XBP"]; b_up = bp["s"] == "vdd"
        b = place_mos(S, bp, "XBP", 760, 200 if b_up else 800)
        if b_up:
            S.wire(b["s"][0], VDDY, b["s"][0], b["s"][1])
        else:
            S.wire(b["s"][0], b["s"][1], b["s"][0], GNDY)
        S.wire(b["d"][0], b["d"][1], b["d"][0], 500)         # XBP.d -> nC bus
        S.label(b["g"][0], b["g"][1], "in")
    # MIM cap: nC -> gnd
    c = place_pas(S, D["XC"], "XC", 940, 640)
    S.wire(c["p"][0], 500, c["p"][0], c["p"][1])
    S.wire(c["n"][0], c["n"][1], c["n"][0], GNDY)
    # 6T Schmitt (vertical output column), gate midpoint on y=500
    s3 = place_mos(S, D["XS3"], "XS3", 1160, 260)
    s4 = place_mos(S, D["XS4"], "XS4", 1160, 420)
    s2 = place_mos(S, D["XS2"], "XS2", 1160, 580)
    s1 = place_mos(S, D["XS1"], "XS1", 1160, 740)
    s2mid = (s3["d"][1] + s4["s"][1]) // 2
    s1mid = (s2["s"][1] + s1["d"][1]) // 2
    S.wire(s3["s"][0], VDDY, s3["s"][0], s3["s"][1])
    S.vline(s3["d"][0], s3["d"][1], s4["s"][1], taps=[s2mid])
    S.vline(s4["d"][0], s4["d"][1], s2["d"][1], taps=[500])
    S.vline(s2["s"][0], s2["s"][1], s1["d"][1], taps=[s1mid])
    S.wire(s1["s"][0], s1["s"][1], s1["s"][0], GNDY)
    S.label(s3["d"][0], s3["d"][1], "s2")
    S.label(s2["s"][0], s2["s"][1], "s1")
    # hysteresis devices (mirrored, at the out-side stack levels)
    f6 = place_mos(S, D["XS6"], "XS6", 1360, 420, mirror=True)
    f5 = place_mos(S, D["XS5"], "XS5", 1520, 580, mirror=True)
    S.wire(f6["d"][0], f6["d"][1], f6["d"][0], GNDY)
    S.wire(f5["d"][0], VDDY, f5["d"][0], f5["d"][1])
    S.vline(f6["s"][0], s2mid, f6["s"][1])
    S.hline(s2mid, s3["d"][0], f6["s"][0])
    S.vline(f5["s"][0], f5["s"][1], s1mid)
    S.hline(s1mid, s1["d"][0], f5["s"][0])
    # Schmitt output bus (y=500) -> both hysteresis gates -> x=bus_x
    S.hline(500, s4["d"][0], bus_x, taps=[f6["g"][0], f5["g"][0]])
    S.vline(f6["g"][0], f6["g"][1], 500)
    S.vline(f5["g"][0], 500, f5["g"][1])
    S.text("* input inverter", 200, VDDY - 140, 0.4)
    S.text("* RC delay (R + MIM C)" + (" + bypass" if has_bp else " -- both edges"),
           460, VDDY - 140, 0.4)
    S.text("* Schmitt trigger + hysteresis", 1080, VDDY - 140, 0.4)


def draw_delay(cell, name):
    """Delay cell: the core drives 'out' directly."""
    edge = "XBP bypass (one fast edge)" if "XBP" in cell["devs"] \
        else "no bypass -- two-sided (both edges delayed)"
    S = Sheet(name, "body: circuits/delay_pulse_design/cells.lib (authority) | "
                    "in -> inverter -> R -> nC -> Schmitt -> out ; " + edge)
    S.hline(VDDY, 120, 1580); port_once(S, 120, VDDY, "vdd")
    S.hline(GNDY, 120, 1580); port_once(S, 120, GNDY, "gnd")
    _core(cell, S, 1680)
    port_once(S, 1680, 500, "out")
    return S


def _inv(S, D, p_inst, n_inst, x, in_net, out_net):
    """Wire a vertical CMOS inverter: PMOS top / NMOS bottom, gates=in_net (left
    bus, y=500), drains joined=out_net (right, y=500), sources to rails."""
    p = place_mos(S, D[p_inst], p_inst, x, 280)
    n = place_mos(S, D[n_inst], n_inst, x, 720)
    S.wire(p["s"][0], VDDY, p["s"][0], p["s"][1])            # PMOS.s -> vdd
    S.wire(n["s"][0], n["s"][1], n["s"][0], GNDY)            # NMOS.s -> gnd
    S.vline(p["d"][0], p["d"][1], n["d"][1], taps=[500])     # output (drains)
    S.vline(p["g"][0], p["g"][1], n["g"][1], taps=[500])     # input gate bus
    S.label(p["d"][0], 500, out_net)
    return p, n


def draw_pulse(cell, name):
    """Pulse cell: the core output is 'dco'; append an inverter (dco->dbar), a
    2-input gate (NAND2 for PHI / NOR2 for PLO combining 'in' and 'dbar'), and
    an output inverter -> 'out'. All stages wired; input signals joined by name."""
    D = cell["devs"]; arch = name.split("_")[0]
    RR = 2760
    S = Sheet(name, "body: circuits/delay_pulse_design/cells.lib (authority) | "
                    "delay core (out=dco) + inverter + 2-input gate + out inverter")
    S.hline(VDDY, 120, RR); port_once(S, 120, VDDY, "vdd")
    S.hline(GNDY, 120, RR); port_once(S, 120, GNDY, "gnd")
    _core(cell, S, 1660)
    S.label(1660, 500, "dco")

    # ---- inverter: dco -> dbar --------------------------------------------
    xp, _ = _inv(S, D, "XPI1", "XPI2", 1840, "dco", "dbar")
    S.hline(500, 1660, xp["g"][0])                          # dco bus -> XPI gate

    # ---- 2-input gate ----------------------------------------------------
    if arch == "PHI":            # NAND2: parallel PMOS + SERIES NMOS (stacked)
        g1 = place_mos(S, D["XG1"], "XG1", 2160, 280)      # PMOS in  (|| pull-up)
        g2 = place_mos(S, D["XG2"], "XG2", 2360, 280)      # PMOS dbar(|| pull-up)
        g3 = place_mos(S, D["XG3"], "XG3", 2160, 560)      # NMOS in  (series, top)
        g4 = place_mos(S, D["XG4"], "XG4", 2160, 740)      # NMOS dbar(series, bottom)
        S.wire(g1["s"][0], VDDY, g1["s"][0], g1["s"][1])   # PMOS sources -> vdd
        S.wire(g2["s"][0], VDDY, g2["s"][0], g2["s"][1])
        S.hline(g1["d"][1], g1["d"][0], g2["d"][0])        # nnd across PMOS drains
        S.vline(g1["d"][0], g1["d"][1], g3["d"][1], taps=[500])  # nnd -> g3.d
        S.vline(g3["s"][0], g3["s"][1], g4["d"][1])        # q (stacked series node)
        S.label(g3["s"][0], (g3["s"][1] + g4["d"][1]) // 2, "q")
        S.wire(g4["s"][0], g4["s"][1], g4["s"][0], GNDY)   # g4.s -> gnd
        nn, nn_x = "nnd", g1["d"][0]
        # 'in' bus (g1.g over g3.g); dbar bracket to g2.g (top) and g4.g (bottom)
        S.vline(g1["g"][0], g1["g"][1], g3["g"][1]); S.label(g1["g"][0], 420, "in")
        S.wire(1860, 500, 2000, 500)
        S.vline(2000, 180, 740, taps=[500])
        S.wire(2000, 180, g2["g"][0], 180)
        S.wire(g2["g"][0], 180, g2["g"][0], g2["g"][1])    # -> g2.g (top)
        S.wire(2000, 740, g4["g"][0], 740)                 # -> g4.g (bottom)
    else:                        # NOR2: SERIES PMOS (stacked) + parallel NMOS
        g1 = place_mos(S, D["XG1"], "XG1", 2160, 280)      # PMOS in  (series, top)
        g2 = place_mos(S, D["XG2"], "XG2", 2160, 460)      # PMOS dbar(series, bottom)
        g3 = place_mos(S, D["XG3"], "XG3", 2160, 740)      # NMOS in  (|| pull-down)
        g4 = place_mos(S, D["XG4"], "XG4", 2360, 740)      # NMOS dbar(|| pull-down)
        S.wire(g1["s"][0], VDDY, g1["s"][0], g1["s"][1])   # g1.s -> vdd
        S.vline(g1["d"][0], g1["d"][1], g2["s"][1])        # p1 (stacked series node)
        S.label(g1["d"][0], (g1["d"][1] + g2["s"][1]) // 2, "p1")
        S.wire(g3["s"][0], g3["s"][1], g3["s"][0], GNDY)   # NMOS sources -> gnd
        S.wire(g4["s"][0], g4["s"][1], g4["s"][0], GNDY)
        S.hline(g3["d"][1], g3["d"][0], g4["d"][0])        # nnr across NMOS drains
        S.vline(g2["d"][0], g2["d"][1], g3["d"][1], taps=[500])  # nnr g2.d -> g3.d
        nn, nn_x = "nnr", g2["d"][0]
        # 'in' bus (g1.g and g3.g), routed on the left around g2.g (the dbar
        # gate sitting between them); dbar bracket to g2.g (middle) and g4.g.
        ix = g1["g"][0] - 40
        S.wire(g1["g"][0], g1["g"][1], ix, g1["g"][1])
        S.vline(ix, g1["g"][1], g3["g"][1])
        S.wire(ix, g3["g"][1], g3["g"][0], g3["g"][1])
        S.label(ix, 500, "in")
        S.wire(1860, 500, 2000, 500)
        S.vline(2000, 460, 820, taps=[500])
        S.wire(2000, 460, g2["g"][0], 460)                 # -> g2.g (middle dbar PMOS)
        S.wire(2000, 820, g4["g"][0], 820)
        S.wire(g4["g"][0], 820, g4["g"][0], g4["g"][1])    # -> g4.g (bottom)
    S.label(nn_x, 500, nn)

    # ---- output inverter: nn -> out --------------------------------------
    xo, _ = _inv(S, D, "XO1", "XO2", 2560, nn, "out")
    S.hline(500, nn_x, xo["g"][0])                          # nn -> XO gate
    S.hline(500, xo["d"][0], 2680); port_once(S, 2680, 500, "out")

    S.text("* inverter (dco->dbar)", 1780, VDDY - 140, 0.4)
    S.text("* 2-input gate (in | dbar)", 2100, VDDY - 140, 0.4)
    S.text("* output inverter", 2520, VDDY - 140, 0.4)
    return S


ALL = [f"{a}_{d}" for d in ("1V8", "3V3", "5V0")
       for a in ("DLYR", "DLYF", "DLY", "PHI", "PLO")]


def main(names):
    made = 0
    for name in names:
        f = CELLS / f"{name}.lib"
        if not f.exists():
            print(f"  skip {name} (no {f})"); continue
        cell = parse_cell(f)
        arch = name.split("_")[0]
        draw = draw_delay if arch in ("DLYR", "DLYF", "DLY") else draw_pulse
        draw(cell, name).write(OUT / f"{name}.sch")
        print(f"  drew {name}.sch ({len(cell['devs'])} devices)")
        made += 1
    print(f"{made} schematic(s) written")


if __name__ == "__main__":
    args = sys.argv[1:] or ALL
    main(args)
