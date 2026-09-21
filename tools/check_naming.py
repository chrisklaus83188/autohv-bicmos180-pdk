#!/usr/bin/env python3
"""CI guard: no reference-process name in the repo, and provenance from a closed set.

TWO RULES, ONE TOOL
-------------------
1. **No external process, vendor or product name appears in any tracked file** -- in its
   contents OR in its path. Reference-specific material lives only in gitignored `LOCAL_*`
   files, and only boolean outcomes (see tools/check_plausibility.py) reach the repo. This
   PDK reuses methodology; it does not copy anyone's data, and it must not read as though
   it does.

2. **Every `source` in models/stat_model.json starts with a taxonomy prefix.** Free text
   was how a reference name got in: a value like `<vendor>:beta-class-band` is a name
   wearing a provenance label. A closed vocabulary makes the category the point and keeps
   the anchor anonymous -- `reference-class:beta-class-band` says exactly as much about
   where the number came from, without saying whose it is.

The pattern list is deliberately in this file and not in a data file: a guard whose rules
can be edited by the thing it guards is not a guard. Adding a name here is a visible,
reviewable act.

    python tools/check_naming.py            # report
    python tools/check_naming.py --check    # exit 1 on any violation
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "models" / "stat_model.json"

# Names that must never appear in a tracked file. One definition, applied to paths and
# contents alike, case-insensitively.
FORBIDDEN = [
    r"onc\s*-?\s*25",
    r"\bon\s*semiconductor\b",
    r"\bonsemi\b",
    r"\bon\s*semi\b",
]
PATTERN = re.compile("|".join(FORBIDDEN), re.I)

# A `source` must start with one of these, followed by `:`, a space, `(` or end of string.
TAXONOMY = ("measured", "derived", "autohv-derived", "literature", "reference-class",
            "declared", "carried-over", "default")


def tracked() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=str(ROOT),
                         capture_output=True, check=True).stdout
    return out.decode("utf-8", errors="replace").split()


# This file necessarily spells the forbidden names, in FORBIDDEN above -- there is no way to
# express the rule without naming what it forbids. It happens to pass its own scan today
# because the regex escapes break the match, but that is luck: a differently spelled pattern
# would make the guard fail on itself. So the exemption is explicit and narrow -- this one
# file, and nothing else -- and the prose here avoids spelling the names, leaving FORBIDDEN
# as the single place in the repository where they appear.
SELF = "tools/check_naming.py"


def scan_names(files: list[str]) -> list[str]:
    bad = []
    for rel in files:
        if rel.replace("\\", "/") == SELF:
            continue
        if PATTERN.search(rel):
            bad.append("path names the reference: %s" % rel)
        p = ROOT / rel
        try:
            txt = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, IsADirectoryError, PermissionError, FileNotFoundError):
            continue          # binary or unreadable: no prose to leak
        for i, line in enumerate(txt.splitlines(), 1):
            if PATTERN.search(line):
                bad.append("%s:%d names the reference" % (rel, i))
    return bad


def scan_sources() -> list[str]:
    bad, seen = [], []

    def walk(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "source" and isinstance(v, str):
                    seen.append(v)
                    headword = re.split(r"[:\s(]", v, maxsplit=1)[0]
                    if headword not in TAXONOMY:
                        bad.append("%s/source: %r does not start with a taxonomy prefix"
                                   % (path, v[:60]))
                elif k != "source_taxonomy":
                    walk(v, "%s/%s" % (path, k))
        elif isinstance(o, list):
            for n, v in enumerate(o):
                walk(v, "%s[%d]" % (path, n))

    walk(json.loads(MODEL.read_text(encoding="utf-8")))
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 on any violation")
    ap.add_argument("--stdin", action="store_true",
                    help="scan text on stdin instead of the tree (commit messages: "
                         "git log --format=%%B <range> | tools/check_naming.py --stdin)")
    args = ap.parse_args(argv)

    if args.stdin:
        # Commit messages are not files, and they outlive any edit to the tree: a message
        # written today is still there after the working copy is cleaned. Scanning them is
        # the same rule applied to the other half of the repository.
        text = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        hits = [(i, l) for i, l in enumerate(text.splitlines(), 1) if PATTERN.search(l)]
        if hits:
            print("naming check FAILED: %d commit-message line(s) name the reference" % len(hits))
            for i, l in hits[:20]:
                print("    line %d: %s" % (i, l.strip()[:90]))
            return 1
        print("ok: no reference name in %d line(s) of input" % len(text.splitlines()))
        return 0

    files = tracked()
    bad = scan_names(files) + scan_sources()
    if bad:
        print("naming check FAILED (%d):" % len(bad))
        for b in bad[:40]:
            print("   ", b)
        if len(bad) > 40:
            print("    ... and %d more" % (len(bad) - 40))
        print()
        print("Reference-specific material belongs in a gitignored LOCAL_* file; only the")
        print("boolean outcome of a comparison may be committed.")
        return 1
    print("ok: %d tracked files carry no reference name; every source is taxonomy-prefixed"
          % len(files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
