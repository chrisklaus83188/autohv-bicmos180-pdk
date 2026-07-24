# D4 — `kp` ladder shape

*The highest-leverage question in the worklist.*

## QUESTION

Audit §2.1 computed an implied cell width per card as `W = kp·L_ch/(mu·Cox)` and
found 287×–5213× — and, critically, that the ratio is **not constant**: it falls
12.7× from the 20 V card to the 200 V card. That sloped residual is why fix #2
was scoped as **thirteen separate re-derivations** rather than the single divisor
that fixes `rd`/`rs`.

But §2.1 held `tox = 30 nm` across every voltage class. Audit §2.7's own `theta`
analysis implies `tox` **rising** with class — 25–75 nm at 20 V to 56–167 nm at
200 V. Thicker oxide → smaller `Cox` → larger implied width, and the effect grows
with class, so it pushes exactly against the slope §2.1 found. If it flattens the
residual, fix #2 collapses to one divisor.

## METHOD

1. Isolation copies of **all thirteen** cards with `rd`, `rs` forced to
   `R_ZERO = 1e-9 Ω`, so no series drop can masquerade as mobility degradation.
   This is the correction `families/vdmos.py` `_do_theta` flags as needed — on
   stock cards the IR drop is a large fraction of `Vov` at the top of the fit
   range and the extracted `theta` is only an upper bound.

2. `theta` by fit. D1 established the model's strong-inversion form exactly, so
   rearranging to a straight line:

   ```
   Vov²/Id = (2 / (kp·(1+lambda·Vds))) · (1 + theta·Vov)
   theta = slope / intercept
   ```

   over `Vov = 0.5…4.0 V`. `kp` falls out of the intercept as a by-product that
   independently re-confirms D1's convention on all thirteen cards.

3. Each measured `theta` → an implied `tox` **band**, via §2.7's
   `theta ≈ (1…3)e-7 / tox[cm]`. A band, never a point: the empirical constant
   spans 3×, and pretending otherwise would repeat the mistake §2.1 made with
   `tox = 30 nm`.

4. The §2.1 implied-width table recomputed **two ways** — (a) `tox = 30 nm` flat,
   (b) the `theta`-implied ladder.

5. The **spread** (max/min) of the implied-width ratio under each hypothesis. The
   hypothesis that makes the residual flatter is the one that says "one divisor".

> **The flatness verdict does not inherit the constant's 3× uncertainty.** The
> empirical constant multiplies every card's `tox` equally and cancels exactly in
> a max/min ratio (`W ~ kp/Cox ~ kp·tox ~ kp/theta`; the constant does not
> appear). Only the *absolute* implied widths inherit it — which is why those are
> reported as bands and the spread is not.

## Fit quality

| metric | value |
|---|---|
| min R² across 13 cards | **0.99986** |
| max IR drop as % of Vov | 1.0e-6 % |
| all well-conditioned | yes |
| max `theta` deviation from card | 4.8 % |
| max `kp` deviation from card | 0.18 % |
| hypothesis (a) reproduces audit §2.1 to | **0.11 %** |

Recovering the card `kp` from the intercept to 0.18 % on all thirteen cards is
not a tautology — it demonstrates D1's `(kp/2)` convention holds family-wide, and
that with series resistance removed the *measured* `theta` equals the *card*
`theta`, so §2.7's `tox` inferences (computed from card values) are not corrupted
by `rd`/`rs`. On stock cards they would have been.

## VERDICT

### Both tables side by side

| device | class | `kp` | `theta` meas | `tox` band (nm) | **(a) ratio @30 nm flat** | §2.1 | **(b) ratio @theta-tox** |
|---|---|---|---|---|---|---|---|
| DNMOS20 | 20 | 1.00 | 0.0387 | 26–78 | 1303× | 1303 | 1124× |
| NDMOS20 | 20 | 2.80 | 0.0419 | 24–72 | **3649×** | 3649 | **2903×** |
| PDMOS20 | 20 | 1.30 | 0.0462 | 22–65 | **5213×** | 5213 | **3758×** |
| NDMOS40 | 40 | 1.90 | 0.0357 | 28–84 | 2476× | 2476 | 2310× |
| PDMOS40 | 40 | 0.85 | 0.0395 | 25–76 | 3408× | 3408 | 2879× |
| NDMOS60 | 60 | 1.20 | 0.0303 | 33–99 | 1564× | 1564 | 1720× |
| PDMOS60 | 60 | 0.55 | 0.0352 | 28–85 | 2205× | 2205 | 2087× |
| NDMOS80 | 80 | 0.80 | 0.0272 | 37–110 | 1043× | 1043 | 1278× |
| PDMOS80 | 80 | 0.38 | 0.0311 | 32–96 | 1524× | 1524 | 1631× |
| NDMOS120 | 120 | 0.45 | 0.0221 | 45–136 | 586× | 586 | 885× |
| PDMOS120 | 120 | 0.21 | 0.0251 | 40–120 | 842× | 842 | 1120× |
| **NDMOS200** | 200 | 0.22 | 0.0180 | 55–166 | **287×** | 287 | **530×** |
| PDMOS200 | 200 | 0.088 | 0.0210 | 48–143 | 353× | 353 | 560× |

