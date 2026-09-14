# Transmission gates — summary

18 CMOS analog-switch cells for the AutoHV BiCMOS 180 PDK. Full method, data and
caveats in [REPORT.md](REPORT.md).

## Pick a cell

`TG_<class>_<domain>` — bodies tied to the rails, ports `a b en vdd gnd`.
`TGB_<class>_<domain>` — bodies on pins, ports `a b en bn bp vdd gnd`.
Class is `1K`, `100R` or `10R`; domain is `1V8`, `3V3` or `5V0`. Only `en` is
driven; each cell makes its own complement.

| | Ron typ | Ron max over PVT | total width | terminal C off | worst injected charge |
|---|---|---|---|---|---|
| `TG_1K_3V3` | 1090 Ω | 2364 Ω | 16.1 µm | 16 fF | 0.02 pC |
| `TG_100R_3V3` | 101 Ω | 207 Ω | 161 µm | 159 fF | 0.25 pC |
| `TG_10R_3V3` | 10.1 Ω | 20.5 Ω | 1610 µm | 1.59 pF | 2.26 pC |
| `TG_1K_5V0` | 1039 Ω | 2156 Ω | 29.4 µm | 25 fF | 0.06 pC |
| `TG_100R_5V0` | 99.9 Ω | 206 Ω | 294 µm | 246 fF | 0.63 pC |
| `TG_10R_5V0` | 9.96 Ω | 20.6 Ω | 2940 µm | 2.46 pF | 5.44 pC |

Typical is TT, nominal supply, 27 °C, and is the worst case over input level.
Max is over five corners, supply ±10 %, −55 to +150 °C, and every input level.
The 1.8 V rows are deliberately left out of this table — see below.

## Three things that shape the design

1. **Wp/Wn = 2.5, family-wide.** Sweeping the split at fixed total width put the
   optimum between 2.0 and 3.0 in every domain, independent of width, with a
   shallow minimum. One ratio costs under 2 % anywhere.
2. **`Ron × Wtot` is constant above roughly 50 µm of width.** So sizing is one
   number per domain: 1.386e4, 1.624e4 and 2.939e4 Ω·µm at 1.8, 3.3 and 5 V with
   the bodies on the rails. Putting the bodies on the signal node instead buys
   1.4× at 5 V and 1.96× at 1.8 V.
3. **Class is a trade of resistance against charge.** Resistance, terminal
   capacitance and injected charge all scale with width, so a decade of Ron costs
   a decade of both.

## Read this before using a 1.8 V cell

At the slow corner with the rail 10 % low and the die at −55 °C, `TG_*_1V8`
rises to about 99× its typical resistance near mid-rail. Both devices are
marginal at once and the gate very nearly opens. Supply droop is the dominant
term: the same cold slow corner at the nominal 1.8 V rail costs only 9×.

Use `TGB_100R_1V8` or `TGB_10R_1V8` with the bodies driven from the signal node,
which recovers the full input range, or restrict the guaranteed signal window to
the bands in REPORT.md §6. The 3.3 V and 5 V families need neither.

## Reproduce

```bash
cd circuits/transmission_gates
python 01_ron_vs_level.py && python 02_ratio.py && python 03_size_ladder.py
python 04_pvt.py && python 05_limits.py
python gen_cells.py && python 06_verify.py && python report.py
bash ../../xschem/gen_tg_syms.sh
ngspice -b smoke.cir
```

`gen_cells.py` writes `cells/*.lib`, `cells.lib`, and the 18 schematics under
`xschem/transmission_gates/`. `xschem/gen_tg_syms.sh` writes the 18 symbols,
following the repository pattern of keeping symbol generators under `xschem/`.
Everything else only reads.
