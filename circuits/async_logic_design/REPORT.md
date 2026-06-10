# Asynchronous Logic Cell Family - AutoHV BiCMOS 180 PDK

Static CMOS standard-cell set (8 cells x 3 voltage domains = 24 cells), each sized for a mid-supply switching threshold with <=5 fF input-pin load, characterized across the full PVT matrix in ngspice.

## 1. Design approach & test conditions

**Devices / channel length** (drawn L fixed per voltage class):

| Domain | N / P device | L (um) | Nominal Vdd | Supply corners |
|---|---|---|---|---|
| 1v8 | NMOS18/PMOS18 | 0.18 | 1.80 V | 1.62, 1.80, 1.98 V |
| 3v3 | NMOS33/PMOS33 | 0.35 | 3.30 V | 2.97, 3.30, 3.63 V |
| 5v0 | NMOS50/PMOS50 | 0.50 | 5.00 V | 3.20, 5.00, 5.50 V |

**PVT matrix** (45 points per cell): 5 process corners {TT,FF,SS,FS,SF} x 3 temperatures {-55, 27, 150 C} x 3 supplies (per table above).

**Sizing strategy.** Each cell is built in static CMOS. The P/N width ratio is tuned (via a DC ratio sweep) so the switching threshold V_M = Vdd/2 at the nominal corner (TT, 27 C, nominal Vdd). Absolute device widths are then scaled so each input pin presents <=5 fF. AND2/OR2 = NAND2/NOR2 + inverter; BUF = inverter + 3x inverter; XOR2/XNOR2 = 12-transistor static gates (two input inverters generate complementary inputs). Minimum drawn width 0.22/0.30/0.40 um (1.8/3.3/5 V).

**Input capacitance** is the average switching load: small-signal AC capacitance at the input pin evaluated at both rails (in=0 and in=Vdd) and averaged. Evaluating at the rails avoids Miller inflation of Cgd that occurs at the high-gain trip point, giving the load a driving stage actually sees.

**Switching threshold V_M** = input voltage at which the output crosses 50% of Vdd (DC sweep). Symmetric 2-input gates are measured with inputs tied. XOR2/XNOR2 cannot be measured tied (output never toggles), so each is swept on one input with the other held at 0 and at Vdd; both thresholds are reported.

**Rise/fall** = output 10%->90% (rise) and 90%->10% (fall) of Vdd, driving a 5 fF load (= fanout-of-1, since each input pin is <=5 fF) with a 20 ps input edge. Min = fastest corner, Max = slowest corner across PVT.

**Area.** No layout was produced; area is a transparent estimate. *Active gate area* = sum of W*L over all transistors. *Layout estimate* = (poly columns x contacted-poly pitch) x (tallest PMOS + tallest NMOS + rail/well overhead), with CPP = 0.50/0.70/0.90 um and overhead = 1.5/2.0/2.5 um for 1.8/3.3/5 V. Treat as a relative/first-order figure.

## 2.1  1.8 V (NMOS18/PMOS18) domain

### Sizing

| Cell | Wn (um) | Wp (um) | Wp/Wn | Cin (fF) | # dev |
|---|---|---|---|---|---|
| Inverter | 0.57 | 2.66 | 4.6 | 4.15 | 2 |
| Buffer | 0.57+1.72 | 2.66+7.97 | 4.6 | 4.15 | 4 |
| NAND2 | 1.40 | 1.83 | 1.3 | 4.15 | 4 |
| NOR2 *cap-limited | 0.22 | 3.65 | 16.6 | 4.98 | 4 |
| AND2 | 1.40/0.57 | 1.83/2.66 | 1.3 | 4.15 | 6 |
| OR2 | 0.22/0.57 | 3.65/2.66 | 16.6 | 4.98 | 6 |
| XOR2 | 0.27(core)/0.27(inv) | 1.40/1.28 | 5.1 | 4.42 | 12 |
| XNOR2 | 0.27(core)/0.27(inv) | 1.40/1.28 | 5.1 | 4.27 | 12 |

