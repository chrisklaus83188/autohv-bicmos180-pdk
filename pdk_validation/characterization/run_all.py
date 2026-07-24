#!/usr/bin/env python3
"""
Phase-2 characterization harness -- orchestrator.

Runs every family module and every discrimination experiment against the PDK
AS-IS, merges the measurements into results/characterization-results.json, and
scores them against docs/anchor-values.json.

    python run_all.py                  # everything, then score
    python run_all.py --only vdmos     # one family (repeatable)
    python run_all.py --skip-experiments
    python run_all.py --no-score

The PDK is measured, never modified. Discrimination experiments may create
isolation copies of individual .model cards under results/local_models/ with a
DISTINCT model name (ngspice keeps the first definition of a name, so shadowing
is impossible -- see char_lib.write_local_model).

Exit code = number of unexpected hard-fails from score.py, so a later CI
hookup gates on regressions against this baseline rather than on the baseline
itself. Wiring that up is deliberately NOT done here.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import char_lib as cl  # noqa: E402

FAMILIES = [
    ("bsim3_mos", "families.bsim3_mos"),
    ("vdmos", "families.vdmos"),
    ("bjt", "families.bjt"),
    ("diodes", "families.diodes"),
    ("passives", "families.passives"),
]

EXPERIMENTS = [
    ("d1_kp_convention", "experiments.d1_kp_convention.run"),
    ("d2_ksubthres", "experiments.d2_ksubthres.run"),
    ("d3_rdrs_isolation", "experiments.d3_rdrs_isolation.run"),
    ("d4_kp_ladder_shape", "experiments.d4_kp_ladder_shape.run"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", action="append", default=None,
                    help="run only these families (repeatable)")
    ap.add_argument("--skip-experiments", action="store_true")
    ap.add_argument("--no-score", action="store_true")
    args = ap.parse_args()

    t0 = time.time()
    col = cl.Collector()
    ver = cl.ngspice_version()
    print(f"ngspice : {ver}")
    print(f"PDK lib : {cl.LIB_PATH}")
    print(f"anchors : {cl.ANCHOR_PATH}")
    print()

    timings: dict[str, float] = {}
    failures: dict[str, str] = {}

    for short, mod in FAMILIES:
        if args.only and short not in args.only:
            continue
        print(f"[{short}] ...", flush=True)
        ts = time.time()
        try:
            m = importlib.import_module(mod)
            m.run(col)
        except Exception as e:  # a broken family must not lose the others
            failures[short] = f"{type(e).__name__}: {e}"
            traceback.print_exc()
        timings[short] = round(time.time() - ts, 1)
        n = len([x for x in col.items])
        print(f"[{short}] done in {timings[short]}s  (cumulative "
              f"measurements: {n})")

    if not args.skip_experiments:
        for short, mod in EXPERIMENTS:
            print(f"[exp:{short}] ...", flush=True)
            ts = time.time()
            try:
                m = importlib.import_module(mod)
                col.experiments[short] = m.run()
            except Exception as e:
                failures[f"exp:{short}"] = f"{type(e).__name__}: {e}"
                traceback.print_exc()
            timings[f"exp:{short}"] = round(time.time() - ts, 1)
            print(f"[exp:{short}] done in {timings[f'exp:{short}']}s")

    wall = round(time.time() - t0, 1)
    payload = col.to_json()
    payload["_meta"] = {
        "title": "AutoHV BiCMOS180 PDK -- phase 2 characterization baseline",
        "purpose": ("Measured the PDK AS-IS. No model fixes landed in phase 2; "
                    "this is the before-picture every later fix is diffed against."),
        "ngspice_version": ver,
        "ngspice_binary": cl.find_ngspice(),
        "pdk_lib": str(cl.LIB_PATH.relative_to(cl.REPO_ROOT).as_posix()),
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "wall_seconds": wall,
        "timings_seconds": timings,
        "module_failures": failures,
        "measurement_count": len(col.items),
        "provenance": ("Every measurement carries the deck that produced it. "
                       "Decks are committed under "
                       "pdk_validation/characterization/decks/ and are "
                       "re-runnable standalone: ngspice -b <deck>."),
        "mc_seeding": ("ngspice time-seeds .param AGAUSS per -b invocation and "
                       "offers no settable seed (-D rndseed does not reach "
                       ".param). MC runs are NOT bit-reproducible; each MC "
                       "measurement records its N and the non-degeneracy check "
                       "result instead."),
        "tag_meaning": {"measured": "read from a simulator output",
                        "derived": "computed from one or more measured values"},
    }

    cl.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = cl.RESULTS_DIR / "characterization-results.json"
    out.write_text(json.dumps(payload, indent=2, default=str),
                   encoding="utf-8", newline="\n")

    print()
    print(f"wall {wall}s   measurements {len(col.items)}   "
          f"errors {len(col.errors)}")
    print(f"results -> {out.relative_to(cl.REPO_ROOT).as_posix()}")
    if failures:
        print("MODULE FAILURES:")
        for k, v in failures.items():
            print(f"  {k}: {v}")

    if args.no_score:
        return 0
    print()
    import score
    return score.main()


if __name__ == "__main__":
    sys.exit(main())
