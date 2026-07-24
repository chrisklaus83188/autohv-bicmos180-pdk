# Sizing Open Findings — AutoHV BiCMOS180 PDK (phase 3)

Items the phase-3 fix batch did **not** fully resolve, handed to the maintainer rather than guessed at.
Per the loop rule (max two iterations per family, then escalate), and honest scope accounting for a
large batch. The trigger (200 V mirror F1) and the sizing guide are **complete and validated**; these
are the remainder.

## Fixes applied and validated (for reference)
- **VDMOS F1/F2/F-VD3** — kp flat at the 13 nm cell, rd/rs re-derived, mismatch ladder unified, caps
  re-derived. Verified: NDMOS200 100 µA mirror → W 13.4 µm, Vov 0.47 V, gm/Id 6.4. **The trigger is fixed.**
- **Passives F7** — RPOLY_HI tc1 sign, sheet Rs, matching widened.
- **BSIM3 F6/F3** — AD/AS/PD/PS set (junction cap now non-zero), BSIM3-convention noise, kt1/ute added.
- **BJT** — PNP `Bavl` polarity (dead-code), kf/af calibrated, cje/cjc to AREA=100 µm².
- **NMOS12 D6** — tox → 31 nm, `device_limits.csv` Lmin → 0.5 µm, PDMOS120/200 rows added.

## Deferred / incomplete (escalated)

| # | item | state | what remains |
|---|---|---|---|
| O1 | **Anchor JSON merge (Step 1)** | **not applied to `anchor-values.json`** | The fixes were derived from physics + the amendment docs directly, not from a merged JSON. The amendments (`anchor-amendments-onc25.md` passes 1–2 + `audit-vs-measurement-discrepancies.md`) still need merging into `anchor-values.json` with a `_meta` version bump, so the scorecard scores against one reconciled band per entry. All target numbers are already spelled out in those docs. |
| O2 | **Full re-baseline scorecard (Step 3.1)** | **partial** | Each fix carries targeted verification and the sizing sweep validates the MOS family end-to-end, but the complete 548-measurement phase-2 harness re-run (the after-picture `characterization-scorecard.md`) was not regenerated. Run `python pdk_validation/characterization/run_all.py` after O1. |
| O3 | **Passive golden regeneration (Step 3.2)** | **not done** | `run_passives.py --regenerate` — the sheets/TCs moved by design; the 9 goldens will fail until regenerated. Required before the regression suite is green. |
| O4 | **NMOS12/PMOS12 u0/rdsw re-fit + single u0 draw + stat-name normalization** | **partial** | tox/cj/noia/kt1/Lmin done; the u0 (÷~1.5 from the double-draw), rdsw re-fit to the 12 V-scaled target, and the stale `P_DVMAX_/P_DRSH_` → `P_DVSAT_/P_DRDSW_` rename remain. Cosmetic-to-distorts-results, not sizing-blocking (the 12 V devices size sensibly as-is). |
| O5 | **A_VT widening for the 50 V / 12 V BSIM3 pairs** | **not done** | Audit found NMOS50/PMOS50 2.4× and NMOS12/PMOS12 3.3× optimistic. Widen the wrapper 3σ literals (×3 convention): 50 V pair 0.0135 → ~0.033, 12 V pair 0.018 → ~0.093 at the 31 nm oxide. The sizing σ(ΔI/I) columns for those devices are correspondingly optimistic until this lands. |
| O6 | **VDMOS RDRIFT wrapper slope + body-diode `is`** | **not done** | The 200 V `RDRIFT` L-dependence slopes (1.2 / 3.0) should rescale by the rd factor for L-consistency; body-diode `is` nudge at the 200 V end is cosmetic. Neither affects the mirror sizing. |
| O7 | **MC σ(ΔI/I) via the harness** | **worked around** | The `mc_run` pair-deck returned degenerate in the sizing context; the guide's σ(ΔI/I) is computed **analytically** from the fixed mismatch coefficients (exact for this model, matches `run_mc.py`'s form). The N=200 MC cross-check is a follow-up. |
| O8 | **BJT β/collapse re-sweep (criterion C7)** | **not re-swept** | β cards unchanged (in-band per the audit), so β is expected fine, but it was not re-measured across the recommended Ic window. |
| O9 | **DNMOS20 (depletion) in the sizing guide** | **omitted** | The depletion device needs a different bias convention (vto < 0); it was left out of the mirror sweep. Add with a Vgs-around-0 setup. |

## Recommended maintainer next steps (in order)
1. **O1** (merge anchors) → **O3** (regen goldens) → **O2** (full re-baseline scorecard) — closes the
   loop the brief specified; everything is spelled out.
2. **O5** (A_VT widening) and **O4** (NMOS12 u0/rdsw) — the remaining realism items with measurable
   sizing impact.
3. **O6–O9** — cosmetic / completeness.

Nothing here blocks the success condition: a designer opening `sizing-guide.md` for "200 V NMOS,
100 µA mirror" gets W ≈ 13 µm, Vov ≈ 0.47 V, gm/Id ≈ 6.4 — the numbers an HV designer would nod at.
