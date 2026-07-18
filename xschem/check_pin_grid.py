#!/usr/bin/env python3
"""Regression guard: every Xschem pin connection point must sit on the snap grid.

An Xschem pin is a rectangle on the pin layer:  B 5 x1 y1 x2 y2 {name=... dir=...}
The electrical connection point is the CENTER of that rectangle. If the center is
not an exact multiple of the snap unit, a wire endpoint (which quantizes to the
snap grid) can never coincide with it -> the pin is unwirable at default snap.

Usage:  python3 check_pin_grid.py [--grid N] [--pitch] [root]
Exits non-zero and prints file / pin / coordinate for every offender.
"""
import argparse
import pathlib
import re
import sys
from collections import defaultdict

PIN_RE = re.compile(r"^B\s+5\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*\{(.*)\}\s*$")
NAME_RE = re.compile(r"name=([^\s}]+)")
DIR_RE = re.compile(r"dir=([^\s}]+)")


def num(s):
    return float(s)


def pins_of(path):
    """Yield (lineno, name, dir, cx, cy) for each pin rectangle in a .sym file."""
    for lineno, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        m = PIN_RE.match(line.strip())
        if not m:
            continue
        x1, y1, x2, y2 = (num(v) for v in m.group(1, 2, 3, 4))
        attrs = m.group(5)
        name = NAME_RE.search(attrs)
        direction = DIR_RE.search(attrs)
        yield (
            lineno,
            name.group(1) if name else "?",
            direction.group(1) if direction else "?",
            (x1 + x2) / 2.0,
            (y1 + y2) / 2.0,
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=str(pathlib.Path(__file__).resolve().parent))
    ap.add_argument("--grid", type=int, default=10, help="snap unit (default 10)")
    ap.add_argument("--pitch", action="store_true",
                    help="also require >=20 spacing between pins sharing an x or y")
    args = ap.parse_args()

    root = pathlib.Path(args.root).resolve()
    grid = args.grid
    syms = sorted(root.rglob("*.sym"))

    offgrid, pitch_bad, npins = [], [], 0
    for sym in syms:
        rel = sym.relative_to(root)
        by_col, by_row = defaultdict(list), defaultdict(list)
        for lineno, name, _d, cx, cy in pins_of(sym):
            npins += 1
            if cx % grid or cy % grid:
                offgrid.append((rel, lineno, name, cx, cy))
            by_col[cx].append((cy, name))
            by_row[cy].append((cx, name))
        if args.pitch:
            for group in (by_col, by_row):
                for _key, items in group.items():
                    items.sort()
                    for (a, na), (b, nb) in zip(items, items[1:]):
                        if abs(b - a) % 20:
                            pitch_bad.append((rel, na, nb, abs(b - a)))

    print(f"checked {npins} pins across {len(syms)} symbols under {root}")

    ok = True
    if offgrid:
        ok = False
        print(f"\nFAIL: {len(offgrid)} pin(s) whose center is not a multiple of {grid}:")
        for rel, lineno, name, cx, cy in offgrid:
            print(f"  {rel}:{lineno}  pin '{name}'  center=({cx:g}, {cy:g})")
    if pitch_bad:
        ok = False
        print(f"\nFAIL: {len(pitch_bad)} adjacent pin pair(s) whose pitch is not a multiple of 20:")
        for rel, na, nb, d in pitch_bad:
            print(f"  {rel}  '{na}' -> '{nb}'  pitch={d:g}")

    if not ok:
        return 1
    print(f"OK: every pin center is a multiple of {grid}"
          + (" and every adjacent pin pitch is a multiple of 20" if args.pitch else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
