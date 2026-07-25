# Voltage-ramp delay cells — AutoHV BiCMOS180, 5 V domain

A delay cell built from a **PDK current mirror charging a PDK capacitor** to make a
linear voltage ramp, with an NMOS reset switch to restart it. This directory holds
the ramp front-end (12 cells) and its testbenches; the ramp-to-edge detector is a
later stage.

```
        VDD
         |
      [ PMOS current mirror ]      <- sources a controlled I (100nA / 1u / 10u / 100u)
         |
        RAMP  o--------+-------+           RAMP = (I/C)*t  after reset is released
         |        [ CMIM ]  [ NMOS ]-- gate
        GND       [ ~1pF ]  [ reset ]      |
                             |          [ BUF_5V0 ]-- RST   (active-high reset)
                            GND
```

## The twelve cells (`cells/`)

`3 mirror topologies × 4 bias currents`. Port order: **`RST RAMP VDD GND`**
(active-high reset: `RST=1` holds `RAMP` at 0; release to ramp).

| topology | file stem | mirror |
|----------|-----------|--------|
| `DLYRAMP_S_*`  | `dlyramp_s_*`  | simple PMOS mirror |
| `DLYRAMP_CS_*` | `dlyramp_cs_*` | standard diode-stack cascode (recommended: flat I) |
| `DLYRAMP_CW_*` | `dlyramp_cw_*` | wide-swing cascode |

currents: `100n`, `1u`, `10u`, `100u`.

Signal-path devices are **all PDK**: `PMOS50` mirror (L = 2 µm, W per current for
V_ov ≈ 200 mV — Strategy B from `../current_mirror_char/designs.json`), `CMIM_STD`
ramp cap (~1 pF), `NMOS50` reset switch, and `BUF_5V0`
(from `../async_logic_design/cells.lib`). The mirror reference current and the
`MIR_CW` wide-swing cascode bias are ideal sources — bias *instruments*, exactly as
in the current-mirror characterization study.

## Testbenches (`tb/`)

One per current (`tb_100n.cir` … `tb_100u.cir`); each instantiates all three
topologies on a shared `RST` / 5 V supply and runs a transient covering a full
reset → ramp → reset cycle, printing the ramp slope (dV/dt) of each topology.

Run from the `tb/` directory (relative `.include`s resolve from the deck):

```
cd tb && ngspice -b tb_10u.cir
```

As-built ramp slopes at TT / 5 V / 27 °C (dV/dt over the 1→3 V window), **re-measured
against `v2-grounded` (ngspice-45)**. Values in V/µs; the pre-`v2-grounded` numbers are
shown in parentheses for reference:

| bias | ideal I/C | S | CS | CW |
|-----:|----------:|--:|---:|---:|
| 100 nA | 0.10 V/µs | 0.095 (0.100) | 0.092 (0.097) | 0.092 (0.097) |
| 1 µA   | 1.0 V/µs  | 0.942 (1.00)  | 0.914 (0.970) | 0.916 (0.973) |
| 10 µA  | 10 V/µs   | 8.79 (9.64)   | 8.51 (9.34)   | 8.68 (9.54)   |
| 100 µA | 100 V/µs  | 52.7 (70.8)   | 51.3 (69.4)   | 57.3 (80.3)   |

**What moved (re-measure, not re-design):** the mirror sizing (`designs.json`, L = 2 µm,
Strategy B) is unchanged, so this is a re-measure. Every slope dropped ~9 % (low current)
to ~26 % (100 µA) because the F6 BSIM3 junction caps — now non-zero on the `PMOS50` mirror
drain and the `NMOS50` reset-switch drain, both on the `RAMP` node — add ~10 % effective
capacitance, so dV/dt = I/C_eff falls. At 100 µA the ramp span also reaches into the
cascode compliance headroom, so the 1→3 V average slope droops further below I/C — expected,
and a target of the coming detector-stage characterization.

## Two simulation notes (why the decks look the way they do)

1. **`.tran ... uic`** is required. `CMIM_STD` includes a behavioral
   voltage-coefficient branch (`Cextra`); with the simple mirror in the deck, the
   DC-operating-point path into that branch stalls the transient. Starting from
   `uic` (ramp held at 0 by reset) avoids it. The reset hold (`TD`) is kept long
   enough (~100 ns+) for the cascode bias to settle before the ramp is released.
2. **Reset switch W = 100 µm.** The switch must sink the largest bias (100 µA) and
   hold `RAMP` *stably* low (~5 mV). A weaker switch lets the node drift, which
   dithers the `Cextra` branch and stalls the run.

Regenerate everything with `python gen_delay_cells.py`.
