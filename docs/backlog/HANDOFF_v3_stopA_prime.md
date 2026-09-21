# Stop A′ — the statistical layer is derived, measured and rebuilt

**Responds to:** the AB1–AB2 rulings reply and the standing autonomy rule
**Branch:** `mc-realism` @ `4f1e8df`, pushed. Six commits, `1e3998a` → `4f1e8df`.
**Date:** 2026-09-18
**Status:** Every item in the §4 queue is done. No §2 stop was hit after AB1. One reported
plausibility miss and one correction to a figure I had been quoting.

---

## 1. Decisions taken under §1

| # | decision | basis | recorded in |
|---|---|---|---|
| 1 | Z2 applied as reduced; `ksubthres`, `VTO`, `A_VT`, `rd`/`rs`/`BV` held | ngspice VDMOS has no oxide; threshold is implant-set; width-vs-area normalisation | `1e3998a`, D2, CHANGELOG |
| 2 | Surviving `_RESISTORS` / `_CAPACITORS` reference names left | AA2 named only the VDMOS `A_VT`; those carry their own rulings, scoped to Z3(b) | `1e3998a` |
| 3 | Duplicate `## D2` heading collapsed | my Z2 edit inserted a second heading instead of retitling | `3ef3a69` |
| 4 | `Q_f` variation taken at 50 %, not the 30 % the ruling's own table implies | tie-break: closer to current PDK behaviour; both recorded | `2dd54a1`, `_VTH_inputs` |
| 5 | Generator applies the **full** oxide-coupling closed form, not the remainder | residual is 4–20 %, geometry-dependent and not subtractable; well inside ±50 % | `dependent_parameters.vth0.validation` |
| 6 | U1 binary sharing landed with the AB1 package | nothing reads `master`/`rho`; removes a live contradiction | `2dd54a1` |
| 7 | U0 declared at 8 % 3σ; per-class Idsat bands retired | bands were externally sourced and the LDMOS one invented | `8b0144d` |
| 8 | Record shape settled on `u0_sigma_1s` / `dominant_variable` / `predicted_3sigma_swing` | two harness versions had written two different shapes | `8b0144d` |
| 9 | `_VTH_VDMOS_template` refreshed | carried a retired σ that disagreed with every entry it describes | `4f1e8df` |
| 10 | Duplicate `### 3.1` collision fixed; §3 renumbered | introduced by my own `A_VT` rewrite | `8b0144d` |

## 2. What the statistical layer now says

**σ(VTH), derived — three terms, no spec windows, no tightening factor**

| device | 1σ mV | | device | 1σ mV |
|---|---|---|---|---|
| NMOS18 | 10.3 | | NMOS50 | 16.5 |
| PMOS18 | 11.3 | | PMOS50 | 17.6 |
| NMOS33 | 12.5 | | NMOS12 | 43.0 |
| PMOS33 | 13.6 | | PMOS12 | 44.5 |
| VDMOS ×13 | 20.0–23.1 | | | |

**`A_VT`, derived (Z1)** — `c_RDF` = 2.1991 mV·µm/√nm, constant to 3.18 % across four oxide
classes: 3.44 / 3.66 / 4.51 / 4.81 / 5.96 / 6.41 / 15.02 / 15.84 mV·µm.

**Predicted 3σ Idsat (U2)** — reported, not targeted:

| group | swing | dominant |
|---|---|---|
| NMOS18 / PMOS18 | 9.64 / 11.96 % | `U0` |
| NMOS33 / NMOS50 / NMOS12 | 7.22 / 6.80 / 6.79 % | `U0` |
| NDMOS20 | 7.30 % | `U0` |
| NDMOS80 | 9.76 % | **`RDSW`** |
| NDMOS200 | 11.59 % | **`RDSW`** |

The `U0`→`RDSW` flip is measured, not declared: it happens exactly where drift resistance takes
over, as the `U0` slope falls through 0.4. That is the U0/Rd anti-correlation as a device property.

**Corners** — 40 directions measured, 17 presets. FF/SS **16.54**, FS/SF **12.83**, slow/fast
everything **22.10**. FF/SS rose and FS/SF fell because the AB1 coupling puts `TOX` in every MOS
direction: same-polarity presets pull each shared oxide together, opposite-polarity presets fight
over it (reported as shared-variable conflicts on presets 3 and 4).

## 3. Acceptance

| check | result |
|---|---|
| plausibility | 17 checked, **2 reported misses**, 4 with no comparable class |
| `corners.json --check` | clean |
| oxide coupling validated against ngspice | `showmod` confirms `vth0`/`k1` do not move with `tox`; residual 3.7–19.5 % |
| plausibility script vs AB1 generator | **zero diff** on all 21 variables |
| `--apply` with no local magnitudes | refused, exit 1 |

> **Corrected 2026-09-19.** The 3.7–19.5 % residual quoted above is wrong. It came from
> constant-current and gm-max extraction, both of which move with `tox` themselves and gave
> criterion-dependent, sign-unstable results (NMOS18 read −0.18 mV at a 1× W/L criterion,
> −0.61 at 0.1×, +3.52 at 10×). Measured from the model's own `@m.xm1.m0[vth]` at bench
> geometry the residual is **negative**, −0.96 to −1.92 mV, i.e. 9–22 %, which makes
> `applied = analytic − residual` *larger* than analytic rather than smaller. See
> `docs/stat-model.md` §2.2a.

**The reported miss:** NMOS33 and PMOS33 land at 0.26× and 0.28× of their comparable midpoint.
Per U3 this is reported, not clamped. Your own §2.4 anticipated it and attributed it to a probable
shared 3.3/5 V implant artefact in the reference — worth noting that the comparable for 3.3 V
(41–56 mV) is *wider* than the one for 5 V (16–22 mV), which is backwards for a thinner oxide.

## 4. A figure I had been quoting wrongly

I reported the external-reference count as falling "28 → 19 → 14 → 12 → 11". Those numbers mixed
case-sensitive and case-insensitive greps and were counting different things at different times.

**One definition — case-insensitive `<reference-name pattern>` across tracked files: 100 occurrences in 16
files.**

| file | count |
|---|---|
| `docs/backlog/HANDOFF_v3_phase1_proposal.md` | 22 |
| `models/stat_model.json` | 19 |
| `docs/backlog/HANDOFF_v3_phase1_progress.md` | 15 |
| `docs/stat-model.md` | 9 |
| 12 further files | 35 |

The naming pass is substantially larger than the model file alone — most of it is committed
backlog handoffs, which §5 of the naming rule explicitly includes.

## 5. State

- `models/stat_model.json` — 51 global variables, 13 dependent parameters, no `master_variables`.
- `models/stat_directions.json` — 40 of 40 groups.
- `models/corners.json` — 17 presets, `--check` clean.
- `tools/check_plausibility.py` — new; local magnitudes gitignored, booleans only.
- `docs/stat-model.md` — §2.1, §2.2, §2.2a, §2.3, §3, §3.1–3.3, §5 regenerated from the artefacts.

## 6. Queued behind this stop

Phase 2 (`tools/gen_models.py`) honouring the `follows` couplings — they are a contract recorded in
`dependent_parameters` and nothing generates perturbed cards from them yet. Then the **naming
pass** per §5 of the rule (inventory, disposition, renames, CI guard, provenance taxonomy), which
that 100-occurrence inventory now sizes properly, followed by Phases 3–7.

Open and unchanged: `k3` grounding at 2.0 awaits the audit landing; the NDMOS200 trigger-case
drift is logged for Phase 7 per AA3.
