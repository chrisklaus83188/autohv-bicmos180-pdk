"""Generate the 18 transmission-gate cells: SPICE .lib bodies and Xschem
implementation schematics.  Symbols follow the repository pattern for cell
families and are generated separately by xschem/gen_tg_syms.sh.

  3 supply domains (1V8 / 3V3 / 5V0)
    x 3 impedance classes (1K / 100R / 10R, sized in 04_pvt.py)
      x 2 body options (TG = bodies to the rails, TGB = bodies on pins)

Every cell carries an internal inverter that makes the PMOS gate drive from the
single `en` input.  The inverter of one class is the pass pair of the class
below it, so the family is one geometry scaled by ten.

Port order
  TG_<class>_<dom>    a b en vdd gnd
  TGB_<class>_<dom>   a b en bn bp vdd gnd
"""
from pathlib import Path

import tg_lib as T

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CELLS = HERE / "cells"
XS = REPO / "xschem" / "transmission_gates"
CELLS.mkdir(exist_ok=True)
XS.mkdir(parents=True, exist_ok=True)

RATIO = 2.5
DOMTAG = {"1v8": "1V8", "3v3": "3V3", "5v0": "5V0"}
CLASSES = ["1K", "100R", "10R"]
NOMINAL = {"1K": "1 kohm", "100R": "100 ohm", "10R": "10 ohm"}

# pass-pair total drawn widths, from 04_pvt.py
WPASS = {
    "1v8": {"1K": (4.0, 10.0), "100R": (40.0, 100.0), "10R": (400.0, 1000.0)},
    "3v3": {"1K": (4.6, 11.5), "100R": (46.0, 115.0), "10R": (460.0, 1150.0)},
    "5v0": {"1K": (8.4, 21.0), "100R": (84.0, 210.0), "10R": (840.0, 2100.0)},
}


def inv_w(dom, cls):
    """Internal inverter: one tenth of the pass pair, floored at the fab minimum."""
    wn, wp = WPASS[dom][cls]
    d = T.DOMAINS[dom]
    return max(d["Wmin"], wn / 10.0), max(d["Wmin"], wp / 10.0)


def wm(w, dom):
    """Drawn width -> (per-finger W, M).  Fingers are kept as WIDE as the fab
    window allows: the BSIM3 narrow-width Vth term (K3/W0 at model default) is
    what degrades a switch at cold/slow, so wide fingers are the right choice."""
    return T.split_wm(w, dom)


def fmt(w, m):
    return "W=%.6gu M=%d" % (w, m)


# ---------------------------------------------------------------- .lib bodies
def cell_lib(dom, cls, bodies):
    d = T.DOMAINS[dom]
    dt = DOMTAG[dom]
    name = ("TG" if bodies == "rail" else "TGB") + "_%s_%s" % (cls, dt)
    wn, wp = WPASS[dom][cls]
    iwn, iwp = inv_w(dom, cls)
    wn_f, mn = wm(wn, dom)
    wp_f, mp = wm(wp, dom)
    iwn_f, imn = wm(iwn, dom)
    iwp_f, imp = wm(iwp, dom)
    L = d["Lmin"]
    bn, bp = ("gnd", "vdd") if bodies == "rail" else ("bn", "bp")
    ports = "a b en vdd gnd" if bodies == "rail" else "a b en bn bp vdd gnd"
    call = ("sig1 sig2 enable vdd 0" if bodies == "rail"
            else "sig1 sig2 enable 0 vdd vdd 0")
    h = [
        "* %s -- CMOS transmission gate, %g V domain, ~%s on-resistance"
        % (name, d["vdd"], NOMINAL[cls]),
        "* AutoHV BiCMOS 180 PDK | %s/%s, L = %g um, Wp/Wn = %g"
        % (d["n"], d["p"], L, RATIO),
        "*",
    ]
    if bodies == "rail":
        h += ["* Bodies are tied to the rails: NMOS body to gnd, PMOS body to vdd.",
              "* This is the shipping default.  Body effect is present and is already",
              "* included in every number in ../REPORT.md."]
    else:
        h += ["* Bodies are brought out on pins bn (NMOS) and bp (PMOS) so the caller",
              "* can bias them.  Driving bn/bp to the switch terminal removes the body",
              "* effect and lowers Ron by 1.4x (5 V) to 1.9x (1.8 V); see ../REPORT.md.",
              "* bn must never sit above, and bp never below, either switch terminal.",
              "* The internal inverter always takes its bodies from the rails."]
    h += [
        "*",
        "* Port order:  " + ports,
        '*   .include "<repo-root>/autohv_bicmos180_case.lib"',
        '*   .include "<this-dir>/%s.lib"' % name,
        "*   X1 %s %s" % (call, name),
        "*",
        "* Typical Ron %s at TT / %g V / 27 C, worst case over the input" % (NOMINAL[cls], d["vdd"]),
        "* level.  PVT envelope and the guaranteed input window: ../REPORT.md.",
        "",
        ".subckt %s %s" % (name, ports),
        "* control inverter: enb = !en  (bodies always on the rails)",
        "XINVP enb en vdd vdd %s %s L=%gu" % (d["p"], fmt(iwp_f, imp), L),
        "XINVN enb en gnd gnd %s %s L=%gu" % (d["n"], fmt(iwn_f, imn), L),
        "* pass pair",
        "XN b en  a %s %s %s L=%gu" % (bn, d["n"], fmt(wn_f, mn), L),
        "XP b enb a %s %s %s L=%gu" % (bp, d["p"], fmt(wp_f, mp), L),
        ".ends %s" % name,
        "",
    ]
    return name, "\n".join(h)


