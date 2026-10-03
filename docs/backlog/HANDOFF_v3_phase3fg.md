# Handoff: Phase 3f–3g — `cjsw` derived, the eighth check in, and two B6 bounds that the physics won't meet

**Responds to:** the 2026-10-02 ruling (Q3 nominal shares withdrawn; derive `cjsw`; add the eighth check)
**Branch:** `mc-realism` @ `5945257`, pushed, tree clean, **seven checks green**
**Date:** 2026-10-02
**Status:** Phase 3 ~92 % done. Both ruled items applied. **Two acceptance bounds in B6 are
exceeded and I believe they must be** — §2. Nothing is blocked; I am continuing to the BJT/diode
rewrite.

---

## 1. Decisions table

| decision | basis |
|---|---|
| `cjsw = ε₀·di`, identical for all four types | your derivation `cj·t_eq` with `t_eq = ε_diel/cj` collapses to `ε_diel`, independent of plate spacing. All four cards declare di = 7.5 and their `cj` is exactly `ε₀·di/thick` — ratio 1.0000 on all four, checked |
| `cj` left unchanged | you relaxed Q-C to "reported, not held", and an exact hold is what forced the bad share |
| `cjsw` follows **`CPER`**, not `CDEN` | area density is set by dielectric thickness, fringe by edge definition — different process steps, and the model already declared separate σ for them (CDEN 0.04/0.0667, CPER 0.0833) |
| the eighth check lives in `stat_model_inventory --check` | as ruled; it needed a `json` import there, since that tool previously only parsed the `.lib`/`.inc` |
| reported the B6 bound misses rather than trimming `cjsw` to fit | a derived value trimmed to satisfy a bound is no longer derived |

## 2. §2 — two of B6's bounds are exceeded, and the physics requires it

`cjsw` is now derived, and ngspice matches the closed form exactly (CMOM 2×2 µm:
**1.9312512097e-15 F** against 1.9313e-15 predicted; 100×100: 3.5265625777e-12 against
3.5266e-12).

**B6's substantive clauses both hold:**

- C/area is size-dependent — CMOM runs **1.379×** at 2 µm to **1.008×** at 100 µm
- M copies carry more perimeter than one M×-area copy — 4×(10×10 µm) gives **1.5063e-13 F**
  against **1.4531e-13 F** for a single 20×20 at equal total area

**The two numeric bounds do not:**

| bound | result |
|---|---|
| "within 1 % at golden" | CMIM_STD +0.27 %, CMIM_HI +0.13 %, CMOM +0.76 %, **CFRINGE +1.45 %** |
| "no size produces more than a few-percent fringe share" | at 2×2 µm: CMIM_HI 6.2 %, **CMIM_STD 11.7 %, CMOM 27.5 %, CFRINGE 42.5 %** |

Two things make these hard to dismiss:

1. **2×2 µm is the minimum *legal* geometry**, not a corner case — `device_limits.csv` gives
   `L,min = 2.0` and `W,min = 2.0` for all four types. Designers can and will instantiate it.
2. **A 2 µm plate over a 369 nm effective dielectric is necessarily fringe-dominated.** The
   plate dimension is only ~5× the gap. A fringe small enough to satisfy "few-percent at any
   size" would have to sit ~10× below what the card's own `di` and `thick` imply.

CFRINGE is the worst on both counts for the same reason: it has the thickest effective
dielectric (369 nm) hence the smallest `cj`, so a fixed ε-per-length fringe is the largest
fraction of it.

**My reading is that the bounds were written expecting a smaller fringe than the derivation
produces**, and that the derivation is the thing to keep. Options, in the order I would pick
them:

1. **Relax both bounds** to match the physics: golden shift ≤ 2 %, and fringe share stated as a
   function of size rather than capped (e.g. ≤ 5 % at ≥ 50 µm, unbounded at minimum geometry).
2. Keep the bounds and declare `cjsw` at ~1/10 the derived value — but then it is declared
   again, not derived, and we are back where Q3 started.
3. Keep the derivation and restrict the minimum legal capacitor geometry, which is a real
   decision about the PDK rather than about the model.

**Recommendation: option 1.** One word is enough.

## 3. The eighth check — in, and it earned its place on the first run

Every global variable with a non-zero σ must now have a realisation: an `applies_to` naming a
card parameter or a wrapper target, a `follows` coupling, or an explicit `realised: false`
carrying a reason. Verified against **both** failure modes — a σ with no realisation, and
`realised: false` with no reason — each turning it red, then green on restore.

**It immediately found `_CPER_template`:** σ = 0.0833, declared, consumed by nothing. That is the
**fifth** instance of this pattern after `VBE`/`VF`, `A_BETA`, the edge-bias trio and `RHEAD` —
but the first found in seconds by a check rather than by inspection weeks later.

CPER was genuinely unrealisable until this phase: it drives `cjsw`, and `cjsw` was 0, which is
why every direction excluded it with the recorded reason *"cjsw is 0 on this card, so there is
no perimeter lever."* That reason was true and is now false, so the exclusion lifts.

All 40 directions re-measured. The four capacitor groups go from one exclusion each to **zero**:

| group | CDEN | CPER | CPER share of the direction |
|---|---|---|---|
| CMIM_STD | 3.9117e-2 | 2.1219e-4 | 0.54 % |
| CFRINGE | 6.3630e-2 | 1.1648e-3 | 1.8 % |

Small because the harness bench sits at 10×10 µm where the fringe is a few percent of C — the
correct magnitude for that geometry, not a weak lever.

## 4. What remains in Phase 3

- **BJT / diodes** — replace the single `AREAEFF` fudge with the three independent terms
  (`A_VBE`, `A_BF`, `A_IS`), then migrate their `MM_SIGMA` callers
- **`MM_SIGMA` removal** from the last wrappers
- **acceptance B2–B7** as scripts under `pdk_validation/`, N = 200, seed 0, LHS
- the two B6 bounds, once §2 is ruled (no code change either way unless you pick option 2 or 3)

Then Phase 4 (`mc_driver`, `corner_sweep`) → **Stop B** → 5, 6, 7 → `v3.0-stats`.

## 5. State

`5945257`, pushed, tree clean. Migration tally so far, every one verified before it ran rather
than after: 250 MOS lines (44 files), 44 VDMOS (9), 51 resistor (9), 4 capacitor (1).

Still outstanding and not mine: the stranded worktree (`transmission-gates` at `61de05f`, 31
modified files) and the six `xschem/designs/*.sch` netlist checks.
