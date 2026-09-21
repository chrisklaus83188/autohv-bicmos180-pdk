# Brief v3: AutoHV statistical model, corners, and Monte Carlo — full replacement

**Repo:** `chrisklaus83188/autohv-bicmos180-pdk`
**Replaces:** `HANDOFF_mc_realism_brief.md`, `HANDOFF_mc_realism_review_REPLY.md` (filed in this
repo as `HANDOFF_mc_realism_rulings.md`), and the open questions in
`HANDOFF_mc_realism_stop1.md`. Rulings from those documents that survive are restated here;
anything not restated is void. Do not consult them for rulings.
**Evidence base still valid:** `HANDOFF_monte_carlo.md` (measured MC behaviour on ngspice-45),
`HANDOFF_mc_realism_review.md` §2 (verified repo facts), `analysis/corner_precheck.md`,
`HANDOFF_mc_realism_stop1.md` (Phase 0 findings).
**Branch:** `mc-realism` (already exists, Phase 0 partly done). **Tag at close-out:** `v3.0-stats`.
**Simulator:** ngspice-45, locally and in CI.

## 0. Intent and governance

Rebuild the PDK's statistical layer the way a fab builds one: a correlated statistical model of
global process variables is the source of truth; corners are generated from it; local mismatch
is Pelgrom-form per drawn shape; Monte Carlo is driven from outside the simulator with fixed
seeds; and every published number in the repo is regenerated from the result.

**Models are no longer frozen.** The stop-1 review established that the existing corners are
common multipliers applied uniformly (not fab-style), so model parameters may be changed
wherever they are not physically grounded. The bar for a change is: state the physics, state
the source, record the before/after. No change is made because it is convenient for a test.

**No shims.** When a parameter or interface changes meaning, change it everywhere and regenerate
what depends on it. No deprecated aliases, no compatibility modes.

**Generated files are never hand-edited.** `autohv_bicmos180_case_models.inc` becomes a generated
artifact with an AUTOGEN header; the generator's `--check` mode is a CI gate.

Out of scope: layout/PCell dimension, distance- or gradient-dependent mismatch, Verilog-A,
temperature-dependent statistical coefficients, self-heating changes.

## 1. Architecture

| artifact | role | authored or generated |
|---|---|---|
| `models/stat_model.json` | correlated global variables: origin, sharing, distribution, 1σ, source; local-mismatch coefficients per device | **authored**, reviewed at Stop A |
| `models/corners.json` | per-group ±3σ z-vectors and the `case` preset table, each with its Mahalanobis distance | generated |
| `autohv_bicmos180_case_models.inc` | model cards with every statistical parameter as one expression in `Z_*` | generated |
| `autohv_bicmos180_case.lib` | 40 wrapper subckts: `M/NF/NS`, mismatch knobs, edge bias, per-shape geometry | authored |
| `tools/gen_models.py` | JSON → `.inc` + `corners.json`; `--check` | authored |
| `tools/mc_driver.py` | external MC: mismatch / process / both / sensitivity; op / tran / ac | authored |
| `tools/corner_sweep.py` | preset list, hand-picked groups, or exhaustive 3^k over instantiated groups | authored (shares loop code with the driver) |
| `pdk_validation/preflight.py` | static checks + liveness gates | authored |
| `docs/stat-model.md`, `docs/corners.md`, `docs/mc-application-note.md`, `docs/mc-eval-task-recipe.md` | the "here is how you do it" set | authored |

### 1.1 Corner and MC interface (one mechanism)

Every statistical model parameter is one expression in a unit-normal variable:

```
vth0 = { VTH0_TT_NMOS1V8 + S_VTHN18 * Z_VTHN18 }               additive (linear)
u0   = { U0_TT_NMOS1V8   * exp(S_U0N18 * Z_U0N18) }             multiplicative (lognormal)
```

`Z_*` are top-level `.param`s resolved by mode:

| mode | `Z_*` value |
|---|---|
| corner (`PROC_ON=0`) | from `corners.json`: the active preset (`case ≥ 0`) or the per-group states (`case = -1`, `c_<GROUP>`) |
| native process MC (`PROC_ON=1`, no driver) | `AGAUSS(0,1,1)` drawn once per run per variable |
| driver process MC (`PROC_ON=1`, driver) | supplied by `alterparam` |

Globals: `case` (integer, default 0), `c_<GROUP>` for each of the 40 groups (0 typ, 1 fast/hi,
2 slow/lo, default 0, read only when `case = -1`), `PROC_ON`, `MM_ON`, `SH_ON` unchanged in
meaning. **`PROC_ON=1` with `case ≠ 0` is legal** and means "process MC centred on that corner"
(the corner's z-vector is added to the draw). `MM_ON=1` at any corner is legal.

The `_isTT/_isFF/…` selector strings and every `P_*` param are removed.

### 1.2 The three ways to run corners

1. **Presets** — `case 0…N`. Realistic sign-off set built from process modules (§3.4).
2. **Full control** — `case = -1` plus `c_<GROUP>` values. Any combination of the 40 groups.
3. **Exhaustive** — `corner_sweep.py --exhaustive`: parse the deck, find the k groups it
   instantiates, run all 3^k. Deterministic, assumption-free worst case.

A `.lib`-section veneer (`.lib autohv_corners.lib nmos18_ss`) that only sets `c_` params may be
generated for familiarity; it is optional and not used by any tool.

## 2. Phase 0 — baseline and housekeeping (partly done on `mc-realism`)

Keep what stop-1 completed. Remaining items:
1. Merge `transmission-gates` → `main` if not yet done; `mc-realism` continues in its worktree.
2. CI builds and caches ngspice-45 (done if stop-1 CI passed on 45; verify the log says 45).
3. Fix the broken CI MC check: correct the stale coefficient **and explain the 21 % gap** before
   any golden is rebaselined. Check in order: √2 pair factor; CLM gain error entering σ/µ via
   the mean; 1σ/3σ convention in the comparison; gm/Id at the check's bias vs the coefficient's
   reference. If unexplained, it is a Stop A finding.
4. Delete leftover MC file copies. **List, do not delete,** the two uncommitted edits in the main
   folder (they are Chris's).
5. Lib header 38 → 40. Commit `circuits/mc_mismatch_check/` as-is.
6. Freeze `pdk_validation/baselines/v2_2/`: every characterization JSON, golden, sizing table,
   and the 36-corner regression output at the pre-program commit. §11 compares against it.

## 3. Phase 1 — author `stat_model.json` (ends at **Stop A**)

### 3.1 Global variables

One entry per variable: `name`, `origin` (process step), `shared_by` (device groups),
`distribution` (`normal` | `lognormal`), `sigma` (1σ, in the parameter's units or as a fraction),
`source` (`the reference process` | `literature:<ref>` | `declared`), `error_bar`. The set to author (adjust to
what the 40 wrappers actually need; report deviations):

| variable | origin | shared by | distribution |
|---|---|---|---|
| `DL_POLY` | poly gate etch/litho CD | every poly-gated MOS (LV, 12 V, VDMOS family), poly resistor **width** | normal |
| `DW_ACT_LV`, `DW_ACT_HV` | active/isolation CD | LV FETs; HV FETs | normal |
| `TOX_18`, `TOX_33`, `TOX_50` | separate gate-oxide growths | 1.8 V; 3.3 V; 5 V + 12 V (rule which oxide NMOS12V/PMOS12V and each VDMOS use; report) | lognormal |
| `VTH_<dev>` | channel implant, per device | one per BSIM3 device and per VDMOS device | normal |
| `U0_<dev>` | doping/mobility residual, per device, **after** the tox dependence | one per device | lognormal |
| `RDSW_<dev>` | S/D extension | one per device (VDMOS: `RD`, `RS`) | lognormal |
| `RSH_<layer>` | one per resistive layer (poly-hi, poly-lo, N+, P+, N-well) | that layer's resistor **and** the gate-R term where the layer is gate poly | lognormal |
| `RHEAD_<layer>` | contact/silicide head | resistors of that layer | lognormal |
| `CDEN_<diel>`, `CPER_<diel>` | dielectric thickness; edge/fringe | capacitor type | lognormal |
| `IS_<bjt>`, `BF_<bjt>` | emitter/base profile | per BJT | lognormal |
| `IS_<dio>`, `RS_<dio>`, `CJ_<dio>` | per diode | lognormal |
| `BV_<vdmos>` | drift doping | per VDMOS | normal |

Dependent parameters are expressed through the variables, not given their own: e.g. `pclm`,
`vsat` follow `TOX`/`VTH` with declared sensitivities, or are held at TT with a documented
reason. **Do not create a variable for a parameter just because the old cards moved it.**

### 3.2 Grounding rule

For each `sigma`: (1) the reference process extraction if it states the quantity; (2) literature for a 0.18 µm
BCD-class process, cited; (3) declared with an error bar. Starting 3σ ranges to ground against
(not to copy): tox 3–5 %; global Vth 60–90 mV; poly CD ±10 nm; poly rsh 15–20 %; well rsh
25–30 %; MIM density 10–15 %; MOM 15–20 %; BJT β 20–30 %. The `source` column replaces the
"three-item residue" freeze in `docs/process-declarations.md`; rewrite that section as a table
generated from the JSON.

### 3.3 Local mismatch (also in the JSON)

Per device, 1σ Pelgrom coefficients in foundry units: MOS `A_VT` (mV·µm), `A_BETA` (%·µm),
`A_W`, `A_L` (µm·µm); resistors `A_RSH`, `A_W`, `A_LEND`, `SIG_HEAD` (§5.3); capacitors `A_C`
(area) and `A_CPER` (perimeter); BJT `A_VBE` (mV·µm) and `A_BF`; diodes `A_IS`. Distributions
normal. Existing values converted from `AGAUSS(0, 3σ, 3)` to 1σ; new ones grounded per §3.2.
The `A_BETA` term is new (typical 1–2 %·µm) and is a value change; record it as such.

### 3.4 Corners (generated into `corners.json`, but designed here)

- **Per-group z-vectors:** for each group, `fast`/`slow` (MOS, BJT, diode) or `hi`/`lo`
  (R, C) = the group's own variables at ±3σ with physically consistent signs (fast = Vth low,
  tox thin, CD short, rdsw low; `DL_POLY` participates in each MOS group's fast/slow). Shared
  variables are set by whichever group is selected; when two selected groups disagree on a
  shared variable, `corner_sweep` reports the conflict and the last-listed group wins — document.
- **Presets (`case`):**

| case | moves |
|---|---|
| 0 | nothing |
| 1–4 | all MOS groups FF / SS / FS / SF; passives typ |
| 5–6 | LV fast + HV slow; LV slow + HV fast |
| 7–8 | all resistor layers lo / hi |
| 9–10 | all capacitors lo / hi |
| 11–12 | BJT + diode lo / hi |
| 13–16 | slow-everything; fast-everything; SS + R lo; FF + R hi |
| −1 | read `c_<GROUP>` |

- **Mahalanobis distance** of every preset and every per-group vector under the correlated
  model is computed by the generator and written to `corners.json` and `docs/corners.md`, so
  "realistic" is a number, not a claim.

**Stop A:** deliver `stat_model.json`, `docs/stat-model.md` (one paragraph per variable: physics,
sharing, number, source), and the proposed preset table. Nothing is generated until Chris
approves.

## 4. Phase 2 — generator

`tools/gen_models.py`:
- Emits `.inc` with every statistical parameter as §1.1 expressions, TT values carried over from
  the current cards unless §3 changed them (record each change in `docs/CHANGELOG.md`).
- Emits `corners.json`. Emits the optional `.lib` veneer.
- `--check`: regenerate to a temp file, byte-compare, non-zero on drift. CI gate.
- Self-tests (numbered B-tests in §10): for every preset and every per-group vector, each
  parameter equals the closed form exactly; `Z=0` reproduces TT exactly.

## 5. Phase 3 — wrappers

### 5.1 Principle
Every drawn shape (finger, segment, copy) receives the global edge bias and an independent local
draw. Parallel shapes amplify width/perimeter bias and follow the area law on local σ; series
shapes amplify length bias and grow end/head σ with count. No `NF`/`M`/`NS`-dependent mismatch
coefficient is added.

### 5.2 MOS (8 BSIM3 wrappers: 18/33/50 N/P, NMOS12V, PMOS12V)
- `M` (exists): `AUM2 = (W/1u)(L/1u)M`; `m={NF*M}` to the inner device.
- `NF` (new): `W` is total width; inner `W={W/NF}`. `NF+1` diffusion stripes of 0.5 µm; outer
  stripes are source for even NF, one outer is drain for odd; shared stripes split half per
  finger. **Inner device receives per-finger `AD/AS/PD/PS` = total/NF** (ngspice multiplies by
  `m`). Limits reader: `W/NF ≥ Wmin_fab`.
- Gate resistance (new): `rgate = RSH_<gatepoly> · (W/NF) / (3·L·NF)` as a series gate resistor
  in the wrapper, fed by the `RSH` variable of the gate poly layer.
- Edge bias (new): in the wrapper, `WEFF = W/NF·(1+Z_W·σW) + S_DW·Z_DW_*`,
  `LEFF = L·(1+Z_L·σL) + S_DL·Z_DL_POLY`; cards' `wint/lint` unchanged.
- Mismatch knobs: `Z_VT`, `Z_BETA`, `Z_W`, `Z_L` (instance params, default 0, unit-normal
  multipliers of the 1σ). Native mode (`MM_ON=1`) draws `AGAUSS(0,1,1)` per knob; `MM_SIGMA`
  removed repo-wide. `A_BETA` applied as a multiplicative `u0` (or `delvto`-equivalent β) term.
- No `NF` on VDMOS/LDMOS/DNMOS20V (`W = n×10 µm` cells is the finger model; document). They keep
  `M`, get `Z_VT` (+ `Z_BETA` on `KP` if the model supports a clean lever; report), and the
  shared `DL_POLY`/`TOX` variables through their `*_STAT` params.

### 5.3 Resistors (5)
- `NS` series segments, `M` parallel copies. Per segment: `L_seg = L/NS + S_DL·Z_DL_*` (poly
  resistors use `Z_DL_POLY` on **width**, since the poly CD acts on the drawn width of a poly
  resistor — rule which dimension each layer's CD acts on and document), `W_seg = W + bias`.
- Nominal: `R = [ NS·(RSH·L_seg/W_seg + 2·R_HEAD(W)) + (NS−1)·R_LINK ] / M`, `R_LINK ≈ 0` ruled;
  `R_HEAD(W) = RHEAD_<layer> / (contacts_per_W · W)` with a declared contact pitch.
- Local σ (closed-form combined; document equivalence to per-piece draws):
  `σ_R²/R² = [ A_RSH²/(W·L) + A_W²/(W²·L) + NS·A_LEND²/L² + 2·NS·SIG_HEAD²/R_seg² ] / M`.
  Constraint (ruled): at the `passives_mc` reference geometry (10×10 µm, NS=1, M=1) the
  combined σ equals today's per-type lumped coefficient exactly; end+head ≤ 20 % of variance
  there. Knob `Z_R`. Limits: `L/NS ≥ Lmin_fab`.

### 5.4 Capacitors (4)
- Add a perimeter term to every capacitor model: `C = CDEN·A_eff + CPER·P_eff`, with
  `A_eff = (W+ΔW)(L+ΔL)` and `P_eff = 2(W+L)+…` per copy; MOM/fringe caps get a perimeter-dominant
  split, MIM a small one — ground the split per §3.2. This is a model change; record it.
- `M` parallel copies; edge bias per copy; local σ² = `[A_C²/A + A_CPER²/P] / M`. Knob `Z_C`.

### 5.5 BJT and diodes
- Replace area-only mismatch with `ΔVbe = A_VBE/√(area·M)` (as a series emitter voltage source
  or `delvto`-equivalent) plus `Δβ/β = A_BF/√area`; diodes `ΔIs/Is = A_IS/√area`. Knob `Z_AREA`
  renamed `Z_VBE`/`Z_BF` (BJT), `Z_IS` (diode). Existing `M` handling unchanged.

### 5.6 Convention
All coefficients 1σ, foundry units, in the JSON; wrappers reference the JSON entry by name in
a comment. `AGAUSS` third argument is a scale, not a clip — stated in the `.lib` header.

## 6. Phase 4 — driver and sweep tool

`tools/mc_driver.py --deck x.sp --mode {mismatch,process,both,sensitivity}
--analysis {op,tran,ac} --n 200 --seed 0 --scheme {iid,lhs,sobol} [--at-case k] --out r.json`
- One ngspice invocation; loop body `alterparam` → `reset` → analysis → collect, with the
  analysis as a single swappable function. `op`: `print` probes (`option numdgt=10`, never
  `echo`). `tran`: named `.meas tran` results. `ac`: named `.meas ac` results (gain, phase
  margin, bandwidth, noise integral).
- Instances enumerated by sorted hierarchical name; per-instantiation-path subckt cloning so
  each copy binds its own z params; z-matrix written into the output JSON.
- Convergence guard: failed `op`, `tran` timestep-too-small, `ac` singular, NaN or failed
  `.meas` → sample marked failed, never averaged; > 1 % failures exits non-zero.
- `sensitivity`: one-at-a-time z = ±1 per instance × term (and per global variable in
  `process`), per-term contributions and RSS. Deterministic σ for graders.
- `--at-case k`: mismatch or process MC centred on a corner.
- Output: metadata (git SHA, ngspice version, seed, scheme, N, mode, case), per-sample values,
  mean, σ, σ/µ, min/max, yield vs `--spec`.

`tools/corner_sweep.py --deck x.sp {--preset 0-16 | --groups NMOS5V0=s,RPOLY_HI=hi | --exhaustive}
--analysis … --meas …` — same loop body; `--exhaustive` parses the deck for instantiated groups
and runs 3^k; reports the worst value per measurement and which combination produced it.

## 7. Phase 5 — liveness gates (preflight, CI)
- native mismatch: σ(delvto) > 0 over 5 runs; two instances differ.
- driver: `--n 5 --seed 0` twice byte-identical; z = +1 sensitivity shift equals the JSON 1σ.
- corners: `case 1` reproduces every parameter's closed form exactly; `gen_models.py --check`.
- negative test: a fixed `.option seed` inside an in-deck loop (HANDOFF C5b) must fail the gate.
- preflight rejects `case ≠ -1` combined with any non-zero `c_<GROUP>`.

## 8. Phase 6 — documents
- `docs/stat-model.md` — variables, physics, sharing, numbers, sources.
- `docs/corners.md` — the three ways to run corners, the preset table with Mahalanobis
  distances, and the sentence: "cases 13–16 are deliberately pessimistic sign-off corners".
- `docs/mc-application-note.md` — how to run MC on anything: modes, seeds, `M/NF/NS`, corner
  vs MC, sensitivity vs sampled σ, tails, the traps that used to exist and why they are gone.
- `docs/mc-eval-task-recipe.md` — for task authors: which spec type maps to which tool
  (corner-type → exhaustive sweep or preset list, deterministic; σ-type → sensitivity mode;
  yield-type → fixed-seed MC), seed/N/scheme disclosed, thresholds kept off the noise floor,
  what to withhold (sizing guide, characterization reports).
- README: replace the MC paragraph with a pointer to the two notes and the sentence that ngspice
  has no MC directive.

## 9. Phase 7 — re-characterization and close-out
In order, each regenerating what the previous invalidated: characterization JSONs → sizing
guide (`--seed 0 --n 200 --scheme lhs`, uniform) → `MIRROR_CHAR.md`, comparator and delay
reports via `report_refresh.py` (provenance lines show seed, scheme, `case`) → passive goldens
→ corner regression re-expressed as the preset list × temperatures × supplies (from JSON, not
hard-coded) → scorecard. Then `docs/CHANGELOG.md` entry, tag `v3.0-stats`, push, verify with
`git ls-remote --tags`.

## 10. Acceptance (each a script under `pdk_validation/`; N = 200, seed 0, LHS unless stated)
- **B1** generator: every preset and per-group vector reproduces the closed form exactly; `--check` green; editing a σ in a scratch branch turns it red.
- **B2** `M=4` on NMOS5V0 mirror: σ(delvto) = σ(M=1)/2 ± 15 %. Also one LV PMOS, one 1.8 V device, NMOS12V.
- **B3** `NF=k` equals k explicit `W/k` devices exactly; Id delta vs NF=1 reported against `2(NF−1)·wint/W`; σ(delvto) invariant; junction cap monotonic; gate R ∝ 1/NF².
- **B4** edge bias: with `Z_DW_*` = +3, `NF=4` Id shift = 4× the NF=1 shift; `Z_DL_POLY` shift NF-invariant. Devices: LV NMOS, LV PMOS, NMOS12V.
- **B5** resistors: `M=4` → R/4, σ/R halves; NS sweep (1,2,5,10): nominal rises by `2(NS−1)·R_HEAD`; `Z_DL` shift 10× at NS=10; sheet/width terms flat, end/head ∝ √NS (one coefficient at a time); reference geometry reproduces old lumped σ exactly; poly resistor width co-moves with MOS `L` under `Z_DL_POLY`.
- **B6** capacitors: `M=4` → 4C, σ/C halves; perimeter term visible (C/area not constant vs size); `M` copies shift more than one 4×-area cap under `Z_DW`.
- **B7** BJT: `ΔVbe` σ scales 1/√area; diode `ΔIs` likewise.
- **B8** driver: byte-identical on repeat; op/tran/ac each on one deck (mirror; comparator offset via `.meas`; an RC or gm-C pole via `.meas ac`); sensitivity RSS vs MC σ within 10 % on the mirror, and one documented case where they diverge; failed sample reported, not averaged; `op` 200 samples < 2 s.
- **B9** process MC: mirror `--mode process` σ/µ ≪ mismatch σ/µ; single-device Idsat: FF and SS at 3–4.3σ from mean (value reported); `--mode both` variance = sum within 10 %; `--at-case 1` mean equals the FF op point.
- **B10** corners: preset regression green after regeneration; `--exhaustive` on a comparator deck runs 3^k and its worst offset ≥ the worst preset offset; two selected groups disagreeing on a shared variable produce the documented conflict message.
- **B11** liveness gates pass; C5b negative test fails as required.
- **B12** every previously published MC number in `docs/` and `circuits/` regenerated with new provenance lines; `report_refresh.py --check` green.

## 11. Pre-registered movers (report; do not tune)
| quantity | before | expected | why |
|---|---|---|---|
| NMOS5V0 mirror σ/µ, M=1 | 4.33 % | 4.3–5.0 % | `A_BETA` added; new seeds |
| σ(delvto) at M=4 | 4.96 mV | ≈ 2.5 mV | `AUM2` |
| corner regression | green | **all values move** | corners regenerated from stat model |
| process σ (NMOS1V8 vth0 etc.) | hand-set 8.3 mV | grounded, likely 20–30 mV | §3.2 |
| passive MC at reference geometry | – | unchanged | §5.3 constraint |
| passive MC away from reference | – | moves; tabulated | end/head terms |
| capacitor nominals | – | move where perimeter term added | §5.4 |
| FF preset Mahalanobis | – | ≈ 3 | by construction |
| slow-everything Mahalanobis | – | ≫ 3, reported | pessimistic by design |

## 12. Stops and reporting
- **Stop A** (end of Phase 1): stat model + preset table for approval. Nothing generated before.
- **Stop B** (end of Phase 4): generator, wrappers, driver, sweep tool working; B1–B11 tabulated.
- Close-out: B12, tag, push, `HANDOFF_v3_stats_results.md` with the B-table, every model change
  with physics and source, every ruling deviated from and why, the Mahalanobis table, and the
  remote verification output.
Push `mc-realism` at every phase commit.
