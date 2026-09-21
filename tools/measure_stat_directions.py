#!/usr/bin/env python3
"""Measure corner directions, per brief v3 rulings Q-A / F3 / G3 / G4, as amended by U2.

  directions For every group, measure g_i = d ln(metric)/d z_i for each variable
             it depends on, then z_fast = 3 g/|g|, z_slow = -z_fast, so the
             Mahalanobis length is 3 by construction.

  Idsat spread  REPORTED, not targeted (ruling U2). U0_<device> is DECLARED at its
             literature mobility spread (_U0_declared), like every other variable,
             and each group's predicted 3-sigma Idsat swing is whatever its own
             grounded inputs produce. The previous pass solved U0 so the swing hit
             an external per-class Idsat band; those bands were externally sourced
             and the LDMOS one was invented, so both are retired. Nothing is now
             tuned to match an outside number.

             The U0-vs-Rd slope probe is kept as a DIAGNOSTIC: where drift
             resistance dominates (LDMOS above ~80 V) U0 has almost no lever, and
             recording that is what carries the U0/Rd anti-correlation.

Metrics, per ruling G3:
  MOS, VDMOS   ln Id.  classic bench Vgs = Vds = class supply (ruling F8);
               analog bench = the sizing guide's gm/Id ~ 6 mirror point.
               DNMOS20 is a depletion device: ln Idss at Vgs = 0.
  resistor     ln R at 0.1 V, low enough that the VCR term stays out of it.
  capacitor    ln C from a small-signal AC current at 0 V bias.
  BJT          ln Ic at the sizing guide's 10 uA point (fixed Vbe).
  diode        ln If at ~100 uA, low enough that RS stays second-order.

How each variable is realized (ruling G4 for VDMOS):
  card parameters      tox, vth0, u0, rdsw, rsh, cj, cjsw, is, bf, rb/rc/re,
                       rs, cjo, bv
  top-level .param     VDMOS VTO_*/KP_*/RD_*/RS_*_STAT
  edge bias            DL_POLY and DW_ACT have no wrapper term yet (Phase 3), so
                       they are realized through the cards' lint/wint, which is
                       exactly equivalent: dL = -2*dlint, dW = -2*dwint. For poly
                       resistors DL_POLY acts on the drawn width, via `narrow`.

Variables with no lever on a group's metric are excluded with a recorded reason
rather than carried as zero components.

  python tools/measure_stat_directions.py --out models/stat_directions.json
  python tools/measure_stat_directions.py --groups NMOS50,RPOLY_HI

Requires NGSPICE_BIN or ngspice on PATH. Nothing in the repo is modified: every
perturbation is written into a scratch copy of the model cards.
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inc_parse  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "autohv_bicmos180_case.lib"
INC = ROOT / "autohv_bicmos180_case_models.inc"
MODEL = ROOT / "models" / "stat_model.json"
SIZING = ROOT / "docs" / "sizing-guide.json"

VT_THERMAL = 0.025852  # kT/q at 27 C

# S2: below this measured slope, U0 is not the variable the band should be
# solved through -- the drift resistance is. Applies to the LDMOS family.
U0_SLOPE_FLOOR = 0.4
U0_HELD_3SIGMA = 0.08   # literature mobility spread where U0 is not solved

# Variables that exist in the model but have no lever on a given metric. Kept
# out of the direction with a reason, rather than sitting in it as a zero.
INERT = {
    "JS_MOS": "junction leakage is picoamps against the bench current",
    "RHEAD": "contact-head resistance has no wrapper term yet (Phase 3)",
    "CPER_flat": "cjsw is 0 on this card, so there is no perimeter lever",
    "TOX_vdmos": "VDMOS cards carry no tox; the oxide reaches them only through "
                 "the KP/VTO loadings that Phase 3 wires",
    "DL_vdmos": "VDMOS cards carry no channel-length parameter to bias",
}

MOS_GROUPS = ["NMOS18", "PMOS18", "NMOS33", "PMOS33", "NMOS50", "PMOS50",
              "NMOS12", "PMOS12"]
VDMOS_GROUPS = ["NDMOS20", "PDMOS20", "NDMOS40", "PDMOS40", "NDMOS60", "PDMOS60",
                "NDMOS80", "PDMOS80", "NDMOS120", "PDMOS120", "NDMOS200",
                "PDMOS200", "DNMOS20"]
RES_GROUPS = ["RPOLY_HI", "RPOLY_LO", "RNWELL", "RNPLUS", "RPPLUS"]
CAP_GROUPS = ["CMIM_STD", "CMIM_HI", "CMOM", "CFRINGE"]
BJT_GROUPS = ["NPN_LV", "PNP_LAT", "NPN_HV", "PNP_HV"]
DIO_GROUPS = ["DIO_PN", "DIO_FAST", "DIO_SCH", "DZ_5V6", "DZ_12", "DZ_24"]
POLY_RES = {"RPOLY_HI", "RPOLY_LO"}


def lmin_um(group: str) -> float:
    """Fabrication minimum L for a group, from device_limits.csv (ruling 4.1)."""
    import csv
    path = ROOT / "pdk_validation" / "device_limits.csv"
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["device"] == group and row["param"] == "L":
                return float(row["min"])
    raise SystemExit(f"no L row for {group} in {path.name}")


def kind_of(group: str) -> str:
    if group in MOS_GROUPS:
        return "mos"
    if group in VDMOS_GROUPS:
        return "vdmos"
    if group in RES_GROUPS:
        return "resistor"
    if group in CAP_GROUPS:
        return "capacitor"
    if group in BJT_GROUPS:
        return "bjt"
    if group in DIO_GROUPS:
        return "diode"
    raise SystemExit(f"unknown group {group}")


def find_ngspice() -> str:
    cand = os.environ.get("NGSPICE_BIN")
    if cand and Path(cand).exists():
        return cand
    for name in ("ngspice_con", "ngspice_con.exe", "ngspice"):
        p = shutil.which(name)
        if p:
            return p
    sys.exit("ngspice not found; set NGSPICE_BIN")


# ------------------------------------------------------------------ scratch

def scratch(workdir: Path, cards: dict[str, dict[str, float]],
            params: dict[str, float]) -> Path:
    """Copy .lib/.inc into workdir with card and top-level .param overrides.

    Card parameters absent from a card are appended, so BSIM3 defaults can be
    overridden too (the k3 lesson from the Phase 0 audit).
    """
    workdir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(LIB, workdir / LIB.name)
    out: list[str] = []
    card, seen = None, set()
    for ln in INC.read_text(encoding="utf-8").splitlines():
        pm = re.match(r"\.param\s+(\w+)\s*=", ln, re.I)
        if pm and pm.group(1) in params:
            out.append(f".param {pm.group(1)}={{{params[pm.group(1)]:.10g}}}")
            continue
        m = re.match(r"\.model\s+(\S+)\s", ln, re.I)
        if m:
            card, seen = m.group(1), set()
        if card in cards and re.match(r"\+\s*\)\s*$", ln):
            for p, v in cards[card].items():
                if p not in seen:
                    out.append(f"+ {p}={v:.10g}")
            card = None
        elif card in cards:
            mm = re.match(r"\+\s*(\w+)\s*=", ln)
            if mm and mm.group(1).lower() in cards[card]:
                p = mm.group(1).lower()
                ln = f"+ {p}={cards[card][p]:.10g}"
                seen.add(p)
        out.append(ln)
    (workdir / INC.name).write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    return workdir


def emission_of(card: str) -> float:
    """The card's emission coefficient: diode `n`, BJT `nf`. Read, never typed.

    Both appear in the same place in the physics -- IS = IS_TT*exp(dV/(n*V_T)) -- and a
    card that declares neither is ideal, n = 1. The four BJTs all carry nf = 1, so this
    changes nothing for them; the six diodes run 1.03 to 1.22.
    """
    for name in ("n", "nf"):
        v = tt_of(name, card)
        if v:
            return v
    return 1.0


def tt_of(name: str, card: str | None = None) -> float | None:
    """TT value of a card parameter or a top-level .param, at case = 0.

    Returns None for exactly ONE reason: the parameter is not on the card (or not a
    top-level .param). That is a fact about the model -- BJT cards genuinely carry no
    `bv` -- and callers test for it.

    It never returns None because it could not read a line. A line that is present but
    unparseable is a defect in this tool, and it stops the run. Conflating those two is
    what silently degraded five direction records: the generated `{TT + sigma*Z}` form
    was unreadable to the old regex, tt_of returned None, and `perturbed()` skipped the
    variable with no record anywhere. See tools/inc_parse.py.
    """
    text = INC.read_text(encoding="utf-8")
    if card:
        m = re.search(rf"^\.model\s+{card}\s.*?(?=^\.model|\Z)", text, re.S | re.M | re.I)
        body = m.group(0) if m else ""
        mm = re.search(rf"^\+\s*{name}\s*=\s*(.+)$", body, re.M | re.I)
    else:
        mm = re.search(rf"^\.param\s+{name}\s*=\s*(.+)$", text, re.M | re.I)
    if not mm:
        return None                       # absent: a fact, not a parse failure
    expr = mm.group(1)
    try:
        p = inc_parse.parse(expr)
    except inc_parse.IncParseError as exc:
        raise SystemExit("measure_stat_directions: cannot read %s%s: %s"
                         % (f"{card}." if card else ".param ", name, exc))
    if p.kind == "reference":
        # The card defers to a top-level .param (a tempco wrapper around FOO_STAT).
        # Follow it rather than reporting no TT, which would drop the variable.
        return tt_of(p.z)
    if p.tt is None:
        raise SystemExit("measure_stat_directions: no TT value for %s%s (%s form): %s"
                         % (f"{card}." if card else ".param ", name, p.kind, expr.strip()))
    return p.tt


# ------------------------------------------------------------------ decks

def deck_mos(group: str, bench: dict, bias: str) -> tuple[str, str]:
    b = bench["classic"] if bias == "classic" else bench["analog"]
    sign = -1.0 if group.startswith("P") else 1.0
    w = bench["W_um"]
    l = bench["L_classic_um"] if bias == "classic" else bench["L_analog_um"]
    body = [f"Vd1 d1 0 {sign * b['Vds']:.6g}", f"Vg1 g1 0 {sign * b['Vgs']:.6g}",
            f"XM1 d1 g1 0 0 {group} W={w:.6g}u L={l:.6g}u M=1"]
    return "\n".join(_wrap(f"{group} {bias}", body,
                           ["op", "print abs(i(Vd1))"])), "i"


def deck_vdmos(group: str, bench: dict, bias: str) -> tuple[str, str]:
    b = bench["classic"] if bias == "classic" else bench["analog"]
    sign = -1.0 if group.startswith("P") else 1.0
    body = [f"Vd1 d1 0 {sign * b['Vds']:.6g}", f"Vg1 g1 0 {sign * b['Vgs']:.6g}",
            f"XM1 d1 g1 0 {group} W={bench['W_um']:.6g}u M=1"]
    return "\n".join(_wrap(f"{group} {bias}", body,
                           ["op", "print abs(i(Vd1))"])), "i"


def deck_resistor(group: str, bench: dict, bias: str) -> tuple[str, str]:
    w, l = bench["W_um"], bench["L_um"]
    body = [f"Vr p 0 {bench['V']:.6g}", f"X1 p 0 {group} L={l:.6g}u W={w:.6g}u"]
    return "\n".join(_wrap(f"{group} R", body, ["op", "print abs(i(Vr))"])), "r"


def deck_capacitor(group: str, bench: dict, bias: str) -> tuple[str, str]:
    s = bench["side_um"]
    body = ["Vac p 0 DC 0 AC 1", f"X1 p 0 {group} L={s:.6g}u W={s:.6g}u"]
    return "\n".join(_wrap(f"{group} C", body,
                           [f"ac lin 1 {bench['freq']:.6g} {bench['freq']:.6g}",
                            "print mag(i(Vac))"])), "c"


def deck_bjt(group: str, bench: dict, bias: str) -> tuple[str, str]:
    """Collector current. `bias` "beta" drives the base with a current source, so
    beta has a lever; the default fixed-Vbe bench is IS/VBE-dominated (G3)."""
    sign = -1.0 if group.startswith("P") else 1.0
    if bias == "beta":
        body = [f"Vc c 0 {sign * bench['Vce']:.6g}",
                f"Ib 0 b {sign * bench['Ib']:.6g}",
                f"X1 c b 0 {group} AREA={bench['AREA']:.6g}"]
    else:
        body = [f"Vc c 0 {sign * bench['Vce']:.6g}",
                f"Vb b 0 {sign * bench['Vbe']:.6g}",
                f"X1 c b 0 {group} AREA={bench['AREA']:.6g}"]
    return "\n".join(_wrap(f"{group} Ic ({bias})", body,
                            ["op", "print abs(i(Vc))"])), "i"


def deck_diode(group: str, bench: dict, bias: str) -> tuple[str, str]:
    body = [f"Vf a 0 {bench['Vf']:.6g}", f"X1 a 0 {group} AREA={bench['AREA']:.6g}"]
    return "\n".join(_wrap(f"{group} If", body, ["op", "print abs(i(Vf))"])), "i"


def _wrap(title: str, body: list[str], control: list[str]) -> list[str]:
    return ([f"* direction bench: {title}", f'.include "{LIB.name}"',
             ".param case=0", ".param PROC_ON=0", ".param MM_ON=0",
             ".option num_threads=1"] + body +
            [".control", "option temp=27", "option numdgt=12"] + control +
            [".endc", ".end", ""])


BUILDERS = {"mos": deck_mos, "vdmos": deck_vdmos, "resistor": deck_resistor,
            "capacitor": deck_capacitor, "bjt": deck_bjt, "diode": deck_diode}


def measure(ng: str, workdir: Path, deck: str, mode: str, bench: dict) -> float:
    with tempfile.NamedTemporaryFile("w", suffix=".cir", dir=workdir,
                                     delete=False, encoding="utf-8") as f:
        f.write(deck)
        path = f.name
    try:
        r = subprocess.run([ng, "-b", Path(path).name], cwd=str(workdir),
                           capture_output=True, text=True, timeout=90)
        out = r.stdout + r.stderr
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
    m = re.search(r"(?:abs\(i\(v\w+\)\)|mag\(i\(vac\)\))\s*=\s*([-\d.eE+]+)", out, re.I)
    if not m:
        raise RuntimeError(f"no metric:\n{out[-700:]}")
    v = abs(float(m.group(1)))
    if v <= 0:
        raise RuntimeError("non-positive metric")
    if mode == "r":
        return bench["V"] / v                      # ln R
    if mode == "c":
        return v / (2 * math.pi * bench["freq"])   # ln C
    return v                                       # ln I


# ------------------------------------------------------------------ variables

NO_LEVER_REASON = {
    "BV_": "breakdown has no lever on drain current at the bench bias "
           "(the device is biased far below its rating)",
    "CJ_": "junction capacitance has no lever on a DC forward current",
}


def perturbations(group: str, model: dict) -> tuple[dict, dict]:
    """Returns (realizable perturbations, excluded {variable: reason})."""
    gv, kind, card = model["global_variables"], kind_of(group), f"{group}_INT"
    out, dead = {}, {}

    def add(var, *, param=None, pname=None, form="multiplicative", sigma=None,
            scale=1.0, extra_params=()):
        out[var] = {"card": card if param else None, "param": param, "pname": pname,
                    "form": form, "sigma": sigma, "scale": scale,
                    "extra": list(extra_params)}

    for name, v in gv.items():
        if name.startswith("_") or group not in v.get("shared_by", []):
            continue
        sig = v.get("sigma")
        if name.startswith("TOX_"):
            if kind == "vdmos":
                dead[name] = INERT["TOX_vdmos"]
            else:
                add(name, param="tox", sigma=sig)
        elif name.startswith("VTH_"):
            if kind == "vdmos":
                add(name, pname=f"VTO_{group}_STAT", form="additive", sigma=sig)
            else:
                add(name, param="vth0", form="additive", sigma=sig)
        elif name == "DL_POLY":
            if kind == "mos":
                add(name, param="lint", form="additive", sigma=sig, scale=-0.5)
            elif kind == "resistor" and group in POLY_RES:
                add(name, param="narrow", form="additive", sigma=sig, scale=-1.0)
            else:
                dead[name] = INERT["DL_vdmos"]
        elif name.startswith("DW_ACT"):
            if kind == "mos":
                add(name, param="wint", form="additive", sigma=sig, scale=-0.5)
            else:
                dead[name] = INERT["DL_vdmos"]
        elif name.startswith("RSH_") and kind == "resistor":
            add(name, param="rsh", sigma=sig)
        elif name.startswith("RSH_GATE"):
            dead[name] = "no rgate term in the wrappers yet (Phase 3)"
        elif name.startswith("CDEN_") and kind == "capacitor":
            add(name, param="cj", sigma=sig)
        elif name == "JS_MOS":
            dead[name] = INERT["JS_MOS"]

    # template-backed variables, named as stat_model.json names them
    t = gv.get("_RDSW_template", {})
    if group in t.get("devices_mos", []):
        add(f"RDSW_{group}", param="rdsw", sigma=t["sigma"])
    elif group in t.get("devices_vdmos", []):
        add(f"RDSW_{group}", pname=f"RD_{group}_STAT", sigma=t["sigma"],
            extra_params=[f"RS_{group}_STAT"])

    for tname, prefix, spec in (
            ("_RHEAD_template", "RHEAD_", None),
            ("_CPER_template", "CPER_", ("cjsw", "multiplicative")),
            ("_VBE_template", "VBE_", ("is", "vbe")),
            ("_BF_template", "BF_", ("bf", "multiplicative")),
            ("_RPAR_template", "RPAR_", ("rb", "rpar")),
            ("_VF_template", "VF_", ("is", "vf")),
            ("_RS_DIO_template", "RS_", ("rs", "multiplicative")),
            ("_CJ_DIO_template", "CJ_", ("cjo", "multiplicative")),
            ("_BV_template", "BV_", ("bv", "multiplicative"))):
        tt = gv.get(tname, {})
        members = tt.get("devices") or tt.get("layers") or tt.get("types") or []
        if group not in members:
            continue
        var = prefix + group
        if spec is None:
            dead[var] = INERT["RHEAD"]
            continue
        param, form = spec
        if param == "cjsw" and not tt_of("cjsw", card):
            dead[var] = INERT["CPER_flat"]
            continue
        if param == "bv" and tt_of("bv", card) is None:
            # BJT cards carry no bv; their breakdown is the wrapper's BVCBO. Record
            # the exclusion with the same reason the VDMOS BV_* get, rather than
            # letting the variable vanish from the direction unrecorded (AD1).
            dead[var] = NO_LEVER_REASON["BV_"]
            continue
        if form in ("vbe", "vf"):
            # IS = IS_TT*exp(dV/(n*V_T)): the emission coefficient belongs in the scale.
            # It is read from the card, never typed -- the six diodes run n = 1.03 to 1.22,
            # so a single constant would be up to 22 % wrong, and worst on the Zeners.
            add(var, param="is", form="exp_v", sigma=tt["sigma"],
                scale=1.0 / (emission_of(card) * VT_THERMAL))
        elif form == "rpar":
            add(var, param="rb", sigma=tt["sigma"], extra_params=["rc", "re"])
        else:
            add(var, param=param, form=form, sigma=tt["sigma"])
    return out, dead


SKIPPED: set[str] = set()
"""(card, param) targets a variable named but the model file does not carry.

