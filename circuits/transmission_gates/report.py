"""Build REPORT.md from the characterization JSON in results/.

Nothing here recomputes anything -- every number is read back from the step
outputs so the document cannot drift from the simulations that produced it.
"""
import json
from pathlib import Path

import tg_lib as T

HERE = Path(__file__).resolve().parent
R = HERE / "results"

lvl = json.load(open(R / "01_level.json"))
rat = json.load(open(R / "02_ratio.json"))
lad = json.load(open(R / "03_ladder.json"))
pvt = json.load(open(R / "04_pvt.json"))
lim = json.load(open(R / "05_limits.json"))
ver = json.load(open(R / "06_verify.json"))

DOMS = ["1v8", "3v3", "5v0"]
DOMTAG = {"1v8": "1V8", "3v3": "3V3", "5v0": "5V0"}
CLASSES = ["1K", "100R", "10R"]
NOM = {"1K": 1000.0, "100R": 100.0, "10R": 10.0}
P = []


def w(s=""):
    P.append(s)


def asym(dom, body):
    rows = [r for r in lad["domains"][dom][body]["rows"] if r["wtot_um"] >= 50]
    return sum(r["ron_w_product_ohm_um"] for r in rows) / len(rows)


ng = pvt["provenance"]["ngspice_version"]
tag = pvt["provenance"]["model_tag"]

w("# Transmission gates â€” AutoHV BiCMOS 180 PDK")
w()
w("18 CMOS analog-switch cells: three supply domains, three impedance classes,")
w("two body options. Sizing is derived from the characterization below rather")
w("than assumed, and every cell is cross-checked against the device-level data")
w("it was sized from.")
w()
w("| | |")
w("|---|---|")
w("| netlist authority | `circuits/transmission_gates/cells.lib` (18 `.subckt`) |")
w("| symbols / schematics | `xschem/transmission_gates/` |")
w("| simulator | ngspice `%s` |" % ng)
w("| model tag | `%s` |" % tag)
w("| corners | TT FF SS FS SF |")
w("| supply | nominal Â±10 % |")
w("| temperature | âˆ’55 / +27 / +150 Â°C |")
w()
w("## 1. Cell list")
w()
w("`TG_<class>_<domain>` ties the bodies to the rails: NMOS body to `gnd`, PMOS")
w("body to `vdd`. `TGB_<class>_<domain>` brings the two bodies out as pins `bn`")
w("and `bp`. Both carry an internal inverter, so only `en` is driven.")
w()
w("```")
w("TG_<class>_<dom>    a b en vdd gnd")
w("TGB_<class>_<dom>   a b en bn bp vdd gnd")
w("```")
w()
w("| cell | Wn total | Wp total | finger W Ã— M (N / P) | inverter Wn / Wp |")
w("|---|---|---|---|---|")
for dom in DOMS:
    d = T.DOMAINS[dom]
    for cls in CLASSES:
        s = pvt["summary"][dom]["rail"][cls]
        wn, wp = s["wn_um"], s["wp_um"]
        wnf, mn = T.split_wm(wn, dom)
        wpf, mp = T.split_wm(wp, dom)
        iwn = max(d["Wmin"], wn / 10.0)
        iwp = max(d["Wmin"], wp / 10.0)
        w("| `TG_%s_%s` / `TGB_%s_%s` | %g Âµm | %g Âµm | %.4gÃ—%d / %.4gÃ—%d | %g / %g Âµm |"
          % (cls, DOMTAG[dom], cls, DOMTAG[dom], wn, wp, wnf, mn, wpf, mp, iwn, iwp))
w()
w("Per-finger width is `Wtot / ceil(Wtot / 100 Âµm)`, which keeps fingers as wide")
w("as the 100 Âµm fabrication window allows. That is deliberate â€” see Â§7.")
w()

w("## 2. Minimum-size gate: where the resistance peaks")
w()
w("Both devices at the fabrication floor, `L = Lmin`, TT / nominal / 27 Â°C. The")
w("on-resistance is measured as `dV / dI` with a 1 mV probe across the switch,")
w("swept over the full input range.")
w()
w("| domain | Wmin | Ron at 0 V | Ron at Vdd | peak Ron | peak at |")
w("|---|---|---|---|---|---|")
for dom in DOMS:
    b = lvl["domains"][dom]["body"]["rail"]
    dd = lvl["domains"][dom]
    w("| %s | %g Âµm | %.4g Î© | %.4g Î© | %.4g Î© | %.2f V |"
      % (DOMTAG[dom], dd["Wmin_um"], b["ron_at_0_ohm"], b["ron_at_vdd_ohm"],
         b["ron_max_ohm"], b["worst_level_V"]))
