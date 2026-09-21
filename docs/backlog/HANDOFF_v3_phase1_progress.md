# Handoff: v3 Phase 1 progress — four Stop A deliverables done, one ruling needed

**Responds to:** the F1–F8 rulings reply
**Brief:** `HANDOFF_v3_stats_brief.md` as amended by the Phase 0 and Phase 1 replies
**Branch:** `mc-realism` @ `ad6032b`, pushed
**Date:** 2026-09-16
**Status:** four of six Stop A deliverables complete. **Stop A is not reachable yet**: 32 of 40
groups have no measured direction, so the preset table and its Mahalanobis distances do not
exist. One ruling (G1) blocks a number; three questions (G2–G4) shape the remaining work.

## 1. What is done

| deliverable | commit | state |
|---|---|---|
| `models/stat_model.json` | `d21c0da` | 131 global variables across the 40 groups; parses, 40/40 wrappers covered by `local_mismatch`, no unknown device names |
| `docs/bsim3-defaults-audit.md` | `865f742` | 34 audit-set parameters; 18 live defaults; `k3` grounded with measured evidence |
| `tools/measure_stat_directions.py` + `models/stat_directions.json` | `9d55c13` | Q-A construction implemented and working; 8 BSIM3 groups measured on both benches |
| `docs/stat-model.md` | `ad6032b` | reading copy: one section per variable family, calibration results, caveats |
| preset table + Mahalanobis | — | **not started** (blocked on the 32 remaining groups) |
| F1 discrepancy note | `ad6032b` | done, inside `stat-model.md` §3.1 |

Phase 0 closed earlier at `ebee2ad`: the CI MC check fixed and its 21 % gap explained, v2.2
baselines frozen (34 files), leftover copies deleted, ngspice-45 CI verified.

## 2. What the calibration produced

`U0` σ solved per group against the reference process class Idsat band, fixed set (`VTH`, `TOX`, `DL_POLY`,
`DW_ACT`, `RDSW`) held at grounded σ, per ruling F3:

| group | class band | fixed set alone | solved `U0` 1σ | achieved | error |
|---|---|---|---|---|---|
| NMOS18 | 20 % | 16.0 % | 4.29 % | 19.9 % | −0.6 % |
| PMOS18 | 20 % | 17.0 % | 3.57 % | 19.9 % | −0.3 % |
| NMOS33 | 20 % | 10.4 % | 6.42 % | 19.6 % | −1.9 % |
| PMOS33 | 20 % | 11.2 % | 5.76 % | 19.7 % | −1.6 % |
| NMOS50 | 14 % | 7.7 % | 4.57 % | 13.8 % | −1.2 % |
| PMOS50 | 14 % | 8.4 % | 3.98 % | 13.9 % | −0.9 % |
| NMOS12 | 14 % | 3.6 % | 5.45 % | 13.7 % | −2.0 % |
| PMOS12 | 14 % | 3.8 % | 4.98 % | 13.8 % | −1.8 % |

No group hit the 3 % floor. The ≤ 2 % residual is left alone on purpose: the band carries a
±25 % error bar, so removing it would be false precision.

## 3. What was found

### 3.1 `k3 = 80` costs 238 mV on a minimum-width device

Measured on NMOS50, L = 1 µm, Vgs = Vds = 5 V; Vth from the model's own readback, against a
50 µm device:

| W | today (`k3` undeclared → 80) | grounded (`k3=2, w0=2.5e-7`) | Id/W today | Id/W grounded |
|---|---|---|---|---|
| 0.4 µm | **+238 mV** | +29 mV | 111.9 µA/µm | 125.5 µA/µm |
| 1.0 µm | +195 mV | +14 mV | 133.1 | 148.0 |
| 4.7 µm | +87 mV | +3 mV | 151.8 | 160.2 |
| 10 µm | +44 mV | +1 mV | 157.0 | 162.0 |

For scale, the entire global 3σ Vth band for this class is ±135 mV. An undeclared default is
imposing a geometry-dependent shift nearly twice that on a minimum-width device — and it is the
direct cause of the `d lnI/d lnW = 1.096` anomaly diagnosed in Phase 0. The statistical model
assumes this grounding lands; if it is rejected, the sizing guide's narrow entries stay as they are.

### 3.2 `A_VT`: the reference process's own measurement contradicts ruling F5 — **G1**

F5 rests on "A_VT ≈ 1 mV·µm per nm of oxide", which the reference process's footnote states. But the reference process §GG
**measures** its 5 V CMOS at **6.35 mV·µm (NMOS) and 5.1 (PMOS)** on a 13.1 nm oxide — that is
0.48 mV·µm per nm. The rule only holds for their 2.5 V devices (0.78–0.94 mV·µm/nm).

Consequences: AutoHV's 5 V `A_VT` of 11.0 mV·µm is **1.7–2.2× wider** than the same-class
measurement, and its agreement with the oxide rule (11 ↔ 11 nm) is arithmetic coincidence, not
grounding. F5 leaves 5 V and 12 V untouched precisely because of that coincidence.

| class | today | F5 as ruled | reference-measurement-anchored |
|---|---|---|---|
| 1.8 V | 3.5 | 4.25 | 3.4 |
| 3.3 V | 4.0 | 6.75 | 5.5 |
| 5 V | 11.0 | 11.0 | **5.3** |
| 12 V | 31.0 | 31.0 | **15.0** |

