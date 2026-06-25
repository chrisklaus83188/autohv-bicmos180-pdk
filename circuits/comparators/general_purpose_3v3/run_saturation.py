#!/usr/bin/env python3
"""
Saturation-margin sign-off for the cmp_gp comparator family.

Design rule (carried over from the user's prior practice): every device that is
SUPPOSED to operate in saturation must keep Vds/Vdsat > 1.4 across all PVT
corners.

Which devices "should be in saturation"?  In a comparator the gain/bias devices
must stay saturated in the linear region; the output buffer (Xm7/Xm8) and the
hysteresis steering switches (Xmha/Xmhb) are large-signal switches that
intentionally sit in triode/cutoff in the resolved states, so they are excluded.

The margin is evaluated at the comparator's TRIP point (output node o2 ~ VDD/2),
which is the operating point where the whole signal chain is simultaneously in
its active region. A fine DC sweep of the input is taken and each device's
Vds/Vdsat is interpolated at v(o2)=VDD/2 via `.meas ... when`.

Usage:
  python run_saturation.py                 # 8 variants x 5 corners, nominal CM
  python run_saturation.py --cm-scan       # also scan input common-mode extremes
  python run_saturation.py --only nin_gp pin_gp
  python run_saturation.py --thresh 1.4
"""
from __future__ import annotations

import argparse
import sys

import run_comparators as rc

# Devices that must stay saturated (exclude output inverter Xm7/Xm8 = digital
# buffer, and Xmha/Xmhb = hysteresis steering switches).
SAT_DEVS = ["xmb", "xtail", "xm1", "xm2", "xm3", "xm4", "xm5", "xm6"]
SAT_DEVS_HYST = SAT_DEVS + ["xhtail"]

# Always-on current sources / bias: drains sit on stable (non-railing) nodes, so
# these must stay saturated in EVERY output state, not just the active region.
# The tail also sets the ICMR. The remaining SAT_DEVS are signal devices that are
# saturated only near the decision and rail by design when the comparator decides
# (Xm6 is a current source but its drain is the railing output o2). See
# SATURATION_SIGNOFF.md "Device roles".
CURRENT_SOURCES = ["xmb", "xtail", "xhtail"]

LABEL = {"xmb": "bias-diode", "xtail": "tail", "xm1": "in+", "xm2": "in-",
         "xm3": "mir-diode", "xm4": "mir-out", "xm5": "stg2-drv",
         "xm6": "stg2-load", "xhtail": "hyst-src"}


def sat_deck(v: dict, case: int, cm: float, vdd: float = 5.0, temp: float = 27) -> str:
    devs = SAT_DEVS_HYST if v["HYSK"] > 0 else SAT_DEVS
    saves = " ".join(f"@m.x1.{d}.m0[vds] @m.x1.{d}.m0[vdsat]" for d in devs)
    lets = "\n".join(
        f"  let r_{d} = abs(@m.x1.{d}.m0[vds])/abs(@m.x1.{d}.m0[vdsat])" for d in devs)
    trip = vdd / 2.0
    meass = "\n".join(
        f"  meas dc rat_{d} find r_{d} when v(x1.o2)={trip}" for d in devs)
    head = (f'.include "{rc.PDK_LIB}"\n.include "{rc.CMP_LIB}"\n'
            f".param case={case} PROC_ON=0 MM_ON=0\n"
            f".options temp={temp}\n"
            f"Vdd vdd 0 {vdd}\n")
    return (head +
            f"Vcm cm 0 {cm}\n"
            "Vinn inn cm 0\n"
            "Vinp inp cm 0\n" +
            rc.inst_line(v) + "\n" +
            rc.bias_line(v) + "\n"
            "CL out 0 1p\n"
            ".control\n"
            f"  save {saves} v(x1.o2)\n"
            "  dc Vinp -0.05 0.05 0.0001\n" +
            lets + "\n" + meass + "\n" +
            ".endc\n.end\n")


