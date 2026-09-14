# Reply: MC realism program — rulings on the pre-start review

**Responds to:** `HANDOFF_mc_realism_review.md` (C1–C16, Q1–Q15)
**Amends:** `HANDOFF_mc_realism_brief.md` (R0–R7, A1–A15, §8). Where this document and the
brief differ, this document wins. Numbering below refers to the brief.
**Date:** 2026-09-14
**Status:** all questions closed. Phase 0 may start.

## 1. Rulings on the seven forks

| # | topic | ruling |
|---|---|---|
| D1 | asymmetric corners (Q7, C7) | Corner numbers stay untouched. σ-form is chosen **per parameter** by the generator: linear `TT ± 3σ` where the cards are additive-built, log-space `TT·exp(±3s)` where they are multiplicative-built (reciprocal multipliers: `u0`, `rdsw`, VDMOS `RD/RS/KP`, BJT `rb/rc/re/tf/tr/bf`, diode `rs/tt`, resistor `rsh`). Selection rule is mechanical: the form with the smaller max reconstruction error over FF/SS. The chosen form is recorded per parameter in the derived JSON. Rationale: a lognormal on a resistance or mobility is the physically grounded distribution (positive-definite, and it is how the cards were evidently constructed); a Gaussian on those parameters is not. A12 is redefined in §3. |
| D2 | `NF` on VDMOS/LDMOS/DNMOS20 (Q12, C12) | **Omitted** for that family. `W = n × 10 µm` cells with the 3 µm minimum is already the finger model; an `NF` with no electrical lever would be a silent no-op. State this in the MC application note. A2b runs on LV NMOS, LV PMOS, and NMOS12. |
| D3 | edge-bias variables (Q2, C2) | `PROC_Z_DL` and `PROC_Z_DW` are **declared** in the derived JSON as the one documented exception to R7 (not derived from corners). σ = 0 by default; TT value = the cards' existing fixed `wint/lint` (MOS) and `narrow/short` (R). Wrapper plumbing is wired now. A2b and A4(ii) run with a nonzero σ set in the test harness only. Grounding the σ is deferred to a later decision; A13 holds because σ = 0 changes nothing. |
| D4 | residue freeze (Q9, C9) | Amend `docs/process-declarations.md` with **one** scoped fourth residue item: "resistor mismatch decomposition and contact head (R3)" — `A_RSH/A_W/A_LEND` split, `σ_head`, `R_head`, `R_link ≈ 0` — each with an error bar. |
| D5 | reference geometry for R3 (Q9) | The geometry used in `pdk_validation/characterization/decks/passives_mc/` is the reference. At that geometry (NS=1, M=1) the combined σ reproduces today's lumped `0.03182/√(W·L)` **exactly**, so existing resistor MC results are unchanged. End and head terms are sized to carry ≤ 20 % of the variance there. |
| D6 | β mismatch term (Q4, C4) | **Deferred.** MOS knobs are `Z_VT`, `Z_W`, `Z_L` only. Add "Pelgrom A_β term — value change, needs grounding" to the follow-up list in the results handoff. |
| D7 | driver analysis scope (Q13b, C13) | **Both `op` and `tran` in scope for v2.3.** See §4. |

## 2. Rulings on Q1–Q15

| Q | ruling |
|---|---|
| Q1 | Accept. Merge `transmission-gates` → `main`; branch `mc-realism` from `main` in a separate `git worktree`; main tree's uncommitted xschem/backlog edits are untouched. |
| Q2 | D3. |
| Q3 | Accept. A2 rewritten in §3. |
| Q4 | Accept: `Z_VT/Z_W/Z_L` (BSIM3 MOS), `Z_VT` (VDMOS family), `Z_AREA` (BJT, diode), `Z_R` (resistor), `Z_C` (capacitor). No β term (D6). |
| Q5a | Accept. Rewrite only the `+P_X` / `*(1+P_X)` tail of each of the 186 expressions; the `_isXX` selector text and every corner number stay byte-identical. A13 guards. |
| Q5b | Accept, scoped: preflight rejects `PROC_ON=1` with `case≠0`. `MM_ON=1` with `case≠0` remains legal (mismatch at a corner is a standard run). |
| Q6 | Accept. C6 table goes into §8 as pre-registered movers. |
| Q7 | D1. |
| Q8 | Accept. Grouping = pattern × family × voltage class; one shared `TOX` variable (cards move tox identically across classes); separate variables per resistor type, capacitor type, diode, NPN, PNP. Within a group the parameters are 100 % correlated — that is what the cards say. A14 band: FF/SS Idsat within 3–4.3σ, value reported. |
| Q9 | D4 + D5. |
| Q10 | Accept: 0.5 µm is the drawn stripe width for outer and shared inner stripes (not a new number); a shared stripe's area and perimeter split half to each adjacent finger; `NF+1` stripes, outer stripes are source when NF is even, one outer stripe is drain when NF is odd. **ngspice multiplies `AD/AS/PD/PS` by `m`, so the inner device receives the per-finger share (`total/NF`), not the total.** |
| Q11 | Accept. Keep `M` on all 13 HV wrappers (already R1-correct via `mtot`); apply the `AUM2` fix to NMOS12/PMOS12 as well as the six LV BSIM3 wrappers. Scope table corrected in §3. |
| Q12 | D2. |
| Q13a | Accept. Per-instantiation-path subckt cloning (`AMP` → `AMP__x1`, `AMP__x2`), each binding its own top-level z params; hierarchical probe paths preserved. |
| Q13b | D7. |
| Q14 | Accept. Build and cache ngspice-45 in `.github/workflows/regression.yml` as a Phase 0 item. Every results JSON records `ngspice --version`. |
| Q15 | Accept. Review stops after Phase 0 and after Phase 3 (each with a short results note); push `mc-realism` at each phase commit; tag `v2.3-stats` and `git ls-remote --tags` verification at close-out only. |

