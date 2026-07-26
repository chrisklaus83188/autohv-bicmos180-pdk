# Post-Fix Staleness Register — AutoHV BiCMOS180 PDK (phase 3)

The phase-3 fix batch changed device electrical behaviour. Every `circuits/` characterization that
sized or measured against the **old** models is now stale. Re-characterizing them is out of scope for
phase 3; this register exists so nobody trusts stale numbers. Each entry: what changed, and what to
re-run.

| circuit study | invalidated by | what to re-run |
|---|---|---|
| ~~`circuits/delay_pulse_design/`~~ **✅ DONE (v2.1-circuits Phase C)** | RPOLY_HI **tc1 sign flip** (+0.0006→−0.0014) changes the delay's temperature drift. (The RPOLY_LO 12× note does **not** apply — this design uses RPOLY_HI, sheet unchanged; see finding.) | re-ran full pipeline: nominal L_R unchanged (no ÷12), slowest corner flipped hot→cold, verify.py ALL OK. See `circuits-requalification.md` Phase C |
| ~~`circuits/delay_cells_voltage_ramp/`~~ **✅ DONE (v2.1-circuits Phase C)** | junction caps (F6) load the RAMP node → ramp slope drops ~9–26 % | re-ran `gen_delay_cells.py` (netlists identical) + re-measured slopes; README updated, 2 findings preserved. See `circuits-requalification.md` Phase C.2 |
| ~~`circuits/comparators/` (9 cells)~~ **✅ DONE (v2.1-circuits Phase B + report layer)** | matching widened → offset σ increases; PMOS50 tempco → offset drift | re-ran `run_comparators.py`/`run_rr.py` at N=200: 5 V σ ×2.1–2.8 (median 2.4), 3.3/1.8 V flat. Saturation orphan fixed. Reports regenerated via `report_refresh.py` AUTOGEN fences (GR2-amendment mechanism). See `circuits-requalification.md` Phase B |
| ~~`circuits/async_logic_design/` (24 cells)~~ **✅ DONE (v2.1-circuits Phase A)** | BSIM3 **junction caps (F6)** → input-cap contract re-verified; **drive** unaffected (Idsat cards unchanged for BSIM3) | re-ran `async_run.py` under the 6.5 fF contract; see `circuits-requalification.md` Phase A |
| ~~`circuits/current_mirror_char/` (PMOS50 study)~~ **✅ DONE (v2.1-circuits Phase D + report layer)** | **matching widened** → MC σ up; λ/r_out unaffected (DC) | re-ran pipeline (DC identical, MC σ ×2.47 mismatch at N=200). Fixed macOS-home-dir + space-in-path wrdata + 2 pdk_validation decks. `MIRROR_CHAR.md` DC/MC sign-off tables regenerated via `report_refresh.py` fences. See `circuits-requalification.md` Phase D |
| ~~`circuits/hv_charge_pump/`~~ **✅ FIRST-QUAL DONE (v2.1-circuits Phase E)** | was uncharacterized; VDMOS kp/rd re-derivation | built the first working testbench; DC function VERIFIED at 200 V (12 V high-side swing SW↔BOOT, bias currents measured). Switching transient does NOT converge — documented failure mode + redesign scope. See `circuits-requalification.md` Phase E |
| `pdk_validation/regression/goldens/*.json` | **passive rsh + tc1 + VCC extraction** — the 9 passive goldens were generated against old sheets/TCs | **`run_passives.py --regenerate`** (phase-3 deferred — see below) |
| `pdk_validation/regression/transients/` wall-time baselines | **VDMOS cap re-derivation** shifts switching speed; **F6 junction caps** shift BSIM3 switching | re-baseline Phase D wall times |

## Regeneration status (phase 3b — closed)

- **Passive goldens: REGENERATED.** `run_passives.py --regenerate` re-cut the 9 goldens against the new
  sheets/TCs. Regression suite green: smoke 800/800, corners 36/36, passives 9/9, transients 13/13.
- **Full phase-2 harness re-baseline: DONE.** `run_all.py` re-run; `characterization-scorecard.md`
  regenerated against the merged `2.1-phase3b` anchors → **280 pass**, 19 residual hard-fails, all
  dispositioned as extraction/criterion/deferred in `sizing-open-findings.md` (v2) — none a model defect.
