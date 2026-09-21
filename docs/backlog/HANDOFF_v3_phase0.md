# Brief v3 — Phase 0 complete, and the questions blocking Phase 1

**Brief:** `HANDOFF_v3_stats_brief.md` (v3: full replacement; supersedes the earlier brief,
the rulings reply — filed here as `HANDOFF_mc_realism_rulings.md`, which v3 calls
`HANDOFF_mc_realism_review_REPLY.md` — and the open questions in `HANDOFF_mc_realism_stop1.md`)
**Branch:** `mc-realism`, worktree; base `61de05f` = `main`
**Date:** 2026-09-16
**Status:** Phase 0 done. **Phase 1 (Stop A) is blocked on Q-A**; Q-B, Q-C and Q-E shape the
`stat_model.json` entries, and Q-D is a tool-design detail for Phase 4.

## 1. Phase 0 against brief §2

| # | item | result |
|---|---|---|
| 1 | merge `transmission-gates` → `main` | already done at stop 1; `main` = `origin/main` = `61de05f` |
| 2 | CI builds and caches ngspice-45 | verified: CI asserts the version and fails if it is not 45; runs on `e842e5c` and `f43e978` both green, source build 203 s then cached |
| 3 | fix the broken CI MC check **and explain the 21 % gap** | done — §2 below. Both axes now pass |
| 4 | delete leftover MC copies; **list, do not delete**, the uncommitted edits | deleted (verified byte-identical to the branch first); the two edits are listed in §4 and untouched |
| 5 | lib header 38 → 40; commit `circuits/mc_mismatch_check/` | done at stop 1 (`5a49e27`, `5f9f114`) |
| 6 | freeze `pdk_validation/baselines/v2_2/` | done (`4117e79`): 34 files from `61de05f` with per-file sha256 in `MANIFEST.json`, plus the 36-corner regression output (36/36 pass) |

## 2. The 21 % gap — explained, and my first hypothesis was wrong

The brief's four candidates do not apply: the √2 pair factor is present and correct; the CLM
gain error cancels because the check uses σ of a *log ratio*; the 1σ/3σ convention was already
handled; and gm/Id is measured empirically per run, not assumed from a reference bias.

I first proposed series resistance and CLM. **Ablation refuted both**: `rdsw=0` leaves the
discrepancy unchanged (1.165 → 1.166) and weakening CLM barely moves it (1.117 → 1.091 on the
L term only).

The real cause is that `run_mc.py` compared the measured σ against **textbook first-order
sensitivities**, which are 9–17 % low on this card. Measured on its own bench (NMOS5V0,
W = 10 µm, L = 1 µm, Vgs = 2 V, Vds = 3 V):

| term | assumed | measured | ratio | attribution (by ablation) |
|---|---|---|---|---|
| d lnI/dVth | −gm/Id = −1.687 V⁻¹ | −1.966 V⁻¹ | 1.165 | mobility degradation: Vth enters the effective field explicitly. `ua=ub=uc=0` → ratio **1.000** |
| d lnI/d lnW | +1 | +1.096 | 1.096 | narrow-width Vth term. `k3=0` → **1.004** |
| d lnI/d lnL | −1 | −1.117 | 1.117 | short-channel Vth roll-off + mobility. `k3=0, dvt0=0`, mobility off → **−1.005** |

Two independent measurements agree exactly: isolating one mismatch term at a time in a scratch
library, and perturbing the drawn dimensions directly with the knob solved out
(+1.0956 / −1.1172 / −1.9656 V⁻¹ both ways).

Putting it together at N = 400: stale coefficient 2.44× (13.5 vs 33 mV·µm, widened in `dc7de19`
and never propagated here), then the sensitivity model 1.21×. With both corrected, expected
0.978 % against measured 1.014 % — about 1.1 standard errors. **The mismatch model was never
wrong; the checker's expectation was.**

**Finding for Stop A:** the NMOS5V0 card declares no `k3`, `k3b` or `w0`, so **BSIM3's default
`k3 = 80` is active** — an undeclared narrow-width Vth term that shifts every narrow device and
that nothing in the PDK documents. Brief §0 unfreezes the models, so this belongs in the §3
authoring pass.

### The fix

`pdk_validation/regression/run_mc.py` now reads `A_VT`, `A_W` and `A_L` from the NMOS5V0 wrapper
in the `.lib` (no hardcoded copies to go stale), and computes the intended σ from sensitivities
measured on the bench — seven op points, about 0.6 s — printing the first-order estimate
alongside so the difference stays visible:

