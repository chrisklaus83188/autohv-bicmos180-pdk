# Characterization Inventory — AutoHV BiCMOS180 PDK

**Scope:** read-only archaeology sweep of the working tree and the full git history (67 commits,
`4f6e1cd` 2026-05-22 → `0e103c4` 2026-07-18, single branch `main`, single tag `v0`, no stashes).
**Purpose:** establish what device characterization, model verification, model fixing, and
PDK-realism work already exists, where its artifacts live, and what each established — as the
baseline for the planned realism audit.

**Nothing in the repo was modified.** No simulations were run. This file is the only artifact created.

Cross-cutting caveat carried throughout: *documented* here means an artifact exists, not that the
artifact is correct. Several documents contradict each other; §6 lists every contradiction found.

---

## 1. Repo map

```
autohv-bicmos180-pdk/
├── autohv_bicmos180_case.lib          40 .subckt device wrappers (592 lines) — the user-facing PDK
├── autohv_bicmos180_case_models.inc   40 .model *_INT cards + all corner/stat params (1532 lines)
├── README.md                          Qucs-S-oriented PDK overview; device/pin/sizing tables
├── BRIEF_pdk_realism.md               UNTRACKED. The plan for the coming audit (see §6.1)
├── BRIEF_hv_monitor.md                UNTRACKED. Outbound design-review brief on CP_VoltageMonitor
├── b3v33check.log                     ngspice byproduct (3 copies in tree; gitignored, NOT tracked)
├── repro_{delay,slew}_vin{100,200}.cir  4 reproducers for the HV micro-stepping handoff
│
├── docs/                              Prose record of the PDK's evolution
│   ├── CHANGELOG.md                   1021 lines — THE richest fix record in the repo
│   ├── MISMATCH_CORNERS.md            The mismatch/MM_SIGMA contract (293 lines)
│   ├── QUICKSTART.md                  1-page ngspice run guide
│   ├── AutoHV_BiCMOS180_PDK_Reference.docx   22 KB binary reference manual (not parsed here)
│   ├── handoffs/                      11 RESOLVED engineering correspondence docs + index
│   └── backlog/                       2 OPEN findings + index
│
├── circuits/                          Design + characterization work built ON the PDK
│   ├── async_logic_design/            24 static-CMOS logic cells, 3 domains, 120 decks
│   ├── comparators/                   9 comparator cells (GP two-stage + rail-to-rail), 3 rails
│   ├── current_mirror_char/           PMOS50 mirror DC/MC study — the cleanest work in the tree
│   ├── delay_pulse_design/            12 DLYR/DLYF/PHI/PLO cells, 45-pt PVT + 200-run MC
│   ├── delay_cells_voltage_ramp/      UNTRACKED. Mirror-into-cap voltage-ramp front-end
│   └── hv_charge_pump/hv_up_lvlsh/    5 hand-written .spice files, ZERO characterization
│
├── pdk_validation/                    Verification harness for the PDK itself
│   ├── regression/                    5 runners + 9 passive goldens + 13 transient decks (CI-gated)
│   ├── bjt_avalanche_stress/          4 audit decks (orphaned)
│   ├── switched_cap_audit/            SC precision audit harness (orphaned deck)
│   └── device_limits.csv              86 geometry-bound rows — read by nothing
│
├── examples/                          8 demo decks, 01…08
├── qucs-s_symbols/                    40 Qucs-S .sym files
├── xschem/                            Xschem front end: 40 device + 24 logic + 9 cmp + 12 dly symbols
└── tools/make_release.py              Sanitized per-task PDK export (allowlist + scrubber)
```

---

## 2. Artifact inventory

### 2.1 Documentation

| Path | Covers | Devices | Key results / conclusions | Repro |
|---|---|---|---|---|
| `docs/CHANGELOG.md` | Every model change since 2026-05-22, reverse-chronological, all under `[Unreleased]` | All | The single most complete fix record. Carries before/after numbers for the VDMOS cap fix, PDMOS200 bv re-rating, Rcond sweep, 1/f calibration, self-heating, SC audit, corner sanity. | n/a (prose) |
| `docs/MISMATCH_CORNERS.md` | Mismatch model contract + `MM_SIGMA` semantics | All 40 | `X_MM = MM_ON*AGAUSS(0,X,3)/scale + MM_SIGMA*X/3/scale`. HSPICE convention: **X is the 3σ bound, true 1σ = X/3**. Four-mode table; `(MM_ON=1, MM_SIGMA≠0)` explicitly "don't do this". | `transients/mismatch_corner.cir` |
| `docs/handoffs/HANDOFF_vdmos_caps.md` | **The VDMOS capacitance diagnosis** | 13 VDMOS | See §3 and §6.2. Full pre-fix table for `cgs`/`cgdmax`/`cgdmin`/`cjo`; the 10 µm-cell physical argument; pF-vs-fF unit-slip hypothesis. | `coss_check.cir` (partial) |
| `docs/handoffs/HANDOFF_cascode_vshift_singularity.md` | `vshift#branch` singular matrix on cascodes | NDMOS200/120 | `method=gear` aborts; `method=trap` "limps through but the operating point is corrupted — e.g. an average supply current measured as `-25.9 A`". | inline repro |
| `docs/handoffs/HANDOFF_dmos200_breakdown.md` | PDMOS200 sub-200 V breakdown | PDMOS200 | Worst corner 194.58 V (FF/SF) vs 200 V class name. `"LEVEL=1 hid this entirely (no bv)"`. | inline repro |
| `docs/handoffs/HANDOFF_dmos200_vshift_multiinstance{,_REPLY}.md` | Multi-instance floating-mirror singularity + the fix | NDMOS200/PDMOS200 | `delvto` rejected by ngspice for VDMOS; `Rgmin` at 1e7/1e6/1e5 still singular; **`Rcond g_int s` is the working fix.** | 4-front-end acceptance test |
| `docs/handoffs/HANDOFF_ngspice_compat*.md` (6 docs) | The ngspice-46 compatibility thread | VDMOS + passives | 3 of 4 claims retracted by the reporter. Only `Vshift` reproduced. Establishes the CI convention: failure on ngspice 46 = known issue; failure on 45.2/47+ = real regression. | 4 mini-repro decks quoted inline |
| `docs/backlog/HANDOFF_dmos200_subthreshold_analog.md` | **OPEN.** HV DMOS `kp` is a power-FET value | NDMOS200/PDMOS200 | `KP_PDMOS200=0.088`, `KP_NDMOS200=0.22` A/V²; strong inversion only near 5 mA; gm/I≈26/V at 10–55 µA → σ(trip) ≈ 340–440 mV. "Needs a maintainer decision before any model-card change." | inline repro |
| `docs/backlog/HANDOFF_dynamic_transient_microstepping.md` | **Filed OPEN, actually resolved.** | NDMOS200/PDMOS200 | 100 V all-clear / 120 V dynamics die. "Not the slew rate. 2 V/µs times out too." | `repro_*.cir` ×4 |
| `BRIEF_pdk_realism.md` (untracked) | **The audit plan.** Thesis: `kp`/`rd`/`rs` scaled to a power die, not the 10 µm cell | NDMOS200/PDMOS200 (+20 V pair) | See §6.1 — this is the most consequential unfiled document in the tree. | measurements described, not committed |
| `BRIEF_hv_monitor.md` (untracked) | HV monitor architecture question | NDMOS200/PDMOS200 | "**Critical gap: there is no analog MOS device between 5 V and 20 V.**" Subthreshold tables at W = 2…1000 µm. | none |
| `circuits/*/REPORT.md`, `SUMMARY.md`, `CHARACTERIZATION.md`, `MIRROR_CHAR.md`, `DESIGN_NOTES.md`, `SATURATION_SIGNOFF.md` | Per-circuit design reports | see §2.2 | Generated from results JSON by `report.py` / `summary.py` / `char_report.py` in each dir. | yes (generated) |
| `xschem/*/README.md` (5) | Usage/install only | — | Essentially no characterization data. Exceptions: `autohv/README.md` `"Id ramps to ~2.7 mA at Vgs=12 V"`; `delay_pulse/README.md` `"~20 ns nominal"`, `"≈ −20 %/+40 % over the PVT matrix"`. | — |

### 2.2 Testbenches and characterization scripts

