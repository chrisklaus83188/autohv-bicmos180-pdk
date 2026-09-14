"""Does the M multiplier reduce mismatch?  (HANDOFF_monte_carlo.md section 3)

NMOS50 mirror at 10 uA, mismatch only (MM_ON=1, PROC_ON=0), TT / 5.0 V / 27 C,
120 fixed-seed runs per geometry, one ngspice invocation per run.

Four geometries: the baseline device, then four times its area reached three
ways -- through M, through W, and through L.  Every mismatch term in the v2.2
MOS wrapper scales as 1/sqrt(AUM2) with AUM2 = W*L and no M, so quadrupling the
area through M leaves sigma(delvto) unchanged while W or L halve it.

This is the "before" evidence for brief acceptance A1: after the R1 fix the
M=4 row must show sigma(delvto) halved.  The sigma/mu(Iout) column also moves
with gm/Id (a wider device at fixed current sits closer to weak inversion),
which is legitimate -- the delvto column is the clean evidence.

Output: results/02_m_sweep.json
"""
import json
import re
from concurrent.futures import ThreadPoolExecutor

import mc_lib as M

NRUN = 120
SEEDS = list(range(1, NRUN + 1))
GEOMS = [          # (W um, L um, M)
    (4.7, 1.0, 1),
    (4.7, 1.0, 4),
    (18.8, 1.0, 1),
    (4.7, 4.0, 1),
]
AVT = 0.033        # V.um, NMOS50 wrapper coefficient, AGAUSS 3-sigma convention

# HANDOFF_monte_carlo.md section 3, measured in-session with inline scripts
HANDOFF_S3 = {
    "W4.7_L1_M1": {"sigma_delvto_mV": 5.039, "sigma_over_mu_pct": 3.624},
    "W4.7_L1_M4": {"sigma_delvto_mV": 4.958, "sigma_over_mu_pct": 6.798},
    "W18.8_L1_M1": {"sigma_delvto_mV": 2.605, "sigma_over_mu_pct": 3.737},
    "W4.7_L4_M1": {"sigma_delvto_mV": 2.422, "sigma_over_mu_pct": 0.671},
}


def key(w, l, m):
    return "W%g_L%g_M%d" % (w, l, m)


def deck(w, l, m, seed):
    return "\n".join([
        ".title m_sweep_%s_seed%d" % (key(w, l, m), seed),
        '.include "%s"' % M.LIB,
        ".param case=%d" % M.CASE,
        ".param PROC_ON=0",
        ".param MM_ON=1",
        ".option num_threads=1",
        "Vdd  dd 0 %.6g" % M.VDD,
        "Iref dd in %.6g" % M.IREF,
        "X1 in  in 0 0 %s W=%gu L=%gu M=%d" % (M.DEV, w, l, m),
        "X2 out in 0 0 %s W=%gu L=%gu M=%d" % (M.DEV, w, l, m),
        "Vout out 0 %.6g" % M.VOUT,
        ".option seed=%d" % seed,
        ".control",
        "option temp=%d" % M.TEMP,
        "option numdgt=10",
        "op",
        "print abs(i(vout)) @m.x1.m0[delvto] @m.x2.m0[delvto]",
        ".endc", ".end", ""])


KEYS = {"abs(i(vout))": "io", "@m.x1.m0[delvto]": "d1", "@m.x2.m0[delvto]": "d2"}


def parse_print(out):
    r = {}
    for ln in out.splitlines():
        m = re.match(r"\s*(\S+)\s*=\s*([-\d.eE+]+)\s*$", ln)
        if m and m.group(1) in KEYS:
            r[KEYS[m.group(1)]] = float(m.group(2))
    return r


def one(job):
    w, l, m, seed = job
    r = parse_print(M.run(deck(w, l, m, seed), "msw_%s_%03d" % (key(w, l, m), seed)))
    if len(r) != len(KEYS):
        raise SystemExit("incomplete result for %s seed %d: %s" % (key(w, l, m), seed, r))
    r["seed"] = seed
    return r


rows_out = []
print("M sweep -- ngspice %s, NMOS50 mirror, %d runs per geometry, MM_ON=1 PROC_ON=0"
      % (M.ngspice_version(), NRUN))
print()
print("  %-14s %8s %14s %14s %14s %11s" % ("geometry", "area", "sigma(delvto)",
                                          "formula v2.2", "formula R1", "sigma/mu"))
print("  %-14s %8s %14s %14s %14s %11s" % ("", "um^2", "mV", "mV", "mV", "Iout %"))
for (w, l, m) in GEOMS:
    with ThreadPoolExecutor(max_workers=8) as ex:
        rows = list(ex.map(one, [(w, l, m, s) for s in SEEDS]))
    rows.sort(key=lambda r: r["seed"])
    io = [r["io"] for r in rows]
    d1 = [r["d1"] for r in rows]
    pooled = d1 + [r["d2"] for r in rows]
    s_io, s_d1, s_pool = M.stats(io), M.stats(d1), M.stats(pooled)
    f_now = AVT / 3.0 / (w * l) ** 0.5            # v2.2 wrapper: no M in AUM2
    f_r1 = AVT / 3.0 / (w * l * m) ** 0.5         # brief R1: AUM2 includes M
    k = key(w, l, m)
    rows_out.append({
        "key": k, "W_um": w, "L_um": l, "M": m, "total_area_um2": w * l * m,
        "sigma_delvto_dev1_mV": s_d1["std"] * 1e3,
        "sigma_delvto_pooled_mV": s_pool["std"] * 1e3,
        "formula_v2_2_mV": f_now * 1e3,
        "formula_R1_mV": f_r1 * 1e3,
        "iout": s_io,
        "sigma_over_mu_pct": s_io["sigma_over_mu_pct"],
        "handoff_section3": HANDOFF_S3.get(k),
        "runs": rows,
    })
    print("  %-14s %8.1f %14.3f %14.3f %14.3f %11.3f"
          % (k, w * l * m, s_pool["std"] * 1e3, f_now * 1e3, f_r1 * 1e3,
             s_io["sigma_over_mu_pct"]))

out = {
    "provenance": M.provenance({"step": "02_mc_m_sweep", "nrun_per_geometry": NRUN,
                                "MM_ON": 1, "PROC_ON": 0,
                                "pattern": "one invocation per sample, .option seed=k",
                                "sigma_delvto_basis": "pooled over both mirror devices"}),
    "geometries": rows_out,
}
(M.RESULTS / "02_m_sweep.json").write_text(json.dumps(out, indent=1))
print()
print("sigma(delvto) is pooled over both devices (2 x %d draws per row)." % NRUN)
print("wrote results/02_m_sweep.json")
