# Handoff: v3 Stop A — the statistical model, complete and measured

**Responds to:** the G1–G4 rulings reply
**Brief:** `HANDOFF_v3_stats_brief.md` as amended by the Phase 0, Phase 1 and G1–G4 replies
**Branch:** `mc-realism`, pushed
**Date:** 2026-09-16
**Status:** all six Stop A deliverables exist. **Nothing is generated from them** — no `.inc`, no
wrapper change, no golden touched. Three items need a ruling before Phase 2 (§4).

## 1. Deliverables

| deliverable | where | state |
|---|---|---|
| statistical model | `models/stat_model.json` | 131 global variables, 40 groups, G1–G4 applied |
| reading copy | `docs/stat-model.md` | one section per variable family, with sources and error bars |
| defaults audit | `docs/bsim3-defaults-audit.md` | 18 live BSIM3 defaults; `k3` grounded with measured evidence |
| measured directions | `models/stat_directions.json` + `tools/measure_stat_directions.py` | **40 of 40 groups**, six bench types, both benches for MOS/VDMOS |
| preset table | `models/corners.json` + `tools/build_corners.py` | cases 0–16 with Mahalanobis distances; `--check` round-trips |
| F1 discrepancy note | `docs/stat-model.md` §3.1 | recorded as unexplained, spec column unused |

## 2. The headline result: compound presets are nowhere near 3σ

Distances are the Euclidean norm of the summed z-vector, which is the Mahalanobis distance because
the variables are independent unit normals.

| case | preset | groups | variables | Mahalanobis |
|---|---|---|---|---|
| 0 | typical | 0 | 0 | 0.00 |
| 1 / 2 | FF / SS, all MOS | 21 | 70 | **13.84** |
| 3 / 4 | FS / SF | 20 | 67 | **13.38** |
| 5 / 6 | LV fast + HV slow, and the reverse | 21 | 70 | **13.84** |
| 7 / 8 | all resistors lo / hi | 5 | 6 | **6.71** |
| 9 / 10 | all capacitors lo / hi | 4 | 3 | **8.49** |
| 11 / 12 | BJT and diodes lo / hi | 10 | 24 | **9.49** |
| 13 / 14 | slow / fast everything | 40 | 102 | **19.99** |
| 15 / 16 | SS + R lo, FF + R hi | 26 | 75 | **15.42** |

A **single-group** corner is exactly 3.00, as the Q-A construction guarantees. But brief §11
pre-registers "FF preset Mahalanobis ≈ 3", and that cannot hold for a 21-group preset: summing 21
independent 3σ directions gives √21 × 3 ≈ 13.7, which is what comes out. The shared-variable rule
explicitly declines to rescale, so the number is reported as-is.

This is not a defect — it is the measurement doing its job. It says plainly that **sign-off at
case 1–4 is a 13.8σ demand**, and that cases 13–16 at 20σ are pessimistic by construction, exactly
as the brief anticipated for those. What it also means is that today's FF/SS corners, which the
existing PDK treats as normal sign-off, are far outside anything the process would produce.
**Ruling needed — see S1.**

Presets 3 and 4 correctly report shared-variable conflicts: n-type and p-type groups pull `TOX`
and `DL_POLY` in opposite directions, which is what an FS/SF corner means.

## 3. What was measured, and what it showed

### 3.1 Calibration lands within 2 % on every class

`U0` σ solved per group against the reference process Idsat band, fixed set at grounded σ, slope measured not
assumed (0.23–0.98 across the 21 MOS/VDMOS groups). No group hit the 3 % floor. Every class lands
within 2 % of its band.

### 3.2 The VDMOS calibration is straining — **S2**

`KP`'s lever on drain current falls monotonically with voltage class, because drift resistance
progressively takes over:

| class | `U0` slope | solved `U0` 3σ | dominant direction terms |
|---|---|---|---|
| 20 V | 0.71 | 17.8 % | `U0` +2.68, `VTH` −1.00 |
| 40 V | 0.57 | 20.5 % | `U0` +2.49, `RDSW` −1.36 |
| 80 V | 0.39 | 25.6 % | `U0` +2.13, `RDSW` −1.92 |
| 120 V | 0.29 | **31.1 %** | **`RDSW` −2.24**, `U0` +1.87 |
| 200 V | 0.23 | **34.7 %** | **`RDSW` −2.42**, `U0` +1.66 |

