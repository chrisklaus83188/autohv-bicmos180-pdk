# Quickstart — AutoHV BiCMOS 180 PDK in ngspice

A 1-page guide to running simulations with this PDK. For the complete device list,
parameters, and worked examples, see
[`docs/AutoHV_BiCMOS180_PDK_Reference.docx`](docs/AutoHV_BiCMOS180_PDK_Reference.docx).

## 1. What you need

Only two files are required to simulate:

```
autohv_bicmos180_case.lib            # the 38 devices — this is what you .include
autohv_bicmos180_case_models.inc     # models, corners, statistics — pulled in by the .lib
```

Keep them in the **same folder**: the `.lib` includes the `.inc` by relative name.
(The `autohv_bicmos180_case/` symbol folder is only for drawing schematics in Qucs-S
and is not needed for simulation.)

## 2. Minimal deck

```spice
.include "autohv_bicmos180_case.lib"
.param case=0          ; corner: 0=TT 1=FF 2=SS 3=FS 4=SF
.param PROC_ON=0       ; 1 = die-to-die process variation
.param MM_ON=0         ; 1 = local device mismatch

Vdd d 0 1.8
Vg  g 0 1.8
X1  d g 0 0 NMOS18 W=10u L=1u M=1   ; pin order: d g s b

.op
.end
```

Run it from the folder holding the two library files:

```
ngspice -b mydeck.cir
```

## 3. The three global knobs

| Parameter | Default | Effect |
|-----------|---------|--------|
| `case`    | 0       | Selects one process corner for the whole run (0=TT, 1=FF, 2=SS, 3=FS, 4=SF) |
| `PROC_ON` | 0       | Set to 1 to enable die-to-die process variation |
| `MM_ON`   | 0       | Set to 1 to enable per-device local mismatch |

Set them anywhere before the analysis line. `case` is global — one corner per run;
sweep it across runs for a corner analysis.

## 4. Devices at a glance

| Family | Examples | Ports (pin order) | Size parameters |
|--------|----------|-------------------|-----------------|
| Core MOSFET | NMOS/PMOS 12, 18, 33, 50 | d g s b | `W`, `L`, `M` |
| HV DMOS/LDMOS | NDMOS 20–200, PDMOS 20–80, DNMOS20 | d g s | `W`, `M` (plus `L` on `NDMOS200`) |
| Bipolar | NPN_LV/HV, PNP_HV/LAT | c b e | `AREA` |
| Diode / Zener | DIO_PN/FAST/SCH, DZ_5V6/12/24 | a c | `AREA` |
| Resistor | RPOLY_HI/LO, RNWELL, RNPLUS, RPPLUS | p n | `L`, `W` |
| Capacitor | CMIM_STD/HI, CMOM, CFRINGE | p n | `L`, `W` |

Voltage classes are encoded in the name (NMOS18 = 1.8 V, NDMOS200 = 200 V). Pin order
is what the netlist uses, so list nodes in that order on the instance line. Full
descriptions are in the reference manual.

## 5. Example decks

Runnable decks live in [`examples/`](examples/) (each includes the library via `../`):

| Deck | Analysis |
|------|----------|
| `01_nominal_op.cir` | Operating point at the typical corner |
| `02_corner_sweep.cir` | Step `case` over all five corners |
| `03_monte_carlo.cir` | Process + mismatch on a current mirror |
| `04_ndmos200_sizing.cir` | 200 V LDMOS on-resistance vs drift length |
| `05_nmos_idvds.cir` | NMOS output characteristics (`.dc`, stepped Vgs) |
| `06_cmos_inverter_tran.cir` | CMOS inverter switching (`.tran`, delay measurement) |

```
cd examples
ngspice -b 05_nmos_idvds.cir
```

## 6. Common pitfalls

- **Separate the files and the include breaks.** The `.lib` and `.inc` must sit
  together; run ngspice from that folder or give a full path in `.include`.
- **Wire the bulk.** Core MOSFETs are 4-terminal (`d g s b`) — connect `b`.
- **Use plain `.include`.** This is a flat library with no `.lib`/`.endl` sections.
- **DMOS size by `W`/`L`/`M`, not `AREA`.** Only bipolars, diodes, and Zeners use `AREA`.