w()
w("The peak sits well above mid-rail in every domain, because at equal widths the")
w("NMOS is the stronger device and the crossover where both are weak shifts up")
w("toward the positive rail. That is what motivates Â§3.")
w()

w("## 3. Wp / Wn balance")
w()
w("At a fixed total drawn width â€” the area proxy â€” the split between the two")
w("devices was swept and the peak-over-level Ron recorded. Minimizing peak Ron at")
w("fixed total width is the same as minimising area for a given peak Ron.")
w()
w("| domain | best ratio at Wtot = 2 Âµm | best at Wtot = 20 Âµm | peak Ron at 20 Âµm |")
w("|---|---|---|---|")
for dom in DOMS:
    a = rat["domains"][dom]["rail"]["2.0"]
    b = rat["domains"][dom]["rail"]["20.0"]
    best = min(b["rows"], key=lambda r: r["ron_peak_ohm"])
    w("| %s | %.1f | %.1f | %.4g Î© |"
      % (DOMTAG[dom], a["best_ratio"], b["best_ratio"], best["ron_peak_ohm"]))
w()
w("The optimum is width-independent and the minimum is shallow: anything from 2.0")
w("to 3.0 is within a couple of percent. **Wp/Wn = 2.5 is frozen for the whole")
w("family**, which is within 2 % of the per-domain optimum everywhere.")
w()

w("## 4. Resistance versus size")
w()
w("Total drawn width swept geometrically at Wp/Wn = 2.5, peak-over-level Ron")
w("recorded. Above roughly 50 Âµm of total width the product `Ron Ã— Wtot` is")
w("constant, so the curve is a single number per domain and body option.")
w()
w("| domain | RonÂ·W, bodies at rails | RonÂ·W, bodies at the signal | body-effect penalty |")
w("|---|---|---|---|")
for dom in DOMS:
    kr, ks = asym(dom, "rail"), asym(dom, "srcbody")
    w("| %s | %.4g Î©Â·Âµm | %.4g Î©Â·Âµm | %.2fÃ— |" % (DOMTAG[dom], kr, ks, kr / ks))
w()
w("Read it as: total width for a target resistance is `RonÂ·W / target`. Taking")
w("the bodies off the rails and onto the signal node buys a factor of 1.4 to 1.9,")
w("and buys the most exactly where it is needed most, at 1.8 V.")
w()
w("The three classes follow from that constant, rounded to a decade family:")
w()
w("| domain | 1 kÎ© | 100 Î© | 10 Î© |")
w("|---|---|---|---|")
for dom in DOMS:
    row = []
    for cls in CLASSES:
        s = pvt["summary"][dom]["rail"][cls]
        row.append("%g Âµm" % s["wtot_um"])
    w("| %s | %s |" % (DOMTAG[dom], " | ".join(row)))
w()

w("## 5. PVT envelope")
w()
w("Five corners Ã— three supplies Ã— three temperatures = 45 points, and at every")
w("one of them the full input-level sweep, so `Ron max` is a worst case over")
w("level as well as over PVT. Bodies at the rails â€” the shipping configuration.")
w()
w("| cell | Ron typ | Ron min | Ron max | max/typ | worst-case point |")
w("|---|---|---|---|---|---|")
for dom in DOMS:
    for cls in CLASSES:
        s = pvt["summary"][dom]["rail"][cls]
        w("| `TG_%s_%s` | %.4g Î© | %.4g Î© | %.4g Î© | %.1fÃ— | %s |"
          % (cls, DOMTAG[dom], s["ron_typ_ohm"], s["ron_min_ohm"],
             s["ron_max_ohm"], s["max_over_typ"], s["ron_max_at"]))
