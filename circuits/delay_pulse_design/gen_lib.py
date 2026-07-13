"""Emit one file per subcircuit (cells/<NAME>.lib) from results.json, plus a
convenience bundle cells.lib that .includes all 12.
Port order for every cell:  in  out  vdd  gnd  (matches the PDK async cells)."""
import json
import dp_lib as D

DOMTAG = {"1v8": "1V8", "3v3": "3V3", "5v0": "5V0"}
METRIC = {"DLYR": "delay", "DLYF": "delay", "PHI": "pulse width",
          "PLO": "pulse width"}


def core(arch, dom, lr, cl, cw, outnode):
    n, p, Lg = dom["n"], dom["p"], dom["Lg"]
    wn, wp, wbp = dom["wn"], dom["wp"], dom["wbp"]
    up = arch in ("DLYR", "PHI")
    L = f"{Lg}u"
    s = []
    s.append(f"XI1 nIN in vdd vdd {p} W={wp}u L={L}")
    s.append(f"XI2 nIN in gnd gnd {n} W={wn}u L={L}")
    s.append(f"XR  nIN nC RPOLY_HI L={lr:.4f}u W={D.WR}u")
    s.append(f"XC  nC  gnd CMIM_HI L={cl:.4f}u W={cw:.4f}u")
    if up:
        s.append(f"XBP nC in vdd vdd {p} W={wbp}u L={L}   $ pull-up bypass (fast falling out)")
    else:
        s.append(f"XBP nC in gnd gnd {n} W={wbp}u L={L}   $ pull-down bypass (fast rising out)")
    s.append(f"XS1 s1 nC gnd gnd {n} W={wn}u L={L}")
    s.append(f"XS2 {outnode} nC s1 gnd {n} W={wn}u L={L}")
    s.append(f"XS3 s2 nC vdd vdd {p} W={wp}u L={L}")
    s.append(f"XS4 {outnode} nC s2 vdd {p} W={wp}u L={L}")
    s.append(f"XS5 vdd {outnode} s1 gnd {n} W={wn}u L={L}")
    s.append(f"XS6 gnd {outnode} s2 vdd {p} W={wp}u L={L}")
    return s


def subckt(arch, dkey, dom, r):
    lr, cl, cw = r["lr_um"], r["cl_um"], r["cw_um"]
    n, p, Lg = dom["n"], dom["p"], dom["Lg"]
    wn, wp = dom["wn"], dom["wp"]
    L = f"{Lg}u"
    name = f"{arch}_{DOMTAG[dkey]}"
    body = []
    if arch in ("DLYR", "DLYF"):
        body = core(arch, dom, lr, cl, cw, "out")
    else:
        body = core(arch, dom, lr, cl, cw, "dco")
        body.append(f"XPI1 dbar dco vdd vdd {p} W={wp}u L={L}")
        body.append(f"XPI2 dbar dco gnd gnd {n} W={wn}u L={L}")
        if arch == "PHI":   # out = in AND (NOT dco)
            body.append(f"XG1 nnd in   vdd vdd {p} W={wp}u L={L}")
            body.append(f"XG2 nnd dbar vdd vdd {p} W={wp}u L={L}")
            body.append(f"XG3 nnd in   q   gnd {n} W={wn}u L={L}")
            body.append(f"XG4 q   dbar gnd gnd {n} W={wn}u L={L}")
            body.append(f"XO1 out nnd vdd vdd {p} W={wp}u L={L}")
            body.append(f"XO2 out nnd gnd gnd {n} W={wn}u L={L}")
        else:               # PLO: out = in OR (NOT dco)
            body.append(f"XG1 p1  in   vdd vdd {p} W={wp}u L={L}")
            body.append(f"XG2 nnr dbar p1  vdd {p} W={wp}u L={L}")
            body.append(f"XG3 nnr in   gnd gnd {n} W={wn}u L={L}")
            body.append(f"XG4 nnr dbar gnd gnd {n} W={wn}u L={L}")
            body.append(f"XO1 out nnr vdd vdd {p} W={wp}u L={L}")
            body.append(f"XO2 out nnr gnd gnd {n} W={wn}u L={L}")
    head = f".subckt {name} in out vdd gnd"
    return head + "\n" + "\n".join(body) + f"\n.ends {name}\n"


