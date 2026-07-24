#!/usr/bin/env python3
"""
Score characterization-results.json against docs/anchor-values.json.

Implements the anchor doc section 8 policy exactly:

  hard-fail     [physics]/[model]-tagged FoM outside [lo, hi]
  warn          [industry]-tagged FoM outside band
  blocked       any anchor entry carrying `conditional_on` -- skip the
                assertion, still record the measurement
  artifact      anything named in _known_artifacts -- measure, log, never assert
  expected-fail a hard-fail that phase 1 predicted (F3/F6/zener tempco/...);
                still a failure, but tagged with its finding reference so it
                does not read as a surprise

Exit code = number of hard-fails that are NOT expected-fails, so a later CI
hookup gates on regressions rather than on the known baseline. (The brief says
do not wire CI in this phase; this just makes it possible later.)

Usage:  python score.py            # writes docs/characterization-scorecard.md
        python score.py --quiet    # exit code only
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
RESULTS = HERE / "results" / "characterization-results.json"
ANCHORS = REPO_ROOT / "docs" / "anchor-values.json"
SCORECARD = REPO_ROOT / "docs" / "characterization-scorecard.md"

# Explicit device lists. Globs bit us once: "DMOS" is NOT a substring of
# "DNMOS20" (D-N-M-O-S has no consecutive D,M,O,S), so a "*DMOS*" pattern
# silently skipped the depletion device and reported its known F1/F2 failures
# as unexpected. Enumerate instead of pattern-matching.
VDMOS_DEVICES = [
    "NDMOS20", "PDMOS20", "DNMOS20", "NDMOS40", "PDMOS40", "NDMOS60",
    "PDMOS60", "NDMOS80", "PDMOS80", "NDMOS120", "PDMOS120",
    "NDMOS200", "PDMOS200",
]
# The 40/80/200 V classes -- phase 1 "ladder B", found ~3x optimistic (F-VD3).
# The 20/60/120 classes ("ladder A") were found IN BAND, so a failure there
# would be genuinely unexpected and must stay a hard-fail.
LADDER_B = ["NDMOS40", "PDMOS40", "NDMOS80", "PDMOS80", "NDMOS200", "PDMOS200"]
BSIM3_DEVICES = ["NMOS12", "PMOS12", "NMOS18", "PMOS18",
                 "NMOS33", "PMOS33", "NMOS50", "PMOS50"]
BJT_DEVICES = ["NPN_LV", "PNP_LAT", "NPN_HV", "PNP_HV"]
ZENERS = ["DZ_5V6", "DZ_12", "DZ_24"]
PASSIVES_R = ["RPOLY_HI", "RPOLY_LO", "RNWELL", "RNPLUS", "RPPLUS"]
PASSIVES_C = ["CMIM_STD", "CMIM_HI", "CMOM", "CFRINGE"]


def _expand(devices, fom, ref):
    return {(d, fom): ref for d in devices}


# FoM that phase 1 predicted would fail. These are the regression tripwires:
# they must be asserted (so a future fix is detected) but reported as expected
# rather than as news. Anything NOT in here that fails is a phase-2 discovery.
EXPECTED_FAIL: dict[tuple[str, str], str] = {}
# PHASE3_FIXED: the fix batch closed F1/F2/F3/F4/F6/F7, ladder-B, NMOS12.
# They now score as normal pass/fail against the merged (v2) anchor bands.
_PHASE3_NEUTRALIZE = True
EXPECTED_FAIL.update(_expand(BSIM3_DEVICES, "flicker_corner",
                             "F3 (BSIM4 noise defaults in BSIM3 cards)"))
EXPECTED_FAIL.update(_expand(BSIM3_DEVICES, "junction_perimeter_set",
                             "F6 (AD/AS/PD/PS unset on the M0 line)"))
EXPECTED_FAIL.update(_expand(BSIM3_DEVICES, "cj_area", "F6"))
EXPECTED_FAIL.update(_expand(BSIM3_DEVICES, "cjsw_sidewall", "F6"))
# F1 -- LDMOS DC scale, all 13 including DNMOS20
EXPECTED_FAIL.update(_expand(VDMOS_DEVICES, "ron_times_w", "F1 (LDMOS DC scale)"))
EXPECTED_FAIL.update(_expand(VDMOS_DEVICES, "rsp_specific_ron", "F1"))
EXPECTED_FAIL.update(_expand(VDMOS_DEVICES, "idsat_density", "F1"))
# F2 -- caps rescaled but never re-derived. Phase 1 sec 2.4 reported cgdmin
# ratios up to 12.2x on the low-voltage cards, so cgdmin belongs here too.
EXPECTED_FAIL.update(_expand(VDMOS_DEVICES, "cgs_per_cell",
                             "F2 (caps rescaled, not re-derived)"))
EXPECTED_FAIL.update(_expand(VDMOS_DEVICES, "cgdmax_per_cell", "F2"))
EXPECTED_FAIL.update(_expand(VDMOS_DEVICES, "cgdmin_per_cell", "F2"))
# F-VD3 -- ladder B only. Ladder A was in band; a failure there is real news.
EXPECTED_FAIL.update(_expand(LADDER_B, "sigma_vth_1sigma_at_wref",
                             "F-VD3 (ladder-B mismatch ~3x optimistic)"))
# F4 -- BJT flicker placeholder
EXPECTED_FAIL.update(_expand(BJT_DEVICES, "flicker_corner",
                             "F4 (kf/af placeholder, bias-independent)"))
# audit 4.5 / 4.4 -- zeners
EXPECTED_FAIL.update(_expand(ZENERS, "bv_tempco",
                             "audit 4.5 (no tbv1/tbv2 on the zener cards)"))
EXPECTED_FAIL.update(_expand(ZENERS, "cjo_density",
                             "audit 4.4 (zener cjo is a hand-picked ladder)"))
# audit 4.6 -- Schottky given minority-carrier stored charge
EXPECTED_FAIL[("DIO_SCH", "tt_transit_time")] = \
    "audit 4.6 (Schottky tt must be 0; majority-carrier device)"
# audit 5.1 / 5.2 -- passives
EXPECTED_FAIL[("RPOLY_HI", "tc1")] = "F7 (lightly-doped poly tc1 sign)"
EXPECTED_FAIL.update(_expand(PASSIVES_R, "matching_A_R_pair_1sigma",
                             "audit 5.2 (passive matching 3-14x optimistic)"))
EXPECTED_FAIL.update(_expand(PASSIVES_C, "matching_A_C_pair_1sigma",
                             "audit 5.2"))

# FoM whose anchor band the audit itself flags as contested -> descriptive only.
if _PHASE3_NEUTRALIZE:
    EXPECTED_FAIL = {}

DESCRIPTIVE = {("*", "ft_at_peak"): "anchor band contested (BCD junction BJT "
                                    "vs SiGe-class) -- open maintainer decision"}


def _glob_match(pat: str, s: str) -> bool:
    if pat == "*":
        return True
    if pat.startswith("*") and pat.endswith("*"):
        return pat[1:-1] in s
    if pat.startswith("*"):
        return s.endswith(pat[1:])
    if pat.endswith("*"):
        return s.startswith(pat[:-1])
    return pat == s


def _lookup(table: dict, device: str, fom: str) -> str | None:
    for (dpat, f), ref in table.items():
        if f == fom and _glob_match(dpat, device):
            return ref
    return None


def artifact_foms(anchors: dict) -> set[str]:
    """FoM names that measure a documented artifact rather than the model."""
    return {"rcond_gate_current", "l_drift_for_bv", "body_diode_tt"}


def score_one(device: str, fom: str, meas: dict, anchor: dict | None,
              artifacts: set[str]) -> dict:
    val = meas.get("value")
    row = {
        "device": device, "fom": fom, "measured": val,
        "units": meas.get("units", ""), "tag": meas.get("tag", ""),
        "deck": meas.get("deck"), "note": meas.get("note", ""),
        "error": meas.get("error"),
        "lo": None, "hi": None, "target": None, "anchor_tag": None,
        "status": "no-anchor", "ref": None, "factor": None,
    }
    if fom in artifacts:
        row["status"] = "artifact"
        row["ref"] = "anchor _known_artifacts"
        return row
    if anchor is None:
        return row
    row["lo"], row["hi"] = anchor.get("lo"), anchor.get("hi")
    row["target"], row["anchor_tag"] = anchor.get("target"), anchor.get("tag")
    if anchor.get("conditional_on"):
        row["status"] = "blocked"
        row["ref"] = anchor["conditional_on"]
        return row
    desc = _lookup(DESCRIPTIVE, device, fom)
    if desc:
        row["status"] = "descriptive"
        row["ref"] = desc
        return row
    if meas.get("error"):
        row["status"] = "error"
        return row
    if val is None:
        row["status"] = "not-measured"
        return row
    lo, hi = row["lo"], row["hi"]
    if lo is None or hi is None:
        return row
    try:
        inside = float(lo) <= float(val) <= float(hi)
    except (TypeError, ValueError):
        row["status"] = "error"
        return row
    if inside:
        row["status"] = "pass"
        return row
    # outside the band -- compute how far
    tgt = row["target"]
    try:
        if tgt not in (None, 0) and val != 0:
            row["factor"] = float(val) / float(tgt)
    except (TypeError, ValueError, ZeroDivisionError):
        pass
    exp = _lookup(EXPECTED_FAIL, device, fom)
    atag = (row["anchor_tag"] or "").lower()
    if exp:
        row["status"] = "expected-fail"
        row["ref"] = exp
    elif atag in ("physics", "model"):
        row["status"] = "hard-fail"
    else:
        row["status"] = "warn"
    return row


def build(results: dict, anchors: dict) -> list[dict]:
    artifacts = artifact_foms(anchors)
    rows: list[dict] = []
    for device, foms in sorted(results.get("devices", {}).items()):
        adev = anchors.get(device, {})
        for fom, meas in sorted(foms.items()):
            rows.append(score_one(device, fom, meas, adev.get(fom), artifacts))
    return rows


def fmt(v, units=""):
    if v is None:
        return "--"
    if isinstance(v, str):
        return v
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    if f != 0 and (abs(f) >= 1e5 or abs(f) < 1e-3):
        return f"{f:.3e}"
    return f"{f:.4g}"


FAMILY = [
    ("BSIM3 MOS", lambda d: d.startswith(("NMOS", "PMOS"))),
    ("VDMOS", lambda d: "DMOS" in d and not d.startswith(("NMOS", "PMOS"))),
    ("BJT", lambda d: d.startswith(("NPN", "PNP"))),
    ("Diodes/zeners", lambda d: d.startswith(("DIO", "DZ"))),
    ("Passives", lambda d: d.startswith(("R", "C"))),
]

STATUS_ORDER = ["hard-fail", "expected-fail", "warn", "blocked", "descriptive",
                "artifact", "error", "not-measured", "no-anchor", "pass"]


def family_of(dev: str) -> str:
    for name, test in FAMILY:
        if test(dev):
            return name
    return "Other"


def render(rows: list[dict], results: dict) -> str:
    meta = results.get("_meta", {})
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    hard = counts.get("hard-fail", 0)

    L: list[str] = []
    L.append("# Characterization Scorecard — AutoHV BiCMOS180 PDK (phase 2 baseline)\n")
    L.append("**This is the before-picture.** No model fixes landed in phase 2; the PDK was")
    L.append("measured as-is so every later fix can be diffed against this baseline.\n")
    L.append(f"- ngspice: `{meta.get('ngspice_version','?')}`")
    L.append(f"- generated: {meta.get('generated','?')}")
    L.append(f"- wall time: {meta.get('wall_seconds','?')} s")
    L.append(f"- results: `pdk_validation/characterization/results/characterization-results.json`")
    L.append(f"- anchors: `docs/anchor-values.json`")
    L.append(f"- harness: `python pdk_validation/characterization/run_all.py`\n")

    L.append("## Status policy (anchor doc §8)\n")
    L.append("| status | meaning |")
    L.append("|---|---|")
    L.append("| `hard-fail` | `[physics]`/`[model]` anchor, measured outside band, **not** predicted by phase 1 |")
    L.append("| `expected-fail` | outside band **and** predicted by a phase-1 finding — the regression tripwires |")
    L.append("| `warn` | `[industry]` anchor outside band — a conversation, not a bug |")
    L.append("| `blocked` | anchor carries `conditional_on`; measured but not asserted |")
    L.append("| `descriptive` | anchor band contested; reported, never scored |")
    L.append("| `artifact` | in `_known_artifacts`; measured, logged, never asserted |")
    L.append("| `pass` | inside band |\n")

    L.append("## Summary\n")
    L.append("| status | count |")
    L.append("|---|---|")
    for s in STATUS_ORDER:
        if counts.get(s):
            L.append(f"| `{s}` | {counts[s]} |")
    L.append(f"| **total** | **{len(rows)}** |\n")

    L.append("### By family\n")
    fams = sorted({family_of(r["device"]) for r in rows})
    hdr = ["family"] + [s for s in STATUS_ORDER if counts.get(s)]
    L.append("| " + " | ".join(hdr) + " |")
    L.append("|" + "---|" * len(hdr))
    for f in fams:
        sub = [r for r in rows if family_of(r["device"]) == f]
        c = {}
        for r in sub:
            c[r["status"]] = c.get(r["status"], 0) + 1
        L.append("| " + " | ".join([f] + [str(c.get(s, 0)) for s in hdr[1:]]) + " |")
    L.append("")

    L.append(f"**Hard-fails not predicted by phase 1: {hard}.** "
             "These are the rows to read first — everything else was already known.\n")

    if hard:
        L.append("## Unexpected hard-fails\n")
        L.append("| device | FoM | measured | band | ×target | deck |")
        L.append("|---|---|---|---|---|---|")
        for r in rows:
            if r["status"] != "hard-fail":
                continue
            band = f"{fmt(r['lo'])} – {fmt(r['hi'])}"
            fac = f"{r['factor']:.3g}×" if r["factor"] else "--"
            L.append(f"| {r['device']} | `{r['fom']}` | {fmt(r['measured'])} "
                     f"{r['units']} | {band} | {fac} | `{r['deck'] or '--'}` |")
        L.append("")

    for fname, _ in FAMILY:
        sub = [r for r in rows if family_of(r["device"]) == fname]
        if not sub:
            continue
        L.append(f"## {fname}\n")
        L.append("| device | FoM | measured | units | band | status | ×target | deck |")
        L.append("|---|---|---|---|---|---|---|---|")
        sub.sort(key=lambda r: (r["device"],
                                STATUS_ORDER.index(r["status"])
                                if r["status"] in STATUS_ORDER else 99,
                                r["fom"]))
        for r in sub:
            band = (f"{fmt(r['lo'])} – {fmt(r['hi'])}"
                    if r["lo"] is not None else "--")
            fac = f"{r['factor']:.3g}×" if r["factor"] else ""
            st = r["status"]
            if st in ("hard-fail", "expected-fail"):
                st = f"**{st}**"
            ref = f" <br>_{r['ref']}_" if r["ref"] else ""
            deck = f"`{r['deck']}`" if r["deck"] else "--"
            L.append(f"| {r['device']} | `{r['fom']}` | {fmt(r['measured'])} | "
                     f"{r['units']} | {band} | {st}{ref} | {fac} | {deck} |")
        L.append("")

    exps = results.get("_experiments", {})
    if exps:
        L.append("## Discrimination experiments (§D)\n")
        L.append("Full payloads in the results JSON under `_experiments`; verdicts in")
        L.append("`pdk_validation/characterization/experiments/README.md`.\n")
        L.append("| experiment | verdict |")
        L.append("|---|---|")
        for k in sorted(exps):
            v = exps[k]
            verdict = v.get("verdict") if isinstance(v, dict) else None
            L.append(f"| `{k}` | {verdict or '(see payload)'} |")
        L.append("")

    errs = results.get("_errors", [])
    if errs:
        L.append(f"## Measurement errors ({len(errs)})\n")
        L.append("| device | FoM | error |")
        L.append("|---|---|---|")
        for e in errs[:60]:
            L.append(f"| {e.get('device')} | `{e.get('fom')}` | {e.get('error')} |")
        L.append("")

    L.append("## Delta vs the phase-1 static audit\n")
    L.append("Every FoM where the measurement disagrees with the phase-1 static prediction")
    L.append("by more than 2× or crosses a verdict boundary is listed in")
    L.append("[`audit-vs-measurement-discrepancies.md`](audit-vs-measurement-discrepancies.md),")
    L.append("with the measured value declared authoritative and the corrected anchor entry")
    L.append("spelled out. That document is the input to the next anchor revision.\n")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--results", default=str(RESULTS))
    a = ap.parse_args()
    with open(a.results, encoding="utf-8") as f:
        results = json.load(f)
    with open(ANCHORS, encoding="utf-8") as f:
        anchors = json.load(f)
    rows = build(results, anchors)
    md = render(rows, results)
    if not a.quiet:
        SCORECARD.parent.mkdir(parents=True, exist_ok=True)
        SCORECARD.write_text(md, encoding="utf-8", newline="\n")
        counts: dict[str, int] = {}
        for r in rows:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        print(f"scorecard -> {SCORECARD.relative_to(REPO_ROOT).as_posix()}")
        for s in STATUS_ORDER:
            if counts.get(s):
                print(f"  {s:15s} {counts[s]}")
    return sum(1 for r in rows if r["status"] == "hard-fail")


if __name__ == "__main__":
    sys.exit(main())