A 31–35 % 3σ mobility spread is not credible. It is an artifact of forcing a 14 % Idsat band onto
a drift-limited device through the one variable ruling F3 lets the solver move. Above 120 V the
direction has already tipped to `RDSW`, which is the honest physics. The fix is to let `RDSW`
carry the band on the high-voltage devices — but that changes F3's fixed set, so it needs a ruling.

### 3.3 `DL_POLY` is not first-order at this bench — closes the F3a gap

`DL_POLY` and `DW_ACT` now enter through the cards' `lint`/`wint` (`dL = −2·dlint`), so the fixed
set is finally what F3a specifies. Their measured contribution is small: on NMOS5V0 the fixed-set
swing moves 7.73 % → 7.80 %, with `g(DL_POLY)` = −0.0031 against `g(VTH)` = −0.0251. F3a expected
`DL_POLY` to be first-order at the classic bench; at L = 1 µm it is not. It would be at minimum L.

### 3.4 Variables with no lever, excluded with reasons

Not carried as zeros, which would dilute the directions:

| variable | groups | reason |
|---|---|---|
| `RSH_GATE` | all 8 MOS | no `rgate` term until Phase 3 — **the Q-B variable is inert everywhere today** |
| `JS_MOS` | all 8 MOS | junction leakage is picoamps against the bench current |
| `TOX_50`, `DL_POLY`, `DW_ACT_HV` | all 13 VDMOS | those cards carry no `tox` or channel-length parameter |
| `BV_<vdmos>` | all 13 VDMOS | breakdown has no lever at a bias far below the rating |
| `RHEAD_<layer>` | all 5 resistors | no head term until Phase 3 |
| `CPER_<type>` | CMIM_STD, CMIM_HI, CMOM | `cjsw = 0` on those cards; only CFRINGE has a perimeter lever |
| `CJ_<dio>` | all 6 diodes | junction capacitance has no lever on a DC forward current |

### 3.5 `BF` needed its own bench, per G3

At a fixed-`Vbe` bench `BF`'s sensitivity is 7e-6 — collector current barely depends on β there. On
a base-current-driven bench it is 0.0394. Both are recorded in `bf_share`, so a β-only corner stays
constructible, and the direction uses the base-driven value.

## 4. Rulings needed before Phase 2

| # | item | my proposal |
|---|---|---|
| **S1** | Compound preset distances are 13.8 (FF/SS) to 20.0 (everything), against §11's "≈ 3". | Keep the sum unrescaled — it is the honest number and the whole point of having the column. Replace §11's entry with "single-group = 3.00; all-MOS FF = 13.8; report the rest", and add one line to `docs/corners.md`: presets 1–6 are **multi-module worst cases, not 3σ process corners**, which is why MC and the exhaustive sweep exist. If instead you want case 1–4 to *be* a 3σ corner, the construction has to change: rescale each preset to 3, which makes FF a much milder corner than today's and will move every published corner result. |
| **S2** | VDMOS `U0` inflated to 31–35 % 3σ at 120–200 V (§3.2). | Extend F3's solve: for VDMOS, calibrate against `RDSW` rather than `U0` where the measured `U0` slope is below ~0.4 (that is 80 V and above). Keep `U0` at a literature 8 % 3σ there. Report both the old and new directions. |
| **S3** | `A_VT` anchors: G1 states "0.78 N / 0.94 P"; the reference process §E reads nmos2v 6.0 / pmos2v 5.0 mV·µm at 6.4 nm, i.e. N 0.9375 / P 0.7812. | The corrected assignment is already applied (N is the worse matcher in both measured anchors). Confirm, so it is on the record rather than being my unilateral reading. |

## 5. Numbers that will move, for §11

| quantity | before | after |
|---|---|---|
| A_VT 1.8 V | 3.5 | N 4.60 / P 3.85 mV·µm |
| A_VT 3.3 V | 4.0 | N 6.17 / P 5.14 |
| A_VT 5 V | 11.0 | **N 6.89 / P 5.63** |
| A_VT 12 V | 31.0 | **N 15.03 / P 12.07** |
| narrow-device Vth (`k3`) | +238 mV at W = 0.4 µm | +29 mV |
| VDMOS A_VT | per-cell 24 mV form | 20 mV·µm, reference-measured |
| BJT/diode `IS` corner | ±6 % | ≈ ±25 % (via `VBE` 6 mV, `VF` 8 mV) |
| tox σ | ±1 % across FF/SS | 4 % 3σ |
| corner distances | never computed | tabulated in §2 |

## 6. After approval

Phase 2 builds `tools/gen_models.py` and generates the `.inc` from this model, with the B1
self-tests. Nothing before then.