No ruling needed on C15; the correction is adopted: the `AUM2` fix changes MC σ only for `M>1`
instances (nominals unchanged), not "published mismatch numbers" wholesale. Fix the lib header
(38 → 40 subckts) in Phase 0.

## 3. Amendments to the brief

**Scope table (Phase 1)** — replace with:

| family | `M` | `NF` / `NS` |
|---|---|---|
| BSIM3 MOS: NMOS/PMOS 18/33/50 and NMOS12/PMOS12 | fix `AUM2` (already have `M`) | `NF` add |
| VDMOS/LDMOS/DNMOS20 (13 wrappers) | keep (already correct) | none (D2) |
| resistors (5) | add | `NS` add |
| capacitors (4) | add | – |
| BJT, diodes | no change | – |

**R0** — the Phase-0 prerequisite check is answered: no corner moves geometry. Replace the
"grounding decision for Chris" sentence with D3.

**R2** — replace "F6 extension lengths" with the Q10 stripe rule. Drop the gate-resistance
bullet (no term exists; listed as follow-up). Drop the VDMOS `NF` mapping paragraph (D2).

**R3** — coefficients per D4/D5. `DL_bias/DW_bias` TT values are the R cards' `short/narrow`;
their σ is `PROC_Z_DL/DW` per D3.

**R5** — knob names per Q4. Delete `Z_BETA` and `Z_GEOM`. R4's "< 1e-6 notation-only"
acceptance stands (no value change is introduced).

**R7** — items 1–5 stand, with: (i) "no literal cards" is understood; derivation evaluates each
expression per case and rewrites only the `P_*` tail (Q5a); (ii) σ-form per parameter per D1;
(iii) grouping per Q8; (iv) `PROC_Z_DL/DW` declared per D3.

**A2** — replace with: `NF=k` equals k explicitly instantiated `W/k` devices (exact, independent
construction); the Id delta vs `NF=1` is reported alongside the analytic `2(NF−1)·wint/W`
prediction; σ(delvto) unchanged within 3 %; total junction capacitance decreases monotonically
with NF.

**A2b** — devices: LV NMOS, LV PMOS, NMOS12 (no VDMOS). Bias driven by setting `PROC_Z_DW`/`DL`
σ nonzero in the harness (D3).

**A4(ii)** — same harness mechanism for the resistor length-bias 10× check.

**A12** — replace with: for every corner, the z-vector reproduces the *ruled model value*
(`TT ± 3σ` or `TT·exp(±3s)` per the recorded form) exactly, **and** the deviation of that value
from the literal card is ≤ 1.5 %, tabulated per parameter in the results handoff. Failure of the
first half means the generator or plumbing is wrong; failure of the second half is reported, never
fixed by editing a card.

**A14** — band 3–4.3σ, value reported (Q8).

**§8** — add the C6 rows (NMOS18 vth0 8.33 → 26.7 mV, u0 3.33 → 5.67 %, PMOS18 u0 3.33 → 6.33 %,
tox correlation change, NDMOS20 vto 13.3 → 16.7 mV, kp 3.33 → 5.00 %) and: "every `PROC_ON=1`
result in the repo moves, e.g. mirror process+mismatch 1.344 %".

**Phase 0** — add: CI ngspice-45 build (Q14); lib header count; commit `circuits/mc_mismatch_check/`
as-is (its 2026-09-14 re-run is byte-identical to the stored JSON).

## 4. Driver scope (D7 detail)

`tools/mc_driver.py --analysis {op,tran}`:
- The per-sample loop body is `alterparam …` → `reset` → *analysis* → collect. The analysis is
  the only thing that changes between modes; implement it as one function.
- `op`: probes are `print` expressions (`@m.x1.m0[delvto]`, `i(vout)`, …) as in the brief.
- `tran`: the deck supplies named `.meas tran` statements; the driver collects each named
  measurement per sample. Probes may also be expressions on the final time point.
- Convergence guard covers both: failed `op`, `tran` timestep-too-small, and any measurement
  returning NaN/failed count as a failed sample (recorded, not averaged; > 1 % fails the run).
- `sensitivity` mode works for both analyses (one-at-a-time z = ±1 on each knob, RSS).
- Acceptance: A7–A10 run in both modes on the mirror (`op`) and on one comparator deck from
  `circuits/comparators/` (`tran`, offset via `.meas`). A11's < 2 s target applies to `op` only;
  `tran` runtime is reported, not gated.
- Per-path subckt cloning (Q13a) applies to both.

## 5. Now closed

Every C1–C16 item has a ruling above. Remaining follow-ups (not this program): grounding
`PROC_Z_DL/DW` σ; Pelgrom A_β term; gate-resistance term; a two-sided σ form if the ≤ 1.5 % card
deviation table shows anything worth chasing.