# ---------------------------------------------------------------- schematics
# autohv MOS symbol pin offsets (unrotated), netlist order d g s b
PINOFF = {"d": (20, -40), "g": (-40, 0), "s": (20, 40), "b": (20, 0)}


def place(x, y, rot, flip, pin):
    px, py = PINOFF[pin]
    if flip:
        px = -px
    if rot == 0:
        return x + px, y + py
    if rot == 1:
        return x - py, y + px
    if rot == 2:
        return x - px, y - py
    return x + py, y - px


def sch(name, dom, cls, bodies):
    d = T.DOMAINS[dom]
    wn, wp = WPASS[dom][cls]
    iwn, iwp = inv_w(dom, cls)
    wn_f, mn = wm(wn, dom)
    wp_f, mp = wm(wp, dom)
    iwn_f, imn = wm(iwn, dom)
    iwp_f, imp = wm(iwp, dom)
    L = d["Lmin"]
    bn, bp = ("gnd", "vdd") if bodies == "rail" else ("bn", "bp")
    o = ["v {xschem version=3.4.8RC file_version=1.3}", "G {}", "K {}", "V {}",
         "S {}", "E {}",
         "T {%s} 560 170 0 0 0.6 0.6 {}" % name,
         "T {~%s at TT / %g V / 27 C, worst case over the input level.} "
         "560 220 0 0 0.3 0.3 {}" % (NOMINAL[cls], d["vdd"]),
         "T {Wp/Wn = %g, L = %g um. PVT envelope and input window: ../REPORT.md.} "
         "560 255 0 0 0.3 0.3 {}" % (RATIO, L),
         "T {body: circuits/transmission_gates/cells.lib is the netlist authority. "
         "Do not hand-edit;} 560 300 0 0 0.28 0.28 {}",
         "T {regenerate with circuits/transmission_gates/gen_cells.py.} "
         "560 330 0 0 0.28 0.28 {}"]
    # Power rails are named nets, not ports.  The symbols carry power by text
    # (VPWR/VGND), so exposing vdd/gnd as pins here makes xschem report a
    # symbol/schematic pin mismatch -- same convention as the logic and
    # comparator schematics, which expose only their signal pins.
    o += ["N 120 100 1400 100 {}",
          "C {lab_pin.sym} 120 100 0 0 {name=lvdd lab=vdd}",
          "N 120 900 1400 900 {}",
          "C {lab_pin.sym} 120 900 0 0 {name=lgnd lab=gnd}",
          "C {iopin.sym} 120 500 0 0 {name=pa lab=a sim_pinnumber=1}",
          "C {iopin.sym} 1400 500 0 0 {name=pb lab=b sim_pinnumber=2}",
          "C {ipin.sym} 120 300 0 0 {name=pen lab=en sim_pinnumber=3}"]
    if bodies != "rail":
        o += ["C {ipin.sym} 120 660 0 0 {name=pbn lab=bn sim_pinnumber=4}",
              "C {ipin.sym} 120 740 0 0 {name=pbp lab=bp sim_pinnumber=5}"]

    def dev(symname, x, y, rot, flip, inst, w, m, nets):
        o.append("C {autohv/%s.sym} %d %d %d %d {name=%s W=%.6gu L=%gu M=%d}"
                 % (symname, x, y, rot, flip, inst, w, L, m))
        for pin, net in nets.items():
            px, py = place(x, y, rot, flip, pin)
            o.append("C {lab_pin.sym} %d %d 0 0 {name=l%s%s lab=%s}"
                     % (px, py, inst, pin, net))

    dev(d["p"], 400, 240, 2, 1, "XINVP", iwp_f, imp,
        {"d": "enb", "g": "en", "s": "vdd", "b": "vdd"})
    dev(d["n"], 400, 700, 0, 0, "XINVN", iwn_f, imn,
        {"d": "enb", "g": "en", "s": "gnd", "b": "gnd"})
    dev(d["n"], 1000, 340, 0, 0, "XN", wn_f, mn,
        {"d": "b", "g": "en", "s": "a", "b": bn})
    dev(d["p"], 1000, 640, 0, 0, "XP", wp_f, mp,
        {"d": "b", "g": "enb", "s": "a", "b": bp})
    o += ["T {* control inverter: enb = !en} 200 470 0 0 0.4 0.4 {}",
          "T {* pass pair: a <-> b} 790 470 0 0 0.4 0.4 {}"]
    return "\n".join(o) + "\n"


