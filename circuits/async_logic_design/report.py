"""Generate the markdown design report from results.json."""
import json, async_lib as A

r=json.load(open(A.os.path.join(A.WORK,"results.json")))
DOMN={"1v8":"1.8 V (NMOS18/PMOS18)","3v3":"3.3 V (NMOS33/PMOS33)","5v0":"5.0 V (NMOS50/PMOS50)"}
ORDER=["INV","BUF","NAND2","NOR2","AND2","OR2","XOR2","XNOR2"]
PRETTY={"INV":"Inverter","BUF":"Buffer","NAND2":"NAND2","NOR2":"NOR2","AND2":"AND2",
        "OR2":"OR2","XOR2":"XOR2","XNOR2":"XNOR2"}
def ps(x): return f"{x*1e12:.0f}"
def f2(x): return f"{x:.2f}"

out=[]
def w(s=""): out.append(s)

w("# Asynchronous Logic Cell Family - AutoHV BiCMOS 180 PDK")
w()
w("Static CMOS standard-cell set (8 cells x 3 voltage domains = 24 cells), each sized "
  "for a mid-supply switching threshold with <=5 fF input-pin load, characterized across "
  "the full PVT matrix in ngspice.")
w()
w("## 1. Design approach & test conditions")
w()
w("**Devices / channel length** (drawn L fixed per voltage class):")
w()
w("| Domain | N / P device | L (um) | Nominal Vdd | Supply corners |")
w("|---|---|---|---|---|")
for dk in ("1v8","3v3","5v0"):
    d=A.DOMAINS[dk]
    vl=", ".join(f"{v:.2f}" for v in d["vlist"])
    w(f"| {dk} | {d['n']}/{d['p']} | {d['L']:.2f} | {d['vdd']:.2f} V | {vl} V |")
w()
w("**PVT matrix** (45 points per cell): 5 process corners {TT,FF,SS,FS,SF} x "
  "3 temperatures {-55, 27, 150 C} x 3 supplies (per table above).")
w()
w("**Sizing strategy.** Each cell is built in static CMOS. The P/N width ratio is tuned "
  "(via a DC ratio sweep) so the switching threshold V_M = Vdd/2 at the nominal corner "
  "(TT, 27 C, nominal Vdd). Absolute device widths are then scaled so each input pin "
  "presents <=5 fF. AND2/OR2 = NAND2/NOR2 + inverter; BUF = inverter + 3x inverter; "
  "XOR2/XNOR2 = 12-transistor static gates (two input inverters generate complementary "
  "inputs). Minimum drawn width 0.22/0.30/0.40 um (1.8/3.3/5 V).")
w()
w("**Input capacitance** is the average switching load: small-signal AC capacitance at "
  "the input pin evaluated at both rails (in=0 and in=Vdd) and averaged. Evaluating at the "
  "rails avoids Miller inflation of Cgd that occurs at the high-gain trip point, giving the "
  "load a driving stage actually sees.")
w()
w("**Switching threshold V_M** = input voltage at which the output crosses 50% of Vdd "
  "(DC sweep). Symmetric 2-input gates are measured with inputs tied. XOR2/XNOR2 cannot "
  "be measured tied (output never toggles), so each is swept on one input with the other "
  "held at 0 and at Vdd; both thresholds are reported.")
w()
w(f"**Rise/fall** = output 10%->90% (rise) and 90%->10% (fall) of Vdd, driving a "
  f"{A.CL_FF:.0f} fF load (= fanout-of-1, since each input pin is <=5 fF) with a 20 ps "
  f"input edge. Min = fastest corner, Max = slowest corner across PVT.")
w()
w("**Area.** No layout was produced; area is a transparent estimate. *Active gate area* = "
  "sum of W*L over all transistors. *Layout estimate* = (poly columns x contacted-poly "
  "pitch) x (tallest PMOS + tallest NMOS + rail/well overhead), with CPP = 0.50/0.70/0.90 "
  "um and overhead = 1.5/2.0/2.5 um for 1.8/3.3/5 V. Treat as a relative/first-order figure.")
w()

