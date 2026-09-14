# Transmission gates — AutoHV BiCMOS 180 PDK

18 CMOS analog-switch cells: three supply domains, three impedance classes,
two body options. Sizing is derived from the characterization below rather
than assumed, and every cell is cross-checked against the device-level data
it was sized from.

| | |
|---|---|
| netlist authority | `circuits/transmission_gates/cells.lib` (18 `.subckt`) |
| symbols / schematics | `xschem/transmission_gates/` |
| simulator | ngspice `ngspice-45` |
| model tag | `v2-grounded` |
| corners | TT FF SS FS SF |
| supply | nominal ±10 % |
| temperature | −55 / +27 / +150 °C |

## 1. Cell list

`TG_<class>_<domain>` ties the bodies to the rails: NMOS body to `gnd`, PMOS
body to `vdd`. `TGB_<class>_<domain>` brings the two bodies out as pins `bn`
and `bp`. Both carry an internal inverter, so only `en` is driven.

```
TG_<class>_<dom>    a b en vdd gnd
TGB_<class>_<dom>   a b en bn bp vdd gnd
```

| cell | Wn total | Wp total | finger W × M (N / P) | inverter Wn / Wp |
|---|---|---|---|---|
| `TG_1K_1V8` / `TGB_1K_1V8` | 4 µm | 10 µm | 4×1 / 10×1 | 0.4 / 1 µm |
| `TG_100R_1V8` / `TGB_100R_1V8` | 40 µm | 100 µm | 40×1 / 100×1 | 4 / 10 µm |
| `TG_10R_1V8` / `TGB_10R_1V8` | 400 µm | 1000 µm | 100×4 / 100×10 | 40 / 100 µm |
| `TG_1K_3V3` / `TGB_1K_3V3` | 4.6 µm | 11.5 µm | 4.6×1 / 11.5×1 | 0.46 / 1.15 µm |
| `TG_100R_3V3` / `TGB_100R_3V3` | 46 µm | 115 µm | 46×1 / 57.5×2 | 4.6 / 11.5 µm |
| `TG_10R_3V3` / `TGB_10R_3V3` | 460 µm | 1150 µm | 92×5 / 95.83×12 | 46 / 115 µm |
| `TG_1K_5V0` / `TGB_1K_5V0` | 8.4 µm | 21 µm | 8.4×1 / 21×1 | 0.84 / 2.1 µm |
| `TG_100R_5V0` / `TGB_100R_5V0` | 84 µm | 210 µm | 84×1 / 70×3 | 8.4 / 21 µm |
| `TG_10R_5V0` / `TGB_10R_5V0` | 840 µm | 2100 µm | 93.33×9 / 100×21 | 84 / 210 µm |

Per-finger width is `Wtot / ceil(Wtot / 100 µm)`, which keeps fingers as wide
as the 100 µm fabrication window allows. That is deliberate — see §7.

## 2. Minimum-size gate: where the resistance peaks

Both devices at the fabrication floor, `L = Lmin`, TT / nominal / 27 °C. The
on-resistance is measured as `dV / dI` with a 1 mV probe across the switch,
swept over the full input range.

| domain | Wmin | Ron at 0 V | Ron at Vdd | peak Ron | peak at |
|---|---|---|---|---|---|
| 1V8 | 0.22 µm | 5206 Ω | 1.774e+04 Ω | 1.089e+05 Ω | 1.01 V |
| 3V3 | 0.3 µm | 8813 Ω | 2.791e+04 Ω | 5.767e+04 Ω | 2.11 V |
| 5V0 | 0.4 µm | 1.65e+04 Ω | 4.655e+04 Ω | 8.002e+04 Ω | 3.30 V |

The peak sits well above mid-rail in every domain, because at equal widths the
NMOS is the stronger device and the crossover where both are weak shifts up
toward the positive rail. That is what motivates §3.

## 3. Wp / Wn balance

At a fixed total drawn width — the area proxy — the split between the two
devices was swept and the peak-over-level Ron recorded. Minimizing peak Ron at
fixed total width is the same as minimising area for a given peak Ron.

| domain | best ratio at Wtot = 2 µm | best at Wtot = 20 µm | peak Ron at 20 µm |
|---|---|---|---|
| 1V8 | 2.0 | 2.0 | 826.4 Ω |
| 3V3 | 3.0 | 3.0 | 846.4 Ω |
| 5V0 | 2.5 | 2.5 | 1558 Ω |