| Path | Targets | Measures | Results alongside? |
|---|---|---|---|
| `pdk_validation/regression/run_smoke.py` | all 40 subckts | `.op` convergence, error patterns, per-op wall time (`--max-op-secs`, **default 4.0**) over 40 dev × 5 corners × 4 stat combos = **800 ops** | no file; console only |
| `pdk_validation/regression/run_passives.py` | 5 R + 4 C | `R(V)` from `.dc Vp -5 5 0.25`; `C(V)` from PWL 0→5 V/1 ms tran (dV/dt = 5000 V/s); diff vs golden at `--tol 1e-3` | **yes** — `goldens/*.json`, regenerable |
| `pdk_validation/regression/run_corners.py` | 9 probes, one per family | sign of `(v − v_TT)/|v_TT|` vs the expected sign table; 36 checks; `EQ_TOL=1e-4` | no file |
| `pdk_validation/regression/run_transients.py` | 13 decks | convergence + `TRAN_OK` marker + per-deck wall budget (2.0/3.0/4.0 s) | no file |
| `pdk_validation/regression/run_mc.py` | NMOS50 pair | σ(I) per device and σ(log I1/I2) per pair, MM and PROC axes, N=200; asserts within `--tol 0.30` | no file |
| `pdk_validation/switched_cap_audit/run_sc_audit.py` | NMOS18 switch + CMIM_STD/HI | Q-injection offset, gain error, RMS residual vs kT/C floor | no file (scratch deleted) |
| `circuits/async_logic_design/async_run.py` + `async_lib.py` | 8 cells × 3 domains | `gnp_` per-µm gate cap; `ratio_` β-ratio for V_M centering; `cap_` per-pin C_in (AC 1 MHz, rail-averaged); `vm_` V_M over 45 PVT pts; `tr_` rise/fall over 45 PVT pts | **yes** — `results.json` |
| `circuits/comparators/*/run_comparators.py`, `run_rr.py` | 9 comparator cells | offset σ (500-run MC for GP, 200 for RR), systematic offset, DC gain, tpd LH/HL, Iq, hysteresis, area | **yes** — `comparator_results.json` ×6 |
| `circuits/comparators/*/run_saturation.py` | same | ICMR bands via `Vds/Vdsat ≥ 1.4` (≥ 1.1 at 1.8 V) over 5 corners × 3 temps × 3 supplies | **NO FILE** — see §6.4 |
| `circuits/current_mirror_char/run_phase0.py`, `build_designs.py`, `run_dc.py`, `run_mc.py`, `compute_metrics.py`, `make_plots.py` | PMOS50, 3 mirror topologies | λ_eff, r_out, gain@Vdd/2, ramp nonlinearity, compliance, area; 1440 DC rows + 9000 MC runs | **yes** — 8 artifacts, all regenerable |
| `circuits/delay_pulse_design/dp_run.py`, `dp_char.py`, `gen_lib.py`, `verify.py` | 12 delay/pulse cells | `size_` L_R bisection to 20 ns; `pvt_` 45-pt delay/passthrough/edges; `mc_` 200-run σ; `verify_` functional | **yes** — `results.json`, `char.json` |
| `circuits/delay_cells_voltage_ramp/gen_delay_cells.py` (untracked) | PMOS50 mirror + CMIM_STD | ramp slope dV/dt over the 1→3 V window, 3 topologies × 4 currents | **NO FILE** — prose table only |
| `circuits/hv_charge_pump/hv_up_lvlsh/*.spice` | NDMOS200/PDMOS200 + NMOS50/PMOS50 | **nothing** — the only testbench in the directory is entirely commented out | none |

### 2.3 Results artifacts

**REPRODUCIBLE** (a present script demonstrably writes it):

| Artifact | Generator |
|---|---|
| `pdk_validation/regression/goldens/*.json` (9) | `run_passives.py --regenerate` |
| `circuits/async_logic_design/results.json` + 120 decks + REPORT/SUMMARY | `async_run.py`, `async_lib.py`, `report.py`, `summary.py` |
| `circuits/comparators/*/comparator_results.json` (6) | `run_comparators.py` / `run_rr.py` |
| `circuits/comparators/comparators_all.lib` | `gen_comparators_all.py` |
| `circuits/current_mirror_char/` — `phase0.json`, `designs.json`, `_geoms.json`, `results.json` (2.3 MB), `mc_results.json` (0.36 MB), `metrics.csv` (1440 rows), `crosscheck.json`, `plots/*.png` (6), `netlists/*.cir` (32) | the documented 6-script pipeline in `MIRROR_CHAR.md:257` |
| `circuits/delay_pulse_design/` — `results.json`, `char.json`, 49 decks, 13 cell libs, 3 reports | `dp_run.py`, `dp_char.py`, `gen_lib.py`, `verify.py`, `report.py`, `char_report.py` |
| `circuits/delay_cells_voltage_ramp/cells/*.lib` (12) + `tb/*.cir` (4) | `gen_delay_cells.py` — **but the generator itself is uncommitted** |

**ORPHANED** (numbers or decks with no generating/consuming script):

| Artifact | Note |
|---|---|
| `pdk_validation/device_limits.csv` | 86 rows. Repo-wide grep for `device_limits` hits only `.git/index`. Read by nothing, regenerated by nothing. |
| `pdk_validation/regression/mc/mc_nmos50_mismatch.cir` | Its own line 2 claims `"Used by run_mc.py"`. It is not — `run_mc.py` carries an inline `DECK_TEMPLATE` (lines 74–97). The deck has already drifted: it lacks the `@m.xm1.m0[gm]` prints `run_mc.py` requires (`raise RuntimeError("could not parse gm")`). Feeding it to `run_mc.py` would fail. |
| `pdk_validation/switched_cap_audit/sample_and_hold.cir` | Shadowed by an inline copy in `run_sc_audit.py:80`; hand-synced only, nothing enforces it. |
| `pdk_validation/bjt_avalanche_stress/*.cir` (4) | No README, no results file. Markers are `NPN_LV_OK`/`BJT_RAMP_OK`, not the `TRAN_OK` the harness greps for, so they cannot be adopted into Phase D unedited. |
| `pdk_validation/autohv_mismatch_mc.cir`, `autohv_passive_validation.cir`, `smoke_p0_*.cir` | Manual-run only, no asserts, non-standard markers. |
| Comparator ICMR / `Vds/Vdsat` sign-off tables | Extensively documented across `SATURATION_SIGNOFF.md`, `CHARACTERIZATION.md` §4 and 6 READMEs; **persisted nowhere.** `run_saturation.py` re-runs but writes no file, so the prose cannot be diffed against a re-run. |
| `circuits/delay_cells_voltage_ramp/` slope table | README prose only; no results file exists in the directory. |
| `circuits/comparators/comparators_all.lib.preswap` | Intentional frozen snapshot taken before `f505458` swapped the 4-FET EN buffer for PDK `INV_5V0` cells and before `c3d1b2a` fixed the `Xser` d/s order. Kept because `.preswap` is self-contained while the current file now depends on `async_logic_design/cells.lib`. |
| `b3v33check.log` ×3 (root = `pmos50_int`, `examples/` = `pmos33_int`, `circuits/delay_pulse_design/` = `pmos18_int`) | ngspice byproducts, each written into whatever cwd ngspice ran from. All three report `Pd = 0 is less than W` / `Ps = 0 is less than W` — i.e. **missing drain/source perimeter on the PMOS cards**, so junction perimeter capacitance and sidewall leakage are unmodeled. Referenced by no document; not in the CHANGELOG. |

### 2.4 Model-file annotations

The model files carry substantive provenance comments. Quoted verbatim, with the notable exception in §6.2.

- **The `temper`/`agauss` split rationale** (`.inc` 275–281): *"ngspice defers any expression that mentions temper to runtime per-temperature evaluation, where agauss is unresolvable; isolating the statistical product here keeps it parse-time. Each card line then reads e.g. `vto={VTO_<dev>_STAT + TC_VTO_<dev>*(temper-27)}`."*
- **Self-heating scope** (`.inc` 11–17): *"Rds(on)/kp thermal coupling NOT included in this first cut (would require behavioral rd/rs/kp rewrites)."*
- **Tempcos flagged uncalibrated** (`.inc` 218): `* === VDMOS temperature coefficients (deterministic; CALIBRATE) ===`. This is the only outstanding-work marker in either model file; there is no literal TODO/FIXME anywhere.
- **The two matrix-conditioning shunts**, repeated in all 13 VDMOS subckts:
  ```
  Rgmin  g g_int 1e9   ; gmin shunt: breaks the singular matrix when MM_ON=0 (DVTH_MM=0V) for cascoded LDMOS
  Rcond  g_int s 1e6   ; gives g_int a DC path to determined s -- fixes multi-instance floating-mirror singularity
  ```
- **DMOS sizing convention** (`.lib` 94 et al.): *"HV DMOS: width W is the size knob (m=W/W_REF); channel/drift length fixed at process min"*.
- **200 V drift physics** (`.lib` 353–356): *"RDRIFT scale factor is 3.0 (vs 1.2 on NDMOS200): PMOS drift in n-well has ~2.5x higher per-um R, so the per-um delta-R also scales by ~2.5x."*
- **Passive matching with literature citations** (`.lib` 473–581, `.inc` 202–205): Allen *CMOS Analog Circuit Design* for poly ~±30 % / n-well ~±40 % absolute and n-well VCR ~8000 ppm/V; Subramanian et al. for MIM σ ~0.1 % vs MOM ~0.65 %; US Pat 6,313,516 and US Pat 12,464,737 (**the latter number is above the currently issued US range — see §6.5**).
- **1/f noise derivation**, on each of 8 BSIM3 cards: *"tox=6.75n -> NMOS18 NOIA * (4.25/6.75)^2 ~ 0.40"* etc.
- **Binning assumption**, on the 18/33/50 cards: `+ binunit=1  $ NOTE: single global fit, no L/W bins defined`.

