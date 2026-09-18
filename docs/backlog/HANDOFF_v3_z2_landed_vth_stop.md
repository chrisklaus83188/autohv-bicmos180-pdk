# Handoff: Z2 landed; U1 ready; σ(VTH) regeneration is a §2 stop

**Responds to:** the AA1–AA3 rulings reply and the standing autonomy rule
**Branch:** `mc-realism` @ `1e3998a`, pushed
**Date:** 2026-09-18
**Status:** Z2 applied and committed as reduced. U1 is derived and ready. **U5 stops under §2** —
the regenerated σ(VTH) misses the plausibility band by 6–20× and would move corner Vth by ~70 mV,
which is three separate §2 triggers. Work is prepared; the decision needs one word.

---

## 1. Decisions taken under §1

| decision | basis | recorded in |
|---|---|---|
| Z2 applied as reduced | AA1 | `1e3998a` |
| `ksubthres` held | ngspice VDMOS has no oxide (`unrecognized parameter (tox)`); bisection returned carded values to ±0.5 % | CHANGELOG |
| `VTO` held | implant-set, not oxide-following | D2, CHANGELOG |
| VDMOS `A_VT` held; external entry removed | width-normalised (`mtot`), not area-normalised | `stat-model.md` §3.2 |
| `rd`/`rs`/`BV` held | drift-region, excluded by Z2 | CHANGELOG |
| Surviving `_RESISTORS` / `_CAPACITORS` reference names left in place | AA2 named only the VDMOS `A_VT`; those two carry their own rulings and are scoped to Z3(b) | commit message |
| Duplicate `## D2` heading collapsed | my Z2 edit inserted a second heading instead of retitling, leaving two D2 blocks with conflicting statuses | working tree |
| U1 binary sharing prepared | nothing in `tools/` reads `master`/`rho`; `build_corners.py` already computes a plain Euclidean norm | generator, dry-run |

## 2. Z2 landed (`1e3998a`)

Scaled by 13/11 = 1.1818 — 13 `KP_*_STAT` parameters and 52 card lines (`kp`, `cgs`, `cgdmax`,
`cgdmin`, `theta`). Measured on all thirteen cards at W = 10 µm, Vov = 3 V:

| quantity | pre-registered | **measured** |
|---|---|---|
| Idsat | +≈18 % | **+4.1 … +10.4 %** |
| Ron | −5 … −10 % | **−1.3 … −8.9 %** |
| subthreshold slope | — | **−0.2 mV/dec** (unchanged) |

`kp` ×1.1818 and `theta` ×1.1818 push opposite ways, so roughly half the drive gain cancels. The
slope result confirms live that holding `ksubthres` was correct.

Supporting: `C_ox` at 13 nm computes to 2.6563 fF/µm², matching the phase-3 stated 2.66, so
inverting `kp` recovers the declared mobilities 400 / 130 cm²/Vs exactly. Body doping re-derived at
11 nm with `V_FB` **solved** rather than assumed: `N_a` 1.80e17–2.83e17 cm⁻³,
`V_FB` −0.710…−0.745 (N) / +0.696…+0.724 (P). Recorded in `stat-model.md` §1.2.

External references in `stat_model.json`: **28 → 19** across Z1 and Z2.

## 3. U1 — ready, no computed output changes

`master_variables` (7 masters, 42 `master` fields, ρ = 0.6–0.7, all `source: declared`) is **inert
in code**: `grep master|rho` over `tools/*.py` and the regression scripts returns nothing, and
`build_corners.py` computes distance as a plain Euclidean norm of summed `z_fast`.

Removing it also resolves a live contradiction — `master_variables` states distance is "Mahalanobis
under the resulting covariance", while `corner_construction` states "Euclidean, because the global
variables are independent unit normals". `corners.json` was built under the latter. Its
`_grounding` field also cites the reference's §8.3 correlation matrices, so removing the block
retires another external reference.

**Correction to my last handoff:** I said U1 had to land before the re-measure or corner distances
would shift. That was wrong — nothing reads the ρ layer, so it changes no number.

## 4. §2 stop — σ(VTH) regeneration

### 4.1 What I derived

`VTH_<device>` is a **wafer-level** additive shift on `vth0`/`VTO`, not the Pelgrom local term
(that is `A_VT`, landed in Z1), so it carries no `1/√(W·L)`. The implant-driven part:

> `σ(Vth) = k1·√(2φ_F)·(σ_dose/2)·0.85`

`k1` because the doping-dependent part of Vth is the depletion-charge term and goes as `√N_a`;
`/2` from the square root; `0.85` is U3's automotive tightening factor. The oxide contribution is
carried separately by `TOX_*` and is not double-counted. VDMOS `k1` comes from each card's own
measured slope at 11 nm, since those cards carry no `k1`. Dose tolerance declared at 3 % 3σ,
the same `literature:0.18um-BCD-class` tier as `TOX_*`.

