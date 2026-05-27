# Changelog

## [Unreleased]

### 2026-05-27 — P1 Phase E: Monte Carlo flow validation

- New `pdk_validation/regression/run_mc.py` plus a small testbench
  deck `pdk_validation/regression/mc/mc_nmos50_mismatch.cir`.
- Verifies three end-to-end properties of the PDK's statistics
  flow on ngspice 45.2:
  1. AGAUSS re-randomizes across `-b` invocations (default
     time-seeded RNG, no special flag needed).
  2. Two subckt instances of the same device get independent
     mismatch draws when `MM_ON=1`.
  3. Measured sigma of `log(I1/I2)` on a two-NMOS50 mismatch
     testbench matches the model-anchored intended sigma within
     statistical noise.
- **Critical finding** documented: ngspice's `AGAUSS(mean, X, N)`
  uses the HSPICE convention -- **true 1-sigma = X / N** (X is
  the clip bound at N sigmas, not the 1-sigma value). Empirically
  verified: `AGAUSS(0, 1, 3)` produces sigma ~ 0.34, range +/-1.
  Every AGAUSS-bearing `.param` in `autohv_bicmos180_case.lib` has
  effective 1-sigma = X / 3; the numbers in the lib are 3-sigma
  bounds. Divide by 3 when reasoning about 1-sigma behavior.
- Baseline on the current lib:
  - **MM axis**: pair sigma(log I1/I2) measured 0.42 %, intended
    0.36 % (16 % deviation; tolerance 30 %). Per-device sigma
    ~0.29 %. PASS.
  - **PROC axis**: pair log-ratio sigma 0.00 % exactly (both
    devices share one die draw), per-device sigma 3.93 % from
    combined Vth/u0/vsat/rdsw process params. PASS.
- Out of scope (follow-on): W*L sigma-scaling sweep, other device
  families, CI integration.

### 2026-05-27 — P1 Phase D: per-class transient regression

- New `pdk_validation/regression/run_transients.py` plus 6 canonical
  `.cir` files under `pdk_validation/regression/transients/`, one
  per device class:
  - `bsim_inverter.cir`      — NMOS18+PMOS18 rail-to-rail switching
  - `vdmos_switching.cir`    — NDMOS20 switching a 10 Ω/12 V load
  - `bjt_common_emitter.cir` — NPN_LV pulse response
  - `diode_rectifier.cir`    — DIO_PN half-wave rectifier
  - `r_thru_zero.cir`        — RNWELL AC current with V(p,n)
    crossing 0 V each half-cycle (strongest VCR)
  - `c_thru_zero.cir`        — CMIM_HI same (strongest VCC)
- The last two are the canonical "abs() kink killers": pre-fix,
  those AC-through-zero passive transients hung at >120 s because
  the non-smooth `|V|` in the VCR/VCC expressions destabilized the
  Newton/LTE timestep loop. The post-fix `sqrt(V*V + 1e-6)` form
  finishes each in ~55 ms.
- Per-deck wall-time budget (2.0 s for active devices, 3.0 s for the
  passive AC-thru-zero decks) is enforced as a pass/fail gate.
  Baseline uses 2-6 % of each budget -> ~20x headroom against
  regression.
- `--deck <stem>` restricts to listed decks; `--max-overrun N`
  scales every deck's budget (use >1 for a legitimately slower
  change, <1 to tighten).

### 2026-05-27 — P1 Phase C: passive R(V)/C(V) golden-curve diff

- New `pdk_validation/regression/run_passives.py`. For each of the 5
  behavioral resistors (`RPOLY_HI/LO`, `RNWELL`, `RNPLUS`, `RPPLUS`)
  it runs a single `.dc Vp -5 5 0.25` and extracts
  `R(V) = V / -i(Vp)`. For each of the 4 capacitors (`CMIM_STD/HI`,
  `CMOM`, `CFRINGE`) it runs a `.tran` with a PWL ramp `0 -> 5 V`
  over 1 ms and extracts `C(V) = -i(Vp) / dV/dt`.
- Each curve is interpolated onto a fixed comparison grid (41 pts
  for R, 21 pts for C) and diffed against a stored golden in
  `pdk_validation/regression/goldens/`. Default tolerance: 1e-3
  relative (`--tol`).
