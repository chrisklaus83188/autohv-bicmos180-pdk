"""Step 1 -- minimum-size transmission gate: Ron across the input range.

Runs every domain at its fabrication-minimum geometry (Wn = Wp = Wmin,
L = Lmin), nominal supply, TT corner, 27 C, for both body configurations.
Also runs NMOS-only and PMOS-only legs so the worst-case level and the
natural Wp/Wn balance ratio can be read off directly.

Output: results/01_level.json
"""
import json
import tg_lib as T

BODIES = ["srcbody", "rail"]
out = {"provenance": T.provenance({"step": "01_ron_vs_level",
                                   "case": "TT", "temp_C": 27,
                                   "supply": "nominal",
                                   "dv_probe_V": T.DV}),
       "domains": {}}

for dom, d in T.DOMAINS.items():
    wmin = d["Wmin"]
    out["domains"][dom] = {"Wmin_um": wmin, "Lmin_um": d["Lmin"],
                           "vdd_V": d["vdd"], "body": {}}
    for body in BODIES:
        # 'both' = the complete gate; 'n'/'p' = single-device legs (W of the
        # absent device set to zero by simply omitting it -- done with two
        # extra variants that carry only one transistor).
        variants = [("both", wmin, wmin)]
        txt = T.level_sweep_deck(f"01 {dom} {body} minsize", dom, variants, body,
                                 outfile=f"01_{dom}_{body}.txt")
        # append single-device legs by hand (the helper always emits a pair)
        lines = txt.splitlines()
        i_ctrl = lines.index(".control")
        d_ = T.DOMAINS[dom]
        bn, bp = ("a", "a") if body == "srcbody" else ("0", "vdd")
        extra = [
            f"Vb_n b_n a {T.DV}",
            f"XN_n b_n en  a {bn} {d_['n']} W={wmin:.6g}u L={d_['Lmin']:.6g}u M=1",
            f"Vb_p b_p a {T.DV}",
            f"XP_p b_p enb a {bp} {d_['p']} W={wmin:.6g}u L={d_['Lmin']:.6g}u M=1",
        ]
        lines[i_ctrl:i_ctrl] = extra
        j = lines.index("let ron_both = %s/abs(i(vb_both))" % T.DV)
        lines[j + 1:j + 1] = [f"let ron_n = {T.DV}/abs(i(vb_n))",
                              f"let ron_p = {T.DV}/abs(i(vb_p))"]
        for k, ln in enumerate(lines):
            if ln.startswith("wrdata"):
                lines[k] = f"wrdata 01_{dom}_{body}.txt ron_both ron_n ron_p"
        txt = "\n".join(lines) + "\n"
        log = T.run_deck(txt, f"01_{dom}_{body}")
        if "error" in log.lower() and "No. of Data Rows" not in log:
            print(log[-2000:])
            raise SystemExit(f"ngspice failed: 01_{dom}_{body}")
        xs, cols = T.read_wrdata(T.DECK / f"01_{dom}_{body}.txt", 3)
        ron, rn, rp = cols
        imax = max(range(len(xs)), key=lambda i: ron[i])
        out["domains"][dom]["body"][body] = {
            "level_V": [round(x, 6) for x in xs],
            "ron_ohm": ron, "ron_nmos_only_ohm": rn, "ron_pmos_only_ohm": rp,
            "ron_min_ohm": min(ron), "ron_max_ohm": max(ron),
            "worst_level_V": round(xs[imax], 6),
            "ron_at_0_ohm": ron[0], "ron_at_vdd_ohm": ron[-1],
            "gn_over_gp_at_worst": rp[imax] / rn[imax],
        }
        print(f"{dom:4s} {body:8s}  Ron {min(ron):9.4g} .. {max(ron):9.4g} ohm "
              f"| worst at V={xs[imax]:.3f}  (gN/gP there = {rp[imax]/rn[imax]:.2f})")

(T.RESULTS / "01_level.json").write_text(json.dumps(out, indent=1))
print("\nwrote results/01_level.json")
