#!/usr/bin/env python3
"""
Characterize the rail-to-rail INPUT comparator CMP_RR in cmp_rr.lib.

One cell whose input common-mode range spans the full supply. Because the two
input pairs hand off across CM, several quantities are CM-dependent, so this
reports them at LOW / MID / HIGH common mode (0.1 / 0.5 / 0.9 x VDD):

  * DC   - quiescent current (worst over both output states), output swing,
           small-signal DC gain, and systematic input offset (trip) at each CM.
  * TRAN - low->high / high->low propagation delay at +/-100 mV overdrive into
           a 1 pF load, taken at mid-rail.
  * MC   - Monte Carlo random input offset (sigma of the trip) at mid-rail,
           where both pairs are active; the offset<->area knob is FIN.

The offset<->area axis is the FIN knob (scales BOTH input pairs and the bottom
load mirror W & L together -> matching area ~FIN^2, offset ~1/FIN, gm/hand-off
points held): gp = normal (FIN1), lo (FIN2), lo2 (FIN3).

Usage:
  python run_rr.py                 # full run, MC N=200
  python run_rr.py --no-mc         # skip Monte Carlo (fast)
  python run_rr.py --mc-n 100
  python run_rr.py --only gp
  python run_rr.py --case 2        # SS corner (default 0=TT)

Env: NGSPICE_BIN path to ngspice_con(.exe); auto-detected if unset.
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
CMP_LIB = (HERE / "cmp_rr.lib").resolve()

# Nominal supply for this cell family (overridden per voltage-domain folder).
VSUP = 1.8
TRIP = VSUP / 2
VLO = 0.1 * VSUP
VHI = 0.9 * VSUP
# rail-to-rail characterization common modes: low / mid / high
CMS = {"lo": round(0.1 * VSUP, 2), "mid": round(0.5 * VSUP, 2), "hi": round(0.9 * VSUP, 2)}

# ------------------------------------------------------------------ variants
# Offset<->area trio via FIN (gp=normal/low-area, lo, lo2). Same IREF.
VARIANTS = {
    "gp":  dict(IREF=5e-6, FIN=1),   # normal / low area
    "lo":  dict(IREF=5e-6, FIN=2),   # lower offset
    "lo2": dict(IREF=5e-6, FIN=3),   # lowest offset
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
    for p in (r"C:\Program Files\Qucs-S-25.2.0-win64\bin\ngspice_con.exe",
              r"C:\Spice64\bin\ngspice_con.exe",
              r"C:\Program Files\ngspice\bin\ngspice_con.exe"):
        if Path(p).exists():
            return p
    sys.exit("ngspice not found; set NGSPICE_BIN")


NG = None  # filled in main()


def inst_line(v: dict) -> str:
    return (f"X1 inp inn out vdd 0 ibp_5uA CMP_RR "
            f"IREF={v['IREF']:g} FIN={v.get('FIN', 1):g}")


def bias_line(v: dict) -> str:
    return f"Ib vdd ibp_5uA {v['IREF']:g}"   # IREF sourced from vdd into ibp_5uA


def header(case: int, proc: int, mm: int) -> str:
    return (f'.include "{PDK_LIB}"\n.include "{CMP_LIB}"\n'
            f".param case={case} PROC_ON={proc} MM_ON={mm}\n"
            f".param VDD={VSUP:g}\nVdd vdd 0 {VSUP:g}\n")


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


def fatal(out: str):
    for pat in ERROR_PATTERNS:
        m = pat.search(out)
        if m:
            return out[m.start():m.start() + 80].splitlines()[0]
    return None


# ---------------------------------------------------------------- analyses
def dc_deck(v: dict, case: int, cm: float, mm: int = 0) -> str:
    return (header(case, 0, mm) +
            f"Vcm cm 0 {cm}\n"
            "Vinn inn cm 0\n"
            "Vinp inp cm -0.05\n" +
            inst_line(v) + "\n" + bias_line(v) + "\n"
            "CL out 0 1p\n"
            ".control\n"
            "  op\n  let iqlo = abs(i(Vdd))\n  print iqlo\n"
            "  alter Vinp 0.05\n  op\n  let iqhi = abs(i(Vdd))\n  print iqhi\n"
            "  alter Vinp -0.05\n"
            "  dc Vinp -0.05 0.05 0.00005\n"
            f"  meas dc vtrip when v(out)={TRIP:g}\n"
            "  meas dc voh max v(out)\n  meas dc vol min v(out)\n"
            f"  meas dc vin_lo when v(out)={VLO:g}\n"
            f"  meas dc vin_hi when v(out)={VHI:g}\n"
            ".endc\n.end\n")


def tran_deck(v: dict, case: int, cm: float) -> str:
    return (header(case, 0, 0) +
            f"Vinn inn 0 {cm}\n"
            f"Vinp inp 0 PULSE({cm-0.1} {cm+0.1} 1u 1n 1n 2u 4u)\n" +
            inst_line(v) + "\n" + bias_line(v) + "\n"
            "CL out 0 1p\n"
            ".control\n  tran 0.5n 5u\n"
            f"  meas tran tpd_lh TRIG v(inp) VAL={cm} RISE=1 TARG v(out) VAL={TRIP:g} RISE=1\n"
            f"  meas tran tpd_hl TRIG v(inp) VAL={cm} FALL=1 TARG v(out) VAL={TRIP:g} FALL=1\n"
            ".endc\n.end\n")


def area_um2(v: dict) -> float:
    fin = v.get("FIN", 1)
    u = 1e-6
    devs = [  # (W, L) all M=1
        (10e-6, 1e-6), (10e-6, 1e-6), (20e-6, 1e-6),          # rbn, mir, rbp
        (20e-6, 1e-6), (20e-6, 1e-6), (10e-6, 1e-6),          # vc1, vc2, isk (vcp bias)
        (20e-6, 1e-6),                                         # NMOS tail
        (40e-6 * fin, 1e-6 * fin), (40e-6 * fin, 1e-6 * fin),  # NMOS pair (xFIN)
        (40e-6, 1e-6),                                         # PMOS tail
        (80e-6 * fin, 1e-6 * fin), (80e-6 * fin, 1e-6 * fin),  # PMOS pair (xFIN)
        (60e-6, 1e-6), (60e-6, 1e-6),                          # fold sources
        (40e-6, 1e-6), (40e-6, 1e-6),                          # cascodes
        (20e-6 * fin, 1e-6 * fin), (20e-6 * fin, 1e-6 * fin),  # bottom mirror (xFIN)
        (40e-6, 1e-6), (40e-6, 1e-6),                          # stage2
        (20e-6, 0.5e-6), (10e-6, 0.5e-6),                      # buffer
    ]
    return sum(w * l for w, l in devs) / (u * u)


def characterize(name: str, v: dict, case: int, mc_n: int) -> dict:
    r = {"variant": name, "FIN": v["FIN"], "area_um2": area_um2(v)}

    # DC at low / mid / high CM
    r["vos_sys_mV"] = {}
    for cmlabel, cm in CMS.items():
        out = run_deck(dc_deck(v, case, cm))
        err = fatal(out)
        if err:
            r.setdefault("error", err)
            continue
        if cmlabel == "mid":
            iqlo, iqhi = meas(out, "iqlo") or 0, meas(out, "iqhi") or 0
            r["iq_uA"] = max(iqlo, iqhi) * 1e6
            r["voh"], r["vol"] = meas(out, "voh"), meas(out, "vol")
            lo, hi = meas(out, "vin_lo"), meas(out, "vin_hi")
            if lo is not None and hi is not None and hi != lo:
                res = abs(hi - lo)
                r["resolution_mV"] = res * 1e3
                r["gain_dB"] = 20 * math.log10((VHI - VLO) / res)
        t = meas(out, "vtrip")
        r["vos_sys_mV"][cmlabel] = t * 1e3 if t is not None else None

    # speed at mid-rail
    out = run_deck(tran_deck(v, case, CMS["mid"]))
    if not fatal(out):
        lh, hl = meas(out, "tpd_lh"), meas(out, "tpd_hl")
        r["tpd_lh_ns"] = lh * 1e9 if lh is not None else None
        r["tpd_hl_ns"] = hl * 1e9 if hl is not None else None

    # Monte Carlo random offset at mid-rail
    if mc_n > 0:
        trips = []
        for _ in range(mc_n):
            o = run_deck(dc_deck(v, case, CMS["mid"], mm=1))
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
    ap.add_argument("--mc-n", type=int, default=200)
    ap.add_argument("--no-mc", action="store_true")
    ap.add_argument("--json", default="comparator_results.json")
    args = ap.parse_args()

    NG = find_ngspice()
    mc_n = 0 if args.no_mc else args.mc_n
    names = args.only or list(VARIANTS)

    rows = []
    for name in names:
        sys.stdout.write(f"  {name:6s} ... "); sys.stdout.flush()
        r = characterize(name, VARIANTS[name], args.case, mc_n)
        rows.append(r)
        print("ERR: " + r["error"] if "error" in r else "ok")

    print(f"\nRail-to-rail comparator  case={args.case}  Vdd={VSUP:g}  CL=1pF  overdrive=100mV")
    print("(offset rows: systematic trip at low/mid/high CM; sigma = MC at mid-rail)\n")
    cols = [("variant", "var", "{}"), ("FIN", "FIN", "{:g}"),
            ("iq_uA", "Iq[uA]", "{:.1f}"), ("vos_sigma_mV", "Vos_sig[mV]", "{:.2f}"),
            ("gain_dB", "gain[dB]", "{:.0f}"), ("tpd_lh_ns", "tpdLH[ns]", "{:.1f}"),
            ("tpd_hl_ns", "tpdHL[ns]", "{:.1f}"), ("area_um2", "area[um2]", "{:.0f}")]
    head = " ".join(f"{h:>11s}" for _, h, _ in cols)
    print(head); print("-" * len(head))
    for r in rows:
        cells = [f"{fmt(r.get(k), s):>11s}" for k, _, s in cols]
        print(" ".join(cells))
    # systematic-offset-vs-CM detail
    print("\nSystematic offset (mV) vs CM:   low / mid / high")
    for r in rows:
        vs = r.get("vos_sys_mV", {})
        print(f"  {r['variant']:5s}  {fmt(vs.get('lo'),'{:+.2f}'):>7s} /"
              f" {fmt(vs.get('mid'),'{:+.2f}'):>7s} /"
              f" {fmt(vs.get('hi'),'{:+.2f}'):>7s}")

    Path(HERE / args.json).write_text(json.dumps(rows, indent=2))
    print(f"\nWrote {args.json}")


if __name__ == "__main__":
    main()
