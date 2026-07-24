# D2 — `ksubthres` semantics

## QUESTION

Phase-1 audit §2.8 assumed `ksubthres` **is** the subthreshold swing in V/decade,
read the ladder straight off the cards as `S = 95 → 60 mV/dec`, and concluded:

1. the ladder slopes the **wrong way** with voltage class, and
2. NDMOS200's `n = 1.01` is **below the room-temperature Boltzmann floor** —
   "unphysical … it says the depletion capacitance is zero".

If ngspice instead reads `ksubthres` as a natural-log (per-e-fold) slope, every
`S` is larger by `ln10 = 2.3026` and both conclusions need re-examining. That
factor is the whole finding.

## METHOD

Direct subthreshold fit on the **stock** cards — `rd`/`rs` are irrelevant at
nano- to microamp currents. **All thirteen** cards are measured, not the three
the brief names: the extra ten cost one short DC sweep each and turn a
three-point regression into a thirteen-point one.

Per card: fine Id–Vg sweep (`Vds = 0.1 V`, 4 mV step) from 1.2 V below the card's
own `vto` to 0.2 V above, in the normalised coordinate `u = pol·Vgs` so
n-channel, p-channel and the depletion DNMOS20 share one code path. Leakage
plateau cut at 50× the floor, then `S` from a least-squares fit of
`log10(|Id|)` vs `u`.

`S_measured` is then regressed against the card's `ksubthres`. Two hypotheses:

| hypothesis | predicted slope `m` |
|---|---|
| per-decade — `S = 1000·ksubthres` | 1000 |
| natural-log — `S = 1000·ln10·ksubthres` | 2302.6 |

**Independent cross-check:** the subthreshold gm/Id ceiling. For
`Id ~ exp(Vgs/k)`, `gm/Id → 1/k`. A natural-log reading puts the ceiling at
`1/ksubthres`; a per-decade reading at `ln10/ksubthres`. This uses a derivative
ratio rather than a log-slope fit — a genuine second opinion on the same sweep.

## VERDICT

### (a) The mapping

```
S_measured [mV/dec] = 1155.6 · ksubthres + 1.21        R² = 0.9998,  13 cards
```

Equivalently `S ≈ 1.171 × (1000·ksubthres)`, tight: the per-card ratio spans only
1.167–1.180 across the whole family. The three brief-named cards alone give
`m = 1150.8`, consistent.

Measured swings reproduce `families/vdmos.py` exactly — NDMOS20 110.9, NDMOS200
70.7 mV/dec.

### (b) The semantics

**`ksubthres` is a per-DECADE slope. The natural-log reading is decisively
excluded** — the measured slope is 16 % off the per-decade hypothesis and 50 %
off the natural-log one.

But it is **not `S` itself** either. ngspice's VDMOS subthreshold branch blends
into the strong-inversion current rather than switching over sharply, so the
swing an extraction actually sees is inflated by a near-constant **1.17×** over
the parameter. Phase 1 was directionally right and quantitatively wrong by 17 %.

### (c) The recomputed n-ladder — `n = S/(ln10·kT/q)`, kT/q at 300.15 K

Boltzmann floor = 59.61 mV/dec.

