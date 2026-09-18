# BSIM3 undeclared-default audit

Stop A deliverable, brief v3 Phase 1 §3.1 (added by the Phase 0 reply).

Every parameter a BSIM3 card does not declare takes the model's built-in default. Those defaults
are as much a part of the PDK as the fitted values, and until now none of them was reviewed. This
audit lists each audit-set parameter, whether the cards declare it, the default that is otherwise
live, and a keep-or-ground decision.

**Method.** Declared/undeclared status is parsed from the eight BSIM3 cards in
`autohv_bicmos180_case_models.inc`. Default values are read back **out of this ngspice build**
(`showmod` on an instantiated device), not quoted from a manual, so they are the values this PDK
actually simulates with. Narrow-width evidence is measured on NMOS50, L = 1 µm, Vgs = Vds = 5 V.

## 1. Summary

| | count |
|---|---|
| BSIM3 cards | 8 (NMOS/PMOS 18, 33, 50, 12) |
| audit-set parameters | 34 |
| declared in all 8 cards | 16 |
| **undeclared in all 8 cards — defaults live** | **18** |
| decisions: ground now | 3 (`k3`, `k3b`, `w0`) |
| decisions: keep default, reason recorded | 15 |

All eight cards declare an identical parameter set, so there is no per-device exception to track.

## 2. Declared in all eight cards — no audit action

`dvt0` `dvt1` `dvt2` `dwg` `dwb` `pdiblc1` `pdiblc2` `drout` `prwg` `prwb` `a0` `ags` `eta0`
`etab` `ute` `kt1`

These carry fitted values per card (e.g. NMOS50: `dvt0=1.8`, `dvt1=0.4`, `dvt2=-0.02`, `a0=1`,
`ags=0.18`, `ute=-1.2`, `kt1=-0.48`).

## 3. Undeclared in all eight cards — defaults live

| parameter | live default | what it does | decision |
|---|---|---|---|
| **`k3`** | **80** | narrow-width Vth shift | **ground — see §4** |
| **`k3b`** | **0** | body-bias term of `k3` | **ground with `k3`** |
| **`w0`** | **2.5e-6** | narrow-width characteristic width | **ground with `k3`** |
| `nlx` | 1.74e-7 | lateral non-uniform doping (short-channel Vth) | keep: L ≥ 0.18 µm here and `dvt0/1/2` are fitted; folding `nlx` in would double-count |
| `dvt0w` | 0 | small-width Vth, width-dependent | keep: term is inert at 0 |
| `dvt1w` | 5.3e6 | partner of `dvt0w` | keep: inert while `dvt0w = 0` |
| `dvt2w` | −0.032 | partner of `dvt0w` | keep: inert while `dvt0w = 0` |
| `keta` | −0.047 | bulk-charge body-effect coefficient | keep: default is the Berkeley fit; no ONC25 value; affects only body-biased operation |
| `b0` | 0 | width dependence of bulk charge | keep: inert at 0 |
| `b1` | 0 | partner of `b0` | keep: inert at 0 |
| `pdiblcb` | 0 | body-bias dependence of DIBL | keep: inert at 0; `pdiblc1/2` are fitted |
| `dsub` | 0.35 | DIBL sub-threshold exponent | keep: `eta0`/`etab` are fitted; no independent data |
| `pscbe1` | 4.24e8 | substrate-current body effect | keep: matters near breakdown, outside the SOA these devices are rated for |
| `pscbe2` | 1e-5 | partner of `pscbe1` | keep, as above |
| `kt2` | 0.022 | second-order Vth tempco | keep: `kt1` is fitted per card; `kt2` is a small correction with no source |
| `ua1` | 4.31e-9 | temperature coefficient of `ua` | keep: `ute` fitted; no ONC25 mobility-tempco split |
| `ub1` | −7.61e-18 | temperature coefficient of `ub` | keep, as above |
| `uc1` | −5.6e-11 | temperature coefficient of `uc` | keep, as above |

