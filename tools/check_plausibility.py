#!/usr/bin/env python3
"""Plausibility check for the statistical layer (ruling U3).

Every generated sigma must land within a stated factor (0.5-2.0x) of the comparable-class
magnitude for a process of this kind. Two rules govern this script:

  1. The comparable magnitudes are held LOCALLY and are never written to the repo. This
     script reads them from a gitignored LOCAL_* file if one is present, and records only
     the BOOLEAN outcome -- {within_band, band} -- in models/stat_model.json.

  2. A class with no comparable magnitude reports {"band": null, "within": null} with a
     note. No band is fabricated, and nothing outside a band is silently clamped: a miss
     is reported and left for a ruling.

Usage:
  python tools/check_plausibility.py            # report only
  python tools/check_plausibility.py --apply    # write the booleans into stat_model.json

The local magnitudes file, if present, is a JSON object of the form:
  {"VTH": {"33": [0.041, 0.056], "50": [0.016, 0.022], "vdmos": [0.020, 0.090]},
   "U0":  {"33": [0.04, 0.06],   "50": [0.016, 0.017]}}
Classes absent from it are reported as having no comparable magnitude.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / "models" / "stat_model.json"
LOCAL = ROOT / "LOCAL_plausibility_magnitudes.json"

BAND_LO, BAND_HI = 0.5, 2.0
NO_COMPARABLE = "no comparable class in the local reference"
NO_LOCAL_FILE = "no local magnitudes file present; check not run"

VDMOS = {"NDMOS20", "PDMOS20", "NDMOS40", "PDMOS40", "NDMOS60", "PDMOS60", "NDMOS80",
         "PDMOS80", "NDMOS120", "PDMOS120", "NDMOS200", "PDMOS200", "DNMOS20"}


def class_of(device: str) -> str:
    if device in VDMOS:
        return "vdmos"
    return re.sub(r"^[NP]MOS", "", device)


def verdict(value: float, band: list | None) -> dict:
    """The only thing that ever reaches the repo: a boolean and the band that produced it."""
    if band is None:
        return {"band": None, "within": None, "note": NO_COMPARABLE}
    lo, hi = BAND_LO * band[0], BAND_HI * band[1]
    return {"band": [round(lo, 6), round(hi, 6)],
            "within": bool(lo <= value <= hi),
            "note": ("checked against a comparable-class magnitude held locally; "
                     "the magnitude itself is never stored")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true",
                    help="write the booleans into models/stat_model.json")
    args = ap.parse_args(argv)

    model = json.loads(MODEL.read_text(encoding="utf-8"))
    gv = model["global_variables"]

    if LOCAL.exists():
        mags = json.loads(LOCAL.read_text(encoding="utf-8"))
        source = f"local magnitudes: {LOCAL.name} (gitignored)"
    else:
        mags = {}
        source = NO_LOCAL_FILE

    print(source)
    print()
    print("%-12s %-10s %10s %-22s %s" % ("variable", "class", "sigma", "band (x0.5-2.0)", "within"))

    misses, checked, unchecked = [], 0, 0
    results = {}
    for name, v in sorted(gv.items()):
        if not name.startswith("VTH_") or not isinstance(v, dict) or "sigma" not in v:
            continue
        dev = name[4:]
        cls = class_of(dev)
        band = (mags.get("VTH") or {}).get(cls)
        r = verdict(v["sigma"], band)
        results[name] = r
        if r["within"] is None:
            unchecked += 1
            shown = "-"
        else:
            checked += 1
            shown = "%.4f-%.4f" % tuple(r["band"])
            if not r["within"]:
                misses.append((name, v["sigma"], r["band"]))
        print("%-12s %-10s %10.5f %-22s %s"
              % (name, cls, v["sigma"], shown,
                 "-" if r["within"] is None else ("yes" if r["within"] else "REPORT")))

    print()
    print("checked %d, no comparable class %d, misses %d" % (checked, unchecked, len(misses)))
    for name, val, band in misses:
        ratio = val / ((band[0] / BAND_LO + band[1] / BAND_HI) / 2)
        print("   MISS %-12s sigma %.5f is %.2fx the comparable midpoint -- reported, not clamped"
              % (name, val, ratio))

    if args.apply and not LOCAL.exists():
        print()
        print("REFUSED: --apply with no local magnitudes file would overwrite every existing")
        print("verdict with null. Provide %s, or run without --apply." % LOCAL.name)
        return 1

    if args.apply:
        for name, r in results.items():
            gv[name]["plausibility"] = r
        MODEL.write_text(json.dumps(model, indent=1, ensure_ascii=True) + "\n",
                         encoding="utf-8", newline="\n")
        print()
        print("wrote plausibility booleans for %d variables" % len(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
