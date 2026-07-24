# AutoHV BiCMOS180 PDK — Audit Summary (handoff)

**Purpose of this document.** A self-contained briefing on a two-phase realism audit of a custom
180 nm BiCMOS-BCD PDK, written so a reader with no prior exposure can pick up the work. Read this
first; the detailed documents are listed in §8.

**Audience.** The maintainer is an experienced analog/HV BCD engineer. Nothing here is pitched at a
novice.

**Status: phases 1 and 2 complete. No model fixes have been applied.** The PDK is exactly as it was;
everything produced so far is analysis, measurement, and proposals.

---

## 1. What the PDK is

`chrisklaus83188/autohv-bicmos180-pdk` — a custom 180 nm BiCMOS-BCD process design kit for ngspice,
intended to resemble a real automotive BCD process. 40 devices: 8 BSIM3 MOS (12/18/33/50 V), 13
VDMOS/LDMOS (20–200 V), 4 BJTs, 6 diodes/zeners, 9 passives. Corner-parameterised (TT/FF/SS/FS/SF)
with separate process and mismatch statistical axes.

It was **generated with LLM assistance and repaired over about two months**. That origin matters: the
defects found are overwhelmingly *systematic generator artifacts* — whole parameter ladders scaled
wrongly, simulator defaults left in place, one convention applied where another was meant — rather
than scattered typos.

---

## 2. What was done

| phase | method | output |
|---|---|---|
| **0** | Repo archaeology — full working tree + 67 commits of history | `characterization-inventory.md` |
| **1** | Static audit — read every model card, check against device physics and industry-typical 180 nm BCD values. Reading plus arithmetic; no simulation. | `model-realism-audit.md`, `anchor-values.md`, `anchor-values.json` |
| **2** | Simulation characterization — a harness measuring every simulation-measurable figure of merit, scored against phase-1 anchor bands, plus four targeted experiments to settle what phase 1 had to assume | `characterization-scorecard.md`, `audit-vs-measurement-discrepancies.md`, the harness itself |

**Phase 2 measured the PDK as-is.** It is the *before-picture* every subsequent fix gets diffed
against. 548 measurements on ngspice-45, 400 s wall, 621 committed standalone-re-runnable decks.

**Method convention used throughout**, inherited from the repo's own best existing work: every claim
carries a provenance tag — `[model]` read from the PDK · `[physics]` derived with the formula shown ·
`[industry]` typical published value with the basis stated · `[measured]` from a simulator run.
Assumptions are stated so they can be attacked; a factor-of-3 band honestly derived beats a false
point value.

---

## 3. The headline: what is actually wrong

Ranked by severity × breadth. All confirmed by measurement unless noted.

| # | finding | scope | magnitude |
|---|---|---|---|
| **F1** | **LDMOS DC parameters are scaled to a power die, not the 10 µm cell the wrapper claims.** `kp` and `rd`/`rs` are displaced by *different amounts in opposite directions* — two independent defects, not one. | all 13 VDMOS | Idsat 311×–11 200× high; Ron·W 456×–1440× low |
| **F2** | **VDMOS capacitances are still wrong after the June-2020 ÷1000 fix.** That fix rescaled but never re-derived, and the residual is voltage-class-sloped. | all 13 VDMOS | `cgs` 48× too high at 20 V falling to 3.3× at 200 V |
| **F3** | **BSIM3 flicker parameters are verbatim BSIM4 defaults in `level=49` cards** — digit-exact, including non-round values. Wrong unit convention. | 8 BSIM3 | ~6.25e21× |
| **F4** | **BJT `kf`/`af` are placeholders.** Flicker corner 2.97 MHz *and bias-independent* (`af=1`), inverting the BJT-vs-CMOS noise trade-off. | 4 BJT | 300–3000× |
| **F5** | **Zener `cjo` is a hand-picked ladder, not derived.** Doping explains only 3–10× of the 100–400×; the residual is non-uniform, so no single divisor fixes it. | 3 zeners | ~100–200× |
| **F6** | **`AD/AS/PD/PS` unset on all 8 BSIM3 wrappers.** Measured junction capacitance is *exactly zero* — 74–83 % of the drain node absent, and junction leakage identically zero. | 8 BSIM3 | 100 % missing |
| **F7** | **`RPOLY_HI` `tc1` has the wrong sign.** +656 ppm/°C measured where lightly-doped grain-boundary-limited poly must go negative. | 1 resistor | sign, ±15–27 % over −40…150 °C |
| **NEW** | **Both PNP avalanche branches are dead code.** `max(V(ci,b)/BVCBO, 0)` zeroes on a p-type device. PNP_LAT sustains **−200 V** against a declared BVCBO of 18 V. | 2 BJT | no breakdown model at all |

