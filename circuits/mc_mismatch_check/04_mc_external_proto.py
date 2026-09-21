"""External random-number driver prototype.  (HANDOFF_monte_carlo.md section 4)

Instead of letting the wrapper draw AGAUSS internally, each mirror device gets
its own knob -- MM_SIGMA={S1} on X1, MM_SIGMA={S2} on X2 -- with MM_ON=0, so the
wrapper draws nothing itself.  Python generates the unit-normal z values from a
fixed seed, and a single ngspice invocation steps `alterparam S1=.. S2=..` +
`reset` + `op` through every sample.

What this establishes, as "before" evidence for the Phase 3 driver:
  * the pattern is live (the knob reaches delvto, W and L through reset),
  * it is bit-reproducible (same seed -> identical output, run twice),
  * it is fast (one invocation for all samples; timed in 03_mc_runtime.py).

Known limitation, recorded in the handoff: a single MM_SIGMA drives the Vth, W
and L terms of a device at the same sigma-multiple, so the three are perfectly
correlated.  The first-order prediction below accounts for that; Phase 2 (R5 as
ruled) replaces MM_SIGMA with independent Z_VT, Z_W, Z_L.

Output: results/04_external_proto.json
"""
import json
import re

import numpy as np

import mc_lib as M

NRUN = 200
SEED = 0
AVT, AW, AL = 0.033, 0.0075, 0.0045    # NMOS5V0 wrapper coefficients, 3-sigma convention


def z_matrix(n=NRUN, seed=SEED):
    """Unit-normal knob values, one row per sample, columns (S1, S2)."""
    return np.random.default_rng(seed).standard_normal((n, 2))


def deck(z):
    lines = [
        ".title external_driver_proto",
        '.include "%s"' % M.LIB,
        ".param case=%d" % M.CASE,
        ".param PROC_ON=0",
        ".param MM_ON=0",
        ".param S1=0",
        ".param S2=0",
        ".option num_threads=1",
        "Vdd  dd 0 %.6g" % M.VDD,
        "Iref dd in %.6g" % M.IREF,
        "X1 in  in 0 0 %s W=%gu L=%gu MM_SIGMA={S1}" % (M.DEV, M.W, M.L),
        "X2 out in 0 0 %s W=%gu L=%gu MM_SIGMA={S2}" % (M.DEV, M.W, M.L),
        "Vout out 0 %.6g" % M.VOUT,
        ".control",
        "option temp=%d" % M.TEMP,
        "option numdgt=10",
    ]
    for s1, s2 in z:
        lines += ["alterparam S1=%.17g" % s1, "alterparam S2=%.17g" % s2,
                  "reset", "op", "print abs(i(vout))"]
    lines += [".endc", ".end", ""]
    return "\n".join(lines)


def run_samples(z, tag):
    out = M.run(deck(z), tag)
    vals = [float(v) for v in re.findall(r"abs\(i\(vout\)\)\s*=\s*([-\d.eE+]+)", out)]
    if len(vals) != len(z):
        raise SystemExit("expected %d samples, got %d:\n%s" % (len(z), len(vals), out[-1500:]))
    return vals


if __name__ == "__main__":
    z = z_matrix()
    a = run_samples(z, "ext_proto_a")
    b = run_samples(z, "ext_proto_b")
    s = M.stats(a)

    # first-order prediction for the correlated single knob: in the mirror ratio,
    # X2's Vth enters with -gm/Id, its W with +1 and its L with -1; X1 the opposite.
    # One z per device multiplies all three, so per unit (z2 - z1):
    mc = json.load(open(M.RESULTS / "01_mc_mirror.json"))
    gmid = mc["gm_over_id_mean"]
    root = (M.W * M.L) ** 0.5
    per_z = -gmid * AVT / 3 / root + AW / 3 / root - AL / 3 / root
    pred_corr = 100 * 2 ** 0.5 * abs(per_z)
    pred_indep = mc["prediction"]["total_pct"]

    out = {
        "provenance": M.provenance({"step": "04_mc_external_proto", "nrun": NRUN,
                                    "MM_ON": 0, "PROC_ON": 0, "z_seed": SEED,
                                    "z_generator": "numpy.random.default_rng(seed).standard_normal",
                                    "pattern": "one invocation, alterparam S1/S2 + reset + op per sample"}),
        "iout": s,
        "sigma_over_mu_pct": s["sigma_over_mu_pct"],
        "bit_identical_on_repeat": a == b,
        "prediction": {
            "gm_over_id_from_01": gmid,
            "correlated_single_knob_pct": pred_corr,
            "independent_terms_pct_from_01": pred_indep,
        },
        "handoff_section4_sigma_over_mu_pct": 3.71,
        "native_mm_on_sigma_over_mu_pct_from_01": mc["sigma_over_mu_pct"],
        "z": z.tolist(),
        "iout_samples": a,
    }
    (M.RESULTS / "04_external_proto.json").write_text(json.dumps(out, indent=1))

    print("External RNG driver prototype -- ngspice %s, NMOS5V0 mirror, %d samples, z seed %d"
          % (M.ngspice_version(), NRUN, SEED))
    print()
    print("  sigma/mu                                   %7.3f %%" % s["sigma_over_mu_pct"])
    print("  distinct samples                           %7d / %d" % (s["distinct"], NRUN))
    print("  bit-identical on repeat                    %7s" % (a == b))
    print("  predicted, correlated single knob          %7.3f %%" % pred_corr)
    print("  predicted, independent terms (01)          %7.3f %%" % pred_indep)
    print("  native MM_ON=1 measurement (01)            %7.3f %%" % mc["sigma_over_mu_pct"])
    print("  HANDOFF section 4 prototype                %7.3f %%" % 3.71)
    print()
    print("wrote results/04_external_proto.json")
