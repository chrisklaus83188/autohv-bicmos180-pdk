# Handoff: Q1–Q4 implemented and landed; two findings need a ruling

**Responds to:** the Q1–Q4 ruling (per-variable ±3σ corners; `VBE_*`/`VF_*` on `is`; full 0–16 menu; term-count assertion)
**Branch:** `mc-realism` @ `368374d` (parent `c15a0b1`)
**Date:** 2026-09-20
**Status:** All four applied in the ruled order, five checks green, before/after table produced.
Two things I found while implementing need you: the diode `n` factor, and Zener breakdown.

---

## 1. What landed, against the numbers you predicted

| ruling | predicted | measured | |
|---|---|---|---|
| Q1 NMOS18 FF/SS | ≈ ±10–13 % | **+13.06 / −11.69 %** | in band |
| Q1 5 V (NMOS50) | ≈ ±10 % | **+12.32 / −11.13 %** | ~1–2 pp above |
| Q2 NPN_LV at preset 11 | ≈ −18.7 % | **−18.672 %** | exact |
| Q2 BJT/diode flatness | none within ±0.5 % of 0 on 11–14 | **none** | met |
| Q4 flat on own preset | none | **none of 40** | met |

**Q1.** `build_corners` emits `z_corner` (per-variable `z_i = 3·sign(g_i)`) and keeps
`z_direction` (joint `3·g/|g|`) per group, so the two points can never be confused again.
`gen_models` reads `z_corner` for the `case = -1` per-group path, so preset and per-group
control use one convention. No multiplier anywhere.

**Q2.** `σ/V_T` folded at generation — `is={2e-16*exp(0.0773635*Z_VBE_NPN_LV)}`. `gen_models`
imports `VT_THERMAL` from the harness rather than keeping a second copy, since a drifted
duplicate would put cards and measured directions quietly out of step. The frozen-27 °C
rationale is written into the code at the point of the fold and into `docs/corners.md`.

**Q3.** `.lib` header now lists all 17 presets plus `case = -1`, states that 1–4 move the MOS
groups only, and points at `docs/corners.md`.

**Q4.** `tools/expected_terms.py`, wired into `build_corners --check`. Verified by deleting a
term from a direction: both arms fire, and `--check` returns 1.

Five checks green: `inc_parse`, `gen_models`, `expected_terms`, `build_corners`,
`stat_model_inventory`. Full 40 × 0–16 before/after in `docs/case-table-q1-before-after.md`;
the current table is `docs/case-table.md`.

## 2. Consequences of Q1 worth stating

**FS/SF now move fewer variables than FF/SS — 58 against 65.** Under per-variable ±3σ a shared
variable pulled `+3` by one group and `−3` by another sums to **exactly 0**, where under the
old construction the two components had unequal magnitudes and left a residue. Typical is the
only value that satisfies both demands, so I believe this is correct; it is reported in the
per-preset conflict list as before, and `docs/corners.md` now says so. Preset distances: FF/SS
40.02, FS/SF 22.85, all-device 13/14 47.62.

**Resistors and capacitors did not move at all.** Expected: per-variable ±3σ and joint 3σ are
the same point for a one-variable group, and those groups have one contributing variable each.

## 3. Finding A — the diode emission coefficient is not 1, and it is not constant

`_VF_template`'s own `derivation` field reads `IS = IS_TT*exp(-dVf/(n*V_T))`. The ruled scale is
`σ/V_T = 0.10328`, which omits `n`. The six diodes do not share an `n`:

| device | `n` | σ/(n·V_T) | implemented (σ/V_T) | error |
|---|---|---|---|---|
| DIO_FAST | 1.03 | 0.1003 | 0.10328 | +3 % |
| DIO_PN | 1.05 | 0.0984 | 0.10328 | +5 % |
| DIO_SCH | 1.08 | 0.0957 | 0.10328 | +8 % |
| DZ_5V6 | 1.15 | 0.0898 | 0.10328 | +15 % |
| DZ_12 | 1.18 | 0.0875 | 0.10328 | +18 % |
| DZ_24 | 1.22 | 0.0847 | 0.10328 | **+22 %** |

**I implemented 0.10328 as ruled** rather than silently substituting my own number, and it is a
one-line change either way. But it makes the diode corner up to 22 % wider than the template's
stated physics, and it is inconsistent across a family that should be consistent.

Note the harness has the same omission: `measure_stat_directions` measures both the `vbe` and
`vf` forms with `scale = 1/VT_THERMAL`. So card and measurement currently agree with each other
and both differ from the derivation. Fixing one without the other would be worse than fixing
neither — they must move together, and the directions would need a re-measure.

**Question 1:** should `n` enter, per device, in both the harness and the generator? BJTs are
unaffected (`nf = 1` on all four).

## 4. Finding B — Zener breakdown voltage is deterministic

No `BV_*` variable exists for any diode: `_BV_template.devices` is the 13 VDMOS plus the 4 BJT
wrapper targets. The six diodes carry a fixed `bv` — and three of them are Zeners, where
breakdown *is* the device's reason for existing:

| device | `bv` | varies? |
|---|---|---|
| DZ_5V6 | 5.6 | no |
| DZ_12 | 12 | no |
| DZ_24 | 24 | no |

A Zener reference whose breakdown has exactly zero spread will make any shunt-regulator or
clamp margin look perfect. The VDMOS `BV_*` variables are declared but resolve to 0 at every
preset, which is deliberate and documented (no lever at a forward-conduction bench) — the Zener
case is different, because breakdown is the operating point, not an off-state limit.

**Question 2:** add `BV_DZ_*` with a Zener bench (reverse breakdown rather than forward `V_f`),
in Phase 3? It needs a new bench and a new metric, so it is not a small edit, and I have not
started it.

## 5. One design decision I made that you should overrule if it is wrong

Q4 said `expected_terms` should be "computed from the realised `applies_to` entries, not typed".
Pure derivation turned out to be impossible for the *term* count: `prune_no_lever` legitimately
moves a variable from term to exclusion after measurement, so the split is not a property of the
model. I stored two things instead:

- `realised` — **model-derived**, and the assertion is the accounting invariant *every realised
  variable is a term or a recorded exclusion*. This cannot be satisfied by editing the
  expectation, and it is the arm that catches AE1.
- `terms` / `excluded` — a **measured snapshot**, asserted for equality as a tripwire against
  silent drift. Updating it is a deliberate edit.

So the strong check is derived and the snapshot is a secondary guard. If you intended the term
count itself to be model-derived, the pruning rule has to become part of the model instead.

## 6. State

`368374d` on `mc-realism`, tree clean. New: `tools/expected_terms.py`,
`docs/case-table-q1-before-after.md`. `tools/case_table.py` now sweeps 0–16 and asserts no group
is flat on a preset it belongs to.

Nothing is blocked. Unless you rule otherwise on §3, the naming pass is next, then Phase 3 —
where §4 belongs if you want it.
