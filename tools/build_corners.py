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
VDMOS_N = ["NDMOS20", "NDMOS40", "NDMOS60", "NDMOS80", "NDMOS120", "NDMOS200",
           "DNMOS20"]          # DNMOS20 is an N-channel depletion device
VDMOS_P = ["PDMOS20", "PDMOS40", "PDMOS60", "PDMOS80", "PDMOS120", "PDMOS200"]
VDMOS = VDMOS_N + VDMOS_P
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
    # Explicit N/P lists, not a name-prefix test: DNMOS20 starts with "D" and so
    # fell into neither side, silently dropping out of FS/SF (ruling 2026-09-19 S2).
    3: ("FS: n-type fast, p-type slow", {**_all(MOS_N, +1), **_all(MOS_P, -1),
                                         **_all(VDMOS_N, +1), **_all(VDMOS_P, -1)}),
    4: ("SF: n-type slow, p-type fast", {**_all(MOS_N, -1), **_all(MOS_P, +1),
                                         **_all(VDMOS_N, -1), **_all(VDMOS_P, +1)}),
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


def z_corner_of(rec: dict) -> dict[str, float]:
    """The SIGN-OFF corner vector: every variable at its own +/-3 sigma (ruling Q1).

    Two conventions turn a statistical model into a corner, and they are not the same
    point:

      joint 3 sigma   z = 3*g/|g|, the point on the group's 3 sigma ellipsoid that
                      maximises the metric. Mahalanobis exactly 3. This is the honest
                      3 sigma of the distribution and is what MC and yield reasoning
                      want. Kept per group as `z_direction`.

      per-variable    z_i = 3*sign(g_i), every contributing variable at its own 3 sigma
      3 sigma         simultaneously. Mahalanobis 3*sqrt(k) for k contributors, i.e.
                      more pessimistic by sqrt(k). This is what production corner
                      libraries ship and what docs/corners.md already described.

    A sign-off corner is deliberately the pessimistic one, so the builder now emits it.
    Variables excluded for having no lever contribute nothing and stay absent, exactly
    as before -- this changes the magnitude of each component, never the membership.
    """
    return {var: 3.0 if g > 0 else -3.0
            for var, g in rec["g_classic"].items() if g != 0.0}


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
            for var, val in z_corner_of(rec).items():
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

    per_group = {}
    for g, r in dirs.items():
        zc = z_corner_of(r)
        per_group[g] = {
            "kind": r["kind"],
            # The sign-off corner: every variable at its own +/-3 sigma.
            "z_corner": {k: round(v, 6) for k, v in zc.items()},
            "mahalanobis_corner": round(math.sqrt(sum(v * v for v in zc.values())), 4),
            # The joint-3-sigma worst-case direction, kept for MC and sensitivity work.
            # Never mix the two: this one is the honest 3 sigma of the distribution.
            "z_direction": {k: round(v, 6) for k, v in r["z_fast"].items()},
            "mahalanobis_direction": 3.0,
            "terms": len(zc),
            "excluded": r["excluded"],
            "bench": r["bench"],
        }
    return {
        "_meta": {
            "program": "v3.0-stats",
            "status": "Stop A preview: built from measured directions; no .inc is generated from it yet",
            "source": ["models/stat_model.json", "models/stat_directions.json"],
            "distance": "Mahalanobis = Euclidean norm of z, because the global variables are "
                        "independent unit normals",
            "corner_construction": "per-variable +-3 sigma (ruling Q1): every variable a group "
                                   "depends on is set to its own 3 sigma simultaneously, sign from "
                                   "the measured direction. This is the sign-off convention and is "
                                   "deliberately more pessimistic than the joint 3 sigma point by "
                                   "sqrt(k) for k contributors.",
            "single_group_distance": "3*sqrt(k) for k contributing variables; see per_group "
                                     "mahalanobis_corner. The joint-3-sigma direction "
                                     "(mahalanobis_direction) is exactly 3.0 and is kept per group "
                                     "for MC and sensitivity work.",
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
        # The term-count invariant first: corners.json can be perfectly current and still
        # be built from a direction that quietly lost terms, because every group's vector
        # is normalised and so carries no trace of how many variables went into it.
        import expected_terms
        model = json.loads(MODEL.read_text(encoding="utf-8"))
        dirs = json.loads(DIRECTIONS.read_text(encoding="utf-8"))["groups"]
        bad = expected_terms.compare(model, dirs, model.get("expected_terms"))
        if bad:
            print("stale: the measured directions disagree with what the model realises")
            for b in bad:
                print("   ", b)
            return 1
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
