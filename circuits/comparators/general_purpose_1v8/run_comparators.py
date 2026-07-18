#!/usr/bin/env python3
"""
Characterize the general-purpose comparator family in cmp_gp.lib.

For each variant (NMOS-/PMOS-input x operating point) this runs, in
ngspice batch mode against the AutoHV BiCMOS 180 PDK:

  * DC   - quiescent current, systematic input offset (trip point),
           output swing VOH/VOL, and small-signal resolution / DC gain
           (input delta to drive OUT from 0.5 V to 4.5 V).
  * TRAN - low->high and high->low propagation delay at +/-100 mV overdrive,
           driving a 1 pF load.
  * HYST - (hysteresis variants only) input hysteresis window from a slow
           triangle sweep (robust to the regenerative load's DC bistability).
  * MC   - Monte Carlo random input offset: N MM_ON=1 runs, sigma of the
           trip point = input-referred 1-sigma offset.

Area is computed analytically from the variant geometry (sum of W*L*M).

Usage:
  python run_comparators.py                 # full run, MC N=40
  python run_comparators.py --no-mc         # skip Monte Carlo (fast)
  python run_comparators.py --mc-n 100      # tighter offset statistics
  python run_comparators.py --only nin_gp pin_gp
  python run_comparators.py --case 2        # SS corner (default 0=TT)

Env:
  NGSPICE_BIN   path to ngspice_con(.exe); auto-detected if unset.
"""
from __future__ import annotations

import argparse
import json
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
PDK_LIB = (HERE / ".." / ".." / ".." / "autohv_bicmos180_case.lib").resolve()
CMP_LIB = (HERE / "cmp_gp.lib").resolve()
CELLS_LIB = (HERE / ".." / ".." / "async_logic_design" / "cells.lib").resolve()   # EN buffer: PDK INV cells

# Nominal supply for this cell family (set per voltage-domain folder).
VSUP = 1.8
TRIP = VSUP / 2          # output mid-rail (trip threshold for meas)
VLO = 0.1 * VSUP         # 10% output level
VHI = 0.9 * VSUP         # 90% output level
NIN_CM = round(0.60 * VSUP, 2)   # high-CM characterization point (NMOS input)
PIN_CM = round(0.30 * VSUP, 2)   # low-CM  characterization point (PMOS input)

# ------------------------------------------------------------------ variants
# One low-area base sizing (WSCALE=0.5, LANA=1u, IREF=5u). The offset<->area axis
# is the FIN knob (scales stage-1 = input pair + load mirror, constant W/L ->
# ICMR & gm fixed, offset ~1/FIN, stage-1 area ~FIN^2). gp=normal(FIN1),
# lo=lower-offset(FIN2), lo2=lowest(FIN3). hyst/lp/fast are one-knob siblings.
#   subckt : CMP_NIN (high CM) or CMP_PIN (low CM); cm : characterization CM
VARIANTS = {
    # NMOS-input (senses high common mode); base WIN=20u
    "nin_gp":   dict(sub="CMP_NIN", cm=NIN_CM, IREF=5e-6,  WSCALE=0.5, WIN=20e-6, LIN=1e-6, LANA=1e-6, FIN=1, HYSK=0),    # normal / low-area
    "nin_lo":   dict(sub="CMP_NIN", cm=NIN_CM, IREF=5e-6,  WSCALE=0.5, WIN=20e-6, LIN=1e-6, LANA=1e-6, FIN=2, HYSK=0),    # lower offset
    "nin_lo2":  dict(sub="CMP_NIN", cm=NIN_CM, IREF=5e-6,  WSCALE=0.5, WIN=20e-6, LIN=1e-6, LANA=1e-6, FIN=3, HYSK=0),    # lowest offset
    "nin_hyst": dict(sub="CMP_NIN", cm=NIN_CM, IREF=5e-6,  WSCALE=0.5, WIN=20e-6, LIN=1e-6, LANA=1e-6, FIN=1, HYSK=0.2),  # + hysteresis
    "nin_lp":   dict(sub="CMP_NIN", cm=NIN_CM, IREF=1e-6,  WSCALE=0.5, WIN=20e-6, LIN=1e-6, LANA=1e-6, FIN=1, HYSK=0),    # low power
    "nin_fast": dict(sub="CMP_NIN", cm=NIN_CM, IREF=10e-6, WSCALE=0.5, WIN=20e-6, LIN=1e-6, LANA=1e-6, FIN=1, HYSK=0),   # fast: 2x current density (saturation-clean)
    # PMOS-input (senses low common mode); base WIN=40u (wider for lower mobility)
    "pin_gp":   dict(sub="CMP_PIN", cm=PIN_CM, IREF=5e-6,  WSCALE=0.5, WIN=40e-6, LIN=1e-6, LANA=1e-6, FIN=1, HYSK=0),
    "pin_lo":   dict(sub="CMP_PIN", cm=PIN_CM, IREF=5e-6,  WSCALE=0.5, WIN=40e-6, LIN=1e-6, LANA=1e-6, FIN=2, HYSK=0),
    "pin_lo2":  dict(sub="CMP_PIN", cm=PIN_CM, IREF=5e-6,  WSCALE=0.5, WIN=40e-6, LIN=1e-6, LANA=1e-6, FIN=3, HYSK=0),
    "pin_hyst": dict(sub="CMP_PIN", cm=PIN_CM, IREF=5e-6,  WSCALE=0.5, WIN=40e-6, LIN=1e-6, LANA=1e-6, FIN=1, HYSK=0.2),
    "pin_lp":   dict(sub="CMP_PIN", cm=PIN_CM, IREF=1e-6,  WSCALE=0.5, WIN=40e-6, LIN=1e-6, LANA=1e-6, FIN=1, HYSK=0),
    "pin_fast": dict(sub="CMP_PIN", cm=PIN_CM, IREF=10e-6, WSCALE=0.5, WIN=40e-6, LIN=1e-6, LANA=1e-6, FIN=1, HYSK=0),  # fast: 2x current density
}