The "keep" decisions fall into three groups: terms that are **inert** at their default
(`dvt0w`-family, `b0`/`b1`, `pdiblcb`), terms that would **double-count** an already-fitted
parameter (`nlx`, `dsub`, `kt2`, `ua1`/`ub1`/`uc1`), and terms that act **outside the rated
operating region** (`pscbe1/2`). None of them is silently shaping a published number.

`k3` is none of those.

## 4. `k3 = 80`: the one default that must be grounded

BSIM3's narrow-width term raises Vth as width shrinks, scaled by `k3 · tox/(Weff + w0)`. With
`k3` undeclared, every AutoHV MOS runs the Berkeley default of 80 — a value appropriate to much
older, thicker-oxide technologies. Fitted values for a 0.18 µm-class process are single digits.

Measured on NMOS50 (L = 1 µm, Vgs = Vds = 5 V), Vth from the model's own readback, quoted against
a 50 µm-wide device:

| W | Vth rise, `k3 = 80` (today) | Vth rise, `k3 = 2, w0 = 2.5e-7` | Id/W today | Id/W grounded |
|---|---|---|---|---|
| 0.4 µm | **+238 mV** | +29 mV | 111.9 µA/µm | 125.5 µA/µm |
| 1.0 µm | +195 mV | +14 mV | 133.1 | 148.0 |
| 4.7 µm | +87 mV | +3 mV | 151.8 | 160.2 |
| 10 µm | +44 mV | +1 mV | 157.0 | 162.0 |
| 50 µm | reference | reference | 162.1 | 163.3 |

For scale: the **global** 3σ Vth spread for this class is ±128–135 mV. The undeclared default is
therefore imposing a *geometry-dependent* threshold shift about twice the entire process corner
on a minimum-width device, and about a third of it on the 4.7 µm device the sizing guide uses for
its 10 µA mirror entry.

**Proposed grounding:** `k3 = 2.0`, `k3b = 0`, `w0 = 2.5e-7`, `source: literature` (0.18 µm-class
fitted range, single-digit `k3`, `w0` of order 1e-7…2.5e-6), `error_bar: ±100 %`. Applied to all
eight cards.

**What moves** (for brief §11): every narrow device. The sizing guide's `analog_min_W` entries,
minimum-width logic cells, and any circuit relying on small-W devices gain roughly 100–240 mV of
threshold back. Wide devices (≥ 10 µm) move by under 45 mV; devices at 50 µm are unaffected.

**Why this is in scope.** Brief §0 unfroze the models: a change needs physics, a source, and a
recorded before/after. This has all three, and it is the direct cause of the sensitivity anomaly
diagnosed in Phase 0 (`d lnI/d lnW` = 1.096 instead of 1.004).

## 5. Non-BSIM3 cards

VDMOS, BJT, diode, R and C cards are outside this audit's parameter set. The VDMOS cards are the
next candidate for the same treatment — they carry no `tox` and only a handful of fitted
parameters — but nothing in them was implicated by Phase 0, so they are listed here as a
follow-up rather than audited now.

## 6. Card self-consistency: `k1` vs `nch` (retained), and the PMOS50 slope fix

Added after the statistical-model program measured every card's subthreshold slope and compared
each card's `nch` against the doping its own `k1` implies.

### 6.1 `k1`/`nch` disagreement is physical, not a defect

`Na(k1) = (k1·C_ox)²/(2·q·ε_si)` is the doping averaged over the depletion region; `nch` is the
surface doping. On a retrograde or halo channel profile the first legitimately exceeds the second,
and the ratio falls as the oxide thickens and halo matters less — which is the pattern measured:

| card | `nch` cm⁻³ | `Na(k1)` cm⁻³ | ratio | measured S mV/dec |
|---|---|---|---|---|
| NMOS18 | 2.2e17 | 6.24e17 | 2.83 | 77.6 |
| PMOS18 | 2.5e17 | 7.89e17 | 3.16 | 80.7 |
| NMOS33 | 1.7e17 | 3.03e17 | 1.78 | 85.6 |
| PMOS33 | 1.9e17 | 3.86e17 | 2.03 | 89.6 |
| NMOS50 | 1.2e17 | 1.37e17 | 1.14 | 96.6 |
| PMOS50 | 1.4e17 | 1.81e17 | 1.29 | 104.3 |
| NMOS12 | 9.0e16 | 2.10e16 | 0.23 | 152.8 |
| PMOS12 | 1.1e17 | 2.51e16 | 0.23 | 170.2 |

**Ruling: retained, no change** on the six LV/mid cards — "retrograde-profile consistent". The
12 V pair inverts the pattern and is handled separately (§7).

Slopes measured by DC sweep at Vds = 0.1 V, W = 10 µm, L = 1 µm, linear fit of Vg against
log₁₀(Id) over the 1e-12…1e-9 A decades, 27 °C.

**Consequence for the statistical model:** every depletion-charge derivation uses `k1`, never
`nch`. `nch` is not an input to any statistical quantity.

### 6.2 PMOS50 subthreshold slope

PMOS50 measured 104.3 mV/dec against its **grounded** anchor of 85–100 (target 95) — a
pre-existing miss. Fixed with the one parameter meant for it:

| parameter | before | after | result |
|---|---|---|---|
| `nfactor` (PMOS50 only) | 1.9000 | **1.5055** | S 104.3 → 95.32 mV/dec |

`k1`, `nch` and `vth0` untouched. Fitted by bisection against the measured slope.

## 7. The 12 V card refit

NMOS12 and PMOS12 were built by scaling the 5 V cards without re-deriving the parameters that
depend on doping and oxide. Three independent lines of evidence agreed:

1. **Body effect.** `γ = tox·√(2qε_si·Na)/ε_ox` from each card's own `nch` at 31 nm is 1.552 (N)
   and 1.715 (P); the cards carried 0.750 and 0.820 — 2.07× and 2.09× low.
2. **Subthreshold slope.** Measured 152.8 / 170.2 mV/dec, against a first-principles
   `n = 1 + C_dep/C_ox` floor of 110.9 / 115.9 — what a high-`C_dep` device does, confirming `nch`
   as the trustworthy parameter on these two cards.
3. **Threshold.** The cards' `vth0` (1.350 / −1.550) is consistent with the *corrected* γ
   (+1.25 / −1.42 V, inside ±0.3) and inconsistent with the copied `k1` (+0.53 / −0.61, outside).
   `vth0` was fitted for the device the corrected `k1` describes.

A parameter-by-parameter comparison also found **22 of 59 shared parameters byte-identical** to the
5 V cards, including `k2`, `voff`, `nfactor`, `cj` and `cjsw`.

### 7.1 What changed

| parameter | NMOS12 | PMOS12 | basis |
|---|---|---|---|
| `k1` | 0.750 → **1.552** | 0.820 → **1.715** | `γ(nch, 31 nm)` |
| `k2` | −0.030 → **−0.03** (no change) | −0.040 → **−0.03** | declared per X2, not re-derived: there is no 12 V extraction data, and the standing value was a byte-copy of the 5 V card. NMOS12's copy already equalled the declared value, so only PMOS12 moved |
| `nfactor` | 1.7000 → **1.0625** | 1.8500 → **0.9713** | fitted to the 120 ± 10 mV/dec derived band |
| `voff` | −0.0700 → **−0.1544** | −0.0800 → **−0.2015** | fitted to hold weak-inversion continuity |
| `cj` | 0.0014 → **0.0012124** | 0.0015 → **0.001329** | `√(nch_5V/nch_12V)` = 0.866 / 0.886 |
| `cjsw` | 1e-10 → **8.66e-11** | 1e-10 → **8.86e-11** | same factor |