### 2.5 Git history as documentation channel

Commit messages are a first-class documentation channel here — several fixes are documented **only**
in the commit body plus the CHANGELOG. Every model-relevant commit appears in the §3 timeline.

### 2.6 Issues / PR text

None present locally. `.github/` contains only `workflows/regression.yml`. No exported issue notes.

---

## 3. Fix history timeline

Chronological. Each entry: hash · date · what was wrong · what changed · what justified it.

**`4f6e1cd` · 2026-05-22 · Initial commit.** 38-device flat library, corner-parameterized with
`PROC_ON`/`MM_ON`. Archaeologically important: at this point MOS Vth mismatch was injected with a
**behavioral gate source** — BSIM3 devices used `BGSHIFT g_int s V={V(g,s)-DVTH_MM}` (a B-source),
VDMOS used the `Vshift` VSRC. This is the origin of the mismatch-model migration in §4.5.

**`a19ddd5` · 2026-05-25 · VCR/VCC + layer-dependent matching added to passives.** Introduced the
`BVCR` and `Cextra` behavioral branches and the per-layer matching coefficients, justified by the
Allen / patent citations quoted in §2.4.

**`0e08f84` · 2026-05-25 · NDMOS200 drift window corrected to ~5.4–10 µm**; `L` relabelled as drift
length (not channel length); DMOS channel length documented separately.

**`6493511` · 2026-05-25 · `device_limits.csv` added.** Geometry bounds only — no voltage, current,
power, SOA or temperature ratings, then or now.

**`21d72ba` · 2026-05-27 · Four model-level bugs fixed in one commit** (empty body; documented in the
CHANGELOG diff): BJT breakdown rebuilt behaviorally as `BVCBO` after discovering the Gummel-Poon
`bv`/`ibv` parameters *"are not GP parameters and were silently ignored"*; NMOS12/PMOS12 migrated
Level-3 → BSIM3 level 49; VDMOS temperature coefficients added; bipolar `kf`/`af` added.
**This single commit covers three of the checklist items** (BSIM3 12 V fix, VDMOS tempco, BJT 1/f).

**`4855fdf` · 2026-05-27 · BGSHIFT → `delvto` for the 8 BSIM3 MOS**, plus `abs()` → `sqrt(V*V+1e-6)`
smoothing at 9 passive sites. Body: *"drop the external Vshift + g_int node split and apply DVTH_MM
via BSIM3's native delvto instance parameter, removing the extra series source and dangling node per
device."* Smoothing justified as *"Cusp-free at V=0 (better DC/Newton convergence), bias dependence
unchanged for |V| >> 1 mV."* VDMOS could not follow — `delvto` is BSIM-only.

**`ef6d369` · 2026-05-27 · P0: the entire VDMOS family was unusable.** `Error: no such function
'agauss'` because `vto`/`kp`/`rd`/`rs` mixed runtime `temper` with parse-time `agauss` in one braced
expression. Fix: hoist the statistical product into **44 parse-time `_STAT` params**. Verified all 11
VDMOS instantiate and converge at 27 °C and 125 °C.

**`3dfeec8`…`a8190e2` · 2026-05-27 · P1 Phases A–F, the regression suite.** Phase A 760-op smoke
(later 800); Phase B per-op wall budget; Phase C passive goldens; Phase D transients — the *"abs()
kink killers"*, pre-fix *">120 s, didn't finish"* vs post-fix *"~55 ms"*; **Phase E, which established
the AGAUSS convention** (see §4.5); Phase F CI.

**`415d8ea` · 2026-05-27 · P2.1 BJT avalanche audit — no code change.** All four BJTs stress-tested
under DC sweep to BVCBO+20 %, transient ramp, and switching above BVCEO. Conclusion: *"the only
simulation-time non-smooth constructs in the entire lib are the 4 BJT avalanche Bavl expressions"* —
every DMOS `max()` is parse-time. `abs(i(Vsen))` found to be *stabilizing*, and the 0.997 clamp turns
the high-Vcb region into a finite plateau rather than a divergence.

**`b4ce4e1` · 2026-05-27 · P2.2 corner sanity, 36/36.** Magnitudes recorded: NMOS18 ID +50 % FF /
−36 % SS; PMOS18 +57/−39; NDMOS20 ±22 %; NPN_LV ±18 %; PNP_LAT ±19 %; DIO_PN Vf ±0.23 %; RPOLY_HI
−10 %/+12 %; CMIM_STD ±3 %.

**`3b045ed` · 2026-05-27 · P3 switched-cap precision audit.** CMIM_STD 10 pF: Q_inj −4.67 mV, gain
+0.128 %, RMS resid 1.17 mV, kT/C floor 20.4 µV. CMIM_HI 20 pF: −2.32 mV, −0.350 %, 1.77 mV, 14.4 µV.
Conclusion: deterministic errors are 100–1000× the kT/C floor, so explicit thermal-noise injection
into the cap model is moot for SC apps.

**`b90b132` · 2026-05-27 · PDMOS120 + PDMOS200 added**, completing the HV PMOS family (38 → 40
devices, smoke 760 → 800). PDMOS200 `kp=0.088, rd=3.00, rs=1.38, bv=207, vto=−1.31`. Explicitly
flagged: *"the new models are engineered (NMOS→PMOS scaling from the existing 80 V pair), not
silicon-fit."* **The `bv=207` introduced here is the bug fixed a week later by `3a81be0`.**

**`0ceabc3` · 2026-05-28 · `Rgmin g g_int 1e9` added to all 13 VDMOS subckts.** Root cause: with
`MM_ON=0`, `Vshift` collapses to a 0 V VSRC; two LDMOS sharing a gate make KCL at that gate a
dependent equation → singular matrix. ngspice 45.2's KLU tolerates it via gmin-stepping; ngspice 46
aborts. Justification: *"Leakage at the largest expected DVTH_MM (~mV) is ~1 pA — 4 to 6 orders of
magnitude below any real mismatch sigma."* Regression `cascoded_ldmos.cir` added.

**`ee4f839` · 2026-05-28 · ngspice-compat thread closed.** Two follow-ups probed and rejected:
`delvto` on VDMOS → *"unknown parameter (delvto)"*; B-source-as-voltage → *"ngspice still emits a
`bshift#branch` variable — B-source-as-voltage has identical MNA structure to a VSRC."* Establishes
the CI convention on the residual ngspice-46 failure.

**`a4f2eaa` · 2026-05-30 · Parasitics #1 + #2: calibrated BSIM3 1/f noise + NQS.** `noimod=2` had been
set but `noia/noib/noic` left at ngspice defaults. Added per-class values scaled as 1/tox²:
NMOS18/PMOS18 (tox 4.25 n) NOIA 6.25e41 / 6.188e40; NMOS33/PMOS33 (6.75 n) 3.13e41 / 3.09e40;
NMOS50/PMOS50 (11 n) 1.56e41 / 1.55e40; NMOS12/PMOS12 (20 n) 9.38e40 / 9.28e39; plus `em=4.1e7, af=1,
ef=1`. NQS `nqsmod=1, elm=5`; op-time median 60 → 75 ms.

**`2f7f1ce` · 2026-05-30 · Parasitics #3: soft self-heating, `SH_ON` gated, default OFF.** Per-class
Rth/Cth: 20 V 200 K/W / 1e-6 J/K → 200 V 80 / 5e-6. Gated with parse-time `.if (SH_ON==1)`
*specifically because* multiplicative B-source gating *"would have reintroduced"* the VSRC-branch
solver problem. Cost ~40 ms parse overhead; smoke budget 2.0 → 4.0 s.

**`6606f45` · 2026-06-01 · Handoff filed: VDMOS terminal caps ~1000× too large.** See §6.2.

**`2cfb8de` · 2026-06-02 · THE VDMOS CAPACITANCE FIX.** All 13 VDMOS `_INT` cards had `cgs`,
`cgdmax`, `cgdmin`, `cjo` ~1000× too large for the `W_REF=10u` reference cell. **52 numerical edits =
4 cap params × 13 cards**, uniform ÷1000. Verified on NDMOS200 W=40u L=8u at AC 1 MHz:

| Vds | before | after |
|---|---|---|
| 0.1 V | 105 pF | 105 fF |
| 12 V | 29.5 pF | 29.5 fF |
| 100 V | 11.4 pF | 11.4 fF |
| 200 V | 8.84 pF | 8.84 fF |

