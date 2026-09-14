"""Step 4 -- usable input window and terminal capacitance.

(a) Input window: at the worst PVT point for each domain/body, the contiguous
    band of input level over which Ron stays under a stated ceiling.  This is
    what turns the 1.8 V dead zone into a spec line instead of a surprise.
(b) Terminal capacitance, switch off and switch on: the node loading that the
    low-Ron variants buy their conductance with.

Output: results/05_limits.json
"""
import json
import re
import tg_lib as T

VARIANTS = {
    "1v8": [("1K", 4.0, 10.0), ("100R", 40.0, 100.0), ("10R", 400.0, 1000.0)],
    "3v3": [("1K", 4.6, 11.5), ("100R", 46.0, 115.0), ("10R", 460.0, 1150.0)],
    "5v0": [("1K", 8.4, 21.0), ("100R", 84.0, 210.0), ("10R", 840.0, 2100.0)],
}
NOMINAL = {"1K": 1000.0, "100R": 100.0, "10R": 10.0}
CEIL = 3.0          # Ron ceiling as a multiple of the class nominal
WORST = {"1v8": (2, 0.90, -55), "3v3": (2, 0.90, 150), "5v0": (2, 0.90, 150)}

out = {"provenance": T.provenance({"step": "05_limits", "ceiling_x_nominal": CEIL}),
       "window": {}, "coff": {}}

for dom, d in T.DOMAINS.items():
    case, vfrac, tc = WORST[dom]
    v = round(d["vdd"] * vfrac, 4)
    out["window"][dom] = {"corner": T.CNAME[case], "vdd_V": v, "temp_C": tc, "body": {}}
    for body in ("rail", "srcbody"):
        tag = f"05w_{dom}_{body}"
        txt = T.level_sweep_deck(f"05 window {dom} {body}", dom, VARIANTS[dom],
                                 body, case=case, temp=tc, vdd=v, outfile=tag + ".txt")
        T.run_deck(txt, tag)
        xs, cols = T.read_wrdata(T.DECK / (tag + ".txt"), 3)
        out["window"][dom]["body"][body] = {}
        for (spec, col) in zip(VARIANTS[dom], cols):
            cls = spec[0]
            lim = CEIL * NOMINAL[cls]
            bad = [xs[i] for i in range(len(xs)) if col[i] > lim]
            if not bad:
                w = {"ok": "full 0..vdd", "excluded_band_V": None}
            else:
                w = {"ok": f"0..{min(bad):.3f} and {max(bad):.3f}..{v:.3f}",
                     "excluded_band_V": [round(min(bad), 4), round(max(bad), 4)],
                     "excluded_frac": round((max(bad) - min(bad)) / v, 4)}
            w["ceiling_ohm"] = lim
            w["ron_peak_ohm"] = max(col)
            out["window"][dom]["body"][body][cls] = w
            print(f"{dom} {body:8s} {cls:5s} @{T.CNAME[case]}/{v}V/{tc}C  "
                  f"peak {max(col):9.4g} ohm  ceiling {lim:6.0f}  -> {w['ok']}")
    print()

# Capacitance looking into one switch terminal: drive `b` with a 1 V AC source
# and hold `a` at DC, so I(Vb) is the terminal admittance -- drain junction,
# gate overlap, and the path through the (off or on) channel to `a`.
for dom, d in T.DOMAINS.items():
    out["coff"][dom] = {}
    for (cls, wn, wp) in VARIANTS[dom]:
        wn_f, mn = T.split_wm(wn, dom)
        wp_f, mp = T.split_wm(wp, dom)
        vm = d["vdd"] / 2
        row = {"wtot_um": wn + wp}
        for state, ven, venb in (("off", 0.0, d["vdd"]), ("on", d["vdd"], 0.0)):
            lines = [
                ".title cnode", '.include "' + T.LIB + '"',
                ".param case=0", ".param PROC_ON=0", ".param MM_ON=0",
                ".option num_threads=1",
                "Vdd vdd 0 %.6g" % d["vdd"],
                "Ven en 0 %.6g" % ven, "Venb enb 0 %.6g" % venb,
                "Va a 0 %.6g" % vm,
                "Vb b 0 %.6g AC 1" % vm,
                "XN b en  a 0   %s W=%.6gu L=%.6gu M=%d" % (d["n"], wn_f, d["Lmin"], mn),
                "XP b enb a vdd %s W=%.6gu L=%.6gu M=%d" % (d["p"], wp_f, d["Lmin"], mp),
                ".control", "option temp=27", "ac lin 1 1e6 1e6",
                "let cnode = imag(i(vb))/(2*pi*1e6)",
                "print cnode", ".endc", ".end", ""]
            log = T.run_deck("\n".join(lines), "05c_%s_%s_%s" % (dom, cls, state))
            val = None
            for ln in log.splitlines():
                m = re.search(r"cnode\s*=\s*([-\d.eE+]+)", ln)
                if m:
                    val = abs(float(m.group(1)))
            row[state + "_fF"] = val * 1e15 if val is not None else None
        out["coff"][dom][cls] = row
        print("%s %-5s terminal C: off = %8.4g fF   on = %8.4g fF   (Wtot %.1f um)"
              % (dom, cls, row["off_fF"], row["on_fF"], wn + wp))

(T.RESULTS / "05_limits.json").write_text(json.dumps(out, indent=1))
print("\nwrote results/05_limits.json")
