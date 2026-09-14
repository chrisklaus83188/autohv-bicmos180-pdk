# transmission_gates/ — AutoHV CMOS analog-switch symbols

18 symbols and 18 implementation schematics for
`circuits/transmission_gates/cells.lib` (3 impedance classes × 3 supply domains
× 2 body options).

- Symbols: `bash xschem/gen_tg_syms.sh`
- Schematics and the `.lib` bodies: `python circuits/transmission_gates/gen_cells.py`

| prefix | bodies | ports |
|---|---|---|
| **TG** | tied to the rails: NMOS to `gnd`, PMOS to `vdd` | `a b en vdd gnd` |
| **TGB** | brought out on pins `bn` / `bp` | `a b en bn bp vdd gnd` |

| class | typical Ron | 1V8 total width | 3V3 | 5V0 |
|---|---|---|---|---|
| **1K** | ~1 kΩ | 14 µm | 16.1 µm | 29.4 µm |
| **100R** | ~100 Ω | 140 µm | 161 µm | 294 µm |
| **10R** | ~10 Ω | 1400 µm | 1610 µm | 2940 µm |

Typical is at TT, nominal supply, 27 °C, and is the worst case over the input
level, not the best. Full PVT envelope, the guaranteed input window per cell,
charge injection and terminal capacitance are in
[`circuits/transmission_gates/REPORT.md`](../../circuits/transmission_gates/REPORT.md).

## The symbol

The classic transmission-gate glyph: a bow-tie body between switch terminals
`a` (left) and `b` (right), `en` on top driving the upper gate bar. `TGB` adds
the body pins `bn` and `bp` below. The class and supply are printed above the
body, for example `100 ohm @ 3.3V`.

## Only `en` is driven

Each cell contains its own inverter, so the PMOS gate drive is made inside. The
bubble on the lower gate bar in the symbol is that inverter. Skew between the
two pass devices is the inverter delay, under 0.32 ns in every cell.

## Power is connected BY TEXT (no wires/pins)

Following the `delay_pulse`, `logic` and `comparators` convention: the signal
terminals `a` and `b`, the control `en`, and on `TGB` the two body pins are the
only pins. Supply and ground are the net-name properties `VPWR` (default
**vdd**) and `VGND` (default **0**), shown as text on the symbol. A placed `TG`
netlists as

```
xU1 sig1 sig2 sel vdd 0 TG_100R_3V3
```

Drive net `vdd` once; ground `0` is automatic.

## Using them

1. Place a cell (`Insert -> transmission_gates/<CELL>`) and wire `a`, `b`, `en`.
2. Drop **`autohv_lib`** (PDK models + corner selector) and **`tg_lib`**
   (includes `circuits/transmission_gates/cells.lib`, adds `.global vdd`).
3. Drive `vdd`. On a `TGB` cell, also drive `bn` and `bp` — they are not
   defaulted, and an undriven body pin leaves the pass device's well floating.

## Two things to know before you place one

- **1.8 V rail-tied gates have a dead zone.** At the slow corner with the rail
  10 % low and the die cold, `TG_*_1V8` rises to roughly 99× its typical
  resistance around mid-rail. Use the `TGB` cell with the bodies driven from the
  signal node, or restrict the guaranteed signal range. The 3.3 V and 5 V
  families hold 2.1× and need no such caveat.
- **`bn` must never sit above, and `bp` never below, either switch terminal.**
  Nothing in the cell prevents forward-biasing a body junction.

## The `.sch` files

The schematics are the drawn implementation and carry the same devices and
geometry as the library, but `cells.lib` is the netlist authority. They expose
only the signal pins, with `vdd` and `gnd` as named nets, so they agree with the
symbols' pin list. They are generated; do not hand-edit them.