The optimum is width-independent and the minimum is shallow: anything from 2.0
to 3.0 is within a couple of percent. **Wp/Wn = 2.5 is frozen for the whole
family**, which is within 2 % of the per-domain optimum everywhere.

## 4. Resistance versus size

Total drawn width swept geometrically at Wp/Wn = 2.5, peak-over-level Ron
recorded. Above roughly 50 µm of total width the product `Ron × Wtot` is
constant, so the curve is a single number per domain and body option.

| domain | Ron·W, bodies at rails | Ron·W, bodies at the signal | body-effect penalty |
|---|---|---|---|
| 1V8 | 1.386e+04 Ω·µm | 7091 Ω·µm | 1.96× |
| 3V3 | 1.624e+04 Ω·µm | 1.092e+04 Ω·µm | 1.49× |
| 5V0 | 2.939e+04 Ω·µm | 2.084e+04 Ω·µm | 1.41× |

Read it as: total width for a target resistance is `Ron·W / target`. Taking
the bodies off the rails and onto the signal node buys a factor of 1.4 to 1.9,
and buys the most exactly where it is needed most, at 1.8 V.

The three classes follow from that constant, rounded to a decade family:

| domain | 1 kΩ | 100 Ω | 10 Ω |
|---|---|---|---|
| 1V8 | 14 µm | 140 µm | 1400 µm |
| 3V3 | 16.1 µm | 161 µm | 1610 µm |
| 5V0 | 29.4 µm | 294 µm | 2940 µm |

## 5. PVT envelope

Five corners × three supplies × three temperatures = 45 points, and at every
one of them the full input-level sweep, so `Ron max` is a worst case over
level as well as over PVT. Bodies at the rails — the shipping configuration.

| cell | Ron typ | Ron min | Ron max | max/typ | worst-case point |
|---|---|---|---|---|---|
| `TG_1K_1V8` | 1269 Ω | 146 Ω | 3.08e+05 Ω | 242.7× | SS 1.62V -55C level=0.8424V |
| `TG_100R_1V8` | 99.36 Ω | 14.07 Ω | 9834 Ω | 99.0× | SS 1.62V -55C level=0.8586V |
| `TG_10R_1V8` | 9.8 Ω | 1.402 Ω | 922.8 Ω | 94.2× | SS 1.62V -55C level=0.8586V |
| `TG_1K_3V3` | 1090 Ω | 287.5 Ω | 2364 Ω | 2.2× | SS 2.97V -55C level=1.6335V |
| `TG_100R_3V3` | 101.2 Ω | 27.73 Ω | 206.7 Ω | 2.0× | SS 2.97V 150C level=1.9305V |
| `TG_10R_3V3` | 10.05 Ω | 2.766 Ω | 20.51 Ω | 2.0× | SS 2.97V 150C level=1.9305V |
| `TG_1K_5V0` | 1039 Ω | 343.7 Ω | 2156 Ω | 2.1× | SS 4.5V 150C level=3.06V |
| `TG_100R_5V0` | 99.85 Ω | 33.39 Ω | 206 Ω | 2.1× | SS 4.5V 150C level=3.105V |
| `TG_10R_5V0` | 9.96 Ω | 3.338 Ω | 20.55 Ω | 2.1× | SS 4.5V 150C level=3.105V |

The 3.3 V and 5 V families hold a **2.1× max-over-typical** spread and a
6–8× total spread, which is an ordinary switch specification. The 1.8 V family
does not, and that is the main finding of this work.

With the bodies driven to the signal node instead (the `TGB` cells wired that
way), the same matrix gives:

| cell | Ron typ | Ron max | max/typ |
|---|---|---|---|
| `TGB_1K_1V8` | 564.9 Ω | 5013 Ω | 8.9× |
| `TGB_100R_1V8` | 50.72 Ω | 275.6 Ω | 5.4× |
| `TGB_10R_1V8` | 5.041 Ω | 26.63 Ω | 5.3× |
| `TGB_1K_3V3` | 709.8 Ω | 1454 Ω | 2.0× |
| `TGB_100R_3V3` | 67.98 Ω | 138 Ω | 2.0× |
| `TGB_10R_3V3` | 6.769 Ω | 13.73 Ω | 2.0× |
| `TGB_1K_5V0` | 725.5 Ω | 1492 Ω | 2.1× |
| `TGB_100R_5V0` | 70.87 Ω | 145.1 Ω | 2.0× |
| `TGB_10R_5V0` | 7.075 Ω | 14.48 Ω | 2.0× |

