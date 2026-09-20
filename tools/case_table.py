#!/usr/bin/env python3
"""Every device's classic-bench metric at case 0-4, as one table (ruling AE1 3).

The corner distance table cannot show this. Each group's direction is renormalised to
exactly 3 sigma, so a group contributes 3.0 to the Mahalanobis distance whether it has one
term or six -- which is precisely why five degraded direction records left corners.json
looking perfectly healthy. A per-device case sweep is the check that actually moves when a
device stops responding to the corners.

Reuses the direction harness's deck builders and benches, so the bench a device is measured
on here is the same one its direction was measured on.

    python tools/case_table.py                     # all 40 groups, markdown to stdout
    python tools/case_table.py --groups NPN_LV,NMOS18
    python tools/case_table.py --out docs/case-table.md
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import measure_stat_directions as M  # noqa: E402

CASES = [0, 1, 2, 3, 4]
CASE_LABEL = {0: "TT", 1: "FF", 2: "SS", 3: "FS", 4: "SF"}


def deck_at_case(group: str, bench: dict, case: int) -> tuple[str, str]:
    """The group's classic deck, with the global corner selector set to `case`."""
    deck, mode = M.BUILDERS[M.kind_of(group)](group, bench, "classic")
    out = deck.replace(".param case=0", ".param case=%d" % case)
    if case and out == deck:
        raise SystemExit("case_table: could not set case=%d for %s -- the deck "
                         "template no longer contains '.param case=0'" % (case, group))
    return out, mode


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--groups", help="comma-separated subset (default: all 40)")
    ap.add_argument("--out", help="write markdown here instead of stdout")
    args = ap.parse_args(argv)

    ng = M.find_ngspice()
    model = json.loads(M.MODEL.read_text(encoding="utf-8"))
    sizing = json.loads(M.SIZING.read_text(encoding="utf-8"))
    groups = (args.groups.split(",") if args.groups else
              M.MOS_GROUPS + M.VDMOS_GROUPS + M.RES_GROUPS + M.CAP_GROUPS +
              M.BJT_GROUPS + M.DIO_GROUPS)

    work = Path(tempfile.mkdtemp(prefix="casetab_"))
    M.scratch(work, {}, {})
    rows, dead = [], []
    for g in groups:
        bench = M.bench_for(g, model, sizing)
        if M.kind_of(g) == "diode" and bench.get("Vf") is None:
            # Solve the forward bias ONCE, at case 0, and hold it across every case.
            # Re-solving per case would re-hit the target current by construction and
            # report zero movement for every diode.
            bench["Vf"] = M.solve_diode_vf(ng, g, bench, work)
        vals = {}
        for c in CASES:
            deck, mode = deck_at_case(g, bench, c)
            vals[c] = M.measure(ng, work, deck, mode, bench)
        base = vals[0]
        if not base:
            dead.append(g)
            continue
        pct = {c: 100.0 * (vals[c] - base) / base for c in CASES}
        rows.append((g, M.kind_of(g), vals, pct))
        print("%-10s %-10s %s" % (g, M.kind_of(g),
              "  ".join("%s %+7.3f%%" % (CASE_LABEL[c], pct[c]) for c in CASES)),
              file=sys.stderr)

    md = ["# Device response to case 0-4", "",
          "Classic bench per group (ruling F8), `PROC_ON=0`, `MM_ON=0`, T=27 C. Percentages",
          "are against that device's own case 0, so a row of zeros means the corners do not",
          "reach that device at all.", "",
          "| device | kind | case 0 (abs) | FF | SS | FS | SF |",
          "|---|---|---:|---:|---:|---:|---:|"]
    for g, kind, vals, pct in rows:
        md.append("| %s | %s | %.6e | %+.3f%% | %+.3f%% | %+.3f%% | %+.3f%% |"
                  % (g, kind, vals[0], pct[1], pct[2], pct[3], pct[4]))
    flat = [g for g, _k, _v, p in rows if all(abs(p[c]) < 1e-9 for c in (1, 2, 3, 4))]
    md += ["", "%d of %d devices measured; %d respond to at least one corner."
           % (len(rows), len(groups), len(rows) - len(flat))]
    if flat:
        md.append("")
        md.append("**Devices no corner moves:** " + ", ".join(flat) +
                  " — each is a finding, not a rounding artifact.")
    if dead:
        md.append("")
        md.append("**Devices with a zero case-0 metric (not measurable): " +
                  ", ".join(dead) + "**")
    text = "\n".join(md) + "\n"

    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
        print("wrote %s" % args.out)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
