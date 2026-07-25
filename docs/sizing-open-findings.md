# Sizing Open Findings — AutoHV BiCMOS180 PDK (phase 4, v3 — freeze)

Phase 4 is the final model-touching batch. All six listed fixes landed and are verified; the scorecard
scores **298 pass** against the amended, literature-grounded anchors (`anchor-values.json`
v4.0-phase4-grounded). **No new sizing-relevant model defect appeared.** The residuals are the same
measurement-extraction / breakdown-criterion / deferred-family items dispositioned since pass-3, plus
the theta-extraction count growing with the (deliberate) larger drift resistance. This file is the
freeze-line record; further model changes ride the normal fix process against the frozen anchors.

**Trigger still holds:** 200 V NMOS, 100 µA mirror → NDMOS200, W 13.4 µm, Vov ≈ 0.39 V, gm/Id 6.4,
σ(ΔI/I) 8.7 %.

## Phase-4 fixes — landed and verified

| step | fix | verification |
|---|---|---|
| 2.1 | HV resistive ladder re-anchor (60/80/120/200 N&P, two-regime) | ron_times_w all in-band (N 15/21/32/45 kΩ·µm; P × 2.5–3×). Idsat: N MV holds 0.23–0.39; P and 200 V drop per the penalty. |
| 2.2 | λ re-fit on 120/200 V (last flattering parameter) | va_class by gds: NDMOS200 887 V, PDMOS200 889 V — inside the grounded 300–1000 V (was ~2400–3900 V). All VDMOS va_class in-band. |
| 2.3 | DIO_SCH tt → ~0 | tt_transit_time now passes; the v1-sized residual is gone. |
| 2.4 | Zener bv tempcos | +1.50 / +7.97 / +20.04 mV/°C (measured 27/125 °C), all on-anchor; 6.2 V zero-TC crossover documented. |
| 2.5 | DNMOS20 depletion recentre | Idss 106 µA/µm at Vgs=0 (was 54.7), Vth −1.6 V; guide self-bias W ~2× smaller. |
| 2.6 | device_limits v2 + pre-flight reader | 40-device SOA envelope; preflight reads it (self-consistent, rated points in-SOA). |

## Residual scorecard items (20 hard-fail + 6 error) — all dispositioned, none sizing-relevant

### A. Measurement-extraction limited (11) — the model is physical; the harness number is not the card value
| items | disposition |
|---|---|
| **theta ×9** (NDMOS/PDMOS 40–200) | The harness extracts an *effective* theta that folds in the drift resistance, which the phase-4 ladder re-anchor made deliberately larger — so the count grew from 7 (v1) to 9. The card theta values are physical (0.12–0.20); the ≈1 readings are rd-contamination. Isolating rd in the extractor is a harness follow-up, **not** a model change. Expected, direct consequence of the grounded ladder. |
| **cox ×2** (NMOS12/PMOS12) | `capmod=3` reports an *effective* Cox just below the ideal ε_ox/t_ox band. Measurement-definition, not an oxide error (31 nm tox is correct, D6). |

### B. Breakdown-criterion (8) — soft-knee / wrapper, not a card-BV error
| items | disposition |
|---|---|
| **NPN bvcbo / bvceo ×4** | `Bavl` avalanche soft knee; measured lands ≈0.841× the card BV at the sampling current. Card BV correct. |
| **PNP bvcbo / bvceo / johnson ×6 (errors)** | Known wrapper bug: the `Bavl` branch is the NPN expression copy-pasted without a sign flip, so it is dead code on the PNPs (collector below base → clamped to 1). BVCBO/BVCEO unmeasurable until the wrapper is made polarity-aware. **The one genuine model defect here** — it is small, long-documented (phase-2 audit worklist), out of phase-4's listed scope, and deferred to the normal post-freeze fix process. It does not affect any sizing number. |

### C. Deferred device families (4) + marginal cap (1)
| items | disposition |
|---|---|
| **zener cjo_density ×3** | Zener junction-cap density not re-derived (synthetic-residue item; buried in the subckt). |
| **DZ_5V6 bv ×1** (5.24 V) | Soft-knee: the 5.6 V part measures 5.24 V at the 1 mA criterion (knee below the label). Zener re-derivation deferred. |
| **PDMOS200 cjo_per_cell ×1** (17) | 200 V p-cell junction cap just under the ±3.5× band at the high-BV end. Cosmetic; no sizing impact. |

## Bottom line

The realism program's freeze condition is met: the sizing guide covers 40/40 devices with no known-wrong
columns, the trigger case lands where an HV designer would expect, and every scorecard residual is a
measurement-extraction limit, a breakdown-criterion artifact, or a deferred/known item — **not a
sizing-relevant model defect.** The single genuine defect (PNP breakdown wrapper polarity) is documented
and handed to the normal fix process. There is no open item that changes a sizing-guide value.
