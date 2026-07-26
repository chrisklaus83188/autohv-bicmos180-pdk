# Edge-Asymmetric Delay & Pulse-Generator Cell Family
### AutoHV BiCMOS 180 PDK | 4 edge-asymmetric archetypes x 3 domains = 12 cells, plus a two-sided DLY variant (+3)

<sub>Models: **v2-grounded** (frozen) · simulator: **ngspice-45** · 20 ns nominal target · 45-pt PVT + 200-run MC.</sub>

A compact cell set that delays one input edge while passing the other through, plus two single-shot pulse generators built on the same delay core. Every cell is sized for a **20 ns** delay / pulse width at the nominal corner and characterized across the full PVT matrix in ngspice.

## 1. Cells

| Cell | Function | Output idle | Delayed/timed edge | Passthrough edge |
|---|---|---|---|---|
| `DLYR_<D>` | rising-edge **delay**, falling-edge passthrough (non-inverting) | follows in | rising | falling |
| `DLYF_<D>` | falling-edge **delay**, rising-edge passthrough (non-inverting) | follows in | falling | rising |
| `PHI_<D>`  | logic-**HIGH pulse** on rising edge, falling-edge passthrough | low | rising -> 20 ns high pulse | falling (stays low) |
| `PLO_<D>`  | logic-**LOW pulse** on falling edge, rising-edge passthrough | high | falling -> 20 ns low pulse | rising (stays high) |
| `DLY_<D>`  | two-sided **delay**: BOTH edges RC-delayed (non-inverting) | follows in | rising + falling | none (see section 5) |

`<D>` = `1V8` / `3V3` / `5V0`.  Port order (all cells): `in out vdd gnd`.

## 2. Architecture

All four archetypes share one delay core:

```
  in --[inv]--> nIN --[ R(poly) ]--+--> nC --[ 6T Schmitt ]--> (delayed)
                                   |
                              [ C(MIM) ]      + 1 bypass FET on nC
```
- **Time constant**: a high-sheet poly resistor `RPOLY_HI` (1200 ohm/sq) charges a high-density MIM cap `CMIM_HI` (2 fF/um^2). The delay to a mid-rail Schmitt trip is `~ln(Vdd/Vtrip)*R*C`, which is **supply-independent**, so the same R,C land ~20 ns in all three domains.
- **Schmitt trigger** (6 transistors) restores a clean, fast output edge from the slow RC ramp and adds noise immunity / hysteresis.
- **Asymmetric edge**: a single bypass FET across `nC` makes the non-delayed edge fast. `DLYR`/`PHI` use a pull-up PMOS (fast falling out); `DLYF`/`PLO` use a pull-down NMOS (fast rising out).
- **Pulse generators**: `PHI = in AND NOT(DLYR(in))`, `PLO = in OR NOT(DLYF(in))`. The delay core sets the pulse width; the AND/OR gate makes the opposite edge a clean passthrough.

## 3. Minimum-area sizing

For a fixed RC the total `area(R)+area(C)` is minimized when the two areas are equal (`area(R) = L_R*W_R`, `area(C) = C/cj`). The resistor uses the minimum precision-poly width `W_R = 0.5 um`; the MIM cap uses the densest available dielectric (`CMIM_HI`). The cap geometry is fixed at **5.36 x 5.36 um** (~57 fF) and the resistor length `L_R` is tuned by bisection in ngspice to hit 20 ns at nominal -- which lands `L_R` near the balance point, i.e. at the area minimum.

**Conditions.** Nominal = case=0 (TT), nominal Vdd, 27 C, 5 fF output load (FO1), 20 ps input edge. PVT matrix = 5 corners {TT,FF,SS,FS,SF} x 3 supplies x 3 temperatures {-55, 27, 150 C} = 45 points/cell.

## 4.1  1.8 V domain -- NMOS18/PMOS18, L = 0.18 um, Wn/Wp = 0.3/0.7 um

### Sizing & area
| Cell | L_R (um) | C (LxW um) | R area | C area | dev area | **active (um^2)** | # dev |
|---|---|---|---|---|---|---|---|
| DLYR_1V8 | 51.6 | 5.36x5.36 | 25.8 | 28.7 | 0.81 | **55.3** | 9 |
| DLYF_1V8 | 53.8 | 5.36x5.36 | 26.9 | 28.7 | 0.81 | **56.4** | 9 |
| PHI_1V8 | 53.8 | 5.36x5.36 | 26.9 | 28.7 | 1.53 | **57.1** | 17 |
| PLO_1V8 | 55.9 | 5.36x5.36 | 28.0 | 28.7 | 1.53 | **58.2** | 17 |

