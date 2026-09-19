#!/usr/bin/env python3
"""Build the corner preset table from the measured directions (brief v3 section 3.4).

Reads `models/stat_model.json` and `models/stat_directions.json` and writes
`models/corners.json` plus a markdown table for `docs/corners.md`.

A corner is a direction, not a list of multipliers. Each group's fast/slow (or
hi/lo) vector is its measured worst-case direction scaled to a Mahalanobis
length of exactly 3. A preset selects groups and sums their vectors; because the
global variables are independent unit normals, the Mahalanobis distance of any
preset is just the Euclidean norm of the summed z-vector.

Shared-variable rule (Phase 0 reply): when several selected groups pull a shared
variable the same way, the sum carries it and the preset's distance is whatever
the sum produces -- reported, not rescaled. Groups pulling a shared variable in
opposite directions are recorded as conflicts.

  python tools/build_corners.py
  python tools/build_corners.py --check     # non-zero if corners.json is stale
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "models" / "stat_model.json"
DIRECTIONS = ROOT / "models" / "stat_directions.json"
OUT = ROOT / "models" / "corners.json"

MOS_N = ["NMOS18", "NMOS33", "NMOS50", "NMOS12"]
MOS_P = ["PMOS18", "PMOS33", "PMOS50", "PMOS12"]
VDMOS = ["NDMOS20", "PDMOS20", "NDMOS40", "PDMOS40", "NDMOS60", "PDMOS60",
         "NDMOS80", "PDMOS80", "NDMOS120", "PDMOS120", "NDMOS200", "PDMOS200",
         "DNMOS20"]
LV_MOS = MOS_N + MOS_P
RES = ["RPOLY_HI", "RPOLY_LO", "RNWELL", "RNPLUS", "RPPLUS"]
CAP = ["CMIM_STD", "CMIM_HI", "CMOM", "CFRINGE"]
BJT = ["NPN_LV", "PNP_LAT", "NPN_HV", "PNP_HV"]
DIO = ["DIO_PN", "DIO_FAST", "DIO_SCH", "DZ_5V6", "DZ_12", "DZ_24"]

# case -> (label, {group: +1 fast/hi | -1 slow/lo})
def _all(groups, sign):
    return {g: sign for g in groups}


PRESETS: dict[int, tuple[str, dict[str, int]]] = {
    0: ("typical, nothing moved", {}),
    1: ("FF: all MOS fast", {**_all(LV_MOS, +1), **_all(VDMOS, +1)}),
    2: ("SS: all MOS slow", {**_all(LV_MOS, -1), **_all(VDMOS, -1)}),
    3: ("FS: n-type fast, p-type slow", {**_all(MOS_N, +1), **_all(MOS_P, -1),
                                         **_all([g for g in VDMOS if g.startswith("N")], +1),
                                         **_all([g for g in VDMOS if g.startswith("P")], -1)}),
    4: ("SF: n-type slow, p-type fast", {**_all(MOS_N, -1), **_all(MOS_P, +1),
                                         **_all([g for g in VDMOS if g.startswith("N")], -1),
                                         **_all([g for g in VDMOS if g.startswith("P")], +1)}),
    5: ("LV fast, HV slow", {**_all(LV_MOS, +1), **_all(VDMOS, -1)}),
    6: ("LV slow, HV fast", {**_all(LV_MOS, -1), **_all(VDMOS, +1)}),
    7: ("all resistors lo", _all(RES, -1)),
    8: ("all resistors hi", _all(RES, +1)),
    9: ("all capacitors lo", _all(CAP, -1)),
    10: ("all capacitors hi", _all(CAP, +1)),
    11: ("BJT and diodes lo", {**_all(BJT, -1), **_all(DIO, -1)}),
    12: ("BJT and diodes hi", {**_all(BJT, +1), **_all(DIO, +1)}),
    13: ("slow everything", {**_all(LV_MOS, -1), **_all(VDMOS, -1), **_all(RES, -1),
                             **_all(CAP, -1), **_all(BJT, -1), **_all(DIO, -1)}),
    14: ("fast everything", {**_all(LV_MOS, +1), **_all(VDMOS, +1), **_all(RES, +1),
                             **_all(CAP, +1), **_all(BJT, +1), **_all(DIO, +1)}),
    15: ("SS with resistors lo", {**_all(LV_MOS, -1), **_all(VDMOS, -1), **_all(RES, -1)}),
    16: ("FF with resistors hi", {**_all(LV_MOS, +1), **_all(VDMOS, +1), **_all(RES, +1)}),
}


def build() -> dict:
    model = json.loads(MODEL.read_text(encoding="utf-8"))
    dirs = json.loads(DIRECTIONS.read_text(encoding="utf-8"))["groups"]

    presets = {}
    for case, (label, selection) in PRESETS.items():
        z: dict[str, float] = {}
        contributors: dict[str, list[str]] = {}
        missing = []
        for group, sign in selection.items():
            rec = dirs.get(group)
            if rec is None:
                missing.append(group)
                continue
            for var, val in rec["z_fast"].items():
                z[var] = z.get(var, 0.0) + sign * val
                contributors.setdefault(var, []).append(f"{group}{'+' if sign > 0 else '-'}")
        # a shared variable pulled both ways by different groups
        conflicts = {}
        for var, who in contributors.items():
            if len(who) > 1 and any(w.endswith("+") for w in who) and any(w.endswith("-") for w in who):
                conflicts[var] = who
        presets[case] = {
            "label": label,
            "groups": selection,
            "z": {k: round(v, 6) for k, v in sorted(z.items()) if abs(v) > 1e-12},
            "mahalanobis": round(math.sqrt(sum(v * v for v in z.values())), 4),
            "shared_variable_conflicts": conflicts,
            "missing_groups": missing,
        }

    per_group = {
        g: {"kind": r["kind"],
            "z_fast": {k: round(v, 6) for k, v in r["z_fast"].items()},
            "mahalanobis": 3.0,
            "excluded": r["excluded"],
            "bench": r["bench"]}
        for g, r in dirs.items()
    }
    return {
        "_meta": {
            "program": "v3.0-stats",
            "status": "Stop A preview: built from measured directions; no .inc is generated from it yet",
            "source": ["models/stat_model.json", "models/stat_directions.json"],
            "distance": "Mahalanobis = Euclidean norm of z, because the global variables are "
                        "independent unit normals",
            "single_group_distance": 3.0,
            "shared_variable_rule": "selected groups' vectors are summed; the preset's distance is "
                                    "whatever the sum produces and is reported, not rescaled. "
                                    "Conflicts (a shared variable pulled both ways) are listed per preset.",
        },
        "presets": presets,
        "per_group": per_group,
    }


def markdown(data: dict) -> str:
    rows = ["| case | preset | groups moved | variables | Mahalanobis |",
            "|---|---|---|---|---|"]
    for case in sorted(data["presets"], key=int):
        p = data["presets"][case]
        rows.append("| %s | %s | %d | %d | **%.2f** |"
                    % (case, p["label"], len(p["groups"]), len(p["z"]), p["mahalanobis"]))
    return "\n".join(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 if corners.json is stale")
    ap.add_argument("--markdown", action="store_true", help="print the docs/corners.md table (it is also printed on a normal run)")
    ap.add_argument("--write-md", action="store_true",
                    help="regenerate the table inside docs/corners.md between its markers")
    args = ap.parse_args(argv)

    data = build()
    text = json.dumps(data, indent=1) + "\n"
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print("stale: models/corners.json differs from the generator output")
            return 1
        print("ok: models/corners.json is current")
        return 0

    OUT.write_text(text, encoding="utf-8", newline="\n")
    print("wrote models/corners.json")
    print()
    print(markdown(data))
    conflicts = {c: p["shared_variable_conflicts"] for c, p in data["presets"].items()
                 if p["shared_variable_conflicts"]}
    print()
    print("presets with shared-variable conflicts:", sorted(conflicts) or "none")

    if args.write_md:
        md = ROOT / "docs" / "corners.md"
        body = md.read_text(encoding="utf-8")
        first, last = "<!-- BEGIN distances -->", "<!-- END distances -->"
        if first not in body or last not in body:
            print("docs/corners.md is missing its distance markers; not written")
        else:
            names = ", ".join(str(c) for c in sorted(conflicts, key=int)) if conflicts else "none"
            lines = [first, markdown(data), "",
                     "Presets with shared-variable conflicts: **" + names
                     + "** \u2014 see above.", last]
            block = "\n".join(lines)
            body = (body[:body.index(first)] + block
                    + body[body.index(last) + len(last):])
            md.write_text(body, encoding="utf-8", newline="\n")
            print("wrote docs/corners.md distance table")
    return 0


if __name__ == "__main__":
    sys.exit(main())
