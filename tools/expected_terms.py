#!/usr/bin/env python3
"""Per-group expected term counts, derived from the model (ruling Q4).

WHY THIS EXISTS
---------------
`corners.json` cannot detect a degraded direction. Every group's joint-3-sigma vector is
renormalised to exactly 3 sigma, so a group contributes the same distance whether it has
one contributing variable or six. When AE1 silently dropped terms from five records, every
distance in the file stayed plausible and nothing failed. The term count is the quantity
that actually moves, so it is the quantity to assert.

THE INVARIANT
-------------
Every variable the model realises for a group must end up either
  * a term in that group's measured direction, or
  * a recorded exclusion ("no lever" and the reason),
and never simply absent. `expected = measured + excluded` per group.

NOT A SELF-REFERENTIAL INPUT
----------------------------
This tool writes `expected_terms` into models/stat_model.json, the file it also reads. That
is safe only because it never reads that key to produce it: the count is computed purely
from `global_variables` and their `applies_to` entries. Do not make it read its own output.

    python tools/expected_terms.py            # print the table
    python tools/expected_terms.py --write    # store into models/stat_model.json
    python tools/expected_terms.py --check    # exit 1 if stored or measured counts disagree
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import measure_stat_directions as M  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "models" / "stat_model.json"
DIRECTIONS = ROOT / "models" / "stat_directions.json"

ALL_GROUPS = (M.MOS_GROUPS + M.VDMOS_GROUPS + M.RES_GROUPS +
              M.CAP_GROUPS + M.BJT_GROUPS + M.DIO_GROUPS)


def realised(model: dict) -> dict[str, int]:
    """{group: how many variables the model realises for it} -- from applies_to only.

    U0_<group> is added for every mos/vdmos group: the harness injects it through
    sigma_overrides rather than through perturbations(), including on the sigma(KP)=0
    devices, where it is measured as a zero lever and recorded as an exclusion.
    """
    out = {}
    for g in ALL_GROUPS:
        perts, dead = M.perturbations(g, model)
        n = len(perts) + len(dead)
        if M.kind_of(g) in ("mos", "vdmos"):
            n += 1                       # U0_<group>, injected outside perturbations()
        out[g] = n
    return out


def compare(model: dict, dirs: dict, stored: dict | None) -> list[str]:
    """Every way the measured record can disagree with what the model realises.

    Two checks, and they catch different things:

      accounting  measured terms + recorded exclusions == variables realised. Purely
                  model-derived, so it cannot be satisfied by rewriting the expectation.
                  This is the AE1 check: a term that vanishes without becoming an
                  exclusion fails here.

      snapshot    the term count equals the stored, reviewed value. A term may legitimately
                  move to `excluded` when its measured lever is zero (prune_no_lever), so
                  this number is not derivable from the model alone -- it is a tripwire
                  against silent drift, and moving it is meant to be a deliberate edit.
    """
    bad, real = [], realised(model)
    for g, n in real.items():
        rec = dirs.get(g)
        if rec is None:
            bad.append(f"{g}: no measured direction at all")
            continue
        got_terms = len(rec.get("g_classic", {}))
        got_excl = len(rec.get("excluded", {}))
        if got_terms + got_excl != n:
            bad.append(f"{g}: {n} variable(s) realised but {got_terms} term(s) + "
                       f"{got_excl} exclusion(s) = {got_terms + got_excl} accounted for; "
                       f"a variable vanished without a record")
        if stored and g in stored and stored[g]["terms"] != got_terms:
            bad.append(f"{g}: direction carries {got_terms} term(s), stored expectation "
                       f"is {stored[g]['terms']}")
    return bad


def expected(model: dict, dirs: dict | None = None) -> dict[str, dict]:
    """The table stored in stat_model.json: realised (model) + terms (measured snapshot)."""
    real = realised(model)
    out = {}
    for g, n in real.items():
        e = {"realised": n}
        if dirs and g in dirs:
            e["terms"] = len(dirs[g].get("g_classic", {}))
            e["excluded"] = len(dirs[g].get("excluded", {}))
        out[g] = e
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    model = json.loads(MODEL.read_text(encoding="utf-8"))
    dirs = json.loads(DIRECTIONS.read_text(encoding="utf-8"))["groups"]

    if args.check:
        stored = model.get("expected_terms")
        bad = compare(model, dirs, stored)
        if stored is None:
            bad.append("models/stat_model.json carries no expected_terms; run --write")
        if bad:
            print("term-count check FAILED (%d):" % len(bad))
            for b in bad:
                print("   ", b)
            return 1
        print("ok: %d groups, every realised variable is a term or a recorded exclusion"
              % len(stored))
        return 0

    exp = expected(model, dirs)
    if args.write:
        model["expected_terms"] = exp
        MODEL.write_text(json.dumps(model, indent=2) + "\n", encoding="utf-8", newline="\n")
        print("wrote expected_terms for %d groups into %s"
              % (len(exp), MODEL.relative_to(ROOT)))
        return 0

    print("%-10s %8s %9s %9s" % ("group", "terms", "excluded", "realised"))
    for g, e in exp.items():
        print("%-10s %8s %9s %9d" % (g, e.get("terms", "-"), e.get("excluded", "-"),
                                     e["realised"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
