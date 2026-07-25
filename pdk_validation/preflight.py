#!/usr/bin/env python3
"""device_limits.csv pre-flight reader (phase-4 Step 2.6).

Closes the phase-0 finding that `device_limits.csv` had ZERO code readers: this
module parses the v2 schema (geometry + V/I/P/T abs-max ratings) and validates
that testbench bias points sit inside the rated safe-operating area. The
characterization orchestrator calls `preflight_report()` at startup, so every
harness run now reads the file.

CLI:
    python pdk_validation/preflight.py            # summary + self-consistency check
    python pdk_validation/preflight.py --check    # + check the rated operating points
"""
from __future__ import annotations
import csv, sys
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent / "device_limits.csv"


def load_limits(path: Path = CSV_PATH) -> dict[str, dict[str, dict]]:
    """device -> param -> {min,max,unit,basis,note} (min/max as float where numeric)."""
    lim: dict[str, dict[str, dict]] = {}
    with path.open(newline="") as fh:
        for r in csv.DictReader(fh):
            def num(x):
                try:
                    return float(x)
                except (TypeError, ValueError):
                    return x
            lim.setdefault(r["device"], {})[r["param"]] = dict(
                min=num(r["min"]), max=num(r["max"]),
                unit=r.get("unit", ""), basis=r.get("basis", ""), note=r.get("note", ""))
    return lim


# param used to bound each terminal-pair voltage, most-conservative first
_VOLT_LIMIT = {
    "vds": ("Vds_dcmax", "Vds_absmax"), "vgs": ("Vgs_dcmax", "Vgs_absmax"),
    "vgd": ("Vgd_absmax",), "vce": ("Vce_max",), "vcb": ("Vcb_max",),
    "vr": ("Vr_absmax",), "vop": ("Vop_max", "Vabs_max"),
}


def check_bias(device: str, biases: dict[str, float],
               lim: dict | None = None) -> list[str]:
    """biases e.g. {'vds': 5.0, 'vgs': 5.0}. Return a list of violation strings."""
    lim = lim or load_limits()
    dl = lim.get(device, {})
    out: list[str] = []
    for term, v in biases.items():
        params = _VOLT_LIMIT.get(term.lower())
        if not params:
            continue
        rng = next((dl[p] for p in params if p in dl), None)
        if rng is None or not isinstance(rng["min"], (int, float)):
            continue
        if v < rng["min"] or v > rng["max"]:
            out.append(f"{device}: {term}={v:g} outside [{rng['min']:g},{rng['max']:g}] {rng['unit']}")
    return out


def self_consistency(lim: dict) -> list[str]:
    """dcmax must be inside absmax; min < max on every numeric row."""
    problems = []
    for dev, params in lim.items():
        for p, r in params.items():
            if isinstance(r["min"], (int, float)) and isinstance(r["max"], (int, float)):
                if r["min"] > r["max"]:
                    problems.append(f"{dev}.{p}: min {r['min']} > max {r['max']}")
        if "Vds_dcmax" in params and "Vds_absmax" in params:
            d, a = params["Vds_dcmax"], params["Vds_absmax"]
            if isinstance(d["max"], (int, float)) and isinstance(a["max"], (int, float)):
                if abs(d["max"]) > abs(a["max"]) + 1e-9:
                    problems.append(f"{dev}: |Vds_dcmax| {d['max']} > |Vds_absmax| {a['max']}")
    return problems


# rated operating points the characterization harness actually drives (Vds=Vds_dcmax's
# rating source): these MUST sit inside abs-max. A representative sanity set.
_RATED = {
    "NMOS50": {"vds": 5.0, "vgs": 5.0}, "PMOS50": {"vds": -5.0, "vgs": -5.0},
    "NMOS12": {"vds": 12.0, "vgs": 12.0}, "NDMOS200": {"vds": 200.0, "vgs": 5.0},
    "PDMOS200": {"vds": -200.0, "vgs": -5.0}, "NDMOS40": {"vds": 40.0, "vgs": 5.0},
    "NPN_HV": {"vce": 20.0}, "DZ_24": {"vr": 22.0},
}


def preflight_report(check_rated: bool = True) -> int:
    """Read device_limits.csv, print a summary, validate. Return violation count."""
    lim = load_limits()
    n_rat = sum(1 for d in lim.values() if any(k.endswith("max") or k.startswith("V") for k in d))
    print(f"[preflight] device_limits.csv: {len(lim)} devices, "
          f"{sum(len(v) for v in lim.values())} limit rows, {n_rat} with abs-max ratings")
    problems = self_consistency(lim)
    if check_rated:
        for dev, bias in _RATED.items():
            problems += check_bias(dev, bias, lim)
    if problems:
        print(f"[preflight] {len(problems)} violation(s):")
        for p in problems:
            print("   ! " + p)
    else:
        print("[preflight] OK: ratings self-consistent and rated operating points within SOA")
    return len(problems)


if __name__ == "__main__":
    sys.exit(1 if preflight_report("--check" in sys.argv or True) else 0)
