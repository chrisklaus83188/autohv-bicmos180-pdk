# Phase-2 discrimination experiments — D1…D4

Four experiments that settle what the phase-1 static audit
(`docs/model-realism-audit.md`) had to **assume**. Each directory holds a
`run.py` exposing `def run() -> dict` (also runnable standalone) and a README
stating its question, method, verdict and consequence.

```
python d1_kp_convention/run.py      # etc.
```

Read-only with respect to the PDK. `autohv_bicmos180_case.lib` and
`autohv_bicmos180_case_models.inc` are never written. Isolation copies go to
`../results/local_models/` via `char_lib.write_local_model()`; decks to
`../decks/<experiment>/`.

## The four verdicts

| # | question | method | **verdict** | consequence |
|---|---|---|---|---|
| **D1** | Is VDMOS saturation `kp·Vov²` or `(kp/2)·Vov²`? | NDMOS200 with `rd=rs=rq≈0`, bias at `Vov ∈ {1,2,3} V`, fit `A` in `Id = A·Vov²` with `theta`/`lambda` divided out analytically | **`kp/2`** — `A = 0.11000000`, `A/kp = 0.4999999986`, residual 2.8e-7 | **No anchor change.** Both `_vdmos_kp_conditional` routes already assume this convention. The §2.1 F1 finding (287×–5213×) survives intact. Add a `convention` note. |
| **D2** | Is `ksubthres` V/decade, V/e-fold, or something else? | Direct subthreshold fit on all 13 stock cards; regress `S_measured` on `ksubthres`; cross-check via gm/Id ceiling | **Per-decade, inflated 1.17×.** `S = 1155.6·ksubthres + 1.21`, R² = 0.9998. Natural-log reading excluded (50 % off). | **OVERTURNS phase-1 §2.8 in part** — see below. Strike the sub-Boltzmann item; keep the slope item; re-ladder against measured `S`. |
| **D3** | How much of the `kp`-route vs Ron-route disagreement is series resistance? | NDMOS20 + NDMOS200, stock vs `rd=rs≈0`; Ron·W and Idsat density on each | **Two independent slips.** Series is only 30 %/39 % of Ron; removing it moves Idsat 1.24×/1.41× against 3649×/287× gaps | Channel-only floor **1.610 / 27.22 Ω·µm**. §2.5 stands but §2.2's table must be recomputed (÷ by full Ron, not `rd+rs`) — 3.30×/2.55× correction. Re-derive `kp` **before** `rd`/`rs`. |
| **D4** | Is fix #2 one divisor or thirteen re-derivations? | All 13 cards with `rd=rs≈0`; fit `theta`; convert to a `tox` band; recompute the §2.1 width table at flat vs laddered `tox`; compare spreads | **Neither — six.** n-channel spread 12.7× (flat `tox`) → **5.5×** (theta-laddered). Flattens 2.3×, not to 1. | One divisor **+ per-class trim** (6 numbers). ⚠ **Conditional on the maintainer declaring `tox` per class** — D4 says what each declaration implies, it does not decide it. |

## D2 overturns a phase-1 finding

Audit §2.8 made two claims. D2 splits them:

- **Structural claim — the `ksubthres` ladder slopes the wrong way with voltage
  class, when `n = 1 + C_dep/Cox` demands it rise. → CONFIRMED.** Measured slope
  −0.00356 per volt of class (phase 1: −0.00310). Multiplying a ladder by a
  near-constant 1.17× cannot flip the sign of its slope, and it does not. This is
  the real defect.
- **Headline claim — NDMOS200 at `n = 1.01`, below the room-temperature
  Boltzmann floor, "unphysical". → OVERTURNED.** Measured `S = 70.7 mV/dec`,
  `n = 1.19`. **No card in the family is sub-Boltzmann.** The finding was an
  artifact of reading `ksubthres` as if it were `S` in V/dec.

Phase 1 had to assume the semantics because nothing in the PDK states them. D2
measured them twice, by independent routes that agree. Where they conflict, the
measurement wins.

