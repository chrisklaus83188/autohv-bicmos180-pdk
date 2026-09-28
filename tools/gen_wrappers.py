#!/usr/bin/env python3
"""Generate the statistical lines of autohv_bicmos180_case.lib from stat_model.json.

Phase 3. A LINE TRANSFORM over autohv_bicmos180_case.lib.in, the same shape as
tools/gen_models.py over the .inc, and for the same reason: the authored file carries 492
lines of device structure -- thermal networks, avalanche generators, VCR/VCC terms, gmin
shunts -- that no statistical model describes. This tool rewrites only the 130 lines the
model owns and passes everything else through.

  A generator never reads the file it writes. Input is the .in template; the tool refuses
  to run if the input path resolves to the output path.

WHAT IT OWNS
------------
  .subckt signatures        pass through (parameter lists are authored)
  .param AUM2               the area norm
  .param DVTH_MM            MOS / VDMOS threshold mismatch
  .param DWREL_MM/DLREL_MM  MOS edge mismatch
  .param mtot               VDMOS width multiplicity
  .param RMM / CMM          resistor / capacitor mismatch
  .param BVCBO              BJT breakdown (ruling AD1)

  .param AREAEFF is NOT owned yet: the BJT/diode wrappers fold everything into one area
  perturbation, and the brief replaces it with three independent terms (A_VBE, A_BF,
  A_IS). Passed through until that rewrite, rather than half-converted.

TWO CONVENTIONS THIS FIXES
--------------------------
1. `AUM2` omitted `M`. stat_model.json's own `local_mismatch._convention` reads
   "sigma = A / sqrt(W*L*M) for MOS", so the wrapper contradicted the model it was meant
   to implement: device multiplicity did not reduce mismatch sigma at all. This is the
   first bug recorded in this program, and the M=4 mirror test is its acceptance.

2. AGAUSS's third argument is a SIGMA SCALE, not a clip. `AGAUSS(0, X, 3)` means X is the
   3-sigma value, so sigma = X/3 -- it does not truncate the distribution at 3 sigma.
   Every coefficient is now emitted as `AGAUSS(0, <1 sigma>, 1)` so that the number a
   reader sees in the file IS the model's 1-sigma value in foundry units, traceable to a
   named entry in stat_model.json rather than scaled by a factor they have to notice.

    python tools/gen_wrappers.py            # write the .lib
    python tools/gen_wrappers.py --check    # regenerate to memory, byte-compare, exit 1
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "models" / "stat_model.json"
TEMPLATE = ROOT / "autohv_bicmos180_case.lib.in"
LIB = ROOT / "autohv_bicmos180_case.lib"

GUARD = "+1e-12"          # keeps sqrt() finite when a geometry is zero
VDMOS_GUARD = "1e-6"


def fmt(x: float) -> str:
    """Six significant figures, no exponent games -- these land in a SPICE file."""
    return "%.6g" % x


def load() -> dict:
    return json.loads(MODEL.read_text(encoding="utf-8"))["local_mismatch"]


def mos_lines(dev: str, lm: dict) -> dict[str, str]:
    """AUM2 + the three MOS mismatch params, from this device's named coefficients."""
    d = lm[dev]
    a_vt = d["A_VT"]["value"] / 1000.0        # mV.um -> V.um
    a_w = d["A_W"]["value"] / 100.0           # %.um  -> relative.um
    a_l = d["A_L"]["value"] / 100.0
    out = {
        # M belongs here: see the module docstring, rule 1.
        "AUM2": ".param AUM2={(W/1u)*(L/1u)*M}",
    }
    for name, coef in (("DVTH_MM", a_vt), ("DWREL_MM", a_w), ("DLREL_MM", a_l)):
        out[name] = (".param %s={MM_ON*AGAUSS(0, %s/sqrt(AUM2%s), 1)"
                     " + MM_SIGMA*%s/sqrt(AUM2%s)}"
                     % (name, fmt(coef), GUARD, fmt(coef), GUARD))
    return out


