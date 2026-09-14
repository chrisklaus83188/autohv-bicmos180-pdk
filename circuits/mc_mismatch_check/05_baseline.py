"""Freeze the MC realism program baseline (brief Phase 0, item 2).

Collects the v2.2 measurements that later phases must reproduce or explain into
pdk_validation/baselines/mc_baseline_v2.2.json:

  * provenance: program base commit, generating commit, ngspice version
  * HANDOFF_monte_carlo.md section 1 values, as recorded and as re-measured (01)
  * the M sweep (02), the runtime table (03), the external-driver prototype (04)
  * the pre-registered expected movers (brief section 8 as amended by the rulings)

Run after 01-04.  No wall-clock timestamps are written, so re-running on the same
commit with the same results produces the same file.
"""
import json
import subprocess
from pathlib import Path

import mc_lib as M

REPO = M.HERE.parents[1]
OUT = REPO / "pdk_validation" / "baselines" / "mc_baseline_v2.2.json"


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


def load(name):
    return json.load(open(M.RESULTS / name))


mc = load("01_mc_mirror.json")
msw = load("02_m_sweep.json")
rt = load("03_runtime.json")
ext = load("04_external_proto.json")

base = git("merge-base", "HEAD", "origin/main")
baseline = {
    "provenance": {
        "program": "MC realism (v2.3-stats)",
        "base_commit": base,
        "base_describe": git("describe", "--tags", "--always", base),
        "generated_at_commit": git("rev-parse", "HEAD"),
        "ngspice_version": M.ngspice_version(),
        "model_tag": M.MODEL_TAG,
        "sources": ["circuits/mc_mismatch_check/results/01_mc_mirror.json",
                    "circuits/mc_mismatch_check/results/02_m_sweep.json",
                    "circuits/mc_mismatch_check/results/03_runtime.json",
                    "circuits/mc_mismatch_check/results/04_external_proto.json"],
    },
    "mirror_nmos50_mismatch_only": {
        "circuit": "NMOS50 mirror W=4.7u L=1u, Iref 10 uA, Vout 2.5 V, TT, 5.0 V, 27 C",
        "nrun": mc["provenance"]["nrun"],
        "pattern": mc["provenance"]["pattern"],
        "handoff_section1": {"sigma_over_mu_pct": 4.33, "sigma_delvto_dev1_mV": 5.263,
                             "mean_iout_uA": 10.649, "gain_zero_mismatch": 1.0640,
                             "gm_over_id": 5.58},
        "measured": {
            "sigma_over_mu_pct": mc["sigma_over_mu_pct"],
            "sigma_delvto_dev1_mV": mc["delvto_dev1"]["std"] * 1e3,
            "sigma_delvto_pair_diff_mV": mc["delvto_pair_diff"]["std"] * 1e3,
            "mean_iout_uA": mc["iout"]["mean"] * 1e6,
            "gain_zero_mismatch": mc["gain_zero_mismatch"],
            "gm_over_id": mc["gm_over_id_mean"],
            "distinct_samples": mc["iout"]["distinct"],
        },
        "wrapper_formula": mc["prediction"],
    },
    "m_sweep": [{k: g[k] for k in ("key", "W_um", "L_um", "M", "total_area_um2",
                                   "sigma_delvto_pooled_mV", "sigma_delvto_dev1_mV",
                                   "formula_v2_2_mV", "formula_R1_mV",
                                   "sigma_over_mu_pct", "handoff_section3")}
                for g in msw["geometries"]],
    "m_sweep_nrun_per_geometry": msw["provenance"]["nrun_per_geometry"],
    "runtime_200_samples": {"host": rt["provenance"]["host"],
                            "best_s": {k: p["best_s"] for k, p in rt["patterns"].items()},
                            "handoff_section4_s": rt["handoff_section4_s"]},
    "external_driver_prototype": {
        "sigma_over_mu_pct": ext["sigma_over_mu_pct"],
        "bit_identical_on_repeat": ext["bit_identical_on_repeat"],
        "z_seed": ext["provenance"]["z_seed"],
        "prediction": ext["prediction"],
        "handoff_section4_sigma_over_mu_pct": ext["handoff_section4_sigma_over_mu_pct"],
    },
    "preregistered_movers": [
        {"quantity": "NMOS50 mirror sigma/mu, M=1, N=200", "before": "4.33 %",
         "expected_after": "4.0-4.6 %", "why": "notation-only change + new seeds"},
        {"quantity": "sigma(delvto) at M=4", "before": "4.96 mV",
         "expected_after": "~2.5 mV", "why": "R1"},
        {"quantity": "sigma(delvto) vs NF at fixed W", "before": "not measured",
         "expected_after": "flat", "why": "R2"},
        {"quantity": "external-driver sigma/mu", "before": "3.71 %",
         "expected_after": "~4.0-4.3 %", "why": "three independent knobs"},
        {"quantity": "sizing-guide sigma column, M=1", "before": "-",
         "expected_after": "unchanged", "why": "nothing physical changed"},
        {"quantity": "36-check corner regression", "before": "green",
         "expected_after": "green, byte-identical", "why": "A13"},
        {"quantity": "200-sample runtime (op)", "before": "0.7 s",
         "expected_after": "< 2 s", "why": "driver overhead (A11)"},
        {"quantity": "NMOS18 vth0 process 1-sigma", "before": "8.33 mV",
         "expected_after": "26.7 mV", "why": "derived from corners (rulings C6)"},
        {"quantity": "NMOS18 u0 process 1-sigma", "before": "3.33 %",
         "expected_after": "5.67 %", "why": "derived from corners (rulings C6)"},
        {"quantity": "PMOS18 u0 process 1-sigma", "before": "3.33 %",
         "expected_after": "6.33 %", "why": "derived from corners (rulings C6)"},
        {"quantity": "tox process variation", "before": "0.333 %, three independent classes",
         "expected_after": "0.333 %, one shared TOX", "why": "rulings Q8"},
        {"quantity": "NDMOS20 vto process 1-sigma", "before": "13.3 mV",
         "expected_after": "16.7 mV", "why": "derived from corners (rulings C6)"},
        {"quantity": "NDMOS20 kp process 1-sigma", "before": "3.33 %",
         "expected_after": "5.00 %", "why": "derived from corners (rulings C6)"},
        {"quantity": "every PROC_ON=1 result in the repo", "before": "e.g. mirror process+mismatch 1.344 %",
         "expected_after": "moves", "why": "derived process sigma (rulings section 3)"},
    ],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(baseline, indent=1) + "\n", encoding="utf-8", newline="\n")
print("wrote %s" % OUT.relative_to(REPO))
print("  base %s (%s), ngspice %s" % (base[:7], baseline["provenance"]["base_describe"],
                                      baseline["provenance"]["ngspice_version"]))