```
A_VT / A_W / A_L (3-sigma)      = 33.0 mV.um / 0.75 %.um / 0.45 %.um
measured d lnI/dVth             = -1.966 V^-1   (gm/ID = 1.687 V^-1)
measured d lnI/dlnW, d lnI/dlnL = +1.096, -1.117   (first order: +1, -1)
intended sigma(log I1/I2) (RSS) ~ 0.978 %
first-order estimate            ~ 0.840 %  [+16 %]
measured sigma                  = 0.924 %  (deviation 5.4 %)
OK: within 30 % of intended sigma
```

`--axis mm -n 200` and `--axis proc -n 80` both pass. No golden was rebaselined.

## 3. Questions

**Q-A blocks Phase 1** — it sets the schema of `stat_model.json`, the Stop A deliverable.

| Q | question | recommendation |
|---|---|---|
| **Q-A** | §3.1 makes `VTH_<dev>`, `U0_<dev>`, `RDSW_<dev>` independent variables, but §3.4 sets a group's fast/slow to ±3σ on **each** of its variables. That vector's Mahalanobis distance is 3·√k, not 3, so §11's "FF preset ≈ 3" and B9's "FF/SS Idsat at 3–4.3σ" are unreachable by construction (k ≈ 4 lands near 6σ). | **(i)** give each device group one latent speed variable with declared loadings onto Vth/u0/rdsw (plus optional small residuals): fast = z=+3 on one variable, distance exactly 3, B9 holds, and it matches the reference process's own per-group fast/slow scheme. **(ii)** keep independent variables and restate §11/B9 as "≈3√k, reported". I recommend (i). |
| **Q-B** | §5.2 feeds `rgate` from "the `RSH` of the gate poly layer", but this PDK has no gate poly layer — only resistor layers at 1200 Ω/□ (RPOLY_HI) and 300 Ω/□ (RPOLY_LO). A silicided gate is typically 5–15 Ω/□, so either would overstate gate R by 20–100×. | Declare a new `RSH_GATE` (~8 Ω/□, literature, with an error bar) and add `rgate`; **or** drop gate R from this program. Either way, add "all transient and AC timing numbers move" to §11 — adding a series gate resistor changes every delay and comparator result, and that mover is missing. |
| **Q-C** | §5.4 adds a perimeter term to every capacitor, which moves published capacitances. | Constrain the `CDEN`/`CPER` split so total C is unchanged at the 10×10 µm reference geometry, as §5.3 already does for resistors. The CMIM_STD golden is exactly that geometry at 10 pF, so goldens stay valid and only the size-dependence changes. |
| **Q-D** | `--exhaustive` 3^k: a comparator deck instantiating 8–12 device types gives 6,561–531,441 runs (≈5 min to ≈7 h at measured speed). | Add `--max-runs`, default ≈20,000, erroring with a pointer to `--groups` or sensitivity-guided pruning. |
| **Q-E** | §5.5's `A_VBE` in mV·µm needs an area in µm², but the wrappers take `AREA=0.04` as a multiple of the declared 100 µm² cell. | Confirm σ = `A_VBE/√(AREA·100·M)`, i.e. `AREA=0.04` means 4 µm². |

### Deviations from §3.1 I will apply unless told otherwise

- **`TOX_50` is not shared with the 12 V devices.** NMOS12V/PMOS12V carry their own fixed
  `tox = 31 nm` against 11 nm at 5 V, and the reference process confirms a separate 12 V oxide. So: `TOX_12`,
  its own variable.
- **VDMOS devices get no `TOX` variable at all.** The ngspice VDMOS cards have no `tox`
  parameter; oxide effects can only enter through `KP`/`VTO`, so that is where their loadings go.

## 4. Left alone, as instructed

The two uncommitted edits in the main folder are **listed, not touched**:

| file | state |
|---|---|
| `.gitignore` | modified (adds the MC `decks/` ignore line) |
| `docs/backlog/README.md` | modified (adds backlog entry #3 for the MC handoff) |

Both are already committed on `mc-realism` (`5f9f114`), so after the merge they can be discarded.
The main folder also holds unrelated xschem work (5 modified, 5 untracked), untouched.

## 5. Next

Phase 1 authoring of `stat_model.json` starts on an answer to Q-A, and ends at Stop A with the
model, `docs/stat-model.md` and the preset table for approval. Nothing is generated before then.
