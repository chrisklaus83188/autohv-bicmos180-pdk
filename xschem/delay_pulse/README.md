# delay_pulse/ — AutoHV edge-delay & pulse-generator symbols

12 symbols for `circuits/delay_pulse_design/cells.lib` (4 archetypes ×
1V8/3V3/5V0). Regenerate with `bash xschem/gen_dly_syms.sh`.

| Archetype | Function (non-inverting) | ~20 ns nominal |
|---|---|---|
| **DLYR** | rising edge delayed, falling passthrough | delay |
| **DLYF** | falling edge delayed, rising passthrough | delay |
| **PHI** | HIGH pulse on rising edge, falling passthrough | pulse width |
| **PLO** | LOW pulse on falling edge, rising passthrough | pulse width |

Each is a "timing box": `in` left, `out` right, with a two-row in→out waveform
inside showing the edge behavior. Ports (all): `in out vdd gnd`.

## Power is connected BY TEXT (no wires/pins)
Only `in`/`out` are pins. Supply/ground are net-name properties `VPWR` (default
**vdd**) and `VGND` (default **0**), shown as text. Netlists as
`xU1 in out vdd 0 DLYF_5V0`. Drive net `vdd` once; ground `0` is automatic.

## Using them
1. Place a cell (`Insert -> delay_pulse/<CELL>`), wire `in` and `out`.
2. Drop **`autohv_lib`** (PDK models + corner) and **`dly_lib`** (includes
   `cells.lib`, adds `.option method=gear maxord=2` for the RC nodes, `.global vdd`).
3. Drive `vdd`.

Note: timing tracks RC and spreads ≈ −20 %/+40 % over the PVT matrix (see REPORT.md).
Verified: DLYF_5V0 delays the falling edge ~20 ns at the nominal corner.
