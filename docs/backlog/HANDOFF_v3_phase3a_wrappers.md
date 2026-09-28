# Handoff: Phase 3a — wrappers generated, the first bug closed, and a finding that moves every mismatch number

**Responds to:** the restart ruling (§1 state check, then Phases 3–7)
**Branch:** `mc-realism` @ `e8f4e7c`, pushed
**Date:** 2026-09-27
**Status:** Phase 3a done and verified. **One §2 question below** — the multi-finger
stripe-sharing formula, which the brief names but does not define. Everything else in Phase 3
proceeds without it.

---

## 1. Decisions taken under the autonomy rule

| decision | why it was mine to take |
|---|---|
| Generate the wrapper section from `stat_model.json` via `tools/gen_wrappers.py` + a pristine `.lib.in` | the brief says coefficients must be "referenced to `stat_model.json` by name"; this program's standing rule is that nothing is typed which can be derived, and a generator never reads the file it writes |
| Emit `AGAUSS(0, <1σ>, 1)` rather than `(0, <3σ>, 3)` | the brief requires 1σ coefficients in foundry units; now the number in the file *is* the model's value, not a value silently scaled by 3 |
| **Keep `MM_SIGMA` for now** | 118 files pass it with non-zero values (`+3`, `-3`, `{S1}`, `{S2}`). "Removed repo-wide" happens after those callers migrate, so the migration can be *verified* behaviour-preserving rather than assumed |
| Leave `.param AREAEFF` unowned | the BJT/diode wrappers fold everything into one area perturbation; the brief replaces it with three independent terms. Passed through rather than half-converted |
| Use `mulu0` for the β knob | verified: ngspice BSIM3 accepts it as an instance parameter and it moves Id (5.4675e-4 → 5.8112e-4 at `mulu0=1.10`) |

## 2. The first bug in this program is closed

`AUM2` omitted `M`. `stat_model.json`'s own `local_mismatch._convention` reads *"sigma = A /
sqrt(W*L*M) for MOS"* — so the wrapper contradicted the model it was meant to implement, and
device multiplicity reduced mismatch σ not at all.

Acceptance, made **deterministic** with `MM_SIGMA=1` so it needs no Monte Carlo, on
NMOS5V0 W=2 µm L=1 µm:

| | measured `delvto` | closed form `A_VT/√(W·L·M)` |
|---|---|---|
| M=1 | 4.2143564159 mV | 5.96/√2 = 4.2143564 mV |
| M=4 | 2.1071782079 mV | 5.96/√8 = 2.1071782 mV |

**Ratio exactly 2.000000000**, and both match the closed form to ten significant figures.

The brief predicted 4.96 → 2.5 mV. The absolute values differ because `A_VT` itself is now the
derived ladder rather than the old spec window (§3); the halving is the property under test.

## 3. Finding — the A_VT ladder had never reached the wrappers

This is the one to look at. Stop A derived the ladder; the `.lib` still carried the
**pre-Stop-A spec-window values**. Every mismatch simulation in this PDK has been running up
to 2× too wide at 5 V and 12 V:

| device | `.lib` was | model | delta |
|---|---|---|---|
| NMOS12V | 31.0 | 15.02 | **−51.5 %** |
| PMOS12V | 31.0 | 15.84 | **−48.9 %** |
| NMOS5V0 | 11.0 | 5.96 | **−45.8 %** |
| PMOS5V0 | 11.0 | 6.41 | **−41.7 %** |
| PMOS3V3 | 4.0 | 4.81 | +20.2 % |
| NMOS3V3 | 4.0 | 4.51 | +12.7 % |
| PMOS1V8 | 3.5 | 3.66 | +4.6 % |
| NMOS1V8 | 3.5 | 3.44 | −1.7 % |

**Nothing else was stale**, which is what makes this safe to land: of 46 σ values in the
wrappers, 29 are numerically unchanged and 9 more move only by rounding (≤ 0.1 %, the model
value now authoritative). `A_W`/`A_L` already matched. VDMOS carried the 0.024–0.033 ladder
correctly; resistors 1.061–2.828 %·µm and capacitors 0.53/1.061 %·µm likewise. **Only the 8
`A_VT` are a real change.**