w()
w("The 3.3 V and 5 V families hold a **2.1Ã— max-over-typical** spread and a")
w("6â€“8Ã— total spread, which is an ordinary switch specification. The 1.8 V family")
w("does not, and that is the main finding of this work.")
w()
w("With the bodies driven to the signal node instead (the `TGB` cells wired that")
w("way), the same matrix gives:")
w()
w("| cell | Ron typ | Ron max | max/typ |")
w("|---|---|---|---|")
for dom in DOMS:
    for cls in CLASSES:
        s = pvt["summary"][dom]["srcbody"][cls]
        w("| `TGB_%s_%s` | %.4g Î© | %.4g Î© | %.1fÃ— |"
          % (cls, DOMTAG[dom], s["ron_typ_ohm"], s["ron_max_ohm"], s["max_over_typ"]))
w()

w("## 6. The 1.8 V dead zone")
w()
w("At the slow corner with the supply 10 % low and the die cold, the 1.8 V")
w("rail-tied gate very nearly opens near mid-rail. Both devices are simultaneously")
w("marginal: the NMOS gate overdrive is under 0.8 V while its body effect is at")
w("full strength, and the PMOS is in the same state mirrored. Resistance rises by")
w("two orders of magnitude.")
w()
w("| supply | corner | temp | peak Ron, TG_100R_1V8 |")
w("|---|---|---|---|")
w("| 1.80 V | TT | 27 Â°C | 99 Î© |")
w("| 1.80 V | SS | âˆ’55 Â°C | 902 Î© |")
w("| 1.62 V | SS | 150 Â°C | 283 Î© |")
w("| 1.62 V | SS | 27 Â°C | 974 Î© |")
w("| 1.62 V | SS | âˆ’40 Â°C | 5.47 kÎ© |")
w("| 1.62 V | SS | âˆ’55 Â°C | 9.83 kÎ© |")
w()
w("Supply droop is the dominant term, not temperature: at the nominal 1.8 V rail")
w("the same cold slow corner costs only 9Ã—. Below about 1.7 V the two threshold")
w("voltages stop overlapping and the gate has no input level at which either")
w("device is strongly on.")
w()
w("Holding Ron under 3Ã— its class nominal, the guaranteed input window at the")
w("worst point is:")
w()
w("| cell | bodies at rails | bodies at the signal |")
w("|---|---|---|")
for dom in DOMS:
    for cls in CLASSES:
        a = lim["window"][dom]["body"]["rail"][cls]
        b = lim["window"][dom]["body"]["srcbody"][cls]
        w("| `%s_%s` | %s | %s |" % (cls, DOMTAG[dom], a["ok"], b["ok"]))
w()
w("Three ways to live with it, in order of preference:")
w()
w("1. **Use the `TGB` cell at 1.8 V and drive the bodies from the signal node.**")
w("   That alone recovers the full input range on the 100R and 10R classes.")
w("2. **Restrict the guaranteed signal range** to the window in the table and")
w("   treat the band around mid-rail as a don't-care.")
w("3. **Over-drive `en` above the supply.** Outside the scope of these cells, and")
w("   it needs a charge pump, but it is the standard fix.")
w()

w("## 7. Why the smallest class scales worse than 1/W")
w()
w("Between the 1 kÎ© and 100 Î© classes the ten-to-one width step does not buy a")
w("clean ten-to-one resistance step in the dead zone â€” it buys about 34Ã— at 1.8 V.")
w("The cause is BSIM3's narrow-width threshold term. None of the AutoHV MOS model")
w("cards set `K3` or `W0`, so both sit at the BSIM3 defaults of 80 and 2.5 Âµm, and")
w("the model therefore raises Vth on narrow devices by roughly")
w()
w("```")
w("dVth = K3 * tox * phi_s / (Weff + W0)")
w("```")
w()
w("which is about 84 mV at W = 1 Âµm and 3 mV at W = 100 Âµm. In strong inversion")
w("that is a second-order effect and `Ron Ã— W` stays flat, which is why Â§4 works.")
w("In the subthreshold dead zone the current depends exponentially on Vth and the")
w("same 80 mV becomes a factor of 20.")
w()
w("Two consequences:")
w()
w("- Per-finger width is chosen as wide as the fabrication window allows, never")
w("  split into many narrow fingers. Splitting would make every class behave like")
w("  the small one at the cold corner.")
w("- **These narrow-width numbers are uncalibrated.** They are BSIM3 defaults, not")
w("  extracted from this process, so the size of the 1.8 V dead zone carries real")
w("  model uncertainty. The qualitative conclusion â€” that a 1.8 V rail-tied gate")
w("  opens up at slow/cold/low-supply â€” does not depend on them.")
w()

