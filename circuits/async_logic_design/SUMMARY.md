# Asynchronous Logic Cell Library - Design Summary
### AutoHV BiCMOS 180 PDK | static CMOS | 8 cells x 3 voltage domains

This library provides eight asynchronous (combinational) logic cells - inverter, buffer, 2-input NAND/NOR/AND/OR, and 2-input XOR/XNOR - implemented in static CMOS in three voltage domains. Every cell is sized for a switching threshold at mid-supply with an input-pin load of <=6.5 fF, and is verified across process, voltage, and temperature.

<sub>Models: **v2-grounded** (frozen) · simulator: **ngspice-45** · input-cap contract **<=6.5 fF hard / 6.0 fF target** (Step-0 decision 1: relaxed from 5.0 fF).</sub>

## 1. Scope and verification conditions

| Item | Value |
|---|---|
| Cells | INV, BUF, NAND2, NOR2, AND2, OR2, XOR2, XNOR2 |
| Domains | 1.8 V (L=0.18 um), 3.3 V (L=0.35 um), 5.0 V (L=0.50 um) |
| Process corners | TT, FF, SS, FS, SF (5) |
| Temperature | -55 C, +27 C, +150 C |
| Supply (1.8/3.3 V) | nominal +/-10%  (1.62/1.80/1.98 ; 2.97/3.30/3.63 V) |
| Supply (5 V) | 3.20 / 5.00 / 5.50 V |
| PVT points / cell | 45 (5 x 3 x 3) |
| Output load (rise/fall) | 5 fF (held constant old-vs-new) |
| Input-cap contract | <=6.5 fF hard / 6.0 fF target |
| Input edge (stimulus) | 20 ps |

**Definitions.** *Switching threshold V_M* = input voltage at which the output reaches 50% of Vdd (DC sweep; 2-input symmetric gates measured inputs-tied; XOR/XNOR swept on one input with the other at each rail). *Rise/fall* = output 10%->90% / 90%->10% of Vdd. *Cin* = average switching capacitance per input pin (rail-averaged, Miller-free). *Area* = (active) sum of W*L, and a first-order standard-cell layout estimate.

## 2. Performance summary by domain
All ranges are min..max **across the full 45-point PVT matrix**. Widths in um.

### 1.8 V domain - NMOS18 / PMOS18, L = 0.18 um

| Cell | Wn/Wp (um) | Cin (fF) | V_M (V) | V_M (%Vdd) | t_rise (ps) | t_fall (ps) | Active (um^2) | Layout est (um^2) |
|---|---|---|---|---|---|---|---|---|
| Inverter | 0.76 / 3.54 | 5.49 | 0.696..1.152 | 43..58% | 21..71 | 35..101 | 0.77 | 2.90 |
| Buffer | 0.76/3.54 -> 2.29/10.62 | 5.49 | 0.703..1.139 | 43..58% | 34..102 | 31..94 | 3.10 | 14.41 |
| NAND2 | 1.87 / 2.44 | 5.49 | 0.698..1.157 | 43..58% | 38..134 | 33..107 | 1.55 | 5.81 |
| NOR2 | 0.22 / 4.08 | 5.51 | 0.699..1.143 | 43..58% | 44..156 | 217..680 | 1.55 | 5.80 |
| AND2 | 1.87/2.44 + 0.76/3.54 | 5.49 | 0.702..1.147 | 43..58% | 28..94 | 41..123 | 2.32 | 10.36 |
| OR2 | 0.22/4.08 + 0.76/3.54 | 5.51 | 0.704..1.133 | 43..57% | 69..192 | 42..132 | 2.32 | 9.52 |
| XOR2 | 0.37/1.87 + 0.37/1.70 | 5.83 | 0.696..1.168 | 43..59% | 94..340 | 186..584 | 2.35 | 11.20 |
| XNOR2 | 0.37/1.87 + 0.37/1.70 | 5.63 | 0.696..1.168 | 43..59% | 94..340 | 186..583 | 2.35 | 11.20 |

<sub>`*` = capacitance-limited (see notes). Wn/Wp for multi-stage cells: BUF = stage1 -> stage2; AND2/OR2 = input gate + output inverter; XOR2/XNOR2 = core + input inverter.</sub>

### 3.3 V domain - NMOS33 / PMOS33, L = 0.35 um

| Cell | Wn/Wp (um) | Cin (fF) | V_M (V) | V_M (%Vdd) | t_rise (ps) | t_fall (ps) | Active (um^2) | Layout est (um^2) |
|---|---|---|---|---|---|---|---|---|
| Inverter | 0.87 / 2.85 | 5.36 | 1.314..2.049 | 44..56% | 48..149 | 60..162 | 1.30 | 4.01 |
| Buffer | 0.87/2.85 -> 2.61/8.55 | 5.36 | 1.323..2.035 | 45..56% | 64..184 | 62..177 | 5.21 | 18.43 |
| NAND2 | 1.91 / 1.83 | 5.38 | 1.324..2.056 | 45..57% | 89..280 | 63..185 | 2.62 | 8.03 |
| NOR2 | 0.30 / 3.59 | 5.64 | 1.320..2.053 | 44..57% | 100..318 | 364..1005 | 2.72 | 8.24 |
| AND2 | 1.91/1.83 + 0.87/2.85 | 5.38 | 1.330..2.046 | 45..56% | 60..188 | 76..216 | 3.92 | 14.19 |
| OR2 | 0.30/3.59 + 0.87/2.85 | 5.64 | 1.327..2.042 | 45..56% | 130..355 | 78..227 | 4.02 | 13.57 |
| XOR2 | 0.40/1.63 + 0.40/1.30 | 5.65 | 1.317..2.153 | 44..59% | 206..670 | 389..1160 | 4.03 | 16.92 |
| XNOR2 | 0.40/1.63 + 0.40/1.30 | 5.64 | 1.317..2.153 | 44..59% | 205..669 | 389..1160 | 4.03 | 16.92 |

