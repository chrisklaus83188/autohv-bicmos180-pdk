#!/usr/bin/env python3
"""Measure the corner directions and calibrate U0, per brief v3 ruling Q-A / F3.

Two passes, both measurement rather than assertion:

  calibrate  For each MOS group, solve the U0 sigma that makes the group's
             3-sigma Idsat swing along its own worst-case direction equal the
             ONC25 class band. The fixed set during calibration is VTH, TOX,
             DL_POLY, DW_ACT and RDSW at their grounded sigma (ruling F3a).
             U0 is floored at 3 % 3-sigma; if the floor binds, the fixed set
             already exceeds the band and that is reported, not tuned away.

  directions For every group, measure g_i = d ln(metric)/d z_i for each
             variable it depends on, then z_fast = 3 g/|g|, z_slow = -z_fast.
             Mahalanobis length is 3 by construction. Measured on the classic
             bench (Vgs = Vds = class supply, ruling F8); the analog bench
             (gm/Id ~ 6) is measured too and reported alongside.

Each variable is perturbed by writing its parameter into a scratch copy of the
model cards -- the wrappers are not modified and the repo is not touched.

  python tools/measure_stat_directions.py --out models/stat_directions.json
  python tools/measure_stat_directions.py --groups NMOS50,PMOS50   # subset

Requires NGSPICE_BIN or ngspice on PATH.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "autohv_bicmos180_case.lib"
INC = ROOT / "autohv_bicmos180_case_models.inc"
MODEL = ROOT / "models" / "stat_model.json"

# Junction saturation current sets leakage (picoamps here) and has no lever on
# an Idsat/Ic direction; it stays in stat_model.json but out of the direction.
METRIC_INERT = {"JS_MOS"}

MOS_GROUPS = ["NMOS18", "PMOS18", "NMOS33", "PMOS33", "NMOS50", "PMOS50",
              "NMOS12", "PMOS12"]
VDMOS_GROUPS = ["NDMOS20", "PDMOS20", "NDMOS40", "PDMOS40", "NDMOS60", "PDMOS60",
                "NDMOS80", "PDMOS80", "NDMOS120", "PDMOS120", "NDMOS200",
                "PDMOS200", "DNMOS20"]


def find_ngspice() -> str:
    cand = os.environ.get("NGSPICE_BIN")
    if cand and Path(cand).exists():
        return cand
    for name in ("ngspice_con", "ngspice_con.exe", "ngspice"):
        p = shutil.which(name)
        if p:
            return p
    sys.exit("ngspice not found; set NGSPICE_BIN")


# ---------------------------------------------------------------- card edits

def card_of(group: str) -> str:
    return f"{group}_INT"


def scratch_lib(workdir: Path, overrides: dict[str, dict[str, float]]) -> Path:
    """Copy .lib/.inc into workdir, applying {card: {param: value}} overrides.

    Parameters absent from a card are appended, so BSIM3 defaults can be
    overridden too (the k3 lesson from the Phase 0 audit).
    """
    workdir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(LIB, workdir / LIB.name)
    out: list[str] = []
    card, seen = None, set()
    for ln in INC.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\.model\s+(\S+)\s", ln, re.I)
        if m:
            card, seen = m.group(1), set()
        if card in overrides and re.match(r"\+\s*\)\s*$", ln):
            for p, v in overrides[card].items():
                if p not in seen:
                    out.append(f"+ {p}={v:.10g}")
            card = None
        elif card in overrides:
            mm = re.match(r"\+\s*(\w+)\s*=", ln)
            if mm and mm.group(1).lower() in overrides[card]:
                p = mm.group(1).lower()
                ln = f"+ {p}={overrides[card][p]:.10g}"
                seen.add(p)
        out.append(ln)
    (workdir / INC.name).write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    return workdir


# ---------------------------------------------------------------- benches

def deck_mos(group: str, bench: dict, bias: str) -> str:
    b = bench["classic"] if bias == "classic" else bench["analog"]
    w, l = bench["W_um"], bench.get("L_um", 1.0)
    ports = "d1 g1 0 0" if group.startswith(("N", "P")) and "DMOS" not in group else "d1 g1 0"
    sign = -1.0 if group.startswith("P") else 1.0
    return "\n".join([
        f"* direction bench: {group} ({bias})",
        f'.include "{LIB.name}"',
        ".param case=0", ".param PROC_ON=0", ".param MM_ON=0",
        ".option num_threads=1",
        f"Vd1 d1 0 {sign * b['Vds']:.6g}",
        f"Vg1 g1 0 {sign * b['Vgs']:.6g}",
        f"XM1 {ports} {group} W={w:.6g}u" + (f" L={l:.6g}u" if "DMOS" not in group else "") + " M=1",
        ".control", "option temp=27", "option numdgt=12", "op",
        "print abs(i(Vd1))", ".endc", ".end", ""])


def run_metric(ng: str, workdir: Path, deck: str) -> float:
    with tempfile.NamedTemporaryFile("w", suffix=".cir", dir=workdir,
                                     delete=False, encoding="utf-8") as f:
        f.write(deck)
        path = f.name
    try:
        r = subprocess.run([ng, "-b", Path(path).name], cwd=str(workdir),
                           capture_output=True, text=True, timeout=60)
        out = r.stdout + r.stderr
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
    m = re.search(r"abs\(i\(vd1\)\)\s*=\s*([-\d.eE+]+)", out)
    if not m:
        raise RuntimeError(f"no metric from bench:\n{out[-600:]}")
    v = float(m.group(1))
    if v <= 0:
        raise RuntimeError(f"non-positive metric {v}")
    return v


# ---------------------------------------------------------------- variables

def tt_value(card: str, param: str) -> float | None:
    """TT value of a card parameter, evaluating the corner expression at case=0."""
    text = INC.read_text(encoding="utf-8")
    m = re.search(rf"^\.model\s+{card}\s.*?(?=^\.model|\Z)", text, re.S | re.M | re.I)
    body = m.group(0) if m else text
    mm = re.search(rf"^\+\s*{param}\s*=\s*(.+)$", body, re.M | re.I)
    if not mm:
        return None
    expr = mm.group(1)
    tt = re.search(r"([-\d.eE+]+)\s*\*\s*_isTT", expr)
    if tt:
        return float(tt.group(1))
    plain = re.match(r"\s*([-\d.eE+]+)\s*$", expr)
    return float(plain.group(1)) if plain else None


def perturbations(group: str, model: dict) -> dict[str, dict]:
    """Which variables touch this group, and how to realize +1 sigma of each."""
    gv = model["global_variables"]
    card = card_of(group)
    out: dict[str, dict] = {}
    is_vdmos = "DMOS" in group

    for name, v in gv.items():
        if name.startswith("_") or group not in v.get("shared_by", []):
            continue
        for ap in v.get("applies_to", []):
            param = ap.get("param", "")
            if not param or "*" in param or ap["form"] == "via-loading":
                continue
            if param in ("tox", "vth0", "u0", "rdsw", "js") and not is_vdmos:
                out[name] = {"card": card, "param": param, "form": ap["form"],
                             "sigma": v["sigma"]}
    # templates carry a device list rather than shared_by; name the expanded
    # variable the way stat_model.json names it, so corners.json can join.
    for tname, key, param, prefix in (("_U0_calibration", "devices", "u0", "U0_"),
                                      ("_RDSW_template", "devices_mos", "rdsw", "RDSW_")):
        t = gv.get(tname, {})
        if group in t.get(key, []):
            sigma = t.get("sigma")
            if sigma is not None:
                out[prefix + group] = {"card": card, "param": param,
                                       "form": "multiplicative", "sigma": sigma}
    # Variables with no lever on this metric are excluded, not carried as zeros.
    for dead in [k for k in out if k in METRIC_INERT]:
        out.pop(dead)
    return out


def measure_group(ng: str, group: str, model: dict, work: Path,
                  u0_sigma: float | None) -> dict:
    bench = model["benches"][group]
    perts = perturbations(group, model)
    if u0_sigma is not None:
        # Same name stat_model.json uses, so main() can read the slope back and
        # corners.json can join to the model.
        perts[f"U0_{group}"] = {"card": card_of(group), "param": "u0",
                                "form": "multiplicative", "sigma": u0_sigma}

    result = {"bench": bench, "g": {}, "g_analog": {}}
    for bias, key in (("classic", "g"), ("analog", "g_analog")):
        base_dir = scratch_lib(work / f"{group}_{bias}_base", {})
        base = run_metric(ng, base_dir, deck_mos(group, bench, bias))
        result[f"metric_{bias}"] = base
        for vname, spec in perts.items():
            tt = tt_value(spec["card"], spec["param"])
            if tt is None:
                continue
            vals = {}
            for sgn in (+1, -1):
                if spec["form"] == "additive":
                    new = tt + sgn * spec["sigma"]
                else:
                    new = tt * math.exp(sgn * math.log1p(spec["sigma"]))
                d = scratch_lib(work / f"{group}_{bias}_{vname}_{sgn}",
                                {spec["card"]: {spec["param"]: new}})
                vals[sgn] = run_metric(ng, d, deck_mos(group, bench, bias))
            result[key][vname] = (math.log(vals[+1]) - math.log(vals[-1])) / 2.0
    return result


def direction(g: dict[str, float]) -> tuple[dict[str, float], float]:
    norm = math.sqrt(sum(v * v for v in g.values()))
    if norm == 0:
        return {k: 0.0 for k in g}, 0.0
    return {k: 3.0 * v / norm for k, v in g.items()}, norm


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--groups", help="comma-separated subset (default: all MOS groups)")
    ap.add_argument("--out", default="models/stat_directions.json")
    ap.add_argument("--keep", action="store_true", help="keep the scratch decks")
    args = ap.parse_args(argv)

    ng = find_ngspice()
    model = json.loads(MODEL.read_text(encoding="utf-8"))
    groups = (args.groups.split(",") if args.groups
              else [g for g in MOS_GROUPS + VDMOS_GROUPS if g in model["benches"]])

    work = Path(tempfile.mkdtemp(prefix="statdir_"))
    bands = model["global_variables"]["_U0_calibration"]["class_bands_3sigma"]
    floor3 = model["global_variables"]["_U0_calibration"]["floor_3sigma"]
    out = {"_meta": {"ngspice": ng, "model": str(MODEL.relative_to(ROOT)),
                     "bench_rule": "classic = Vgs = Vds = class supply (ruling F8)"},
           "groups": {}}
    try:
        for g in groups:
            cls = re.sub(r"^[NP]?(MOS|DMOS)", "", g) or "vdmos"
            band = bands.get(cls, bands.get("vdmos"))
            fixed = measure_group(ng, g, model, work, u0_sigma=None)
            gvec = fixed["g"]
            swing_fixed = 3.0 * math.sqrt(sum(v * v for v in gvec.values()))

            # Measure d ln(metric)/d z_u0 at a probe sigma rather than assuming
            # it is 1 per unit relative u0: on these cards it is ~0.84, and
            # assuming it undershoots the class band (Phase 0 lesson).
            probe = 0.01
            probed = measure_group(ng, g, model, work, u0_sigma=probe)
            slope = abs(probed["g"].get("U0_" + g, 0.0)) / probe
            if slope <= 0:
                sys.exit(f"{g}: u0 has no measurable lever on the metric")
            if swing_fixed >= band:
                u0_sigma, floored = floor3 / 3.0, True
            else:
                need = math.sqrt(max(band ** 2 - swing_fixed ** 2, 0.0)) / 3.0 / slope
                floored = need < floor3 / 3.0
                u0_sigma = max(need, floor3 / 3.0)
            full = measure_group(ng, g, model, work, u0_sigma=u0_sigma)
            z_fast, norm = direction(full["g"])
            out["groups"][g] = {
                "bench": full["bench"],
                "class_band_3sigma": band,
                "u0_sigma_1s": u0_sigma,
                "u0_floor_hit": floored,
                "fixed_set_3sigma_swing": swing_fixed,
                "u0_slope_measured": slope,
                "band_error_pct": 100.0 * (3.0 * norm / band - 1.0),
                "g_classic": full["g"],
                "g_analog": full["g_analog"],
                "z_fast": z_fast,
                "idsat_3sigma_swing": 3.0 * norm,
                "mahalanobis": 3.0,
            }
            print(f"{g:9s} band {band*100:5.1f} %  fixed-set {swing_fixed*100:5.1f} %  "
                  f"slope {slope:4.2f}  u0 1s {u0_sigma*100:5.2f} %"
                  f"{'  FLOOR' if floored else ''}  swing {3*norm*100:5.1f} %  "
                  f"err {100*(3*norm/band-1):+5.1f} %")
    finally:
        if not args.keep:
            shutil.rmtree(work, ignore_errors=True)

    Path(ROOT / args.out).write_text(json.dumps(out, indent=1) + "\n",
                                     encoding="utf-8", newline="\n")
    print(f"wrote {args.out} for {len(out['groups'])} groups")
    return 0


if __name__ == "__main__":
    sys.exit(main())
