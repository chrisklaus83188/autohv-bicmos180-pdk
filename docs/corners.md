# Corners

Generated from `models/corners.json` by `tools/build_corners.py`. Do not edit the table by hand.

## What a preset is

Presets set each participating variable to ±3σ, as foundry corner libraries do. The joint distance
is reported so the pessimism is visible; it is not a target. A single-group corner sits at `3·√k`
for *k* contributing variables — see `per_group.mahalanobis_corner` in `models/corners.json`.
`case 1–4` are multi-group worst cases; `case 13–16` are multi-module worst cases. Yield questions
are answered by MC, not by corners.

### Two 3σ points, and why the corner is the pessimistic one

There are two defensible ways to turn a statistical model into a corner, and they are different
points in the same space. Both are stored per group, and they must never be mixed:

| | construction | distance | stored as | used for |
|---|---|---|---|---|
| **joint 3σ** | `z = 3·g/|g|` — the point on the group's 3σ ellipsoid that maximises the metric | exactly 3 | `z_direction` | MC, sensitivity, yield reasoning |
| **per-variable 3σ** | `z_i = 3·sign(g_i)` — every contributing variable at its own 3σ at once | `3·√k` | `z_corner` | **sign-off corners: what the presets use** |

The joint-3σ point is the statistically honest 3σ of the distribution: it is the worst case that
actually has 3σ probability. A sign-off corner is deliberately *not* that point. Every production
corner library sets each variable to its own ±3σ simultaneously, which is more pessimistic by
roughly `√k`, and that margin is the point of a sign-off corner rather than an error in it.

A consequence worth stating plainly: because the corner is more pessimistic than the joint 3σ, a
device's corner spread is wider than its measured 3σ swing. NMOS1V8's measured 3σ swing is 9.2 %;
its FF/SS corner spread is wider, and both numbers are correct — they answer different questions.

Two further consequences follow, and both are correct behaviour rather than defects:

- **The joint Mahalanobis distance of a multi-group preset is large.** A preset that moves *k*
  independent variables to ±3σ sits at `3·√k`. For a full CMOS corner in any production library
  that is well above 10. It measures how unlikely the *simultaneous* worst case is, which is the
  point of reporting it.
- **Opposite-polarity presets carry shared-variable conflicts.** `case 3`/`4` (FS/SF) ask n-type
  to go fast while p-type goes slow, but the two share `TOX_<class>`, `DL_POLY` and `DW_ACT_*`.
  The generator sums the contributions and reports the conflict per preset rather than silently
  picking a side. Under per-variable ±3σ a variable pulled `+3` by one group and `−3` by another
  sums to exactly **0** — the shared variable sits at typical, which is the only value that can
  satisfy both demands. That is why FS/SF carry fewer moved variables than FF/SS.

## Distances

<!-- BEGIN distances -->
| case | preset | groups moved | variables | Mahalanobis |
|---|---|---|---|---|
| 0 | typical, nothing moved | 0 | 0 | **0.00** |
| 1 | FF: all MOS fast | 21 | 65 | **40.02** |
| 2 | SS: all MOS slow | 21 | 65 | **40.02** |
| 3 | FS: n-type fast, p-type slow | 21 | 58 | **22.85** |
| 4 | SF: n-type slow, p-type fast | 21 | 58 | **22.85** |
| 5 | LV fast, HV slow | 21 | 65 | **40.02** |
| 6 | LV slow, HV fast | 21 | 65 | **40.02** |
| 7 | all resistors lo | 5 | 6 | **9.00** |
| 8 | all resistors hi | 5 | 6 | **9.00** |
| 9 | all capacitors lo | 4 | 3 | **9.00** |
| 10 | all capacitors hi | 4 | 3 | **9.00** |
| 11 | BJT and diodes lo | 10 | 24 | **14.70** |
| 12 | BJT and diodes hi | 10 | 24 | **14.70** |
| 13 | slow everything | 40 | 97 | **47.62** |
| 14 | fast everything | 40 | 97 | **47.62** |
| 15 | SS with resistors lo | 26 | 70 | **44.40** |
| 16 | FF with resistors hi | 26 | 70 | **44.40** |

Presets with shared-variable conflicts: **3, 4** — see above.
<!-- END distances -->

## How a direction is measured

Per group, `g_i = d ln(metric)/d z_i` on the group's own classic bench (Vgs = Vds = class supply,
sizing-guide width). From that one `g` come both vectors: `z_direction = 3·g/|g|` (joint 3σ,
distance exactly 3.00) and `z_corner_i = 3·sign(g_i)` (per-variable, distance `3·√k`).
`models/stat_directions.json` carries the full `g` vectors, the bench, and the variables excluded
for having no lever, each with a reason.

### The term-count invariant

A degraded direction is invisible in `corners.json`: every group's vector is normalised, so it
carries no trace of how many variables went into it, and all 40 distances stayed entirely
plausible while five records had silently lost terms. The quantity that actually moves is the
term count, so that is what `tools/expected_terms.py` asserts, in two parts:

- **Accounting (derived).** Every variable the model realises for a group is either a term in its
  measured direction or a recorded exclusion — never simply absent. Computed from `applies_to`
  alone, so it cannot be satisfied by editing the expectation.
- **Snapshot (measured).** The term count equals a stored, reviewed value. This one cannot be
  derived: `prune_no_lever` legitimately moves a variable from term to exclusion *after*
  measurement, so the split is an outcome, not a property of the model. It is a tripwire against
  silent drift, and moving it is meant to be a deliberate edit.

`build_corners --check` runs both before it compares the file, because `corners.json` can be
perfectly current and still be built from a direction that quietly lost terms.

## History

The `≈ 3` expectation once attached to compound presets belonged to the ρ-decomposition of masters,
which ruling U1 retired in favour of binary sharing. It is void: with independent unit normals the
distance of a *k*-variable worst case is `3·√k` and always was.