### 4.2 The result, against the comparable-class check

| device | today | **dose-only** | comparable | today/cmp | **mine/cmp** |
|---|---|---|---|---|---|
| NMOS33 / PMOS33 | 38.0 mV | **2.5 / 2.8** | 41–56 mV | 0.78 | **0.05 / 0.06** |
| NMOS50 / PMOS50 | 45.0 mV | **2.7 / 3.1** | 16–22 mV | 2.37 | **0.14 / 0.16** |
| NDMOS200 | 43.3 mV | **4.5** | 20–90 mV | 0.79 | **0.08** |
| NMOS18 | 29.3 mV | **2.3** | *none available* | — | — |
| NMOS12 | 50.0 mV | **6.0** | *none available* | — | — |

All 21 devices fall outside the ruled 0.5–2.0× band, so per §5.2 this is **reported, not clamped**.

**U5's premise is confirmed but narrower than stated.** Today's σ is 2.37× the comparable at 5 V —
"several times too wide" holds there — but it is 0.78× at 3.3 V and 0.79× for LDMOS, i.e. already
about right for those classes. The spec-window conflation inflated the 5 V class specifically.

### 4.3 Why this is a §2 stop, not a §1 decision

Three triggers, any one of which would be sufficient:

| trigger | evidence |
|---|---|
| designer-visible in an ordinary simulation | slow-corner Vth: NMOS50 **−73.5 → −4.4 mV**, NMOS18 **−70.2 → −5.5 mV**, NMOS33 −59.5 → −3.9 mV |
| changes character of the corners | `VTH` carries **63.8 %** of NMOS18's corner direction and **72.5 %** of PMOS18's; collapsing it re-weights every LV corner and forces the U0 solve to absorb the difference |
| plausibility miss > 2× with no explanation | 6–20× too narrow, on all 21 devices |

### 4.4 What is missing, physically

Dose-only is 0.05–0.16× of comparable; today's spec-window value is 0.78–2.37×. The truth is
between them, and the term I omitted is **flat-band / fixed-charge variation**, which no source in
the repo sizes. Backing it out of the comparables:

| target | implied σ(V_FB) |
|---|---|
| 5 V at 16 / 19 / 22 mV | 15.8 / 18.8 / 21.8 mV |
| 3.3 V at 41 / 48 / 56 mV | 40.9 / 48.4 / 55.9 mV |
| LDMOS at 20 / 55 / 90 mV | 19.5 / 54.8 / 89.9 mV |

Note what that says: to reach the comparables, **flat-band would have to dominate Vth spread
almost entirely** — the dose term contributes under 3 % of the variance. That is a strong claim and
needs its own source rather than my assumption.

## 5. The decision I need

**Recommendation: split `VTH_<device>` into two causes** — the derived dose term plus an explicit
`VFB_<class>` flat-band/fixed-charge variable, added in quadrature.

- It is the physically honest structure, and §5.3 already endorses adding variables we lack.
- It keeps the dose term *derived* rather than fitted.
- It isolates the undetermined quantity in one named place with its own error bar, instead of
  hiding it inside a tuned dose number.

The alternative I am **not** proposing: raising `σ_dose` from 3 % to ~25 % 3σ to hit the band. That
is fitting a free parameter while calling it a derivation — the same thing I declined to do for
`c_RDF` in Z1.

**AB1 — approve the split?** And if so, what basis for σ(V_FB): a literature value you can cite, or
"use the comparable-class magnitude as the target and back out σ(V_FB)" (which lands 5 V at
16–22 mV and 3.3 V at 41–56 mV, but makes flat-band dominant by construction)?

**AB2 — the 1.8 V and 12 V classes have no comparable magnitude at all.** I initially hard-coded
bands for them by copying the 3.3 V row and spanning two unrelated rows; that was invented and is
withdrawn. They should report "no comparable magnitude" rather than a fabricated pass/fail. Confirm
that is what you want, or give me a basis for those two classes.

## 6. Two corrections of mine

- **Invented plausibility bands.** I hard-coded `18 → (41, 56)` by copying the 3.3 V row and
  `12 → (16, 56)` by spanning two unrelated rows. The source table has no 1.8 V and no 12 V entry.
  Withdrawn; see AB2.
- **U1 ordering.** I said it had to land before the re-measure or distances would shift. Nothing
  reads the ρ layer, so it changes no number.

## 7. State and queue

Nothing from §4 is applied — `stat_model.json` is untouched by the VTH work. The only uncommitted
change is the D2 heading fix. Behind AB1: U2 (per-device Idsat σ replacing the externally sourced
class bands), the plausibility-boolean script, re-measure all 40 directions, rebuild `corners.json`,
**Stop A′**. Then the naming pass.