HEADER = """* AutoHV BiCMOS 180 PDK -- edge-asymmetric delay & pulse-generator cell library
*
* 12 cells = 4 archetypes x 3 voltage domains (1.8 / 3.3 / 5 V).
* Every cell delivers a 20 ns delay or 20 ns pulse width at the NOMINAL corner
* (case=0 / TT, nominal supply, 27 C).  See REPORT.md / SUMMARY.md for the full
* sizing methodology, area breakdown and PVT envelope.
*
* Archetypes:
*   DLYR_<D>  rising-edge delay,  falling-edge passthrough   (non-inverting)
*   DLYF_<D>  falling-edge delay, rising-edge  passthrough   (non-inverting)
*   PHI_<D>   logic-HIGH pulse on rising edge, falling-edge passthrough
*   PLO_<D>   logic-LOW  pulse on falling edge, rising-edge  passthrough
*   <D> = 1V8 / 3V3 / 5V0
*
* Timing element: a high-sheet poly resistor (RPOLY_HI) charges a high-density
* MIM cap (CMIM_HI); a 6T Schmitt trigger restores a clean fast output edge.
* A single bypass transistor across the RC node makes one edge fast (the
* passthrough edge) while the other is RC-delayed.  Resistor and cap areas are
* balanced near the analytic minimum for a fixed RC.
*
* Port order (all cells):   in  out  vdd  gnd
*
* Usage:
*   .include "<repo-root>/autohv_bicmos180_case.lib"
*   .include "<repo-root>/circuits/delay_pulse_design/cells.lib"
*   X1 a y vdd 0 DLYR_3V3
*
* NOTE: the timing target is met at the nominal corner only; the delay/width
* tracks RC and spreads roughly -20%/+40% over the full PVT matrix (see REPORT).
"""


def cell_header(arch, dkey, dom, name):
    return (
        f"* {name} -- {D.ARCH_LONG[arch]}\n"
        f"* AutoHV BiCMOS 180 PDK | {dom['vdd']} V domain "
        f"({dom['n']}/{dom['p']}, L = {dom['Lg']} um)\n"
        f"* ~20 ns {METRIC[arch]} at the nominal corner (case=0/TT, nominal Vdd, 27 C).\n"
        f"* Methodology, area and PVT/Monte-Carlo envelope: ../REPORT.md, "
        f"../CHARACTERIZATION.md.\n"
        "*\n"
        "* Port order:  in  out  vdd  gnd\n"
        "* The calling deck must also include the PDK device library, e.g.:\n"
        '*   .include "<repo-root>/autohv_bicmos180_case.lib"\n'
        f'*   .include "<this-dir>/{name}.lib"\n'
        f"*   X1 a y vdd 0 {name}\n"
        "*\n"
        "* When several RC cells share one transient deck, add "
        "`.option method=gear maxord=2`.\n"
    )


def main():
    with open(D.WORK / "results.json") as f:
        res = json.load(f)
    cells_dir = D.WORK / "cells"
    cells_dir.mkdir(exist_ok=True)
    names = []
    for dkey in ("1v8", "3v3", "5v0"):
        dom = D.DOMAINS[dkey]
        for arch in D.ARCHES:
            name = f"{arch}_{DOMTAG[dkey]}"
            names.append(name)
            txt = cell_header(arch, dkey, dom, name) + "\n" + \
                subckt(arch, dkey, dom, res[dkey][arch])
            with open(cells_dir / f"{name}.lib", "w", newline="\n") as f:
                f.write(txt)
    print(f"wrote {len(names)} per-cell files in cells/")

    # convenience bundle: include every per-cell file
    bundle = [HEADER,
              "\n* This bundle simply includes the 12 per-cell files in cells/.",
              "* Each subcircuit also lives in its own file cells/<NAME>.lib.\n"]
    for dkey in ("1v8", "3v3", "5v0"):
        dom = D.DOMAINS[dkey]
        bundle.append(f"\n* ---- {dom['vdd']} V domain ----")
        for arch in D.ARCHES:
            name = f"{arch}_{DOMTAG[dkey]}"
            bundle.append(f'.include "cells/{name}.lib"')
    with open(D.WORK / "cells.lib", "w", newline="\n") as f:
        f.write("\n".join(bundle) + "\n")
    print("wrote cells.lib (bundle)")


if __name__ == "__main__":
    main()
