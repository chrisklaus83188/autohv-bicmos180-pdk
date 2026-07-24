# Audit vs Measurement — where phase 2 overturns or refines phase 1

**Rule applied throughout: where a measurement contradicts the static audit, the measurement wins.**
Phase 1 ([`model-realism-audit.md`](model-realism-audit.md)) was reading plus arithmetic and had to
assume answers to several questions. Phase 2 measured them. This document lists every place the two
disagree, with the corrected anchor entry spelled out so [`anchor-values.json`](anchor-values.json)
can be amended in one pass.

**Nothing here has been applied.** The anchor JSON is unchanged; the maintainer applies these
alongside the open decisions.

Sources: [`characterization-scorecard.md`](characterization-scorecard.md) ·
`pdk_validation/characterization/results/characterization-results.json` ·
`pdk_validation/characterization/experiments/README.md`.
Measured on ngspice-45 (KLU), 548 measurements, 400 s wall.

---

## 0. Summary

| # | item | phase-1 verdict | phase-2 measurement | outcome |
|---|---|---|---|---|
| 1 | NDMOS200 sub-Boltzmann | `n = 1.01`, "unphysical, below the Boltzmann floor" | `S = 70.7 mV/dec`, **`n = 1.19`** | **OVERTURNED — strike from worklist** |
| 2 | §2.2 implied-width table | divided by `rd+rs` | series R is only **30–39 %** of Ron | **MISATTRIBUTED — reissue table** |
| 3 | fix #2 scope | 13 per-card re-derivations | residual flattens 12.7× → **5.5×** under the theta-implied oxide ladder | **REFINED — ~6 numbers, not 13** |
| 4 | `kp` convention | assumed `(kp/2)·Vov²` | `A/kp = 0.4999999986` | **CONFIRMED — no anchor change** |
| 5 | PNP avalanche | not examined | **dead code on both PNPs** | **NEW — blocks-realism** |
| 6 | BSIM3 `vth_tempco` | not examined | BSIM3 default `kt1`, identical on all 8 | **NEW — distorts-results** |
| 7 | VDMOS `rd_tempco` | `TC_*` self-flagged CALIBRATE | 2.3–2.7× the anchor band, 13/13 | **NEW + definition gap** |
| 8 | `BVCBO` | 14 V (`.param`) | **11.77 V** — `Bavl` feedback runs away at M = 2 | **NEW** |
| 9 | zener `bv` tempco | "expect identically flat 0.000" | **sign-flips with measurement current** | **REFINED — stronger evidence** |
| 10 | cap reconciliation (§6.3 fork) | 1.6–2.1× gap unexplained | **bias-dependent ⇒ not a rescale**; source deck is inoperable | **RESOLVED as far as possible** |
| 11 | VDMOS `cjo` | "correct on every card, no action" | mild slope; 4 of 13 just outside band | **REFINED** |
| 12 | F1, F2, F3, F4, F6, F7, F-VD3, F-BJT1 | predicted | all reproduced, several to 3 significant figures | **CONFIRMED** |

**Confirmation quality worth noting.** F2's predicted cgs excess was 48.2× / 4.6× / 3.3× for
NDMOS20 / NDMOS200 / PDMOS200; measured 48.0× / 4.62× / 3.27×. The BV corner table matches
`3a81be0` to 0.04 %. F4's predicted 3.12 MHz measured 2.97 MHz. The static audit's arithmetic was
sound where its assumptions held — every discrepancy below traces to an *assumption*, not to an
arithmetic error.

---

## 1. OVERTURNED — NDMOS200 is not sub-Boltzmann (D2)

**Phase 1 §2.8** read `ksubthres` as mV/decade directly, giving NDMOS200 `n = 1.01` and the
conclusion *"unphysical — it says the depletion capacitance is zero, i.e. a perfect gate."*

**Measured:** `S = 1155.6 · ksubthres + 1.21`, R² = 0.9998 across all 13 cards. `ksubthres` is a
**per-decade** slope inflated by **1.17×** — the natural-log reading is excluded (50 % off). The
gm/Id ceiling agrees independently on all 13.

