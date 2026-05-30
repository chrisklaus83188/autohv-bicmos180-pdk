#!/usr/bin/env python3
"""
Phase D: short transient regression per device class.

Runs each canonical .cir under pdk_validation/regression/transients/ in
ngspice batch mode, asserts that:

  * the deck reaches the TRAN_OK marker (the .tran completed),
  * ngspice prints no fatal-error patterns, and
  * the wall time stays under the deck's budget (default = max(2.0,
    5 x measured baseline); override per-deck via the TRANSIENTS table).

The thing this is most directly defending against is the kind of
convergence/timestep blow-up the pre-fix abs() kink caused on a passive
transient: op-level checks (Phase A) passed cleanly, but transients
hung at >120 s. The 'r_thru_zero' and 'c_thru_zero' decks drive a
sinusoid through V(p,n)=0 each half-cycle on the strongest-VCR resistor
and strongest-VCC cap respectively, which is the worst case for
re-introducing that kind of regression.

Usage:
  python run_transients.py                    # full run (~3-5 s wall)
  python run_transients.py --deck bsim_inverter vdmos_switching
  python run_transients.py --max-overrun 3.0  # multiplier on per-deck budget

Env:
  NGSPICE_BIN     path to ngspice_con(.exe); auto-detected if unset
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
DECK_DIR = HERE / "transients"

# (deck_filename, friendly_name, budget_seconds)
# Budgets are deliberately generous (~5x typical wall) -- this gate is
# meant to catch convergence/stiffness blow-ups (>>10x slowdown), not
# subtle perf creep. Bump per-deck if a deliberate change makes a deck
# legitimately slower.
TRANSIENTS = [
    ("bsim_inverter.cir",      "BSIM3 inverter",          2.0),
    ("noise_check.cir",        "BSIM3 noise + NQS check", 3.0),
    ("vdmos_switching.cir",    "VDMOS switching load",    2.0),
    ("bjt_common_emitter.cir", "BJT common-emitter",      2.0),
    ("bjt_breakdown_ramp.cir", "BJT BVCBO ramp (P2)",     2.0),
    ("cascoded_ldmos.cir",     "Cascoded LDMOS, MM_ON=0", 2.0),
    ("self_heating.cir",       "Self-heating (SH_ON=1)",  3.0),
    ("diode_rectifier.cir",    "Diode rectifier",         2.0),
    ("r_thru_zero.cir",        "RNWELL AC thru 0 V",      3.0),
    ("c_thru_zero.cir",        "CMIM_HI AC thru 0 V",     3.0),
]

ERROR_PATTERNS = [
    re.compile(r"^\s*Error[: ]",            re.MULTILINE | re.IGNORECASE),
    re.compile(r"no such function",         re.IGNORECASE),
    re.compile(r"singular matrix",          re.IGNORECASE),
    re.compile(r"iteration limit reached",  re.IGNORECASE),
    re.compile(r"timestep too small",       re.IGNORECASE),
    re.compile(r"unknown subckt",           re.IGNORECASE),
    re.compile(r"unknown parameter",        re.IGNORECASE),
]


def find_ngspice() -> str | None:
    cand = os.environ.get("NGSPICE_BIN")
    if cand and Path(cand).exists():
        return cand
    # On Windows the preferred batch binary is ngspice_con(.exe) (the
    # plain ngspice.exe opens a GUI/console window and doesn't stream
    # stdout). On Linux/macOS the binary is just `ngspice` and runs in
    # batch mode under -b.
    for name in ("ngspice_con", "ngspice_con.exe", "ngspice"):
        p = shutil.which(name)
        if p:
            return p
    for p in (
        r"C:\Spice64\bin\ngspice_con.exe",
        r"C:\Program Files\ngspice\bin\ngspice_con.exe",
    ):
        if Path(p).exists():
            return p
    return None


def run_deck(
    ngspice: str, deck_path: Path, budget: float
) -> tuple[bool, str, float]:
    """Returns (ok, reason, elapsed_seconds)."""
    # Run with cwd = deck's directory so that the deck's relative
    # .include path resolves consistently regardless of where the
    # harness was invoked from.
    cwd = deck_path.parent
    t0 = time.monotonic()
    try:
        res = subprocess.run(
            [ngspice, "-b", deck_path.name],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=max(60.0, budget * 4),
        )
        out = (res.stdout or "") + "\n" + (res.stderr or "")
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT (>{max(60.0, budget*4):.0f}s)", time.monotonic() - t0
    elapsed = time.monotonic() - t0

    for pat in ERROR_PATTERNS:
        m = pat.search(out)
        if m:
            line_start = out.rfind("\n", 0, m.start()) + 1
            line_end = out.find("\n", m.end())
            if line_end < 0:
                line_end = len(out)
            line = out[line_start:line_end].strip()
            return False, line[:160], elapsed

    if "TRAN_OK" not in out:
        return False, "no TRAN_OK marker (tran did not complete cleanly)", elapsed

    if elapsed > budget:
        return False, (
            f"exceeded budget: {elapsed:.2f}s > {budget:.2f}s"
        ), elapsed

    return True, "", elapsed


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--deck",
        nargs="+",
        default=None,
        help="restrict to listed deck names (filename stem, e.g. bsim_inverter)",
    )
    p.add_argument(
        "--max-overrun",
        type=float,
        default=1.0,
        help=(
            "multiplier applied to every deck's budget (default 1.0). "
            "Use >1 to loosen during legitimate slowdowns; <1 to tighten."
        ),
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    ngspice = find_ngspice()
    if ngspice is None:
        print("ERROR: ngspice_con not found", file=sys.stderr)
        return 2
    if not DECK_DIR.is_dir():
        print(f"ERROR: deck dir not found at {DECK_DIR}", file=sys.stderr)
        return 2

    decks = TRANSIENTS
    if args.deck:
        wanted = set(args.deck)
        decks = [
            d for d in TRANSIENTS
            if d[0].rsplit(".", 1)[0] in wanted or d[0] in wanted
        ]
        missing = wanted - {d[0].rsplit(".", 1)[0] for d in decks} - {d[0] for d in decks}
        if missing:
            print(f"ERROR: unknown deck(s): {sorted(missing)}", file=sys.stderr)
            return 2

    print(f"ngspice : {ngspice}")
    print(f"decks   : {len(decks)}  (under {DECK_DIR.relative_to(REPO_ROOT)})")
    print(f"overrun : {args.max_overrun:.2f}x  per-deck budget multiplier")
    print()

    fails: list[tuple[str, str]] = []
    total_wall = 0.0
    name_w = max(len(name) for _, name, _ in decks) + 1

    for filename, name, base_budget in decks:
        budget = base_budget * args.max_overrun
        deck_path = DECK_DIR / filename
        if not deck_path.exists():
            fails.append((name, f"deck file missing: {deck_path}"))
            print(f"  {name:<{name_w}s} MISS  no such file")
            continue
        ok, reason, elapsed = run_deck(ngspice, deck_path, budget)
        total_wall += elapsed
        if ok:
            pct = (elapsed / budget) * 100
            print(
                f"  {name:<{name_w}s} OK    {elapsed*1000:6.0f} ms  "
                f"({pct:4.0f}% of {budget:.1f}s budget)"
            )
        else:
            fails.append((name, reason))
            print(
                f"  {name:<{name_w}s} FAIL  {elapsed*1000:6.0f} ms  "
                f"-> {reason}"
            )

    print()
    print(f"Wall: {total_wall:.1f}s total")
    if fails:
        print(f"Passed: {len(decks)-len(fails)}/{len(decks)}")
        for name, reason in fails:
            print(f"  {name}: {reason}")
        return 1
    print(f"Passed: {len(decks)}/{len(decks)}")
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
