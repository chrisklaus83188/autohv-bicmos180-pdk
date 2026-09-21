# Handoff: MC realism program — multipliers, fingers, statistical model overhaul, external driver

**Repo:** `chrisklaus83188/autohv-bicmos180-pdk`
**Base:** `main` at v2.2-defaults (confirm with `git describe`; if `main` is behind a branch, stop and report)
**Simulator:** ngspice-45 (pin in CI; also run the final scorecard on whatever CI uses)
**Prior context:** `HANDOFF_monte_carlo.md` (read it first — it holds the measured evidence every ruling below rests on)
**Program tag at end:** `v2.3-stats`

## 0. Intent and non-goals

Make the PDK's statistical modelling structurally realistic and make MC results deterministic
enough to grade in LLM eval tasks. The two goals are the same work: every "trap" found in the
prior session is a realism defect, and the fixes remove the traps.

This is a structural program, not a patch set. Do not add compatibility shims, deprecated
aliases, or "legacy mode" switches. When a parameter changes meaning, change it everywhere in
the repo and regenerate what depends on it.

Out of scope (do not start): layout/PCell dimension, distance- or gradient-dependent mismatch,
Verilog-A, temperature-dependent mismatch coefficients, any model-card (BSIM/VDMOS) parameter
edit that is not a statistical parameter. Models stay at their v2-grounded values, and
the corner cards (TT/FF/SS/FS/SF and any others) are **frozen** — Phase 4 derives from
them, it does not edit them.

## 1. Baseline capture (Phase 0)

Before touching anything, freeze a baseline that later phases must reproduce or explain.

1. Commit `circuits/mc_mismatch_check/` as-is (it is untracked). Regenerate `REPORT.md`.
   Also commit or stash the unrelated transmission-gate deliverable so the tree is clean.
2. Record `git rev-parse HEAD`, `ngspice --version`, and the values from HANDOFF §1
   (200-run NMOS5V0 mirror: σ/µ = 4.33 %, σ(delvto) = 5.263 mV) into
   `pdk_validation/baselines/mc_baseline_v2.2.json`.
3. Enumerate every wrapper in the `.lib` files and produce `docs/stat-model-inventory.md`
   with one row per device: family (LV FET / HV FET / VDMOS / BJT / diode / R / C),
   rated voltage, current instance parameters, whether it has a mismatch block, which
   mismatch terms it has, the coefficient and convention (1σ or 3σ), and what `AUM2`
   or equivalent area term it computes. This table is the work list for Phases 1–2.
   Classify FETs by the `device_limits` rated voltage, not by name.
4. Capture the in-session experiments from HANDOFF §3 and §4 (M sweep, runtime table,
   external-driver prototype) as committed scripts under `circuits/mc_mismatch_check/`.
   They become regression evidence for Phase 1.

## 2. Multipliers and fingers (Phase 1)

### Scope

| family | `M` | `NF` |
|---|---|---|
| LV FETs (1.8 V, 3.3 V, 5 V classes) | add | add |
| HV FETs incl. VDMOS/LDMOS, NMOS12V, DNMOS20V | **no** | add |
| resistors | add | `NS` series segments instead (R3) |
| capacitors | add | – |
| BJT, diodes | no change | – |

### Rulings (apply as written; flag disagreement in the report rather than deviating)

**R0 — Every drawn instance is subject to lithography error, globally and locally.**
Every finger, segment, or copy is a separately drawn shape. Global edge bias (`DL`/`DW`,
corners and Phase-4 process variables) is applied per drawn shape; local mismatch is
drawn independently per shape. The wrapper implementations below (`W/NF` with `m=NF`,
per-segment `L/NS + DL_bias`, per-copy capacitor perimeter) exist to make that true by
construction. The *results* differ by topology and that is expected physics, not an
inconsistency to fix:
- parallel shapes (MOS `NF`, MOS `M`, cap `M`): width/perimeter bias is amplified
  `NF×`/`M×`, length bias is not; local σ follows the area law (independent draws average).