ERROR_PATTERNS = [
    re.compile(r"^\s*Error[: ]", re.MULTILINE | re.IGNORECASE),
    re.compile(r"no such function", re.IGNORECASE),
    re.compile(r"singular matrix", re.IGNORECASE),
    re.compile(r"iteration limit reached", re.IGNORECASE),
    re.compile(r"timestep too small", re.IGNORECASE),
    re.compile(r"Effective channel (width|length)", re.IGNORECASE),
]


def find_ngspice() -> str:
    cand = os.environ.get("NGSPICE_BIN")
    if cand and Path(cand).exists():
        return cand
    for name in ("ngspice_con", "ngspice_con.exe", "ngspice"):
        p = shutil.which(name)
        if p:
            return p
    for p in (
        r"C:\Program Files\Qucs-S-25.2.0-win64\bin\ngspice_con.exe",
        r"C:\Spice64\bin\ngspice_con.exe",
        r"C:\Program Files\ngspice\bin\ngspice_con.exe",
    ):
        if Path(p).exists():
            return p
    sys.exit("ngspice not found; set NGSPICE_BIN")


NG = None  # filled in main()


def inst_line(v: dict) -> str:
    """The X-line instantiating the comparator under test as X1."""
    return (f"X1 inp inn out vdd 0 {('ibp_5uA' if v['sub']=='CMP_NIN' else 'ibn_5uA')} vdd {v['sub']} IREF={v['IREF']:g} "
            f"WSCALE={v['WSCALE']:g} WIN={v['WIN']:g} LIN={v['LIN']:g} "
            f"LANA={v['LANA']:g} FIN={v.get('FIN', 1):g} HYSK={v['HYSK']:g}")


def bias_line(v: dict) -> str:
    """Drive the bias pin: source IREF into ibp_5uA (NIN); sink IREF from ibn_5uA (PIN)."""
    if v["sub"] == "CMP_NIN":
        return f"Ib vdd ibp_5uA {v['IREF']:g}"
    return f"Ib ibn_5uA 0 {v['IREF']:g}"


def header(case: int, proc: int, mm: int) -> str:
    return (f'.include "{PDK_LIB}"\n'
            f'.include "{CELLS_LIB}"\n'
            f'.include "{CMP_LIB}"\n'
            f".param case={case} PROC_ON={proc} MM_ON={mm}\n"
            f".param VDD={VSUP:g}\n"
            f"Vdd vdd 0 {VSUP:g}\n")


def run_deck(text: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".cir", delete=False, dir=HERE) as f:
        f.write(text)
        path = f.name
    try:
        out = subprocess.run([NG, "-b", path], capture_output=True, text=True,
                             timeout=120).stdout
    finally:
        os.unlink(path)
    return out


def meas(out: str, name: str):
    m = re.search(rf"^\s*{re.escape(name)}\s*=\s*([-+0-9.eE]+)", out, re.MULTILINE)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def fatal(out: str) -> str | None:
    for pat in ERROR_PATTERNS:
        if pat.search(out):
            m = pat.search(out)
            return out[m.start():m.start() + 80].splitlines()[0]
    return None


