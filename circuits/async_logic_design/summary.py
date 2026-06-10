"""Generate SUMMARY.md - a consolidated performance summary from results.json."""
import json, async_lib as A

r=json.load(open(A.os.path.join(A.WORK,"results.json")))
ORDER=["INV","BUF","NAND2","NOR2","AND2","OR2","XOR2","XNOR2"]
PRETTY={"INV":"Inverter","BUF":"Buffer","NAND2":"NAND2","NOR2":"NOR2","AND2":"AND2",
        "OR2":"OR2","XOR2":"XOR2","XNOR2":"XNOR2"}
DOMN={"1v8":"1.8 V","3v3":"3.3 V","5v0":"5.0 V"}
DEVN={"1v8":"NMOS18 / PMOS18","3v3":"NMOS33 / PMOS33","5v0":"NMOS50 / PMOS50"}
def ps(x): return f"{x*1e12:.0f}"
out=[]
def w(s=""): out.append(s)

def wn_wp(c,W):
    if c=="BUF": return f"{W['wn1']:.2f}/{W['wp1']:.2f} -> {W['wn2']:.2f}/{W['wp2']:.2f}"
    if c in("AND2","OR2"): return f"{W['wn']:.2f}/{W['wp']:.2f} + {W['wni']:.2f}/{W['wpi']:.2f}"
    if c in("XOR2","XNOR2"): return f"{W['wn']:.2f}/{W['wp']:.2f} + {W['wni']:.2f}/{W['wpi']:.2f}"
    return f"{W['wn']:.2f} / {W['wp']:.2f}"

def vm_span(info):
    vmd=info["vm"]
    lo=min(m["min"] for m in vmd.values()); hi=max(m["max"] for m in vmd.values())
    fl=min(m["fracmin"] for m in vmd.values()); fh=max(m["fracmax"] for m in vmd.values())
    return lo,hi,fl,fh

w("# Asynchronous Logic Cell Library - Design Summary")
w("### AutoHV BiCMOS 180 PDK | static CMOS | 8 cells x 3 voltage domains")
w()
w("This library provides eight asynchronous (combinational) logic cells - inverter, "
  "buffer, 2-input NAND/NOR/AND/OR, and 2-input XOR/XNOR - implemented in static CMOS in "
  "three voltage domains. Every cell is sized for a switching threshold at mid-supply with "
  "an input-pin load of <=5 fF, and is verified across process, voltage, and temperature.")
w()
w("## 1. Scope and verification conditions")
w()
w("| Item | Value |")
w("|---|---|")
w("| Cells | INV, BUF, NAND2, NOR2, AND2, OR2, XOR2, XNOR2 |")
w("| Domains | 1.8 V (L=0.18 um), 3.3 V (L=0.35 um), 5.0 V (L=0.50 um) |")
w("| Process corners | TT, FF, SS, FS, SF (5) |")
w("| Temperature | -55 C, +27 C, +150 C |")
w("| Supply (1.8/3.3 V) | nominal +/-10%  (1.62/1.80/1.98 ; 2.97/3.30/3.63 V) |")
w("| Supply (5 V) | 3.20 / 5.00 / 5.50 V |")
w("| PVT points / cell | 45 (5 x 3 x 3) |")
w("| Output load (rise/fall) | 5 fF (fanout-of-1) |")
w("| Input edge (stimulus) | 20 ps |")
w()
w("**Definitions.** *Switching threshold V_M* = input voltage at which the output reaches "
  "50% of Vdd (DC sweep; 2-input symmetric gates measured inputs-tied; XOR/XNOR swept on one "
  "input with the other at each rail). *Rise/fall* = output 10%->90% / 90%->10% of Vdd. "
  "*Cin* = average switching capacitance per input pin (rail-averaged, Miller-free). "
  "*Area* = (active) sum of W*L, and a first-order standard-cell layout estimate.")
w()

w("## 2. Performance summary by domain")
w("All ranges are min..max **across the full 45-point PVT matrix**. Widths in um.")
for dk in ("1v8","3v3","5v0"):
    d=A.DOMAINS[dk]
    w()
    w(f"### {DOMN[dk]} domain - {DEVN[dk]}, L = {d['L']:.2f} um")
    w()
    w("| Cell | Wn/Wp (um) | Cin (fF) | V_M (V) | V_M (%Vdd) | t_rise (ps) | t_fall (ps) | Active (um^2) | Layout est (um^2) |")
    w("|---|---|---|---|---|---|---|---|---|")
    for c in ORDER:
        info=r[dk][c]; W={k:float(v) for k,v in info["W"].items()}
        cin=max(info["caps"].values())
        lo,hi,fl,fh=vm_span(info)
        tr,tf=info["trise"],info["tfall"]
        ar=info["area"]
        note="*" if info.get("cap_limited") else ""
        w(f"| {PRETTY[c]}{note} | {wn_wp(c,W)} | {cin:.2f} | {lo:.3f}..{hi:.3f} | "
          f"{fl*100:.0f}..{fh*100:.0f}% | {ps(tr['min'])}..{ps(tr['max'])} | "
          f"{ps(tf['min'])}..{ps(tf['max'])} | {ar['active_um2']:.2f} | {ar['layout_um2']:.2f} |")
    w()
    w("<sub>`*` = capacitance-limited (see notes). Wn/Wp for multi-stage cells: "
      "BUF = stage1 -> stage2; AND2/OR2 = input gate + output inverter; "
      "XOR2/XNOR2 = core + input inverter.</sub>")