Also: passive matching is 4–11× optimistic across all nine devices; VDMOS mismatch has two
inconsistent ladders (40/80/200 V is ~3× tight); NMOS12/PMOS12 carry four Level-3→BSIM3 migration
defects; `device_limits.csv` gives the 12 V parts a 0.15 µm `Lmin` — shorter than the 1.8 V device,
on a 20 nm oxide.

**What is genuinely good**, and should survive any fix: the BJT avalanche construction for NPNs and
every BVCEO/BVCBO ratio; the entire PNP_LAT DC parameter set (real lateral-PNP physics, not a copied
NPN); the Schottky thermionic-emission parameters; all four capacitor densities, VCC and TCC values;
the resistor voltage-coefficient block; the mismatch *machinery* (AGAUSS re-randomisation and the
3σ convention are correct — only the magnitudes are wrong); BV corner behaviour, which matches its
own audit table to 0.04 %.

---

## 4. Where measurement overturned the static audit

Phase 2 exists partly to check phase 1. It found four places where the static reasoning was wrong,
and the rule applied was **the measurement wins**.

1. **"NDMOS200 is sub-Boltzmann" — OVERTURNED.** Phase 1 read `ksubthres` as mV/decade directly and
   concluded `n = 1.01`, "a perfect gate, unphysical." Measured: `ksubthres` is per-decade inflated
   1.17×; NDMOS200 swings at 70.7 mV/dec, `n = 1.19`. **No card in the family is sub-Boltzmann.**
   Strike it. (The *structural* half of that finding — the swing ladder slopes the wrong way with
   voltage class — survives untouched and is the real defect.)
2. **The implied-width table was misattributed.** Phase 1 took the card's whole on-resistance to be
   `rd+rs`. Measured: series resistance is only 30–39 % of Ron; the channel dominates. The table is
   overstated 3.30×/2.55× and must be reissued — but the two-independent-slips conclusion
   *strengthens*, with the family disagreement widening from 30× to 40×.
3. **The `kp` fix is smaller than scoped.** Phase 1 called for 13 per-card re-derivations, assuming a
   flat 30 nm oxide. Measuring `theta` on all 13 cards and letting the oxide ladder rise with voltage
   class flattens the residual 12.7× → 5.5×. **About six numbers, not thirteen** — conditional on §5.
4. **A published repro deck cannot have produced its own numbers.** An old handoff's capacitance
   measurement contains `echo ... ; print cdrain`, and `;` is a *comment* character in ngspice's
   control language — the print never executes. That closes a long-standing unexplained 1.6–2.1×
   discrepancy in the repo's history as *unreconcilable from the decks*.

Phase 1's arithmetic was otherwise sound: F2's predicted 48.2×/4.6×/3.3× measured 48.0×/4.62×/3.27×.
Every discrepancy traced to an **assumption**, not a calculation.

---

## 5. The five open decisions — these are the blockers

Nothing further should be applied to the models until these are answered. They are the maintainer's
to make; the audit deliberately does not make them.

| # | decision | what it gates | recommendation |
|---|---|---|---|
| **1** | **Is `W_REF = 10u` a genuine 10 µm drawn cell, or a label on a power die?** | every `kp`/`rd`/`rs` target — i.e. the magnitude of F1 | **10 µm cell.** The junction capacitance and body-diode groups independently land on it, and the earlier capacitance fix already assumed it. |
| **2** | **Declare `tox` per VDMOS voltage class.** Nothing in the PDK states it, and three separate findings depend on it. | the *shape* of the F1 fix — 6 numbers vs 13 | The theta-implied rising ladder is better supported (derived from a card parameter, monotonic, correctly ordered) but is in tension with the carded `vto = 1.00–1.31 V`, which suggests a thinner oxide. **A process question, not a simulation one.** |
| **3** | **What physical area does BJT/diode `AREA = 1` mean?** Currently undeclared *and mutually inconsistent* — `is` implies 4–80 µm², `cje`/`cjc` imply 300–900 µm². | `is`, `cje`, `cjc`, `cjo` for 4 BJTs + 6 diodes | Must be declared before any of those can be fixed. |
| **4** | **Fix the BSIM3 noise parameters, or migrate the cards to `level=54` (BSIM4)?** The current values are exactly right for BSIM4 and ~6.25e21× wrong for BSIM3. | F3 | Either is defensible. Migration is arguably less work and gains a better model. |
| **5** | **Declare a qualification temperature range.** The model files state none. | every tempco sweep | −40 … +150 °C (automotive BCD default). |