# ---------------------------------------------------------------- emit
if __name__ == "__main__":
    made = []
    for dom in ("1v8", "3v3", "5v0"):
        for cls in CLASSES:
            for bodies in ("rail", "pins"):
                name, body = cell_lib(dom, cls, bodies)
                (CELLS / (name + ".lib")).write_text(body, newline="\n")
                (XS / (name + ".sch")).write_text(sch(name, dom, cls, bodies),
                                                  newline="\n")
                made.append(name)

    bundle = [
        "* AutoHV BiCMOS 180 PDK -- CMOS transmission-gate (analog switch) cell library",
        "*",
        "* 18 cells = 3 supply domains x 3 impedance classes x 2 body options.",
        "*",
        "*   TG_<class>_<dom>    bodies tied to the rails (NMOS->gnd, PMOS->vdd)",
        "*                       ports: a b en vdd gnd",
        "*   TGB_<class>_<dom>   bodies brought out on pins bn / bp",
        "*                       ports: a b en bn bp vdd gnd",
        "*",
        "*   <class> = 1K / 100R / 10R   (typical Ron at TT, nominal supply, 27 C,",
        "*                                worst case over the input level)",
        "*   <dom>   = 1V8 / 3V3 / 5V0",
        "*",
        "* Every cell contains its own inverter, so only `en` is driven; enb is made",
        "* inside.  Wp/Wn = 2.5 and L = Lmin throughout.  Sizing method, PVT envelope",
        "* and the guaranteed input window per cell are in REPORT.md.",
        "*",
        "* Usage:",
        '*   .include "<repo-root>/autohv_bicmos180_case.lib"',
        '*   .include "<repo-root>/circuits/transmission_gates/cells.lib"',
        "*   X1 sig1 sig2 sel vdd 0 TG_100R_3V3",
        "", ""]
    for dom in ("1v8", "3v3", "5v0"):
        bundle.append("* ---- %g V domain ----" % T.DOMAINS[dom]["vdd"])
        for cls in CLASSES:
            for pre in ("TG", "TGB"):
                bundle.append('.include "cells/%s_%s_%s.lib"' % (pre, cls, DOMTAG[dom]))
        bundle.append("")
    (HERE / "cells.lib").write_text("\n".join(bundle), newline="\n")

    print("wrote %d cells -> cells/*.lib, cells.lib" % len(made))
    print("wrote %d schematics -> xschem/transmission_gates/ "
          "(symbols: bash xschem/gen_tg_syms.sh)" % len(made))
    for n in made:
        print("  " + n)