Junction densities scale on the **card-`nch`** basis, not `Na(k1)`: a source/drain-to-well junction
is set by the doping on its lightly-doped side, for which `nch` is the nearer proxy, while `Na(k1)`
is the halo-inflated depletion-averaged *channel* doping. The cards already distinguished the 12 V
junction in `xj` (5e-7 m vs the 5 V card's 2.6e-7) while carrying identical densities — corroborating
that depth was genuine and density was the copy.

### 7.2 Acceptance, measured

| quantity | NMOS12 | PMOS12 | target |
|---|---|---|---|
| subthreshold slope | 152.8 → **120.9** mV/dec | 170.2 → **124.4** | 120 ± 10 |
| weak-inversion Id at `vth0` − 0.3 V | 98 % of before | 100 % | ≥ 90 % |
| ΔVth at Vsb = 5 V | 0.825 → **2.090 V** | 0.910 → **2.406 V** | ≈ γ-implied |
| implied `k1_eff`, long device (W 50 µm, L 10 µm) | **1.463 (94 % of declared)** | **1.677 (98 %)** | body effect = γ(nch) |
| Idsat at Vgs = Vds = 12 V, cases 0–4 | **−5.7 to −6.3 %** | **−5.7 to −6.3 %** | within 10 % |

Three extraction methods agree on ΔVth (constant-current at 1 µA and 100 nA, and gm-max linear
extrapolation: 2.090 / 2.078 / 2.044 on NMOS12), so the numbers are not extraction artefacts.

### 7.3 Two predictions of mine that were wrong, and what actually happened

- **"Idsat will not move, because `k1` only touches the body-bias term."** It moved −6.0 % on
  both cards. Reverting **one** parameter at a time attributes the entire shift to **`k1`**: with
  `k1` alone put back, the pre-refit current returns exactly (1.854488e-03 N / 8.652385e-04 P),
  while reverting `k2`, `voff`, `nfactor` or `cj`/`cjsw` alone leaves the full −6.0 % in place.
  `k1` is not confined to the body-bias term — it also sets BSIM3's bulk-charge factor `Abulk`,
  which scales the saturation current at any bias including Vbs = 0. The operating-point split
  confirms that mechanism: at Vgs = 12 V, the saturation current (Vds = 12 V) moves −6.0 % while
  the linear current (Vds = 0.1 V) moves only −0.9 % (N) / −1.1 % (P). A threshold shift would
  move both alike; a bulk-charge effect moves saturation and barely touches linear.

  I mis-attributed this bullet **twice**: first to `k1`/`k2` jointly (the ablation reverted them
  together and could not separate them), then to `k2` alone — which the card diff already refuted,
  since NMOS12's `k2` never changed yet its Idsat moved the full −6.0 %. The one-at-a-time
  measurement above is what settles it. The acceptance passes either way, but the reasoning behind
  the original prediction was wrong.
- **"The measured body effect should equal the closed form."** It is ~16 % below it
  (2.090 vs 2.495 V). `dvt0` — short-channel Vth roll-off — accounts for the geometry-dependent
  part: disabling it moves the implied `k1_eff` from 1.383 to 1.465, and a wide/long device
  independently reproduces 1.463. `k3` and `toxm` contribute nothing. The remaining 6 % is BSIM3
  evaluating `√(φs − Vbs)` where the closed form uses `√(2φ_F + Vsb)`.

### 7.4 Anchor updated

`docs/anchor-values.json`, NMOS12/PMOS12 `subthreshold_swing`: 72–96 (target 80, `industry`) →
**110–130 (target 120, `autohv-derived`)**. The retired value was a thin-oxide industry number and
does not apply to a 31 nm gate. The first-principles floor (110.9 / 115.9) is recorded in the
entry's basis.

### 7.5 What moves downstream

12 V body effect roughly doubles: ΔVth at Vsb = 5 V rises by ≈ 1.2–1.5 V, so every 12 V circuit
with source not tied to body moves. Subthreshold and weak-inversion entries move; strong-inversion
Idsat moves −6 %. Junction capacitances drop 11–13 %, so 12 V delay and comparator timing moves.
The NMOS12 analog-floor and every 12 V sizing-guide entry are re-derived in Phase 7.