- Goldens generated from the post-P0 lib. Numerical sanity:
  - `RPOLY_HI` 12.27-12.29 kΩ (rsh=1200, L/W=10 with mild VCR),
  - `RNWELL` 18.65-19.55 kΩ (strongest VCR at ~5 % @ 5 V),
  - `CMIM_HI` 20.00-20.03 pF (cj=0.002 over 100×100 um, mild VCC).
- `--regenerate` rewrites goldens from the current lib (use only
  when the new behavior is the accepted baseline; commit the
  updated JSONs alongside the lib change).
- Catches: VCR/VCC coefficient drift, re-introduced `abs()` kinks
  (the curve would re-acquire a cusp at V=0), unit typos on
  `rsh`/`cj`. Doesn't yet sweep temperature -- folded into Phase D.

### 2026-05-27 — P1 Phase B: per-op wall-time budget

- `run_smoke.py` now times every op and treats `--max-op-secs` (default
  `2.0`) as a hard pass/fail gate: any op that converges but exceeds
  the budget is reported as a failure. Catches the kind of
  convergence/stiffness regression the pre-fix `abs()` kink caused
  (>120 s vs. ~3 s after the smooth-`|V|` fix).
- Run footer now prints `median / p95 / max` op time and flags the
  slowest test when it crosses 50 % of the budget.
- Baseline on ngspice-45.2: median ~53 ms, p95 ~67 ms, max ~204 ms —
  the default budget gives ~10× headroom.
- New flag: `--max-op-secs 0` disables the gate (useful when
  benchmarking long-running transient experiments under the same
  harness later).

### 2026-05-27 — P1 Phase A: device-instantiation regression suite

- New `pdk_validation/regression/run_smoke.py` plus a README.
  Generates a minimal bias deck per `.subckt`, runs
  `ngspice_con -b`, and asserts `op` convergence and the absence of
  fatal-error patterns (`no such function`, `singular matrix`,
  `iteration limit reached`, etc.).
- Sweeps the full corner × statistics matrix:
  38 devices × 5 corners (`case=0..4`) × 4 `(PROC_ON, MM_ON)` combos
  = **760 ops**. Runs in ~45 s serially on ngspice-45.2.
- `--quick` mode: 38 ops at `case=0`, `(PROC,MM)=(1,1)` only — for
  fast iteration while editing the lib (~3 s).
- Baseline result on the post-P0 lib: **760/760 PASS**.
- Catches the P0 class (temper/agauss collision) instantly: any
  regression that re-mixes parse-time statistics with runtime
  `temper` would trip the `no such function 'agauss'` pattern.

### 2026-05-27 — P0 fix: VDMOS family is instantiable

- Bug: any VDMOS instantiation (`NDMOS20/40/60/80/120/200`,
  `PDMOS20/40/60/80`, `DNMOS20`) failed at `op` with
  `Error: no such function 'agauss'`. Root cause: each `.model`
  card's `vto`/`kp`/`rd`/`rs` mixed `temper` (runtime) and the
  `agauss`-bearing `P_D*` params (parse-time) in one braced
  expression. ngspice defers any expression containing `temper`
  to per-temperature runtime evaluation, where `agauss` is not
  resolvable — so the whole expression failed.
- Fix: hoist the statistical product into parse-time `.param`
  definitions, one per affected expression per device
  (`VTO_<dev>_STAT`, `KP_<dev>_STAT`, `RD_<dev>_STAT`,
  `RS_<dev>_STAT` — 44 in total). Each card line now reads
  e.g. `vto={VTO_NDMOS20_STAT + TC_VTO_NDMOS20*(temper-27)}`,
  so the runtime-deferred expression contains only numbers and
  `temper`. Statistically identical to the old form (the
  `agauss` draw simply moves to parse time).
- Verified on ngspice-45.2: all 11 VDMOS devices instantiate
  and `op` converges at T=27 °C and T=125 °C with
  `case=0`, `PROC_ON=1`, `MM_ON=1`. Smoke decks at
  `pdk_validation/smoke_p0_ndmos20.cir` and
  `pdk_validation/smoke_p0_vdmos_all.cir`.

### 2026-05-27 — Library refinements

- MOS Vth mismatch (NMOS/PMOS 12/18/33/50): replaced the external
  `Vshift g g_int DC {DVTH_MM}` + node-split workaround with BSIM3's
  native `delvto` instance parameter on `M0`. Removes the extra
  series voltage source and dangling `g_int` node per device while
  delivering the same mismatch Vth shift through the model's
  intrinsic mechanism.
