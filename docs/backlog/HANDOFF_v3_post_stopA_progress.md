# Handoff: post-Stop-A progress — masters in, S2 switch built, one solve defect open

**Responds to:** the S1–S3 rulings reply (Stop A approved subject to §1–§4)
**Brief:** `HANDOFF_v3_stats_brief.md` as amended by the Phase 0, Phase 1, G1–G4 and S1–S3 replies
**Branch:** `mc-realism`, pushed
**Date:** 2026-09-17
**Status:** §6 items 1 and 2 built; item 3 (re-measure + rebuild) blocked on a defect in my own S2
solve, described in §3. Phase 2 has not started. Three questions, T1–T3.

## 1. Done this round

| §6 item | state |
|---|---|
| 1. masters into `stat_model.json` | **done** — 7 masters, 36 variables tagged, loadings declared |
| 1. `docs/stat-model.md` section | not yet |
| 2. S2 calibration switch | **built**, and it correctly switches — but the solve does not converge for the switched variable (§3) |
| 3. re-measure at Lmin, rebuild `corners.json` with covariance-aware Mahalanobis | blocked on §3; `build_corners.py` still uses the Euclidean norm |
| 4. Phase 2 generator | not started |

## 2. S1 — masters added, and the loadings are declared

**§1.2 step 1 checked and answered: the correlation data is not available locally.** the reference process §8.3
*does* carry master-variable correlation matrices — the local extraction names them, in its
"noted, not pursued" list, and states they were never transcribed ("§8 Statistical Models (p102)
offers full worst-case libraries + master-variable correlations (not transcribed — the LSL/USL
cross-check suffices)"). Nothing else in the extraction carries ρ values, loadings or a covariance
matrix. So §1.2 step 2 applies and the loadings are **declared**:

| master | ρ | loads onto |
|---|---|---|
| `G_N` | 0.7 | NMOS `VTH`/`U0` all classes, plus every N-LDMOS `VTO`/`KP` (22 variables) |
| `G_P` | 0.7 | PMOS and P-LDMOS equivalents (20) |
| `G_OX` | 0.7 | `TOX_18/33/50/12` |
| `G_LITHO` | 0.7 | `DL_POLY`, `DW_ACT_LV/HV` |
| `G_RSH` | 0.6 | all `RSH_<layer>`, `RSH_GATE`, all `RHEAD_<layer>` |
| `G_CAP` | 0.6 | `CDEN_*`, `CPER_*` |
| `G_BJT` | 0.6 | `VBE_*`, `BF_*`, `VF_<dio>` |

`RDSW_*`, `BV_*`, `RS_<dio>`, `CJ_<dio>` stay uncorrelated, as ruled. Each variable now carries
`master: {name, rho}`; σ is unchanged, only the decomposition. Recorded in the JSON that these are
the least-grounded numbers in the model. **See T3** — the real matrices exist in the source
document.

## 3. S2 — the switch works, the solve does not converge — **T1**

The harness now measures the `U0` slope first and, below 0.4, holds `U0` at the literature 8 % 3σ
and solves `RDSW` instead. It switches exactly where predicted. But the switched solve lands far
off the band:

| group | `U0` slope | solved | σ 1σ | achieved swing | band error |
|---|---|---|---|---|---|
| NMOS5V0 (Lmin bench) | 0.73 | `U0` | 5.55 % | 13.8 % | −1.6 % |
| NDMOS40V | 0.57 | `U0` | 6.84 % | 13.7 % | −1.9 % |
| NDMOS200V | 0.23 | **`RDSW`** | 3.44 % | **8.4 %** | **−40.0 %** |

The defect is mine, in the solve rather than the ruling. I compute
`need = √(band² − fixed²)/3/slope` from a slope measured at a 1 % probe. That inversion is only
valid if the response is locally linear. `U0` satisfies that; `RDSW` does not — the drift
resistance saturates, so the effective slope at the σ needed to close the gap is much smaller than
the probe slope, and the single shot undershoots by 40 %.

This is the third time in this program that assuming a linear sensitivity produced a wrong number
(first `run_mc.py`'s expectation, then my own `U0` calibration slope, now this). The fix is the
one that worked twice: iterate — re-measure the achieved swing, re-solve, repeat to a tolerance,
with a cap and an explicit failure if it will not converge.

**Before I build that, T1 asks whether convergence is even the right goal here**, because of T2.

## 4. §4.1 — the Lmin bench does what the ruling expected

Classic benches now use each class's `Lmin_fab` from `device_limits` (0.18 / 0.35 / 0.5 / 0.5 µm
for the 18 / 33 / 50 / 12 classes) instead of the L = 1 µm analog default. On NMOS5V0 that roughly
doubles the `DL_POLY` sensitivity, **−0.0031 → −0.0067**, which is the effect F3a originally
expected and my L = 1 µm measurement did not show. `VTH` and `TOX` sensitivities are essentially
unchanged. The L = 1 µm and analog-bench directions are retained as additional records.

VDMOS benches carry no `L_classic_um`: those wrappers take no channel length. Correct, and now
recorded explicitly rather than appearing as a null.

## 5. Questions

| # | question | my proposal |
|---|---|---|
| **T1** | The `RDSW` solve undershoots the band by 40 % because the response saturates (§3). Iterate to convergence, or accept what the device can actually deliver? | Iterate, but **cap it**: if the achievable 3σ swing at a physically sensible `RDSW` σ (say ≤ 30 % 3σ) still falls short of the band, stop and report the shortfall rather than inflating the variable — that is exactly the failure mode S2 was written to prevent, just moved from `U0` to `RDSW`. |
| **T2** | **Is the 14 % Idsat band even the right target for a 200 V LDMOS?** The class bands come from the reference process's *CMOS* classes (±20 / 20 / 14 %). I applied 14 % to all 13 VDMOS as an assumption; the reference process states no LDMOS Idsat band. The 40 % shortfall may be telling us the target is wrong rather than the solve. | Ground or drop it: if the reference process gives an LDMOS Rdson or Idsat spread anywhere, use it per class; otherwise declare the VDMOS band from the Rdson tolerance a power-device datasheet would quote (typically ±25–35 % on Rdson, which is a *wider* Idsat band than 14 %) and record it as declared. I would not keep an un-grounded 14 % that the physics then has to be bent to meet. |
| **T3** | The master loadings are declared at 0.7/0.6 ±0.2 and are now the least-grounded numbers in the model, yet the reference process §8.3 contains the real correlation matrices — they were simply never transcribed into the local extraction. | If the source document is still available, transcribing §8.3 would move the single weakest part of the model to `source: the reference process`. It is a read, not an experiment. Worth doing before Phase 2 freezes the structure. |

## 6. Next, once T1–T2 are answered

Fix the solve, add the covariance-aware Mahalanobis to `build_corners.py` (distance becomes
√(zᵀΣ⁻¹z) built from the master decomposition; single-group corners must still come out at 3.00),
write the `docs/stat-model.md` masters section, re-measure all 40 groups, rebuild `corners.json`,
and post the new preset table — including the all-MOS FF distance, which §1.3 expects to fall from
13.84 to roughly 4–6 once the masters are in.