### Timing across PVT
| Cell | metric | nominal (ns) | PVT min..max (ns) | worst-case corner | passthrough |
|---|---|---|---|---|---|
| DLYR_1V8 | rise delay | 20.03 | 14.1..28.9 | SS,1.62V,-55C | fast edge <= 2.5 ns |
| DLYF_1V8 | fall delay | 19.78 | 13.7..28.7 | SS,1.62V,-55C | fast edge <= 1.2 ns |
| PHI_1V8 | high-pulse width | 20.09 | 14.2..28.7 | SS,1.62V,-55C | no pulse (idle low) |
| PLO_1V8 | low-pulse width | 19.84 | 13.8..29.0 | SS,1.62V,-55C | no pulse (idle high) |

## 4.2  3.3 V domain -- NMOS33/PMOS33, L = 0.35 um, Wn/Wp = 0.4/0.95 um

### Sizing & area
| Cell | L_R (um) | C (LxW um) | R area | C area | dev area | **active (um^2)** | # dev |
|---|---|---|---|---|---|---|---|
| DLYR_3V3 | 53.8 | 5.36x5.36 | 26.9 | 28.7 | 2.13 | **57.7** | 9 |
| DLYF_3V3 | 55.9 | 5.36x5.36 | 28.0 | 28.7 | 2.13 | **58.8** | 9 |
| PHI_3V3 | 53.8 | 5.36x5.36 | 26.9 | 28.7 | 4.02 | **59.6** | 17 |
| PLO_3V3 | 58.1 | 5.36x5.36 | 29.1 | 28.7 | 4.02 | **61.8** | 17 |

### Timing across PVT
| Cell | metric | nominal (ns) | PVT min..max (ns) | worst-case corner | passthrough |
|---|---|---|---|---|---|
| DLYR_3V3 | rise delay | 19.96 | 15.3..26.2 | SS,2.97V,-55C | fast edge <= 3.4 ns |
| DLYF_3V3 | fall delay | 20.16 | 15.3..26.6 | SS,2.97V,-55C | fast edge <= 1.7 ns |
| PHI_3V3 | high-pulse width | 19.64 | 15.1..25.7 | SS,2.97V,-55C | no pulse (idle low) |
| PLO_3V3 | low-pulse width | 20.38 | 15.4..27.0 | SS,2.97V,-55C | no pulse (idle high) |

## 4.3  5.0 V domain -- NMOS50/PMOS50, L = 0.5 um, Wn/Wp = 0.5/1.15 um

### Sizing & area
| Cell | L_R (um) | C (LxW um) | R area | C area | dev area | **active (um^2)** | # dev |
|---|---|---|---|---|---|---|---|
| DLYR_5V0 | 51.6 | 5.36x5.36 | 25.8 | 28.7 | 3.71 | **58.2** | 9 |
| DLYF_5V0 | 51.6 | 5.36x5.36 | 25.8 | 28.7 | 3.71 | **58.2** | 9 |
| PHI_5V0 | 51.6 | 5.36x5.36 | 25.8 | 28.7 | 7.01 | **61.5** | 17 |
| PLO_5V0 | 53.8 | 5.36x5.36 | 26.9 | 28.7 | 7.01 | **62.6** | 17 |

### Timing across PVT
| Cell | metric | nominal (ns) | PVT min..max (ns) | worst-case corner | passthrough |
|---|---|---|---|---|---|
| DLYR_5V0 | rise delay | 20.29 | 16.3..29.9 | SS,3.2V,-55C | fast edge <= 8.5 ns |
| DLYF_5V0 | fall delay | 20.00 | 16.0..30.1 | SS,3.2V,-55C | fast edge <= 4.7 ns |
| PHI_5V0 | high-pulse width | 20.02 | 16.1..29.2 | SS,3.2V,-55C | no pulse (idle low) |
| PLO_5V0 | low-pulse width | 20.17 | 16.1..30.5 | SS,3.2V,-55C | no pulse (idle high) |

## 5. Two-sided delay cells (DLY)