<sub>`*` = capacitance-limited (see notes). Wn/Wp for multi-stage cells: BUF = stage1 -> stage2; AND2/OR2 = input gate + output inverter; XOR2/XNOR2 = core + input inverter.</sub>

### 5.0 V domain - NMOS50 / PMOS50, L = 0.50 um

| Cell | Wn/Wp (um) | Cin (fF) | V_M (V) | V_M (%Vdd) | t_rise (ps) | t_fall (ps) | Active (um^2) | Layout est (um^2) |
|---|---|---|---|---|---|---|---|---|
| Inverter | 1.12 / 3.04 | 5.38 | 1.411..3.054 | 44..56% | 89..435 | 106..437 | 2.08 | 6.00 |
| Buffer | 1.12/3.04 -> 3.36/9.13 | 5.38 | 1.416..3.035 | 44..55% | 118..495 | 114..472 | 8.33 | 26.98 |
| NAND2 | 2.29 / 1.88 | 5.40 | 1.410..3.059 | 44..56% | 167..858 | 114..521 | 4.17 | 12.00 |
| NOR2 | 0.40 / 3.83 | 5.50 | 1.426..3.080 | 45..56% | 183..891 | 658..2521 | 4.23 | 12.12 |
| AND2 | 2.29/1.88 + 1.12/3.04 | 5.40 | 1.415..3.045 | 44..55% | 111..538 | 140..592 | 6.25 | 21.16 |
| OR2 | 0.40/3.83 + 1.12/3.04 | 5.50 | 1.434..3.065 | 45..56% | 247..888 | 142..607 | 6.31 | 20.12 |
| XOR2 | 0.53/1.64 + 0.53/1.45 | 5.73 | 1.415..3.169 | 44..58% | 398..2059 | 640..3005 | 6.34 | 25.25 |
| XNOR2 | 0.53/1.64 + 0.53/1.45 | 5.73 | 1.415..3.169 | 44..58% | 397..2058 | 640..3004 | 6.34 | 25.25 |

<sub>`*` = capacitance-limited (see notes). Wn/Wp for multi-stage cells: BUF = stage1 -> stage2; AND2/OR2 = input gate + output inverter; XOR2/XNOR2 = core + input inverter.</sub>

## 3. Headline numbers

| Metric | 1.8 V | 3.3 V | 5.0 V |
|---|---|---|---|
| Fastest edge, INV (t_r min, ps) | 21 | 48 | 89 |
| Slowest edge, any cell (ps) | 680 | 1160 | 3005 |
| Worst input-pin Cin (fF) | 5.83 | 5.65 | 5.73 |
| V_M window across all cells/PVT (%Vdd) | 43-59% | 44-59% | 44-58% |
| Cell area range, INV..XOR (um^2 est) | 2.9-14.4 | 4.0-18.4 | 6.0-27.0 |

## 4. Key results and trade-offs

- **Threshold centering:** V_M holds within ~0.43-0.58 of the instantaneous supply for every cell across all 45 PVT points, and within a few percent of 0.50 Vdd at nominal. Temperature drift of V_M is small (devices sit near the zero-temperature-coefficient bias).
- **Input load:** every input pin is <=6.5 fF (worst case 5.4-5.8 fF). Input-pin cap is a gate load and is essentially unmoved by the F6 junction caps (which load drain/source, not the gate); the 6.5 fF budget (up from 5.0 fF) just lets each cell use proportionally wider devices.
- **No cell is capacitance-limited under the 6.5 fF contract.** Under the old 5.0 fF limit NOR2/OR2 had to back off their series PMOS (V_M off-centre); the relaxed budget lets them reach their ideal P/N ratio and centre V_M.
- **Speed ranking** (fastest to slowest): INV ~ BUF ~ AND2 < NAND2 < OR2 < NOR2 << XOR2 ~ XNOR2. NOR/OR (series PMOS) and especially XOR/XNOR (small cap-budgeted core driving a 2-high stack) are the slow cells - inherent to a light-input-load, mid-supply static design rather than a sizing deficiency. The NOR2/OR2/XOR/XNOR fall edges slowed ~45-60% vs the pre-F6 numbers (junction caps now load the output); simpler cells stay within ~+/-10% as the wider devices the relaxed budget allows offset it.
- **Sizing intuition:** PMOS is wider than NMOS on most cells (Wp/Wn ~ 2.7-4.7 on the inverter) to offset this PDK's lower hole mobility and |Vtp| > Vtn. NAND2 inverts that (wider NMOS) because of its series pull-down; NOR2 is the extreme opposite.
- **Scaling across domains:** moving 1.8 V -> 3.3 V -> 5.0 V, cells grow ~1.4x then ~2x in estimated area (longer L and taller cells) and edges slow ~2x per step at fixed load.

## 5. Deliverables
- `SUMMARY.md` (this file) and `REPORT.md` - methodology + full tables.
- `results.json` - complete numeric results (per-PVT min/max and worst-case conditions).
- `async_lib.py`, `async_run.py`, `report.py` - generators/driver; `decks/` - all ngspice decks.