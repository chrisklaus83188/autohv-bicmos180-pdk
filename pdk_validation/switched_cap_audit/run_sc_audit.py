#!/usr/bin/env python3
"""
P3.1: switched-cap precision audit.

Topology (in sample_and_hold.cir):
  Vin -> NMOS18 switch (gate = phi) -> hold node -> CMIM_STD to GND

Drive Vin with a slow ramp 0 -> 1 V over 10 us; clock phi at 1 MHz
50 % duty. After each phi falling edge (sample taken, then switch
opens), V_hnode holds approximately V_in at the sampling instant,
plus charge-injection / clock-feedthrough / settling residue.

We harvest one (V_in_sample, V_hold) pair per clock period, then:
  * fit V_hold = gain * V_in_sample + offset
  * report gain error (gain - 1) and offset
  * compute the residual RMS as a coarse SAMPLING-FIDELITY surrogate.

kT/C noise (the fundamental sampled-cap thermal-noise floor) does
*not* show up here in a deterministic .tran -- ngspice does not
inject thermal noise into a tran run. The expected magnitude is:
    sigma_kTC = sqrt(k * T / C)
              = sqrt(1.38e-23 * 300 / 10e-12)
              = 20.4 uV RMS  (at 10 pF, 300 K)
This is the floor any precision SC application has to respect; if
the residue from this audit is below ~20 uV, the deterministic SC
flow is already at the noise floor.

Usage:
  python run_sc_audit.py
  python run_sc_audit.py --cap CMIM_HI   # repeat with the high-density cap
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
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
LIB_PATH = REPO_ROOT / "autohv_bicmos180_case.lib"

# --- Test-bench parameters (kept in lockstep with sample_and_hold.cir) ---
T_CLK = 1e-6                 # 1 us clock period
T_RISE = 5e-9                # phi rise/fall edge
T_PHI_HIGH = 495e-9          # phi high duration
T_FIRST_FALL = 100e-9 + T_RISE + T_PHI_HIGH   # ~600 ns
RAMP_END = 10e-6
TRAN_STOP = 11e-6
TRAN_TSTEP = 10e-9
TRAN_MAXSTEP = 50e-9
C_HOLD_PF = 10.0             # CMIM_STD 100x100 um -> 10 pF
T_KELVIN = 300.0
KB = 1.380649e-23


def find_ngspice() -> str | None:
    cand = os.environ.get("NGSPICE_BIN")
    if cand and Path(cand).exists():
        return cand
    for name in ("ngspice_con", "ngspice_con.exe", "ngspice"):
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


DECK = """\
* P3.1 SC audit (generated): {cap_name} hold cap, NMOS18 switch.
.include "{lib}"
.param case=0
.param PROC_ON=0
.param MM_ON=0

Vin in 0 PWL(0 0 {ramp_end:g} 1 100u 1)
Vphi phi 0 PULSE(0 1.8 100n {trise:g} {trise:g} {tphi_h:g} {tclk:g})

XSW in phi hnode 0 NMOS18 W=10u L=1u M=1
XCH hnode 0 {cap_name} L=100u W=100u

