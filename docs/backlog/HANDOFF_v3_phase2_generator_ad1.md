# Handoff: AC1/AC2 landed; the Phase 2 generator is built and verified; one §2 stop (AD1)

**Responds to:** the AC1–AC2 rulings reply ("write `gen_models.py`, no further stop until Stop B")
**Branch:** `mc-realism` @ `b71d01c`, pushed. `tools/gen_models.py` written, **not committed**.
**Date:** 2026-09-19
**Status:** The generator is written and passes every acceptance gate except one, which is a §2
stop I could not have foreseen from the contract: **four lines in the authored `.lib` reference
parameters Phase 2 deletes, and the model has no variable to replace them with.**

---

## 1. AC1 / AC2 landed (`b71d01c`)

`_KPRD_sharing` removed; `U0` and `RD` are independent draws, recorded with the physical reason
(separate implants) and **not** the reasoning I gave you. `σ(KP) = 0` implemented for the five
drift-dominated devices by the measured `U0`-slope < 0.4 criterion, per device rather than per
class. The five re-measured: `U0` leaves each direction (3 terms → 2), predicted Idsat swing moves
−0.12 to −0.44 points. `corners.json` rebuilt, `--check` green.

**Your correction is recorded and I have not repeated the error.** The z-ratios are ratios of
measured sensitivities from the worst-case-direction construction; they say nothing about process
covariance. Nothing in the docs claims the measurement disproved signed sharing.

**One result worth keeping.** Removing `U0` from five groups changed **no preset distance at all**
— every one identical to four decimals. That surprised me enough to chase it as a suspected defect
through three wrong explanations. It is correct by construction: each per-group vector is
renormalised to exactly 3σ, so dropping a lever redistributes the same length onto the survivors.
The five dropped `U0` components summed to 1.918577 in squares; the surviving `RDSW`/`VTH`
components gained **+1.918578**. `corners.json`'s own `_meta` already said
`single_group_distance: 3.0`, which predicts this.

## 2. The generator

`tools/gen_models.py` is a **line transform**, not a rebuild. The `.inc` carries 918 deterministic
card lines, 19 in-card comments, 32 preamble comments, 52 `TC_*` tempco params and 4 control params
that no statistical model describes. Regenerating those from JSON would re-author correct content
and make `--check` byte-compare meaningless, so the tool rewrites only what the model owns.

| section | action | count |
|---|---|---|
| `_isXX` selectors | removed | 5 |
| `P_*` params | removed | 186 |
| `Z_*` draws | **added** | 117 |
| `c_<GROUP>` params | **added** | 40 |
| `<KIND>_<DEV>_STAT` | rewritten | 52 |
| card lines carrying a selector or `P_` draw | rewritten | 143 |
| card lines wrapping a `_STAT` in a tempco | passed through | 39 |
| `pclm` (corner-only, no variable) | collapsed to TT | 6 |

`Z_*` resolution is one expression per variable, as §1.1 specifies:

```
.param Z_VTH_NMOS50={((case==-1) ? (per-group c_ terms) : (preset terms)) + PROC_ON*AGAUSS(0,1,1)}
```

`case = -1` resolves `c_<GROUP>` as 0 → 0, 1 → +z_fast, 2 → −z_fast, since `z_slow = −z_fast` by
construction and only `z_fast` is stored. Per AC2, **corners are not generated here** —
`build_corners.py` remains the sole producer.

## 3. Verification

| gate | result |
|---|---|
| ngspice parses a ternary in a `.param` | **yes** — verified by reading it back through a resistance at case 1 / 2 / −1: 900 / 1100 / 1250 Ω, exactly as predicted |
| **`case 0` reproduces the current file** | **exact to 12 significant digits**, all 36 working devices |
| surviving `_isXX` | **0** |
| surviving `P_*` draws | **0** (1 grep hit is prose in a section comment) |
| dangling `Z_*` | **none** |
| `--check` before the write | reports stale, **exit 1** — correct CI-gate behaviour |

`case 0` matching exactly is the B1 "`Z = 0` reproduces TT" test: at preset 0 every `Z` is 0, so
`TT + σ·0 = TT`.

### 3.1 Movers, 36 devices × case 0–4 (delta generated vs current)

| class | case 1 | case 2 |
|---|---|---|
| 1.8 V CMOS | −20 to −22 % | +28 to +32 % |
| 3.3 V CMOS | −14 to −16 % | +17 to +21 % |
| 5 V CMOS | −11 to −13 % | +14 to +17 % |
| 12 V CMOS | −9 to −11 % | +11 to +14 % |
| LDMOS 20–60 V | −1 to −6 % | +2 to +7 % |
| **LDMOS 80–200 V** | **+1 to +5 %** | **−0.1 to −3 %** |
| resistors | −10 % | +12 % |
| capacitors | −2.9 % | +3.1 % |
| diodes | −5 to −15 % | +6 to +20 % |