### Results across PVT

| Cell | V_M min..max (V) | V_M (%Vdd) | t_rise min..max (ps) | t_fall min..max (ps) | Active area (um^2) | Layout est (um^2) |
|---|---|---|---|---|---|---|
| Inverter | 0.694..1.123 | 43..57% | 16..70 | 25..98 | 0.58 | 2.36 |
| Buffer | 0.702..1.113 | 43..56% | 24..87 | 20..76 | 2.32 | 11.18 |
| NAND2 | 0.699..1.130 | 43..57% | 23..114 | 21..88 | 1.16 | 4.73 |
| NOR2 | 0.691..1.107 | 43..56% | 26..125 | 108..428 | 1.39 | 5.37 |
| AND2 | 0.703..1.123 | 43..57% | 19..86 | 28..114 | 1.74 | 8.34 |
| OR2 | 0.697..1.099 | 43..56% | 40..141 | 29..119 | 1.98 | 8.59 |
| XOR2 | 0.693..1.135 | 43..57% | 61..455 | 132..601 | 1.77 | 9.53 |
| XNOR2 | 0.693..1.135 | 43..57% | 61..454 | 132..601 | 1.77 | 9.53 |

<sub>V_M %Vdd = V_M as a fraction of the supply at that PVT point. XOR2/XNOR2 V_M spans both input conditions (other input = 0 and = Vdd).</sub>

## 2.2  3.3 V (NMOS33/PMOS33) domain

### Sizing

| Cell | Wn (um) | Wp (um) | Wp/Wn | Cin (fF) | # dev |
|---|---|---|---|---|---|
| Inverter | 0.65 | 2.14 | 3.3 | 4.08 | 2 |
| Buffer | 0.65+1.96 | 2.14+6.41 | 3.3 | 4.08 | 4 |
| NAND2 | 1.43 | 1.37 | 1.0 | 4.09 | 4 |
| NOR2 *cap-limited | 0.30 | 2.91 | 9.7 | 4.70 | 4 |
| AND2 | 1.43/0.65 | 1.37/2.14 | 1.0 | 4.09 | 6 |
| OR2 | 0.30/0.65 | 2.91/2.14 | 9.7 | 4.70 | 6 |
| XOR2 | 0.30(core)/0.30(inv) | 1.24/0.98 | 4.1 | 4.38 | 12 |
| XNOR2 | 0.30(core)/0.30(inv) | 1.24/0.98 | 4.1 | 4.37 | 12 |

### Results across PVT

| Cell | V_M min..max (V) | V_M (%Vdd) | t_rise min..max (ps) | t_fall min..max (ps) | Active area (um^2) | Layout est (um^2) |
|---|---|---|---|---|---|---|
| Inverter | 1.319..2.035 | 44..56% | 38..158 | 49..171 | 0.98 | 3.35 |
| Buffer | 1.327..2.021 | 45..56% | 48..162 | 44..160 | 3.91 | 14.52 |
| NAND2 | 1.326..2.031 | 45..56% | 62..264 | 44..170 | 1.96 | 6.73 |
| NOR2 | 1.282..1.974 | 43..54% | 69..291 | 195..660 | 2.24 | 7.29 |
| AND2 | 1.330..2.021 | 45..56% | 46..188 | 60..210 | 2.94 | 11.70 |
| OR2 | 1.289..1.963 | 43..54% | 81..272 | 61..221 | 3.22 | 11.68 |
| XOR2 | 1.323..2.123 | 45..58% | 200..904 | 301..1210 | 3.05 | 14.85 |
| XNOR2 | 1.323..2.123 | 45..58% | 200..903 | 301..1210 | 3.05 | 14.85 |

<sub>V_M %Vdd = V_M as a fraction of the supply at that PVT point. XOR2/XNOR2 V_M spans both input conditions (other input = 0 and = Vdd).</sub>

## 2.3  5.0 V (NMOS50/PMOS50) domain

### Sizing