---

## 6. Fix worklist state

Phase 1 produced an 18-item worklist ordered by severity × effort. Phase 2 changed four entries:

- **`kp` re-derivation** — rescoped from 13 derivations to ~6 numbers *(pending decision 2)*.
- **`rd`/`rs` divisor** — still one divisor, but its table must be recomputed against total Ron, and
  it must be checked against the measured **channel-only floor** (1.61 Ω·µm NDMOS20, 27.22 Ω·µm
  NDMOS200). **Ordering constraint: re-derive `kp` before `rd`/`rs`** — the floor is set by the same
  defective `kp`, so fixing `kp` downward raises it. The two defects are independent but coupled
  through this floor.
- **`ksubthres` ladder** — the sub-Boltzmann clause is struck; the slope clause stands at unchanged
  severity. Any re-laddering must target *measured S*, not `1000·ksubthres`.
- **NEW: make `Bavl` polarity-aware** so the PNPs get the breakdown model the NPNs have.

One coupling worth carrying: `kp` currently makes the 200 V devices *pessimistic* (subthreshold at µA
currents) while the ladder-B mismatch makes them *optimistic* by 3×. **Fixing either alone moves the
headline downstream number in a direction that will look wrong until the other lands.**

---

## 7. The harness

`pdk_validation/characterization/` — runnable end-to-end via `python run_all.py` (~7 min).

- `char_lib.py` — deck templating, ngspice invocation, output parsing, extraction helpers, a Monte
  Carlo driver that spawns **one process per sample** (mandatory: ngspice re-randomises `.param
  AGAUSS` only across `-b` invocations, so a loop inside one invocation yields identical samples)
- `families/` — five modules, one per device family
- `experiments/` — the four discrimination experiments, each with its own README and verdict
- `score.py` — applies the scoring policy; exit code = unexpected hard-fail count, so a later CI
  hookup gates on *regressions against this baseline* rather than on the baseline itself
- `decks/` — 621 committed decks, each standalone: `ngspice -b <deck>`

**Deliberately not wired into CI.** That is a separate decision.

Seven ngspice behaviours cost real time and are documented for reuse — most importantly that
**ngspice keeps the first definition of a model name and silently discards later ones**, so isolation
copies cannot shadow a PDK card. Anything relying on shadowing runs on stock cards while reporting
that it changed them.

---

## 8. Document map

| document | what it is | size |
|---|---|---|
| `characterization-inventory.md` | Repo archaeology — what exists, what was fixed when, what is orphaned. The map. | 61 KB |
| `model-realism-audit.md` | Phase-1 findings, per-device tables, 18-item fix worklist | 54 KB |
| `anchor-values.md` / `.json` | Golden figures of merit — 40 devices, 447 entries with target/band/units/provenance, plus a known-artifact register so measurement noise isn't filed as bugs | 18 KB / 122 KB |
| `characterization-scorecard.md` | Phase-2 baseline: every measurement vs its anchor band, with status and the deck that produced it | 100 KB |
| `audit-vs-measurement-discrepancies.md` | **Where measurement overturned phase 1**, each with the corrected anchor entry spelled out | 22 KB |
| `pdk_validation/characterization/experiments/README.md` | The four experiment verdicts | 7 KB |

---

## 9. Caveats on this work

Stated plainly so they are not discovered later.

- **ngspice-45, not the 45.2 the repo pins.** One minor revision; it is the only install on the
  machine. The exact version string is recorded in the results file.
- **Monte Carlo is not bit-reproducible.** ngspice time-seeds `.param AGAUSS` per invocation and
  offers no settable seed. Each MC measurement records its N and its non-degeneracy check instead.
- **Of the 32 unexpected hard-fails, 13 are partly the harness's fault** — the `rd_tempco` anchor
  bands drift resistance while the harness measures total Ron. The proposal splits the figure of
  merit rather than pretending the model is that wrong. Two more (`bvceo`, zener `bv`) are
  measurement-criterion mismatches of the same kind.
- **Two bugs were introduced and caught during phase 2**: the isolation-copy mechanism was documented
  backwards, and the MC degeneracy check used an absolute quantum that flags healthy farad-scale runs.
  Both fixed; both would have produced silently wrong results.
- **`[industry]` bands carry real uncertainty.** They are typical published values, not this
  process's silicon. Where one disagrees with something the maintainer previously defended in the
  repo's own history, both positions are on the record rather than one silently overriding the other.
- **The whole library is uncalibrated by its own admission** — the README says the values are
  "physically plausible defaults rather than silicon-extracted." This audit checks internal
  consistency and physical plausibility. It cannot substitute for silicon.