Worked examples: `NDMOS20_INT: cgdmax 4.032e-10 → 4.032e-13, cgs 4.992e-10 → 4.992e-13, cjo 1.4e-10 →
1.4e-13`; `NDMOS200_INT: cgdmax 3.5e-11 → 3.5e-14, cgs 4.8e-11 → 4.8e-14, cjo 2.2e-11 → 2.2e-14`.
Physical consequence: *"the oversized drain-source cjo coupled HV drain slew straight onto
high-impedance cascode source nodes via displacement current, parking them at ~14 V instead of the
intended VDD−Vth ~4 V… Any HV-stack design using NMOS cascodes showed false SOA violations."*
Regression `coss_check.cir` added, asserting `Cdrain < 1 pF` (baseline ~105 fF, ~10× margin).

**`0cb9315` · 2026-06-04 · `MM_SIGMA` deterministic mismatch corners.** 40 subckts, 56 AGAUSS
expressions extended. The additive form was forced by a simulator limitation: *"probed ngspice's
.param expression parser and confirmed it does NOT support ==, !=, <, >= operators inside
expressions."* Regression `mismatch_corner.cir`: analytic −1.44 %, measured −1.48 %, tol ±10 %.

**`3a81be0` · 2026-06-05 · PDMOS200 breakdown re-rating.** Worst corner was 194.58 V — below its own
200 V class name, and the only VDMOS in the lib whose worst corner sat under its class. Audit table:
PDMOS20 +7.3 %, PDMOS60 +12.6 %, PDMOS80 +8.0 %, **PDMOS200 −2.7 % ← bug**, NDMOS200 +5.8 %. Fix: TT
207 → **230 V**, giving FF/SF 216.2 V (+8.1 % margin). Verified at FF/125 °C: 195 V went from
"Avalanche (mA+)" to "29.8 nA leakage". The N/P corner asymmetry was investigated and ruled *correct
physics*: *"FS = fast-N/slow-P → P-weak; SF = slow-N/fast-P → P-weak."*

**`4b05308` · 2026-06-05 · `Rcond g_int s 1e7` added to all 13 VDMOS.** `Rgmin` shunts `g_int`→`g`,
but in floating high-side mirrors `g` is itself floating; `s` is determined. Verified on 4 floating
PDMOS200 mirrors at VIN = 200 V: `voutA 2.19 V (5.0 V diff)`, `voutB 1.79 (4.3)`, `voutC 2.59 (5.7)`,
`voutD 2.07 (4.8)` — correctly ordered. Known limitation recorded: `.tran` on the same topology at
200 V still fails.

**`454959e` · 2026-06-05 · `Rcond` 1e7 → 1e6, fixing the TRAN micro-stepping.** Mechanism: *"in fast
TRAN, Cgs between g and s adds a frequency-dependent admittance that competes with Rcond. As VIN
rises, cap-mediated current at the floating gate grows and the matrix conditioning that was OP-tight
becomes TRAN-unsolvable."* All four `repro_*.cir` now pass: `slew_m43=0.68 V`, `slew_m57=0.47 mV`,
`slew_mvccm=0.11 V`; `tdly_43=29.2 ns`, `tdly_vccm=113 ns`, `tdly_57=207 ns`. Leakage at 1 MΩ ~1 µA/V
of DVTH_MM ≈ 5 nA at typical mismatch. Residual: a deck that *jumps* the rail to 200 V at t=0 with no
soft-start still micro-steps — *"'don't do that' rather than a real residual."*

**`92d6f39` · 2026-06-05 · Subthreshold-`kp` handoff filed.** Still open. Superseded in thesis by
`BRIEF_pdk_realism.md`, which argues this is not a modeling choice but a scale bug.

**`5cbd2e7` · 2026-06-10 · `tools/make_release.py`.** Defines the shippable PDK by allowlist.

