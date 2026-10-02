# Handoff: Phase 3d–3e — resistors exact, capacitor σ landed, one §2 stop

**Branch:** `mc-realism` @ `a2a20d2`, pushed, tree clean, **seven checks green**
**Date:** 2026-10-01
**Status:** Phase 3 is ~85 % done. **One §2 stop:** the capacitor *nominal* split (Q3) is held
at zero on a scaling-law objection — the σ split landed and is active. Everything else proceeds.

---

## 1. §2 STOP — the capacitor nominal split diverges as 1/size

Q3 puts 2 % (MIM) and 30 % (CMOM/CFRINGE) of total C on the **perimeter** at the 100×100 µm
golden geometry. Total C is indeed unchanged *there*, as Q-C requires. But a perimeter term
diverges as 1/size, and the golden geometry is the largest one anyone uses:

| L=W | 2 µm | 10 µm | 50 µm | 100 µm | 200 µm |
|---|---|---|---|---|---|
| CMIM_STD | **1.98×** | 1.18× | 1.02× | 1.00× | 0.99× |
| CMOM | **15.70×** | 3.70× | 1.30× | 1.00× | 0.85× |

A 15.7× change on a 2×2 µm CMOM would invalidate every switched-capacitor design in the repo.
I held it rather than ship it and report afterwards.

**Why I think the premise doesn't carry.** The reasoning for the fringe types is that their
"area" density is *mostly interdigitated edge*. That is true of the physical **origin** — but it
does not follow to `cjsw`. Finger count scales with **area**, so interdigitated edge capacitance
belongs in `cj`, where it already is. Only the true **outline** fringe scales with perimeter.

**And the MIM number looks ~7× high.** A perimeter fringe *is* physically right for a plate
capacitor, but 2 % at golden implies **0.5 fF/µm**. The card's own dielectric thickness
(66 nm) and plate density (1 fF/µm²) imply a fringe of roughly `cj·t_ox` ≈ **0.07 fF/µm** —
about 0.28 % at golden.

**Recommendation: derive `cjsw` from the dielectric rather than declaring a share** —
`cjsw ≈ cj·t_ox` for all four types, with the interdigitated edge left in `cj`. That is
grounded instead of declared, and it keeps C/area size-dependent (acceptance B6) without the
divergence. The structure is already in place: landing it is **one value per type** once ruled.

The σ split is unaffected and **active** — a `1/√P` σ term does not diverge the way a `1/size`
nominal term does, and edge definition genuinely does dominate CMOM matching.

## 2. Resistors (Q2) — acceptance B5 exact on every count

| check | measured | predicted |
|---|---|---|
| M=2 halves | 609.97112642 Ω | 1219.9422528/2 = 609.9711264 |
| NS=4 head delta | **45.0000000 Ω** | 6 extra heads × 7.5 Ω |
| σ at reference | 1.061000e-3 | model 1.060999e-3 |
| σ at NS=4 | 1.34206e-3 | model 1.34206e-3 |
| σ(NS=4)/σ(NS=1) | 1.2649 | √(1.60/1.00) = 1.2649 |

That last ratio is the ruled `√NS` growth of the end/head terms, falling out of the closed form
rather than being fitted.

**Getting there required measuring the model, not trusting it.** My assumption about the ngspice
semiconductor-R geometry was wrong. An L/W sweep on the bare card gives effective-geometry
offsets of **2.031e-07** and **2.433e-07** against card values of `short=1e-07` and
`narrow=1.2e-07`: the model applies **both corrections on both edges**. Using 1× left M=2 off by
0.6 % and B5 about 1 % short — which is how it was caught. `short` and `narrow` are now read
from the card template and the wrapper perturbs the *effective* geometry.

**Nominal shift, designer-visible:** contact heads are new physics, previously absent entirely.
Resistor values rise **+1.24 %** at the 10×10 µm reference and **+0.12 %** at the 100×10 µm R(V)
golden geometry. Passive goldens regenerate in Phase 7.

**Also removed:** `RSH0` in the old wrappers was dead code duplicating the card's own `rsh`
nominal, free to drift from it.

## 3. Capacitors (Q3) — what did land

σ² = `A_C²/A + A_CPER²/P`, divided by M. Verified exactly on CMIM_STD at the reference:
nominal **1.0000000300e-13 F** unchanged, M=2 **exactly double**, `Z_C=1` giving **5.30e-4**
relative against the model's 5.2997e-4 — today's lumped σ.

**One scale factor, solved rather than guessed.** Scaling both dimensions by `√x` multiplies
area by `x` but perimeter only by `√x`, so the old `LS=√CMM` trick would realise ~0.85× the
intended σ on the 30 %-perimeter types, and M parallel copies have the same problem. The wrapper
now solves `k²(1−f) + k·f = M·CMM` for the positive root, with `f` the perimeter share at the
instance's own geometry, collapsing to `k=1` at M=CMM=1.

## 4. A pattern worth a check of its own

`RHEAD_<layer>` was another **declared-but-unrealised** variable (`applies_to: null`). That is
the **fourth** instance: `VBE`/`VF`, then `A_BETA`, then the edge-bias trio, now `RHEAD`. Each
was found only because someone looked. A check that fails when a variable with a σ has no
realisation would have caught all four on the day they were written — cheap to add, and I will
add it with the B2–B7 scripts unless you would rather it waited.

Related: `Z_RSH_GATE` and `Z_RHEAD_*` were undeclared because `gen_models` only declared Z_ for
wrapper targets on `*_template` entries. Fixed for any target-only global.

## 5. What remains in Phase 3

- **BJT / diodes** — replace the single `AREAEFF` fudge with the three independent terms
  (`A_VBE`, `A_BF`, `A_IS`), then migrate their `MM_SIGMA` callers
- **`MM_SIGMA` removal** from the last wrappers once those callers move
- **acceptance B2–B7** as scripts under `pdk_validation/`, N=200, seed 0, LHS
- the capacitor nominal split, once §1 is ruled (one value per type)

Then Phase 4 (`mc_driver`, `corner_sweep`) → **Stop B** → 5, 6, 7 and the `v3.0-stats` tag.

## 6. State

`a2a20d2`. Migrations so far: 250 MOS lines (44 files), 44 VDMOS (9), 51 resistor (9), 4
capacitor (1) — all behaviour-preserving, each verified before the migration ran rather than
after. Still outstanding and not mine: the stranded worktree and the six `xschem/designs/*.sch`
netlist checks.