def vdmos_lines(dev: str, lm: dict) -> dict[str, str]:
    """VDMOS is WIDTH-normalised, not area-normalised.

    The ladder is quoted as 3 sigma at the W_REF = 10 um reference cell and the model says
    in as many words that it must not be converted into a Pelgrom area coefficient. So the
    divisor is sqrt(mtot) with mtot = (W/W_REF)*M, and only the 3->1 sigma restatement
    changes here.
    """
    three = lm["_VDMOS"]["A_VT"]["ladder"][dev]
    one = three / 3.0
    return {
        "mtot": ".param mtot={(W/W_REF)*M}",
        "DVTH_MM": (".param DVTH_MM={MM_ON*AGAUSS(0, %s, 1)/sqrt(max(mtot,%s))"
                    " + MM_SIGMA*%s/sqrt(max(mtot,%s))}"
                    % (fmt(one), VDMOS_GUARD, fmt(one), VDMOS_GUARD)),
    }


def res_lines(dev: str, lm: dict) -> dict[str, str]:
    one = lm["_RESISTORS"]["lumped_today_1sigma_pct_um"][dev] / 100.0
    return {
        "AUM2": ".param AUM2={(L/1u)*(W/1u)}",
        "RMM": (".param RMM={1+MM_ON*AGAUSS(0, %s/sqrt(AUM2%s), 1)"
                " + MM_SIGMA*%s/sqrt(AUM2%s)}"
                % (fmt(one), GUARD, fmt(one), GUARD)),
    }


def cap_lines(dev: str, lm: dict) -> dict[str, str]:
    one = lm["_CAPACITORS"]["A_C"][dev] / 100.0
    return {
        "AUM2": ".param AUM2={(L/1u)*(W/1u)}",
        "CMM": (".param CMM={1+MM_ON*AGAUSS(0, %s/sqrt(AUM2%s), 1)"
                " + MM_SIGMA*%s/sqrt(AUM2%s)}"
                % (fmt(one), GUARD, fmt(one), GUARD)),
    }


def bjt_lines(dev: str, gv: dict) -> dict[str, str]:
    """BVCBO: TT in volts from the _BV_template wrapper target, sigma from the template."""
    t = gv["_BV_template"]
    entry = next(a for a in t["applies_to"] if a.get("target") == "wrapper_BVCBO")
    tt = entry["tt_V"][dev]
    return {"BVCBO": ".param BVCBO={%s*exp(%s*Z_BV_%s)}"
                     % (fmt(tt), fmt(t["sigma"]), dev)}


def generate() -> str:
    if TEMPLATE.resolve() == LIB.resolve():
        raise SystemExit("gen_wrappers: template and output are the same file; a generator "
                         "must never read the file it writes")
    model = json.loads(MODEL.read_text(encoding="utf-8"))
    lm, gv = model["local_mismatch"], model["global_variables"]

    MOS = [d for d in lm if isinstance(lm[d], dict) and "A_VT" in lm[d] and "A_W" in lm[d]]
    VDMOS = list(lm["_VDMOS"]["A_VT"]["ladder"])
    RES = list(lm["_RESISTORS"]["lumped_today_1sigma_pct_um"])
    CAP = list(lm["_CAPACITORS"]["A_C"])
    BJT = list(next(a for a in gv["_BV_template"]["applies_to"]
                    if a.get("target") == "wrapper_BVCBO")["tt_V"])

    out, dev, repl = [], None, {}
    for line in TEMPLATE.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\.subckt (\S+) ", line)
        if m:
            dev = m.group(1)
            if dev in MOS:
                repl = mos_lines(dev, lm)
            elif dev in VDMOS:
                repl = vdmos_lines(dev, lm)
            elif dev in RES:
                repl = res_lines(dev, lm)
            elif dev in CAP:
                repl = cap_lines(dev, lm)
            elif dev in BJT:
                repl = bjt_lines(dev, gv)
            else:
                repl = {}
            out.append(line)
            continue
        p = re.match(r"\.param (\w+)=", line)
        if p and p.group(1) in repl:
            out.append(repl[p.group(1)])
            continue
        out.append(line)
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="regenerate and byte-compare; exit 1 on drift")
    args = ap.parse_args(argv)

    text = generate()
    if args.check:
        if LIB.read_text(encoding="utf-8") != text:
            print("stale: %s differs from the generator output" % LIB.name)
            return 1
        print("ok: %s is current" % LIB.name)
        return 0
    LIB.write_text(text, encoding="utf-8", newline="\n")
    print("wrote %s" % LIB.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
