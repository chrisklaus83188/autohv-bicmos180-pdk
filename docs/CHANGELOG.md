# Changelog

## [Unreleased]

### 2026-05-28 — Verification close-out for the Vshift gmin shunt

Verification reply from the handoff author
(`HANDOFF_ngspice_compat_REPLY_VERIFIED.md`) confirms the Rgmin fix
resolves the realistic workload on ngspice 46:

  * **Simplified level shifter at SS / 125 C** -- previously failed
    with "singular matrix: check node v.x1.xn6.vshift#branch" -- now
    passes. TT and FF pass too. This is the case that motivated the
    whole investigation.
  * **Full level shifter** -- failure mode moved off any
    `vshift#branch` node. Pre-fix the deck never found an operating
    point (gmin / true-gmin / source stepping all failed). Post-fix
    "Transient op finished successfully", then transient runs to
    t ~ 4.57 us before failing at `ecextra#branch` during a 200 V
    SW ramp. The handoff author traces this residual to the level-
    shifter topology + tight `.options`, not the PDK; they're
    handling it on their side.

Residual not addressed (intentionally):

  * **Minimal 4-cascoded-LDMOS repro on ngspice 46** still fails.
    The Rgmin shunt repairs the matrix conditioning (no more
    "singular matrix" warning), but ngspice 46's transient solver
    still aborts at t ~ 1 ns with "trouble with node v.xn4.vshift#branch".
    Tested two follow-up workarounds and confirmed neither helps:
      - **Option A: `delvto` on the VDMOS M-element.** ngspice 45.2
        rejects with `unknown parameter (delvto)`. VDMOS doesn't
        expose a Vth instance shifter analogous to BSIM3's
        `delvto`; original handoff's pre-existing finding stands.
      - **Option C: `Bshift gd g_int V=-DVTH_MM` (B-source as
        voltage)** instead of `Vshift`. Probe shows ngspice still
        creates a `bshift#branch` variable -- B-source-as-voltage
        has the same MNA structure as a VSRC, so it would hit the
        same ngspice-46 transient-solver wall.
    Concluded: this is an ngspice-46 solver-tolerance issue around
    VSRC branch variables that cannot be addressed inside the PDK
    without dropping per-instance Vth mismatch. Documented in the
    cascoded_ldmos.cir docstring so a future ngspice-46-only
    failure isn't confused with a PDK regression.

**Ship decision:** the Rgmin fix as landed in `0ceabc3` is final.
BVCR / Cextra / Bavl remain unchanged per the handoff author's
retraction in `HANDOFF_ngspice_compat_REPRO_RESULTS.md`.

### 2026-05-28 — Fix VDMOS Vshift singular-matrix on ngspice 46 (gmin shunt)

The 13 VDMOS subckts each use `Vshift g g_int DC {-DVTH_MM}` to apply
the mismatch threshold shift. When `MM_ON=0` (default), `DVTH_MM=0`
and `Vshift` collapses to a 0 V VSRC. With two LDMOSes sharing the
external gate node (a routine pattern in HV cascodes, level shifters,
charge pumps, gate drivers), KCL at the shared gate becomes 0=0 -- a
dependent equation -- and the matrix is singular. ngspice 45.2's
KLU solver tolerates this via gmin-stepping; ngspice 46 doesn't.

Fix: add `Rgmin g g_int 1e9` in parallel with each `Vshift` (13 sites,
all VDMOS subckts: NDMOS20/40/60/80/120/200, PDMOS20/40/60/80/120/200,
DNMOS20). 1 GOhm leaks ~1 pA per mV -- 4 to 6 orders of magnitude
below any real mismatch sigma. Standard foundry idiom for Vshift-style
HV mismatch wrappers.

