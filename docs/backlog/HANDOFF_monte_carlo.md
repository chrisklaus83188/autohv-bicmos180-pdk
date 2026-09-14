# Handoff: Monte Carlo setup — verification, traps, eval-task design, improvements

## Summary

Monte Carlo **works** in this PDK on ngspice-45: local-mismatch draws are live and
independent per instance. A 200-run mismatch-only MC on a simple NMOS50 current mirror
gives **σ/µ = 4.33 %**, matching both the sizing guide (4.08 %) and a hand calculation
from the wrapper's own mismatch expression (4.01 %) within sampling noise.

Along the way the session found two seeding traps, one real wrapper defect (the `M`
multiplier does not reduce mismatch), and worked through what an LLM-eval task built on
this exercise would need. Nothing below has been committed, and no PDK file was changed.

Status of the work tree when this was written: `circuits/mc_mismatch_check/` is
untracked. Its `decks/` folder is gitignored (regenerable). An unrelated transmission-gate
deliverable is also uncommitted in the same tree.

## 1. What was run

Directory: `circuits/mc_mismatch_check/`

| file | purpose |
|---|---|
| `mc_lib.py` | shared circuit, ngspice runner, stats helpers |
| `00_mc_mechanism.py` | checks C1–C6: does MC randomize, and which drive patterns are reproducible |
| `01_mc_mirror.py` | the 200-run mirror measurement plus analytic cross-check |
| `report.py` → `REPORT.md` | full write-up generated from `results/*.json` |

```bash
cd circuits/mc_mismatch_check
python 00_mc_mechanism.py
python 01_mc_mirror.py
python report.py
```