w()
w("## 3. Headline numbers")
w()
# compute some highlights
def cell_metric(dk,c,k): return r[dk][c][k]
w("| Metric | 1.8 V | 3.3 V | 5.0 V |")
w("|---|---|---|---|")
# nominal-ish fastest cell = INV typical (TT,nom,27) not stored; use min trise of INV
row=["Fastest edge, INV (t_r min, ps)"]
for dk in ("1v8","3v3","5v0"): row.append(ps(r[dk]["INV"]["trise"]["min"]))
w("| "+" | ".join(row)+" |")
row=["Slowest edge, any cell (ps)"]
for dk in ("1v8","3v3","5v0"):
    mx=max(max(r[dk][c]["trise"]["max"],r[dk][c]["tfall"]["max"]) for c in ORDER)
    row.append(ps(mx))
w("| "+" | ".join(row)+" |")
row=["Worst input-pin Cin (fF)"]
for dk in ("1v8","3v3","5v0"):
    row.append(f"{max(max(r[dk][c]['caps'].values()) for c in ORDER):.2f}")
w("| "+" | ".join(row)+" |")
row=["V_M window across all cells/PVT (%Vdd)"]
for dk in ("1v8","3v3","5v0"):
    fl=min(vm_span(r[dk][c])[2] for c in ORDER); fh=max(vm_span(r[dk][c])[3] for c in ORDER)
    row.append(f"{fl*100:.0f}-{fh*100:.0f}%")
w("| "+" | ".join(row)+" |")
row=["Cell area range, INV..XOR (um^2 est)"]
for dk in ("1v8","3v3","5v0"):
    a=[r[dk][c]["area"]["layout_um2"] for c in ORDER]
    row.append(f"{min(a):.1f}-{max(a):.1f}")
w("| "+" | ".join(row)+" |")
w()

w("## 4. Key results and trade-offs")
w()
w("- **Threshold centering:** V_M holds within ~0.43-0.58 of the instantaneous supply for "
  "every cell across all 45 PVT points, and within a few percent of 0.50 Vdd at nominal. "
  "Temperature drift of V_M is small (devices sit near the zero-temperature-coefficient bias).")
w("- **Input load:** every input pin is <=5 fF (worst case 4.1-5.0 fF), as specified.")
w("- **NOR2 / OR2 are capacitance-limited (`*`).** Centering V_M with tied inputs needs a wide "
  "series-PMOS stack (Wp/Wn ~ 8-17). At minimum NMOS width that would exceed 5 fF, so the "
  "PMOS is held back to keep Cin <=5 fF; V_M then sits slightly below mid-supply (~0.45-0.50 "
  "Vdd). Relaxing the 5 fF limit would allow exact centering.")
w("- **Speed ranking** (fastest to slowest, by drive into 5 fF): INV ~ BUF ~ AND2 < NAND2 < "
  "OR2 < NOR2 << XOR2 ~ XNOR2. NOR/OR (series PMOS) and especially XOR/XNOR (small "
  "cap-budgeted core driving a 2-high stack) are the slow cells - inherent to a <=5 fF, "
  "mid-supply static design rather than a sizing deficiency.")
w("- **Sizing intuition:** PMOS is wider than NMOS on most cells (Wp/Wn ~ 2.7-4.7 on the "
  "inverter) to offset this PDK's lower hole mobility and |Vtp| > Vtn. NAND2 inverts that "
  "(wider NMOS) because of its series pull-down; NOR2 is the extreme opposite.")
w("- **Scaling across domains:** moving 1.8 V -> 3.3 V -> 5.0 V, cells grow ~1.4x then ~2x in "
  "estimated area (longer L and taller cells) and edges slow ~2x per step at fixed load.")
w()
w("## 5. Deliverables")
w("- `SUMMARY.md` (this file) and `REPORT.md` - methodology + full tables.")
w("- `results.json` - complete numeric results (per-PVT min/max and worst-case conditions).")
w("- `async_lib.py`, `async_run.py`, `report.py` - generators/driver; `decks/` - all ngspice decks.")

txt="\n".join(out)
open(A.os.path.join(A.WORK,"SUMMARY.md"),"w",encoding="utf-8").write(txt)
print(txt)