.control
tran {tstep:g} {tstop:g} 0 {tmax:g} UIC
wrdata {{OUT}} v(in) v(phi) v(hnode)
quit
.endc
.end
"""


def parse_wrdata(path: Path) -> tuple[list[float], list[float], list[float], list[float]]:
    """Parse the wrdata file. Columns: t, v(in), t, v(phi), t, v(hnode).
    Returns (t, v_in, v_phi, v_hnode)."""
    t: list[float] = []
    v_in: list[float] = []
    v_phi: list[float] = []
    v_hnode: list[float] = []
    with open(path, "r") as f:
        for line in f:
            parts = line.split()
            if len(parts) < 6:
                continue
            try:
                vals = [float(p) for p in parts]
            except ValueError:
                continue
            t.append(vals[0])
            v_in.append(vals[1])
            v_phi.append(vals[3])
            v_hnode.append(vals[5])
    return t, v_in, v_phi, v_hnode


def interp(xs: list[float], ys: list[float], target: float) -> float:
    """Linear interpolation at target on a monotonic-increasing xs."""
    if target <= xs[0]:
        return ys[0]
    if target >= xs[-1]:
        return ys[-1]
    lo, hi = 0, len(xs) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if xs[mid] <= target:
            lo = mid
        else:
            hi = mid
    if xs[hi] == xs[lo]:
        return ys[lo]
    f = (target - xs[lo]) / (xs[hi] - xs[lo])
    return ys[lo] + f * (ys[hi] - ys[lo])


def find_phi_falls(t: list[float], v_phi: list[float],
                    threshold: float = 0.9) -> list[float]:
    """Return the times at which phi falls below `threshold` (=high->low)."""
    falls: list[float] = []
    prev = v_phi[0]
    for i in range(1, len(t)):
        cur = v_phi[i]
        if prev >= threshold and cur < threshold:
            # Linear interp to find exact crossing.
            if cur == prev:
                falls.append(t[i])
            else:
                f = (threshold - prev) / (cur - prev)
                falls.append(t[i - 1] + f * (t[i] - t[i - 1]))
        prev = cur
    return falls


def linear_fit(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Return (slope, intercept) least-squares fit."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    slope = sxy / sxx
    intercept = my - slope * mx
    return slope, intercept


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--cap",
        choices=("CMIM_STD", "CMIM_HI"),
        default="CMIM_STD",
        help="hold capacitor (default CMIM_STD ~ 10 pF; CMIM_HI ~ 20 pF)",
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

    # Build deck.
    lib_uri = str(LIB_PATH).replace("\\", "/")
    out_data = Path(tempfile.gettempdir()) / "sc_audit_scratch.data"
    out_uri = str(out_data).replace("\\", "/")
    deck = DECK.format(
        lib=lib_uri,
        cap_name=args.cap,
        ramp_end=RAMP_END,
        trise=T_RISE,
        tphi_h=T_PHI_HIGH,
        tclk=T_CLK,
        tstep=TRAN_TSTEP,
        tstop=TRAN_STOP,
        tmax=TRAN_MAXSTEP,
    ).replace("{OUT}", out_uri)

    # Cap is 10 pF for CMIM_STD, 20 pF for CMIM_HI.
    c_hold_pf = 10.0 if args.cap == "CMIM_STD" else 20.0

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cir", delete=False, encoding="utf-8"
    ) as f:
        f.write(deck)
        deck_path = f.name
    try:
        if out_data.exists():
            out_data.unlink()
        res = subprocess.run(
            [ngspice, "-b", deck_path],
            capture_output=True, text=True, timeout=60,
        )
        out = (res.stdout or "") + (res.stderr or "")
        if "Error" in out or "no such function" in out:
            print(f"ngspice errored:\n{out[-600:]}", file=sys.stderr)
            return 1
    finally:
        try:
            os.unlink(deck_path)
        except OSError:
            pass

    if not out_data.exists():
        print(f"ngspice did not write {out_data}", file=sys.stderr)
        return 1

    t, v_in, v_phi, v_hnode = parse_wrdata(out_data)
    out_data.unlink()
    if not t:
        print("no data rows", file=sys.stderr)
        return 1

    # --- Identify sampling instants (phi falling edges) ---
    falls = find_phi_falls(t, v_phi)
    if not falls:
        print("no phi falls found", file=sys.stderr)
        return 1

    # For each fall, sample (V_in at the fall time, V_hold a few ns
    # *after* the fall to let charge injection settle).
    settling_delay = 50e-9    # 50 ns after fall: well into hold phase
    pairs: list[tuple[float, float]] = []
    for tf in falls:
        # Skip falls that land outside the ramp + first hold window.
        if tf > TRAN_STOP - settling_delay:
            continue
        vin_sample = interp(t, v_in, tf)
        vhold_after = interp(t, v_hnode, tf + settling_delay)
        pairs.append((vin_sample, vhold_after))

    if len(pairs) < 3:
        print(f"too few sample pairs ({len(pairs)})", file=sys.stderr)
        return 1

    # --- Statistics ---
    vins = [p[0] for p in pairs]
    vhs = [p[1] for p in pairs]

    slope, intercept = linear_fit(vins, vhs)

    # Residual RMS = error after removing the linear gain+offset model.
    residuals = [(vhs[i] - (slope * vins[i] + intercept)) for i in range(len(pairs))]
    rms_resid = math.sqrt(sum(r * r for r in residuals) / len(residuals))

    # Raw per-sample error (V_hold - V_in_sampled), no linear correction.
    raw_errs = [vhs[i] - vins[i] for i in range(len(pairs))]
    max_abs_raw = max(abs(e) for e in raw_errs)
    mean_raw = sum(raw_errs) / len(raw_errs)
    rms_raw = math.sqrt(sum(e * e for e in raw_errs) / len(raw_errs))

    sigma_kTC = math.sqrt(KB * T_KELVIN / (c_hold_pf * 1e-12))

    print(f"ngspice : {ngspice}")
    print(f"lib     : {LIB_PATH}")
    print(f"cap     : {args.cap}  (~ {c_hold_pf:.0f} pF nominal)")
    print(f"samples : {len(pairs)} clock periods sampled")
    print()
    print("Per-sample raw error (V_hold_after_injection - V_in_at_sample):")
    print(f"  max |err|  = {max_abs_raw*1e6:8.2f} uV")
    print(f"  mean err   = {mean_raw*1e6:8.2f} uV   (offset surrogate)")
    print(f"  RMS err    = {rms_raw*1e6:8.2f} uV")
    print()
    print("Linear fit  V_hold = gain * V_in_sample + offset:")
    print(f"  gain       = {slope:.6f}        (gain error {(slope-1)*1e4:+8.2f} ppm of slope, ie {(slope-1)*100:+.4f} %)")
    print(f"  offset     = {intercept*1e6:+8.2f} uV")
    print(f"  RMS resid  = {rms_resid*1e6:8.2f} uV    (gain+offset removed)")
    print()
    print("Sample table (V_in -> V_hold, raw_err = V_hold - V_in):")
    for i, (vi, vh) in enumerate(pairs):
        err_uv = (vh - vi) * 1e6
        print(f"  {i:2d}  V_in={vi:7.4f} V   V_hold={vh:7.4f} V   raw_err = {err_uv:+8.2f} uV")
    print()
    print(f"Reference: kT/C noise floor at 10 pF, 300 K = {sigma_kTC*1e6:.2f} uV RMS")
    print(f"           kT/C noise floor at this cap     = "
          f"{math.sqrt(KB*T_KELVIN/(c_hold_pf*1e-12))*1e6:.2f} uV RMS "
          f"({c_hold_pf:.0f} pF)")
    print()
    print(".tran is deterministic and does not inject thermal noise; the")
    print("kT/C value above is the *target* a precision SC app has to clear.")
    print("If the residual RMS shown above is well below that floor, the")
    print("model's deterministic flow is fine and kT/C dominates in silicon.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