| device | class | `ksubthres` | S phase-1 | n phase-1 | **S measured** | **n measured** |
|---|---|---|---|---|---|---|
| DNMOS20 | 20 | 0.085 | 85.0 | 1.43 | 99.8 | **1.68** |
| NDMOS20 | 20 | 0.095 | 95.0 | 1.59 | 110.9 | **1.86** |
| PDMOS20 | 20 | 0.110 | 110.0 | 1.85 | 128.5 | **2.16** |
| NDMOS40 | 40 | 0.088 | 88.0 | 1.48 | 102.8 | **1.73** |
| PDMOS40 | 40 | 0.096 | 96.0 | 1.61 | 112.2 | **1.88** |
| NDMOS60 | 60 | 0.080 | 80.0 | 1.34 | 93.4 | **1.57** |
| PDMOS60 | 60 | 0.090 | 90.0 | 1.51 | 105.1 | **1.76** |
| NDMOS80 | 80 | 0.075 | 75.0 | 1.26 | 87.6 | **1.47** |
| PDMOS80 | 80 | 0.082 | 82.0 | 1.38 | 95.9 | **1.61** |
| NDMOS120 | 120 | 0.070 | 70.0 | 1.18 | 81.9 | **1.37** |
| PDMOS120 | 120 | 0.077 | 77.0 | 1.29 | 90.2 | **1.51** |
| **NDMOS200** | 200 | 0.060 | 60.0 | **1.01** | **70.7** | **1.19** |
| PDMOS200 | 200 | 0.065 | 65.0 | 1.09 | 76.7 | **1.29** |

**(i) Is the falling-with-class slope still wrong? — YES, STILL WRONG.**
Physics requires `n = 1 + C_dep/Cox` to *rise* with class as the oxide thickens.
Phase 1's ladder slopes −0.00310 per volt of class; the measured ladder slopes
−0.00356. Both negative — and multiplying a ladder by a near-constant 1.17×
cannot change the sign of its slope. Measured n falls monotonically 1.86 → 1.19
across the n-channel family. **This half of §2.8 survives unchanged, and it is
the half that matters, because it is structural rather than numerical.**

**(ii) Is NDMOS200 still sub-Boltzmann? — NO. OVERTURNED.**
Measured `S = 70.7 mV/dec`, `n = 1.19`. Above 1 by a clear margin. **No card in
the family is sub-Boltzmann.** NDMOS200 remains the softest card and sits
marginally under the 1.2 industry-band edge, so "low" survives — but "physically
impossible" does not, and those are different claims.

### (d) The gm/Id cross-check

**13 of 13** cards put the measured ceiling nearer `ln10/ksubthres` than
`1/ksubthres`, at a mean of **0.873×** the `ln10/ksubthres` prediction. A
natural-log reading would have put it at `1/ln10 = 0.434×` this — excluded by a
wide margin.

The cross-check agrees on the *residual* too: the ceiling sits **13 % below**
ideal `ln10/k`, the same direction and comparable magnitude as the measured swing
sitting **17 % above** `1000·ksubthres`. Two independent features of the same
sweep, one answer. **The data supports the per-decade reading.**

## CONSEQUENCE

**This experiment OVERTURNS a phase-1 finding.** Phase 1 had to assume the
semantics because nothing in the PDK states them. D2 measured them, twice, by
routes that agree. The measurement wins.

**Fix worklist:**

- **STRIKE** the "NDMOS200 is sub-Boltzmann / n = 1.01 unphysical" item. There is
  nothing to fix.
- **KEEP** the "ksubthres ladder slopes the wrong way" item at unchanged
  severity — it sets the subthreshold gm/Id ceiling, which is what
  `HANDOFF_dmos200_subthreshold_analog.md` turns on.
- Any re-laddering must target **measured S**, not `1000·ksubthres`. A card
  wanting `S = 90 mV/dec` needs `ksubthres ≈ 0.0769`, not 0.090.

**Anchor (maintainer applies):** record the measured mapping
`S_mV_per_dec = 1.171 × 1000 × ksubthres` (R² = 0.9998, 13 cards) beside the
`subthreshold_swing` entry. **No anchor band changes** — the measured swings land
where the anchor already expected them.

**Also correct in the harness:** `families/vdmos.py` `_do_idvg()` emits
`model_ksubthres_note = "the card's ksubthres IS S in V/dec by construction"`.
That wording is off by 17 % and should be replaced with the measured mapping.

## RUN

```
python run.py
```

Decks land in `../../decks/d2_ksubthres/`. No isolation copies — D2 measures
stock cards.