## 6. The 1.8 V dead zone

At the slow corner with the supply 10 % low and the die cold, the 1.8 V
rail-tied gate very nearly opens near mid-rail. Both devices are simultaneously
marginal: the NMOS gate overdrive is under 0.8 V while its body effect is at
full strength, and the PMOS is in the same state mirrored. Resistance rises by
two orders of magnitude.

| supply | corner | temp | peak Ron, TG_100R_1V8 |
|---|---|---|---|
| 1.80 V | TT | 27 °C | 99 Ω |
| 1.80 V | SS | −55 °C | 902 Ω |
| 1.62 V | SS | 150 °C | 283 Ω |
| 1.62 V | SS | 27 °C | 974 Ω |
| 1.62 V | SS | −40 °C | 5.47 kΩ |
| 1.62 V | SS | −55 °C | 9.83 kΩ |

Supply droop is the dominant term, not temperature: at the nominal 1.8 V rail
the same cold slow corner costs only 9×. Below about 1.7 V the two threshold
voltages stop overlapping and the gate has no input level at which either
device is strongly on.

Holding Ron under 3× its class nominal, the guaranteed input window at the
worst point is:

| cell | bodies at rails | bodies at the signal |
|---|---|---|
| `1K_1V8` | 0..0.680 and 1.021..1.620 | 0..0.794 and 0.907..1.620 |
| `100R_1V8` | 0..0.713 and 1.004..1.620 | full 0..vdd |
| `10R_1V8` | 0..0.713 and 1.004..1.620 | full 0..vdd |
| `1K_3V3` | full 0..vdd | full 0..vdd |
| `100R_3V3` | full 0..vdd | full 0..vdd |
| `10R_3V3` | full 0..vdd | full 0..vdd |
| `1K_5V0` | full 0..vdd | full 0..vdd |
| `100R_5V0` | full 0..vdd | full 0..vdd |
| `10R_5V0` | full 0..vdd | full 0..vdd |

Three ways to live with it, in order of preference:

1. **Use the `TGB` cell at 1.8 V and drive the bodies from the signal node.**
   That alone recovers the full input range on the 100R and 10R classes.
2. **Restrict the guaranteed signal range** to the window in the table and
   treat the band around mid-rail as a don't-care.
3. **Over-drive `en` above the supply.** Outside the scope of these cells, and
   it needs a charge pump, but it is the standard fix.

## 7. Why the smallest class scales worse than 1/W

Between the 1 kΩ and 100 Ω classes the ten-to-one width step does not buy a
clean ten-to-one resistance step in the dead zone — it buys about 34× at 1.8 V.
The cause is BSIM3's narrow-width threshold term. None of the AutoHV MOS model
cards set `K3` or `W0`, so both sit at the BSIM3 defaults of 80 and 2.5 µm, and
the model therefore raises Vth on narrow devices by roughly

```
dVth = K3 * tox * phi_s / (Weff + W0)
```

which is about 84 mV at W = 1 µm and 3 mV at W = 100 µm. In strong inversion
that is a second-order effect and `Ron × W` stays flat, which is why §4 works.
In the subthreshold dead zone the current depends exponentially on Vth and the
same 80 mV becomes a factor of 20.

Two consequences:

- Per-finger width is chosen as wide as the fabrication window allows, never
  split into many narrow fingers. Splitting would make every class behave like
  the small one at the cold corner.
- **These narrow-width numbers are uncalibrated.** They are BSIM3 defaults, not
  extracted from this process, so the size of the 1.8 V dead zone carries real
  model uncertainty. The qualitative conclusion — that a 1.8 V rail-tied gate
  opens up at slow/cold/low-supply — does not depend on them.

## 8. Current range

Two separate limits. The device rating is the PDK DC current density times the
NMOS width, which binds because near the ground rail the NMOS carries
everything. The useful limit is almost always the voltage drop instead.

