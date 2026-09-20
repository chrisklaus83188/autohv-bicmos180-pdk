# Corners

Generated from `models/corners.json` by `tools/build_corners.py`. Do not edit the table by hand.

## What a preset is

Presets set each participating variable to ±3σ, as foundry corner libraries do. The joint distance
is reported so the pessimism is visible; it is not a target. Single-group corners are exactly 3σ;
`case 1–4` are multi-group worst cases; `case 13–16` are multi-module worst cases. Yield questions
are answered by MC, not by corners.

Two consequences follow, and both are correct behaviour rather than defects:

- **The joint Mahalanobis distance of a multi-group preset is large.** A preset that moves *k*
  independent variables to ±3σ sits at `3·√k`. For a full CMOS corner in any production library
  that is well above 10. It measures how unlikely the *simultaneous* worst case is, which is the
  point of reporting it.
- **Opposite-polarity presets carry shared-variable conflicts.** `case 3`/`4` (FS/SF) ask n-type
  to go fast while p-type goes slow, but the two share `TOX_<class>`, `DL_POLY` and `DW_ACT_*`.
  The generator sums the contributions and reports the conflict per preset rather than silently
  picking a side.

## Distances

<!-- BEGIN distances -->
| case | preset | groups moved | variables | Mahalanobis |
|---|---|---|---|---|
| 0 | typical, nothing moved | 0 | 0 | **0.00** |
| 1 | FF: all MOS fast | 21 | 65 | **16.54** |
| 2 | SS: all MOS slow | 21 | 65 | **16.54** |
| 3 | FS: n-type fast, p-type slow | 21 | 65 | **13.18** |
| 4 | SF: n-type slow, p-type fast | 21 | 65 | **13.18** |
| 5 | LV fast, HV slow | 21 | 65 | **16.54** |
| 6 | LV slow, HV fast | 21 | 65 | **16.54** |
| 7 | all resistors lo | 5 | 6 | **6.71** |
| 8 | all resistors hi | 5 | 6 | **6.71** |
| 9 | all capacitors lo | 4 | 3 | **8.49** |
| 10 | all capacitors hi | 4 | 3 | **8.49** |
| 11 | BJT and diodes lo | 10 | 24 | **9.49** |
| 12 | BJT and diodes hi | 10 | 24 | **9.49** |
| 13 | slow everything | 40 | 97 | **22.11** |
| 14 | fast everything | 40 | 97 | **22.11** |
| 15 | SS with resistors lo | 26 | 70 | **18.08** |
| 16 | FF with resistors hi | 26 | 70 | **18.08** |

Presets with shared-variable conflicts: **3, 4** — see above.
<!-- END distances -->

## How a direction is measured

Per group, `g_i = d ln(metric)/d z_i` on the group's own classic bench (Vgs = Vds = class supply,
sizing-guide width), then `z_fast = 3·g/|g|` and `z_slow = −z_fast`. A single-group corner is
therefore exactly 3.00 by construction. `models/stat_directions.json` carries the full `g` vectors,
the bench, and the variables excluded for having no lever, each with a reason.

## History

The `≈ 3` expectation once attached to compound presets belonged to the ρ-decomposition of masters,
which ruling U1 retired in favour of binary sharing. It is void: with independent unit normals the
distance of a *k*-variable worst case is `3·√k` and always was.