Every mismatch-dependent result in the repo — mirror characterisation, comparator offsets, the
sizing guide's σ columns — is therefore stale until Phase 7 re-characterisation. That is
already in the plan; this is notice of how much it will move.

## 4. The generator

`tools/gen_wrappers.py` is a line transform over a new `autohv_bicmos180_case.lib.in`, the
same shape as `gen_models.py` over the `.inc`, and for the same reason: **492 of 622 lines are
authored device structure** — thermal networks, avalanche generators, VCR/VCC terms, gmin
shunts — that no statistical model describes. It owns 130 lines, refuses to run if its input
path resolves to its output path, and has `--check`.

Verified: every changed line lies inside the owned set, and no parameter vanished.

Also recorded in the `.lib` header, per the brief: **AGAUSS's third argument is a σ scale, not
a clip.** `AGAUSS(0,X,3)` means X is the 3σ value; it truncates nothing.

**Seven checks green** (`inc_parse`, `check_naming`, `gen_models`, `gen_wrappers`,
`expected_terms`, `build_corners`, `stat_model_inventory`), and all six device families
simulate with `MM_ON=1`.

## 5. §2 question — the multi-finger stripe-sharing formula

The brief says *"stripe-sharing `AD/AS/PD/PS` as **per-finger** values (ngspice multiplies by
`m`)"* but does not give the formula, and the choice is designer-visible: it sets junction
capacitance, so it moves every AC and transient result.

**The area share I can derive cleanly.** `NF` fingers sit on `NF+1` diffusion stripes; drain
and source take half each; ngspice multiplies the per-finger value by `m = NF·M`. So

> `AD = AS = (W/NF)·LD·(NF+1)/(2·NF)`

which gives exactly `W·LD` at `NF=1`, and totals 1.5·W_f·LD at `NF=2` and 2.5 at `NF=4` —
matching the stripe count in each case. I am confident in this one.

**The perimeter share I am not willing to invent.** An end stripe has three sides exposed
(`W_f + 2·LD`); an interior stripe has both long sides facing gates, so only its two short
sides (`2·LD`) are junction perimeter. That gives

> `PD = PS = [2·(W_f + 2·LD) + (NF−1)·2·LD] / (2·NF)`

per finger — but whether `PD` should count the gate-facing edge at all is a model convention
(BSIM3's `PD` is meant to exclude the channel edge), and getting it wrong misstates sidewall
capacitance on every multi-finger device.

**Recommendation: adopt both formulas above**, with the perimeter one excluding gate-facing
edges as written. One word is enough, or give me the convention you want.

Until then `NF` is not wired: the wrappers still take `M` only, which is exactly today's
behaviour, so nothing is blocked or half-done.

## 6. What is next, without waiting

In order: the four knobs (`Z_VT`, `Z_BETA` via `mulu0`, `Z_W`, `Z_L`) and the gate resistor and
edge-bias wiring; then the `MM_SIGMA` → knob migration across the 118 callers with
byte-identical verification, then its removal; then resistors (`NS`, heads), capacitors (the
perimeter split, which needs `A_CPER` solved from the Q-C constraint since the model has it
`null`), and the BJT/diode three-term rewrite; then the Zener bench and `BV_DZ_*`; then
re-measure the directions that `RSH_GATE`/`RHEAD_*`/`CPER_*` make live, rebuild `corners.json`,
and run B2–B7.

## 7. State

`e8f4e7c` on `mc-realism`, pushed, tree clean. New: `tools/gen_wrappers.py`,
`autohv_bicmos180_case.lib.in`.

Also from the state check, still outstanding and not mine: the stranded worktree
(`transmission-gates` at `61de05f`, 31 modified files, remote `98cefc2`) and the six
`xschem/designs/*.sch` netlist verifications.