# ---- per-domain detail
for dk in ("1v8","3v3","5v0"):
    d=A.DOMAINS[dk]; vdd=d["vdd"]
    w(f"## 2.{('1v8','3v3','5v0').index(dk)+1}  {DOMN[dk]} domain")
    w()
    # sizing table
    w("### Sizing")
    w()
    w("| Cell | Wn (um) | Wp (um) | Wp/Wn | Cin (fF) | # dev |")
    w("|---|---|---|---|---|---|")
    for c in ORDER:
        info=r[dk][c]; W={k:float(v) for k,v in info["W"].items()}
        cin=max(info["caps"].values())
        if c=="BUF":
            wn=f"{W['wn1']:.2f}+{W['wn2']:.2f}"; wp=f"{W['wp1']:.2f}+{W['wp2']:.2f}"; ratio=f"{W['wp1']/W['wn1']:.1f}"
        elif c in ("AND2","OR2"):
            wn=f"{W['wn']:.2f}/{W['wni']:.2f}"; wp=f"{W['wp']:.2f}/{W['wpi']:.2f}"; ratio=f"{W['wp']/W['wn']:.1f}"
        elif c in ("XOR2","XNOR2"):
            wn=f"{W['wn']:.2f}(core)/{W['wni']:.2f}(inv)"; wp=f"{W['wp']:.2f}/{W['wpi']:.2f}"; ratio=f"{W['wp']/W['wn']:.1f}"
        else:
            wn=f"{W['wn']:.2f}"; wp=f"{W['wp']:.2f}"; ratio=f"{W['wp']/W['wn']:.1f}"
        note=" *cap-limited" if info.get("cap_limited") else ""
        w(f"| {PRETTY[c]}{note} | {wn} | {wp} | {ratio} | {cin:.2f} | {info['area']['ndev']} |")
    w()
    # results table
    w("### Results across PVT")
    w()
    w("| Cell | V_M min..max (V) | V_M (%Vdd) | t_rise min..max (ps) | t_fall min..max (ps) | Active area (um^2) | Layout est (um^2) |")
    w("|---|---|---|---|---|---|---|")
    for c in ORDER:
        info=r[dk][c]
        vmd=info["vm"]
        # pick representative cfg(s)
        cfgs=list(vmd.keys())
        def vmcell(m): return f"{m['min']:.3f}..{m['max']:.3f}"
        def frcell(m): return f"{m['fracmin']*100:.0f}..{m['fracmax']*100:.0f}%"
        tr=info["trise"]; tf=info["tfall"]
        ar=info["area"]
        if c in ("XOR2","XNOR2"):
            # two cfgs; combine ranges
            allmin=min(m["min"] for m in vmd.values()); allmax=max(m["max"] for m in vmd.values())
            fmin=min(m["fracmin"] for m in vmd.values()); fmax=max(m["fracmax"] for m in vmd.values())
            vmtxt=f"{allmin:.3f}..{allmax:.3f}"; frtxt=f"{fmin*100:.0f}..{fmax*100:.0f}%"
        else:
            m=vmd[cfgs[0]]; vmtxt=vmcell(m); frtxt=frcell(m)
        w(f"| {PRETTY[c]} | {vmtxt} | {frtxt} | {ps(tr['min'])}..{ps(tr['max'])} | "
          f"{ps(tf['min'])}..{ps(tf['max'])} | {ar['active_um2']:.2f} | {ar['layout_um2']:.2f} |")
    w()
    # worst-case conditions footnote for slowest cell
    w("<sub>V_M %Vdd = V_M as a fraction of the supply at that PVT point. "
      "XOR2/XNOR2 V_M spans both input conditions (other input = 0 and = Vdd).</sub>")
    w()

# notes
w("## 3. Notes and trade-offs")
w()
w("- **All input pins meet the <=5 fF target** (worst pin 4.1-5.0 fF). ")
w("- **NOR2 / OR2 are capacitance-limited** (marked *cap-limited). Centering V_M exactly at "
  "Vdd/2 with tied inputs needs a very wide series-PMOS stack (Wp/Wn ~ 8-17); at minimum "
  "NMOS width that pushes Cin above 5 fF. The PMOS was therefore backed off to hold Cin "
  "<=5 fF, which lands V_M a few % below mid-supply at nominal (still ~0.45-0.50 Vdd). "
  "Relaxing the 5 fF limit would allow exact centering.")
w("- **NOR2/OR2 and XOR2/XNOR2 are intrinsically slower**: the series-PMOS pull-up (NOR/OR) "
  "and the small cap-budgeted core devices feeding a 2-high stack (XOR/XNOR) limit drive. "
  "This is fundamental to a <=5 fF, mid-supply static design, not a sizing error.")
w("- **V_M tracks supply well**: across all corners/temperatures V_M stays ~0.45-0.56 of the "
  "instantaneous supply for INV/BUF/NAND/AND/XOR/XNOR; temperature drift of V_M is small "
  "(the design is close to the zero-temp-coefficient bias).")
w("- Rise/fall asymmetry (t_fall > t_rise on several cells) follows directly from the "
  "PMOS-heavy ratio required to center V_M given this PDK's |Vtp| > Vtn and lower hole "
  "mobility; the weaker NMOS makes the pull-down edge slower.")
w()
w("## 4. Files")
w("- `async_lib.py` - deck generators + ngspice driver. `async_run.py` - sizing & PVT sweep. ")
w("- `results.json` - full numeric results. `decks/` - every generated ngspice deck.")

txt="\n".join(out)
open(A.os.path.join(A.WORK,"REPORT.md"),"w",encoding="utf-8").write(txt)
print(txt)