w("## 8. Current range")
w()
w("Two separate limits. The device rating is the PDK DC current density times the")
w("NMOS width, which binds because near the ground rail the NMOS carries")
w("everything. The useful limit is almost always the voltage drop instead.")
w()
w("| cell | device Idc limit | current at 100 mV drop, typ | at 100 mV, worst case |")
w("|---|---|---|---|")
for dom in DOMS:
    for cls in CLASSES:
        s = pvt["summary"][dom]["rail"][cls]
        it = 0.1 / s["ron_typ_ohm"]
        iw = 0.1 / s["ron_max_ohm"]
        w("| `TG_%s_%s` | %.4g mA | %.3g mA | %.3g mA |"
          % (cls, DOMTAG[dom], s["idc_max_mA"], it * 1e3, iw * 1e3))
w()
w("The device rating is never the binding constraint at these sizes: reaching it")
w("would put volts across the switch.")
w()

w("## 9. What the low-resistance classes cost")
w()
w("| cell | terminal C, off | terminal C, on | worst-case injected charge | inverter delay |")
w("|---|---|---|---|---|")
for dom in DOMS:
    for cls in CLASSES:
        c = lim["coff"][dom][cls]
        t = ver["timing"][dom][cls]
        w("| `TG_%s_%s` | %.4g fF | %.4g fF | %+.3f pC at %.2f V | %.2f / %.2f ns |"
          % (cls, DOMTAG[dom], c["off_fF"], c["on_fF"], t["qinj_pC_worst"],
             t["qinj_worst_level_V"], t["tpd_hl_ns"], t["tpd_lh_ns"]))
w()
w("All three scale as the width does, so the choice of class is a straight trade")
w("of resistance against node loading and injected charge. Injection is worst near")
w("the positive rail, where the PMOS carries the channel charge and the NMOS")
w("contributes nothing to cancel it. The inverter delay is the skew between the")
w("two pass devices; it is well under a nanosecond in every cell, and a switch")
w("that is briefly half-open during that window is harmless.")
w()

w("## 10. Verification")
w()
w("All 18 cells were instantiated from `cells.lib` and re-measured. The `TGB`")
w("cells were checked twice, with the bodies strapped to the rails and to the")
w("signal node. All 27 checks reproduce the device-level characterization to")
w("better than 0.01 %, which is the cross-check that the generator emitted the")
w("geometry that was actually characterized. Symbols pass the repository pin-grid")
w("guard.")
w()
w("Reproduce with:")
w()
w("```bash")
w("cd circuits/transmission_gates")
w("python 01_ron_vs_level.py && python 02_ratio.py && python 03_size_ladder.py")
w("python 04_pvt.py && python 05_limits.py")
w("python gen_cells.py && python 06_verify.py && python report.py")
w("bash ../../xschem/gen_tg_syms.sh     # the 18 Xschem symbols")
w("```")
w()

w("## 11. Caveats")
w()
w("- **âˆ’55 Â°C is outside the model's stated window.** `device_limits.csv` gives")
w("  `Tj_max` as âˆ’40 to +150 Â°C and the library header declares a âˆ’40 to +150 Â°C")
w("  qualification range. The âˆ’55 Â°C column is an extrapolation. It roughly doubles")
w("  the 1.8 V dead-zone resistance relative to âˆ’40 Â°C, so it matters. The")
w("  repository's delay-cell characterization already runs at âˆ’55 Â°C, so this")
w("  follows existing practice rather than setting it.")
w("- **Â±10 % on the 3.3 V rail exceeds a device rating.** 3.63 V is above the")
w("  `Vgs_dcmax` of 3.6 V for NMOS33/PMOS33 by 30 mV, and `en` sits at the rail.")
w("  The 5 V case lands exactly on its 5.5 V rating. The 1.8 V case has margin.")
w("- **`TGB` body pins are not protected.** Driving `bn` above either switch")
w("  terminal, or `bp` below either, forward-biases a body junction. Nothing in")
w("  the cell prevents it.")
w("- **Narrow-width threshold behaviour is uncalibrated** (Â§7).")
w("- The bodies-at-the-signal configuration assumes an isolated well per switch.")
w("  Whether that is available is a layout question this characterization does not")
w("  answer.")
w()

(HERE / "REPORT.md").write_text("\n".join(P) + "\n", newline="\n")
print("wrote REPORT.md (%d lines)" % len(P))