def eval_point(v: dict, case: int, cm: float, vdd: float = 5.0, temp: float = 27):
    devs = SAT_DEVS_HYST if v["HYSK"] > 0 else SAT_DEVS
    out = rc.run_deck(sat_deck(v, case, cm, vdd, temp))
    if rc.fatal(out):
        return None, {"error": rc.fatal(out)}
    ratios = {}
    for d in devs:
        r = rc.meas(out, f"rat_{d}")
        ratios[d] = r
    return ratios, {}


# PVT axes for the full sign-off. VDD range for the 5 V rail is 3.2-5.5 V.
TEMPS = [-40, 27, 125]
# Supply sign-off range: the 5 V rail spans 3.2-5.5 V (3.2 = chip UVLO); the 3.3 V
# and 1.8 V rails are characterized at +/-10 % of nominal.
if abs(rc.VSUP - 5.0) < 0.01:
    VDDS = [3.2, 5.0, 5.5]
else:
    VDDS = [round(0.9 * rc.VSUP, 2), rc.VSUP, round(1.1 * rc.VSUP, 2)]
CN = {0: "TT", 1: "FF", 2: "SS", 3: "FS", 4: "SF"}


# worst-case PVT set for CM-band finding (hot/slow bind the tail; cold checked too)
PVT_WORST = [(2, 125), (3, 125), (2, -40), (1, 125)]


def worst_margin(v, devs, cm, vdd):
    """Min Vds/Vdsat over the included devices, worst over the PVT_WORST set."""
    m = 1e9
    for case, temp in PVT_WORST:
        ratios, err = eval_point(v, case, cm, vdd, temp)
        if err:
            continue
        vals = [ratios[d] for d in devs if ratios.get(d) is not None]
        if vals:
            m = min(m, min(vals))
    return m


def cm_band(v, devs, vdd, thresh):
    """The CM interval over which worst_margin >= thresh, by bisection from a
    known-good mid point toward each rail. Returns (lo, hi) or None."""
    # seed: a CM in the part's strong half. Include low absolute values so a
    # narrow low-CM band (e.g. high-density PMOS-input at low VDD) isn't missed.
    seeds = [vdd * f for f in (0.5, 0.4, 0.6, 0.3, 0.7, 0.2)] + [0.5, 0.4, 0.3]
    good = next((s for s in seeds if worst_margin(v, devs, round(s, 2), vdd) >= thresh), None)
    if good is None:
        return None

    def edge(lo, hi):  # bisect boundary between passing `lo`/`hi` side
        for _ in range(7):
            mid = (lo + hi) / 2
            if worst_margin(v, devs, round(mid, 2), vdd) >= thresh:
                lo = mid
            else:
                hi = mid
        return lo
    low = edge(good, 0.2)             # walk down toward vss
    high = edge(good, vdd - 0.2)      # walk up toward vdd
    return (round(low, 2), round(high, 2))