# ---------------------------------------------------------------- analyses
def dc_deck(v: dict, case: int) -> str:
    return (header(case, 0, 0) +
            f"Vcm cm 0 {v['cm']}\n"
            "Vinn inn cm 0\n"
            "Vinp inp cm -0.05\n" +   # defined LOW state for a clean quiescent-current read
            inst_line(v) + "\n" +
            bias_line(v) + "\n"
            "CL out 0 1p\n"
            ".control\n"
            "  op\n"
            "  let iqlo = abs(i(Vdd))\n"   # out LOW state
            "  print iqlo\n"
            "  alter Vinp 0.05\n"
            "  op\n"
            "  let iqhi = abs(i(Vdd))\n"   # out HIGH state
            "  print iqhi\n"
            "  alter Vinp -0.05\n"
            "  dc Vinp -0.05 0.05 0.00005\n"
            f"  meas dc vtrip   when v(out)={TRIP:g}\n"
            "  meas dc voh     max v(out)\n"
            "  meas dc vol     min v(out)\n"
            f"  meas dc vin_lo  when v(out)={VLO:g}\n"
            f"  meas dc vin_hi  when v(out)={VHI:g}\n"
            ".endc\n.end\n")


def tran_deck(v: dict, case: int) -> str:
    cm = v["cm"]
    return (header(case, 0, 0) +
            "Vinn inn 0 {cm}\n".replace("{cm}", f"{cm}") +
            # rise at 1u, fall at 3u; +/-100 mV overdrive about inn
            f"Vinp inp 0 PULSE({cm-0.1} {cm+0.1} 1u 1n 1n 2u 4u)\n" +
            inst_line(v) + "\n" +
            bias_line(v) + "\n"
            "CL out 0 1p\n"
            ".control\n"
            "  tran 0.5n 5u\n"
            f"  meas tran tpd_lh TRIG v(inp) VAL={cm} RISE=1 TARG v(out) VAL={TRIP:g} RISE=1\n"
            f"  meas tran tpd_hl TRIG v(inp) VAL={cm} FALL=1 TARG v(out) VAL={TRIP:g} FALL=1\n"
            ".endc\n.end\n")


def hyst_deck(v: dict, case: int) -> str:
    cm = v["cm"]
    # quasi-static triangle +/-80 mV about inn (slow enough that tpd << ramp time,
    # so measured trips are not corrupted by the asymmetric rise/fall delays)
    return (header(case, 0, 0) +
            f"Vinn inn 0 {cm}\n"
            f"Vinp inp 0 PWL(0 {cm-0.08} 50u {cm+0.08} 100u {cm-0.08})\n" +
            inst_line(v) + "\n" +
            bias_line(v) + "\n"
            "CL out 0 1p\n"
            ".control\n"
            "  tran 20n 100u\n"
            f"  meas tran vtrip_up when v(out)={TRIP:g} RISE=1\n"
            f"  meas tran vtrip_dn when v(out)={TRIP:g} FALL=1\n"
            f"  meas tran vin_up   find v(inp) when v(out)={TRIP:g} RISE=1\n"
            f"  meas tran vin_dn   find v(inp) when v(out)={TRIP:g} FALL=1\n"
            ".endc\n.end\n")


def area_um2(v: dict) -> float:
    ws, lana, win, lin = v["WSCALE"], v["LANA"], v["WIN"], v["LIN"]
    fin = v.get("FIN", 1)                       # stage-1 matching scale (pair + load)
    u = 1e-6
    bu = (10e-6 if v["sub"] == "CMP_NIN" else 20e-6) * ws  # bias-mirror unit width
    lw = (20e-6 if v["sub"] == "CMP_NIN" else 10e-6) * ws  # stage-1 load unit width
    devs = [  # (W, L, M)
        (bu, lana, 1), (bu, lana, 2),                        # mb, tail
        (win * fin, lin * fin, 1), (win * fin, lin * fin, 1),        # input pair (xFIN)
        (lw * fin, lana * fin, 1), (lw * fin, lana * fin, 1),        # load mirror (xFIN)
        (80e-6 * ws, lana, 1), (bu, lana, 4),                # stage2 (NIN widths)
        (20e-6 * ws, 0.5e-6, 1), (10e-6 * ws, 0.5e-6, 1),    # buffer
    ]
    if v["sub"] == "CMP_PIN":  # PIN stage-2 driver = 40u; load already lw above
        devs[6] = (40e-6 * ws, lana, 1); devs[7] = (bu, lana, 4)
    if v["HYSK"] > 0:  # steering tail + two switches
        devs += [(bu * v["HYSK"], lana, 1), (bu, 0.5e-6, 1), (bu, 0.5e-6, 1)]
    return sum(w * l * m for w, l, m in devs) / (u * u)