`DLY_<D>` removes the single bypass FET from the delay core, so **both** edges are RC-delayed instead of one edge being a fast passthrough. It is otherwise identical to `DLYR`/`DLYF` -- same inverter, poly R, MIM cap and 6T Schmitt -- with one fewer transistor. The resistor length is centered between the `DLYR` rise-tuned and `DLYF` fall-tuned values so both edges land near 20 ns at nominal. Non-inverting.

| Cell | L_R (um) | active (um^2) | # dev | rise delay (nom) | fall delay (nom) | rise PVT min..max | fall PVT min..max |
|---|---|---|---|---|---|---|---|
| DLY_1V8 | 52.7 | 55.8 | 8 | 20.1 ns | 19.0 ns | 14.1..29.0 ns | 13.2..27.5 ns |
| DLY_3V3 | 54.8 | 58.0 | 8 | 19.9 ns | 19.2 ns | 15.2..26.1 ns | 14.7..25.3 ns |
| DLY_5V0 | 51.6 | 57.8 | 8 | 19.8 ns | 19.4 ns | 15.9..29.2 ns | 15.6..29.1 ns |

<sub>Both edges are real ~20 ns delays; the small rise-vs-fall offset is the Schmitt trip asymmetry (not removable by resizing R, which scales both edges equally). Full both-edge PVT + 200-run Monte-Carlo statistics are in CHARACTERIZATION.md section 8.</sub>

## 6. Headline numbers

| Metric | 1.8 V | 3.3 V | 5.0 V |
|---|---|---|---|
| Delay-cell active area (um^2) | 55 | 58 | 58 |
| Pulse-cell active area (um^2) | 57 | 60 | 62 |
| Nominal delay/width spread (ns) | 19.8-20.1 | 19.6-20.4 | 20.0-20.3 |
| Full-PVT delay/width spread (ns) | 14-29 | 15-27 | 16-30 |

## 7. Notes & trade-offs

- **Timing target is nominal-only**, as specified. The delay/width is an RC product, so it tracks process (poly Rsh +/-12%, MIM Cj +/-3%), temperature (poly tc1) and the Schmitt trip. Across the full 45-point matrix the timing spans roughly **-31% / +51%** of nominal (slowest = SS, -55C, low Vdd; fastest = FF, 150C). Note the slowest corner is at **-55C**: `RPOLY_HI` tc1 is negative under v2-grounded, so the resistor is highest at cold and this now sets the worst case (it was the hot corner before the tc1 sign-flip). If a PVT-stable delay is needed, a current-reference-biased starved core or a trimmed R can be added at extra area.
- **Area is dominated by the RC** (~57 um^2 of the ~57-62 um^2 active area is the poly resistor + MIM cap; the ~15 transistors add only a few um^2). Resistor and cap areas are balanced (~28-30 um^2 each) at the analytic minimum for a 20 ns RC with W_R = 0.5 um and CMIM_HI.
- **Even smaller area** is possible by trading predictability: replacing the poly resistor with a long-channel starved device shrinks the timing element ~10-20x but widens PVT spread to several-x. The poly+MIM RC was chosen so '20 ns' is a meaningful, repeatable number.
- **Passthrough edge** is fast (sub-ns to ~10 ns depending on domain; the 5 V bypass FET is the slowest because the 5 V devices are slow and must overpower the resistor). It is always far shorter than the 20 ns timed edge, preserving the asymmetry.
- **Pulse cells** return cleanly to their idle rail on the passthrough edge (verified: no spurious pulse) and emit exactly one 20 ns pulse per active edge.
- **Simulation note**: the RC uses the PDK's behavioral-source devices (`RPOLY_HI`/`CMIM_HI` carry B-source voltage-coefficient terms). A single cell sims fine with default trapezoidal integration (used for all characterization here); when several cells share one transient deck, add `.option method=gear maxord=2` to avoid a t=0 timestep collapse (standard ngspice practice for many parallel behavioral RC branches). See `examples/08_delay_pulse_cells_usage.cir`.

## 8. Files
- `dp_lib.py` - deck generators + ngspice driver. `dp_run.py` - sizing & PVT sweep. `dp_char_dly.py` - two-sided DLY characterization. `gen_lib.py` - emits `cells.lib`. `report.py` - this report.
- `cells/<NAME>.lib` - the 15 sized subckts, one file per cell. `cells.lib` - convenience bundle that `.include`s all 15. `results.json` - full numeric results. `decks/` - generated ngspice decks.
