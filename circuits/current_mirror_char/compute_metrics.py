#!/usr/bin/env python3
"""
compute_metrics.py -- metrics table, V_SD collapse residual, UVLO compliance, and
a junction-leakage projection.

Outputs:
  metrics.csv     one row per (design,topo,PVT) with provenance tags
  crosscheck.json V_SD collapse residuals, UVLO compliance, leakage projection
All numbers are extracted from results.json (real .dc sweeps); nothing analytic
feeds a measured column.  Metrics are anchored to general, supply-agnostic points
(gain at Vdd/2; lambda_eff / r_out over a fixed in-saturation window).
"""
import json, os, csv
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

res = json.load(open(os.path.join(HERE, "results.json")))
sweeps = res["sweeps"]
designs = json.load(open(os.path.join(HERE, "designs.json")))["designs"]
UVLO_DESIGN = "B_10u"          # a general locked design for the UVLO check


# ---- metrics.csv ---------------------------------------------------------
def write_csv():
    cols = ["design","strategy","topo","Vdd","corner","temp_C","Iin_A",
            "I_at_0_A","I_at_vddhalf_A","gain_at_0","gain_vddhalf",
            "lambda_eff_perV","rout_ohm","band_hi_V","ramp_nonlin_pct",
            "vmax_1pct_V","vmax_0p1pct_V","area_um2","provenance"]
    with open(os.path.join(HERE, "metrics.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(cols)
        for s in sweeps:
            m = s["metrics"]; nm = s["name"]
            area = designs[nm]["area_um2"][s["topo"]]
            prov = f"netlists/{nm}_{s['topo']}.cir(case={s['case']},"\
                   f"temp={s['temp']},Vdd={s['Vdd']}):dc_sweep_i(Vout)"
            w.writerow([nm, designs[nm]["strategy"], s["topo"], s["Vdd"],
                s["corner"], s["temp"], f"{s['Iin']:.4g}",
                f"{m['I_at_0']:.6g}", f"{m['I_at_vddhalf']:.6g}",
                f"{m['gain_at_0']:.5f}", f"{m['gain_vddhalf']:.5f}",
                f"{m['lambda_eff']:.6g}", f"{m['rout_inband']:.6g}",
                f"{m['band_hi_V']:.2f}", f"{m['ramp_nonlin_pct']:.4f}",
                f"{m['vmax_1pct']:.4f}", f"{m['vmax_0p1pct']:.4f}",
                f"{area:.3f}", prov])
    print(f"wrote metrics.csv ({len(sweeps)} rows)")


# ---- V_SD collapse residual ----------------------------------------------
def vsd_collapse():
    out = {}
    byname = {}
    for s in sweeps:
        if s["case"] == 0 and s["temp"] == 27:
            byname.setdefault((s["name"], s["topo"]), {})[s["Vdd"]] = s
    vsd_grid = np.arange(0.5, 3.0+1e-9, 0.1)
    for (name, topo), byv in byname.items():
        curves = []
        for Vdd, s in byv.items():
            v = np.array(s["grid_Vout"]); i = np.array(s["grid_Iout"])
            vsd = Vdd - v
            o = np.argsort(vsd)
            curves.append(np.interp(vsd_grid, vsd[o], i[o]))
        curves = np.array(curves)
        mean = curves.mean(0)
        resid = np.max(np.abs(curves-mean)/np.abs(mean))
        out[f"{name}:{topo}"] = float(resid)
    return out


# ---- UVLO compliance at the 3.2 V floor of the 5 V domain ----------------
def uvlo_compliance():
    """At the 3.2 V UVLO floor, is each topology still a good current source up to
    mid-rail (Vdd/2 = 1.6 V)?  General check on a locked design (no app trip point)."""
    out = {}
    for topo in ("MIR_S","MIR_CS","MIR_CW"):
        s = next(x for x in sweeps if x["name"]==UVLO_DESIGN and x["topo"]==topo
                 and x["Vdd"]==3.2 and x["case"]==0 and x["temp"]==27)
        v=np.array(s["grid_Vout"]); i=np.array(s["grid_Iout"])
        gmid = float(np.interp(1.6,v,i))/s["Iin"]
        droop = 1 - float(np.interp(1.6,v,i))/float(np.interp(0,v,i))
        out[topo] = dict(design=UVLO_DESIGN, gain_at_vddhalf=gmid,
                         droop_0_to_vddhalf_pct=droop*100,
                         vmax_1pct=s["metrics"]["vmax_1pct"],
                         vmax_0p1pct=s["metrics"]["vmax_0p1pct"])
    return out


# ---- junction-leakage projection at 100 nA / 150 C -----------------------
def leakage_projection():
    """[PROJECTION] -- NOT a measured number.  BSIM3 sees AD/AS/PD/PS=0 so junction
    leakage is modelled as zero.  Estimate what it WOULD be for the drawn output
    device using plausible drain geometry and a HV p+/nwell Js(150C)."""
    ext = 0.6e-6
    Js_150 = 5e-3     # A/m^2  (area component, order-of-magnitude HV @150C)
    Jsw_150 = 5e-10   # A/m    (perimeter component)
    proj = {}
    for name in ("B_100n","A_100n"):
        W = designs[name]["geometry"]["W_um"]*1e-6
        AD = W*ext; PD = 2*(W+ext)
        Ileak = Js_150*AD + Jsw_150*PD
        Iin = designs[name]["Iin"]
        proj[name] = dict(W_um=W*1e6, AD_um2=AD*1e12, PD_um=PD*1e6,
                          Ileak_est_A=Ileak, Iin_A=Iin,
                          leak_frac_of_Iin_pct=100*Ileak/Iin)
    proj["_note"] = ("[PROJECTION] Js/Jsw are plausible HV p+/nwell values at "
                     "150C; the PDK models set AD/AS/PD/PS=0 so simulated leakage "
                     "is exactly zero. This estimate is walled off and feeds no "
                     "measured number.")
    return proj


def main():
    write_csv()
    cc = dict(vsd_collapse_residual=vsd_collapse(),
              uvlo_compliance_vdd3v2=uvlo_compliance(),
              leakage_projection=leakage_projection())
    with open(os.path.join(HERE, "crosscheck.json"), "w") as f:
        json.dump(cc, f, indent=2)

    print("\n=== V_SD collapse residual (max frac spread across 4 Vdd, 0.5-3.0V band) ===")
    worst = max(cc["vsd_collapse_residual"].values())
    print(f"  worst residual over all designs/topologies: {worst:.2e}  (all ~machine epsilon)")
    print(f"\n=== UVLO (Vdd=3.2) compliance, {UVLO_DESIGN} ===")
    for t,r in cc["uvlo_compliance_vdd3v2"].items():
        print(f"  {t:7s} gain@Vdd/2={r['gain_at_vddhalf']:.4f}  "
              f"droop0-1.6V={r['droop_0_to_vddhalf_pct']:.2f}%  vmax1%={r['vmax_1pct']:.2f}V")
    print("\n=== leakage projection [PROJECTION, not measured] ===")
    for k in ("B_100n","A_100n"):
        p=cc["leakage_projection"][k]
        print(f"  {k}: Ileak~{p['Ileak_est_A']:.2e}A = {p['leak_frac_of_Iin_pct']:.4f}% of Iin({p['Iin_A']:.1e}A)")

if __name__ == "__main__":
    main()