Device under test: two-transistor NMOS mirror, both `NMOS50` W = 4.7 µm, L = 1 µm (the
sizing guide's gm/Id ≈ 6 entry for NMOS50 at 10 µA). Ideal 10 µA into the diode-connected
device, output held at 2.5 V. TT (`case=0`), 5.0 V, 27 °C, `MM_ON=1`, `PROC_ON=0`.
Seeds 1..200, one ngspice invocation each, so results are bit-reproducible.

| quantity | value |
|---|---|
| mean Iout | 10.649 µA |
| σ | 0.461 µA |
| σ/µ | 4.33 % |
| min / max | 9.472 / 11.937 µA |
| gain with mismatch off | 1.0640 |
| gm/Id at the operating point | 5.58 /V |
| σ(delvto) per device, measured vs formula | 5.263 vs 5.074 mV |

The 6.4 % offset of the mean is channel-length modulation (reference at Vds = 1.366 V,
output at 2.5 V), not mismatch. It is unchanged with `MM_ON=0`.

## 2. Findings about the mechanism

**No Monte Carlo directive exists.** HSPICE `.MONTE`, HSPICE `.dc … sweep monte=`, and
Spectre `montecarlo` are all parse errors. The loop must be built by hand.

**Check results** (`results/00_mechanism.json`, 40 samples each):

| check | pattern | live | reproducible |
|---|---|---|---|
| C1 | `MM_ON=0` negative control | no (flat, as required) | – |
| C2 | in-deck `reset` + `op` loop, unseeded | yes | no |
| C3 | separate invocations, unseeded | yes | no |
| C4 | separate invocations, `set rndseed=k` in `.control` | yes | **no** |
| C5 | separate invocations, `.option seed=k` in netlist | yes | **yes** |
| C5b | in-deck loop + fixed `.option seed` | **no — all iterations identical** | yes |
| C6 | two instances in one run | independent `delvto` and `W` | – |

- **`docs/characterization-inventory.md` item 22 does not reproduce.** It suspected the
  in-deck loop is inert. On ngspice-45 `reset` re-draws every `.param AGAUSS`. The item can
  be closed, with C5b as the one way to make its predicted failure happen.
- **`set rndseed` does not pin the draw.** It is applied after `.param AGAUSS` is evaluated
  at parse time. `circuits/current_mirror_char/run_mc.py` documents itself as
  *"Reproducible: run k uses `set rndseed=k`"* — that claim is false on this build. Its
  statistics remain valid because the draws are live.
- **A fixed `.option seed` freezes an in-deck loop.** `reset` re-seeds to the same value.
  Adding a seed is good practice in other tools and here silently yields σ = 0.
- **Recommended in-simulator pattern:** one invocation per sample, `.option seed=k`.
- **`AGAUSS(nom, avar, n)` has σ = avar/n.** The wrapper coefficient 0.033 V·µm for NMOS50
  is therefore a 3σ figure (1σ = 11 mV·µm). Reading it as 1σ predicts 3× the spread.
  The third argument scales; it does **not** truncate, so tails are unbounded Gaussian.
  Largest draw seen in 200 runs was 3.14σ; the run cannot distinguish truncated from
  untruncated tails.
- **`echo "$&x"` rounds to 6 significant figures.** That produced five false duplicate
  samples out of 200 before switching to `print` with `option numdgt=10`. All 200 `(delvto1,
  delvto2)` pairs were in fact distinct.
- **Readback syntax:** `@m.x1.m0[delvto]`, `@m.x1.m0[w]`, `@m.x2.m0[gm]` — the wrapper
  subckt instance `X1` contains device `M0`.

## 3. Wrapper defect: `M` does not reduce mismatch

Every MOS wrapper computes `.param AUM2={(W/1u)*(L/1u)}` with no `M`, and all three
mismatch terms (and the `MM_SIGMA` deterministic path) scale as `1/sqrt(AUM2)`.

Measured in-session, NMOS50 mirror at 10 µA, 120 runs per row:

| geometry | total area | σ(delvto) | σ/µ(Iout) |
|---|---|---|---|
| W=4.7 L=1 M=1 | 4.7 µm² | 5.039 mV | 3.624 % |
| W=4.7 L=1 M=4 | 18.8 µm² | 4.958 mV | 6.798 % |
| W=18.8 L=1 M=1 | 18.8 µm² | 2.605 mV | 3.737 % |
| W=4.7 L=4 M=1 | 18.8 µm² | 2.422 mV | 0.671 % |

Quadrupling area via `M` leaves σ(delvto) unchanged; via W or L it halves, as expected.
The σ/µ column also moves with gm/Id (wider device at fixed current sits closer to weak
inversion), which is legitimate — the `delvto` column is the clean evidence.

## 4. Other measurements taken in-session

These were run with inline scripts and are **not yet captured in a committed script**.

**Runtime, 200 samples, same mirror:**

| pattern | wall clock |
|---|---|
| in-deck loop, one invocation | 0.7 s |
| `.option seed=k` per invocation, 8 parallel workers | 3.1 s |
| external driver (below), one invocation | 0.7 s |

**External RNG driver works.** Instantiating devices with `MM_SIGMA={S1}` / `{S2}`,
`MM_ON=0`, generating Gaussian z-values in Python with a fixed seed, and stepping
`alterparam S1=… S2=…` + `reset` + `op` in one control block gave 200 samples in 0.7 s,
σ/µ = 3.71 %, bit-identical on repeat. It lands within sampling noise of the analytic 4.0 %.
Caveat: a single `MM_SIGMA` drives the Vth, W, and L terms at the same σ-multiple, so they
become perfectly correlated. For MOS in this PDK the Vth term dominates the geometry terms
by roughly 3.8 × gm/Id, so the error is small, but exact statistics need three independent
knobs.

## 5. Eval-task design discussion

The user is considering an LLM-eval task modelled on this exercise.

### What is non-trivial for a model

- No MC directive in ngspice (fails loudly — benign).
- PDK globals `case` / `PROC_ON` / `MM_ON` (documented in README and `.lib` header).
- `AGAUSS` σ = avar/n convention (fails silently, 3× error).
- The fixed-seed freeze (fails silently, σ = 0) and `set rndseed` not pinning.
- Instance-parameter readback syntax.

Circuit judgment, arguably the best discriminators:
- Separating the systematic CLM gain error from random spread (needs an `MM_ON=0` control).
- Pair σ carries √2, and only the threshold *difference* matters with a forced reference.

### Documentation tiers

**Must provide** (otherwise the task tests guessing): simulator and version; how to include
the library; device port order (`d g s b`); the three globals, legal values, and effect;
that mismatch is per instance. The README has all of this **except** an explicit statement
that ngspice has no MC directive and the loop must be built by hand — add that sentence.

**Should provide:** the `.lib` source. Real PDKs ship it. Hand-computing σ from it is good
engineering and does not shortcut the task (gm/Id still needs an operating point; the
formula says nothing about systematic vs random).

**Must withhold:**
- `docs/sizing-guide.md` — contains 4.08 % for this exact device/current/geometry.
- `circuits/current_mirror_char/MIRROR_CHAR.md` — mirror MC results.
- `docs/characterization-inventory.md` item 22 — hands over the loop question.
- `circuits/mc_mismatch_check/REPORT.md` and this handoff.

**Fairness of the traps:** withholding the fixed-seed freeze is fair (a careful engineer
notices σ = 0). Withholding the `set rndseed` behavior is **not** fair if bit-reproducibility
is required — either document it or don't require reproducibility.

### Task-construction recommendations

- **Require both a hand prediction and a simulated measurement, and require reconciliation.**
  This turns the silent `AGAUSS` 3× error into a visible one.
- **Grade with a tolerance band.** No bit-exact answer exists without mandating a seeding
  pattern. At n = 200 the standard error on σ is ~5 %; ~15 % tolerance is reasonable.
- **Avoid answer leakage:** move device, current, or geometry off the sizing guide's grid,
  or withhold the guide.
- **Mismatch-only vs process+mismatch is a weak discriminator on a mirror** — the repo's own
  data gives 1.256 % vs 1.344 % because a ratio cancels global shifts. Use an absolute
  current reference if that distinction should matter.
- **Any task where a model proposes a device array (`M > 1`) will be scored against
  physically wrong results** until the `M` defect is fixed.

## 6. Proposed improvements (not started)

In recommended order:

1. **Fix `AUM2` to include `M`** in all MOS wrappers: `AUM2={(W/1u)*(L/1u)*M}`. One line per
   wrapper. Invalidates published mismatch numbers, so it needs a re-characterization pass.
   Governance note: models are frozen at v2-grounded, but this is a wrapper change, the same
   category the v2.2-defaults program touched.
2. **Add an MC liveness gate to `pdk_validation/preflight.py`** (documented in
   `docs/geometry-minima.md` as a hard gate in regression): assert σ > 0 over a few samples
   and that two instances draw different `delvto`. Catches the fixed-seed freeze and any
   future ngspice change. Nothing in the repo currently notices if MC stops randomizing.
3. **Move RNG out of the simulator:** split `MM_SIGMA` into independent `MM_SIGMA_VTH`,
   `MM_SIGMA_W`, `MM_SIGMA_L`, and ship a Python driver. Gives reproducibility at in-deck-loop
   speed, and enables stratified sampling, sensitivity analysis, and worst-case search.
4. **Correct the reproducibility claim** in `circuits/current_mirror_char/run_mc.py` and
   **close item 22** in `docs/characterization-inventory.md`. Offered to the user, not done.
5. **Document tail behavior:** `AGAUSS` third argument is a scale, not a clip.
6. **Ship a runner or short MC application note** so the traps are not rediscovered.

## 7. Open decisions for the user

- Whether to apply the two doc corrections in item 4 above.
- Whether to take on the `M` fix and the resulting re-characterization.
- Whether to capture the section-3 and section-4 experiments as committed scripts.
- Whether and where to commit `circuits/mc_mismatch_check/`.
