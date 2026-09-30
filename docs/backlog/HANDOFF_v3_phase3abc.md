# Handoff: Phase 3a–3c landed — three defects found, all five rulings applied

**Branch:** `mc-realism` @ `5d442df`, pushed, tree clean, **seven checks green**
**Date:** 2026-09-30
**Status:** Phase 3 is ~70 % done. Q1–Q5 are all applied. No blockers, nothing waiting on you.
Remaining Phase 3 work is listed in §5 and I am continuing into it.

---

## 1. Decisions table

| decision | basis |
|---|---|
| Wrapper section generated from `stat_model.json` (`tools/gen_wrappers.py` + pristine `.lib.in`) | coefficients must be traceable by name; 492 of 622 lines are authored device structure, so it is a line transform, not a rebuild |
| Coefficients emitted as `AGAUSS(0, <1σ>, 1)` | the number in the file is now the model's own value, not one silently scaled by 3 |
| MOS wrapper body expanded from a marker | after Phase 3b nothing authored remained inside it; line-patching a fully statistical block would be pretence |
| `MM_SIGMA` migrated before removal, not removed first | 118 files passed it; equivalence was **verified against closed forms** before the migration ran |
| Generated docs excluded from the migration | editing them would be silently undone by their generator |
| Zener bench is **current-driven** | that is how a Zener is specified and used; a voltage-driven bench measures current on the near-vertical knee where sensitivity is numerically hopeless |
| VDMOS `Vshift` polarity flipped | see §4 — a knob must mean one thing on every device |

## 2. The three rulings that changed numbers

**Q1 finger geometry.** Both formulas verified against ngspice readback, exactly:

| | AD measured | PD measured |
|---|---|---|
| NF=1 | 1.0000e-12 | 3.0000e-06 |
| NF=4 | 1.5625e-13 | 7.5000e-07 |

`NF` also moves Id (3.500e-5 at NF=1 vs 3.178e-5 at NF=4 for the same total width) because
BSIM3's narrow-width term sees the per-finger width — which is the point of modelling fingers.

**Q2 resistors / Q3 capacitors.** Combined σ at the reference geometry reproduces today's
lumped values **exactly** — 0.106100 / 0.282800 / 0.176800 % for the resistors, 0.053000 /
0.106100 % for the capacitors. That is acceptance B5/B6's constraint, met by construction.

**Q4 `A_IS`** derived as `A_VBE/(n·V_T)` with `n` read per card, so the junction family keeps
one story.

**Q5 Zener bench.** Physical and dominated by `BV` as predicted: DZ_12V clamps at **11.990 V**
on 100 µA against a nominal 12 V; `g(BV)` = 0.0166 against its 0.0167 σ (≈1:1); `RS` = 1.35e-6,
non-zero at the bench current exactly as you anticipated. All three Zeners: 5.0 % swing, 2 terms,
`VF` excluded with a recorded reason.

## 3. The program's first bug, closed

`AUM2` omitted `M`, contradicting `stat_model.json`'s own `_convention`. Deterministic acceptance
(`MM_SIGMA=1`, no MC) on NMOS5V0 W=2 µm L=1 µm: **4.2143564159 mV at M=1, 2.1071782079 mV at
M=4 — ratio exactly 2.000000000**, both matching `A_VT/√(W·L·M)` to ten significant figures.

And the A_VT ladder, derived at Stop A, had **never reached the wrappers**: NMOS12V −51.5 %,
NMOS5V0 −45.8 %, 3V3 +12.7/+20.2 %. Nothing else was stale (29 of 46 σ values numerically
unchanged, 9 more by rounding only), which is what made it safe to land in one step.

## 4. Three defects found by checking rather than assuming

**(a) `Z_RSH_GATE` was never declared.** `gen_models` declared Z_ for wrapper targets only when
the model entry was a `*_template`; `RSH_GATE` is a plain global whose only realisation is a
wrapper target, so adding the gate resistor produced a **dangling reference and ngspice failed
outright**. Fixed for any target-only global.

**(b) `PD` double-counted the gate-facing sidewall.** The old wrapper used `2·(W_f + LD)`,
counting both long edges, where BSIM3 handles the gate-side sidewall through `cjswg`. At NF=1
that is 5.0e-6 where Q1's convention gives 3.0e-6 — sidewall junction capacitance was ~40 % too
high on every MOS device in the PDK.

**(c) `Z_VT` meant opposite things on MOS and VDMOS.** The MOS shifts Vth through `delvto`, the
VDMOS through a gate `Vshift`, and they disagreed:

| | Z_VT = 0 | Z_VT = +3 | |
|---|---|---|---|
| NMOS5V0 | 1.80104e-4 | 1.78196e-4 | falls → higher Vth ✓ |
| NDMOS20V | 6.32552e-3 | **6.37775e-3** | **rose** → lower Vth ✗ |

One knob value meant "slower" on a MOS and "faster" on a VDMOS. Polarity flipped on all 13
cards; both families now fall together. Random MC was never affected (symmetric); the
deterministic knob was simply wrong. Corner directions cannot be affected — the harness sets
`MM_ON=0` and never passes `Z_VT`, so `DVTH_MM` is identically zero in every direction
measurement.

**A fourth, in the edge bias:** `Z_DW_ACT_*` and `Z_DL_POLY` were declared with live corner
values and consumed by **nothing** — `applies_to: additive-in-wrapper` with no wrapper to honour
it. That is the third time this exact pattern has appeared (after `VBE`/`VF`, then `A_BETA`).
Sign and scale now match how the harness measured them (`lint`/`wint` at `scale=-0.5`,
`dL=-2·dlint`), so +1σ means longer/wider.

## 5. What remains in Phase 3

The Q2/Q3/Q4 coefficients are in the model but not yet in the wrappers:

- **resistors** — `NS` series segments, `R_HEAD`, the four-term closed form
- **capacitors** — perimeter term in the wrapper *and* the nominal split in the `.inc` cards
- **BJT / diodes** — replace the single `AREAEFF` fudge with the three independent terms
  (`A_VBE`, `A_BF`, `A_IS`)
- **`MM_SIGMA` removal** from the remaining 32 wrappers, after their callers migrate
- **acceptance B2–B7** as scripts under `pdk_validation/`, N=200, seed 0, LHS

Then Phase 4 (`mc_driver`, `corner_sweep`) → **Stop B** → 5, 6, 7 and the `v3.0-stats` tag.

## 6. State

`5d442df`, pushed. All 40 directions re-measured, corners and `expected_terms` rebuilt. The
term-count invariant earned its keep again: adding `BV_*` to six devices without re-measuring
turned it red immediately and named the missing record.

Still outstanding and not mine: the stranded worktree (`transmission-gates` at `61de05f`, 31
modified files) and the six `xschem/designs/*.sch` netlist checks.
