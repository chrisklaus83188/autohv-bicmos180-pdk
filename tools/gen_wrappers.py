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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inc_parse import IncParseError, tt_of  # noqa: E402

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


# Lateral diffusion / contacted-stripe length used for the junction geometry. Authored, not
# statistical: it is a layout constant, and the previous wrappers hardcoded the same 0.5 um.
LD = "0.5u"


def mos_wrapper(dev: str, w_def: str, l_def: str, lm: dict, gv: dict) -> list[str]:
    """The whole BSIM3 wrapper body. Phase 3b, with ruling Q1 for the finger geometry.

    KNOBS. Four independent deterministic n-sigma dials replace the single MM_SIGMA, which
    moved Vth, W and L together -- a scenario no process produces, since the three are
    independent. MM_SIGMA=X is exactly Z_VT=X Z_W=X Z_L=X, which is how the 118 callers
    migrate; Z_BETA is new and had no MM_SIGMA equivalent.

    BETA. Driven through the BSIM3 instance parameter `mulu0` (verified: ngspice accepts it
    and it moves Id). Id does not move by the full 1+DBETA in saturation -- velocity
    saturation and series resistance absorb part of it -- which is correct physics, not a
    scaling error.

    EDGE BIAS. Z_DW_ACT_* and Z_DL_POLY were declared with live corner values and consumed by
    NOTHING: their applies_to says `additive-in-wrapper`, and no wrapper existed to honour it.
    Same class of defect as VBE/VF before Finding A. The sign and scale must match how the
    harness measured the direction -- it perturbs lint/wint with scale=-0.5, and dL=-2*dlint,
    so a +1 sigma draw means L LONGER by +sigma metres. Hence `+ sigma*Z`, additive in metres.

    GATE RESISTOR. RSH_GATE * (W/NF) / (3*L*NF): the 1/3 is the distributed-gate result for a
    single-side-fed poly finger. It is a series element on the gate, so DC is untouched (no
    gate current) and only AC/transient see it -- which is the point of adding it.

    FINGER GEOMETRY (ruling Q1). NF fingers sit on NF+1 diffusion stripes, drain and source
    taking half each, and ngspice multiplies the per-finger value by m = NF*M:

        AD = AS = (W/NF)*LD*(NF+1)/(2*NF)

    exact at NF=1, and totalling 1.5 and 2.5 stripe-areas at NF=2 and NF=4.

    PD/PS are the FIELD-OXIDE sidewall perimeter only: BSIM3 handles the gate-side sidewall
    through cjswg, so the gate-facing edge is excluded (ruling Q1). An end stripe exposes
    three sides (W_f + 2*LD); an interior stripe, sharing both long sides with gates, exposes
    only its two short sides (2*LD):

        PD = PS = [2*(W_f + 2*LD) + (NF-1)*2*LD] / (2*NF)

    At NF=1 this is W_f + 2*LD. The previous wrapper used 2*(W_f + LD), i.e. it counted BOTH
    long edges, so it double-counted the gate-facing sidewall. Sidewall junction capacitance
    therefore drops by about one W_f of perimeter per finger -- a real, intended change.
    """
    d = lm[dev]
    s_vt = d["A_VT"]["value"] / 1000.0        # mV.um -> V.um
    s_be = d["A_BETA"]["value"] / 100.0       # %.um  -> relative.um
    s_w = d["A_W"]["value"] / 100.0
    s_l = d["A_L"]["value"] / 100.0

    dw_var = "DW_ACT_LV" if dev in gv["DW_ACT_LV"]["shared_by"] else "DW_ACT_HV"
    s_dw = gv[dw_var]["sigma"]
    s_dl = gv["DL_POLY"]["sigma"]
    rg_nom, rg_sig = gv["RSH_GATE"]["nominal"], gv["RSH_GATE"]["sigma"]

    def mm(name, coef, knob):
        return (".param %s={MM_ON*AGAUSS(0, %s/sqrt(AUM2%s), 1) + %s*%s/sqrt(AUM2%s)}"
                % (name, fmt(coef), GUARD, knob, fmt(coef), GUARD))

    return [
        ".subckt %s d g s b params: W=%s L=%s M=1 NF=1 Z_VT=0 Z_BETA=0 Z_W=0 Z_L=0"
        % (dev, w_def, l_def),
        "* Phase 3b. Coefficients are 1 sigma in foundry units, from local_mismatch.%s" % dev,
        "* in models/stat_model.json. AGAUSS's third argument is a sigma SCALE, not a clip.",
        ".param AUM2={(W/1u)*(L/1u)*M}",
        mm("DVTH_MM", s_vt, "Z_VT"),
        mm("DBETA_MM", s_be, "Z_BETA"),
        mm("DWREL_MM", s_w, "Z_W"),
        mm("DLREL_MM", s_l, "Z_L"),
        "* Global edge bias, additive in metres: +1 sigma means WIDER/LONGER, matching how",
        "* measure_stat_directions perturbs lint/wint (scale=-0.5, dL=-2*dlint).",
        ".param WEFF={W*(1+DWREL_MM) + %s*Z_%s}" % (fmt(s_dw), dw_var),
        ".param LEFF={L*(1+DLREL_MM) + %s*Z_DL_POLY}" % fmt(s_dl),
        ".param WF={WEFF/NF}",
        ".param LD=%s" % LD,
        "* Ruling Q1: shared stripes; PD excludes the gate-facing sidewall (BSIM3 cjswg).",
        ".param ADF={WF*LD*(NF+1)/(2*NF)}",
        ".param PDF={(2*(WF+2*LD) + (NF-1)*2*LD)/(2*NF)}",
        ".param RG={%s*exp(%s*Z_RSH_GATE)*WF/(3*LEFF*NF)}" % (fmt(rg_nom), fmt(rg_sig)),
        "M0 d gi s b %s_INT W={WF} L={LEFF} m={NF*M} delvto={DVTH_MM} mulu0={1+DBETA_MM}"
        " AD={ADF} AS={ADF} PD={PDF} PS={PDF}" % dev,
        "RGATE g gi {RG}",
        ".ends %s" % dev,
    ]


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
        # MM_SIGMA drove this single term only, so Z_VT is an exact one-for-one
        # replacement -- unlike the MOS case, where one dial moved three terms.
        "DVTH_MM": (".param DVTH_MM={MM_ON*AGAUSS(0, %s, 1)/sqrt(max(mtot,%s))"
                    " + Z_VT*%s/sqrt(max(mtot,%s))}"
                    % (fmt(one), VDMOS_GUARD, fmt(one), VDMOS_GUARD)),
    }