- series shapes (resistor `NS`): length bias is amplified `NS×`, width bias is not; local
  end and head terms grow with NS, sheet and width terms follow the area law.
No NF- or M-dependent *mismatch* coefficient is added anywhere — that is beyond
professional-grade model sets. NF-dependent parasitics (shared diffusions, gate R) are
covered in R2. Prerequisite to check in Phase 0 and report: the corner cards must move
model geometry parameters (`lint`/`wint`/`dwc`/`dlc`/`xl`/`xw` or the VDMOS equivalents),
not only Vth/mobility; if they do not, the per-shape edge bias has no lever and this is a
grounding decision for Chris, not something to fill in.

**R1 — `M` means M identical, independent, parallel copies.**
Electrical: every extensive quantity scales ×M (current, capacitance, 1/R). Implement by
passing `m={M}` to the inner device so the model handles it natively; do not hand-scale
parameters. Statistical: independent copies average, so all local-mismatch σ scale as
`1/sqrt(M)`. The area term becomes `AUM2={(W/1u)*(L/1u)*M}` in every MOS wrapper, and the
resistor/capacitor equivalents get the same factor. Integer, ≥ 1, default 1.

**R2 — `W` is total width; `NF` splits it into `NF` fingers of `W/NF` each.**
This matches the dominant foundry-PCell convention. Consequences:
- Inner device: `W={W/NF}`, `m={NF*M}` (LV) or `m={NF}` (HV), with `L` unchanged.
- `AD/AS/PD/PS`: computed per finger with shared diffusions — for `NF` fingers there are
  `NF+1` diffusion stripes of which `NF-1` are shared; outer stripes get the full
  contact-to-gate extension, inner stripes half. Use the extension lengths already declared
  in the F6 work (`docs/process-declarations.md`); do not introduce new numbers.
- Mismatch area is total area `W·L·M`. **`NF` does not appear in `AUM2`.** Fingering does
  not change the device's total area or its matching; it changes junction capacitance and
  gate resistance.
- Gate resistance: if the wrappers already carry an `rgate`/`rsh_poly` term, scale it as
  `1/NF²` (per-finger length ÷NF, and NF in parallel). If they do not, do not add one in
  this program — note it in `docs/stat-model-inventory.md` as a follow-up.
- Geometry checks: the limits reader must enforce `W/NF ≥ Wmin_fab` (per finger), not
  `W ≥ Wmin_fab`. Integer, ≥ 1, default 1.
- VDMOS: the existing cell/finger structure (10 µm cell, 3 µm Wmin clamp) is the finger
  model. Map `NF` onto it without changing any DC/AC parameter; if the existing wrapper's
  width handling conflicts with R2, stop and report the conflict with the two options.

**R3 — Resistors get `NS` (series segments) and `M` (parallel copies); capacitors get `M`.**
`NS` is *not* fingering. A `W=1u L=100u NS=10` resistor is ten `W=1u L=10u` bodies in
series, each with its own two contact heads, joined by metal. Consequences:
- Nominal: `R = M⁻¹ · [ NS·(Rsh·(L/NS)/W + 2·R_head(W)) + (NS−1)·R_link ]`. `R_head(W)` is
  the contact-plus-end resistance of one head (contact resistance ÷ contacts-per-width,
  plus the end/spreading term); `R_link` is the metal strap between segments (may be ruled
  ≈ 0 if the process declarations have no number). A segmented resistor is therefore
  *higher* than the unsegmented one by `2(NS−1)·R_head + (NS−1)·R_link` — this must be
  visible in simulation. If the resistor wrappers have no head-resistance term today,
  ground one from the reference process contact-resistance data and add it; if nothing is available,
  declare a value in the synthetic-residue list with an error bar.