- **Phase-D transient wall times: re-baselined** after the VDMOS cap / F6 junction-cap changes;
  `multi_mirror_floating.cir` dispositioned to an OP-convergence check (the large physical rd re-triggered
  floating-mirror micro-stepping under `tran`; OP converges cleanly and is the Rcond fix's actual target).

## Regeneration status (phase 4 — freeze)

- **Regression suite: GREEN** — smoke 800/800, corners 36/36, passives 9/9, transients 13/13. The
  phase-4 HV rd re-anchor (P 200 V rd ~4.5×) did **not** re-trigger the floating-mirror convergence
  issue. Passive goldens **not** regenerated (no fix moved them); their version stamp refreshed to the
  actual `ngspice --version` (ngspice-45).
- **Full harness re-baseline: DONE** — `run_all.py` re-run (561 measurements) → `characterization-scorecard.md`
  regenerated against `anchor-values.json` v4.0-phase4-grounded → **298 pass** (was 280), 20 hard-fail +
  6 error, all dispositioned in `sizing-open-findings.md` (v3). Movers vs v1: DIO_SCH tt resolved,
  va_class ×11 now pass, zener bv-vs-T non-flat, DNMOS20 recentred; theta-extraction count 7→9 (larger
  rd) — all expected. New: `va_class` (2-point gds Early voltage) added to the VDMOS family module.
- **Sizing guide: REGENERATED** from the final model state (`sizing-guide.{md,json}` v4.0-phase4). DNMOS20
  self-bias W ~2× smaller (Idss 54.7→106 µA/µm); VDMOS mirror points stable (the gm/Id≈6 point is
  insensitive to rd); md now assembled by a single correct writer (interleave bug fixed).
- **device_limits.csv v2** adopted (geometry + V/I/P/T SOA) with a real pre-flight reader in `run_all.py`.

**The `circuits/` studies (delay, comparators, async-logic, mirror MC, charge-pump) were still NOT
re-run** — that characterization refresh remains the follow-up pass. The table above is the complete
list of what it must cover; the model side is now **frozen and tagged (`v2-grounded`)**.

## Requalification status (v2.1-circuits — the circuits re-qualification program)

The follow-up pass is now in progress. Program summary + old-vs-new tables:
`docs/circuits-requalification.md`. Entries clear here as each phase lands.

- **Phase A — `async_logic_design/`: ✅ CLEARED.** Re-generated all 24 cells under the Step-0
  input-cap contract (5.0→6.5 fF hard / 6.0 fF target). `results.json`/`REPORT.md`/`SUMMARY.md`
  regenerated, stamped `v2-grounded` / `ngspice-45`. NOR2 `cap_limited` True→False in all 3 domains
  (now centres V_M); NOR/OR/XOR fall edges +45–60 % from F6 output junction load; input-pin cap
  itself unmoved (gate load, not junction). No model-defect findings.
- **Phase B — `comparators/`: ✅ CLEARED (data + reports).** Re-ran all 6 sub-libraries at MC N=200
  against `v2-grounded`; regenerated `comparator_results.json` ×6, `comparators_all.lib`, and (orphan
  fix) `saturation_{margin,icmr}.json` ×3. Offset re-signed: 5 V cells σ ×2.1–2.8 (median 2.4);
  3.3/1.8 V flat. Report layer: the hand-authored `.md` reports had no generators (GR2 conflict);
  ruled Option A and implemented via `circuits/report_refresh.py` AUTOGEN fences (provenance-stamped,
  `--check`-enforceable). No model-defect findings.
- **Phase C — `delay_pulse_design/` + `delay_cells_voltage_ramp/`: ✅ CLEARED.** delay_pulse: re-ran
  full pipeline (dp_run→dp_char 200-MC→gen_lib→verify→reports) against `v2-grounded`; verify.py ALL OK.
  **Finding filed:** the pre-registered "L_R ÷12" is a brief-premise error — the design uses RPOLY_HI
  (sheet unchanged), not RPOLY_LO; nominal L_R unchanged, slowest corner flipped hot→cold via the
  RPOLY_HI tc1 sign-flip. voltage-ramp: re-measured (slopes ↓9–26 % from F6 RAMP-node junction caps),
  README updated with both findings preserved. No model-defect findings.
- **Phase D — `current_mirror_char/`: ✅ CLEARED (data + reports).** Fixed the hardcoded macOS home-dir
  path (mirror_lib ROOT → `__file__`-derived; 65 netlists now use a relative include), the bare-`ngspice`
  calls, the space-in-repo-path `wrdata` failure, and 2 pdk_validation deck paths — the pipeline had
  never run on this machine. Re-ran DC (conclusions identical: L=2 µm, cascode λ_eff flattening, r_out) +
  MC at N=200 (σ ×2.47 mismatch — the pre-registered ×2.4). metrics/plots/netlists regenerated.
  `MIRROR_CHAR.md` DC/MC sign-off tables regenerated via `report_refresh.py` fences (GR2 amendment). No
  model findings.
- **Phase E — `hv_charge_pump/hv_up_lvlsh/`: ✅ CLEARED (first qualification).** The repo's only 200 V
  circuit had never been simulated (only a commented testbench). Built `tb_levelshifter_op.cir` (DC),
  `tb_levelshifter.cir` (transient), `run_lvlsh.py` (harness + REPORT). DC function VERIFIED at the
  200 V rail (set/reset toggles ON_HS/OFF_HS a clean 12 V between SW=200 V and BOOT=212 V; idle bias
  0.69 mA, active 12 µA). The switching transient does NOT converge (delay-cell BVCR / HV-cascode
  timestep collapse) — documented as the redesign scope, not fixed here (Step-0 ruling 4). No model
  findings (the OP solves cleanly at 200 V).

**All five phases have landed. The staleness register is empty.**
