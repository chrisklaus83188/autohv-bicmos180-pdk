# AutoHV BiCMOS 180 PDK (Qucs-S)

A self-contained device library for a 180 nm high-voltage BiCMOS process, packaged
for **schematic capture and netlisting in Qucs-S**. Place devices, wire them, set
parameters, and export an ngspice-flavored SPICE netlist for simulation in your
target simulator.

- **38 devices** across seven families (core MOSFETs, HV DMOS/LDMOS, BJTs, diodes,
  Zeners, resistors, capacitors)
- **5 process corners** selected by one global parameter
- **Process + mismatch statistics** via two orthogonal switches

See **[docs/AutoHV_BiCMOS180_PDK_Reference.docx](docs/AutoHV_BiCMOS180_PDK_Reference.docx)**
for the full device reference and user guide.

## Repository layout

```
autohv_bicmos180_case.lib            # the library: 38 .subckt wrappers (reference this)
autohv_bicmos180_case_models.inc     # global params, corner selectors, .model cards
autohv_bicmos180_case/               # one .sym schematic symbol per device (38 files)
docs/                                # PDK reference manual (.docx)
examples/                            # runnable ngspice example decks
```

The `.lib` includes the `.inc` on its first line via a relative path, so the two
files must stay in the same folder. The symbol folder must be named exactly
`autohv_bicmos180_case` (matching the `.lib` base name) and sit beside the `.lib`.

## Install into Qucs-S

Copy the library files and symbol folder into your Qucs-S workspace user library so
the layout under `user_lib/` is:

```
<workspace>/user_lib/
    autohv_bicmos180_case.lib
    autohv_bicmos180_case_models.inc
    autohv_bicmos180_case/   (the 38 .sym files)
```

Restart Qucs-S so the Libraries dock re-scans. The devices appear under the
`autohv_bicmos180_case` library. Re-place any devices already on a schematic after
updating, since the symbol is baked in at placement time.

## Quick usage

In a simulation deck, reference the `.lib` and keep the `.inc` beside it. Three
global parameters control everything:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `case`    | 0       | Process corner: 0=TT, 1=FF, 2=SS, 3=FS, 4=SF |
| `PROC_ON` | 0       | 1 = enable die-to-die process variation |
| `MM_ON`   | 0       | 1 = enable local device mismatch |

```spice
.include "autohv_bicmos180_case.lib"
.param case=0
.param PROC_ON=0
.param MM_ON=0

Vdd d 0 1.8
Vg  g 0 1.8
X1  d g 0 0 NMOS18 W=10u L=1u M=1   ; d g s b

.op
.end
```

## Examples

Runnable ngspice decks in `examples/` (each `.include`s the library via `../`):

- `01_nominal_op.cir` — typical-corner operating point
- `02_corner_sweep.cir` — step `case` over all five corners
- `03_monte_carlo.cir` — process + mismatch on a current mirror
- `04_ndmos200_sizing.cir` — 200 V LDMOS on-resistance vs drift length

```
cd examples
ngspice -b 01_nominal_op.cir
```

## Device sizing at a glance

| Family | Ports | Size parameters |
|--------|-------|-----------------|
| Core MOSFET (NMOS/PMOS 12/18/33/50) | d g s b | `W`, `L`, `M` |
| HV DMOS/LDMOS (N/PDMOS, DNMOS20)    | d g s   | `W`, `M` (plus `L` on `NDMOS200`) |
| Bipolar (NPN/PNP)                   | c b e   | `AREA` |
| Diode / Zener                       | a c     | `AREA` |
| Resistor                            | p n     | `L`, `W` |
| Capacitor                           | p n     | `L`, `W` |

Ports are listed in pin order; that order is what the generated netlist uses.

## Notes

The DMOS drift-length window and coefficients on `NDMOS200`, and the qualitative
resistor/capacitor descriptions, are physically plausible defaults rather than
silicon-extracted values — calibrate to your process. Breakdown is held at the model
card rating regardless of `L`. See the reference manual, Section 8, for the full list
of caveats.