def characterize(name: str, v: dict, case: int, mc_n: int) -> dict:
    r = {"variant": name, "input": "NMOS" if v["sub"] == "CMP_NIN" else "PMOS",
         "cm": v["cm"], "area_um2": area_um2(v)}

    out = run_deck(dc_deck(v, case))
    err = fatal(out)
    if err:
        r["error"] = err
        return r
    iqlo, iqhi = meas(out, "iqlo") or 0, meas(out, "iqhi") or 0
    r["iq_uA"] = max(iqlo, iqhi) * 1e6           # worst-case quiescent current
    r["iq_lo_uA"], r["iq_hi_uA"] = iqlo * 1e6, iqhi * 1e6
    r["voh"] = meas(out, "voh")
    r["vol"] = meas(out, "vol")
    lo, hi = meas(out, "vin_lo"), meas(out, "vin_hi")
    if lo is not None and hi is not None and hi != lo:
        res = abs(hi - lo)
        r["resolution_mV"] = res * 1e3
        r["gain_dB"] = 20 * math.log10(4.0 / res)
    if v["HYSK"] == 0:  # systematic offset = DC trip (meaningless for hysteretic)
        r["vos_sys_mV"] = (meas(out, "vtrip") or float("nan")) * 1e3

    out = run_deck(tran_deck(v, case))
    if not fatal(out):
        lh, hl = meas(out, "tpd_lh"), meas(out, "tpd_hl")
        r["tpd_lh_ns"] = lh * 1e9 if lh is not None else None
        r["tpd_hl_ns"] = hl * 1e9 if hl is not None else None

    if v["HYSK"] > 0:
        out = run_deck(hyst_deck(v, case))
        up, dn = meas(out, "vin_up"), meas(out, "vin_dn")
        if up is not None and dn is not None:
            r["hyst_mV"] = abs(up - dn) * 1e3
            r["vos_sys_mV"] = ((up + dn) / 2 - v["cm"]) * 1e3  # hysteresis center

    if mc_n > 0:
        trips = []
        for _ in range(mc_n):
            o = run_deck(dc_deck(v, case).replace("MM_ON=0", "MM_ON=1"))
            t = meas(o, "vtrip")
            if t is not None:
                trips.append(t)
        if len(trips) > 2:
            r["vos_sigma_mV"] = statistics.pstdev(trips) * 1e3
            r["mc_runs"] = len(trips)
    return r


def fmt(x, spec="{:.2f}"):
    if isinstance(x, str):
        return x
    if isinstance(x, (int, float)) and not math.isnan(x):
        return spec.format(x)
    return "--"


def main():
    global NG
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="+")
    ap.add_argument("--case", type=int, default=0)
    ap.add_argument("--mc-n", type=int, default=40)
    ap.add_argument("--no-mc", action="store_true")
    ap.add_argument("--json", default="comparator_results.json")
    args = ap.parse_args()

    NG = find_ngspice()
    mc_n = 0 if args.no_mc else args.mc_n
    names = args.only or list(VARIANTS)

    rows = []
    for name in names:
        sys.stdout.write(f"  {name:10s} ... "); sys.stdout.flush()
        r = characterize(name, VARIANTS[name], args.case, mc_n)
        rows.append(r)
        print("ERR: " + r["error"] if "error" in r else "ok")

    cols = [("variant", "variant", "{}"), ("input", "in", "{}"),
            ("iq_uA", "Iq[uA]", "{:.1f}"), ("vos_sys_mV", "Vos_sys[mV]", "{:+.2f}"),
            ("vos_sigma_mV", "Vos_sig[mV]", "{:.2f}"), ("gain_dB", "gain[dB]", "{:.0f}"),
            ("tpd_lh_ns", "tpdLH[ns]", "{:.1f}"), ("tpd_hl_ns", "tpdHL[ns]", "{:.1f}"),
            ("hyst_mV", "hyst[mV]", "{:.1f}"), ("area_um2", "area[um2]", "{:.0f}")]
    print("\nCorner case=%d  (Vdd=5, CL=1pF, overdrive=100mV)\n" % args.case)
    head = " ".join(f"{h:>11s}" for _, h, _ in cols)
    print(head); print("-" * len(head))
    for r in rows:
        cells = []
        for key, _, spec in cols:
            val = r.get(key)
            cells.append(f"{fmt(val, spec):>11s}" if val is not None else f"{'--':>11s}")
        print(" ".join(cells))

    Path(HERE / args.json).write_text(json.dumps(rows, indent=2))
    print(f"\nWrote {args.json}")


if __name__ == "__main__":
    main()
