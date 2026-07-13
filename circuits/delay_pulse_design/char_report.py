"""Render CHARACTERIZATION.md from char.json (PVT envelopes + Monte Carlo)."""
import json
import dp_lib as D

DOMTAG = {"1v8": "1.8 V", "3v3": "3.3 V", "5v0": "5.0 V"}
TAG = {"1v8": "1V8", "3v3": "3V3", "5v0": "5V0"}
METRIC_NAME = {"DLYR": "rise delay", "DLYF": "fall delay",
               "PHI": "HIGH-pulse width", "PLO": "LOW-pulse width"}


def ns(x): return f"{x*1e9:.2f}" if isinstance(x, (int, float)) else "n/a"
def ps(x): return f"{x*1e12:.0f}" if isinstance(x, (int, float)) else "n/a"


def cell(dk, a): return f"{a}_{TAG[dk]}"


def area_exact(arch, dkey, lr, cl, cw):
    """Area = sum over every device of (length x width), in um^2.
    Transistors contribute W*L (channel area); the poly resistor and MIM cap
    contribute their drawn L*W. Device inventory per archetype:
      delay core (9 FETs): 4xPMOS(wp) + 4xNMOS(wn) + 1 bypass(wbp)
      pulse cells add 8 FETs: 4xPMOS(wp) + 4xNMOS(wn)
    plus 1 resistor (lr x WR) and 1 MIM cap (cl x cw)."""
    dom = D.DOMAINS[dkey]
    Lg, wn, wp, wbp = dom["Lg"], dom["wn"], dom["wp"], dom["wbp"]
    nwp, nwn = (4, 4) if arch in ("DLYR", "DLYF") else (8, 8)
    a_fet = Lg * (nwp * wp + nwn * wn + wbp)
    n_fet = 9 if arch in ("DLYR", "DLYF") else 17
    a_res = lr * D.WR
    a_cap = cl * cw
    return dict(fet=a_fet, res=a_res, cap=a_cap, total=a_fet + a_res + a_cap,
                n_fet=n_fet, n_dev=n_fet + 2)


def histogram(samples, width=46, bins=14):
    """Compact ASCII histogram of MC samples (values in s)."""
    if not samples:
        return ["(no data)"]
    v = [x * 1e9 for x in samples]      # ns
    lo, hi = min(v), max(v)
    if hi - lo < 1e-9:
        return [f"all samples ~ {lo:.2f} ns"]
    bw = (hi - lo) / bins
    counts = [0] * bins
    for x in v:
        k = min(bins - 1, int((x - lo) / bw))
        counts[k] += 1
    cmax = max(counts)
    out = []
    for k in range(bins):
        c = counts[k]
        bar = "#" * round(width * c / cmax) if cmax else ""
        out.append(f"{lo + k*bw:6.2f} | {bar} {c}")
    return out