- Geometry realized per segment, not per total: every segment is
  `L_seg = L/NS + DL_bias`, `W_seg = W + DW_bias`, where `DL_bias`/`DW_bias` are the
  process-side edge biases (TT-nominal, shifted by corners and by the Phase-4 global
  `DL`/`DW` variables). Because the bias is applied `NS` times in series, a segmented
  resistor's sensitivity to length bias is `NS×` that of the single resistor; width-bias
  sensitivity is unchanged. **The wrapper must apply the bias per segment — never to the
  total L.** This is the systematic (correlated) part of "unit segments don't reproduce
  the single resistor".
- Local mismatch, term by term, all segments and heads drawing independently:
  | term | per-segment σ² (relative) | scaling with NS after combining |
  |---|---|---|
  | sheet ρ | `A_RSH² / (W·L_seg)` | invariant (area law) |
  | width edge | `A_W² / (W²·L_seg)` | invariant (averages) |
  | length/end | `A_LEND² / L_seg²` (two ends per segment) | `×NS` in variance |
  | head | `σ_head²` per head, 2 per segment | `×NS` in variance |
  Combined on the single two-terminal element:
  `σ_R²/R² = [ A_RSH²/(W·L) + A_W²/(W²·L) + NS·A_LEND²/L² + 2·NS·σ_head²/R_seg² ] / M`
  (one draw with this σ is statistically identical to the NS·(2NS+1) separate draws it
  represents, since a sum of independent Gaussians is Gaussian; document the equivalence
  and the derivation in the wrapper comment). One `Z_R` knob per resistor instance in
  external mode.
- Net effect to verify: segmenting is `NS×` worse on systematic length bias and `√NS` worse
  on the random end and head terms; sheet and width terms are unaffected. A single large
  resistor and an NS-segment unit array of the same drawn W×L must therefore differ in
  both nominal and σ, with the gap growing with NS.
- Geometry checks: `L/NS ≥ Lmin_fab` per segment; `W ≥ Wmin_fab`. Integer, ≥ 1, default 1.
- Capacitors: `M` parallel copies only; `C·M`, σ_C/C = `A_C/√(area·M)`, with the
  process-side edge bias applied per copy (perimeter term), same principle.
- If R or C wrappers lack a local-mismatch term entirely, add one in the form above.
  Coefficients (`A_RSH`, `A_W`, `A_LEND`, `A_C`, `σ_head`, `DL_bias`, `DW_bias`): ground
  from the reference process documentation on hand where it states matching or edge bias; otherwise
  declare a literature-typical value and add it to the synthetic-residue list in
  `docs/process-declarations.md` with an error bar. Do not invent silently, and do not
  collapse the terms into one lumped `A_R` — the NS behaviour depends on keeping them
  separate.

### Acceptance (Phase 1)

Each is a script under `pdk_validation/`, N = 200 fixed-seed samples, ±15 % tolerance on σ
unless stated:
- A1: NMOS5V0 mirror W=4.7 L=1: `M=4` gives σ(delvto) = σ(M=1)/2. Baseline showed 4.96 mV
  unchanged; expected ≈ 2.5 mV. Same test on one PMOS LV device and one 1.8 V device.
- A2: `NF` sweep at constant W (NF = 1, 2, 4): σ(delvto) unchanged within 3 %; Id at fixed
  bias unchanged within 1 %; total junction capacitance decreases monotonically.
- A2b: with the width bias driven (corner card or `PROC_Z_DW=+3`), the Id shift of an
  `NF=4` device is that of an `NF=1` device of the same total W with 4× the width bias
  (equivalently: matches a single `W/4` device ×4); with the length bias driven the shift is
  NF-invariant. Same test for `M=4`. Capacitor `M=4` under perimeter bias shifts more
  than one `4×`-area capacitor. Run on one LV NMOS, one LV PMOS, and one VDMOS.
- A3: `M=4` vs `W=4×`: Id equal within model narrow-width effects (report the delta; it is
  not required to be zero).