NDMOS200 swings at **70.7 mV/dec**, `n = 1.19`. **No card in the family is sub-Boltzmann.**

**But the structural half of §2.8 survives.** The ladder still slopes the wrong way with voltage
class (measured −0.00356 per volt of class vs phase 1's −0.00310) where `n = 1 + C_dep/Cox` demands
it rise. Multiplying a ladder by a near-constant cannot flip its slope, and it does not.

> **Anchor amendment 1.** No band changes — measured swings land where the anchor already expected.
> Add next to every VDMOS `subthreshold_swing` entry:
> `"ksubthres_to_S_mapping": "S_mV_per_dec = 1.171 * 1000 * ksubthres (D2, R^2=0.9998, 13 cards)"`.
> **Worklist:** strike fix #11's "NDMOS200 `n = 1.01` is below the Boltzmann floor" clause; keep the
> ladder-slope clause at unchanged severity. Any re-laddering must target **measured S**, not
> `1000·ksubthres` — a card wanting `S = 90 mV/dec` needs `ksubthres ≈ 0.0769`, not `0.090`.
> **Code:** `families/vdmos.py` `_do_idvg` carries the wording *"the card's ksubthres IS S in V/dec
> by construction"* — off by 17 %, should be corrected.

---

## 2. MISATTRIBUTED — the §2.2 implied-width table divided by the wrong resistance (D3)

**Phase 1 §2.2** took the card's whole on-resistance to be `rd + rs`.

**Measured:** the decomposition validates to 0.03 % / 0.11 % against the carded `rd+rs`, and series
resistance is only **30.3 %** (NDMOS20) and **39.2 %** (NDMOS200) of total Ron. **The channel
dominates**, which §2.2 did not allow for.

Two consequences pulling opposite ways:

- **The `kp` route is clean.** Removing `rd`/`rs` lifts Idsat by 1.24× / 1.41× against implied-width
  gaps of 3649× / 287× — series resistance explains **under 0.2 %** of F1's `kp` half. This closes
  off "maybe it's just series resistance."
- **The Ron route was overstated by 3.30× / 2.55×.** Re-cast on total measured Ron, the implied
  widths become 288× / 911×, and the kp-vs-Ron disagreement moves from 2.43× / 0.08× to
  **12.66× / 0.31×** — the family swing *widens* from 30× to 40×. The two-independent-slips
  conclusion of §2.5 is strengthened, not weakened.

**Channel-only floor: NDMOS20 1.610 Ω·µm, NDMOS200 27.22 Ω·µm** (Vov = 4 V, Vds = 0.1 V).

> **Anchor amendment 2.** Add to each VDMOS `ron_times_w` entry:
> `"channel_only_floor_ohm_um"` (1.610 / 27.22 for the two measured; others need the same run) with
> basis *"D3: total Ron*W can never fall below this — it is the channel resistance the same kp sets."*
> **Worklist ordering constraint:** the floor is itself set by the defective `kp`, so **fixing `kp`
> downward raises it**. Fix #2 and fix #3 are coupled through this floor even though the defects are
> independent. **Re-derive `kp` before `rd`/`rs`**, and check any `rd`/`rs` divisor against the floor —
> a divisor driving total Ron·W below it is arithmetically impossible, not merely optimistic.

---

## 3. REFINED — fix #2 is about six numbers, not thirteen (D4)

**Phase 1 §2.1** concluded `kp` carries a sloped error (287×–5213×) needing 13 per-card
re-derivations — but assumed `tox = 30 nm` flat, while its own §2.7 theta analysis implied `tox`
rising with class.

**Measured** (all 13 cards, `rd = rs ≈ 0` so series resistance cannot masquerade as mobility
degradation; all fits R² > 0.99986; hypothesis (a) reproduces §2.1's published table to **0.11 %**):

| grouping | (a) `tox` = 30 nm flat | (b) theta-implied ladder | flattening |
|---|---|---|---|
| all 13 | 18.2× | **7.1×** | 2.6× |
| **n-channel** | **12.7×** | **5.5×** | **2.3×** |
| p-channel | 14.8× | 6.7× | 2.2× |

Mechanically: under (b), `Cox ∝ theta` so `W ∝ kp/theta`; `kp` falls 12.7× across the n-channel
family while `theta` falls 2.2×. **The sloped residual is real but mostly an artifact of the flat-tox
assumption.** The spread metric is independent of the empirical constant's 3× band — it cancels in a
max/min ratio — so the *flatness* verdict does not inherit that uncertainty; only the absolute widths do.

> **Anchor amendment 3.** Add a `_vdmos_tox_conditional` block alongside `_vdmos_kp_conditional`,
> recording: the two hypotheses, their measured residual spreads (12.7× flat vs 5.5× laddered,
> n-channel), and the theta-implied `tox` band per class. This is a **second, orthogonal fork** to the
> existing 10 µm-cell-vs-power-die one: that fork sets the *magnitude* of the `kp` fix, this one sets
> its *shape*.
> **Recommendation:** one divisor + a per-class trim — **six numbers**, divisor from the family
> geometric mean. Thirteen independent derivations are not justified by a 5.5× spread (the same order
> as the 2.8× §2.2 was willing to call "roughly flat").
> **⚠ This does not decide the oxide ladder.** The theta-implied ladder is better supported — derived
> from a card parameter, monotonic, correctly ordered — but is in tension with the carded
> `vto = 1.00–1.31 V`, which for LDMOS body doping suggests a *thinner* oxide. That is a
> process-declaration question, not a simulation one. **Do not apply fix #2 in either scoping until
> `tox` is declared per class.**

---

## 4. CONFIRMED — the `kp/2` convention (D1)

Fitted prefactor `A = 0.11000000` against card `kp = 0.22`; **`A/kp = 0.4999999986`**, residual
2.8e-7. ngspice-45 VDMOS saturation is `Id = (kp/2)·Vov²`; `kp` is a transconductance parameter, not
the saturation prefactor. The uncorrected fit (0.4816) lands on the same side of the fork, so the
verdict does not depend on the theta/lambda correction.

> **Anchor amendment 4.** No values change — both `_vdmos_kp_conditional` routes already assume this
> (`µ·Cox·(W/L)` *is* the SPICE level-1 `KP` definition; `kp_from_idsat_density` states
> `kp = 2·Id/Vov²` outright). Add `"convention": "Id = (kp/2)*Vov^2, verified by D1"` for the record.
> F1 survives intact — D1 only removes the possibility that a factor of 2 was bookkeeping.

---

## 5. NEW — the PNP avalanche branch is dead code

**Not examined in phase 1.** Phase 1 §4.1 checked the BVCEO/BVCBO *ratios* and found all four in
band, and §7 called the `Bavl` construction "well-built" — but never checked whether it *executes*
on a p-type device.

`Bavl` uses `min(max(V(ci,b)/BVCBO, 0), 0.997)` with a positive `BVCBO`. **On a PNP the collector
sits below the base**, so `V(ci,b) < 0`, the `max(…, 0)` zeroes it, and the branch is inert.

**Measured: PNP_LAT sustains −200 V at 0.19 nA against a declared `BVCBO` of 18 V.** Same for
PNP_HV. Both PNPs have **no breakdown model at all**. This is the source of 4 of the 14 harness
errors (BVCEO/BVCBO unmeasurable on both PNPs).

> **Anchor amendment 5.** Mark `bvcbo` and `bvceo_implied` on PNP_LAT and PNP_HV as
> `"conditional_on": "PNP avalanche branch is inert — no breakdown is modelled (phase-2 discovery)"`
> so phase 3 reports them blocked rather than failing to measure.
> **Worklist:** add a new fix — *"make `Bavl` polarity-aware, e.g. `abs(V(ci,b))/BVCBO`, so the PNPs
> get the breakdown model the NPNs have."* Severity **blocks-realism**: a designer sees an
> HV-tolerant PNP that does not exist, and in an automotive PDK that is the unsafe direction.

---

## 6. NEW — BSIM3 `vth_tempco` is an unset-parameter default

**Measured: −0.3665 mV/°C, byte-identical on all eight BSIM3 devices across every voltage class.**
Anchor band is −2.0 … −1.0, so all eight fail ~3–4× low.

A class-independent answer is the signature of an unset parameter: none of the eight cards defines
`kt1`, `kt2` or `ute`, so BSIM3 falls back to `kt1 = −0.11 V` and the result is arithmetic, not
physics.

Corollary: `mobility_tempco_exponent` is in the anchor for all eight but was deliberately **not
measured** — with `ute` unset it returns the BSIM3 default −1.5, which sits exactly on the anchor
target. That would be a **false pass**, and is worse than a missing measurement.

> **Anchor amendment 6.** Keep the `vth_tempco` band; add
> `"note": "PDK cards define no kt1/kt2 — measured value is the BSIM3 default, class-independent"`.
> For `mobility_tempco_exponent` add `"conditional_on": "ute unset on all 8 cards — measuring it
> returns the simulator default and would pass falsely"`.
> **Worklist:** new fix — *"add `kt1`/`kt2`/`ute` to the eight BSIM3 cards"*, severity
> distorts-results, effort low. Nothing in the PDK currently has a real MOS temperature model.

---

## 7. NEW — VDMOS `rd_tempco` fails 13/13, part definition and part physics

**Measured 14 580 – 24 240 ppm/°C** against an anchor band of 4000–9000. Every card, 2.3–2.7×.

Two causes, and they should be separated:

1. **Definition gap.** The anchor's basis says *"drift resistance rises with T"* but the harness
   measures **total Ron·W**. Per D3 the channel is 60–70 % of Ron, and `kp` falls with T as well, so
   the total tempco compounds two mechanisms where the anchor bands one.
2. **Real, on top of that.** Even allowing for the definition, the carded `TC_RD` of 0.005–0.009 /°C
   yields ~9000 ppm/°C at the 200 V end by itself — the top of the band — and the `TC_*` set is
   self-flagged `CALIBRATE`.

> **Anchor amendment 7.** Split the FoM. Keep `rd_tempco` (band 4000–9000, `[physics]`, drift only)
> and require it to be measured with `rd`/`rs` isolated D3-style. Add a new
> `ron_tempco` (total, `[industry]`, proposed band **8000–18000 ppm/°C**, basis *"channel + drift in
> series; channel is 60–70 % of Ron per D3"*) and point the harness at that. As it stands the harness
> measures a quantity the anchor does not define, and 13 hard-fails are partly an artifact of that.

---

## 8. NEW — `BVCBO` reads 16 % under its own `.param`

**Measured NPN_LV `BVCBO` = 11.77 V against `.param BVCBO = 14`.** Mechanism: `Bavl` feeds back on
the **external** sense current, closing a loop that runs away at M = 2 rather than M → ∞. Solving
`1/(1−x⁴) − 1 = 1` gives `x = 0.841`, and `0.841 × 14 = 11.77` — exact.

Related: **`bvceo_implied` fails high** (NPN_LV 7.465 V vs band 3.5–7.0; NPN_HV 24.83 vs 11.25–22.5)
because the brief's 1 µA criterion lands on the soft knee. The ladder falls 7.46 → 6.24 → 5.18 as the
criterion rises, and the **sustaining voltage is 5.17 V — in band**. Turnover peak is 11.86 V with
6.7 V of snapback.

> **Anchor amendment 8.** For `bvcbo`, add
> `"note": "the Bavl feedback runs away at M=2, not M→∞, so measured BVCBO is 0.841x the .param"`
> and widen the band to include it, or state the criterion. For `bvceo_implied`, **specify the
> criterion in the basis** — sustaining voltage, not a 1 µA compliance point — and keep the band. As
> written the anchor and the harness measure different quantities.

---

## 9. REFINED — the zener tempco evidence is stronger than "flat"

Phase 1 §4.5 predicted an identically flat 0.000 mV/°C.

**Measured: DZ_24 reads −0.73 mV/°C at a 1 µA criterion and +0.46 mV/°C at 1 mA.** `bv` itself is
temperature-invariant; what moves is the offset between `bv` and the criterion, because the breakdown
branch carries `nbv·Vt` in its exponent.

**A physical tempco cannot flip sign with measurement current.** This is a sharper demonstration of
the missing `tbv1`/`tbv2` than a flat zero would have been.

Related: **DZ_5V6 `bv` measures 5.243 V** against a band of 5.32–5.88 (card `bv = 5.6`) — the same
soft-knee criterion effect.

> **Anchor amendment 9.** Add to each zener `bv` and `bv_tempco`:
> `"measurement_criterion": "1 uA — note the nbv*Vt soft knee puts the measured bv below the card
> value and makes the apparent tempco criterion-dependent (phase-2 finding)"`. Keep the tempco band;
> the finding stands and is better evidenced.

---

## 10. RESOLVED as far as the decks allow — the §6.3 cap-reconciliation fork

Phase 1 §6.3 recorded an unexplained 1.6–2.1× gap between `HANDOFF_vdmos_caps.md`'s pre-fix numbers
(172 / 52 / 18.7 pF) and the CHANGELOG's (105 / 29.5 / 8.84 pF) on a nominally identical deck.

**Three measured findings:**

1. **The two decks are methodologically identical** — both drive the drain with a 1 V AC source, both
   hold the gate at DC 0 with no AC component, both read `i(VB)`, both divide by 2πf. Run today they
   agree to **0.0000 %** at all four biases.
2. **Today reproduces the CHANGELOG exactly** (105 / 29.5 / 11.4 / 8.84 fF). Since VDMOS terminal C is
   linear in the cap card parameters, the CHANGELOG's pre-fix column is exactly 1000× these —
   self-consistent. **The handoff's numbers are not reachable from any uniform rescale**, and
   critically the handoff/CHANGELOG ratio is **not flat**: it rises 1.64 → 1.76 → 2.12 with drain
   bias. A different W/M/mtot would scale every point equally; a bias-dependent ratio can only come
   from a different split between the bias-independent caps (`cgs`, `cgd`) and the bias-dependent
   junction cap (`cjo`). **Most likely the handoff measured an earlier card revision.**
3. **The handoff's Repro-1 as published cannot have produced its own numbers.** It contains
   `echo "Vds=$vb" ; print cdrain` — and `;` is a **comment** character in the ngspice control
   language, so `print cdrain` never executes. Run verbatim it emits zero `cdrain` lines. Both the
   verbatim deck and a fixed version are committed under `decks/vdmos/` so this is checkable.

> **No anchor change.** This closes an inventory item: the gap is **not reconcilable from the decks**,
> and the published repro is inoperable. Worth a line in the handoff archive so a future reader does
> not re-derive this.

---

## 11. REFINED — VDMOS `cjo` has a mild slope after all

Phase 1 §2.4 found `cjo` in band on every card (0.25×–2.9×) and called it *"the control that shows
the cgs slope is real."*

**Measured: 4 of 13 fall just outside** — NDMOS20 132 fF (band 19.9–124.2) and PDMOS20 141.4
(20.8–129.8) slightly **high**; NDMOS200 20.74 (band 28.6–178.5) and PDMOS200 16.97 (28.3–176.6)
slightly **low**. So `cjo` carries a weak version of the same voltage-class slope as `cgs` — roughly
2.7× at 20 V down to 0.3× at 200 V, against `cgs`'s 48× → 3.3×.

The control still holds: `cjo`'s slope is **~15× weaker** than `cgs`'s, so the F2 conclusion is
unaffected. But `cjo` is not perfectly clean and the phase-1 "no action" should become "low priority".

> **Anchor amendment 10.** Widen the `cjo_per_cell` bands to ±3× of target (from the present
> ~0.4×–2.5×) to reflect genuine assumption uncertainty in `N_d` and pitch, **or** accept the four
> failures as a real low-severity finding. Recommend the latter — the slope is systematic, not noise.

---

## 12. Method findings worth carrying into phase 3

Not model defects, but they change how future measurements should be made.

| # | finding | consequence |
|---|---|---|
| A | **ngspice keeps the FIRST definition of a model name** and silently discards later ones. Isolation copies cannot shadow a PDK card. | `char_lib.write_local_model` originally documented the opposite. Corrected; `experiments/exp_lib.py` renames the card and instantiates it raw, proving wrapper-equivalence rather than assuming it. **Anything relying on shadowing runs on stock cards while reporting otherwise.** |
| B | Exactly `rd=0`/`rs=0` will not converge on a VDMOS card (gmin and source stepping both fail). | Use `1e-9 Ω` — nine orders below the carded values, 1 nV at 1 A. |
| C | **The phase-C tran-ramp method under-reads capacitor bias dependence by exactly 10×.** The golden's `C(5)/C(0)−1` is 6.5e-5; an AC probe gives 6.494e-4, which is precisely the wrapper's `VCC1·5 + VCC2·25`. | The ramp under-integrates the behavioral `Cextra` branch. `run_passives.py`'s goldens are correct at V = 0 but understate VCC. Use an AC probe for voltage coefficients. |
| D | `print` truncates at 80 columns unless `set width=1000`, **silently dropping trailing vectors**. | Bit two family modules. |
| E | `.noise` accepts only a voltage source as input reference and **silently produces no plot** if that source lacks an `ac` spec. | — |
| F | `;` is a comment character in the ngspice control language. | Cause of finding 10.3. |
| G | `char_lib.mc_run`'s degeneracy check originally compared `round(v, 15)` — an absolute quantum that flags healthy farad-scale MC as degenerate. | Fixed to a relative comparison. Any future family reporting farads, coulombs or sub-fA currents would have hit it. |

---

## 13. What phase 2 confirmed without amendment

For completeness, so the amendments above are read in proportion:

- **F1** — Idsat density 311×–11 200× high, Ron·W 456×–1440× low, all 13 VDMOS.
- **F2** — cgs excess measured 48.0× / 4.62× / 3.27× against predicted 48.2× / 4.6× / 3.3×.
- **F3** — input-referred noise is pure 1/f across the entire 1 Hz–1 GHz sweep, top-decade log-log
  slope −1.00, **no floor at all**; corner extrapolates to ~1e27 Hz.
- **F4** — 2.97 MHz at 100 µA (predicted 3.12), and `af = 1.011–1.015`, `kf = 9.9e-13` recovered
  directly from the flicker coefficients by a fit-independent route.
- **F6** — `imag(i(Vb)) = 0.000000e+00` **exactly**. 100 % of junction capacitance absent, all 8.
- **F7** — RPOLY_HI `tc1 = +656 ppm/°C` measured, +8.89 % at 150 °C where physics demands negative.
- **F-VD3** — ladder A lands at 0.95–1.09× its anchor, ladder B at 0.32–0.33×. Clean separation.
- **F-BJT1** — NPN_LV fT is 200 MHz at 100 µA against a 3.54 GHz `tf` ceiling (predicted 265 MHz).
- **Passive matching** — 4.2×–11× optimistic, measured pair σ landing on the wrapper's own prediction
  within sampling noise, so the convention is not the explanation.
- **BV corners** — match the `3a81be0` audit table to 0.04 % at all five corners on both 200 V parts.
- **BV vs L** — flat to 0.0009 % over L = 5/8/12/16 µm, confirming the L knob is penalty-only.
- **AGAUSS convention** — no MC run degenerate; measured per-device σ(Vth) matches `X/3/√(W·L)` to
  2–4 % at N = 200. The mismatch machinery works correctly; only the magnitudes are wrong.
