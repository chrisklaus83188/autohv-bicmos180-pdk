#!/usr/bin/env python3
"""Generate docs/stat-model-inventory.md from the PDK library.

One row per device wrapper in autohv_bicmos180_case.lib: family, rated voltage,
instance parameters, mismatch terms with coefficient and sigma convention, the
area term the mismatch scales with, and the MC realism program work list
(docs/backlog/HANDOFF_mc_realism_brief.md as amended by
docs/backlog/HANDOFF_mc_realism_rulings.md).

  python tools/stat_model_inventory.py           # write the document
  python tools/stat_model_inventory.py --check   # exit 1 if the document is stale
"""
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "autohv_bicmos180_case.lib"
INC = ROOT / "autohv_bicmos180_case_models.inc"
LIMITS = ROOT / "pdk_validation" / "device_limits.csv"
OUT = ROOT / "docs" / "stat-model-inventory.md"

GEOM_PARAMS = ("lint", "wint", "dwc", "dlc", "xl", "xw", "narrow", "short")
RATED_PARAMS = ("Vds_dcmax", "Vce_max", "Vr_absmax", "Vop_max", "Vabs_max")
LV_FET_MAX_V = 6.0   # a BSIM3 FET rated at or below this Vds_dcmax is an LV FET

TERM_LABEL = {
    "DVTH_MM": "Vth (delvto)",
    "DWREL_MM": "W, relative",
    "DLREL_MM": "L, relative",
    "RMM": "R, lumped (applied to L)",
    "CMM": "C, lumped (applied to area)",
    "AREAEFF": "AREA, relative",
}
# AGAUSS(0, coef[/sqrt(scale)], n)[/sqrt(scale)] -- the scale may carry one nested call
_SQRT = r"sqrt\(([^()]*(?:\([^()]*\))?[^()]*)\)"
AGAUSS = re.compile(r"AGAUSS\(\s*0\s*,\s*([-\d.eE+]+)\s*(?:/\s*" + _SQRT +
                    r")?\s*,\s*(\d+)\s*\)(?:\s*/\s*" + _SQRT + r")?")

# Program work list per family (brief section 2 scope table as amended by the rulings)
WORK = {
    "LV FET": ("fix `AUM2` to include `M`; add `NF` (Q10 stripe rule)", "`Z_VT` `Z_W` `Z_L`"),
    "HV FET": ("fix `AUM2` to include `M`; add `NF` (Q10 stripe rule)", "`Z_VT` `Z_W` `Z_L`"),
    "VDMOS/LDMOS": ("none: `M` already R1-correct via `mtot`; no `NF` (D2)", "`Z_VT`"),
    "resistor": ("add `M`; add `NS` (R3, D4/D5)", "`Z_R`"),
    "capacitor": ("add `M`", "`Z_C`"),
    "BJT": ("none", "`Z_AREA`"),
    "diode": ("none", "`Z_AREA`"),
}


def parse_lib():
    devs, cur, header = [], None, []
    for ln in LIB.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\.subckt\s+(\S+)\s+(.*?)\s+params:\s*(.*)$", ln, re.I)
        if m:
            cur = {"name": m.group(1), "ports": m.group(2).split(),
                   "params": dict(re.findall(r"(\w+)=(\S+)", m.group(3))), "body": []}
        elif cur is not None:
            if re.match(r"\.ends\b", ln, re.I):
                devs.append(cur)
                cur = None
            else:
                cur["body"].append(ln)
        elif not devs:
            header.append(ln)
    return devs, header


def parse_models():
    cards, cur = {}, None
    for ln in INC.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\.model\s+(\S+)\s+(\w+)", ln, re.I)
        if m:
            cur = m.group(1)
            cards[cur] = {"type": m.group(2).upper(), "lines": []}
        elif cur and ln.startswith("+"):
            cards[cur]["lines"].append(ln)
        else:
            cur = None
    return cards