- A4: resistor `M=4`: R/4 and σ(R)/R halves. Resistor `NS` sweep (1, 2, 5, 10) at fixed
  drawn W, L: (i) nominal rises by `2(NS−1)·R_head + (NS−1)·R_link` at zero edge bias;
  (ii) with the corner (or `PROC_Z_DL=+3`) length bias applied, the nominal shift of the
  NS=10 array is 10× that of NS=1, and the width-bias shift is equal; (iii) mismatch
  σ/R decomposed by term — sheet and width terms flat vs NS, end and head terms growing
  as √NS — verified by zeroing all but one coefficient at a time. `NS=10, M=10` returns R
  to ≈ the NS=1 value plus the head penalty. Capacitor `M=4`: 4C and σ(C)/C halves.
- A4b: limits reader rejects `L/NS < Lmin_fab`.
- A5: limits reader rejects `W/NF < Wmin_fab`, accepts `W ≥ Wmin_fab` with `NF=1`.
- A6: repo-wide sweep — every existing instantiation with `M` or `NF` absent still simulates
  identically (defaults are 1). Regression (smoke/corners/passives/transients) unchanged
  before Phase 2 begins.

## 3. Mismatch convention and knobs (Phase 2)

**R4 — All coefficients are 1σ, quoted in foundry units.** Rewrite every
`AGAUSS(nom, 3σ, 3)` as `AGAUSS(nom, σ, 1)`. Name the constants `A_VT` (mV·µm), `A_BETA`
(%·µm), `A_L`/`A_W` (µm·µm) per device, and put the numbers in a single table in
`docs/process-declarations.md` — that table is the source of truth; wrappers reference it
by comment. Acceptance: with identical seeds, σ(delvto) before/after the rewrite agrees to
< 1e-6 relative (this is a notation change, not a value change).

**R5 — Three independent per-instance z-knobs replace `MM_SIGMA`.**
Instance parameters `Z_VT`, `Z_BETA`, `Z_GEOM` (default 0), each a unit-normal multiplier
applied to that term's 1σ. When `MM_ON=1` the wrapper draws `AGAUSS` internally (native
mode, kept for standalone use); when `MM_ON=0` the knobs apply. Remove `MM_SIGMA`
entirely and sweep the repo for uses. The wrapper keeps computing σ from geometry — the
driver supplies only z. Acceptance: with `MM_ON=0`, setting `Z_VT=1` on one instance
shifts its `delvto` by exactly the 1σ value from the table; `Z_BETA` and `Z_GEOM` set
independently produce independent shifts.

**R6 — Document the distribution.** `AGAUSS`'s third argument scales; it does not truncate.
State this in the `.lib` header and README. No truncation is added.

## 4. External MC driver (Phase 3)

Ship `tools/mc_driver.py` (with `pdk_validation` importing it, not the reverse).

Interface:
```
mc_driver.py --deck design.sp --mode {mismatch,process,both,sensitivity}
             --n 200 --seed 0 --scheme {iid,lhs,sobol}
             --probe "@m.x1.m0[delvto]" --probe "i(vout)" ... --out results.json
```
Behaviour:
- Enumerates statistical instances in the deck (sorted by hierarchical instance name, not
  netlist order) so a given `(seed, instance name)` always yields the same z regardless of
  how the netlist is arranged. This is what makes grading reproducible across
  reformulations of the same design.
- Generates the z-matrix in NumPy (`default_rng(seed)`; LHS/Sobol via `scipy.stats.qmc`),
  writes it into the output JSON alongside the results.
- Runs **one** ngspice invocation: `.option numdgt=10`, `MM_ON=0`, and a `.control` loop of
  `alterparam` (all knobs for one sample) → `reset` → `op` → `print` of every probe. Never
  `echo` (6-sig-fig rounding, HANDOFF §2).
- Per-sample convergence guard: parse ngspice output for failed `op` (no-convergence,
  singular matrix, timestep) and for any probe that is NaN or hits a supply rail; failed
  samples are recorded as failed, **not** dropped and not averaged in. If more than 1 % of
  samples fail the run exits non-zero.
- `sensitivity` mode: one-at-a-time, each instance × each term set to z = +1 (and −1 to
  report asymmetry), returning per-term contributions and the RSS total. This is the
  deterministic, sampling-noise-free σ estimate; it is what eval graders should use for
  σ-type specs.
