#!/usr/bin/env python3
"""
Phase E: Monte Carlo validation of mismatch / process flow.

Goals (per handoff P1 "Monte Carlo validation"):

  1. Verify AGAUSS re-randomizes across MC iterations (not just within
     one solve).
  2. Verify the measured sigma matches the intended sigma on a known
     mismatch-sensitive testbench within reasonable statistical noise.
  3. Document the exact ngspice invocation needed for repeatable MC.

Scope here is the "validate the flow" first cut: one device family
(BSIM3 NMOS50), one bias point, one statistical axis (--axis mm or
proc). Cross-family / W*L scaling sweeps are follow-on work.

ngspice incantation (verified on 45.2):

  Each ngspice_con -b invocation re-randomizes the .param AGAUSS draws
  using a time-seeded RNG, so subprocess-per-iteration with no special
  flags is sufficient for MC. Within a single invocation, two
  subckt instances get independent draws (subckt-local .param is
  re-evaluated per X line during expansion). CLI -D rndseed=N does NOT
  affect .param AGAUSS, because .param is parsed before the .control
  block where 'set rndseed' would take effect.

AGAUSS convention in ngspice 45.2 (HSPICE-style, empirically verified):

  AGAUSS(mean, X, N) draws a Gaussian truncated at +/-X, with true
  sigma = X / N. That is, X is the bound at N sigmas, not the 1-sigma
  value. A 200-sample probe of AGAUSS(0, 1, 3) gives sigma ~ 0.34,
  range +/-1.0, confirming the X/N = 1/3 interpretation.

  Concretely: a .param like AGAUSS(0, 0.0135, 3) has true sigma 4.5 mV,
  not 13.5 mV. The numbers in autohv_bicmos180_case.lib are written
  as 3-sigma bounds; divide by 3 when reasoning about 1-sigma.

Testbench: two identical NMOS50 in saturation (Vds=3 V, Vgs=2 V),
W=10u, L=1u. Per iteration we capture i(Vd1), i(Vd2) and gm via
@m.xm1.m0[gm] / @m.xm2.m0[gm], and form log(I1/I2). Expected sigma at
this size:

  sigma(DVTH_MM, per device) = (13.5 mV / sqrt(W*L_um2)) / 3
                             = (13.5 / sqrt(10)) / 3 = 1.42 mV
  sigma(delta_Vth, pair)     = sqrt(2) * 1.42 = 2.01 mV
  gm/ID at this bias (empirical, BSIM3) ~ 1.7 V^-1
  Vth-only contribution to sigma(log(I1/I2)) ~ 0.34 %
  W/L mismatch contribution (from DWREL_MM, DLREL_MM)  ~ 0.13 %
  combined (RSS)                                       ~ 0.37 %

Usage:
  python run_mc.py                 # MM_ON=1, N=200, ~15 s wall
  python run_mc.py -n 500          # tighter statistics
  python run_mc.py --axis proc     # PROC_ON=1 instead of MM_ON=1
"""
from __future__ import annotations

import argparse
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
LIB_PATH = REPO_ROOT / "autohv_bicmos180_case.lib"

DECK_TEMPLATE = """\
* MC iteration: NMOS50 mismatch testbench (axis={axis})
.include "{lib}"
.param case=0
.param PROC_ON={proc}
.param MM_ON={mm}

Vd1 d1 0 3
Vg1 g1 0 2
Vd2 d2 0 3
Vg2 g2 0 2

XM1 d1 g1 0 0 NMOS50 W=10u L=1u M=1
XM2 d2 g2 0 0 NMOS50 W=10u L=1u M=1

.control
op
echo MC_BEGIN
print i(Vd1) i(Vd2) @m.xm1.m0[gm] @m.xm2.m0[gm]
echo MC_END
quit
.endc
.end
"""

