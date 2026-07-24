#!/usr/bin/env python3
"""
D1 -- which saturation-current convention does ngspice's VDMOS `kp` use?

QUESTION
    Is VDMOS saturation current  Id = kp*Vov^2  or  Id = (kp/2)*Vov^2 ?
    A factor of two that rescales every kp target in docs/anchor-values.json.

METHOD
    An isolation copy of NDMOS200_INT with rd/rs/rq forced to R_ZERO, so the
    measured current is pure channel and no series drop can masquerade as a
    smaller prefactor. Nothing else is touched -- ksubthres in particular is
    left alone, and the bias points sit 1-3 V into strong inversion where the
    subthreshold term contributes nothing.

    Bias at Vov in {1, 2, 3} V at Vds = 10 V (well past Vdsat = Vov, so the
    device is saturated at every point). Two prefactors are reported per point:

      A_naive = Id / Vov^2
      A_corr  = Id * (1 + theta*Vov) / (Vov^2 * (1 + lambda*Vds))

    A_corr is the one to read. lambda and theta both perturb a raw Id/Vov^2 fit,
    and rather than suppress them by biasing at small Vov -- which would trade a
    known, card-stated perturbation for an unknown subthreshold contamination --
    they are DIVIDED OUT ANALYTICALLY using the card's own theta and lambda,
    read back from ngspice rather than assumed. The size of each correction is
    reported per point so the reader can see it is small (theta*Vov <= 5.4%,
    lambda*Vds = 1.2% on this card) and that the verdict does not rest on it:
    A_naive and A_corr must land on the same side of the kp / kp-over-2 fork,
    and the payload states whether they do.

    The fitted prefactor is a least-squares fit of Id against Vov^2 THROUGH THE
    ORIGIN (the correct form -- Id = A*Vov^2 has no constant term), on the
    theta/lambda-corrected currents.

RUN
    python run.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import exp_lib as E                                                # noqa: E402

SUBDIR = "d1_kp_convention"
DEV = "NDMOS200"
VOV_LIST = [1.0, 2.0, 3.0]
VDS = 10.0


def run() -> dict:
    out: dict = {
        "experiment": "D1",
        "question": ("Is ngspice VDMOS saturation current kp*Vov^2 or "
                     "(kp/2)*Vov^2?"),
        "provenance": E.provenance(),
    }

    # -- control: the raw-instance wiring must reproduce the wrapper ---------
    out["wrapper_equivalence_check"] = E.wrapper_equivalence_check(DEV, SUBDIR)

    # -- stock and isolation cards, both read back from ngspice --------------
    dut_stock = E.stock(DEV)
    card_stock, deck_stock = E.read_card(dut_stock, SUBDIR)

    dut = E.DUT(DEV, "d1", rd=E.R_ZERO, rs=E.R_ZERO, rq=E.R_ZERO)
    card, deck_iso = E.read_card(dut, SUBDIR)

    out["dut"] = dut.as_dict()
    out["cards"] = {
        "stock": {"values": card_stock, "deck": deck_stock},
        "isolated": {"values": card, "deck": deck_iso},
        "delta_took_effect": bool(card["rd"] < 1e-6 and card["rs"] < 1e-6
                                  and card_stock["rd"] > 1e-3),
        "note": ("Both cards are read back through ngspice's @<MODEL>[param] "
                 "accessors, so the rd/rs edit is PROVEN to have landed. This "
                 "matters: see exp_lib's docstring -- an isolation copy that "
                 "reuses the PDK model name is silently ignored by ngspice-45, "
                 "and the experiment would have run on stock cards."),
    }

    kp, vto = card["kp"], card["vto"]
    theta, lam = card["theta"], card["lambda"]
    p = E.pol(DEV)

    # -- the measurement ----------------------------------------------------
    pts: list[dict] = []
    for vov in VOV_LIST:
        nm = f"{DEV}_d1_vov{vov:g}"
        idd, dp = E.id_at(dut, vto, vov, VDS, SUBDIR, nm)
        theta_corr = 1.0 + theta * vov
        lam_corr = 1.0 + lam * VDS
        pts.append({
            "vov_V": vov, "vgs_V": vto + p * vov, "vds_V": p * VDS,
            "id_A": idd,
            "A_naive": idd / vov ** 2,
            "A_corr": idd * theta_corr / (vov ** 2 * lam_corr),
            "theta_correction_pct": (theta_corr - 1.0) * 100.0,
            "lambda_correction_pct": (lam_corr - 1.0) * 100.0,
            "deck": dp,
        })
    out["bias_points"] = pts

    # -- fit A in Id = A*Vov^2, through the origin --------------------------
    def fit_through_origin(xs, ys):
        sxx = sum(x * x for x in xs)
        return sum(x * y for x, y in zip(xs, ys)) / sxx if sxx else float("nan")

    x2 = [q["vov_V"] ** 2 for q in pts]
    id_corr = [q["A_corr"] * q["vov_V"] ** 2 for q in pts]
    a_fit = fit_through_origin(x2, id_corr)
    a_fit_naive = fit_through_origin(x2, [q["id_A"] for q in pts])

    resid = [abs(a_fit * x - y) / y for x, y in zip(x2, id_corr) if y]
    out["fit"] = {
        "form": "Id = A * Vov^2, least squares through the origin",
        "A_fitted_corrected": a_fit,
        "A_fitted_uncorrected": a_fit_naive,
        "max_relative_residual_corrected": max(resid) if resid else None,
        "kp_from_card": kp,
        "kp_over_2": kp / 2.0,
        "ratio_A_over_kp": a_fit / kp,
        "ratio_A_over_kp_uncorrected": a_fit_naive / kp,
        "pointwise_A_corr": [q["A_corr"] for q in pts],
        "pointwise_A_corr_spread_pct": (
            (max(q["A_corr"] for q in pts) / min(q["A_corr"] for q in pts) - 1)
            * 100.0),
    }

    r = a_fit / kp
    verdict = "kp" if abs(r - 1.0) < abs(r - 0.5) else "kp/2"
    agree = ((a_fit_naive / kp > 0.75) == (r > 0.75))
    out["verdict"] = {
        "convention": verdict,
        "one_word": verdict,
        "measured_ratio_A_over_kp": r,
        "statement": (
            f"ngspice-45 VDMOS saturation current is Id = ({verdict})*Vov^2. "
            f"The fitted prefactor is {a_fit:.6g} A/V^2 against a card kp of "
            f"{kp:.6g}, a ratio of {r:.4f} -- "
            + ("indistinguishable from 1/2, so the model carries the standard "
               "SPICE factor-of-two internally and kp is a TRANSCONDUCTANCE "
               "PARAMETER, not the saturation prefactor."
               if verdict == "kp/2" else
               "indistinguishable from 1, so kp IS the saturation prefactor "
               "directly and there is no internal factor of two.")),
        "corrected_and_uncorrected_agree": agree,
        "robustness": (
            f"The uncorrected fit gives A/kp = {a_fit_naive/kp:.4f} and the "
            f"theta/lambda-corrected fit {r:.4f}. "
            + ("Both land on the same side of the fork, so the verdict does "
               "not depend on the correction -- the two candidates are a "
               "factor of two apart and the corrections are single-digit "
               "percent."
               if agree else
               "THESE DISAGREE, which should be impossible for a 2x fork with "
               "single-digit-percent corrections. Treat the verdict as unsafe "
               "and investigate before using it.")),
    }

    # -- what this means for the anchor -------------------------------------
    anchor_kp_n = 0.000767      # _vdmos_kp_conditional.decision_A.kp_n.target
    anchor_kp_idsat = 0.00025   # .kp_from_idsat_density.target
    out["consequence_for_anchor"] = {
        "anchor_path": ("docs/anchor-values.json  ->  _vdmos_kp_conditional  "
                        "->  decision_A_10um_cell"),
        "kp_n_target": anchor_kp_n,
        "kp_p_target": 0.000249,
        "kp_from_idsat_density_target": anchor_kp_idsat,
        "kp_n_basis_as_written": "mu_n*Cox*(W/L_ch), mu_n=400 cm2/Vs, W/L=10/0.6",
        "kp_from_idsat_basis_as_written": "kp = 2*Id/Vov^2",
        "ruling": (
            "NO RESCALE IS NEEDED. Both anchor routes already assume the "
            "kp/2 convention that D1 measures, and they are consistent with "
            "each other and with the model.\n"
            "  (a) The mu*Cox*(W/L) route. The anchor derives kp_n from "
            "mu*Cox*(W/L) with no factor of two. That is exactly the SPICE "
            "level-1 KP definition, in which Id_sat = (KP/2)(W/L)Vov^2 -- the "
            "factor of two lives in the CURRENT equation, not in KP itself. "
            "Since VDMOS folds W/L into kp (it has no W or L), the anchor's "
            "kp = mu*Cox*(W/L) is directly comparable to the card's kp under "
            "the measured Id = (kp/2)Vov^2 form. Consistent. No /2.\n"
            "  (b) The Idsat-density route. The anchor writes its basis as "
            "kp = 2*Id/Vov^2, which is the algebraic inverse of "
            "Id = (kp/2)Vov^2. Also consistent. No /2.\n"
            "So the phase-1 kp targets stand as written, and the F1 gap in "
            "audit 2.1 is NOT a factor-of-two bookkeeping error that would "
            "shrink it -- the 287x-5213x implied-width finding survives D1 "
            "intact. What D1 removes is the possibility that half of that gap "
            "was a convention mistake."
            if verdict == "kp/2" else
            "The anchor's mu*Cox*(W/L) basis is the SPICE level-1 KP "
            "convention, which carries an internal factor of two that the "
            "model does NOT. Every kp target in _vdmos_kp_conditional must be "
            "HALVED before it is compared to a card value."),
        "recommended_amendment": (
            "Add a one-line `convention` field to _vdmos_kp_conditional "
            "recording the measured result -- 'ngspice VDMOS: "
            f"Id_sat = (kp/2)*Vov^2, measured A/kp = {r:.4f} (D1)' -- so the "
            "next reader does not have to re-derive it. No target values "
            "change." if verdict == "kp/2" else
            "Halve kp_n, kp_p and kp_from_idsat_density, and record the "
            "convention explicitly."),
        "maintainer_applies_this": True,
    }
    return out


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
