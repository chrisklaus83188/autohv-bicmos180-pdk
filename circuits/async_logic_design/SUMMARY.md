# Asynchronous Logic Cell Library - Design Summary
### AutoHV BiCMOS 180 PDK | static CMOS | 8 cells x 3 voltage domains

This library provides eight asynchronous (combinational) logic cells - inverter, buffer, 2-input NAND/NOR/AND/OR, and 2-input XOR/XNOR - implemented in static CMOS in three voltage domains. Every cell is sized for a switching threshold at mid-supply with an input-pin load of <=5 fF, and is verified across process, voltage, and temperature.

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
| Output load (rise/fall) | 5 fF (fanout-of-1) |
| Input edge (stimulus) | 20 ps |

**Definitions.** *Switching threshold V_M* = input voltage at which the output reaches 50% of Vdd (DC sweep; 2-input symmetric gates measured inputs-tied; XOR/XNOR swept on one input with the other at each rail). *Rise/fall* = output 10%->90% / 90%->10% of Vdd. *Cin* = average switching capacitance per input pin (rail-averaged, Miller-free). *Area* = (active) sum of W*L, and a first-order standard-cell layout estimate.

## 2. Performance summary by domain
All ranges are min..max **across the full 45-point PVT matrix**. Widths in um.

### 1.8 V domain - NMOS18 / PMOS18, L = 0.18 um

| Cell | Wn/Wp (um) | Cin (fF) | V_M (V) | V_M (%Vdd) | t_rise (ps) | t_fall (ps) | Active (um^2) | Layout est (um^2) |
|---|---|---|---|---|---|---|---|---|
| Inverter | 0.57 / 2.66 | 4.15 | 0.694..1.123 | 43..57% | 16..70 | 25..98 | 0.58 | 2.36 |
| Buffer | 0.57/2.66 -> 1.72/7.97 | 4.15 | 0.702..1.113 | 43..56% | 24..87 | 20..76 | 2.32 | 11.18 |
| NAND2 | 1.40 / 1.83 | 4.15 | 0.699..1.130 | 43..57% | 23..114 | 21..88 | 1.16 | 4.73 |
| NOR2* | 0.22 / 3.65 | 4.98 | 0.691..1.107 | 43..56% | 26..125 | 108..428 | 1.39 | 5.37 |
| AND2 | 1.40/1.83 + 0.57/2.66 | 4.15 | 0.703..1.123 | 43..57% | 19..86 | 28..114 | 1.74 | 8.34 |
| OR2 | 0.22/3.65 + 0.57/2.66 | 4.98 | 0.697..1.099 | 43..56% | 40..141 | 29..119 | 1.98 | 8.59 |
| XOR2 | 0.27/1.40 + 0.27/1.28 | 4.42 | 0.693..1.135 | 43..57% | 61..455 | 132..601 | 1.77 | 9.53 |
| XNOR2 | 0.27/1.40 + 0.27/1.28 | 4.27 | 0.693..1.135 | 43..57% | 61..454 | 132..601 | 1.77 | 9.53 |

<sub>`*` = capacitance-limited (see notes). Wn/Wp for multi-stage cells: BUF = stage1 -> stage2; AND2/OR2 = input gate + output inverter; XOR2/XNOR2 = core + input inverter.</sub>

### 3.3 V domain - NMOS33 / PMOS33, L = 0.35 um

| Cell | Wn/Wp (um) | Cin (fF) | V_M (V) | V_M (%Vdd) | t_rise (ps) | t_fall (ps) | Active (um^2) | Layout est (um^2) |
|---|---|---|---|---|---|---|---|---|
| Inverter | 0.65 / 2.14 | 4.08 | 1.319..2.035 | 44..56% | 38..158 | 49..171 | 0.98 | 3.35 |
| Buffer | 0.65/2.14 -> 1.96/6.41 | 4.08 | 1.327..2.021 | 45..56% | 48..162 | 44..160 | 3.91 | 14.52 |
| NAND2 | 1.43 / 1.37 | 4.09 | 1.326..2.031 | 45..56% | 62..264 | 44..170 | 1.96 | 6.73 |
| NOR2* | 0.30 / 2.91 | 4.70 | 1.282..1.974 | 43..54% | 69..291 | 195..660 | 2.24 | 7.29 |
| AND2 | 1.43/1.37 + 0.65/2.14 | 4.09 | 1.330..2.021 | 45..56% | 46..188 | 60..210 | 2.94 | 11.70 |
| OR2 | 0.30/2.91 + 0.65/2.14 | 4.70 | 1.289..1.963 | 43..54% | 81..272 | 61..221 | 3.22 | 11.68 |
| XOR2 | 0.30/1.24 + 0.30/0.98 | 4.38 | 1.323..2.123 | 45..58% | 200..904 | 301..1210 | 3.05 | 14.85 |
| XNOR2 | 0.30/1.24 + 0.30/0.98 | 4.37 | 1.323..2.123 | 45..58% | 200..903 | 301..1210 | 3.05 | 14.85 |