def parse_limits():
    rated = {}
    with open(LIMITS, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for p in RATED_PARAMS:
        for r in rows:
            if r["param"] == p and r["device"] not in rated:
                # PMOS limits are stored as negative ranges; the rating is the magnitude
                rated[r["device"]] = (p, max(abs(float(r["min"])), abs(float(r["max"]))))
    return rated


def body_params(body):
    out = {}
    for ln in body:
        m = re.match(r"\.param\s+(\w+)\s*=\s*\{(.*)\}\s*(?:;.*)?$", ln)
        if m:
            out[m.group(1)] = m.group(2)
        else:
            m = re.match(r"\.param\s+(\w+)\s*=\s*(\S+)", ln)
            if m:
                out[m.group(1)] = m.group(2)
    return out


def inner_device(body):
    for ln in body:
        if re.match(r"[MQDRC]\w*\s", ln) and "_INT" in ln:
            model = re.search(r"(\w+_INT)", ln).group(1)
            mult = re.search(r"\b[mM]=\{?([^}\s]+)\}?", ln)
            return {"line": ln, "model": model, "m": mult.group(1) if mult else None}
    return None


def geom_values(card):
    vals, moved = {}, []
    for ln in card["lines"]:
        m = re.match(r"\+\s*(\w+)\s*=\s*(.*)$", ln)
        if m and m.group(1).lower() in GEOM_PARAMS:
            if "_is" in m.group(2):
                moved.append(m.group(1))
            else:
                vals[m.group(1)] = m.group(2).strip()
    return vals, moved


def card_value(card, name):
    for ln in card["lines"]:
        m = re.match(r"\+\s*%s\s*=\s*(.*)$" % name, ln)
        if m:
            return m.group(1).strip()
    return None


def family(card, rated):
    t = card["type"]
    if t in ("NMOS", "PMOS"):
        v = rated[1] if rated else None
        return ("LV FET" if v is not None and v <= LV_FET_MAX_V else "HV FET"), "BSIM3 (level 49)"
    return {"VDMOS": ("VDMOS/LDMOS", "VDMOS"), "NPN": ("BJT", "Gummel-Poon NPN"),
            "PNP": ("BJT", "Gummel-Poon PNP"), "D": ("diode", "diode"),
            "R": ("resistor", "semiconductor R"), "C": ("capacitor", "semiconductor C")}[t]


def fmt_term(name, expr, fam, bp):
    m = AGAUSS.search(expr)
    if not m:
        return None
    coef, n = float(m.group(1)), int(m.group(3))
    scale = m.group(2) or m.group(4) or "1"
    if name == "DVTH_MM" and fam == "VDMOS/LDMOS":
        unit, k = "mV per √cell (W_REF=%s)" % bp.get("W_REF", "?"), 1e3
    elif name == "DVTH_MM":
        unit, k = "mV·µm", 1e3
    elif name == "AREAEFF":
        unit, k = "%·√AREA", 1e2
    else:
        unit, k = "%·µm", 1e2
    return {"name": name, "coef": coef, "n": n, "sigma1": coef / n, "scale": scale,
            "text": "%s: %.4g %s at %dσ (1σ %.4g) ÷ √(%s)" % (
                TERM_LABEL.get(name, name), coef * k, unit, n, coef / n * k, scale)}


def build():
    devs, header = parse_lib()
    cards = parse_models()
    rated = parse_limits()
    inc_text = INC.read_text(encoding="utf-8")
    lib_text = LIB.read_text(encoding="utf-8")

    rows, fam_count, misfits = [], {}, []
    agauss_n = {}
    for d in devs:
        bp = body_params(d["body"])
        dev = inner_device(d["body"])
        card = cards[dev["model"]]
        fam, model = family(card, rated.get(d["name"]))
        fam_count[fam] = fam_count.get(fam, 0) + 1
        terms = [t for t in (fmt_term(k, v, fam, bp) for k, v in bp.items() if "AGAUSS" in v) if t]
        for t in terms:
            agauss_n[t["n"]] = agauss_n.get(t["n"], 0) + 1
        area = ("`AUM2=%s`" % bp["AUM2"] if "AUM2" in bp else
                "`mtot=%s`" % bp["mtot"] if "mtot" in bp else
                "`AREA`" if "AREA" in d["params"] else "–")
        mm_sigma = any("MM_SIGMA*" in bp.get(t["name"], "") for t in terms)
        notes = []
        if model.startswith("BSIM3"):
            if "AUM2" in bp and "M" not in re.findall(r"\b\w+\b", bp["AUM2"]):
                notes.append("`AUM2` omits `M` (defect)")
                misfits.append((d["name"], "`AUM2` omits `M`: an `M`-copy array gets single-copy mismatch"))
            if "*0.5u" in dev["line"]:
                notes.append("AD/AS/PD/PS hardcode 0.5 µm")
            gv, moved = geom_values(card)
            if gv:
                notes.append("fixed " + ", ".join("%s=%s" % kv for kv in gv.items()))
            if moved:
                notes.append("corner-moved geometry: " + ", ".join(moved))
        if "M" not in d["params"]:
            notes.append("no `M` instance parameter")
            if fam in ("resistor", "capacitor"):
                misfits.append((d["name"], "no `M` instance parameter (R1 adds one)"))
        if fam == "VDMOS/LDMOS":
            notes.append("ngspice VDMOS has no W/L/AD/AS; size via `m=%s`" % dev["m"])
            misfits.append((d["name"], "VDMOS: no per-finger geometry, `NF` has no lever (D2)"))
        if fam == "capacitor":
            cjsw = card_value(card, "cjsw")
            if cjsw == "0":
                notes.append("`cjsw=0`: no perimeter term")
                misfits.append((d["name"], "`cjsw=0` and no `narrow`/`short`: per-copy edge bias (R0/R3) has no lever"))
            else:
                notes.append("perimeter term via `cjsw`; card has no `narrow`/`short`")
                misfits.append((d["name"], "perimeter via `cjsw` only; no `narrow`/`short`, and D3 declares DL/DW for MOS and R only"))
        if fam == "resistor":
            gv, _ = geom_values(card)
            notes.append("TT edge bias %s; no head resistance" %
                         ", ".join("%s=%s" % kv for kv in gv.items()))
        rv = rated.get(d["name"])
        rows.append({
            "name": d["name"], "family": fam, "model": model,
            "rated": "%s %g V" % (rv[0], rv[1]) if rv else "–",
            "params": " ".join("%s=%s" % kv for kv in d["params"].items()),
            "has_M": "M" in d["params"],
            "terms": "<br>".join(t["text"] for t in terms) or "none",
            "area": area, "mm_sigma": "yes" if mm_sigma else "no",
            "work": WORK[fam][0], "knobs": WORK[fam][1],
            "notes": "; ".join(notes) or "–",
        })

    # global findings
    corner_re = re.compile(r"(\w+)\s*=\s*\{[(\s]*" + r"\s*\+\s*".join(
        r"[-+]?[\d.]+(?:[eE][-+]?\d+)?\*_is" + c for c in ("TT", "FF", "SS", "FS", "SF")))
    corner_inc = [m.group(1) for m in corner_re.finditer(inc_text)]
    corner_lib = [m.group(1) for m in corner_re.finditer(lib_text)]
    geom_moved = [p for p in corner_inc + corner_lib if p.lower() in GEOM_PARAMS]
    header_claim = re.search(r"All (\d+) \.SUBCKT", "\n".join(header))
    rgate = re.search(r"\b(rgate|rsh_poly|rgeomod)\b", lib_text + inc_text, re.I)
    beta = [r["name"] for r in rows if re.search(r"BETA|U0", r["terms"], re.I)]
    findings = [
        ("device wrappers in the library", "%d" % len(devs)),
        ("library header claims", header_claim.group(1) if header_claim else "no count"),
        ("corner-selected expressions `(tt*_isTT + ... + sf*_isSF)`",
         "%d (%d in the models file, %d in the library)"
         % (len(corner_inc) + len(corner_lib), len(corner_inc), len(corner_lib))),
        ("of those, geometry parameters (%s) — brief R0 prerequisite" % "/".join(GEOM_PARAMS),
         "%d — no corner moves geometry; edge bias is declared per D3" % len(geom_moved)
         if not geom_moved else "%d" % len(geom_moved)),
        ("gate-resistance term (`rgate`/`rsh_poly`/`rgeomod`) in wrappers or cards",
         "present" if rgate else "absent — R2 gate-R bullet dropped, listed as follow-up"),
        ("β/mobility mismatch term in any wrapper", ", ".join(beta) if beta else "absent (D6: deferred)"),
        ("AGAUSS sigma convention across mismatch terms",
         ", ".join("%d terms at n=%d" % (c, n) for n, c in sorted(agauss_n.items()))),
    ]
    return rows, fam_count, findings, misfits


def render():
    rows, fam_count, findings, misfits = build()
    L = ["# Statistical model inventory",
         "",
         "<!-- Generated by tools/stat_model_inventory.py -- do not edit by hand. -->",
         "",
         "Work list for the MC realism program, Phases 1–2: one row per device wrapper in",
         "`autohv_bicmos180_case.lib`, read against `autohv_bicmos180_case_models.inc` and",
         "`pdk_validation/device_limits.csv`. Program references:",
         "`docs/backlog/HANDOFF_mc_realism_brief.md` as amended by",
         "`docs/backlog/HANDOFF_mc_realism_rulings.md`.",
         "",
         "FET family is set by the `device_limits` rated `Vds_dcmax` (LV at or below %g V),"
         % LV_FET_MAX_V,
         "not by device name. Coefficients are quoted as written in the wrapper (the AGAUSS",
         "second argument over its third) and as the resulting 1σ.",
         "",
         "Regenerate with `python tools/stat_model_inventory.py`; `--check` fails if stale.",
         "",
         "## Summary",
         "",
         "| family | wrappers |",
         "|---|---|"]
    for fam in ("LV FET", "HV FET", "VDMOS/LDMOS", "BJT", "diode", "resistor", "capacitor"):
        L.append("| %s | %d |" % (fam, fam_count.get(fam, 0)))
    L += ["| **total** | **%d** |" % sum(fam_count.values()), "",
          "## Global findings", "", "| check | result |", "|---|---|"]
    L += ["| %s | %s |" % f for f in findings]
    L += ["", "## Wrappers that do not fit the R1/R2 pattern", "",
          "| device | issue |", "|---|---|"]
    L += ["| %s | %s |" % m for m in misfits]
    L += ["", "## Device table", "",
          "| device | family | model | rated | instance params | mismatch terms | area term | "
          "`MM_SIGMA` path | Phase 1 (`M`/`NF`/`NS`) | Phase 2 knobs | notes |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append("| %(name)s | %(family)s | %(model)s | %(rated)s | `%(params)s` | %(terms)s | "
                 "%(area)s | %(mm_sigma)s | %(work)s | %(knobs)s | %(notes)s |" % r)
    L += ["", "## Follow-ups outside this program", "",
          "- Gate-resistance term for fingered MOS (R2): no term exists to scale with `NF`.",
          "- Pelgrom A_β mismatch term (D6): a value change that needs grounding.",
          "- σ grounding for `PROC_Z_DL` / `PROC_Z_DW` (D3): declared with σ = 0.",
          ""]
    return "\n".join(L)


if __name__ == "__main__":
    text = render()
    if "--check" in sys.argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print("stale: %s differs from generator output" % OUT.relative_to(ROOT))
            sys.exit(1)
        print("ok: %s is current" % OUT.relative_to(ROOT))
    else:
        OUT.write_text(text, encoding="utf-8", newline="\n")
        print("wrote %s" % OUT.relative_to(ROOT))