Scope: this is intentionally **narrower** than the global
`NGSPICE_COMPAT` switch proposed in `HANDOFF_ngspice_compat.md`.
That handoff's claims #1 (BVCR), #2 (Cextra), and #4 (Bavl) were
retracted in `HANDOFF_ngspice_compat_REPRO_RESULTS.md` after their
own author confirmed those repros pass on ngspice 46. Only claim
#3 (Vshift) reproduced standalone, so only it is fixed here.
BVCR / Cextra / Bavl behavioral elements are unchanged.

Regression coverage added: new
`pdk_validation/regression/transients/cascoded_ldmos.cir` deck --
two NDMOS200 + two NDMOS120 with shared gates at `MM_ON=0`. This
is the exact pattern the original suite was missing (the existing
smoke + transients exercise single VDMOS devices; the cascoded
pattern, which is where the singular matrix manifests, was not
covered). Phase D is now 8 decks; new deck baseline 84 ms.

Baseline post-fix on ngspice 45.2:
  smoke      :  800/800 ops    (40 dev x 5 corners x 4 stat combos)
  passives   :    9/9  goldens   (R(V)/C(V) unchanged -- no VCR/VCC edit)
  corners    :   36/36 checks    (9 family probes x 4 non-TT corners)
  transients :    8/8  decks     (incl. new cascoded_ldmos.cir)

Awaiting verification on ngspice 46 from the handoff author per
`HANDOFF_ngspice_compat_REPLY_FIX_LANDED.md`.

### 2026-05-27 — Add PDMOS120 and PDMOS200 (complete the HV PMOS family)

The HV VDMOS family previously stopped at 80 V on the P-channel side
(PDMOS20/40/60/80) while N-channel went up to 200 V (NDMOS20/40/60/80/
120/200). Added two new p-channel devices to fill the gap:

  PDMOS120 -- 120 V p-channel HV DMOS, single-arg subckt
              .subckt PDMOS120 d g s params: W=10u M=1
  PDMOS200 -- 200 V p-channel LDMOS, W and L (drift) parameterised
              .subckt PDMOS200 d g s params: W=10u L=8u M=1

The 200 V variant uses the same RDRIFT-extension scheme as NDMOS200
but with a 3.0x per-um delta-R scale factor (vs 1.2x on NDMOS200),
reflecting the ~2.5x higher per-um drift resistance of an n-well
drift region vs the p-substrate / n-drift used by NDMOS200. Default
L is 8 um (= L_REF); recommended drift window 5 u .. 16 u.

Nominal sizing (TT, derived by scaling NDMOS120/200 with the 80V
NDMOS<->PDMOS ratios extracted from the existing pair):

                      kp      rd      rs      bv     vto
   PDMOS120         0.21   1.15   0.58    128   -1.25
   (vs NDMOS120)   0.45   0.55   0.25    135    1.20    (kp 0.47x, rd 2.1x)
   PDMOS200        0.088  3.00   1.38    207   -1.31
   (vs NDMOS200)   0.22   1.20   0.55    225    1.25    (kp 0.40x, rd 2.5x)

Additions across the lib:

  .inc:
    + 10 P_D*_PDMOS{120,200} statistical params (sigma matches the
      corresponding NDMOS counterpart at each voltage class)
    +  8 TC_*_PDMOS{120,200} temperature coefficients (same magnitudes
      as N counterparts)
    +  8 *_PDMOS{120,200}_STAT params (parse-time STAT split per the
      P0 temper/agauss-separation pattern)
    +  2 .model PDMOS{120,200}_INT VDMOS cards (pchan)

  .lib:
    +  2 .subckt PDMOS{120,200} wrappers with the same Vshift-based
      mismatch idiom as the other DMOS subckts (VDMOS rejects delvto)

  Symbols:
    + qucs-s_symbols/PDMOS120.sym  (copy of PDMOS80.sym -- same p-arrow)
    + qucs-s_symbols/PDMOS200.sym  (same)

  Regression:
    run_smoke.py: device list 38 -> 40; total ops 760 -> 800
                  (5 corners x 4 stat combos x 40 devices). Both new
                  devices pass at every combination in ~52 ms each.

