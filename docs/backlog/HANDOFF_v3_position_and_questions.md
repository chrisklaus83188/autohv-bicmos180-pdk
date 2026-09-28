# Handoff: where the program stands, and five things I should not decide alone

**Branch:** `mc-realism` @ `e9038f8`, pushed, tree clean, seven checks green
**Date:** 2026-09-27
**Purpose:** a position statement, not a package report. Phase 3a is reported separately in
`HANDOFF_v3_phase3a_wrappers.md`. This document exists so you can steer before I spend effort
on choices that are yours.

---

## 1. Position, phase by phase

| phase | state |
|---|---|
| 0–2 | done and landed |
| naming pass, history rewrite, device rename | done, verified from a clean clone |
| **3 — wrappers** | **3a done**: wrappers generated from `stat_model.json`, `M` now reduces mismatch (ratio exactly 2.000), A_VT ladder propagated (up to −51.5 %). 3b–3f not started |
| 4 — `mc_driver` / `corner_sweep` | not started. **Fully specified; needs nothing from you** |
| 5 — liveness gates | not started. Fully specified |
| 6 — the two documents | not started. Fully specified |
| 7 — re-characterisation, tag | not started. Specified, but see §4 |

## 2. What I can finish with no further input

Most of it. Concretely: the four MOS knobs (`Z_VT`, `Z_BETA` via `mulu0` — verified working,
`Z_W`, `Z_L`); the gate resistor (`RSH_GATE` σ = 0.0667 exists and the formula is given); edge
bias (σ = 0 until grounded, so it wires as zero); VDMOS `Z_VT`; the `MM_SIGMA` → knob migration
across 118 callers with byte-identical verification, then its removal; `BV_DZ_*` at 5 % 3σ
lognormal and the reverse-bias Zener bench; all of Phase 4, 5 and 6; and the Phase 7 mechanics.

I will proceed on all of that. The rest of this document is the part I should not invent.

## 3. Five questions. Each has a recommendation; a one-word answer unblocks it.

### Q1 — multi-finger perimeter convention (carried over from Phase 3a)

Area share I derived and trust: `AD = AS = (W/NF)·LD·(NF+1)/(2·NF)`. Perimeter share I will not
invent, because whether `PD` counts the gate-facing edge is a model convention and guessing
misstates sidewall capacitance on every multi-finger device.
**Recommendation:** `PD = PS = [2·(W_f + 2·LD) + (NF−1)·2·LD]/(2·NF)`, excluding gate-facing
edges.

### Q2 — the resistor four-way split is underdetermined

`_RESISTORS.terms` names `A_RSH`, `A_W`, `A_LEND`, `SIG_HEAD`. **None of the four exists as an
entry — there are no values at all.** The brief gives one equality (combined σ at the 10×10 µm
reference equals today's lumped value) and one inequality (end+head ≤ 20 % of variance there).
That is **four unknowns, one equation and one bound** — two or three degrees of freedom left
over, and whatever I pick sets how `NS` behaves.

**Recommendation:** variance shares **sheet 64 / width 16 / end 10 / head 10** — end+head at
the 20 % ceiling, so the `NS` mechanism is actually visible and testable rather than numerically
irrelevant, and sheet-dominant within the area-law pair, which is right for poly.

| type | lumped | `A_RSH` | `A_W` | `A_LEND` | `SIG_HEAD` |
|---|---|---|---|---|---|
| RPOLY_HI / LO | 1.061 | 0.849 | 0.424 | 0.336 | 0.336 |
| RNWELL | 2.828 | 2.262 | 1.131 | 0.894 | 0.894 |
| RNPLUS / RPPLUS | 1.768 | 1.414 | 0.707 | 0.559 | 0.559 |

### Q3 — the capacitor splits are underdetermined, and there are two of them

`A_CPER.value` is `null`. Two separate splits hide behind it:

- **σ split**: σ² = `A_C²/A + A_CPER²/P`, with one equality (total σ at the reference) and two
  unknowns → one free parameter.
- **nominal-C split**: `C = C_area·A + C_per·P` holding total C at the 100×100 µm golden
  geometry — again one equality, two unknowns → one free parameter.

**Recommendation:** put **20 % of the σ variance** in the perimeter term, mirroring Q2, and
**2 % of the nominal C** at the golden geometry in the perimeter density (a small fringe share
is what 100×100 µm physically implies), with the ±100 % error bar the model already carries.

| type | `A_C` now | `A_C` new | `A_CPER` |
|---|---|---|---|
| CMIM_STD / CMIM_HI | 0.530 | 0.474 | 0.150 |
| CMOM / CFRINGE | 1.061 | 0.949 | 0.300 |

### Q4 — `A_IS` for diodes does not exist

The brief calls for `ΔIs/Is = A_IS/√area`, but `_BJT` carries only `A_VBE` and `A_BF`.

**Recommendation: derive it rather than declare it** — `A_IS = A_VBE/(n·V_T)`, reusing exactly
the Finding A physics (the emission coefficient read per card, never typed). That keeps one
story for the whole junction-mismatch family instead of a new free number:

| device | `n` | `A_IS` (%·µm) |
|---|---|---|
| DIO_FAST / DIO_PN / DIO_SCH | 1.03 / 1.05 / 1.08 | 3.76 / 3.68 / 3.58 |
| DZ_5V6 / DZ_12V / DZ_24V | 1.15 / 1.18 / 1.22 | 3.36 / 3.28 / 3.17 |

### Q5 — how much of Phase 7 do you actually want re-run?

A_VT moved by up to 51.5 %, so **every mismatch-dependent result in the repo is stale**: mirror
characterisation, comparator offsets and delays, the sizing guide's σ columns, the scorecard.
Phase 7 says re-characterise, and I will — but the scale is worth confirming before I spend it,
and there is a related choice:

**Should `pdk_validation/baselines/v2_2/` be superseded by a new `v3_0` baseline, or kept
alongside it?** It is a frozen snapshot whose mismatch numbers are now known-wrong rather than
merely old. My instinct is to **keep v2_2 frozen and add v3_0**, since the whole argument for
not editing a baseline is that it records what was true then — but "known-wrong" is a different
case from "superseded", and it is your call whether v2_2 should carry a note saying so.

## 4. Two items still outstanding that are not mine

- **The stranded worktree.** `…/autohv-bicmos180-pdk` is still on `transmission-gates` at
  `61de05f` (pre-rewrite) with **31 modified files**; the remote is `98cefc2`. Untouched. The
  files are safe on disk but that branch points at history the remote no longer has.
- **`xschem/designs/*.sch`** — renamed, symbol references all resolve, but **not
  netlist-verified**; xschem is not on PATH here.

## 5. What I will do next, absent a reply

Phase 3b (the four knobs, gate resistor, edge bias), then the `MM_SIGMA` migration and removal,
then the Zener bench and `BV_DZ_*` — all of which are unblocked — and then Phase 4. I will leave
the resistor split, the capacitor splits, the diode `A_IS` and `NF` wiring untouched until you
answer, since each one would otherwise bake in a number I chose rather than one you ruled.