# .lib AGAUSS values for NMOS50 (lines 53-70 of the .lib).
# All AGAUSS(mean, X, N) use the HSPICE convention: true sigma = X/N.
DVTH_3SIG_BASE = 0.0135       # V, before 1/sqrt(AUM2). True sigma = X/3.
DWREL_3SIG_BASE = 0.0075      # rel, ditto.
DLREL_3SIG_BASE = 0.0045      # rel, ditto.
AGAUSS_CLIP_N  = 3
WL_UM2 = 10                   # W * L in um^2 for the testbench
VGS = 2.0


def find_ngspice() -> str | None:
    cand = os.environ.get("NGSPICE_BIN")
    if cand and Path(cand).exists():
        return cand
    for name in ("ngspice_con", "ngspice_con.exe"):
        p = shutil.which(name)
        if p:
            return p
    for p in (
        r"C:\Spice64\bin\ngspice_con.exe",
        r"C:\Program Files\ngspice\bin\ngspice_con.exe",
    ):
        if Path(p).exists():
            return p
    return None


PRINT_RE_I = re.compile(
    r"^i\(vd([12])\)\s*=\s*(-?\d+\.\d+e[+-]?\d+)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
PRINT_RE_GM = re.compile(
    r"^@m\.xm([12])\.m0\[gm\]\s*=\s*(-?\d+\.\d+e[+-]?\d+)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def run_one(ngspice: str, deck: str) -> tuple[float, float, float, float]:
    """Returns (I_d1, I_d2, gm1, gm2) (currents as positive magnitudes)."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cir", delete=False, encoding="utf-8"
    ) as f:
        f.write(deck)
        deck_path = f.name
    try:
        res = subprocess.run(
            [ngspice, "-b", deck_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        out = (res.stdout or "") + (res.stderr or "")
    finally:
        try:
            os.unlink(deck_path)
        except OSError:
            pass

    if "no such function" in out:
        raise RuntimeError(f"ngspice errored: {out[-300:]!r}")
    if "MC_BEGIN" not in out or "MC_END" not in out:
        raise RuntimeError(f"missing MC markers: {out[-400:]!r}")

    i_found = {m.group(1): float(m.group(2)) for m in PRINT_RE_I.finditer(out)}
    gm_found = {m.group(1): float(m.group(2)) for m in PRINT_RE_GM.finditer(out)}
    if "1" not in i_found or "2" not in i_found:
        raise RuntimeError(f"could not parse i(Vd1)/i(Vd2): {out!r}")
    if "1" not in gm_found or "2" not in gm_found:
        raise RuntimeError(f"could not parse gm: {out!r}")
    # i(Vdx) is current into the Vdx '+' terminal; the drain current
    # is the load current = -i(Vdx). Return positive magnitudes.
    return -i_found["1"], -i_found["2"], gm_found["1"], gm_found["2"]


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "-n", "--iterations", type=int, default=200,
        help="number of MC iterations (default 200)",
    )
    p.add_argument(
        "--axis", choices=("mm", "proc"), default="mm",
        help="statistical axis: 'mm' = MM_ON=1, 'proc' = PROC_ON=1",
    )
    p.add_argument(
        "--tol", type=float, default=0.30,
        help=(
            "max relative deviation of measured sigma from intended sigma "
            "for the MM 'sanity' gate (default 0.30 = 30%%). Generous; "
            "this is statistical, not a tight match."
        ),
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    ngspice = find_ngspice()
    if ngspice is None:
        print("ERROR: ngspice_con not found", file=sys.stderr)
        return 2
    if not LIB_PATH.exists():
        print(f"ERROR: lib not found at {LIB_PATH}", file=sys.stderr)
        return 2

    lib_uri = str(LIB_PATH).replace("\\", "/")
    if args.axis == "mm":
        deck = DECK_TEMPLATE.format(lib=lib_uri, proc=0, mm=1, axis="mm")
        axis_label = "MM_ON=1, PROC_ON=0"
    else:
        deck = DECK_TEMPLATE.format(lib=lib_uri, proc=1, mm=0, axis="proc")
        axis_label = "PROC_ON=1, MM_ON=0"

    print(f"ngspice    : {ngspice}")
    print(f"lib        : {LIB_PATH}")
    print(f"testbench  : NMOS50, W=10u L=1u, Vds=3 V, Vgs=2 V")
    print(f"axis       : {axis_label}")
    print(f"iterations : {args.iterations}")
    print()

    # --- Re-randomization probe: two back-to-back runs at the SAME axis
    # settings. Two identical ngspice invocations should differ if the
    # default RNG re-seeds between processes; if they match exactly
    # there's a problem (e.g. AGAUSS is being constant-folded or the
    # default seed is fixed).
    a1, a2, _, _ = run_one(ngspice, deck)
    b1, b2, _, _ = run_one(ngspice, deck)
    same_in_run = (a1 == a2) and (b1 == b2)
    same_between_runs = (a1 == b1) and (a2 == b2)
    print(f"probe iter 0 : I1={a1*1e6:.3f} uA  I2={a2*1e6:.3f} uA  delta={(a1-a2)*1e6:+.3f} uA")
    print(f"probe iter 1 : I1={b1*1e6:.3f} uA  I2={b2*1e6:.3f} uA  delta={(b1-b2)*1e6:+.3f} uA")
    if same_in_run and args.axis == "mm":
        print("  WARN: M1 and M2 got identical draws in a single run -- per-instance mismatch broken?")
    if same_between_runs:
        print("  ERR: two back-to-back runs gave IDENTICAL draws -- AGAUSS not re-randomizing")
        return 1
    else:
        print("  OK: AGAUSS draws differ across runs (re-randomization confirmed)")
    print()

    # --- Full MC sweep
    samples: list[tuple[float, float, float, float]] = []
    started = time.monotonic()
    progress_every = max(1, args.iterations // 10)
    for i in range(args.iterations):
        i1, i2, g1, g2 = run_one(ngspice, deck)
        samples.append((i1, i2, g1, g2))
        if (i + 1) % progress_every == 0:
            elapsed = time.monotonic() - started
            print(f"  ... {i+1}/{args.iterations} done in {elapsed:.0f}s", flush=True)
    elapsed = time.monotonic() - started

    I1 = [s[0] for s in samples]
    I2 = [s[1] for s in samples]
    GM1 = [s[2] for s in samples]
    GM2 = [s[3] for s in samples]
    log_ratios = [math.log(s[0] / s[1]) for s in samples]

    mean_I1 = statistics.mean(I1)
    mean_I2 = statistics.mean(I2)
    mean_gm1 = statistics.mean(GM1)
    mean_gm2 = statistics.mean(GM2)
    sigma_lr = statistics.stdev(log_ratios)
    mean_lr = statistics.mean(log_ratios)

    # Per-instance ID spread (axis-independent: process moves both
    # together, mismatch moves them apart). We report it for context.
    sigma_I1_rel = statistics.stdev(I1) / mean_I1
    sigma_I2_rel = statistics.stdev(I2) / mean_I2

    # --- Intended sigma for the MM axis.
    # AGAUSS(0, X, 3) has true 1-sigma = X / 3 (HSPICE convention,
    # empirically verified on ngspice 45.2). The .lib's AGAUSS calls
    # use X = (3-sigma bound) / sqrt(W*L_um2).
    sigma_dvth_dev = DVTH_3SIG_BASE / math.sqrt(WL_UM2) / AGAUSS_CLIP_N
    sigma_dwrel_dev = DWREL_3SIG_BASE / math.sqrt(WL_UM2) / AGAUSS_CLIP_N
    sigma_dlrel_dev = DLREL_3SIG_BASE / math.sqrt(WL_UM2) / AGAUSS_CLIP_N

    sigma_dvth_pair = math.sqrt(2) * sigma_dvth_dev
    sigma_wlrel_pair = math.sqrt(2) * math.sqrt(sigma_dwrel_dev**2
                                                + sigma_dlrel_dev**2)

    # Empirical gm/ID from this run (averages out per-iteration jitter).
    gm_over_id_emp = ((mean_gm1 / mean_I1) + (mean_gm2 / mean_I2)) / 2

    sigma_lr_vth_part = gm_over_id_emp * sigma_dvth_pair
    sigma_lr_wl_part = sigma_wlrel_pair   # ID is linear in W/L
    expected_sigma_lr_mm = math.sqrt(
        sigma_lr_vth_part**2 + sigma_lr_wl_part**2
    )

    print()
    print(f"Wall: {elapsed:.1f}s for {args.iterations} iterations  "
          f"({elapsed/args.iterations*1000:.0f} ms each)")
    print()
    print("Per-device drain current:")
    print(f"  I1  mean = {mean_I1*1e6:8.3f} uA   sigma/mean = {sigma_I1_rel*100:6.3f} %")
    print(f"  I2  mean = {mean_I2*1e6:8.3f} uA   sigma/mean = {sigma_I2_rel*100:6.3f} %")
    print()
    print("Pair log-ratio  log(I1/I2):")
    print(f"  mean  = {mean_lr*100:+7.4f} %  (should be near 0; nonzero indicates RNG bias)")
    print(f"  sigma = {sigma_lr*100:7.4f} %")
    print()

    if args.axis == "mm":
        print("Intended sigma for MM axis (AGAUSS HSPICE conv: 1-sigma = X/3):")
        print(f"  sigma(DVTH_MM, per device) = ({DVTH_3SIG_BASE*1000:.1f} mV / sqrt({WL_UM2})) / 3 = "
              f"{sigma_dvth_dev*1000:.3f} mV")
        print(f"  sigma(delta_Vth, pair)     = sqrt(2) x above       = "
              f"{sigma_dvth_pair*1000:.3f} mV")
        print(f"  gm/ID (empirical from this run)                    = "
              f"{gm_over_id_emp:.3f} V^-1")
        print(f"  Vth-only contribution to sigma(log I1/I2)          = "
              f"{sigma_lr_vth_part*100:.3f} %")
        print(f"  W/L-mismatch contribution                          = "
              f"{sigma_lr_wl_part*100:.3f} %")
        print(f"  intended sigma(log I1/I2)  (RSS)                   ~ "
              f"{expected_sigma_lr_mm*100:.3f} %")
        deviation = abs(sigma_lr - expected_sigma_lr_mm) / expected_sigma_lr_mm
        print(f"  measured sigma             = {sigma_lr*100:.3f} %  "
              f"(deviation {deviation*100:.1f} %)")
        if deviation > args.tol:
            print(f"  FAIL: deviation > {args.tol*100:.0f} % tolerance")
            return 1
        print(f"  OK: within {args.tol*100:.0f} % of intended sigma")
    else:
        # PROC axis: both transistors get the SAME process shift, so the
        # pair log-ratio sigma should be effectively zero (only the
        # absolute current changes). Verify that.
        print("Intended for PROC axis:")
        print("  Per-instance current has nonzero sigma (process drift).")
        print("  Pair log-ratio sigma should be ~0 (both devices share")
        print("  one die-level draw; subckt-local mismatch draws are off).")
        if sigma_lr > 1e-4:
            print(f"  WARN: log-ratio sigma {sigma_lr*100:.4f}% larger than ~0 "
                  "-- check that PROC_ON params are not also being mismatched")
        else:
            print(f"  OK: log-ratio sigma {sigma_lr*100:.4f}% << per-device sigma "
                  f"{sigma_I1_rel*100:.3f}%")
        if sigma_I1_rel < 1e-4:
            print("  FAIL: per-device current sigma is ~0 -- PROC axis broken?")
            return 1

    print()
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