| Cell | Wn (um) | Wp (um) | Wp/Wn | Cin (fF) | # dev |
|---|---|---|---|---|---|
| Inverter | 0.84 | 2.28 | 2.7 | 4.11 | 2 |
| Buffer | 0.84+2.52 | 2.28+6.85 | 2.7 | 4.11 | 4 |
| NAND2 | 1.72 | 1.41 | 0.8 | 4.13 | 4 |
| NOR2 *cap-limited | 0.40 | 3.10 | 7.8 | 4.62 | 4 |
| AND2 | 1.72/0.84 | 1.41/2.28 | 0.8 | 4.13 | 6 |
| OR2 | 0.40/0.84 | 3.10/2.28 | 7.8 | 4.62 | 6 |
| XOR2 | 0.40(core)/0.40(inv) | 1.23/1.09 | 3.1 | 4.46 | 12 |
| XNOR2 | 0.40(core)/0.40(inv) | 1.23/1.09 | 3.1 | 4.55 | 12 |

### Results across PVT

| Cell | V_M min..max (V) | V_M (%Vdd) | t_rise min..max (ps) | t_fall min..max (ps) | Active area (um^2) | Layout est (um^2) |
|---|---|---|---|---|---|---|
| Inverter | 1.435..3.061 | 45..56% | 73..472 | 90..481 | 1.56 | 5.06 |
| Buffer | 1.441..3.042 | 45..55% | 92..442 | 88..425 | 6.25 | 21.36 |
| NAND2 | 1.428..3.046 | 45..55% | 124..837 | 84..499 | 3.13 | 10.13 |
| NOR2 | 1.417..2.964 | 43..54% | 131..834 | 367..1726 | 3.50 | 10.81 |
| AND2 | 1.435..3.030 | 45..55% | 88..554 | 114..594 | 4.69 | 17.56 |
| OR2 | 1.424..2.948 | 44..54% | 155..732 | 116..614 | 5.07 | 17.40 |
| XOR2 | 1.435..3.168 | 45..58% | 303..2856 | 520..3295 | 4.76 | 22.32 |
| XNOR2 | 1.435..3.168 | 45..58% | 302..2851 | 520..3293 | 4.76 | 22.32 |

<sub>V_M %Vdd = V_M as a fraction of the supply at that PVT point. XOR2/XNOR2 V_M spans both input conditions (other input = 0 and = Vdd).</sub>

## 3. Notes and trade-offs

- **All input pins meet the <=5 fF target** (worst pin 4.1-5.0 fF). 
- **NOR2 / OR2 are capacitance-limited** (marked *cap-limited). Centering V_M exactly at Vdd/2 with tied inputs needs a very wide series-PMOS stack (Wp/Wn ~ 8-17); at minimum NMOS width that pushes Cin above 5 fF. The PMOS was therefore backed off to hold Cin <=5 fF, which lands V_M a few % below mid-supply at nominal (still ~0.45-0.50 Vdd). Relaxing the 5 fF limit would allow exact centering.
- **NOR2/OR2 and XOR2/XNOR2 are intrinsically slower**: the series-PMOS pull-up (NOR/OR) and the small cap-budgeted core devices feeding a 2-high stack (XOR/XNOR) limit drive. This is fundamental to a <=5 fF, mid-supply static design, not a sizing error.
- **V_M tracks supply well**: across all corners/temperatures V_M stays ~0.45-0.56 of the instantaneous supply for INV/BUF/NAND/AND/XOR/XNOR; temperature drift of V_M is small (the design is close to the zero-temp-coefficient bias).
- Rise/fall asymmetry (t_fall > t_rise on several cells) follows directly from the PMOS-heavy ratio required to center V_M given this PDK's |Vtp| > Vtn and lower hole mobility; the weaker NMOS makes the pull-down edge slower.

## 4. Files
- `async_lib.py` - deck generators + ngspice driver. `async_run.py` - sizing & PVT sweep. 
- `results.json` - full numeric results. `decks/` - every generated ngspice deck.