| cell | device Idc limit | current at 100 mV drop, typ | at 100 mV, worst case |
|---|---|---|---|
| `TG_1K_1V8` | 8 mA | 0.0788 mA | 0.000325 mA |
| `TG_100R_1V8` | 80 mA | 1.01 mA | 0.0102 mA |
| `TG_10R_1V8` | 800 mA | 10.2 mA | 0.108 mA |
| `TG_1K_3V3` | 7.36 mA | 0.0917 mA | 0.0423 mA |
| `TG_100R_3V3` | 73.6 mA | 0.988 mA | 0.484 mA |
| `TG_10R_3V3` | 736 mA | 9.95 mA | 4.88 mA |
| `TG_1K_5V0` | 10.08 mA | 0.0962 mA | 0.0464 mA |
| `TG_100R_5V0` | 100.8 mA | 1 mA | 0.485 mA |
| `TG_10R_5V0` | 1008 mA | 10 mA | 4.87 mA |

The device rating is never the binding constraint at these sizes: reaching it
would put volts across the switch.

## 9. What the low-resistance classes cost

| cell | terminal C, off | terminal C, on | worst-case injected charge | inverter delay |
|---|---|---|---|---|
| `TG_1K_1V8` | 16.68 fF | 21.36 fF | +0.009 pC at 1.62 V | 0.10 / 0.11 ns |
| `TG_100R_1V8` | 165.4 fF | 216.4 fF | +0.088 pC at 1.62 V | 0.09 / 0.10 ns |
| `TG_10R_1V8` | 1653 fF | 2164 fF | +0.856 pC at 1.62 V | 0.08 / 0.10 ns |
| `TG_1K_3V3` | 16.01 fF | 24.77 fF | +0.024 pC at 2.97 V | 0.15 / 0.19 ns |
| `TG_100R_3V3` | 158.9 fF | 247.1 fF | +0.245 pC at 2.97 V | 0.13 / 0.17 ns |
| `TG_10R_3V3` | 1588 fF | 2471 fF | +2.259 pC at 2.97 V | 0.11 / 0.17 ns |
| `TG_1K_5V0` | 24.67 fF | 37.86 fF | +0.063 pC at 4.50 V | 0.27 / 0.31 ns |
| `TG_100R_5V0` | 245.7 fF | 377.9 fF | +0.629 pC at 4.50 V | 0.20 / 0.28 ns |
| `TG_10R_5V0` | 2456 fF | 3779 fF | +5.435 pC at 4.50 V | 0.18 / 0.27 ns |

All three scale as the width does, so the choice of class is a straight trade
of resistance against node loading and injected charge. Injection is worst near
the positive rail, where the PMOS carries the channel charge and the NMOS
contributes nothing to cancel it. The inverter delay is the skew between the
two pass devices; it is well under a nanosecond in every cell, and a switch
that is briefly half-open during that window is harmless.

## 10. Verification

All 18 cells were instantiated from `cells.lib` and re-measured. The `TGB`
cells were checked twice, with the bodies strapped to the rails and to the
signal node. All 27 checks reproduce the device-level characterization to
better than 0.01 %, which is the cross-check that the generator emitted the
geometry that was actually characterized. Symbols pass the repository pin-grid
guard.

Reproduce with:

```bash
cd circuits/transmission_gates
python 01_ron_vs_level.py && python 02_ratio.py && python 03_size_ladder.py
python 04_pvt.py && python 05_limits.py
python gen_cells.py && python 06_verify.py && python report.py
bash ../../xschem/gen_tg_syms.sh     # the 18 Xschem symbols
```

## 11. Caveats

- **−55 °C is outside the model's stated window.** `device_limits.csv` gives
  `Tj_max` as −40 to +150 °C and the library header declares a −40 to +150 °C
  qualification range. The −55 °C column is an extrapolation. It roughly doubles
  the 1.8 V dead-zone resistance relative to −40 °C, so it matters. The
  repository's delay-cell characterization already runs at −55 °C, so this
  follows existing practice rather than setting it.
- **±10 % on the 3.3 V rail exceeds a device rating.** 3.63 V is above the
  `Vgs_dcmax` of 3.6 V for NMOS33/PMOS33 by 30 mV, and `en` sits at the rail.
  The 5 V case lands exactly on its 5.5 V rating. The 1.8 V case has margin.
- **`TGB` body pins are not protected.** Driving `bn` above either switch
  terminal, or `bp` below either, forward-biases a body junction. Nothing in
  the cell prevents it.
- **Narrow-width threshold behaviour is uncalibrated** (§7).
- The bodies-at-the-signal configuration assumes an isolated well per switch.
  Whether that is available is a layout question this characterization does not
  answer.

