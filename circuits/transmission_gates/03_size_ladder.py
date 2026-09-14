"""Step 2b -- Ron vs size.

At the frozen Wp/Wn balance ratio, sweep the TOTAL drawn width geometrically
and record the worst-case (peak-over-input-level) Ron.  This is the curve that
turns an impedance target into a geometry.  TT / 27 C / nominal supply.

Output: results/03_ladder.json
"""
import json
import math
import tg_lib as T

RATIO = 2.5          # Wp/Wn, frozen from step 02 (within 2 % of the per-domain optimum)
BODIES = ["srcbody", "rail"]
NSTEP = 25           # geometric steps

out = {"provenance": T.provenance({"step": "03_size_ladder", "case": "TT",
                                   "temp_C": 27, "supply": "nominal",
                                   "wp_over_wn": RATIO}),
       "ratio": RATIO, "domains": {}}

for dom, d in T.DOMAINS.items():
    wtot_min = d["Wmin"] * (1 + RATIO)          # both devices at the fab floor
    wtot_max = 6000.0
    wtots = [wtot_min * (wtot_max / wtot_min) ** (k / (NSTEP - 1))
             for k in range(NSTEP)]
    out["domains"][dom] = {}
    for body in BODIES:
        variants = []
        for k, wt in enumerate(wtots):
            wn = wt / (1 + RATIO)
            wp = wt * RATIO / (1 + RATIO)
            variants.append((f"s{k:02d}", wn, wp))
        tag = f"03_{dom}_{body}"
        txt = T.level_sweep_deck(f"03 ladder {dom} {body}", dom, variants, body,
                                 outfile=tag + ".txt")
        log = T.run_deck(txt, tag)
        if "No. of Data Rows" not in log:
            print(log[-3000:]); raise SystemExit("ngspice failed " + tag)
        xs, cols = T.read_wrdata(T.DECK / (tag + ".txt"), len(variants))
        rows = []
        for (vt, col) in zip(variants, cols):
            imax = max(range(len(xs)), key=lambda i: col[i])
            wn, wp = vt[1], vt[2]
            wt = wn + wp
            rows.append({
                "wtot_um": wt, "wn_um": wn, "wp_um": wp,
                "ron_peak_ohm": col[imax],
                "worst_level_V": round(xs[imax], 4),
                "ron_at_0_ohm": col[0], "ron_at_vdd_ohm": col[-1],
                "ron_w_product_ohm_um": col[imax] * wt,
                "idc_max_mA": d["idc_dens"] * wn,      # NMOS leg is the binding one
                "gate_area_um2": wt * d["Lmin"],
            })
        out["domains"][dom][body] = {"rows": rows}
        print(f"\n--- {dom} / {body} (Wp/Wn={RATIO}) ---")
        print("  Wtot[um]   Wn[um]    peak Ron[ohm]  @V     Ron*W[ohm.um]  Idc[mA]")
        for r in rows:
            print(f"  {r['wtot_um']:9.2f} {r['wn_um']:8.2f} {r['ron_peak_ohm']:13.4g} "
                  f"{r['worst_level_V']:6.2f} {r['ron_w_product_ohm_um']:14.4g} "
                  f"{r['idc_max_mA']:8.3g}")

(T.RESULTS / "03_ladder.json").write_text(json.dumps(out, indent=1))
print("\nwrote results/03_ladder.json")
