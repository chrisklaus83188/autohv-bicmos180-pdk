# High-Side Gate-Driver Level Shifter — First-Qualification Report
### AutoHV BiCMOS180 PDK · 200 V class (NDMOS200 / PDMOS200) · `circuits/hv_charge_pump/hv_up_lvlsh/`

<sub>Models: **v2-grounded** (frozen) · simulator: **ngspice-45** · V_HV = 200 V rail, V_BOOT = 12 V bootstrap, V_DDL = 5 V logic.</sub>

**First characterization of this circuit.** Its only prior testbench was the commented example in `levelshifter_top.spice`; it had never been simulated. This is a *minimal first qualification* (Step-0 ruling 4): verify function at the 200 V rail and measure output levels and bias currents. Placeholder sizings are the `levelshifter_top.spice` defaults (HV whv/whvp = 40 µm, lhv = 8 µm; LV wp = 20 µm / wn = 10 µm), consistent with `docs/sizing-guide.md`.

## 1. Function at the 200 V rail — VERIFIED (DC operating point)

SW held at 200 V, BOOT floating 12 V above it (212 V). The high-side latch is set/reset by the low-side ON/OFF commands and the buffered outputs `ON_HS`/`OFF_HS` swing between SW (200 V) and BOOT (212 V) — a clean 12 V high-side gate-drive referenced to the 200 V rail.

| State | Q (V) | QB (V) | ON_HS (V) | OFF_HS (V) | I_BOOT | I_VDD |
|---|---|---|---|---|---|---|
| idle | 210.65 | 210.65 | 200.0 | 200.0 | 690.8 µA | 0.17 µA |
| set | 199.96 | 211.99 | 212.0 | 200.0 | 12.0 µA | 4.87 µA |
| reset | 211.99 | 199.96 | 200.0 | 212.0 | 12.0 µA | 4.87 µA |

- **Set** (ON=5 V): `ON_HS` → 212 V (BOOT, high-side driver on), `OFF_HS` → 200 V (SW). Latch Q/QB = 200/212 V.
- **Reset** (OFF=5 V): outputs flip — `ON_HS` → 200 V, `OFF_HS` → 212 V; Q/QB = 212/200 V.
- **Idle** (ON=OFF=0): the cross-coupled latch sits metastable-symmetric (Q ≈ QB ≈ 210.7 V); set/reset resolves it deterministically.
- **Bias current** from the 12 V bootstrap: ~0.69 mA standing (idle, through the R1/R2 bias resistors + mirror legs), ~12 µA in the resolved set/reset states.

## 2. Switching (transient) — DOES NOT CONVERGE (redesign scope)

The full switching transient (SW ramped to 200 V, then ON/OFF one-shots) **fails to complete**: the timestep collapses to ~1e-20 s at t ≈ 5.01e-07 s on node `von#branch`. This is *not* a sizing problem and is left for a later redesign (Step-0 ruling 4 — do not redesign here).

**Failure mode.** The stall originates in the `DELAY_CELL` block: its series `RPOLY_HI` resistors carry a behavioral voltage-coefficient branch (BVCR), and in combination with the floating HV cascode nodes this forms a stiff loop that micro-steps to a standstill early in the ramp (before SW even reaches high voltage). Simulator aids (`rshunt`, `gmin`, `method=gear`, `uic`) shift the reported node but do not clear the collapse.

**Redesign scope (later, not this program):**
- Replace the delay-cell behavioral-R timing with a device-based delay, or gate the BVCR branch so it is well-defined from t=0 (this mirrors the `.tran uic` / behavioral-branch findings already documented for `delay_cells_voltage_ramp` and the VDMOS `Rcond` handoffs).
- Give the HV cascode source nodes (S5/S6/S9/S12) a defined start (small pull-down or `.ic`) so the level-shift legs do not float at t=0.
- Re-verify dynamic set/reset propagation and high-side slew once the above land; the **static function at 200 V is already correct**, so the redesign is a convergence/robustness task, not a topology change.

## 3. Files

- `tb_levelshifter_op.cir` — DC operating-point verification (this report's §1).
- `tb_levelshifter.cir` — full transient (documents the §2 non-convergence).
- `run_lvlsh.py` — this harness. `lvlsh_results.json` — machine-readable results + provenance.
- Design: `levelshifter_top.spice` (top), `levelshifter.spice`, `buffer.spice`, `delay_cell.spice`, `inv.spice` (unchanged — no redesign in this program).