#!/usr/bin/env python3
"""Apply models/device_rename_map.json across every tracked file and path (ruling 2.3).

WHY A TOOL AND NOT A sed LOOP
-----------------------------
The renames overlap. `NDMOS20` is a prefix of `NDMOS200`; `NMOS20` sits inside `DNMOS20`;
and every device name also appears inside composites -- `NMOS18_INT`, `VTH_NMOS18`,
`Z_VTH_NMOS18`, `c_NMOS18`, `KP_NDMOS20_STAT`, `TC_KP_NDMOS20`. Two properties are needed
and neither comes free:

  * **Underscore is a word character**, so `\\bNMOS18\\b` does NOT match `NMOS18_INT` and a
    word-boundary rule silently leaves every composite behind. The token rule is
    `(?<![A-Za-z0-9])<old>(?![A-Za-z0-9])`, which treats `_` as a separator.
  * **One simultaneous pass, never sequential.** Rewriting `NDMOS20 -> NDMOS20V` and then
    `NDMOS200 -> NDMOS200V` over the same text can double-apply. A single alternation with
    a callback rewrites each site exactly once.

EXCLUSIONS, and why each one
----------------------------
  models/device_rename_map.json  holds both old and new names; rewriting it destroys the map
  tools/check_naming.py          holds the old names as a forbidden set, by design
  tools/rename_devices.py        this file, for the same reason
  pdk_validation/baselines/v2_2/ a frozen historical snapshot (ruling 2.4 section 4): the
                                 comparison tools apply the map when reading it instead

    python tools/rename_devices.py --dry-run     # inventory first, always
    python tools/rename_devices.py --apply
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "models" / "device_rename_map.json"

EXCLUDE_EXACT = {
    "models/device_rename_map.json",
    "tools/check_naming.py",
    "tools/rename_devices.py",
}
EXCLUDE_PREFIX = ("pdk_validation/baselines/",)

# Only the .sym FILES under xschem/autohv/ are generated (by xschem/gen_syms.sh, which
# hardcodes the names in its emit_mos/emit_dev calls): rename the generator, delete the
# stale symbols, re-run it. Excluding the whole directory was wrong -- README.md and
# examples/*.sch live there too, are hand-authored, and were silently left behind until
# check_naming's retired-name scan caught all 26.
# qucs-s_symbols/*.sym has NO generator (make_release.py only packages it), so those are
# static sources and are renamed like any other file.
def generated(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    return rel.startswith("xschem/autohv/") and rel.endswith(".sym")


def load_map() -> dict[str, str]:
    return json.loads(MAP.read_text(encoding="utf-8"))["map"]


def token_re(names) -> re.Pattern:
    """One alternation, longest first, with separator-aware lookarounds."""
    alts = "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
    return re.compile(r"(?<![A-Za-z0-9])(%s)(?![A-Za-z0-9])" % alts)


def excluded(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    return rel in EXCLUDE_EXACT or rel.startswith(EXCLUDE_PREFIX) or generated(rel)


def tracked() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=str(ROOT),
                         capture_output=True, check=True).stdout
    return out.decode("utf-8", errors="replace").split()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    args = ap.parse_args(argv)

    mapping = load_map()
    rx = token_re(mapping)
    files = tracked()

    content_hits: dict[str, int] = {}
    path_hits: list[tuple[str, str]] = []
    per_name: dict[str, int] = {k: 0 for k in mapping}

    for rel in files:
        if excluded(rel):
            continue
        new_rel = rx.sub(lambda m: mapping[m.group(1)], rel)
        if new_rel != rel:
            path_hits.append((rel, new_rel))
        p = ROOT / rel
        try:
            txt = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, IsADirectoryError, PermissionError, FileNotFoundError):
            continue
        found = rx.findall(txt)
        if found:
            content_hits[rel] = len(found)
            for f in found:
                per_name[f] += 1
        if args.apply and found:
            p.write_text(rx.sub(lambda m: mapping[m.group(1)], txt),
                         encoding="utf-8", newline="\n")

    if args.apply:
        for old_rel, new_rel in path_hits:
            dst = ROOT / new_rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "mv", old_rel, new_rel], cwd=str(ROOT), check=True)

    print("%-48s %s" % ("device", "occurrences"))
    for k in sorted(per_name, key=lambda x: -per_name[x]):
        print("  %-46s %d" % ("%s -> %s" % (k, mapping[k]), per_name[k]))
    print()
    print("files with content hits: %d   total occurrences: %d"
          % (len(content_hits), sum(content_hits.values())))
    print("paths to rename: %d" % len(path_hits))
    for a, b in path_hits[:30]:
        print("   %s  ->  %s" % (a, b))
    if len(path_hits) > 30:
        print("   ... and %d more" % (len(path_hits) - 30))

    if args.dry_run:
        print()
        print("top files by occurrences:")
        for rel in sorted(content_hits, key=lambda x: -content_hits[x])[:25]:
            print("   %-60s %d" % (rel, content_hits[rel]))
        print()
        print("(dry run: nothing written)")
    else:
        print()
        print("applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