INC_TEMPLATE = ROOT / "autohv_bicmos180_case_models.inc.in"


def edge_corrections() -> dict:
    """{card: {narrow, short}} from the MODEL CARD template -- read, never typed.

    The ngspice semiconductor-R model computes its own effective geometry as L-short and
    W-narrow. Any wrapper arithmetic on L or W must be done on the EFFECTIVE value and
    converted back, or it lands on the wrong lever:

      * M parallel copies: widening the drawn strip to M*W lets the model subtract `narrow`
        ONCE where M strips each lose it, overstating width by (M-1)*narrow -- measured as a
        0.6 % error at M=2.
      * a relative perturbation on the drawn L scales (L*RMM - short) instead of
        RMM*(L - short), so the realised sigma is out by L/(L-short) -- about 1 % at
        L = 10 um, which would have made acceptance B5 miss by that much.

    MEASURED, not assumed: the model applies BOTH corrections on BOTH edges, so the
    effective geometry is L-2*short and W-2*narrow. An L/W sweep on the bare card
    gives offsets of 2.031e-07 and 2.433e-07 against card values of 1e-07 and
    1.2e-07. Using 1x left acceptance B5 about 1 % short, which is how this was
    caught.
    """
    out = {}
    card = None
    for line in INC_TEMPLATE.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\.model\s+(\S+)\s", line, re.I)
        if m:
            card = m.group(1)
            continue
        q = re.match(r"\+\s*(narrow|short)\s*=\s*(.+?)\s*$", line, re.I)
        if q and card:
            try:
                out.setdefault(card, {})[q.group(1).lower()] = tt_of(q.group(2))
            except IncParseError as exc:
                raise SystemExit("gen_wrappers: %s.%s: %s" % (card, q.group(1), exc))
    return out


