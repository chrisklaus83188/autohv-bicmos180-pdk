# Post-Fix Staleness Register — AutoHV BiCMOS180 PDK (phase 3)

The phase-3 fix batch changed device electrical behaviour. Every `circuits/` characterization that
sized or measured against the **old** models is now stale. Re-characterizing them is out of scope for
phase 3; this register exists so nobody trusts stale numbers. Each entry: what changed, and what to
re-run.

| circuit study | invalidated by | what to re-run |
|---|---|---|
| `circuits/delay_pulse_design/` | **RPOLY_LO rsh 25→300 Ω/□** (12× resistance change) — the delay RC is set by RPOLY_HI + CMIM_HI, but any cell using RPOLY_LO shifts; also RPOLY_HI **tc1 sign flip** changes the delay's temperature drift qualitatively | re-run `dp_run.py` / `dp_char.py`; the 20 ns targets and the −20 %/+40 % PVT spread will move |
| `circuits/delay_cells_voltage_ramp/` (untracked) | PMOS50 **kt1/ute added** (Vth tempco was ~0, now −1.6 mV/°C) + junction caps (F6) — the mirror ramp slope and its temperature drift change | re-run `gen_delay_cells.py` measurements |
| ~~`circuits/comparators/` (9 cells)~~ **◑ DATA DONE, reports pending (v2.1-circuits Phase B)** | matching widened → offset σ increases; PMOS50 tempco → offset drift | re-ran `run_comparators.py`/`run_rr.py` at N=200: 5 V σ ×2.1–2.8 (median 2.4), 3.3/1.8 V flat. Saturation orphan fixed (writes JSON). `.md` reports await ruling — see `circuits-requalification.md` Phase B + `handoffs/HANDOFF_comparator_report_regeneration.md` |
| ~~`circuits/async_logic_design/` (24 cells)~~ **✅ DONE (v2.1-circuits Phase A)** | BSIM3 **junction caps (F6)** → input-cap contract re-verified; **drive** unaffected (Idsat cards unchanged for BSIM3) | re-ran `async_run.py` under the 6.5 fF contract; see `circuits-requalification.md` Phase A |
| `circuits/current_mirror_char/` (PMOS50 study) | PMOS50 **kt1/ute** (tempco), **matching widened**, **junction caps** — λ/r_out mostly unaffected (DC), but MC σ and temperature behaviour change | re-run `run_mc.py`; the σ(λ)/matching clouds widen |
| `circuits/hv_charge_pump/` | **VDMOS kp/rd wholesale re-derivation** — every HV device behaves differently (this is the F1 fix). Any level-shifter timing/current is now different | uncharacterized to begin with; no stale numbers, but the netlists now behave physically |
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
- **Phase B — `comparators/`: ◑ DATA CLEARED, reports pending.** Re-ran all 6 sub-libraries at
  MC N=200 against `v2-grounded`; regenerated `comparator_results.json` ×6, `comparators_all.lib`,
  and (orphan fix) `saturation_{margin,icmr}.json` ×3, all provenance-stamped. Offset re-signed at
  measured values: 5 V cells σ ×2.1–2.8 (median 2.4, the pre-registered figure); 3.3/1.8 V flat.
  The hand-authored `.md` reports have no generator scripts (conflict with ground rule 2) — escalated
  to the orchestrator (`handoffs/HANDOFF_comparator_report_regeneration.md`); report regeneration
  finishes once ruled. No model-defect findings.
- **Phases C–E** (delay/pulse + voltage-ramp, mirror MC, HV charge pump): pending.
