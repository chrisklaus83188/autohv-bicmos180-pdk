"""200-run Monte Carlo, local mismatch only, on a simple NMOS5V0 current mirror.

Nominal PVT: TT (case=0), Vdd = 5.0 V, 27 C.  MM_ON=1, PROC_ON=0.
Iref = 10 uA.  Both devices NMOS5V0 W = 4.7 um, L = 1.0 um -- the sizing guide's
own gm/Id ~ 6 entry for this device and current.

Each run is its own ngspice invocation carrying `.option seed=k`, which is the
only pattern found to be both statistically live and bit-reproducible; see
00_mc_mechanism.py for the evidence.

Per run the deck reports the mirror output current, the gate voltage the
reference settles at, the delvto actually applied to each instance, and the
output device's gm and Id -- so the measured spread can be checked against the
wrapper's own mismatch formula rather than only against itself.

Output: results/01_mc_mirror.json
"""
import json
import re
from concurrent.futures import ThreadPoolExecutor

import mc_lib as M

NRUN = 200
SEEDS = list(range(1, NRUN + 1))


def deck(seed):
    return "\n".join(
        [".title mc_mirror_seed%d" % seed] + M.mirror(mm=1, proc=0) +
        [".option seed=%d" % seed,
         ".control",
         "option temp=%d" % M.TEMP,
         # echo's $& formatting rounds to 6 significant figures, which is enough
         # to make independent samples collide; print + numdgt keeps full precision
         "option numdgt=10",
         "op",
         "print abs(i(vout)) v(in) @m.x1.m0[delvto] @m.x2.m0[delvto]",
         "print @m.x2.m0[gm] @m.x2.m0[id]",
         ".endc", ".end", ""])


KEYS = {"abs(i(vout))": "io", "v(in)": "vg", "@m.x1.m0[delvto]": "d1",
        "@m.x2.m0[delvto]": "d2", "@m.x2.m0[gm]": "gm", "@m.x2.m0[id]": "id"}


def parse_print(out):
    r = {}
    for ln in out.splitlines():
        m = re.match(r"\s*(\S+)\s*=\s*([-\d.eE+]+)\s*$", ln)
        if m and m.group(1) in KEYS:
            r[KEYS[m.group(1)]] = float(m.group(2))
    return r


def one(seed):
    r = parse_print(M.run(deck(seed), "mc_%03d" % seed))
    if len(r) != len(KEYS):
        raise SystemExit("incomplete result for seed %d: %s" % (seed, r))
    r["seed"] = seed
    return r


with ThreadPoolExecutor(max_workers=8) as ex:
    rows = list(ex.map(one, SEEDS))
rows.sort(key=lambda r: r["seed"])

io = [r["io"] for r in rows]
gain = [v / M.IREF for v in io]
d1 = [r["d1"] for r in rows]
d2 = [r["d2"] for r in rows]
dd = [b - a for a, b in zip(d1, d2)]          # pair threshold difference
gmid = [r["gm"] / abs(r["id"]) for r in rows]

# zero-mismatch reference point: the systematic part of the gain
base = M.parse_res(M.run(M.deck_single(mm=0, proc=0), "mc_base"))[0]
gain0 = base["iout"] / M.IREF

# what the wrapper's own formula predicts, independent of the simulation:
#   ngspice AGAUSS(nom, avar, n) has standard deviation avar/n, so the per-device
#   threshold sigma is A_VT / (3 * sqrt(W*L)) with A_VT = 0.033 V.um for NMOS5V0.
AVT, AW, AL = 0.033, 0.0075, 0.0045
area = M.W * M.L
sig_vth_dev = AVT / 3.0 / area ** 0.5
sig_vth_pair = 2 ** 0.5 * sig_vth_dev
sig_w_pair = 2 ** 0.5 * AW / 3.0 / area ** 0.5
sig_l_pair = 2 ** 0.5 * AL / 3.0 / area ** 0.5
gmid_mean = sum(gmid) / len(gmid)
pred_vth_pct = 100 * gmid_mean * sig_vth_pair
pred_geo_pct = 100 * (sig_w_pair ** 2 + sig_l_pair ** 2) ** 0.5
pred_pct = (pred_vth_pct ** 2 + pred_geo_pct ** 2) ** 0.5

s_io = M.stats(io)
s_dd = M.stats(dd)
s_d1 = M.stats(d1)

out = {
    "provenance": M.provenance({"nrun": NRUN, "MM_ON": 1, "PROC_ON": 0,
                                "pattern": "one invocation per sample, .option seed=k"}),
    "iout": s_io,
    "gain_mean": sum(gain) / len(gain),
    "gain_zero_mismatch": gain0,
    "sigma_over_mu_pct": s_io["sigma_over_mu_pct"],
    "delvto_dev1": s_d1,
    "delvto_pair_diff": s_dd,
    "gm_over_id_mean": gmid_mean,
    "prediction": {
        "sigma_vth_per_device_V": sig_vth_dev,
        "sigma_vth_pair_V": sig_vth_pair,
        "from_vth_pct": pred_vth_pct,
        "from_geometry_pct": pred_geo_pct,
        "total_pct": pred_pct,
        "sizing_guide_pct": M.GUIDE_SIGMA_PCT,
    },
    "runs": rows,
}
(M.RESULTS / "01_mc_mirror.json").write_text(json.dumps(out, indent=1))

print("200-run Monte Carlo, mismatch only, TT / 5.0 V / 27 C")
print("  NMOS5V0 mirror, W = %g um, L = %g um, Iref = %g uA" % (M.W, M.L, M.IREF * 1e6))
print()
print("  Iout mean        %10.4f uA" % (s_io["mean"] * 1e6))
print("  Iout sigma       %10.4f uA" % (s_io["std"] * 1e6))
print("  sigma/mu         %10.3f %%" % s_io["sigma_over_mu_pct"])
print("  Iout min / max   %10.4f / %.4f uA" % (s_io["min"] * 1e6, s_io["max"] * 1e6))
print("  distinct samples %10d / %d" % (s_io["distinct"], NRUN))
print()
print("  gain (mean Iout/Iref)          %.4f" % (sum(gain) / len(gain)))
print("  gain with mismatch off         %.4f   <- systematic, from Vds mismatch (CLM)" % gain0)
print()
print("  measured sigma(delvto), one device   %8.3f mV" % (s_d1["std"] * 1e3))
print("  formula   sigma(delvto), one device  %8.3f mV" % (sig_vth_dev * 1e3))
print("  measured sigma(delvto2 - delvto1)    %8.3f mV" % (s_dd["std"] * 1e3))
print("  formula   sigma of that difference   %8.3f mV" % (sig_vth_pair * 1e3))
print()
print("  gm/Id at the operating point   %.2f /V" % gmid_mean)
print("  predicted sigma/mu from the wrapper formula  %.3f %%" % pred_pct)
print("    threshold term %.3f %%, geometry term %.3f %%" % (pred_vth_pct, pred_geo_pct))
print("  sizing guide pre-registered value            %.2f %%" % M.GUIDE_SIGMA_PCT)
print()
print("wrote results/01_mc_mirror.json")