def res_wrapper(dev: str, l_def: str, w_def: str, keep: list[str], lm: dict,
                gv: dict) -> list[str]:
    """NS-segmented resistor with contact heads (ruling Q2, brief 5.3).

    NOMINAL.  R = [ RSH*L/W_eff + NS*2*R_HEAD ] / M

    The sheet part is NS-INDEPENDENT: NS segments of length L/NS in series carry the same
    sheet resistance as one of length L. What NS buys is contact heads -- two per segment --
    so the head term grows linearly with NS. M parallel copies divide the whole thing, which
    the sheet element gets for free by widening to W_eff*M (M strips of width W_eff are one
    strip of width M*W_eff at the same sheet resistance).

    `rsh` is already statistical on the card, so the global sheet variation arrives through
    the model and must NOT be re-applied here. The wrapper's old RSH0 param was dead code
    duplicating that nominal, free to drift from it; it is gone.

    LOCAL SIGMA.  Four terms, from the ruled 64/16/10/10 variance shares:

        sigma_rel = sqrt( A_RSH^2 + A_W^2 + NS*(A_LEND^2 + SIG_HEAD^2) ) / sqrt(W*L*M)

    Sheet and width are area-law and so NS-independent; end and head grow as sqrt(NS) because
    each segment contributes its own. At the W=L=10 um, NS=1, M=1 reference this reproduces
    today's lumped sigma exactly, which is acceptance B5.

    RMM scales BOTH the sheet element and the head element, so it perturbs the total
    resistance rather than only the body -- applying it to L alone would leave the head term
    unperturbed and make the realised sigma fall short of the model's.

    EDGE BIAS.  Poly resistors take DL_POLY on their WIDTH (applies_to: poly_resistor_W).
    Sign matches the harness, which perturbs `narrow` at scale=-1.0, and narrow reduces
    effective width -- so +1 sigma means WIDER by +sigma metres. The diffusion and well types
    carry no poly edge, so they get no width bias.
    """
    ec = edge_corrections().get(dev + "_INT", {})
    one = {k: lm["_RESISTORS"][k]["per_type"][dev]
           for k in ("A_RSH", "A_W", "A_LEND", "SIG_HEAD")}
    # %.um -> relative.um
    a_rsh, a_w = one["A_RSH"] / 100.0, one["A_W"] / 100.0
    a_end, a_hd = one["A_LEND"] / 100.0, one["SIG_HEAD"] / 100.0
    rh = gv["_RHEAD_template"]
    poly = dev in ("RPOLY_HI", "RPOLY_LO")

    body = [
        ".subckt %s p n params: L=%s W=%s NS=1 M=1 Z_R=0" % (dev, l_def, w_def),
    ]
    # authored type comments, carried through with the marker prefix stripped
    body += ["* " + c[len("*KEEP"):].lstrip() for c in keep if c.startswith("*KEEP ")]
    body += [
        "* Phase 3d. Coefficients are 1 sigma in foundry units from "
        "local_mismatch._RESISTORS.",
        ".param AUM2={(L/1u)*(W/1u)*M}",
        "* sheet and width are area-law; end and head grow as sqrt(NS), one per segment.",
        ".param SR={sqrt(%s + %s + NS*(%s + %s))}"
        % (fmt(a_rsh ** 2), fmt(a_w ** 2), fmt(a_end ** 2), fmt(a_hd ** 2)),
        ".param RMM={1 + MM_ON*AGAUSS(0, SR/sqrt(AUM2%s), 1) + Z_R*SR/sqrt(AUM2%s)}"
        % (GUARD, GUARD),
    ]
    if poly:
        body.append(".param WEFF={W + %s*Z_DL_POLY}" % fmt(gv["DL_POLY"]["sigma"]))
    else:
        body.append(".param WEFF={W}")
    body += [
        ".param RHEAD={%s*exp(%s*Z_RHEAD_%s)}" % (fmt(rh["nominal"]), fmt(rh["sigma"]), dev),
    ]
    # the authored VCR coefficients, verbatim
    body += [k[len("*KEEPLINE "):] for k in keep
             if k.startswith("*KEEPLINE ") and ".param VCR" in k]
    body += [
        "* Perturb and parallel the EFFECTIVE geometry, then convert back, so the"
        " model's own",
        "* L-short / W-narrow corrections land where they belong (see edge_corrections).",
        ".param SHORT=%s" % fmt(ec.get("short", 0.0)),
        ".param NARROW=%s" % fmt(ec.get("narrow", 0.0)),
        ".param LDRAWN={(L-2*SHORT)*RMM + 2*SHORT}",
        ".param WDRAWN={M*(WEFF-2*NARROW) + 2*NARROW}",
        "R0   p mid %s_INT L={LDRAWN} W={WDRAWN}" % dev,
    ]
    # The authored BVCR source ends on `n`. The contact heads go in series AFTER it, so its
    # far node is re-pointed to the internal `nh`: that keeps V(p,mid) spanning exactly the
    # resistor body, as it did before, while the heads sit at the far end of the chain.
    for k in keep:
        if k.startswith("*KEEPLINE ") and k[len("*KEEPLINE "):].startswith("BVCR"):
            tok = k[len("*KEEPLINE "):].split(None, 3)
            body.append(" ".join([tok[0], tok[1], "nh", tok[3]]))
    body += [
        "* two contact heads per segment, so the head term is the only NS-dependent nominal.",
        "RHD  nh n {NS*2*RHEAD*RMM/M}",
        ".ends %s" % dev,
    ]
    return body


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
    pending_res, keep = None, []
    for line in TEMPLATE.read_text(encoding="utf-8").splitlines():
        mk = re.match(r"\* <<<MOS_WRAPPER (\S+) W=(\S+) L=(\S+)>>>", line)
        if mk:
            out.extend(mos_wrapper(mk.group(1), mk.group(2), mk.group(3), lm, gv))
            continue
        rk = re.match(r"\* <<<RES_WRAPPER (\S+) L=(\S+) W=(\S+)>>>", line)
        if rk:
            pending_res = (rk.group(1), rk.group(2), rk.group(3))
            keep = []
            continue
        if pending_res is not None:
            if line.startswith("*KEEP"):
                keep.append(line)
                continue
            out.extend(res_wrapper(pending_res[0], pending_res[1], pending_res[2],
                                   keep, lm, gv))
            pending_res, keep = None, []
        m = re.match(r"\.subckt (\S+) ", line)
        if m:
            dev = m.group(1)
            if dev in list(lm["_VDMOS"]["A_VT"]["ladder"]):
                line = line.replace("MM_SIGMA=0", "Z_VT=0")
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