The magnitude falls monotonically with voltage class and then **reverses sign** at 120–200 V, which
is where `RDSW` dominates the direction and `σ(KP) = 0` applies. That ordering is the σ changes
landed since Stop A′ showing through, and it is the pre-registered "all values move".

### 3.2 Two behaviour changes that are corrections, not regressions

- **`pclm` collapses to TT** on six cards, removing a ±2.72 % (n) / ±3.04 % (p) FF–SS spread on
  output conductance. Authorised: `dependent_parameters.pclm` is `held_at_TT` — "no corner or
  spread data; affects output conductance, not the corner metric".
- **DNMOS20 loses its FS/SF corner values** (−10.0 % / +11.2 %). It appears in **no** FS/SF preset —
  only 1, 2, 5, 6, 13–16 — yet the old card carried hand-written `_isFS`/`_isSF` coefficients
  (`VTO` −1.67111 / −1.51111). The old file was asserting corner behaviour with no basis in the
  preset table; the generated TT is what `corners.json` actually says.

## 4. AD1 — §2 stop: the BJT `BVCBO` has no model variable

`autohv_bicmos180_case.lib` lines 409/418/427/436 define, inside each BJT wrapper:

```
.param BVCBO={((14*_isTT + 13.3*_isFF + 14.7*_isSS + 13.3*_isFS + 14.7*_isSF))*(1+P_DBV_NPN_LV)}
```

Phase 2 deletes both `_isXX` and `P_*` from the `.inc`, so all four BJT wrappers fail to elaborate:
`Undefined parameter [_istt]` → `Undefined parameter [bvcbo]` → fatal. These are the **only** four
such lines in the whole `.lib`; nothing else there references a selector or a `P_` draw.

**It is not a rename.** There is no `BV_<bjt>` variable anywhere in `stat_model.json` —
`_BV_template` covers the 13 VDMOS only, and the four BJTs own just `VBE`, `BF` and `RPAR`.
Meanwhile `dependent_parameters.BVCBO` already reads `follows: BV_<device>, coefficient 1.0`,
presuming a variable that was never authored. So this is a gap in the model, surfaced by the
generator rather than caused by it.

**Three facts that frame the choice:**

- Each `BVCBO` carries a **−10.0 % FF–SS spread**, identical on all four devices — a declared
  ladder, not a fitted one.
- `BVCBO` feeds only the `Bavl` avalanche source, negligible until `|V(ci,b)|` nears breakdown.
- The VDMOS `BV_*` are **excluded from every measured direction** for exactly this reason:
  "breakdown has no lever on drain current at the bench bias". A BJT `BV` would behave the same —
  carried in the `.inc`, contributing 0 to every corner vector.

**Recommendation: author `BV_<bjt>` by extending `_BV_template.devices` with the four BJTs** at the
existing 5 % 3σ, let the generator emit `Z_BV_<bjt>`, and rewrite the four `.lib` lines as
`{TT*exp(σ*Z_BV_<bjt>)}`. It matches what the VDMOS already do, satisfies
`dependent_parameters.BVCBO` as written, and is behaviourally inert at every corner. The
alternative — collapsing `BVCBO` to TT like `pclm` — silently deletes a declared −10 % breakdown
ladder, which matters to anything exercising avalanche.

**Why this is a stop and not a §1 decision:** it authors new statistical variables, and it edits
the authored `.lib`, which is Phase 3 territory.

## 5. What I got wrong building this

The generator needed five fixes, every one found by **running** it rather than reading it:

| fault | symptom | cause |
|---|---|---|
| `tt_of` required two open parens | `pclm` lines passed through with selectors intact | `pclm` wraps its `_isTT` in **one** paren; every other expression uses two |
| silent passthrough on `tt is None` | unparseable output, no error at generation time | the fallback emitted broken content instead of failing; now raises |
| `Z_*` declared from `corners.json` only | 20 dangling references (`BV_*`, `CJ_*`, `JS_MOS`) | those are pruned from the directions for having no lever, but the model still owns their card parameters |
| **`"P_" in expr` as a substring test** | the 13 `kp` tempco wrappers misrouted and raised | `P_` occurs *inside* `KP_<DEV>_STAT` and `TC_KP_<DEV>` — needed `\bP_[A-Z]` |
| probe regex matched any `=` | every "current" column read `27.0` | it was matching `TEMP = 27.000000` from the banner |

And one judgement error worth recording: when the four BJT decks first failed I twice concluded it
was **my harness, not the generator**, and moved on. It was the generator — or rather the `.lib`
gap the generator exposes. I only found it after printing the raw ngspice output instead of
filtering it, which I should have done on the first failure rather than the fourth.

## 6. State

`b71d01c` pushed, tree clean apart from `tools/gen_models.py`, which is written and unstaged. The
live `.inc` is untouched. On an AD1 ruling: author the variable, regenerate, confirm `--check`
green, confirm a σ edit turns it red, run the 40-device table including the four BJTs, and commit
Phase 2. Then the naming pass, then Phase 3.
