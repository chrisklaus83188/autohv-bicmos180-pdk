"""Step 2a -- pick the Wp/Wn balance ratio.

At a fixed TOTAL drawn width (the area proxy), sweep the split between the
NMOS and the PMOS and find the ratio that minimizes the WORST-CASE Ron over
the whole input range.  Minimizing peak Ron at fixed total width is the same
as minimizing area for a given peak Ron, so this ratio is the right one to
freeze before the width ladder.

Run at two total widths to confirm the optimum is width-independent.
Output: results/02_ratio.json
"""
import json
import tg_lib as T

RATIOS = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0, 8.0]
WTOTS = [2.0, 20.0]          # um, total drawn width (Wn + Wp)
BODIES = ["srcbody", "rail"]

out = {"provenance": T.provenance({"step": "02_ratio", "case": "TT",
                                   "temp_C": 27, "supply": "nominal"}),
       "ratios": RATIOS, "wtots_um": WTOTS, "domains": {}}

for dom, d in T.DOMAINS.items():
    out["domains"][dom] = {}
    for body in BODIES:
        out["domains"][dom][body] = {}
        for wtot in WTOTS:
            variants = []
            for r in RATIOS:
                wn = wtot / (1 + r)
                wp = wtot * r / (1 + r)
                if wn < d["Wmin"] or wp < d["Wmin"]:
                    continue
                variants.append((f"r{str(r).replace('.','p')}", wn, wp))
            tag = f"02_{dom}_{body}_w{str(wtot).replace('.','p')}"
            txt = T.level_sweep_deck(f"02 ratio {dom} {body} Wtot={wtot}", dom,
                                     variants, body, outfile=tag + ".txt")
            log = T.run_deck(txt, tag)
            if "No. of Data Rows" not in log:
                print(log[-2000:]); raise SystemExit("ngspice failed " + tag)
            xs, cols = T.read_wrdata(T.DECK / (tag + ".txt"), len(variants))
            rows = []
            for (vt, col) in zip(variants, cols):
                r = float(vt[0][1:].replace("p", "."))
                imax = max(range(len(xs)), key=lambda i: col[i])
                rows.append({"ratio": r, "wn_um": vt[1], "wp_um": vt[2],
                             "ron_peak_ohm": col[imax],
                             "worst_level_V": round(xs[imax], 4),
                             "ron_at_0_ohm": col[0], "ron_at_vdd_ohm": col[-1]})
            best = min(rows, key=lambda x: x["ron_peak_ohm"])
            out["domains"][dom][body][str(wtot)] = {"rows": rows,
                                                    "best_ratio": best["ratio"]}
            print(f"{dom:4s} {body:8s} Wtot={wtot:5.1f}um -> best Wp/Wn = "
                  f"{best['ratio']:.1f}  (peak Ron {best['ron_peak_ohm']:.4g} ohm "
                  f"at V={best['worst_level_V']:.3f})")
            flat = "  ".join(f"{r['ratio']:.1f}:{r['ron_peak_ohm']:.4g}" for r in rows)
            print(f"      peak Ron vs ratio: {flat}")

(T.RESULTS / "02_ratio.json").write_text(json.dumps(out, indent=1))
print("\nwrote results/02_ratio.json")