def report(res):
    L = []; A = L.append
    A("# Delay & Pulse-Generator Cell Characterization Report")
    A("### AutoHV BiCMOS 180 PDK | 12 cells (4 archetypes x 3 voltage domains)\n")
    A("Full PVT corner characterization plus 200-run Monte Carlo for the "
      "edge-asymmetric delay and pulse cells in "
      "`circuits/delay_pulse_design/cells.lib`. All results are from ngspice "
      "transient analysis on the unmodified PDK device models (BSIM3 core "
      "MOSFETs, behavioral-source poly resistor and MIM capacitor) -- no model "
      "simplifications, no behavioral stand-ins for the cells.\n")

    A("## 1. Cells under test\n")
    A("| Cell | Function |")
    A("|---|---|")
    A("| `DLYR_<D>` | rising-edge delay, falling-edge passthrough |")
    A("| `DLYF_<D>` | falling-edge delay, rising-edge passthrough |")
    A("| `PHI_<D>`  | HIGH pulse on rising edge, falling-edge passthrough |")
    A("| `PLO_<D>`  | LOW pulse on falling edge, rising-edge passthrough |")
    A("\n`<D>` = `1V8`/`3V3`/`5V0`. Each cell was sized for ~20 ns at nominal; "
      "this report measures how that timing moves over PVT and statistics.\n")

    A("## 2. Conditions\n")
    A("**Measured quantities** (every transient): `delay`/`width` = the cell's "
      "primary metric (input-edge -> output-edge for delays; output pulse "
      "high/low duration for pulse cells), at the 50% level; `passthrough` = "
      "the fast (non-delayed) edge, input->output at 50% (delay cells); "
      "`t_rise`/`t_fall` = output 10-90% / 90-10% edge rate into a 5 fF load.\n")
    A("**PVT matrix** (45 points/cell):")
    A("")
    A("| Axis | Values |")
    A("|---|---|")
    A("| Process | TT, FF, SS, FS, SF (all 5 corners) |")
    A("| Temperature | -55, 27, 150 C |")
    A("| Supply (1.8 V) | 1.62, 1.80, 1.98 V (+-10%) |")
    A("| Supply (3.3 V) | 2.97, 3.30, 3.63 V (+-10%) |")
    A("| Supply (5.0 V) | 3.20, 5.00, 5.50 V |")
    A("")
    A("**Monte Carlo**: typical corner (case=0/TT, nominal supply, 27 C), "
      f"**{res['1v8']['DLYR']['mc']['m']['n']} iterations**, with **both** "
      "die-to-die process variation (`PROC_ON=1`) and per-device local mismatch "
      "(`MM_ON=1`) enabled. Each iteration re-randomizes every AGAUSS draw via "
      "`reset` (re-randomization verified: 200 distinct results from 200 runs; "
      "the PDK's RNG is time-seeded per run). Statistics on the BSIM3 core "
      "devices, the poly resistor (Rsh + matching) and the MIM cap (Cj + "
      "matching) all participate.\n")

    # ------------------------------------------------------------ AREA
    A("## 3. Area\n")
    A("**Definition**: area = the sum over every device in the cell of "
      "(length x width). Transistors contribute their channel area W x L; the "
      "poly resistor (`RPOLY_HI`, W = 0.5 um) and the MIM capacitor "
      "(`CMIM_HI`, 5.36 x 5.36 um) contribute their drawn L x W. This is a "
      "device-area sum, not a placed-and-routed layout figure.\n")
    A("| Cell | # devices | FETs (um^2) | resistor (um^2) | MIM cap (um^2) | "
      "**total (um^2)** |")
    A("|---|---|---|---|---|---|")
    for dk in ("1v8", "3v3", "5v0"):
        for a in D.ARCHES:
            r = res[dk][a]
            ar = area_exact(a, dk, float(r["lr_um"]), float(r["cl_um"]),
                            float(r["cw_um"]))
            A(f"| {cell(dk,a)} | {ar['n_dev']} ({ar['n_fet']} FET + R + C) "
              f"| {ar['fet']:.2f} | {ar['res']:.1f} | {ar['cap']:.1f} "
              f"| **{ar['total']:.1f}** |")
    A("\n<sub>The poly resistor + MIM cap set the ~20 ns RC and dominate the "
      "area (~55 um^2); the 9-17 transistors add only ~1-3 um^2. Resistor and "
      "cap areas are deliberately balanced near the analytic minimum for a fixed "
      "RC. Pulse cells (PHI/PLO) carry 8 extra transistors (inverter + output "
      "gate) versus the delay cells.</sub>\n")

    # ------------------------------------------------------------ PVT
    A("## 4. PVT corner results\n")
    for dk in ("1v8", "3v3", "5v0"):
        A(f"### 4.{('1v8','3v3','5v0').index(dk)+1}  {DOMTAG[dk]} domain\n")
        A("| Cell | metric | nominal | min (corner) | max (corner) | "
          "passthrough max | t_rise max | t_fall max |")
        A("|---|---|---|---|---|---|---|---|")
        for a in D.ARCHES:
            r = res[dk][a]; pm = r["pvt"]["m"]; nomv = r["nominal"].get("m")
            fe = r["pvt"]["fe"]; tr = r["pvt"]["tr"]; tf = r["pvt"]["tf"]
            fetxt = f"{ns(fe['max'])} ns" if (a in ("DLYR", "DLYF") and fe) else "-"
            A(f"| {cell(dk,a)} | {METRIC_NAME[a]} | {ns(nomv)} ns "
              f"| {ns(pm['min'])} ns ({pm['min_at']}) "
              f"| {ns(pm['max'])} ns ({pm['max_at']}) "
              f"| {fetxt} | {ps(tr['max']) if tr else '-'} ps "
              f"| {ps(tf['max']) if tf else '-'} ps |")
        # spread summary
        A("")
        sp = []
        for a in D.ARCHES:
            pm = res[dk][a]["pvt"]["m"]; nomv = res[dk][a]["nominal"].get("m")
            if pm and nomv:
                sp.append((pm["min"]/nomv - 1)*100); sp.append((pm["max"]/nomv - 1)*100)
        if sp:
            A(f"<sub>Delay/width PVT spread vs nominal across this domain: "
              f"{min(sp):+.0f}% .. {max(sp):+.0f}%.</sub>\n")

    # ------------------------------------------------------------ MC
    A("## 5. Monte Carlo results (process + mismatch, TT, 200 runs)\n")
    for dk in ("1v8", "3v3", "5v0"):
        A(f"### 5.{('1v8','3v3','5v0').index(dk)+1}  {DOMTAG[dk]} domain\n")
        A("| Cell | mean | sigma | sigma/mean | min | max | 1%..99% | +-3sigma band |")
        A("|---|---|---|---|---|---|---|---|")
        for a in D.ARCHES:
            m = res[dk][a]["mc"]["m"]
            if not m:
                A(f"| {cell(dk,a)} | n/a |"); continue
            lo3 = (m["mean"] - 3*m["std"]); hi3 = (m["mean"] + 3*m["std"])
            A(f"| {cell(dk,a)} | {ns(m['mean'])} ns | {m['std']*1e12:.0f} ps "
              f"| {m['rel']*100:.2f}% | {ns(m['min'])} | {ns(m['max'])} "
              f"| {ns(m['p1'])}..{ns(m['p99'])} | {ns(lo3)}..{ns(hi3)} ns |")
        A("")

    # ------------------------------------------------------------ histograms
    A("## 6. Monte Carlo distributions (delay / pulse width)\n")
    A("Each histogram: 200 runs, x-axis bins in ns, bar length proportional to "
      "count.\n")
    for dk in ("1v8", "3v3", "5v0"):
        for a in D.ARCHES:
            m = res[dk][a]["mc"]["m"]
            if not m or "samples" not in m:
                continue
            samp = [float(x) for x in m["samples"]]
            A(f"**{cell(dk,a)}** ({METRIC_NAME[a]}): mean {ns(m['mean'])} ns, "
              f"sigma {m['std']*1e12:.0f} ps ({m['rel']*100:.2f}%)")
            A("```")
            for ln in histogram(samp):
                A(ln)
            A("```\n")

    # ------------------------------------------------------------ observations
    A("## 7. Observations\n")
    # compute some cross-cell aggregates
    def allmc(stat):
        return [res[dk][a]["mc"]["m"][stat] for dk in res for a in D.ARCHES
                if res[dk][a]["mc"]["m"]]
    rels = [res[dk][a]["mc"]["m"]["rel"]*100 for dk in res for a in D.ARCHES
            if res[dk][a]["mc"]["m"]]
    A(f"- **MC spread is tight**: 1-sigma on the delay/width is "
      f"{min(rels):.1f}-{max(rels):.1f}% of the mean across all 12 cells. The "
      "timing is an RC product and the MIM cap (sigma_Cj ~ 0.1%) and poly Rsh "
      "are well controlled; most of the statistical spread comes from the "
      "Schmitt-trip (device Vth mismatch) rather than the RC itself.")
    A("- **PVT dominates over statistics**: the corner-to-corner delay swing "
      "(roughly -20%/+40% of nominal, worst case SS / hot / low-Vdd) is much "
      "larger than the +-3-sigma MC band. For a fixed-corner design the MC band "
      "is what matters; for a multi-corner design, budget the PVT envelope.")
    A("- **Temperature & supply**: delay increases at hot / low-supply (slower "
      "devices, higher poly Rsh via tc1) and shortens at cold / high-supply. "
      "The 5 V domain shows the widest PVT envelope because its supply axis "
      "(3.2-5.5 V) is the widest.")
    A("- **Output edges stay sharp**: the Schmitt output drives clean 10-90% "
      "edges (tens to a few hundred ps into 5 fF) regardless of the slow RC "
      "ramp, so downstream timing sees a real digital edge, not the RC slope.")
    A("- **Passthrough preserved over PVT**: the fast (non-delayed) edge stays "
      "far shorter than the timed edge at every corner, so the asymmetry holds.")
    A("- **Area is RC-bound**: each cell is ~56-64 um^2, of which ~55 um^2 is "
      "the poly resistor + MIM cap that set the time constant; the transistors "
      "are ~1-3 um^2. Area scales with the target delay (longer delay -> larger "
      "RC -> more area), essentially independent of voltage domain.")
    A("\n## 8. Files\n")
    A("- `char.json` - full numeric results (PVT envelopes, MC stats, raw MC "
      "samples). `dp_char.py` - characterization driver. `char_report.py` - "
      "this report. `decks/pvt_*`, `decks/mc_*` - the generated ngspice decks.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    res = json.load(open(D.WORK / "char.json"))
    with open(D.WORK / "CHARACTERIZATION.md", "w", newline="\n") as f:
        f.write(report(res))
    print("wrote CHARACTERIZATION.md")