- Output JSON: metadata (git SHA, ngspice version, seed, scheme, N, mode), per-sample probe
  values, mean, σ, σ/µ, min/max, and yield against optional `--spec probe<value` limits.

Acceptance (Phase 3):
- A7: `--mode mismatch --seed 0` twice → byte-identical JSON. Different seed → different
  samples, σ within sampling noise.
- A8: NMOS5V0 mirror: driver σ/µ vs native `MM_ON=1` per-invocation `.option seed=k` σ/µ
  agree within 10 % at N = 200. The old single-knob prototype gave 3.71 %; with three
  independent knobs expect ≈ 4.0–4.3 %.
- A9: `sensitivity` RSS vs MC σ agree within 10 % on the mirror (linear regime). Record a
  case where they should *not* agree (a comparator or clipped output) to document the limit.
- A10: a deliberately unconverged sample (e.g. absurd z) is reported as failed, not averaged.
- A11: 200 samples in < 2 s wall clock on the mirror (baseline 0.7 s).

## 5. Global process variables and corners from the stat model (Phase 4)

This is the largest structural change. Do it after Phases 1–3 are green and committed.

**R7 — The corner cards are the source of truth. The process stat model is *derived from*
them, never the reverse.** No corner card is edited in this program. Corner simulation
(`case=`) continues to select the literal cards, unchanged. Only the `PROC_ON=1` path is
rewired.

Mechanism — a generator, not a hand-maintained table:
1. `tools/derive_stat_model.py` parses TT and every corner card and computes, for each
   model parameter that differs from TT in any corner, the per-corner δ = corner − TT.
   Output: `models/stat-model-derived.json` (committed, AUTOGEN-fenced, `--check` mode
   fails CI if the corner cards changed without regeneration).
2. Group parameters into global variables by co-movement across corners. Rule: a parameter
   that moves in the same direction in FF/SS for both NMOS and PMOS, and does not move in
   FS/SF, is a **shared** variable (`TOX`, `DL`, `DW` are the expected members). A
   parameter that moves oppositely between NMOS and PMOS in FS/SF is a **per-type**
   variable (`VTHN`, `VTHP`, `U0N`, `U0P`, …). Passives, BJTs, and anything that moves in
   only one corner get their own variable. Report the inferred variable list; do not
   assume the candidate names above.
3. σ per variable: `σ = (FF − SS)/6` on each parameter (equivalently δ/3 when symmetric),
   so `z = +3` lands on FF and `z = −3` on SS. **Asymmetry ruling:** where TT is not the
   midpoint of FF and SS, use `(FF − SS)/6` anyway, centre at TT, and list the parameter
   and its asymmetry in the report. Corner sims are unaffected. (Chris may later rule a
   two-sided σ; do not implement one now.)
4. Wrapper plumbing: each stat parameter in `PROC_ON=1` mode is
   `TT + Σ_k (δ_k/3)·PROC_Z_k`, where `PROC_Z_k` are top-level `.param`s (default 0) that
   the driver sets with `alterparam`. Native random mode (`PROC_ON=1`, no driver) draws
   each `PROC_Z_k` once per run via `AGAUSS(0,1,1)`, so all instances share it.
5. A corner is now also expressible as a z-vector (`FF ≡ PROC_Z_VTHN=+3, PROC_Z_VTHP=+3,
   PROC_Z_TOX=…`); document these vectors in the derived JSON. This is for the driver and
   the liveness gate only — `case=` keeps using the cards.

Acceptance (Phase 4):
- A12: for every corner, setting its z-vector with `PROC_ON=1` reproduces every parameter
  of the literal card within 1 % (exact where symmetric). This is a generator self-test;
  failure means the generator or plumbing is wrong, never that a card should be edited.
- A13: the 36-corner regression is byte-identical before and after (cards untouched, path
  untouched).