<sub>`*` = capacitance-limited (see notes). Wn/Wp for multi-stage cells: BUF = stage1 -> stage2; AND2/OR2 = input gate + output inverter; XOR2/XNOR2 = core + input inverter.</sub>

### 5.0 V domain - NMOS50 / PMOS50, L = 0.50 um

| Cell | Wn/Wp (um) | Cin (fF) | V_M (V) | V_M (%Vdd) | t_rise (ps) | t_fall (ps) | Active (um^2) | Layout est (um^2) |
|---|---|---|---|---|---|---|---|---|
| Inverter | 0.84 / 2.28 | 4.11 | 1.435..3.061 | 45..56% | 73..472 | 90..481 | 1.56 | 5.06 |
| Buffer | 0.84/2.28 -> 2.52/6.85 | 4.11 | 1.441..3.042 | 45..55% | 92..442 | 88..425 | 6.25 | 21.36 |
| NAND2 | 1.72 / 1.41 | 4.13 | 1.428..3.046 | 45..55% | 124..837 | 84..499 | 3.13 | 10.13 |
| NOR2* | 0.40 / 3.10 | 4.62 | 1.417..2.964 | 43..54% | 131..834 | 367..1726 | 3.50 | 10.81 |
| AND2 | 1.72/1.41 + 0.84/2.28 | 4.13 | 1.435..3.030 | 45..55% | 88..554 | 114..594 | 4.69 | 17.56 |
| OR2 | 0.40/3.10 + 0.84/2.28 | 4.62 | 1.424..2.948 | 44..54% | 155..732 | 116..614 | 5.07 | 17.40 |
| XOR2 | 0.40/1.23 + 0.40/1.09 | 4.46 | 1.435..3.168 | 45..58% | 303..2856 | 520..3295 | 4.76 | 22.32 |
| XNOR2 | 0.40/1.23 + 0.40/1.09 | 4.55 | 1.435..3.168 | 45..58% | 302..2851 | 520..3293 | 4.76 | 22.32 |

<sub>`*` = capacitance-limited (see notes). Wn/Wp for multi-stage cells: BUF = stage1 -> stage2; AND2/OR2 = input gate + output inverter; XOR2/XNOR2 = core + input inverter.</sub>

## 3. Headline numbers

| Metric | 1.8 V | 3.3 V | 5.0 V |
|---|---|---|---|
| Fastest edge, INV (t_r min, ps) | 16 | 38 | 73 |
| Slowest edge, any cell (ps) | 601 | 1210 | 3295 |
| Worst input-pin Cin (fF) | 4.98 | 4.70 | 4.62 |
| V_M window across all cells/PVT (%Vdd) | 43-57% | 43-58% | 43-58% |
| Cell area range, INV..XOR (um^2 est) | 2.4-11.2 | 3.4-14.9 | 5.1-22.3 |

## 4. Key results and trade-offs

- **Threshold centering:** V_M holds within ~0.43-0.58 of the instantaneous supply for every cell across all 45 PVT points, and within a few percent of 0.50 Vdd at nominal. Temperature drift of V_M is small (devices sit near the zero-temperature-coefficient bias).
- **Input load:** every input pin is <=5 fF (worst case 4.1-5.0 fF), as specified.
- **NOR2 / OR2 are capacitance-limited (`*`).** Centering V_M with tied inputs needs a wide series-PMOS stack (Wp/Wn ~ 8-17). At minimum NMOS width that would exceed 5 fF, so the PMOS is held back to keep Cin <=5 fF; V_M then sits slightly below mid-supply (~0.45-0.50 Vdd). Relaxing the 5 fF limit would allow exact centering.
- **Speed ranking** (fastest to slowest, by drive into 5 fF): INV ~ BUF ~ AND2 < NAND2 < OR2 < NOR2 << XOR2 ~ XNOR2. NOR/OR (series PMOS) and especially XOR/XNOR (small cap-budgeted core driving a 2-high stack) are the slow cells - inherent to a <=5 fF, mid-supply static design rather than a sizing deficiency.
- **Sizing intuition:** PMOS is wider than NMOS on most cells (Wp/Wn ~ 2.7-4.7 on the inverter) to offset this PDK's lower hole mobility and |Vtp| > Vtn. NAND2 inverts that (wider NMOS) because of its series pull-down; NOR2 is the extreme opposite.
- **Scaling across domains:** moving 1.8 V -> 3.3 V -> 5.0 V, cells grow ~1.4x then ~2x in estimated area (longer L and taller cells) and edges slow ~2x per step at fixed load.

## 5. Deliverables
- `SUMMARY.md` (this file) and `REPORT.md` - methodology + full tables.
- `results.json` - complete numeric results (per-PVT min/max and worst-case conditions).
- `async_lib.py`, `async_run.py`, `report.py` - generators/driver; `decks/` - all ngspice decks.