*(b) is quoted at the `tox_lo` edge; the ratios at `tox_hi` are identical — see
the band-independence note above.*

### The spread metrics

| group | **(a) tox = 30 nm flat** | **(b) theta-implied ladder** | flattening |
|---|---|---|---|
| all 13 | 18.2× | **7.1×** | 2.6× |
| **n-channel only** | **12.7×** | **5.5×** | **2.3×** |
| p-channel only | 14.8× | 6.7× | 2.2× |

### One line

**NEITHER — fewer than thirteen, more than one.**

The `theta`-implied oxide ladder flattens the residual **substantially but not to
one number**. It removes 2.3× of the 12.7× n-channel slope — most of it — and
leaves 5.5× behind.

Mechanically this is simple. Under (b), `tox ~ 1/theta`, so `Cox ~ theta` and
`W ~ kp/theta`. `kp` falls 12.7× across the n-channel family while `theta` falls
2.2×, so the residual falls by the ratio. The `kp` ladder and the `theta` ladder
are laddered together, but not proportionally.

### Ruling on fix #2

**Not thirteen re-derivations.** A 5.5× spread does not justify thirteen
independent physical derivations — it is the same order as the 2.8× spread audit
§2.2 was willing to call "roughly flat" and fix with a single divisor for
`rd`/`rs`.

**But not cleanly one divisor either.** A single divisor leaves a 5.5× residual,
well above measurement error, which would show up as a real drive-current ladder
error across voltage classes.

**RECOMMENDATION: one divisor plus a per-class trim — six numbers (one per
voltage class), not thirteen and not one.** Derive the divisor from the family
geometric mean and let the per-class trim absorb the residual ladder. If the
maintainer will accept a ~2× drive-current error at the extremes of the family,
one divisor is defensible and fix #2 becomes as cheap as fix #3.

## ⚠ MAINTAINER DECISION REQUIRED

**This experiment does not decide the oxide ladder.** Everything above is
conditional on the maintainer **declaring `tox` per VDMOS voltage class**. The
PDK never states it; audit §2.7 already recommends stating it because three
separate findings depend on it. D4 tells the maintainer what each declaration
implies:

| declaration | n-channel residual spread | scope of fix #2 |
|---|---|---|
| `tox = 30 nm` flat | **12.7×** | per-card — thirteen re-derivations, as phase 1 scoped it |
| theta-implied rising ladder | **5.5×** | one divisor + at most a per-class trim |

The theta-implied ladder is the better-supported of the two: it is derived from a
card parameter rather than assumed, it is monotonic and correctly ordered, and a
rising `tox` with voltage class is what the process would actually do. **But** it
is in tension with the `vto = 1.00–1.31 V` the cards carry, which for LDMOS body
doping suggests a *thinner* oxide — and D4 cannot resolve that tension. It is a
process-declaration question, not a simulation question.

**Do not apply fix #2 in either scoping until `tox` is declared.**

## CONSEQUENCE for the anchor (maintainer applies)

`_vdmos_kp_conditional` currently forks on `decision_A_10um_cell` vs
`decision_B_power_die`. D4 exposes a **second, orthogonal fork** — the oxide
ladder — that changes the **shape** of the `kp` fix rather than its magnitude.

Propose adding a `_vdmos_tox_conditional` block alongside it, recording the two
hypotheses, their measured residual spreads (12.7× flat vs 5.5× laddered,
n-channel), and the theta-implied `tox` band per class from the table above. The
existing `kp_n`/`kp_p` targets are computed at `tox = 20–50 nm` and would need
restating per class under the laddered hypothesis.

## RUN

```
python run.py
```

Decks in `../../decks/d4_kp_ladder_shape/`, thirteen isolation copies in
`../../results/local_models/*_d4.mod`.