- Smoothed `|V|` in voltage-coefficient expressions: replaced
  `abs(V(p,n))` with `sqrt(V(p,n)*V(p,n)+1e-6)` in the VCR
  branches of `RPOLY_HI`, `RPOLY_LO`, `RNWELL`, `RNPLUS`, `RPPLUS`
  and the VCC branches of `CMIM_STD`, `CMIM_HI`, `CMOM`, `CFRINGE`.
  Removes the cusp at V=0 (now C∞) so Newton/DC convergence is
  cleaner; bias dependence is unchanged for |V| >> 1 mV.

### Initial snapshot

Initial tracked version of the AutoHV BiCMOS 180 PDK for Qucs-S.

### Library
- Collapsed the original five corner-sectioned libraries into a single flat library;
  the corner is selected by a global `case` parameter (0=TT, 1=FF, 2=SS, 3=FS, 4=SF).
- Orthogonal statistics: `PROC_ON` (die-to-die process) and `MM_ON` (local mismatch),
  both off by default.
- Removed the redundant `_MC` device wrappers (statistics live in the base devices),
  reducing the library from 76 to 38 `.subckt` devices.
- DMOS/LDMOS sizing reworked from `AREA` to physical `W`/`M` (all DMOS) and an
  additional drift-length `L` on the 200 V `NDMOS200`. Width scales current linearly
  via an internal multiplier; `L` raises modeled on-resistance (breakdown held at the
  model rating).

### Models
- Bipolar breakdown reinstated. Removed the inert `bv`/`ibv` from the four
  Gummel-Poon BJT cards (they are not GP parameters and were silently ignored,
  so the `P_DBV_*` draws varied nothing) and rebuilt breakdown behaviorally in
  the subckts as a collector-base avalanche branch keyed to the original ratings
  (now `BVCBO`), with the `P_DBV_*` draws kept live. Model beta now sets
  BVceo < BVcbo.
- 12 V devices (`NMOS12`/`PMOS12`) converted from MOS Level 3 to BSIM3
  (level 49) for smooth output conductance, charge-conserving capacitances and a
  real subthreshold region, matching the 18/33/50 family. Also removes a Level-3
  `lambda`/`kappa` ambiguity that made gds differ between ngspice and SmartSpice.
  Corner Vth/u0/vsat/rdsw carried over from the Level-3 sets; Monte-Carlo draws
  remapped with none added and none left dead.
- HV drift-MOS (VDMOS, all 11 cards) given temperature dependence (on-resistance
  rises, Kp/Vth fall with T) via per-device tempco constants grouped at the top
  of the models include. Previously the VDMOS array had no temperature behavior.
- Bipolars given 1/f (flicker) noise (`kf`/`af`); flicker was previously zero.
- Annotated the inert `binunit=1` on the BSIM3 cards (no L/W bins are shipped).

### Symbols
- Schematic symbols for all 38 devices, with corrected device-specific artwork
  (core FET orientation, HV DMOS extended-drain symbol, zig-zag resistors).

### Docs / tooling
- Added the PDK reference manual (`docs/`) and runnable example decks (`examples/`).

### Notes & known limitations
- Calibration required. Signs and mechanisms are validated on ngspice 42,
  but the magnitudes are engineered, not fit to silicon: the BSIM3 12 V secondary
  coefficients, the VDMOS tempco constants (`TC_*`), and the BJT avalanche
  sharpness (`MAV_BJT`) and `kf`/`af`. The converted BSIM3 12 V cards
  intentionally do not reproduce the old Level-3 I-V.
- `AGAUSS` in `.param` is not parsed by stock ngspice in its default mode; the
  statistics rely on Qucs-S preprocessing, an HSPICE-compatibility path, or
  SmartSpice (native `AGAUSS`).
- The avalanche subckts use ngspice idioms (`temper` re-evaluation in `.model`
  braces, the `**` operator, `min`/`max`, and the `i(Vsen)` current probe);
  confirm equivalents when porting to SmartSpice.
- Deferred: cap VCC charge-form conversion; substrate/junction caps and a
  self-heating thermal node on the HV array (interface change); and calibrated
  MOS 1/f (`noia/noib/noic`, currently on `noimod=2` defaults).