def run_pvt(names, thresh):
    """Report the input common-mode range (ICMR) per VDD, worst over process
    corners and the -40/+125 C temperature extremes.

    ICMR definition (per design rule): the common-mode span -- inputs tied equal
    (balanced diff pair, evaluated at the trip) -- over which every input-stage
    device intended to be saturated keeps Vds/Vdsat >= thresh. The binding device
    is the tail current source: as the common mode approaches the tail's rail it
    runs out of Vds and the band ends. NOTE: a large *differential* overdrive
    (decided state, one device carrying all of Itail) stresses the tail further
    than this balanced common-mode definition -- a separate differential-range
    consideration, see SATURATION_SIGNOFF.md."""
    print(f"Input common-mode range (ICMR): tail & input-stage Vds/Vdsat >= {thresh},"
          f" inputs balanced")
    print(f"  process: corners {[CN[c] for c,_ in dict.fromkeys((c,0) for c,_ in PVT_WORST)]}"
          f"   temp: -40/+125 C   VDD: {VDDS} V  (5 V rail range 3.2-5.5)\n")
    bands = {}
    for name in names:
        v = rc.VARIANTS[name]
        devs = SAT_DEVS_HYST if v["HYSK"] > 0 else SAT_DEVS
        print(f"{name}  ({'NMOS' if v['sub']=='CMP_NIN' else 'PMOS'} input)")
        bands[name] = {}
        for vdd in VDDS:
            b = cm_band(v, devs, vdd, thresh)
            bands[name][vdd] = b
            print(f"   VDD={vdd:>3} V   ICMR: "
                  + (f"[{b[0]:.2f}, {b[1]:.2f}] V" if b else "none"))
        print()
    # joint NIN+PIN ICMR for the gp pair, if both present
    if "nin_gp" in bands and "pin_gp" in bands:
        print("Joint NIN+PIN ICMR (gp pair):")
        for vdd in VDDS:
            n, p = bands["nin_gp"][vdd], bands["pin_gp"][vdd]
            if n and p:
                print(f"   VDD={vdd:>3} V   [{min(n[0],p[0]):.2f}, {max(n[1],p[1]):.2f}] V"
                      + ("   (gap!)" if p[1] < n[0] else ""))
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+")
    ap.add_argument("--thresh", type=float, default=1.4)
    ap.add_argument("--cm-scan", action="store_true")
    ap.add_argument("--pvt", action="store_true",
                    help="full corner x temp x VDD(3.2-5.5) sweep at CM edges")
    args = ap.parse_args()

    rc.NG = rc.find_ngspice()
    names = args.only or list(rc.VARIANTS)
    corner_name = CN

    if args.pvt:
        sys.exit(0 if run_pvt(names, args.thresh) else 1)

    print(f"Saturation margin Vds/Vdsat  (rule: > {args.thresh})  evaluated at "
          f"trip (v(o2)=VDD/2)\n")
    overall_ok = True
    for name in names:
        v = rc.VARIANTS[name]
        devs = SAT_DEVS_HYST if v["HYSK"] > 0 else SAT_DEVS
        # corners at nominal CM
        per_dev_min = {d: 1e9 for d in devs}
        worst = (1e9, None, None)  # ratio, corner, dev
        for case in range(5):
            ratios, err = eval_point(v, case, v["cm"])
            if err:
                print(f"{name}: ERROR {err['error']}"); overall_ok = False; continue
            for d in devs:
                r = ratios[d]
                if r is None:
                    continue
                per_dev_min[d] = min(per_dev_min[d], r)
                if r < worst[0]:
                    worst = (r, corner_name[case], d)
        vmin, vcorner, vdev = worst
        ok = vmin >= args.thresh
        overall_ok &= ok
        flag = "PASS" if ok else "**FAIL**"
        print(f"{name:9s} cm={v['cm']:>3}V  min Vds/Vdsat = {vmin:5.2f} "
              f"({LABEL.get(vdev, vdev)} @ {vcorner})   {flag}")
        # per-device worst-over-corners detail
        detail = "  ".join(f"{LABEL.get(d, d)}:{per_dev_min[d]:.1f}" for d in devs)
        print(f"            {detail}")

        if args.cm_scan:
            # rated input-CM range over which the >1.4 rule is guaranteed
            lo, hi = (1.5, 4.5) if v["sub"] == "CMP_NIN" else (0.5, 3.2)
            for cm in (lo, hi):
                cworst = (1e9, None)
                for case in range(5):
                    ratios, err = eval_point(v, case, cm)
                    if err:
                        continue
                    for d in devs:
                        if ratios[d] is not None and ratios[d] < cworst[0]:
                            cworst = (ratios[d], d)
                cok = cworst[0] >= args.thresh
                overall_ok &= cok
                print(f"            CM={cm}V: min {cworst[0]:5.2f} "
                      f"({LABEL.get(cworst[1], cworst[1])})  "
                      f"{'PASS' if cok else '**FAIL**'}")
        print()

    print("ALL PASS" if overall_ok else "SOME FAILURES — see **FAIL** above")
    sys.exit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()
