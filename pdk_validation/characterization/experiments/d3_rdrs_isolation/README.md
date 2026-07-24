# D3 — `rd`/`rs` isolation

## QUESTION

Audit §2.5 backs an implied cell width out of the model two ways — from `kp` and
from `rd+rs` — and the two disagree by **2.43×** on NDMOS20 and **0.08×** on
NDMOS200, a 30× swing across the family. Is that disagreement real information
about two independent defects, or is it series-resistance interaction: one defect
seen twice?

## METHOD

NDMOS20 and NDMOS200, each measured on the **stock** card and on an isolation
copy with `rd` and `rs` forced to `R_ZERO = 1e-9 Ω`.

`rq` is deliberately **kept** (unlike D1): quasi-saturation is a drift-velocity
effect inside the device, not a terminal series resistance, and zeroing it would
remove a mechanism this question is not about.

Two quantities on each of the four combinations:

- **Ron·W** at `Vov = 4 V`, `Vds = 0.1 V`. With `rd = rs = 0` this is
  **channel-only** resistance — the number the eventual `rd`/`rs` re-derivation
  needs, because it is the part of Ron that `rd`/`rs` must *not* be asked to
  account for.
- **Idsat density** at `Vov = 4 V`, `Vds = min(0.5·BV, 10) V`.

## VERDICT

### The 2×2 tables

**Ron·W (Ω·µm)**

| device | stock | rd=rs=0 (channel only) |
|---|---|---|
| NDMOS20 | 2.310 | **1.610** |
| NDMOS200 | 44.744 | **27.225** |

**Idsat density (mA/µm)**

| device | stock | rd=rs=0 |
|---|---|---|
| NDMOS20 | 1674.4 | 2074.5 |
| NDMOS200 | 117.7 | 166.1 |

### The decomposition is clean

Subtracting the `rd=rs=0` on-resistance from the stock one recovers the card's
own `rd+rs` to **0.03 %** (NDMOS20: 0.07002 Ω measured vs 0.070 carded) and
**0.11 %** (NDMOS200: 1.7520 vs 1.750). Ron really does separate into a channel
term and a series term, so the split below can be trusted.

| device | Ron stock | channel | series | **series share** |
|---|---|---|---|---|
| NDMOS20 | 0.2310 Ω | 0.1610 Ω | 0.0700 Ω | **30.3 %** |
| NDMOS200 | 4.4744 Ω | 2.7225 Ω | 1.7520 Ω | **39.2 %** |

**The channel dominates Ron on both cards.** Audit §2.2 did not allow for this —
it took the card's *entire* on-resistance to be `rd+rs`.

### Two consequences, pulling opposite ways

**(1) The `kp` route is CLEAN.** Removing `rd`/`rs` lifts Idsat density by only
**1.239×** (NDMOS20) and **1.411×** (NDMOS200), against implied-width gaps of
3649× and 287×. Series resistance explains **under 0.2 %** of the `kp` finding.
F1's `kp` half cannot be blamed on `rd`/`rs`.

**(2) The Ron route was MISATTRIBUTED.** Because `rd+rs` are only 30 %/39 % of
Ron, audit §2.2's implied widths are overstated by **3.30×** and **2.55×**.
Re-cast on the total measured Ron:

| device | audit W-from-kp | audit W-from-rd+rs | **W from total Ron** | disagreement before | **after** |
|---|---|---|---|---|---|
| NDMOS20 | 3649× | 951× | **288×** | 2.43× | **12.66×** |
| NDMOS200 | 287× | 2327× | **911×** | 0.08× | **0.31×** |

### One line

**TWO INDEPENDENT SLIPS — the disagreement survives.**

It does not collapse; it **moves**. The swing across the family *widens* from 30×
to 40×. Audit §2.5's conclusion — `rd`/`rs` carry a clean uniform ~10³ slip while
`kp` carries a slip *and* a wrong ladder slope — stands, and the correction makes
the case stronger rather than weaker.

## CONSEQUENCE

**Channel-only Ron·W, for the `rd`/`rs` re-derivation:**

> **NDMOS20 = 1.610 Ω·µm, NDMOS200 = 27.22 Ω·µm** at `Vov = 4 V`, `Vds = 0.1 V`.

This is a **floor**. Total Ron·W can never fall below it, because this is the
channel resistance the same `kp` that sets Idsat also sets. Two things follow:

1. Any `rd`/`rs` proposal must be checked against it. A divisor that would drive
   total Ron·W near or below the channel-only value is *arithmetically
   impossible*, not merely optimistic.
2. More awkwardly, the floor is itself set by the same defective `kp`. Fixing
   `kp` downward **raises** this floor, so fix #2 and fix #3 are coupled through
   it even though the defects are independent.

**Fix worklist:**

- **Fix #2 (`kp`)** is untouched by `rd`/`rs` and can be scoped on its own
  evidence. D3 closes off "maybe it is just series resistance".
- **Fix #3 (`rd`/`rs`)** needs audit §2.2's implied-width table **recomputed** —
  it divided by `rd+rs` where it should have divided by the full on-resistance.
  The correction is 3.30× at 20 V and 2.55× at 200 V. Not uniform, so it also
  slightly steepens what §2.2 called a flat ratio. That does **not** overturn the
  "one divisor" verdict for `rd`/`rs` — a 1.3× tilt inside a ~10³ slip is noise —
  but the table should be reissued with the measured split.
- **Ordering: re-derive `kp` first, then `rd`/`rs` against the resulting
  channel-only floor.**

## RUN

```
python run.py
```

Decks in `../../decks/d3_rdrs_isolation/`, isolation copies in
`../../results/local_models/{NDMOS20,NDMOS200}_d3.mod`.