The file is authored **as F5 directs**, with the conflict recorded in
`_meta.open_review_item`. Changing it is one number per device.

### 3.3 The F1 hypothesis check fails

F1 asked whether a unit conversion explains the reference process's spec-column matching values against its
model-form ones. It does not. A single normalization would give one constant ratio:

| layer | AutoHV 1σ | the reference process spec column | ratio |
|---|---|---|---|
| RPOLY_HI | 1.061 %·µm | 0.045 | 23.6× |
| RPOLY_LO | 1.061 | 0.042 | 25.3× |
| RNWELL | 2.828 | 0.363 | 7.8× |
| RNPLUS | 1.768 | 0.0094 | **188×** |
| RPPLUS | 1.768 | 0.040 | 44× |

A 24× spread, so no area or unit conversion reconciles them. The relative ordering disagrees too:
The reference process ranks n+ diffusion best-matching and n-well worst; AutoHV ranks high-res poly best and n+
diffusion mid-pack. Recorded as unexplained, spec column unused per F1 — and it is also a flag on
AutoHV's own per-layer matching values, which do not reproduce the reference process's ordering either.

### 3.4 Measuring beats assuming, again

My first calibration assumed `d lnI/d z_u0 = 1` per unit relative `u0`. Measured, it is
**0.83–0.98** depending on class, and the assumption undershot the band by 11 %. That is the same
error as the Phase 0 `run_mc.py` diagnosis, one layer up. The harness now measures the slope at a
probe σ before solving.

### 3.5 The classic and analog benches disagree by 10×

On NMOS50, the threshold sensitivity is **−0.025** at the classic bench (Vgs = Vds = 5 V) and
**−0.269** at the analog bench (gm/Id ≈ 6). Ruling F8 picks classic for the corner direction,
which is right for what `case` means — and this measurement is the evidence for the paragraph F8
asked for in `docs/corners.md`: a corner chosen for drive strength is not the worst point for a
gm/Id-biased analog circuit, which is why the exhaustive sweep and MC exist.

### 3.6 Smaller findings

- **All 13 VDMOS sit on `TOX_50`.** Gate oxide follows the gate rating (the reference process's 200 V LDMOS with
  a 5 V gate uses the 13 nm oxide), and every AutoHV VDMOS is rated ±5.5 V DC on the gate.
  `TOX_12` serves NMOS12/PMOS12 only.
- **`JS_MOS` has no lever** on an Idsat direction — junction leakage is picoamps against ~166 µA.
  It stays in the model but is excluded from directions, with the reason recorded, rather than
  sitting in the vector as a zero.
- **the reference process §8 ships full worst-case libraries with "master-variable correlations"** (noted but not
  transcribed in the local extraction). That is the same latent-factor construction Q-A(i) chose —
  the real process does it this way too.
- **VDMOS local mismatch is now grounded**: the reference process §GG gives NLDMOS40V5VA σ(ΔVth) = 8.2 mV at
  12 µm², i.e. `A_VT ≈ 20 mV·µm`, about 3× the CMOS coefficient.
- **The 5 V Vth band is ±135 mV measured** (the reference process §HH: 0.657 / 0.792 / 0.927), used in place of
  the ±128 mV synthesis F2 quoted — same source, tighter provenance.

## 4. Questions

| # | question | my proposal |
|---|---|---|
| **G1** (blocks `A_VT`) | §3.2: the reference process's measured 5 V `A_VT` contradicts the oxide rule F5 rests on. | Re-anchor on the measurement: 3.4 / 5.5 / 5.3 / 15.0 mV·µm, `source: reference-class:measured-5V-scaled-by-oxide`. This *narrows* 5 V and 12 V mismatch, so it moves published σ the opposite way from F5 — pre-register both directions. |
| **G2** | §2: the 12 V class is the weakest-grounded — its fixed set covers only 3.6 % of the 14 % band, so `U0` carries nearly the whole corner, because `VTH_12` is declared rather than measured. | Accept it and label the 12 V corner as the weakest-grounded class in `docs/corners.md`. The alternative is to widen `VTH_12` on the oxide ratio (31/13.1 × 135 mV ≈ 320 mV 3σ), which I do **not** recommend without a source. |
| **G3** | Metrics for the remaining 32 groups. | Resistors `ln R` at 1 V; capacitors `ln C` from a small-signal step at 0 V; BJT `ln Ic` at the sizing-guide 10 µA point (fixed `Vbe`); diodes `ln If` at 1 mA; **DNMOS20 `ln Idss` at Vgs = 0**, since it is a depletion device with no mirror point in the sizing guide. |
| **G4** | VDMOS perturbation target. Those cards carry no `tox`, `u0` or `rdsw`; their statistics live in top-level `*_STAT` params (`VTO_*`, `KP_*`, `RD_*`, `RS_*`) plus a card-level `bv`. | Perturb the `*_STAT` params directly and `bv` on the card. This is what makes `TOX_50` and `DL_POLY` reach VDMOS "via loading" as the model already declares. |

## 5. Next work package

One self-contained pass: extend the harness with the four missing bench types (VDMOS, resistor,
capacitor, BJT/diode), measure the 32 remaining directions, then build the preset table with
Mahalanobis distances for cases 0–16 and bring the whole set to Stop A. G3 and G4 shape it; G1
can land independently as one edit per device.
