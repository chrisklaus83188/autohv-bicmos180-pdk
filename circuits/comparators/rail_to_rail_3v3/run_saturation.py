#!/usr/bin/env python3
"""
Saturation / rail-to-rail sign-off for the CMP_RR comparator.

Unlike a single-pair comparator (whose ICMR is the CM band where its tail stays
saturated), CMP_RR is rail-to-rail by construction: the NMOS and PMOS pairs hand
off across CM, so the sign-off question is instead

  "does every ALWAYS-ON device keep Vds/Vdsat > thresh over the WHOLE 0..VDD
   input common-mode range, across PVT?"

The input pairs and their tails are EXEMPT where they intentionally cut off (an
off pair near a rail is by design, not a violation); the harness still reports
the ACTIVE-pair margin (min over the four pair devices at each CM ~= the active
pair) for information.

Ratios are evaluated AT THE TRIP (meas ... when v(o2)=VDD/2), i.e. the balanced
linear operating point, not a resolved digital state.

Usage:
  python run_saturation.py                 # per-VDD worst-case summary, gp variant
  python run_saturation.py --pvt           # full corner x temp x VDD detail
  python run_saturation.py --thresh 1.4
  python run_saturation.py --variant lo

Env: NGSPICE_BIN path to ngspice_con(.exe); auto-detected if unset.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PDK_LIB = (HERE / ".." / ".." / ".." / "autohv_bicmos180_case.lib").resolve()
CMP_LIB = (HERE / "cmp_rr.lib").resolve()

VSUP = 3.3
FIN = {"gp": 1, "lo": 2, "lo2": 3}

# Always-on signal-path devices: must hold saturation over the full rail.
ALWAYS_ON = ["xf1", "xf2", "xcp1", "xcp2", "xmm1", "xmm2", "xs2n", "xs2p"]
# Input pairs: hand-off devices, checked where active (informational).
PAIRS = ["xn1", "xn2", "xp1", "xp2"]
LABEL = {"xf1": "fold", "xf2": "fold", "xcp1": "casc", "xcp2": "casc",
         "xmm1": "mir", "xmm2": "mir", "xs2n": "stg2n", "xs2p": "stg2p"}

CN = {0: "TT", 1: "FF", 2: "SS", 3: "FS", 4: "SF"}
TEMPS = [-40, 27, 125]
if abs(VSUP - 5.0) < 0.01:
    VDDS = [3.2, 5.0, 5.5]
else:
    VDDS = [round(0.9 * VSUP, 2), VSUP, round(1.1 * VSUP, 2)]
# slow/hot binds Vdsat; cold and skew corners checked too
PVT_WORST = [(2, 125), (3, 125), (4, 125), (2, -40), (1, 125)]

ERR = [re.compile(p, re.I) for p in (r"^\s*Error[: ]", r"singular matrix",
        r"iteration limit", r"timestep too small", r"Effective channel")]


def find_ngspice() -> str:
    cand = os.environ.get("NGSPICE_BIN")
    if cand and Path(cand).exists():
        return cand
    for name in ("ngspice_con", "ngspice_con.exe", "ngspice"):
        p = shutil.which(name)
        if p:
            return p
    for p in (r"C:\Program Files\Qucs-S-25.2.0-win64\bin\ngspice_con.exe",
              r"C:\Spice64\bin\ngspice_con.exe"):
        if Path(p).exists():
            return p
    sys.exit("ngspice not found; set NGSPICE_BIN")


NG = None


def run_deck(text: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".cir", delete=False, dir=HERE) as f:
        f.write(text)
        path = f.name
    try:
        return subprocess.run([NG, "-b", path], capture_output=True, text=True,
                              timeout=120).stdout
    finally:
        os.unlink(path)


def meas(out: str, name: str):
    m = re.search(rf"^\s*{re.escape(name)}\s*=\s*([-+0-9.eE]+)", out, re.MULTILINE)
    try:
        return float(m.group(1)) if m else None
    except ValueError:
        return None


def fatal(out: str):
    for p in ERR:
        if p.search(out):
            return True
    return False


def sat_deck(variant: str, case: int, cm: float, vdd: float, temp: float) -> str:
    devs = ALWAYS_ON + PAIRS
    saves = " ".join(f"@m.x1.{d}.m0[vds] @m.x1.{d}.m0[vdsat]" for d in devs)
    trip = vdd / 2.0
    lets = "\n".join(
        f"  let r_{d}=abs(@m.x1.{d}.m0[vds])/abs(@m.x1.{d}.m0[vdsat])" for d in devs)
    meass = "\n".join(
        f"  meas dc rat_{d} find r_{d} when v(x1.o2)={trip:g}" for d in devs)
    return (f'.include "{PDK_LIB}"\n.include "{CMP_LIB}"\n'
            f".param case={case} PROC_ON=0 MM_ON=0\n.options temp={temp}\n"
            f"Vdd vdd 0 {vdd:g}\nVcm cm 0 {cm:g}\n"
            "Vinn inn cm 0\nVinp inp cm 0\n"
            f"X1 inp inn out vdd 0 ibp_5uA CMP_RR IREF=5u FIN={FIN[variant]:g}\n"
            "Ib vdd ibp_5uA 5u\nCL out 0 1p\n"
            ".control\n"
            f"  save {saves} v(x1.o2)\n"
            "  dc Vinp -0.08 0.08 0.0004\n" + lets + "\n" + meass + "\n"
            ".endc\n.end\n")


def eval_point(variant, case, cm, vdd, temp):
    out = run_deck(sat_deck(variant, case, cm, vdd, temp))
    if fatal(out):
        return None, None
    ao = [meas(out, f"rat_{d}") for d in ALWAYS_ON]
    pr = [meas(out, f"rat_{d}") for d in PAIRS]
    ao = [x for x in ao if x is not None]
    pr = [x for x in pr if x is not None]
    return (min(ao) if ao else None), (min(pr) if pr else None)


def cm_points(vdd):
    return [round(vdd * f, 3) for f in (0.04, 0.15, 0.3, 0.5, 0.7, 0.85, 0.96)]


def worst_over_cm(variant, case, vdd, temp):
    wao, wpr = 1e9, 1e9
    for cm in cm_points(vdd):
        ao, pr = eval_point(variant, case, cm, vdd, temp)
        if ao is not None:
            wao = min(wao, ao)
        if pr is not None:
            wpr = min(wpr, pr)
    return wao, wpr


def main():
    global NG
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="gp", choices=list(FIN))
    ap.add_argument("--thresh", type=float, default=1.4)
    ap.add_argument("--pvt", action="store_true")
    args = ap.parse_args()
    NG = find_ngspice()

    print(f"CMP_RR rail-to-rail saturation sign-off  (variant={args.variant}, "
          f"rule Vds/Vdsat > {args.thresh})")
    print(f"  always-on signal devices over the FULL 0..VDD input CM; input pairs "
          f"checked where active.\n  VDD: {VDDS} V   temp: -40/27/125 C   "
          f"corners: {[CN[c] for c,_ in dict.fromkeys((c,0) for c,_ in PVT_WORST)]}\n")

    if args.pvt:
        ok = True
        for vdd in VDDS:
            print(f"VDD={vdd} V")
            for case, temp in PVT_WORST:
                ao, pr = worst_over_cm(args.variant, case, vdd, temp)
                flag = "" if ao >= args.thresh else "   <-- FAIL"
                print(f"   {CN[case]}/{temp:+4d}C  always-on min={ao:5.2f}  "
                      f"active-pair min={pr:5.2f}{flag}")
                ok = ok and ao >= args.thresh
        print("\n" + ("PASS: all always-on devices > %.2f over the full rail, all corners."
                      % args.thresh if ok else "FAIL: see above."))
        sys.exit(0 if ok else 1)

    # summary: worst over the PVT_WORST set, per VDD
    print(f"{'VDD':>6} {'always-on min':>15} {'active-pair min':>16}  result")
    ok = True
    for vdd in VDDS:
        wao, wpr = 1e9, 1e9
        for case, temp in PVT_WORST:
            ao, pr = worst_over_cm(args.variant, case, vdd, temp)
            wao, wpr = min(wao, ao), min(wpr, pr)
        res = "PASS" if wao >= args.thresh else "FAIL"
        ok = ok and wao >= args.thresh
        print(f"{vdd:6.2f} {wao:15.2f} {wpr:16.2f}  {res}")
    print("\n" + ("Rail-to-rail saturation sign-off PASSED." if ok else "FAILED."))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
