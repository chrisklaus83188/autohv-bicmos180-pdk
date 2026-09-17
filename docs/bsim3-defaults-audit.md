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