All four regression phases pass on the post-addition lib:
  smoke:      800 / 800   (median 57 ms / op, max 303 ms)
  corners:     36 /  36   (9 family probes x 4 non-TT corners)
  passives:     9 /   9   (R + C goldens unchanged; existing devices
                           untouched)
  transients:   7 /   7   (~0.7 s wall total)

Notes for users:
  * The new models are engineered (NMOS-to-PMOS scaling from the
    existing 80 V pair), not silicon-fit. Calibration TODO matches
    the rest of the lib's note about uncalibrated magnitudes.
  * PDMOS200 with the recommended RESURF window (L = 5 - 16 um) gives
    Rds(on) roughly 2.5x of NDMOS200 at the same L; expect that
    factor to grow further if pushed beyond 16 um.

### 2026-05-27 — P3.1: switched-cap precision audit (CMIM_STD / CMIM_HI)

New deck `pdk_validation/switched_cap_audit/sample_and_hold.cir` plus
`run_sc_audit.py` (Python). Topology: NMOS18 sampling switch into a
CMIM_STD or CMIM_HI hold cap, driven by a slow Vin ramp (0 -> 1 V over
10 us) and clocked at 1 MHz / 50 % duty. For each clock period the
harness pairs (V_in at the phi falling edge, V_hold 50 ns after the
fall, when charge injection has settled), fits a linear model, and
reports gain error, offset, and RMS residual.

Baseline numbers on the current lib (ngspice 45.2, TT, no statistics):

| Cap (size) | Q_inj offset | Gain error | RMS residual | kT/C floor |
|------------|--------------|------------|--------------|------------|
| CMIM_STD (10 pF) | -4.67 mV | +0.128 % | 1.17 mV | 20.4 uV |
| CMIM_HI  (20 pF) | -2.32 mV | -0.350 % | 1.77 mV | 14.4 uV |

Charge-injection offset halves with 2x hold cap, as expected for a
charge-dominant error. Deterministic errors are ~100 - 1000x the kT/C
noise floor, so:

  * The PDK's deterministic SC flow is sound: charge injection is
    physically reasonable in magnitude (a few mV on 10 pF with an
    NMOS18 switch matches W*L*Cox*Vov/(2C) within 2x).
  * Explicit thermal-noise injection (kT/C) into the cap model is
    moot for SC applications -- the systematic errors dominate by
    orders of magnitude unless designers use cancellation techniques
    (dummy / complementary switches, autozero, CDS).

The audit is one-shot investigation; not added to CI gating.

### 2026-05-27 — P3.2: line-ending convention (.gitattributes)

Added `.gitattributes` with `* text=auto eol=lf` plus explicit `eol=lf`
entries for the project's text extensions (`.lib`, `.inc`, `.cir`,
`.sym`, `.py`, `.md`, `.csv`, `.yml`, `.yaml`, `.json`). Docx / pdf /
image extensions explicitly marked binary. Repo was already stored as
LF in git, so this is mostly preventive -- future commits stop
emitting CRLF/LF normalization warnings, and any new collaborator on
Windows gets a clean diff regardless of their `core.autocrlf`.

### 2026-05-27 — P2.2: corner-sanity check across all device families

- New `pdk_validation/regression/run_corners.py`. For each of 9
  representative devices (one per family/polarity) it measures
  one canonical quantity at all 5 corners (TT, FF, SS, FS, SF)
  and verifies the *sign* of the relative change vs TT matches
  the .inc's corner-factor design:
    BSIM3 NMOS/PMOS, VDMOS NMOS/PMOS, BJT NPN/PNP, Diode, R, C.
- 36 corner checks total (9 probes x 4 non-TT corners). All PASS
  on the current lib.