## Two methodological findings worth carrying forward

**1. `char_lib`'s isolation-copy mechanism does not work as documented.**
`write_local_model()` / `lib_include()` state the copy is *".include'd AFTER the
PDK so this card shadows the original"*. **ngspice-45 keeps the FIRST definition
of a model name and silently discards the later one — no warning.** Verified: a
deck including the PDK then a second `.model NDMOS200_INT VDMOS (… rd=0 rs=0 …)`
reads back `@NDMOS200_INT[rd] = 1.2`. Any experiment built on the documented
assumption would have run entirely on stock cards while believing it had zeroed
`rd`/`rs`.

`exp_lib.isolated()` works around this by **renaming** the copy and instantiating
it as a raw VDMOS device, bypassing the subckt wrapper.
`wrapper_equivalence_check()` proves the bypass is exact rather than asserting
it — it runs the *unmodified* card both ways and reports the Id ratio, which came
back **1.0 exactly** for n-channel, p-channel and the depletion DNMOS20.

Every experiment also reads its isolation card back through ngspice's
`@<MODEL>[param]` accessors, so the edit is *proven* to have landed.

**2. Exactly `rd=0`/`rs=0` will not converge.** ngspice-45's VDMOS fails gmin
stepping, source stepping and the transient op, dying with *"Timestep too small;
trouble with `<model>`-instance m0"*. `rd = rs = 1e-9 Ω` converges and reads back
correctly. At the ~1 A these cards carry that drops 1 nV, against the
0.070–4.38 Ω the stock cards carry — nine orders of magnitude down. Every
"`rd=rs=0`" in D1/D3/D4 means `R_ZERO = 1e-9`.

## Cross-experiment consistency

The four are not independent checks of unrelated things — they interlock, and the
interlocks all hold:

- **D1 → D4.** D1 established `Id = (kp/2)·Vov²/(1+theta·Vov)·(1+lambda·Vds)` on
  one card. D4's fit recovers the card `kp` from the intercept on **all thirteen**
  to within 0.18 %, confirming the convention family-wide.
- **D3 → D4.** D3 showed series resistance is 30–39 % of Ron, which is exactly
  why D4 must zero `rd`/`rs` before extracting `theta`. With them zeroed the IR
  drop is 1e-6 % of `Vov` and every fit lands at R² > 0.9998.
- **D2 internal.** The swing fit and the gm/Id ceiling — a log-slope fit and a
  derivative ratio, different features of the same sweep — agree on both the
  per-decade reading *and* the direction and rough size of the 1.17× residual.
- **D4 → §2.1.** Hypothesis (a) reproduces audit §2.1's published table to 0.11 %,
  so the departure under hypothesis (b) is the `tox` ladder and not a
  recomputation error.

## Anchor amendments proposed (maintainer applies — nothing here edits the JSON)

1. `_vdmos_kp_conditional`: add
   `convention: "ngspice VDMOS: Id_sat = (kp/2)·Vov²; measured A/kp = 0.5000 (D1)"`.
   **No target values change.**
2. Beside `subthreshold_swing`: record
   `S_mV_per_dec = 1.171 × 1000 × ksubthres` (D2, R² = 0.9998, 13 cards).
   **No band changes.** Also fix `families/vdmos.py` `_do_idvg`'s
   `model_ksubthres_note`, which asserts the 1.00× reading.
3. New `_vdmos_tox_conditional` block: the two oxide hypotheses, their measured
   residual spreads (12.7× flat vs 5.5× laddered, n-channel), and the
   theta-implied `tox` band per class. `kp_n`/`kp_p` are computed at
   `tox = 20–50 nm` and need restating per class under the laddered hypothesis.
4. Audit §2.2's implied-width table: reissue divided by full measured Ron rather
   than `rd+rs` (3.30× at 20 V, 2.55× at 200 V). Does **not** overturn the "one
   divisor" verdict for `rd`/`rs`.