Not an error -- the model may legitimately point at a parameter a given card lacks --
but never silent either. An unnoticed skip here is precisely how DNMOS20 fell to a
zero-length direction with nothing in the record to show for it.
"""


def perturbed(spec: dict, sgn: int) -> tuple[dict, dict]:
    """Build the (card, param) override dicts for +/-1 sigma of one variable."""
    cards, params = {}, {}
    sigma, scale = spec["sigma"], spec["scale"]
    targets = [(spec["card"], spec["param"])] if spec["param"] else []
    targets += [(spec["card"], p) for p in spec["extra"] if spec["param"]]
    pnames = ([spec["pname"]] if spec["pname"] else []) + \
             ([p for p in spec["extra"] if not spec["param"]])

    def new_value(tt: float) -> float:
        if spec["form"] == "additive":
            return tt + sgn * sigma * scale
        if spec["form"] == "exp_v":
            return tt * math.exp(sgn * sigma * scale)
        return tt * math.exp(sgn * math.log1p(sigma))

    for card, param in targets:
        tt = tt_of(param, card)
        if tt is None:
            SKIPPED.add(f"{card}.{param}")     # absent from the card; recorded, not silent
            continue
        cards.setdefault(card, {})[param] = new_value(tt)
    for pname in pnames:
        tt = tt_of(pname)
        if tt is None:
            SKIPPED.add(f".param {pname}")
            continue
        params[pname] = new_value(tt)
    return cards, params


def bench_for(group: str, model: dict, sizing: dict) -> dict:
    kind = kind_of(group)
    b = dict(model["benches"].get(group, {}))
    if kind == "mos":
        b["L_analog_um"] = b.get("L_um", 1.0)
        b["L_classic_um"] = lmin_um(group)      # ruling 4.1
    if kind == "resistor":
        b.update({"W_um": 2.0, "L_um": 16.5, "V": 0.1})
    elif kind == "capacitor":
        b.update({"side_um": 100.0, "freq": 1e6})
    elif kind == "bjt":
        pt = sizing["bjt"][group]["10uA"]
        b.update({"Vbe": pt["Vbe_V"], "Vce": 2.0, "AREA": 1.0,
                  "Ib": 1e-5 / max(pt.get("beta", 100.0), 1.0)})
    elif kind == "diode":
        b.update({"AREA": 1.0, "Vf": None})
    return b


def solve_diode_vf(ng: str, group: str, bench: dict, work: Path,
                   target_a: float = 1e-4) -> float:
    """Find the forward voltage giving ~target current at TT, by bisection."""
    lo, hi = 0.2, 1.2
    d = scratch(work / f"{group}_vf", {}, {})
    for _ in range(24):
        mid = 0.5 * (lo + hi)
        deck, mode = deck_diode(group, {**bench, "Vf": mid}, "classic")
        try:
            i = measure(ng, d, deck, mode, bench)
        except RuntimeError:
            i = 0.0
        if i < target_a:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def measure_group(ng: str, group: str, model: dict, sizing: dict, work: Path,
                  sigma_overrides: dict[str, float] | None = None,
                  bias_override: str | None = None) -> dict:
    kind = kind_of(group)
    bench = bench_for(group, model, sizing)
    if kind == "diode" and bench.get("Vf") is None:
        bench["Vf"] = solve_diode_vf(ng, group, bench, work)
    perts, dead = perturbations(group, model)
    for var, sig in (sigma_overrides or {}).items():
        if var in perts:
            perts[var] = {**perts[var], "sigma": sig}
        elif var.startswith("U0_") and kind in ("mos", "vdmos"):
            perts[var] = ({"card": None, "param": None, "pname": f"KP_{group}_STAT",
                           "form": "multiplicative", "sigma": sig, "scale": 1.0, "extra": []}
                          if kind == "vdmos" else
                          {"card": f"{group}_INT", "param": "u0", "pname": None,
                           "form": "multiplicative", "sigma": sig, "scale": 1.0, "extra": []})

    builder = BUILDERS[kind]
    if bias_override:
        biases = (bias_override,)
    else:
        biases = ("classic", "analog") if kind in ("mos", "vdmos") else ("classic",)
    result = {"bench": bench, "kind": kind, "excluded": dead, "g": {}, "g_analog": {}}
    for bias in biases:
        key = "g_analog" if bias == "analog" else "g"
        base_dir = scratch(work / f"{group}_{bias}_base", {}, {})
        deck, mode = builder(group, bench, bias)
        base = measure(ng, base_dir, deck, mode, bench)
        result[f"metric_{bias}"] = base
        for vname, spec in perts.items():
            vals = {}
            for sgn in (+1, -1):
                cards, params = perturbed(spec, sgn)
                if not cards and not params:
                    break
                d = scratch(work / f"{group}_{bias}_{vname}_{sgn}", cards, params)
                deck, mode = builder(group, bench, bias)
                vals[sgn] = measure(ng, d, deck, mode, bench)
            if len(vals) == 2:
                result[key][vname] = (math.log(vals[+1]) - math.log(vals[-1])) / 2.0
    return result


# A variable whose measured |g| is below this is treated as having no lever on
# the metric: it is moved to `excluded` with a reason instead of sitting in the
# direction as a zero. The threshold is well under the smallest real term seen
# (RDSW on a MOS classic bench, ~7e-4).
NO_LEVER = 1e-9



def prune_no_lever(rec: dict) -> None:
    """Move measured-zero variables out of the direction, with a reason."""
    for var, g in list(rec["g"].items()):
        if abs(g) > NO_LEVER:
            continue
        reason = next((r for pre, r in NO_LEVER_REASON.items() if var.startswith(pre)),
                      "measured lever on this metric is zero")
        rec["excluded"][var] = reason
        rec["g"].pop(var)
        rec["g_analog"].pop(var, None)


def direction(g: dict[str, float]) -> tuple[dict[str, float], float]:
    norm = math.sqrt(sum(v * v for v in g.values()))
    if norm == 0:
        return {k: 0.0 for k in g}, 0.0
    return {k: 3.0 * v / norm for k, v in g.items()}, norm


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--groups", help="comma-separated subset (default: all 40)")
    ap.add_argument("--out", default="models/stat_directions.json")
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args(argv)

    ng = find_ngspice()
    model = json.loads(MODEL.read_text(encoding="utf-8"))
    sizing = json.loads(SIZING.read_text(encoding="utf-8"))
    groups = (args.groups.split(",") if args.groups else
              MOS_GROUPS + VDMOS_GROUPS + RES_GROUPS + CAP_GROUPS + BJT_GROUPS + DIO_GROUPS)

    u0d = model["global_variables"]["_U0_declared"]
    u0_sigma, floor3 = u0d["sigma"], u0d["floor_3sigma"]
    # sigma(KP) = 0 where the drift region dominates: mobility has no meaningful
    # lever there, so the variable is dropped rather than carried as a near-zero.
    u0_zero = set(u0d.get("sigma_zero_devices", []))
    work = Path(tempfile.mkdtemp(prefix="statdir_"))
    out = {"_meta": {"ngspice": ng, "model": "models/stat_model.json",
                     "bench_rule": "classic = Vgs = Vds = class supply (ruling F8); "
                                   "metrics per ruling G3"},
           "groups": {}}
    try:
        for g in groups:
            kind = kind_of(g)
            if kind in ("mos", "vdmos"):
                probe = 0.01
                u0_var, rd_var = f"U0_{g}", f"RDSW_{g}"

                # Diagnostic only (U2): which variable actually has the lever.
                # Where drift resistance dominates, U0 has almost none -- that is
                # the U0/Rd anti-correlation, recorded rather than solved around.
                u0_slope = abs(measure_group(ng, g, model, sizing, work,
                                             {u0_var: probe})["g"].get(u0_var, 0.0)) / probe
                dominant = u0_var if u0_slope >= U0_SLOPE_FLOOR else rd_var

                # U0 is declared, like everything else. No band, no solve.
                sig = 0.0 if g in u0_zero else u0_sigma
                full = measure_group(ng, g, model, sizing, work, {u0_var: sig})
                rec = {"u0_sigma_1s": sig,
                       "u0_source": ("declared (_U0_declared), sigma forced to 0: drift-dominated"
                                     if g in u0_zero else "declared (_U0_declared)"),
                       "u0_slope_measured": u0_slope,
                       "dominant_variable": dominant,
                       "u0_floor_3sigma": floor3}
                print(f"{g:9s} {kind:9s} u0 {sig*100:4.2f} %  u0slope {u0_slope:4.2f}  "
                      f"dom {dominant.split('_')[0]:4s}", end="")
            else:
                full = measure_group(ng, g, model, sizing, work, None)
                rec = {}
                print(f"{g:9s} {kind:9s}", end="")
            prune_no_lever(full)
            if kind == "bjt":
                beta = measure_group(ng, g, model, sizing, work, None, bias_override="beta")
                bf_var = f"BF_{g}"
                full["bf_share"] = {
                    "bench": "base-current driven (ruling G3)",
                    "g_beta_bench": beta["g"].get(bf_var),
                    "g_fixed_vbe_bench": full["g"].get(bf_var),
                    "note": "BF has no lever at a fixed-Vbe bench; the beta-bench value is "
                            "what a beta-only corner must use",
                }
                if beta["g"].get(bf_var) is not None:
                    full["g"][bf_var] = beta["g"][bf_var]
            z_fast, norm = direction(full["g"])
            rec["predicted_3sigma_swing"] = 3.0 * norm
            rec["metric_3sigma_swing"] = 3.0 * norm
            print(f"  swing {3*norm*100:5.1f} %  terms {len(full['g'])}  "
                  f"excluded {len(full['excluded'])}")
            rec.update({"bench": full["bench"], "kind": full["kind"],
                        "metric_classic": full.get("metric_classic"),
                        "metric_analog": full.get("metric_analog"),
                        "g_classic": full["g"], "g_analog": full["g_analog"],
                        "excluded": full["excluded"], "z_fast": z_fast,
                        "mahalanobis": 3.0})
            if "bf_share" in full:
                rec["bf_share"] = full["bf_share"]
            out["groups"][g] = rec
    finally:
        if not args.keep:
            shutil.rmtree(work, ignore_errors=True)

    (ROOT / args.out).write_text(json.dumps(out, indent=1) + "\n",
                                 encoding="utf-8", newline="\n")
    print(f"wrote {args.out} for {len(out['groups'])} of 40 groups")
    if SKIPPED:
        # Targets the model named but the cards do not carry. Reported, never silent.
        print("skipped %d target(s) absent from the model file: %s"
              % (len(SKIPPED), ", ".join(sorted(SKIPPED))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