- Confirms `case` propagates to every device family (including
  through the P0-fixed VDMOS `_STAT` params). Sample magnitudes:
    BSIM3 NMOS18 ID: +50% FF, -36% SS, +49% FS, -35% SF
    BSIM3 PMOS18 ID: +57% FF, -39% SS, -39% FS, +56% SF
                     (cross-pair naming verified: FS=slow-P, SF=fast-P)
    VDMOS NDMOS20 ID: +-22% (P0 STAT params carry case correctly)
    BJT NPN_LV Ic: +-18% (FS fast, SF slow; tracks NMOS)
    BJT PNP_LAT Ic: +-19% (SF fast, FS slow; tracks PMOS)
    DIO_PN Vf: +-0.23% (FS=SF=TT exactly, as designed)
    RPOLY_HI R: -10%/+12% (FS=SF=TT exactly)
    CMIM_STD C: +-3% (FS=SF=TT exactly)
- Wired into CI as a new gating step after Phase D, before MC.

### 2026-05-27 — P2.1: BJT avalanche audit (no code change required)

The handoff flagged the four BJT subckts (`NPN_LV/HV`, `PNP_LAT/HV`)
as having simulation-time non-smooth constructs in their `Bavl`
expressions:

  `Bavl ci b I={ abs(i(Vsen))*( 1/(1 - (min(max(V(ci,b)/BVCBO,0),0.997))**MAV_BJT) - 1 ) }`

Stress-tested all four under three regimes:

  * DC sweep Vcc from 0 V to BVCBO + 20 % (with Ib forced) - all 4
    subckts converge at every step. Decks in
    `pdk_validation/bjt_avalanche_stress/`.
  * Transient ramp Vcc 0 -> BVCBO + 20 % over 1 us - 251 timepoints,
    220 ms wall, no timestep blow-up.
  * Transient switching at Vcc held above BVCEO with Ib pulsed
    0 <-> 100 uA and 1 ns edges - Ic transitions through zero each
    edge; 432 timepoints, 170 ms wall, no timestep blow-up.

The `abs(i(Vsen))` is actually a *stabilizing* feature: once the
small-signal model would give "Ic = beta*Ib/(2-M)" with M > 2 (well
beyond BVCEO), the magnitude wrapper keeps the avalanche current
positive and the clamp at 0.997 turns the high-Vcb region into a
finite plateau rather than a divergence. No smoothing needed.

The handoff also flagged `max()` calls in the DMOS subckts as
potential simulation-time kinks. On inspection, all of those
(`max(mtot,1e-6)`, `max(L,L_MIN)`, `max(1.2*(Leff/L_REF-1)/mtot, 1e-6)`)
depend only on parse-time parameters and are evaluated once during
expansion - **not** simulation-time. No risk there.

Net result: **the only simulation-time non-smooth constructs in the
entire lib are the four BJT avalanche `Bavl` expressions**, and they
have now been verified to converge cleanly under stress.

Added `pdk_validation/regression/transients/bjt_breakdown_ramp.cir`
to the Phase D suite (one deck, 62 ms baseline) so any future
regression in this area shows up as a budget hit. Phase D is now
7 decks; all pass.

### 2026-05-27 — P1 Phase F: CI wiring (GitHub Actions)

- New `.github/workflows/regression.yml`. Triggers on push to
  `main`, PR to `main`, and manual `workflow_dispatch`.
- Runs on `ubuntu-24.04` with Python 3.12 and ngspice from
  `apt-get` (likely 41-42; older than the local 45.2 baseline).
- Phases A/B/C/D **gate** the build (suite must pass to merge);
  Phase E runs with `continue-on-error: true` because it's a
  statistical sanity check (intended-vs-measured sigma) that can
  occasionally land outside tolerance due to small-N noise. CI
  uses `-n 80 --tol 0.40` for E to balance speed and stability.
- Cross-platform plumbing: `find_ngspice()` in all four harnesses
  now also looks for plain `ngspice` (Linux/macOS binary name),
  falling back from `ngspice_con(.exe)` (Windows-preferred batch
  binary).
- If Phase C's goldens drift on a different ngspice version, two
  fix paths documented in the regression README: regenerate
  goldens on the CI version, or switch the workflow to build
  ngspice 45.2 from source with `actions/cache`.

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
