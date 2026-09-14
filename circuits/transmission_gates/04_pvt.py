"""Step 3 -- three impedance variants per domain, characterized over PVT.

Variants are sized from the step-02b ladder to hit ~1 kohm / ~100 ohm / ~10 ohm
peak-over-input-level Ron at the TYPICAL point (TT, nominal supply, 27 C) in the
shipping (rail-tied body) configuration.  Wp/Wn = 2.5, L = Lmin.

Matrix: 5 process corners x 3 supplies (+/-10 %) x 3 temperatures, and at every
one of those 45 points the full 0..vdd input-level sweep, so the reported Ron_max
is a true worst case over level as well as over PVT.

Output: results/04_pvt.json
"""
import json
from concurrent.futures import ThreadPoolExecutor

import tg_lib as T

RATIO = 2.5
BODIES = ["rail", "srcbody"]

# (class, Wn_total_um, Wp_total_um) -- Wp = 2.5*Wn, decade-scaled
VARIANTS = {
    "1v8": [("1K", 4.0, 10.0), ("100R", 40.0, 100.0), ("10R", 400.0, 1000.0)],
    "3v3": [("1K", 4.6, 11.5), ("100R", 46.0, 115.0), ("10R", 460.0, 1150.0)],
    "5v0": [("1K", 8.4, 21.0), ("100R", 84.0, 210.0), ("10R", 840.0, 2100.0)],
}

jobs = []
for dom in T.DOMAINS:
    for body in BODIES:
        for case in T.CORNERS:
            for v in T.vlist(dom):
                for tc in T.TEMPS:
                    jobs.append((dom, body, case, v, tc))


def one(job):
    dom, body, case, v, tc = job
    vs = str(v).replace(".", "p")
    tag = f"04_{dom}_{body}_c{case}_v{vs}_t{tc}"
    variants = [(cls, wn, wp) for (cls, wn, wp) in VARIANTS[dom]]
    txt = T.level_sweep_deck(f"04 pvt {dom} {body} {T.CNAME[case]} {v}V {tc}C",
                             dom, variants, body, case=case, temp=tc, vdd=v,
                             outfile=tag + ".txt")
    log = T.run_deck(txt, tag)
    if "No. of Data Rows" not in log:
        return (job, None, log[-1500:])
    xs, cols = T.read_wrdata(T.DECK / (tag + ".txt"), len(variants))
    res = {}
    for (vt, col) in zip(variants, cols):
        imax = max(range(len(col)), key=lambda i: col[i])
        res[vt[0]] = {"ron_max_ohm": col[imax], "ron_min_ohm": min(col),
                      "worst_level_V": round(xs[imax], 4)}
    return (job, res, None)


print(f"running {len(jobs)} PVT points ...")
data = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    for job, res, err in ex.map(one, jobs):
        if res is None:
            print("FAILED", job); print(err); raise SystemExit(1)
        dom, body, case, v, tc = job
        data.setdefault(dom, {}).setdefault(body, []).append(
            {"case": case, "corner": T.CNAME[case], "vdd_V": v, "temp_C": tc,
             "variants": res})

out = {"provenance": T.provenance({"step": "04_pvt", "wp_over_wn": RATIO,
                                   "corners": [T.CNAME[c] for c in T.CORNERS],
                                   "temps_C": T.TEMPS, "vtol": T.VTOL,
                                   "note": "-55 C is below the model Tj_min of -40 C"}),
       "variants": VARIANTS, "ratio": RATIO, "pvt": data, "summary": {}}

for dom in T.DOMAINS:
    d = T.DOMAINS[dom]
    out["summary"][dom] = {}
    for body in BODIES:
        rows = data[dom][body]
        out["summary"][dom][body] = {}
        for (cls, wn, wp) in VARIANTS[dom]:
            typ = [r for r in rows if r["case"] == 0 and r["temp_C"] == 27
                   and abs(r["vdd_V"] - d["vdd"]) < 1e-6][0]["variants"][cls]
            allmax = max(rows, key=lambda r: r["variants"][cls]["ron_max_ohm"])
            allmin = min(rows, key=lambda r: r["variants"][cls]["ron_min_ohm"])
            s = {"wn_um": wn, "wp_um": wp, "wtot_um": wn + wp,
                 "ron_typ_ohm": typ["ron_max_ohm"],
                 "ron_max_ohm": allmax["variants"][cls]["ron_max_ohm"],
                 "ron_max_at": f"{allmax['corner']} {allmax['vdd_V']}V {allmax['temp_C']}C "
                               f"level={allmax['variants'][cls]['worst_level_V']}V",
                 "ron_min_ohm": allmin["variants"][cls]["ron_min_ohm"],
                 "ron_min_at": f"{allmin['corner']} {allmin['vdd_V']}V {allmin['temp_C']}C",
                 "idc_max_mA": d["idc_dens"] * wn,
                 "gate_area_um2": (wn + wp) * d["Lmin"]}
            s["spread_x"] = s["ron_max_ohm"] / s["ron_min_ohm"]
            s["max_over_typ"] = s["ron_max_ohm"] / s["ron_typ_ohm"]
            out["summary"][dom][body][cls] = s

(T.RESULTS / "04_pvt.json").write_text(json.dumps(out, indent=1))

for dom in T.DOMAINS:
    for body in BODIES:
        print(f"\n=== {dom} / {body} ===")
        print("  class   Wn[um]   Wp[um]   Ron_typ   Ron_max   Ron_min  max/typ  spread  Idc[mA]")
        for cls in ("1K", "100R", "10R"):
            s = out["summary"][dom][body][cls]
            print(f"  {cls:6s} {s['wn_um']:8.1f} {s['wp_um']:8.1f} "
                  f"{s['ron_typ_ohm']:9.4g} {s['ron_max_ohm']:9.4g} {s['ron_min_ohm']:9.4g} "
                  f"{s['max_over_typ']:8.2f} {s['spread_x']:7.2f} {s['idc_max_mA']:8.4g}")
            print(f"         worst at {s['ron_max_at']}")
print("\nwrote results/04_pvt.json")
