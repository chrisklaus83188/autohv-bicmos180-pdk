# Post-Fix Staleness Register — AutoHV BiCMOS180 PDK (phase 3)

The phase-3 fix batch changed device electrical behaviour. Every `circuits/` characterization that
sized or measured against the **old** models is now stale. Re-characterizing them is out of scope for
phase 3; this register exists so nobody trusts stale numbers. Each entry: what changed, and what to
re-run.

| circuit study | invalidated by | what to re-run |
|---|---|---|
| `circuits/delay_pulse_design/` | **RPOLY_LO rsh 25→300 Ω/□** (12× resistance change) — the delay RC is set by RPOLY_HI + CMIM_HI, but any cell using RPOLY_LO shifts; also RPOLY_HI **tc1 sign flip** changes the delay's temperature drift qualitatively | re-run `dp_run.py` / `dp_char.py`; the 20 ns targets and the −20 %/+40 % PVT spread will move |
| `circuits/delay_cells_voltage_ramp/` (untracked) | PMOS50 **kt1/ute added** (Vth tempco was ~0, now −1.6 mV/°C) + junction caps (F6) — the mirror ramp slope and its temperature drift change | re-run `gen_delay_cells.py` measurements |
| `circuits/comparators/` (9 cells) | BSIM3 **junction caps (F6)** now non-zero → input/parasitic caps and delay change; **matching widened 3–14×** → offset σ increases; PMOS50 **tempco** → offset drift | re-run `run_comparators.py` / `run_rr.py`; **offset σ will roughly triple** (matching was that optimistic) |
| `circuits/async_logic_design/` (24 cells) | BSIM3 **junction caps (F6)** → the ≤5 fF input-cap contract must be re-verified (caps were understated); **drive** unaffected (Idsat cards unchanged for BSIM3) | re-run `async_run.py`; **the ≤5 fF contract is the item most likely to break** — junction cap was missing entirely |
| `circuits/current_mirror_char/` (PMOS50 study) | PMOS50 **kt1/ute** (tempco), **matching widened**, **junction caps** — λ/r_out mostly unaffected (DC), but MC σ and temperature behaviour change | re-run `run_mc.py`; the σ(λ)/matching clouds widen |
| `circuits/hv_charge_pump/` | **VDMOS kp/rd wholesale re-derivation** — every HV device behaves differently (this is the F1 fix). Any level-shifter timing/current is now different | uncharacterized to begin with; no stale numbers, but the netlists now behave physically |
| `pdk_validation/regression/goldens/*.json` | **passive rsh + tc1 + VCC extraction** — the 9 passive goldens were generated against old sheets/TCs | **`run_passives.py --regenerate`** (phase-3 deferred — see below) |
| `pdk_validation/regression/transients/` wall-time baselines | **VDMOS cap re-derivation** shifts switching speed; **F6 junction caps** shift BSIM3 switching | re-baseline Phase D wall times |

## Regeneration status (phase 3)

- **Passive goldens: NOT yet regenerated.** They will fail against the new sheets/TCs by design. Run
  `python pdk_validation/regression/run_passives.py --regenerate` and commit — this is a required
  follow-up before the regression suite is green again.
- **Full phase-2 harness re-baseline: PARTIAL.** The trigger device and the sizing sweep are validated;
  the complete 548-measurement after-picture scorecard over all corners is the deferred re-run (see
  `sizing-open-findings.md`). The fix commits each carry their own targeted verification.

**None of the `circuits/` studies were re-run in phase 3** — the brief scoped that out. This register
is the complete list of what a follow-up characterization pass must refresh.