- A14: `mc_driver.py --mode process` on the NMOS5V0 mirror gives σ/µ ≪ mismatch σ/µ (the
  ratio cancels global shifts); on a single-device Idsat probe it gives σ such that the
  FF and SS Idsat sit at ≈ ±3σ from the mean. `--mode both` samples process and
  per-instance mismatch together and its variance is the sum of the two within 10 %.
- A15: `derive_stat_model.py --check` is green; deliberately editing a corner card in a
  scratch branch makes it red.

If a corner card contains a parameter change that cannot be expressed as `TT + coef·z`
(e.g. a model-level flag or a different model type per corner), leave that parameter out
of the stat model, keep it corner-only, and list it in the report. Do not modify the card.

## 6. Liveness gate (Phase 5)

Add to `pdk_validation/preflight.py`, documented in `docs/geometry-minima.md` as a hard
regression gate:
- native mode: 5 samples with `MM_ON=1`, assert σ(delvto) > 0 and two instances in one
  deck draw different `delvto`;
- external mode: `mc_driver.py --n 5 --seed 0` twice, assert byte-identical, and assert the
  z = +1 sensitivity shift equals the table 1σ;
- process mode: `PROC_Z_VTHN=+3` reproduces the FF Vth within 1 %.
The gate must fail on a deck with a fixed `.option seed` inside an in-deck loop (HANDOFF C5b)
— add that as a negative test.

## 7. Re-characterization, documentation, close-out (Phase 6)

Order matters; each step regenerates what the previous invalidated.
1. Re-run the mismatch characterization behind the sizing guide with the driver
   (`--mode mismatch --seed 0 --n 200`, uniform N as ruled in GR2). The σ column for
   `M=1` entries must be unchanged within sampling noise (nothing physical changed for
   them); add an "analog-min with M" note where `M>1` is now the cheaper way to hit a σ
   target than widening.
2. Regenerate `MIRROR_CHAR.md` and the comparator reports through `report_refresh.py`
   (AUTOGEN fences, `--check` green). Provenance lines must now show seed and scheme.
3. Regenerate passive goldens and the full scorecard; regression must be green.
4. Docs: correct the reproducibility claim in `circuits/current_mirror_char/run_mc.py`
   (`set rndseed` does not pin draws — either switch it to the driver or `.option seed`);
   close `docs/characterization-inventory.md` item 22 with a pointer to C5b; add to the
   README the sentence "ngspice has no Monte Carlo directive; use `tools/mc_driver.py`";
   write `docs/mc-application-note.md` covering modes, seeds, the `M`/`NF` semantics
   (R1/R2), the 1σ convention, the tail behaviour, and the sensitivity-vs-MC choice.
5. Update `docs/stat-model-inventory.md` to the after-picture.
6. Tag `v2.3-stats`, **push, and verify with `git ls-remote --tags`**. The push is an
   acceptance criterion; the program is not complete without it.

## 8. Pre-registered expected movers

| quantity | before | expected after | why |
|---|---|---|---|
| NMOS5V0 mirror σ/µ, M=1, N=200 | 4.33 % | 4.0–4.6 % | notation-only change + new seeds |
| σ(delvto) at M=4 | 4.96 mV | ≈ 2.5 mV | R1 |
| σ(delvto) vs NF at fixed W | not measured | flat | R2 |
| external-driver σ/µ | 3.71 % | ≈ 4.0–4.3 % | three independent knobs |
| sizing-guide σ column, M=1 | – | unchanged | nothing physical changed |
| 36-corner regression | green | green, unchanged | A13 |
| 200-sample runtime | 0.7 s | < 2 s | driver overhead |

Anything that moves outside these bands is a finding to report, not to tune away.

## 9. Reporting

Produce `HANDOFF_mc_realism_results.md` at the end with: per-phase acceptance table
(pass/fail with measured numbers), every ruling you disagreed with and why, every place
the inventory showed a wrapper that did not fit the R1/R2 pattern, the synthetic-residue
additions from R3, and the final tag + remote verification output. Keep the prior
handoff's format — tables of measured values, not prose claims.
