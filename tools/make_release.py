#!/usr/bin/env python3
"""
make_release.py -- create a sanitized snapshot of the PDK suitable for sharing
with a new task without leaking project-specific information from other tasks.

Produces a fresh git repo (with one initial commit) containing only the generic
/ reusable PDK files, then zips it for delivery. The git history of the source
repo is NOT carried into the export, so commit messages, agent emails, and
task names from previous engagements are not exposed.

Usage:
    python tools/make_release.py
    python tools/make_release.py --out path/to/output.zip
    python tools/make_release.py --dry-run

What's INCLUDED in the export:
    autohv_bicmos180_case.lib            the device library
    autohv_bicmos180_case_models.inc     the model cards
    qucs-s_symbols/                      schematic symbols for Qucs-S
    xschem/                              schematic symbols + generators for Xschem
    README.md
    docs/QUICKSTART.md
    docs/MISMATCH_CORNERS.md
    docs/AutoHV_BiCMOS180_PDK_Reference.docx
    docs/CHANGELOG.md                    -- with task references scrubbed
    examples/                            generic example decks
    pdk_validation/regression/           the four-runner regression suite
    pdk_validation/bjt_avalanche_stress/ generic device audit
    pdk_validation/switched_cap_audit/   generic precision audit
    .gitattributes
    .github/workflows/regression.yml

What's EXCLUDED:
    HANDOFF_*.md at repo root            task-specific handoffs
    repro_*.cir  at repo root            task-specific reproducer decks
    tools/                               maintainer scripts (this one)
    release/                             prior export outputs
    .git/                                source repo history
    anything not in the explicit include list

Sanitization passes are run on a small number of text files to scrub task IDs
(e.g. "chuba14f", "xqmfaf10") and references to internal handoff docs that
won't exist in the export. Update SANITIZE_RULES below when new task names
enter the source files.
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path

# Resolve repo root assuming this script lives at <repo>/tools/make_release.py
REPO = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Whitelist: what goes into the export. Paths are relative to the repo root.
# Trailing "/" means "this directory recursively". Anything not listed here is
# excluded by construction.
# ---------------------------------------------------------------------------
INCLUDE = [
    "autohv_bicmos180_case.lib",
    "autohv_bicmos180_case_models.inc",
    "qucs-s_symbols/",
    "xschem/",
    "README.md",
    "docs/QUICKSTART.md",
    "docs/MISMATCH_CORNERS.md",
    "docs/AutoHV_BiCMOS180_PDK_Reference.docx",
    "docs/CHANGELOG.md",
    "examples/",
    "pdk_validation/regression/",
    "pdk_validation/bjt_avalanche_stress/",
    "pdk_validation/switched_cap_audit/",
    ".gitattributes",
    ".github/workflows/regression.yml",
]

# Additional exclusions applied to anything that survived INCLUDE. Useful for
# excluding subdirectories of an included directory (e.g. a stray HANDOFF doc
# accidentally committed under docs/).
EXCLUDE_GLOBS = [
    "HANDOFF_*.md",
    "repro_*.cir",
    "*/.git/*",
    "__pycache__",
    "*.pyc",
    "*.log",         # ngspice b3v33check.log etc. produced during regression
    "*.raw",         # ngspice raw output
    ".scratch.*",
]

# ---------------------------------------------------------------------------
# Sanitization rules: (regex, replacement). Applied to files in SANITIZE_FILES.
# Order matters -- more specific patterns first, generic catch-alls last.
# Add new task names here as they appear in the source.
# ---------------------------------------------------------------------------
SANITIZE_RULES = [
    # Specific task names (current + historical)
    (r"\bchuba14f\b",                          "an HV switching task"),
    (r"\bxqmfaf10\b",                          "an HV level-shifter task"),
    # Handoff doc references -- these files won't exist in the export, so
    # rewrite references to them as descriptive prose
    (r"`?HANDOFF_dynamic_transient_microstepping\.md`?",      "an internal handoff"),
    (r"`?HANDOFF_dmos200_vshift_multiinstance_REPLY\.md`?",   "an internal handoff"),
    (r"`?HANDOFF_dmos200_vshift_multiinstance\.md`?",         "an internal handoff"),
    (r"`?HANDOFF_dmos200_breakdown\.md`?",                    "an internal handoff"),
    (r"`?HANDOFF_cascode_vshift_singularity\.md`?",           "an internal handoff"),
    (r"`?HANDOFF_ngspice_compat_REPLY_VERIFIED\.md`?",        "an internal handoff"),
    (r"`?HANDOFF_ngspice_compat_REPLY_FINAL\.md`?",           "an internal handoff"),
    (r"`?HANDOFF_ngspice_compat_REPLY_FIX_LANDED\.md`?",      "an internal handoff"),
    (r"`?HANDOFF_ngspice_compat_REPRO_RESULTS\.md`?",         "an internal handoff"),
    (r"`?HANDOFF_ngspice_compat_REPRO_REQUEST\.md`?",         "an internal handoff"),
    (r"`?HANDOFF_ngspice_compat\.md`?",                       "an internal handoff"),
    (r"`?HANDOFF_vdmos_caps\.md`?",                           "an internal handoff"),
    # Generic catch-all for anything new, with or without .md extension and
    # with or without backtick quoting.
    (r"`?HANDOFF_[A-Za-z0-9_]+(\.md)?`?",                     "an internal handoff"),
    # Agent / author emails that may have leaked into source files
    (r"jabbah\.technetium\.kui@mercor\.expert",               "anonymous"),
    (r"<chrisklaus[0-9]+@[^>]+>",                             "<pdk-maintainer@local>"),
    # "Per HANDOFF_..." style phrasing now reads "Per an internal handoff from
    # an HV switching task" -- tighten the doubled "from an ... from a ..."
    (r"Per an internal handoff from an HV switching task",     "Per an internal handoff"),
    (r"Per an internal handoff from an HV level-shifter task", "Per an internal handoff"),
]

# Files whose text content gets the SANITIZE_RULES pass. Limited to the files
# we've audited and know contain task references. Other text files (README,
# QUICKSTART, MISMATCH_CORNERS) have no task references at time of writing.
SANITIZE_FILES = [
    "docs/CHANGELOG.md",
    "autohv_bicmos180_case.lib",  # Rcond comment lines reference an internal handoff
    "pdk_validation/regression/transients/multi_mirror_floating.cir",
    "pdk_validation/regression/transients/cascoded_ldmos.cir",
    "pdk_validation/regression/transients/coss_check.cir",
]

# Initial commit author for the exported git repo. Override at the CLI if you
# want a different label in the release's history.
DEFAULT_AUTHOR_NAME  = "PDK Maintainer"
DEFAULT_AUTHOR_EMAIL = "pdk-release@local"


# ---------------------------------------------------------------------------
# Implementation
# ---------------------------------------------------------------------------

def is_excluded(rel: Path) -> bool:
    """Check rel against the EXCLUDE_GLOBS."""
    s = rel.as_posix()
    name = rel.name
    for pat in EXCLUDE_GLOBS:
        if rel.match(pat) or Path(name).match(pat):
            return True
        # */ patterns
        if pat.startswith("*/") and pat[2:] in s:
            return True
    return False


def collect_files(repo: Path) -> list[Path]:
    """Walk the INCLUDE list and yield every concrete file, repo-relative."""
    files: list[Path] = []
    for entry in INCLUDE:
        src = repo / entry
        if not src.exists():
            print(f"  WARN: include path missing: {entry}", file=sys.stderr)
            continue
        if src.is_file():
            rel = Path(entry)
            if not is_excluded(rel):
                files.append(rel)
        else:
            # Directory: walk recursively
            for p in src.rglob("*"):
                if p.is_file():
                    rel = p.relative_to(repo)
                    if not is_excluded(rel):
                        files.append(rel)
    return sorted(set(files))


def sanitize_text(text: str) -> tuple[str, int]:
    """Apply SANITIZE_RULES and return (new_text, num_substitutions_made)."""
    n = 0
    for pat, repl in SANITIZE_RULES:
        text, count = re.subn(pat, repl, text)
        n += count
    return text, n


def copy_and_sanitize(repo: Path, files: list[Path], dest: Path) -> int:
    """Copy files into dest; run sanitization on the audited set."""
    sub_total = 0
    sanitize_set = {Path(p) for p in SANITIZE_FILES}
    for rel in files:
        src = repo / rel
        dst = dest / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if rel in sanitize_set:
            text = src.read_text(encoding="utf-8")
            text, n = sanitize_text(text)
            dst.write_text(text, encoding="utf-8")
            sub_total += n
            if n:
                print(f"  sanitized {rel}: {n} substitution(s)")
        else:
            shutil.copy2(src, dst)
    return sub_total


def init_git_repo(dest: Path, author_name: str, author_email: str,
                  message: str) -> None:
    """Initialise dest as a fresh git repo with one initial commit."""
    def run(*args: str) -> None:
        subprocess.run(args, cwd=dest, check=True, capture_output=True)
    run("git", "init", "-q", "-b", "main")
    # Use repo-local config so we don't touch the user's global identity.
    run("git", "config", "user.name", author_name)
    run("git", "config", "user.email", author_email)
    run("git", "add", "-A")
    run("git", "commit", "-q", "-m", message,
        "--author", f"{author_name} <{author_email}>")


def zip_repo(src: Path, out: Path) -> int:
    """Zip src (including its .git/) into out. Return file count."""
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for p in src.rglob("*"):
            if p.is_file():
                arc = p.relative_to(src.parent)  # one top-level folder in the zip
                zf.write(p, arc)
                n += 1
    return n


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--out", default=None,
        help="output zip path (default: release/autohv_bicmos180_pdk_<DATE>.zip)",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="list files that would be exported; do not write a zip",
    )
    p.add_argument(
        "--author-name", default=DEFAULT_AUTHOR_NAME,
        help=f"initial-commit author name (default: {DEFAULT_AUTHOR_NAME!r})",
    )
    p.add_argument(
        "--author-email", default=DEFAULT_AUTHOR_EMAIL,
        help=f"initial-commit author email (default: {DEFAULT_AUTHOR_EMAIL!r})",
    )
    p.add_argument(
        "--no-git", action="store_true",
        help="don't initialise a git repo; ship raw files in the zip",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    today = date.today().isoformat()
    out_path = Path(args.out) if args.out else (
        REPO / "release" / f"autohv_bicmos180_pdk_{today}.zip"
    )

    files = collect_files(REPO)

    print(f"Source repo : {REPO}")
    print(f"Output      : {out_path}")
    print(f"Files       : {len(files)}")
    print(f"Mode        : {'dry-run' if args.dry_run else 'real'}")
    print()

    if args.dry_run:
        for f in files:
            print(f"  {f}")
        # Show what sanitization would do
        print()
        print("Sanitization preview:")
        for sf in SANITIZE_FILES:
            src = REPO / sf
            if not src.exists():
                continue
            _, n = sanitize_text(src.read_text(encoding="utf-8"))
            print(f"  {sf}: {n} substitution(s) would be applied")
        return 0

    # Build the snapshot in a temp dir, then zip it
    with tempfile.TemporaryDirectory(prefix="pdk_release_") as tmp:
        snapshot = Path(tmp) / "autohv_bicmos180_pdk"
        snapshot.mkdir()
        n_subs = copy_and_sanitize(REPO, files, snapshot)
        print(f"Copied {len(files)} files, {n_subs} sanitization substitution(s).")
        if not args.no_git:
            init_git_repo(
                snapshot, args.author_name, args.author_email,
                f"Initial commit: AutoHV BiCMOS 180 PDK release {today}",
            )
            print("Initialised fresh git repo with one initial commit.")
        n_zipped = zip_repo(snapshot, out_path)
        print(f"Wrote {out_path} ({n_zipped} files in zip).")
    print()
    print("Release ready to share.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
