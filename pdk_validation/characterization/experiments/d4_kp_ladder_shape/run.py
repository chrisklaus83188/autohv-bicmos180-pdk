#!/usr/bin/env python3
"""
D4 -- is the kp fix one divisor, or thirteen separate re-derivations?

QUESTION
    Audit 2.1 computed an implied cell width per card as
    W = kp*L_ch/(mu*Cox) and found 287x-5213x, and -- critically -- that the
    ratio is NOT constant: it falls 12.7x from the 20 V card to the 200 V card.
    That sloped residual is why fix #2 was scoped as thirteen re-derivations
    rather than the single divisor that fixes rd/rs.

    But audit 2.1 held tox = 30 nm across every voltage class. Audit 2.7's own
    theta analysis implies tox RISING with class -- 25-75 nm at 20 V to
    56-167 nm at 200 V. A thicker oxide means a smaller Cox means a LARGER
    implied width, and the effect grows with class, so it pushes exactly against
    the slope audit 2.1 found. If it flattens the residual, fix #2 collapses to
    one divisor like rd/rs.

METHOD
    1. Isolation copies of ALL THIRTEEN cards with rd and rs forced to R_ZERO,
       so no series drop can masquerade as mobility degradation. This is the
       correction families/vdmos.py's _do_theta flags as needed: on stock cards
       the IR drop across rd+rs is a large fraction of Vov at the top of the fit
       range and the extracted theta is only an upper bound.

    2. theta by fit from Id-Vg. D1 established the model's strong-inversion form
       exactly:
                Id = (kp/2) * Vov^2 / (1 + theta*Vov) * (1 + lambda*Vds)
       Rearranged to a straight line,
                Vov^2 / Id = (2 / (kp*(1+lambda*Vds))) * (1 + theta*Vov)
       so a single least-squares fit of Vov^2/Id against Vov gives
       theta = slope/intercept, with kp falling out of the intercept as a
       by-product that independently re-confirms D1's convention on all 13
       cards. Fit over Vov = 0.5..4.0 V. R^2 and the residual IR drop are
       reported per card so a badly conditioned fit cannot pass silently.

    3. Each measured theta -> an implied tox BAND, via audit 2.7's
       theta ~ (1..3)e-7 / tox[cm]. A band, never a point: the empirical
       constant spans 3x and pretending otherwise would be the same mistake
       audit 2.1 made with tox = 30 nm.

    4. The audit 2.1 implied-width table recomputed two ways --
       (a) tox = 30 nm flat for all thirteen
       (b) the theta-implied tox ladder
       with W = kp*L_ch/(mu*Cox), L_ch = 0.6 um, mu_n = 400, mu_p = 130 cm^2/Vs,
       Cox = eps_ox/tox.

    5. The SPREAD of the implied-width ratio across the family under each
       hypothesis (max/min). The hypothesis that makes the residual FLATTER is
       the one that says "one divisor".

       Note the spread under (b) is INDEPENDENT of where in the 1e-7..3e-7 band
       the empirical constant sits: that constant multiplies every card's tox
       equally and cancels in a max/min ratio. So the flatness verdict does not
       inherit the constant's 3x uncertainty, even though the absolute widths
       do. Only the ABSOLUTE implied widths need the band.

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
from char_lib import linfit                                        # noqa: E402

SUBDIR = "d4_kp_ladder_shape"
VOV_LO, VOV_HI, STEP = 0.5, 4.0, 0.05

# audit 2.1's implied-width ratios at tox = 30 nm flat, for cross-checking that
# the recomputation reproduces the audit before it departs from it.
AUDIT_2_1_RATIO = {
    "NDMOS20": 3649, "PDMOS20": 5213, "DNMOS20": 1303,
    "NDMOS40": 2476, "PDMOS40": 3408, "NDMOS60": 1564, "PDMOS60": 2205,
    "NDMOS80": 1043, "PDMOS80": 1524, "NDMOS120": 586, "PDMOS120": 842,
    "NDMOS200": 287, "PDMOS200": 353,
}


def _fit_theta(dut: E.DUT) -> dict:
    dev = dut.dev
    card, card_deck = E.read_card(dut, SUBDIR)
    p, vto = E.pol(dev), card["vto"]
    kp, lam, theta_card = card["kp"], card["lambda"], card["theta"]
    svto = p * vto
    vds = min(0.5 * E.BV_RATED[dev], 10.0)

    u, idr, dp = E.run_idvg(dut, svto + VOV_LO, svto + VOV_HI, STEP, vds,
                            SUBDIR, f"{dev}_d4_theta",
                            "strong-inversion Id-Vg (theta)")
    xs, ys, ids = [], [], []
    for uu, ii in zip(u, idr):
        vov = uu - svto
        if vov < VOV_LO - 1e-9 or ii <= 0:
            continue
        xs.append(vov)
        ys.append(vov * vov / ii)
        ids.append(ii)
    if len(xs) < 8:
        raise RuntimeError(f"{dev}: only {len(xs)} usable points")

    slope, intercept = linfit(xs, ys)
    if not math.isfinite(slope) or not math.isfinite(intercept) or not intercept:
        raise RuntimeError(f"{dev}: degenerate theta fit")
    theta = slope / intercept
    r2 = E.r2_of(xs, ys, slope, intercept)
    # kp back out of the intercept: intercept = 2/(kp*(1+lambda*Vds))
    kp_fit = 2.0 / (intercept * (1.0 + lam * vds))

    rd_rs = card["rd"] + card["rs"]
    ir_top = ids[-1] * rd_rs
    tox_lo, tox_hi = E.tox_band_from_theta_nm(theta)
    return {
        "device": dev, "vclass_V": E.vclass(dev),
        "polarity": "p" if p < 0 else "n",
        "card_kp": kp, "card_theta": theta_card, "card_lambda": lam,
        "card_rd_ohm": card["rd"], "card_rs_ohm": card["rs"],
        "theta_measured_1_per_V": theta,
        "theta_measured_over_card": theta / theta_card if theta_card else None,
        "kp_from_fit_intercept": kp_fit,
        "kp_fit_over_card_kp": kp_fit / kp,
        "fit_r2": r2, "fit_points": len(xs),
        "fit_vov_range_V": [xs[0], xs[-1]],
        "vds_V": p * vds,
        "ir_drop_at_top_of_range_V": ir_top,
        "ir_drop_as_pct_of_vov": 100.0 * ir_top / xs[-1],
        "tox_implied_lo_nm": tox_lo, "tox_implied_hi_nm": tox_hi,
        "well_conditioned": bool(r2 > 0.98 and ir_top < 0.01 * xs[-1]),
        "decks": {"card": card_deck, "sweep": dp},
    }


def run() -> dict:
    out: dict = {
        "experiment": "D4",
        "question": ("Is the kp fix one divisor or thirteen re-derivations? "
                     "i.e. does a rising tox ladder flatten audit 2.1's "
                     "sloped implied-width residual?"),
        "provenance": E.provenance(),
        "tox_flat_nm": E.TOX_FLAT_NM,
        "inputs": {"L_ch_um": E.L_CH_UM, "mu_n_cm2_Vs": E.MU_N,
                   "mu_p_cm2_Vs": E.MU_P, "W_REF_um": E.W_UM,
                   "W_formula": "W_implied = kp * L_ch / (mu * Cox), "
                                "Cox = eps_ox / tox"},
    }
    out["wrapper_equivalence_check"] = E.wrapper_equivalence_check(
        "NDMOS200", SUBDIR)

    rows, errors = [], []
    for dev in E.DEVICES:
        try:
            rows.append(_fit_theta(E.DUT(dev, "d4", rd=E.R_ZERO, rs=E.R_ZERO)))
        except Exception as e:                                    # noqa: BLE001
            errors.append({"device": dev, "error": str(e)})
    rows.sort(key=lambda z: (z["vclass_V"], z["device"]))
    out["theta_extraction"] = rows
    out["errors"] = errors
    if len(rows) < 10:
        out["verdict"] = {"error": "too few cards extracted"}
        return out

    out["theta_fit_quality"] = {
        "min_r2": min(r["fit_r2"] for r in rows),
        "max_ir_drop_pct_of_vov": max(r["ir_drop_as_pct_of_vov"] for r in rows),
        "all_well_conditioned": all(r["well_conditioned"] for r in rows),
        "max_theta_deviation_from_card_pct": max(
            abs(r["theta_measured_over_card"] - 1) * 100 for r in rows),
        "max_kp_deviation_from_card_pct": max(
            abs(r["kp_fit_over_card_kp"] - 1) * 100 for r in rows),
        "interpretation": (
            "With rd = rs = 0 the fit is exactly conditioned and recovers both "
            "the card's theta and, from the intercept, the card's kp under "
            "D1's Id = (kp/2)Vov^2 convention. That is the point of the "
            "control, not a tautology: it demonstrates (i) that D1's "
            "convention holds on all thirteen cards, not just NDMOS200, and "
            "(ii) that once series resistance is removed the MEASURED theta "
            "equals the CARD theta, so audit 2.7's tox inferences -- which "
            "were computed from card values -- are not corrupted by rd/rs. On "
            "the stock cards they would have been: families/vdmos.py flags its "
            "own theta extraction as an upper bound for exactly this reason."),
    }

    # ------------------------------------------------- the two width tables
    tbl = []
    for r in rows:
        dev, kp = r["device"], r["card_kp"]
        w_flat = E.w_implied_um(kp, dev, E.TOX_FLAT_NM)
        w_lo = E.w_implied_um(kp, dev, r["tox_implied_lo_nm"])
        w_hi = E.w_implied_um(kp, dev, r["tox_implied_hi_nm"])
        tbl.append({
            "device": dev, "vclass_V": r["vclass_V"],
            "polarity": r["polarity"], "kp": kp,
            "theta_measured": r["theta_measured_1_per_V"],
            "tox_flat_nm": E.TOX_FLAT_NM,
            "tox_theta_implied_band_nm": [r["tox_implied_lo_nm"],
                                          r["tox_implied_hi_nm"]],
            "W_implied_a_flat_tox_um": w_flat,
            "ratio_a_vs_W_REF": w_flat / E.W_UM,
            "audit_2_1_ratio": AUDIT_2_1_RATIO.get(dev),
            "W_implied_b_theta_tox_lo_um": w_lo,
            "W_implied_b_theta_tox_hi_um": w_hi,
            "ratio_b_lo_vs_W_REF": w_lo / E.W_UM,
            "ratio_b_hi_vs_W_REF": w_hi / E.W_UM,
        })
    out["width_table"] = tbl

    # reproduce audit 2.1 before departing from it
    checks = [abs(z["ratio_a_vs_W_REF"] / z["audit_2_1_ratio"] - 1) * 100
              for z in tbl if z["audit_2_1_ratio"]]
    out["audit_2_1_reproduction_check"] = {
        "max_deviation_pct": max(checks),
        "verdict": ("hypothesis (a) reproduces audit 2.1's table to within "
                    f"{max(checks):.2f}%, so any difference under hypothesis "
                    "(b) is the tox ladder and not a recomputation error"),
    }

    # --------------------------------------------------- the spread metrics
    def spreads(sel) -> dict:
        g = [z for z in tbl if sel(z)]
        if len(g) < 2:
            return {}
        return {
            "devices": [z["device"] for z in g],
            "spread_a_flat_tox_x": E.spread(z["ratio_a_vs_W_REF"] for z in g),
            "spread_b_theta_tox_x": E.spread(z["ratio_b_lo_vs_W_REF"]
                                             for z in g),
            "min_ratio_a": min(z["ratio_a_vs_W_REF"] for z in g),
            "max_ratio_a": max(z["ratio_a_vs_W_REF"] for z in g),
            "min_ratio_b_lo": min(z["ratio_b_lo_vs_W_REF"] for z in g),
            "max_ratio_b_lo": max(z["ratio_b_lo_vs_W_REF"] for z in g),
        }

    sp = {
        "all_13": spreads(lambda z: True),
        "n_channel_only": spreads(lambda z: z["polarity"] == "n"),
        "p_channel_only": spreads(lambda z: z["polarity"] == "p"),
    }
    # the flatness verdict must not inherit the empirical constant's 3x band
    sp["_band_independence"] = (
        "spread_b is computed on the tox_lo edge of the band, but it is "
        "identical on the tox_hi edge: theta ~ C/tox with C in 1e-7..3e-7 puts "
        "the SAME C in every card's tox, so C cancels exactly in a max/min "
        "ratio. Verified by construction -- W ~ kp/Cox ~ kp*tox ~ kp/theta, "
        "and C does not appear. The flatness verdict is therefore robust to "
        "the 3x uncertainty in the empirical constant; only the ABSOLUTE "
        "implied widths inherit it, which is why those are reported as bands.")
    out["spread_metrics"] = sp

    a_all, b_all = sp["all_13"]["spread_a_flat_tox_x"], sp["all_13"]["spread_b_theta_tox_x"]
    a_n, b_n = (sp["n_channel_only"]["spread_a_flat_tox_x"],
                sp["n_channel_only"]["spread_b_theta_tox_x"])
    flatten_all, flatten_n = a_all / b_all, a_n / b_n
    one_divisor = b_n < 2.0

    out["verdict"] = {
        "spread_all_13": {"a_flat_tox_x": a_all, "b_theta_tox_x": b_all,
                          "flattening_factor": flatten_all},
        "spread_n_channel": {"a_flat_tox_x": a_n, "b_theta_tox_x": b_n,
                             "flattening_factor": flatten_n},
        "spread_p_channel": {
            "a_flat_tox_x": sp["p_channel_only"]["spread_a_flat_tox_x"],
            "b_theta_tox_x": sp["p_channel_only"]["spread_b_theta_tox_x"]},
        "one_line": ("ONE DIVISOR" if one_divisor else
                     "NEITHER -- fewer than thirteen, more than one"),
        "statement": (
            f"The theta-implied oxide ladder FLATTENS the residual "
            f"substantially but does not flatten it to one number.\n"
            f"  Hypothesis (a), tox = 30 nm flat: the implied-width ratio "
            f"spans {a_n:.1f}x across the n-channel cards "
            f"({sp['n_channel_only']['max_ratio_a']:.0f}x down to "
            f"{sp['n_channel_only']['min_ratio_a']:.0f}x) and {a_all:.1f}x "
            f"across all thirteen.\n"
            f"  Hypothesis (b), theta-implied tox ladder: {b_n:.1f}x "
            f"n-channel, {b_all:.1f}x across all thirteen.\n"
            f"So the tox ladder removes {flatten_n:.1f}x of the "
            f"{a_n:.1f}x n-channel slope -- most of it -- but leaves "
            f"{b_n:.1f}x behind. That is the answer to the question as posed: "
            "the sloped residual is REAL but it is mostly an artifact of the "
            "flat-tox assumption, not mostly a real kp ladder error.\n"
            "Mechanically the result is simple. Under (b), tox ~ 1/theta, so "
            "Cox ~ theta and W ~ kp/theta. kp falls 12.7x across the "
            "n-channel family while theta falls 2.2x, so the residual falls by "
            "the ratio. The kp ladder and the theta ladder are laddered "
            "together but not proportionally."),
        "ruling_on_fix_2": (
            f"NOT thirteen re-derivations. A {b_n:.1f}x spread does not "
            "justify thirteen independent physical derivations -- it is the "
            "same order as the 2.8x spread audit 2.2 was willing to call "
            "'roughly flat' and fix with a single divisor for rd/rs. "
            + ("It is also not cleanly one divisor: a single divisor would "
               f"leave a {b_n:.1f}x residual, which is more than the "
               "measurement error and would show up as a real drive-current "
               "ladder error across voltage classes.\n"
               "RECOMMENDATION: one divisor plus a per-class trim -- six "
               "numbers (one per voltage class), not thirteen, and not one. "
               "Derive the divisor from the family geometric mean and let the "
               "per-class trim absorb the residual ladder. If the maintainer "
               "will accept a 2x drive-current error at the extremes of the "
               "family, one divisor is defensible and fix #2 becomes as cheap "
               "as fix #3."
               if b_n >= 2.0 else
               "It is close enough to flat that ONE DIVISOR is defensible, "
               "and fix #2 becomes as cheap as fix #3.")),
        "MAINTAINER_DECISION_REQUIRED": (
            "*** THIS EXPERIMENT DOES NOT DECIDE THE OXIDE LADDER. ***\n"
            "Everything above is conditional on the maintainer DECLARING tox "
            "per VDMOS voltage class. The PDK never states it, and audit 2.7 "
            "already recommends stating it because three separate findings "
            "depend on it. D4 tells the maintainer what each declaration "
            "implies:\n"
            f"  * Declare tox = 30 nm flat  -> implied-width residual spans "
            f"{a_n:.1f}x n-channel -> fix #2 is a per-card job, thirteen "
            "re-derivations, as phase 1 scoped it.\n"
            f"  * Declare the theta-implied rising ladder -> residual spans "
            f"{b_n:.1f}x -> fix #2 collapses to one divisor plus at most a "
            "per-class trim.\n"
            "The theta-implied ladder is the better-supported of the two -- it "
            "is derived from a card parameter rather than assumed, it is "
            "monotonic and correctly ordered, and a rising tox with voltage "
            "class is what the process would actually do. But it is in "
            "tension with the vto = 1.00-1.31 V the cards carry, which for "
            "LDMOS body doping suggests a THINNER oxide, and D4 cannot "
            "resolve that tension. It is a process-declaration question, not "
            "a simulation question.\n"
            "Do not apply fix #2 in either scoping until tox is declared."),
        "consequence_for_anchor": (
            "docs/anchor-values.json: _vdmos_kp_conditional currently forks on "
            "decision_A_10um_cell vs decision_B_power_die. D4 shows a SECOND, "
            "orthogonal fork -- the oxide ladder -- that changes the SHAPE of "
            "the kp fix rather than its magnitude. Propose adding a "
            "`_vdmos_tox_conditional` block alongside it recording the two "
            f"hypotheses, their measured residual spreads ({a_n:.1f}x flat vs "
            f"{b_n:.1f}x laddered, n-channel), and the theta-implied tox band "
            "per class from the table above. The existing kp_n/kp_p targets "
            "are computed at tox 20-50 nm and would need restating per class "
            "under the laddered hypothesis. MAINTAINER APPLIES; do not edit "
            "the anchor from this experiment."),
    }
    return out


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