**`86e9f02` … `dd13f73` · 2026-06-10 · async logic library.** Note `7aeaf76` fixed a hardcoded
Windows PDK path in all 120 decks; `dd13f73` deliberately deleted the `cells.lib` generator (the only
file ever deleted in the repo's history) to make the `.lib` the standalone source.

**`69860d9` … `6ed9b99` · 2026-06-25/26 · comparator family**, incl. two documented negative results:
pure current scaling does not speed the cell up (only current *density* does), and a 4×-density
variant *"fails the rule at 3.2 V, so it is not shipped."*

**`7da15ad`, `de71d6b` · 2026-07-12 · delay/pulse cells** cherry-picked from a now-deleted
`delay-pulse-cells` branch.

**`e0930f2` · 2026-07-12 · handoff triage.** 13 root `HANDOFF_*.md` split into `docs/handoffs/` (11
resolved) and `docs/backlog/` (2 open). A rename, not a deletion.

**`7824cf2` · 2026-07-13 · PMOS current-mirror characterization.** Phase 0 locks L = 2 µm (λ·L
minimized, area ∝ L²); standard cascode drops λ_eff ~1000× and holds it flat over PVT; wide-swing
adds +0.4 V compliance at equal area; `I_out(V_SD)` collapses across Vdd **to machine epsilon**.

**`660a3f7` … `0e103c4` · 2026-07-18 · xschem repairs.** No model changes.

**Deleted files, whole history:** exactly one —
`circuits/async_logic_design/gen_cells_lib.py` (`dd13f73`, deliberate). **No characterization data,
results, or model files were ever deleted.**

---

## 4. Conventions in force

### 4.1 `W_REF` / `L_REF`

- `W_REF = 10u`, declared in **all 13 VDMOS subckts**. The `.model` card describes **one 10 µm-wide
  reference cell**; instance sizing is purely by multiplier: `.param mtot={(W/W_REF)*M}`, then
  `M0 d g_int s NDMOS20_INT m={mtot}`. The `VDMOS` primitive has no W/L of its own.
- `L_REF = 8u`, declared **only** on NDMOS200 and PDMOS200, with `L_MIN=5u` and `Leff={max(L,L_MIN)}`.
  `L_REF` is the drift length at which the card's built-in `rd` is exact; a series resistor adds the
  delta: `RDRIFT={max(1.2*(Leff/L_REF-1)/mtot, 1e-6)}` (NDMOS200) / `3.0*` (PDMOS200).
- The 8 BSIM3 subckts have **no** `W_REF`/`L_REF` — they pass real `W`/`L` (defaults `W=10u L=1u`).

### 4.2 Units

Meters with SPICE suffixes throughout. Mismatch area normalizer explicitly converted to µm²:
`.param AUM2={(W/1u)*(L/1u)}`. Model values are SI/absolute: `tox` in m, `cj` in F/m², `cjsw` in F/m,
`cgso/cgdo/cgbo` in F/m, `rsh` in Ω/□, `Rth` in K/W, `Cth` in J/K. **VDMOS `cgs`/`cgdmax`/`cgdmin`/
`cjo` are absolute farads for the 10 µm cell**, scaled at instantiation by `m={mtot}` — this is the
convention the ÷1000 fix restored, and it is nowhere stated inside the model files (§6.2).
Voltage coefficients are quoted in ppm/V in comments but stored as fractions (`VCR1=200e-6`).

### 4.3 Corners

Five, selected by one global `.param case=0`: **0=TT, 1=FF, 2=SS, 3=FS, 4=SF**, decoded one-hot:

```
.param _isFF={(case==1)}  _isSS={(case==2)}  _isFS={(case==3)}  _isSF={(case==4)}
.param _isTT={1 - _isFF - _isSS - _isFS - _isSF}
```

Every corner-dependent parameter is a dot product, e.g.
`vth0={((0.48*_isTT + 0.4*_isFF + 0.56*_isSS + 0.4*_isFS + 0.56*_isSF))+P_DVTH_NMOS18}`.
Convention is consistent: **FS = fast-NMOS / slow-PMOS**, SF the reverse. Two orthogonal statistical
gates, both default OFF: `PROC_ON` (die-to-die) and `MM_ON` (local mismatch).

### 4.4 Temperature

`tnom=27` on all 8 BSIM3 cards and all 4 capacitor cards. VDMOS uses runtime `temper` with a 27 °C
reference on all four of vto/kp/rd/rs. Resistor and BJT/diode cards carry no `tnom` (BJT/diode temp
is via `eg=1.11 / xti=3 / xtb`).

**There is no `.temp`/`.options temp` statement and no stated qualification range anywhere in either
model file** — no `-40`, `125`, `150`, or `175`. For an automotive-labelled PDK the temperature range
is encoded only in the *characterization scripts* (which use −55/+27/+150 °C for logic and delay
cells, and −40/+27/+125 °C for comparators — note these two ranges disagree; §6.5).

### 4.5 Mismatch model

**Form** (`docs/MISMATCH_CORNERS.md` §1), uniform across all 40 devices:

```
X_MM = MM_ON*AGAUSS(0, X, 3)/scale + MM_SIGMA*X/3/scale
```

**The AGAUSS convention is the load-bearing fact** (established empirically in Phase E, `8485df1`):
*"`AGAUSS(mean, X, N)` in ngspice 45.2 uses the HSPICE convention — X is the clip bound at N sigmas;
true 1-sigma = X / N. Empirically: `AGAUSS(0, 1, 3)` over 200 samples → sigma ~0.34, range ±1.0."*
**Every literal in the lib is a 3σ bound; divide by 3 for 1σ.**

**Injection differs by family:**

| Family | Mechanism | Area scaling |
|---|---|---|
| 8 BSIM3 MOS | `delvto={DVTH_MM}` on `M0`, plus `WEFF={W*(1+DWREL_MM)}`, `LEFF={L*(1+DLREL_MM)}` | `1/sqrt(AUM2)` = 1/√(W·L) |
| 13 VDMOS | series `Vshift g g_int DC {-DVTH_MM}` (VDMOS rejects `delvto`) | `1/sqrt(max(mtot,1e-6))` — **width only, no length term** |
| 4 BJT + 6 diodes | `AREAEFF = AREA*(1 + …)` | `1/sqrt(AREA)` |
| 5 resistors | `RMM` scaling on `L` | `1/sqrt(AUM2)` |
| 4 capacitors | `CMM`, with `LS=sqrt(CMM)` applied to both L and W | `1/sqrt(AUM2)` |

**Coefficients (3σ):**
- Vth, BSIM3 (V·µm): NMOS18/PMOS18 **0.0105**; NMOS33/PMOS33 **0.012**; NMOS50/PMOS50 **0.0135**;
  NMOS12/PMOS12 **0.018**. ΔW/W = **0.0075**, ΔL/L = **0.0045** for all eight.
- Vth, VDMOS: 20 V + DNMOS20 **0.024**; 60 V **0.027**; 120 V **0.030**; 40 V **0.0085**;
  80 V **0.0095**; 200 V **0.011**. (Non-monotonic — see §6.5.)
- BJT/diode AREA: **0.012** for all ten.
- Resistors: RPOLY_HI 0.0075, RPOLY_LO 0.003, RNWELL 0.013, RNPLUS 0.005, RPPLUS 0.0055.
- Capacitors: CMIM_STD 0.0015, CMIM_HI 0.002, CMOM 0.006, CFRINGE 0.0075.

There is **no `AVT`/`AVB` named parameter** — the AVT role is played by these bare literals.

**`MM_SIGMA` semantics:** per-instance, default 0, signed sigma count. `MM_SIGMA=+3` pins the
parameter at exactly the +X bound. Any real value works, so `.step MM_SIGMA -3 3 0.5` sweeps natively.
The four-mode table is the hard contract; `(MM_ON=1, MM_SIGMA≠0)` is explicitly **"don't do this"** —
the terms *add*, they do not exclude.

**Migration history** (three distinct migrations, all in the CHANGELOG, **none of them in
`MISMATCH_CORNERS.md`**):
1. BSIM3: `BGSHIFT` B-source → external `Vshift` VSRC + `g_int` node split → native `delvto`
   (`4855fdf`). VDMOS could not follow.
2. VDMOS conditioning: nothing → `Rgmin 1e9` (`0ceabc3`) → `+ Rcond 1e7` (`4b05308`) →
   `Rcond 1e6` (`454959e`).
3. Conditional → additive `MM_SIGMA` form (`0cb9315`), forced by ngspice's parser.

### 4.6 Device limits

`pdk_validation/device_limits.csv`, columns `device,param,min,max,note`, 86 rows, 38 distinct devices,
params ∈ {L, W, M, AREA, LCH}. **Geometry bounds only** — no voltage, current, power, SOA, or
temperature ratings. The single electrical statement in the whole file is the embedded note
`"~5.4u = realistic 200V minimum"` on `NDMOS200,L,5.4,10.0`.

In-model breakdown lives on the cards instead: VDMOS `bv` 24/22 (20 V class) … 225 (NDMOS200) /
**230** (PDMOS200, post-re-rating), each with corner spread and a `P_DBV_*` statistical term;
diode `bv` DIO_PN 100 / DIO_FAST 80 / DIO_SCH 45 / DZ 5.6/12/24; BJT `BVCBO` in the subckt
(NPN_LV 14, PNP_LAT 18, NPN_HV 45, PNP_HV 32) with a behavioral avalanche branch (`MAV_BJT=4`,
clamped at 0.997).

### 4.7 Regression contract

ngspice **45.2** is the pinned dev baseline. Phases A/B (smoke 800 ops), C (9 passive goldens,
tol 1e-3), D (13 transients, per-deck wall budget), and P2.2 (36 corner sign checks) **gate CI**.
Phase E (Monte Carlo) is `continue-on-error` — *"a statistical sanity check… can occasionally land
outside tolerance due to small-N noise."* CI installs ngspice from apt on ubuntu-24.04 (≈41–42),
which the workflow itself acknowledges diverges from the 45.2 goldens.

---

## 5. Coverage matrix

Rows = device families. Columns = characterization type. **C** = characterized (artifact exists),
**P** = partial, **✗** = never. Paths given where an artifact exists.

| Family | DC | AC / caps | Noise | Mismatch-MC | Temperature | Corners |
|---|---|---|---|---|---|---|
| **BSIM3 NMOS/PMOS 18/33/50** | **C** `regression/run_smoke.py`, `run_corners.py`, `circuits/async_logic_design/decks/ratio_*`, `vm_*` | **C** `async_logic_design/decks/cap_*`, `gnp_*` (per-pin C_in, per-µm fF/µm) | **P** `transients/noise_check.cir` runs `.noise` on NMOS18 only — parses and converges, **no value asserted** | **C** `run_mc.py` (NMOS50 pair, σ 0.29 %/device, 0.42 % pair), `transients/mismatch_corner.cir` | **C** `async_logic_design/decks/vm_*`, `tr_*` at −55/+27/+150 °C | **C** `run_corners.py` (NMOS18/PMOS18 probes), 45-pt PVT in async + delay-pulse |
| **BSIM3 NMOS12/PMOS12** | **P** smoke + `xschem/autohv/examples/tb_nmos12_idvg.sch` (`Id ~2.7 mA at Vgs=12 V`) | ✗ | ✗ (NOIA assigned in `a4f2eaa`, never measured) | ✗ (not in `run_mc.py`; no `binunit`, no `P_TOX_*`/`P_CJ_*` — §6.5) | ✗ | **P** smoke only — **not among the 9 `run_corners.py` probes** |
| **PMOS50 specifically** | **C** `circuits/current_mirror_char/` — 1440 rows, 4 current decades, 3 topologies, λ_eff/r_out/compliance | ✗ | ✗ | **C** `mc_results.json`, **9000 runs** (3 designs × 3 topos × 2 modes × 500) | **C** `metrics.csv` −55/+27/+150 °C | **C** `metrics.csv` all 5 corners × 4 Vdd |
| **VDMOS 20/40/60/80/120 V** | **P** smoke + `run_corners.py` (NDMOS20/PDMOS20 only) | ✗ **no AC characterization of any VDMOS other than NDMOS200** | ✗ (explicitly out of scope in `a4f2eaa`) | ✗ no MC on any VDMOS | **P** tempcos applied (`21d72ba`) but flagged `CALIBRATE`; only smoke at 27/125 °C | **P** NDMOS20/PDMOS20 probed; 40/60/80/120 never |
| **NDMOS200 / PDMOS200** | **C** — and **contested**. `run_smoke.py`, `HANDOFF_dmos200_subthreshold_analog.md` (gm/I, Vov tables), `BRIEF_pdk_realism.md` (Isat, R_on at W = 10 µm) | **P** `transients/coss_check.cir` — NDMOS200 only, single point (W=40u L=8u, Vds=0.1 V), asserts only `< 1 pF` | ✗ | ✗ — mismatch coefficient (0.011) assigned, never validated | **P** `smoke_p0_vdmos_all.cir` at 27/125 °C; PDMOS200 breakdown verified at FF/125 °C | **C** for `bv` (`3a81be0` audit across all 5); DC otherwise unverified per corner |
| **DNMOS20 (depletion)** | **P** smoke only | ✗ | ✗ | ✗ | **P** smoke at 27/125 °C | ✗ not a `run_corners.py` probe |
| **BJT NPN_LV/HV, PNP_LAT/HV** | **C** smoke, `run_corners.py` (NPN_LV/PNP_LAT), `bjt_avalanche_stress/` ×4 (DC to BVCBO+20 %, ramp, switching above BVCEO) | **P** `transients/bjt_common_emitter.cir` exercises Miller loading; no C extraction | **P** `kf=1e-12, af=1` assigned on all four (`21d72ba`); never measured | ✗ AREA-mismatch coefficient (0.012) assigned, never validated | ✗ no temperature sweep (only `eg`/`xti`/`xtb` on the cards) | **C** `run_corners.py`, ±18 %/±19 % |
| **Diodes / Zeners** | **C** smoke, `run_corners.py` (DIO_PN Vf), `transients/diode_rectifier.cir` | **P** rectifier exercises junction cap + `tt`; **Zener `cjo` flagged 100–400× signal-diode value and never investigated** (§6.4) | ✗ | ✗ | ✗ | **C** DIO_PN Vf ±0.23 % |
| **Resistors (5)** | **C** `goldens/*.json` R(V), 41 pts, −5…+5 V | **C** same | **P** `kf/af/wf/lf/ef` assigned per layer; never measured | **C** `autohv_mismatch_mc.cir` — **but likely statistically inert, §6.5** | **P** `autohv_passive_validation.cir` sweeps −40/27/125 °C, no assert | **C** `run_corners.py` RPOLY_HI −10 %/+12 % |
| **Capacitors (4)** | **C** `goldens/*.json` C(V), 21 pts, 0…5 V | **C** same, + `switched_cap_audit` on CMIM_STD/HI | ✗ (audit concluded kT/C is moot: deterministic errors 100–1000× the floor) | ✗ | **P** `autohv_passive_validation.cir` VCC at 0/10/20 V bias | **C** `run_corners.py` CMIM_STD ±3 % |

**The clearest structural gap the matrix exposes:** the 40/60/80/120 V VDMOS classes have essentially
no characterization beyond `.op` convergence — no AC, no noise, no mismatch, no per-corner DC. They
were engineered by interpolation and never checked. NMOS12/PMOS12 are nearly as thin.

---

## 6. Gaps and inconsistencies

### 6.1 The audit's own premise is already written down but uncommitted

`BRIEF_pdk_realism.md` (untracked, modified 2026-07-22) is the most consequential document in the
tree and **is not in git**. Its thesis, stated in its own words: the DC parameters `kp`, `rd`, `rs`
*"are scaled to a discrete power-FET die, not to the 10 µm drawn cell the wrapper claims"* — the same
generator-scale bug as the capacitance bug, caught on AC and missed on DC.

Its evidence, which the audit should either build on or refute:

| device | implied W from `kp` | implied W from `R_on` | ratio | drawn W |
|---|---|---|---|---|
| NDMOS200 | 5936 µm | 2235 µm | 2.7× | 10 µm |
| PDMOS200 | 2353 µm | 863 µm | 2.7× | 10 µm |
| NDMOS20 | 83 720 µm | 43 288 µm | 1.9× | 10 µm |
| PDMOS20 | 40 066 µm | 20 865 µm | 1.9× | 10 µm |

*"Two independent DC parameters agree with each other to within ~2×, while both disagree with the
drawn width by 200–8000×."* The split-halves argument: `cgs = 48 fF` implies a 10 µm × 0.6 µm channel
at tox ≈ 20 nm (C_ox·W·L ≈ 10 fF, same order; a millimetre device would need ~6 pF), and σ(Vth) =
3.67 mV matches Pelgrom A_VT ≈ 15 mV·µm on a 10 µm device. Conclusion: *"caps and mismatch are scaled
to the drawn 10 µm cell; `kp`, `rd`, `rs` are scaled to a power die."*

It also explicitly names the capacitance fix as precedent: *"That fix establishes the intended
convention: `W_REF = 10 µm` is meant to be a genuine 10 µm drawn cell. The caps were corrected to it.
The DC parameters were not."*

The brief labels every number `[model]` / `[measured]` / `[assumed]` and flags the `[assumed]` set
(LDMOS Isat 0.2 mA/µm, 200 V specific R_on 2 mΩ·cm², cell pitch 20 µm, tox 20–40 nm, Pelgrom A_VT
10–20 mV·µm) as *"the weak link."* It also concedes: *"I have not checked the 40/60/80/120 V cards as
carefully as the 20 V and 200 V ones, or the capacitances post-fix"* — which lines up exactly with the
coverage holes in §5.

**Risk:** an untracked file has no history and no backup. So are `BRIEF_hv_monitor.md` and the whole
of `circuits/delay_cells_voltage_ramp/`.

### 6.2 Checklist verification — the eight known prior-work items

| # | Item | Status | Evidence / absence |
|---|---|---|---|
| 1 | **VDMOS capacitance fix** (13 cards, `cgs`/`cgdmax`/`cgdmin`/`cjo` ~1000× too large, uniform ÷1000) | **DOCUMENTED** — the best-documented change in the repo | Diagnosis: `docs/handoffs/HANDOFF_vdmos_caps.md` (156 lines, full pre-fix table for all 13 cards with line numbers). Fix: `2cfb8de` + CHANGELOG 2026-06-01 with the 4-point before/after AC table. Guard: `transients/coss_check.cir`. **But see the three sub-gaps below.** |
| 2 | **Gate-capacitance bug** (behavioral V-sources presenting 0 F at MOS gates) | **UNDOCUMENTED — no trace found** | Two independent agents searched the full tree (`*.md`, `*.py`, `*.cir`, `*.lib`, `*.json`) and the git log for `0 F`, `zero cap`, `no gate load`, `behavioral`, `B-source`, `Egate`, `gate cap`, `presents 0`, `does not load`, `VCVS`, `infinite impedance`. **Zero hits.** The nearest neighbours are all different bugs: `HANDOFF_cascode_vshift_singularity.md` describes a 0 V behavioral source at the gate but the complaint is a *singular matrix from the branch unknown*, and it argues the gate capacitance is *present* (*"connects to nothing but the MOSFET gate (a capacitance, no DC path)"*); the VDMOS cap bug is the opposite polarity (1000× too large); `b3v33check.log` reports missing `Pd`/`Ps` — drain/source *perimeter*, not gate. Note the async `cap_*` decks measure gate C correctly, with the AC source at the gate node and C extracted from its own branch current — a 0 F bug would have been visible there. **Recommend confirming this item is real before treating it as a property of this PDK.** |
| 3 | **BSIM3 NMOS12/PMOS12 fixes** | **PARTIALLY DOCUMENTED** | `21d72ba` (2026-05-27) migrated them Level-3 → BSIM3 level 49. **The commit body is empty**; the record lives only in the CHANGELOG diff. No characterization followed — see the NMOS12/PMOS12 row in §5 and the four residual defects in §6.5. |
| 4 | **VDMOS temperature dependence** | **PARTIALLY DOCUMENTED** | Applied in `21d72ba` (empty body), mechanism documented in the model file (`.inc` 218–273, `temper-27` on vto/kp/rd/rs). **Explicitly marked uncalibrated in-file: `(deterministic; CALIBRATE)`.** No temperature characterization deck exists for any VDMOS beyond the 27/125 °C smoke pair. |
| 5 | **BJT flicker noise + avalanche branches** | **DOCUMENTED (avalanche) / PARTIAL (flicker)** | Avalanche: `21d72ba` added the `Bavl` behavioral branch after finding GP `bv`/`ibv` *"are not GP parameters and were silently ignored"*; audited in depth by `415d8ea` (P2.1) across three stress regimes with a written conclusion; 4 audit decks + 1 regression deck. Flicker: `kf=1e-12, af=1` assigned in the same empty-bodied commit; **never measured or validated**. |
| 6 | **Mismatch migration BGSHIFT → series Vshift** | **DOCUMENTED, but split across sources and partly mis-stated** | The actual history is three-legged: initial `BGSHIFT g_int s V={V(g,s)-DVTH_MM}` B-source (`4f6e1cd`) → BSIM3 moved to native **`delvto`** (`4855fdf`), VDMOS stayed on the **series `Vshift` VSRC** because `delvto` is BSIM-only (proven twice: `unknown parameter (delvto)`). So it is not one migration but a fork. **`MISMATCH_CORNERS.md`, the doc that owns this contract, records none of it** — it documents only the end state. |
| 7 | **Delay-cell family characterization (RC vs current-starved; trimmable vs untrimmable error decomposition)** | **NOT FOUND AS DESCRIBED** | Two directories are adjacent but neither matches. `circuits/delay_pulse_design/` is an **RC + Schmitt** family (12 cells, 45-pt PVT, 200-run MC, σ/µ 5.10–6.28 %) with **no current-starved comparison**. `circuits/delay_cells_voltage_ramp/` (untracked) is a **current-mirror-into-MIM-cap voltage ramp**; its `cs`/`cw` suffixes mean **cascode-standard / cascode-wide-swing, not current-starved**. Repo-wide grep for `trimmab`, `untrimmab`, `current.?starv`, `error decomposition`, `systematic error`, `random error` returns only three `cmp_rr.lib` uses of "starved" (meaning a starved diff pair) and two forward-looking sentences in `delay_pulse_design/REPORT.md:102,104`. **No error decomposition exists in this repo.** |
| 8 | **Async logic ≤5 fF input-capacitance contract** | **DOCUMENTED — and enforced in code, not just prose** | `async_run.py:6-8`: `CAP_MODEL_TGT = 4.5` / `CAP_HARD = 5.0`, with a retreat loop (`Rstar *= 0.90`, ≤8 iterations) that backs off the P/N ratio until `cmax <= CAP_HARD`. Measured worst pin **4.978 fF** (NOR2/OR2 pin b, 1.8 V) — 0.022 fF of margin. Stated in `REPORT.md:3,17,119` and `SUMMARY.md:83`. The contract has a documented cost: NOR2/OR2 are flagged `cap_limited: true` and their V_M lands ~0.45–0.50 Vdd instead of centred, *"Relaxing the 5 fF limit would allow exact centering."* |
| 9 | **`sync_logic_design/` scoping or contract documents** | **DOES NOT EXIST** | There is no `sync_logic_design/` anywhere in the tree or in the history (`git log --diff-filter=D` shows one deleted file total, unrelated). The library that exists is `circuits/async_logic_design/` — combinational only, no sequential/synchronous cells. **Possibly a naming confusion with `async_logic_design`; possibly work in another repo or an unmerged branch.** The only branch ever referenced in commit messages, `delay-pulse-cells`, was cherry-picked and deleted. |

**Three sub-gaps inside the otherwise well-documented capacitance fix**, all audit-relevant:

- **Suggestion #1 of the handoff was never carried out**: *"Regenerate `cgs / cgdmax / cgdmin / cjo`
  for all 13 VDMOS `_INT` cards from process capacitance densities at the `W_REF=10µm` cell."* Only
  the verify step (#2) was done. The fix is a uniform ÷1000 justified by an order-of-magnitude
  argument, **not a re-derivation from process densities**. This matters directly: it means the caps
  are *self-consistently rescaled*, not *independently validated* — so `BRIEF_pdk_realism.md`'s use of
  `cgs = 48 fF` as an independent witness for the 10 µm cell rests on a value that was set by
  assuming the 10 µm cell.
- **Suggestion #3 was never carried out**: *"Consider corner-parametrizing the VDMOS caps with the
  `_isTT/_isFF/…` one-hot selector the way the diode `cjo` cards already are."* **VDMOS capacitances
  remain fixed across all five corners**, unlike every other corner-varying quantity in the lib.
- **The zener follow-up was explicitly deferred and never done.** CHANGELOG: zener `cjo` (TT) is
  `1.2e-10` (5V6), `5.5e-11` (12 V), `2.8e-11` (24 V) — *"100-400x the corresponding signal-diode
  `cjo=2.8e-13`. That's NOT exactly 1000x like the VDMOS slip, so it's a different magnitude problem…
  Recommended: a separate dedicated investigation before adjusting zener caps."* **No such
  investigation exists.** This is a live, named, unexamined realism defect.

### 6.3 An unexplained numerical discrepancy inside the capacitance fix

The handoff and the maintainer report **different measurements from the nominally identical deck**
(NDMOS200 W=40u L=8u, AC 1 MHz):

| Vds | `HANDOFF_vdmos_caps.md` (pre-fix) | CHANGELOG 2026-06-01 (pre-fix) | ratio |
|---|---|---|---|
| 0.1 V | 172 pF | 105 pF | 1.64× |
| 12 V | 52 pF | 29.5 pF | 1.76× |
| 200 V | 18.7 pF | 8.84 pF | 2.12× |

The ÷1000 conclusion is robust to this (both sets are ~1000× the physical target), but a consistent
1.6–2.1× gap on the same deck is unexplained in either document and nobody reconciled it. If the
audit re-measures, this is a known fork in the record.

### 6.4 Orphaned results and unpersisted numbers

- **Comparator ICMR / saturation sign-off** — the single largest body of characterization prose in
  the repo with no machine-readable backing. `run_saturation.py` exists in all 6 folders and is
  re-runnable, but writes no file. The tables in `SATURATION_SIGNOFF.md`, `CHARACTERIZATION.md` §4 and
  all six READMEs were transcribed by hand and **cannot be diffed against a re-run**.
- **`circuits/delay_cells_voltage_ramp/` slope table** — README prose only; and the whole directory,
  including its sole generator `gen_delay_cells.py`, is uncommitted. Its README is also the **only**
  record of two hard-won simulation findings: that `.tran … uic` is mandatory (*"`CMIM_STD` includes a
  behavioral voltage-coefficient branch (`Cextra`); with the simple mirror in the deck, the
  DC-operating-point path into that branch stalls the transient"*) and that the reset switch must be
  W = 100 µm (*"A weaker switch lets the node drift, which dithers the `Cextra` branch and stalls the
  run"*). Both would have to be rediscovered.
- **`device_limits.csv`** — 86 rows, zero readers, zero regenerators. Nothing validates that any deck
  respects these bounds.
- **`pdk_validation/bjt_avalanche_stress/`** (4 decks), **`sample_and_hold.cir`**,
  **`mc_nmos50_mismatch.cir`**, **`autohv_mismatch_mc.cir`**, **`autohv_passive_validation.cir`**,
  **`smoke_p0_*.cir`** — all orphaned, per §2.3.
- **README baseline tables** in `pdk_validation/regression/README.md` (Phase E σ values, Phase D
  per-deck wall times, SC audit numbers) are hand-transcribed from console output that is never
  persisted.
- **`circuits/hv_charge_pump/hv_up_lvlsh/`** — the only HV (200 V) *circuit* in the tree, and the only
  directory with zero characterization of any kind: no results file, no driver script, no sign-off, and
  its only testbench is entirely commented out. Its sizing params are labelled *"tunable"* / *"size for
  bias I"*, i.e. placeholders. NDMOS200/PDMOS200 appear nowhere else in `circuits/`.

### 6.5 Contradictions and defects found

**Between documents:**

1. **Device count.** `README.md:22` says 38 subckts; `QUICKSTART.md` and the xschem READMEs say 40;
   `.lib` header says *"All 38 .SUBCKT devices"*; `.inc` header says *"lists only the 76 devices, not
   the 38 internal *_INT models."* **Actual: 40 and 40.** Neither 38 nor 76 is correct.
2. **`MM_SIGMA` usage is documented backwards in one place.** `xschem/autohv/README.md:29` says
   `MM_SIGMA` *"needs global `MM_ON=1`"* — the direct opposite of the contract in `README.md`,
   `QUICKSTART.md`, `MISMATCH_CORNERS.md` and the CHANGELOG, all of which specify `MM_ON=0` and warn
   that the two terms add.
3. **`docs/backlog/README.md` item 2 is stale.** It lists the HV transient micro-stepping as open;
   the CHANGELOG entry of 2026-06-06 reports all four reproducers passing with `Rcond=1e6` and
   declares the downstream task unblocked at the full 200 V range. The backlog was never reconciled.
   The genuine residual is much narrower (a bare `.tran` that jumps the rail at t=0).
4. **Both `BRIEF_*.md` files quote the pre-re-rating `PDMOS200 bv=207`.** Current TT is **230 V**
   (`3a81be0`, 2026-06-05). If the audit reasons from the brief's verbatim model card, that field is
   stale.
5. **Three different minimum drift lengths for the 200 V LDMOS.** Code clamps at `L_MIN=5u`; the
   `.lib` comment says *"Recommended RESURF window ~5u..16u"*; `device_limits.csv` says
   `NDMOS200,L,5.4,10.0`. Both the minimum (5 vs 5.4) and the maximum (16 vs 10) disagree.
6. **Two incompatible temperature ranges in use.** Logic and delay-cell characterization uses
   −55/+27/+150 °C; comparator characterization uses −40/+27/+125 °C. Neither is stated anywhere as
   *the* PDK qualification range, and the model files encode no range at all.
7. **`pdk_validation/regression/README.md` has drifted from its own code in four places:** it says
   "all 38" devices and "760 ops" (code asserts 40, runs 800); it says `--max-op-secs` default 2.0
   (code says 4.0, bumped 2026-05-29); it tabulates 6 Phase D decks (there are 13); its Phase F gating
   table omits `run_corners.py`, which CI does gate on.
8. **`xschem/designs/NOTES.md` is stale** relative to the working tree — it records
   `CP_VoltageMonitor.sch` at commit `4bf81be`, but the file is modified with untracked `.bak` and
   `.prenudge` siblings.
9. **`mc/mc_nmos50_mismatch.cir:2` makes a false provenance claim** (*"Used by run_mc.py"*) — and the
   two have already drifted incompatibly.

**Inside the model files:**

10. **The VDMOS ÷1000 rescale is recorded nowhere in the model files.** The most consequential
    numeric change in the PDK lives only in `docs/CHANGELOG.md` and `HANDOFF_vdmos_caps.md`. A future
    regeneration of these cards has nothing in-file to warn it, and a reader of the `.inc` alone has
    no way to know these are per-10 µm-cell absolute values.
11. **VDMOS mismatch coefficients are non-monotonic across the voltage ladder.** 20 V = 0.024,
    60 V = 0.027, 120 V = 0.030 (rising with class) but 40 V = 0.0085, 80 V = 0.0095, 200 V = 0.011 —
    roughly 3× smaller. The 200 V part ends up better-matched than the 20 V part. The two sets look
    like they came from different generator passes (corroborated by cosmetic formatting differences:
    `NDMOS40_INT` writes `a=0.30`/`rb=0.10` where 20/60/120 write `0.3`/`0.1`).
12. **`Rcond g_int s 1e6` is a 1 MΩ DC leakage path from gate to source on every VDMOS** — ~5 µA of
    static gate current at 5 V drive, which a real MOS gate does not have. It exists purely as a
    matrix-conditioning fix and is not flagged as a modelling artefact anywhere outside the inline
    comment. (The CHANGELOG's leakage figure of ~5 nA is computed against `DVTH_MM` (~5 mV), not
    against the full gate drive.)
13. **`Rth`/`Cth` comments claim "(override per-instance)" but they are not overridable** — they are
    `.param` declarations *inside* the subckt body, absent from the `.subckt` interface line.
14. **`RSH0` is dead in all five resistor subckts** — declared, never referenced, and duplicates the
    TT sheet value only, so under any non-TT corner it silently disagrees with the `_INT` card.
15. **Capacitor subckts hardcode the TT `CJ0`** for the voltage-coefficient term, so under FF/SS the
    linear cap moves ±3 % but the VCC increment does not.
16. **`B_pdiss` on the 200 V parts measures the wrong power.** Sense source is `Vsense dd dd_sense`
    but power is `I={V(d,s)*i(Vsense)}` — `V(d,s)` includes the drop across the external `Rdrift`, so
    the dissipation driving `TJ` includes a resistor the transistor model does not.
17. **NMOS12/PMOS12 carry four distinct residual defects** from the Level-3 → BSIM3 migration:
    stale Level-1 statistical parameter names applied to BSIM3 parameters (`P_DVTO_` → `vth0`,
    `P_DVMAX_` → `vsat`, `P_DRSH_` → `rdsw`, where every other MOS uses `P_DVTH_`/`P_DVSAT_`/
    `P_DRDSW_`); **two independent random draws multiplied into `u0`**
    (`u0={(…)*(1+P_DUO_NMOS12)*(1+P_DKP_NMOS12)}`, inflating σ(u0) to ~15.6 % vs a single 10 % term
    elsewhere — a leftover from a Level-1 card that had separate UO and KP); hard-constant
    `tox`/`cj`/`cjsw`/`js` with no corner or statistical terms, unlike the other six; and no
    `binunit=1` line.
18. **`device_limits.csv` has no rows at all for PDMOS120 or PDMOS200** (38 devices listed vs 40 in
    the lib). PDMOS200 is one of only two devices that takes an `L`, and it is the one device whose
    `L` is unbounded by the limits table. The same two are missing from `smoke_p0_vdmos_all.cir`,
    which instantiates 11 of 13 VDMOS while its header claims "all 11". Plausibly the origin of the
    stale "38" in the READMEs.
19. **Suspicious citation.** `.lib:473` cites *"US Pat 12,464,737"* — a number above the currently
    issued US range, unlike the plausible *"US Pat 6,313,516"* cited at `.inc:205`.

**In the verification infrastructure:**

20. **Assertion coverage is much thinner than the phase names imply.** Of 13 Phase D decks, only
    **two** check an electrical quantity (`coss_check.cir` asserts `Cdrain < 1 pF`;
    `mismatch_corner.cir` asserts `log(I1/I2)` in a window). The other 11 `echo TRAN_OK`
    unconditionally — they gate on convergence and wall time only. Phase C goldens are the only
    numerical regression net and they cover **passives exclusively**. `run_corners.py` checks *signs*,
    not magnitudes. **Nothing in CI would catch a 20 % BSIM3 `vth0` shift** — or, notably, a repeat of
    the very class of scale error that `BRIEF_pdk_realism.md` alleges is still present in `kp`.
21. **`self_heating.cir`'s header claims it verifies `V(XN.TJ)` settles to ~5.7 K, but the
    `.control` block never reads `V(XN.TJ)`.** That claim is unbacked by any assertion.
22. **`autohv_mismatch_mc.cir`'s 500-iteration MC loop is likely statistically inert.** It loops
    `reset` + `op` *inside a single ngspice invocation*, but `run_mc.py`'s own documented finding is
    that `.param AGAUSS` is drawn at parse time and only re-randomizes across `-b` invocations
    (*"CLI -D rndseed=N does NOT affect .param AGAUSS, because .param is parsed before the .control
    block"*). If so, all 500 iterations see identical resistances, every printed σ ≈ 0, and the
    layer-ordering claim the deck exists to demonstrate is unverifiable. `run_mc.py` treats exactly
    this condition as a hard error in its own pre-flight probe. **Not confirmed by running (read-only
    task) — inferred from the sibling script. Worth checking early in the audit.**
23. **CI runs a materially older ngspice than the goldens were generated on** (apt on ubuntu-24.04,
    ~41–42, vs the pinned 45.2 baseline), with no version assertion — `ngspice --help | head -1 || true`
    cannot fail. A silent apt bump can move Phase C's numerical baseline with no signal.
    Additionally, `write_golden` stamps `"ngspice_version": "45.2"` as a **hardcoded string literal**,
    so a golden regenerated on CI would still claim 45.2.
24. **A third party's home directory is hardcoded in 69 places across 37 files** — all referencing
    user `christopherklaus` (`/Users/christopherklaus/Documents/ngspice/autohv-bicmos180-pdk` or
    `C:/Users/christopherklaus/AppData/Local/Temp`). 65 of them stem from one line,
    `circuits/current_mirror_char/mirror_lib.py:20`, which stamps the path into all 32 generated
    netlists — **so none of the `current_mirror_char` decks run on this machine as committed**, even
    though the directory is otherwise the most reproducible in the tree. Two of the remaining four are
    inside the release allowlist and not in `SANITIZE_FILES`:
    `pdk_validation/bjt_avalanche_stress/dc_sweep_through_breakdown.cir:17` and
    `pdk_validation/switched_cap_audit/sample_and_hold.cir:44`. **The release zip therefore ships a
    third party's username** — precisely the leak class `make_release.py` exists to prevent (it scrubs
    task IDs and emails but has no rule for filesystem paths).
25. **The release export is broken as delivered.** `make_release.py`'s `INCLUDE` allowlist omits
    `circuits/` entirely, but the shipped `examples/07_async_cells_usage.cir` and
    `08_delay_pulse_cells_usage.cir` `.include` files under `circuits/`, and 45 of the shipped xschem
    symbols resolve against those same libs. `collect_files()` warns only on missing INCLUDE entries,
    never on dangling `.include` targets, so this fails silently.

### 6.6 Things that look characterized but aren't

- **VDMOS 40/60/80/120 V classes.** Present in the smoke suite, symbol libraries, `device_limits.csv`
  and the sizing tables — but never AC-characterized, never noise-characterized, never MC'd, and not
  among the corner probes. Their `bv` values were audited once (`3a81be0`) only as a side-effect of
  the PDMOS200 investigation.
- **VDMOS capacitances post-fix.** `coss_check.cir` checks **one device at one bias point** with a
  threshold 10× above the expected value. It would catch a re-introduced 1000× slip; it would not
  catch a 5× error, and it says nothing about the other 12 cards.
- **All assigned-but-unmeasured statistical and noise parameters:** BJT `kf`/`af`, the BSIM3
  `NOIA/NOIB/NOIC` sets, the VDMOS `TC_*` tempcos (self-flagged `CALIBRATE`), `MAV_BJT`, all Rth/Cth
  thermal defaults, and every mismatch coefficient except the NMOS50 Vth term validated in Phase E.
- **The whole library's absolute magnitudes.** Stated repeatedly and honestly, most compactly in
  `README.md:128-131`: *"physically plausible defaults rather than silicon-extracted values —
  calibrate to your process. Breakdown is held at the model card rating regardless of `L`."*

---

## 7. Suggested entry points for the audit

Ordered by expected information per unit effort, not by severity.

1. **`docs/CHANGELOG.md`** — read it end to end first. Nothing else in the repo compresses the
   history as well, and several fixes exist nowhere else in prose.
2. **`BRIEF_pdk_realism.md`** — the audit's own hypothesis, already argued with numbers. Commit it
   before working from it.
3. **`docs/handoffs/HANDOFF_vdmos_caps.md`** — the template for how this class of bug was found,
   argued, and fixed last time, including the two suggestions that were never carried out (§6.2).
4. **`circuits/current_mirror_char/MIRROR_CHAR.md`** — the methodological high-water mark: ideal
   sources labelled as instruments, per-row provenance tags in `metrics.csv`, `[projection]` values
   walled off from measured ones. Worth matching.
5. **§6.5 items 20 and 22** — the two findings that would change how much the existing verification
   evidence can be trusted.
