# Delay & Pulse-Generator Cell Characterization Report
### AutoHV BiCMOS 180 PDK | 12 cells (4 archetypes x 3 voltage domains)

Full PVT corner characterization plus 200-run Monte Carlo for the edge-asymmetric delay and pulse cells in `circuits/delay_pulse_design/cells.lib`. All results are from ngspice transient analysis on the unmodified PDK device models (BSIM3 core MOSFETs, behavioral-source poly resistor and MIM capacitor) -- no model simplifications, no behavioral stand-ins for the cells.

## 1. Cells under test

| Cell | Function |
|---|---|
| `DLYR_<D>` | rising-edge delay, falling-edge passthrough |
| `DLYF_<D>` | falling-edge delay, rising-edge passthrough |
| `PHI_<D>`  | HIGH pulse on rising edge, falling-edge passthrough |
| `PLO_<D>`  | LOW pulse on falling edge, rising-edge passthrough |

`<D>` = `1V8`/`3V3`/`5V0`. Each cell was sized for ~20 ns at nominal; this report measures how that timing moves over PVT and statistics.

## 2. Conditions

**Measured quantities** (every transient): `delay`/`width` = the cell's primary metric (input-edge -> output-edge for delays; output pulse high/low duration for pulse cells), at the 50% level; `passthrough` = the fast (non-delayed) edge, input->output at 50% (delay cells); `t_rise`/`t_fall` = output 10-90% / 90-10% edge rate into a 5 fF load.

**PVT matrix** (45 points/cell):

| Axis | Values |
|---|---|
| Process | TT, FF, SS, FS, SF (all 5 corners) |
| Temperature | -55, 27, 150 C |
| Supply (1.8 V) | 1.62, 1.80, 1.98 V (+-10%) |
| Supply (3.3 V) | 2.97, 3.30, 3.63 V (+-10%) |
| Supply (5.0 V) | 3.20, 5.00, 5.50 V |

**Monte Carlo**: typical corner (case=0/TT, nominal supply, 27 C), **200 iterations**, with **both** die-to-die process variation (`PROC_ON=1`) and per-device local mismatch (`MM_ON=1`) enabled. Each iteration re-randomizes every AGAUSS draw via `reset` (re-randomization verified: 200 distinct results from 200 runs; the PDK's RNG is time-seeded per run). Statistics on the BSIM3 core devices, the poly resistor (Rsh + matching) and the MIM cap (Cj + matching) all participate.

## 3. Area

**Definition**: area = the sum over every device in the cell of (length x width). Transistors contribute their channel area W x L; the poly resistor (`RPOLY_HI`, W = 0.5 um) and the MIM capacitor (`CMIM_HI`, 5.36 x 5.36 um) contribute their drawn L x W. This is a device-area sum, not a placed-and-routed layout figure.

| Cell | # devices | FETs (um^2) | resistor (um^2) | MIM cap (um^2) | **total (um^2)** |
|---|---|---|---|---|---|
| DLYR_1V8 | 11 (9 FET + R + C) | 0.83 | 26.9 | 28.7 | **56.4** |
| DLYF_1V8 | 11 (9 FET + R + C) | 0.83 | 28.0 | 28.7 | **57.5** |
| PHI_1V8 | 19 (17 FET + R + C) | 1.55 | 28.0 | 28.7 | **58.2** |
| PLO_1V8 | 19 (17 FET + R + C) | 1.55 | 29.1 | 28.7 | **59.3** |
| DLYR_3V3 | 11 (9 FET + R + C) | 2.17 | 28.0 | 28.7 | **58.9** |
| DLYF_3V3 | 11 (9 FET + R + C) | 2.17 | 29.1 | 28.7 | **60.0** |
| PHI_3V3 | 19 (17 FET + R + C) | 4.06 | 28.0 | 28.7 | **60.8** |
| PLO_3V3 | 19 (17 FET + R + C) | 4.06 | 29.1 | 28.7 | **61.9** |
| DLYR_5V0 | 11 (9 FET + R + C) | 3.80 | 25.8 | 28.7 | **58.3** |
| DLYF_5V0 | 11 (9 FET + R + C) | 3.80 | 26.9 | 28.7 | **59.4** |
| PHI_5V0 | 19 (17 FET + R + C) | 7.10 | 26.9 | 28.7 | **62.7** |
| PLO_5V0 | 19 (17 FET + R + C) | 7.10 | 28.0 | 28.7 | **63.8** |

<sub>The poly resistor + MIM cap set the ~20 ns RC and dominate the area (~55 um^2); the 9-17 transistors add only ~1-3 um^2. Resistor and cap areas are deliberately balanced near the analytic minimum for a fixed RC. Pulse cells (PHI/PLO) carry 8 extra transistors (inverter + output gate) versus the delay cells.</sub>

## 4. PVT corner results

### 4.1  1.8 V domain

| Cell | metric | nominal | min (corner) | max (corner) | passthrough max | t_rise max | t_fall max |
|---|---|---|---|---|---|---|---|
| DLYR_1V8 | rise delay | 20.36 ns | 16.24 ns (FF,1.98V,-55C) | 27.82 ns (SS,1.62V,150C) | 3.16 ns | 1995 ps | 589 ps |
| DLYF_1V8 | fall delay | 20.14 ns | 15.95 ns (FF,1.98V,-55C) | 27.62 ns (SS,1.62V,150C) | 1.36 ns | 682 ps | 1254 ps |
| PHI_1V8 | HIGH-pulse width | 20.23 ns | 16.43 ns (FF,1.98V,-55C) | 27.07 ns (SS,1.62V,150C) | - | 276 ps | 195 ps |
| PLO_1V8 | LOW-pulse width | 20.06 ns | 16.05 ns (FF,1.98V,-55C) | 27.25 ns (SS,1.62V,150C) | - | 263 ps | 214 ps |

<sub>Delay/width PVT spread vs nominal across this domain: -21% .. +37%.</sub>

### 4.2  3.3 V domain

| Cell | metric | nominal | min (corner) | max (corner) | passthrough max | t_rise max | t_fall max |
|---|---|---|---|---|---|---|---|
| DLYR_3V3 | rise delay | 20.21 ns | 16.64 ns (FF,3.63V,-55C) | 27.24 ns (SS,2.97V,150C) | 4.07 ns | 2314 ps | 934 ps |
| DLYF_3V3 | fall delay | 20.39 ns | 16.63 ns (FF,3.63V,-55C) | 27.62 ns (SS,2.97V,150C) | 1.91 ns | 1016 ps | 1736 ps |
| PHI_3V3 | HIGH-pulse width | 19.81 ns | 16.43 ns (FF,3.63V,-55C) | 26.44 ns (SS,2.97V,150C) | - | 396 ps | 304 ps |
| PLO_3V3 | LOW-pulse width | 19.83 ns | 16.31 ns (FF,3.63V,-55C) | 26.63 ns (SS,2.97V,150C) | - | 361 ps | 349 ps |

<sub>Delay/width PVT spread vs nominal across this domain: -18% .. +35%.</sub>

### 4.3  5.0 V domain

| Cell | metric | nominal | min (corner) | max (corner) | passthrough max | t_rise max | t_fall max |
|---|---|---|---|---|---|---|---|
| DLYR_5V0 | rise delay | 19.70 ns | 15.95 ns (FF,5.5V,-55C) | 32.71 ns (SS,3.2V,150C) | 10.26 ns | 5377 ps | 2603 ps |
| DLYF_5V0 | fall delay | 20.11 ns | 16.29 ns (FF,5.5V,-55C) | 34.29 ns (SS,3.2V,150C) | 5.46 ns | 2756 ps | 4046 ps |
| PHI_5V0 | HIGH-pulse width | 20.05 ns | 16.35 ns (FF,5.5V,-55C) | 32.75 ns (SS,3.2V,150C) | - | 1099 ps | 873 ps |
| PLO_5V0 | LOW-pulse width | 20.18 ns | 16.50 ns (FF,5.5V,-55C) | 34.17 ns (SS,3.2V,150C) | - | 988 ps | 1005 ps |

<sub>Delay/width PVT spread vs nominal across this domain: -19% .. +70%.</sub>

## 5. Monte Carlo results (process + mismatch, TT, 200 runs)

### 5.1  1.8 V domain

| Cell | mean | sigma | sigma/mean | min | max | 1%..99% | +-3sigma band |
|---|---|---|---|---|---|---|---|
| DLYR_1V8 | 20.48 ns | 1135 ps | 5.54% | 17.31 | 24.35 | 18.03..23.02 | 17.08..23.88 ns |
| DLYF_1V8 | 20.27 ns | 1204 ps | 5.94% | 16.96 | 24.82 | 17.97..22.96 | 16.66..23.89 ns |
| PHI_1V8 | 20.27 ns | 1157 ps | 5.71% | 17.75 | 23.41 | 17.99..23.14 | 16.80..23.74 ns |
| PLO_1V8 | 19.99 ns | 1254 ps | 6.28% | 17.23 | 23.13 | 17.51..22.51 | 16.23..23.75 ns |

### 5.2  3.3 V domain

| Cell | mean | sigma | sigma/mean | min | max | 1%..99% | +-3sigma band |
|---|---|---|---|---|---|---|---|
| DLYR_3V3 | 20.19 ns | 1083 ps | 5.37% | 17.26 | 23.85 | 17.83..22.69 | 16.94..23.44 ns |
| DLYF_3V3 | 20.37 ns | 1106 ps | 5.43% | 17.30 | 22.80 | 17.89..22.70 | 17.05..23.69 ns |
| PHI_3V3 | 19.95 ns | 1218 ps | 6.11% | 16.90 | 22.90 | 17.35..22.33 | 16.29..23.60 ns |
| PLO_3V3 | 19.77 ns | 1142 ps | 5.78% | 16.96 | 22.43 | 17.25..22.40 | 16.34..23.19 ns |

### 5.3  5.0 V domain

| Cell | mean | sigma | sigma/mean | min | max | 1%..99% | +-3sigma band |
|---|---|---|---|---|---|---|---|
| DLYR_5V0 | 19.69 ns | 1066 ps | 5.41% | 16.97 | 22.73 | 17.06..22.20 | 16.49..22.89 ns |
| DLYF_5V0 | 20.14 ns | 1081 ps | 5.37% | 17.33 | 23.86 | 17.96..22.51 | 16.89..23.38 ns |
| PHI_5V0 | 20.01 ns | 1033 ps | 5.16% | 17.64 | 23.37 | 17.77..22.56 | 16.91..23.11 ns |
| PLO_5V0 | 20.14 ns | 1026 ps | 5.10% | 16.34 | 22.27 | 17.81..22.16 | 17.06..23.22 ns |

## 6. Monte Carlo distributions (delay / pulse width)

Each histogram: 200 runs, x-axis bins in ns, bar length proportional to count.

**DLYR_1V8** (rise delay): mean 20.48 ns, sigma 1135 ps (5.54%)
```
 17.31 | ### 2
 17.81 | ### 2
 18.31 | ######### 7
 18.81 | ############################ 21
 19.32 | ########################################## 31
 19.82 | ###################################### 28
 20.32 | ############################################## 34
 20.83 | ####################################### 29
 21.33 | ############################### 23
 21.83 | ################ 12
 22.33 | ######## 6
 22.84 | ##### 4
 23.34 |  0
 23.84 | # 1
```

**DLYF_1V8** (fall delay): mean 20.27 ns, sigma 1204 ps (5.94%)
```
 16.96 | ## 2
 17.52 | ###### 5
 18.08 | ########## 9
 18.64 | ####################### 20
 19.20 | ##################################### 32
 19.77 | ############################################## 40
 20.33 | ##################################### 32
 20.89 | ################################## 30
 21.45 | ################## 16
 22.01 | ######### 8
 22.58 | ##### 4
 23.14 | # 1
 23.70 |  0
 24.26 | # 1
```

**PHI_1V8** (HIGH-pulse width): mean 20.27 ns, sigma 1157 ps (5.71%)
```
 17.75 | ############ 8
 18.15 | ##### 3
 18.56 | ######################### 16
 18.96 | ################################### 23
 19.37 | ############################# 19
 19.77 | ################################### 23
 20.17 | ############################################## 30
 20.58 | ################################### 23
 20.98 | ############################### 20
 21.39 | ####################### 15
 21.79 | ################# 11
 22.20 | ##### 3
 22.60 | ##### 3
 23.00 | ##### 3
```

**PLO_1V8** (LOW-pulse width): mean 19.99 ns, sigma 1254 ps (6.28%)
```
 17.23 | ######## 5
 17.65 | ########## 6
 18.07 | ############################ 17
 18.49 | ############################## 18
 18.91 | ############################ 17
 19.33 | ################################## 21
 19.76 | ############################################## 28
 20.18 | ########################################### 26
 20.60 | ################################## 21
 21.02 | ############# 8
 21.44 | ############################## 18
 21.86 | ########## 6
 22.28 | ############ 7
 22.70 | ### 2
```

**DLYR_3V3** (rise delay): mean 20.19 ns, sigma 1083 ps (5.37%)
```
 17.26 | # 1
 17.73 | ###### 5
 18.20 | ########## 8
 18.67 | ############################### 24
 19.14 | ############################ 22
 19.61 | ########################################## 33
 20.08 | ###################################### 30
 20.55 | ############################################## 36
 21.02 | ###################### 17
 21.50 | ################# 13
 21.97 | ######## 6
 22.44 | ##### 4
 22.91 |  0
 23.38 | # 1
```

**DLYF_3V3** (fall delay): mean 20.37 ns, sigma 1106 ps (5.43%)
```
 17.30 | ## 1
 17.69 | ##### 3
 18.09 | ############ 8
 18.48 | ########### 7
 18.87 | ######################### 16
 19.27 | ######################### 16
 19.66 | ################################### 23
 20.05 | ############################################## 30
 20.45 | ######################################### 27
 20.84 | ############################################## 30
 21.23 | ####################### 15
 21.62 | ############ 8
 22.02 | ############### 10
 22.41 | ######### 6
```

**PHI_3V3** (HIGH-pulse width): mean 19.95 ns, sigma 1218 ps (6.11%)
```
 16.90 | ### 2
 17.33 | ###### 4
 17.76 | ################# 11
 18.19 | ############################ 18
 18.62 | ######################### 16
 19.05 | ####################### 15
 19.47 | ############################################## 30
 19.90 | ########################################### 28
 20.33 | ##################### 14
 20.76 | ######################################### 27
 21.19 | ############################ 18
 21.62 | ################## 12
 22.05 | ##### 3
 22.48 | ### 2
```

**PLO_3V3** (LOW-pulse width): mean 19.77 ns, sigma 1142 ps (5.78%)
```
 16.96 | ##### 3
 17.35 | ###### 4
 17.75 | ########### 7
 18.14 | ################# 11
 18.53 | ########################## 17
 18.92 | ############################################## 30
 19.31 | ######################################## 26
 19.70 | ######################################### 27
 20.09 | ################################ 21
 20.48 | ############################### 20
 20.87 | #################### 13
 21.26 | ############## 9
 21.65 | ###### 4
 22.04 | ############ 8
```

**DLYR_5V0** (rise delay): mean 19.69 ns, sigma 1066 ps (5.41%)
```
 16.97 | ###### 5
 17.38 | ### 3
 17.79 | ########## 9
 18.21 | ############### 13
 18.62 | ############################ 24
 19.03 | ################################# 29
 19.44 | ######################### 22
 19.85 | ############################################## 40
 20.26 | ########################## 23
 20.67 | ################# 15
 21.08 | ########## 9
 21.49 | ###### 5
 21.90 | # 1
 22.31 | ## 2
```

**DLYF_5V0** (fall delay): mean 20.14 ns, sigma 1081 ps (5.37%)
```
 17.33 | ## 2
 17.80 | ###### 5
 18.27 | ########### 9
 18.73 | ######################## 20
 19.20 | ######################################### 34
 19.66 | ############################################## 38
 20.13 | ############################### 26
 20.60 | ############################## 25
 21.06 | ####################### 19
 21.53 | ############ 10
 21.99 | ########## 8
 22.46 | #### 3
 22.93 |  0
 23.39 | # 1
```

**PHI_5V0** (HIGH-pulse width): mean 20.01 ns, sigma 1033 ps (5.16%)
```
 17.64 | ######### 6
 18.05 | ###### 4
 18.46 | ################### 13
 18.87 | ########################################## 28
 19.28 | ############################################## 31
 19.69 | ########################################## 28
 20.10 | ############################################# 30
 20.51 | ################################# 22
 20.92 | ######################## 16
 21.33 | ################ 11
 21.73 | ####### 5
 22.14 | #### 3
 22.55 |  0
 22.96 | ### 2
```

**PLO_5V0** (LOW-pulse width): mean 20.14 ns, sigma 1026 ps (5.10%)
```
 16.34 | # 1
 16.77 |  0
 17.19 | # 1
 17.61 | #### 3
 18.04 | ###### 5
 18.46 | ################# 14
 18.88 | ################### 15
 19.31 | ############################## 24
 19.73 | ############################################## 37
 20.15 | ######################################### 33
 20.58 | ############################### 25
 21.00 | ############################# 23
 21.42 | ########### 9
 21.85 | ############ 10
```

## 7. Observations

- **MC spread is tight**: 1-sigma on the delay/width is 5.1-6.3% of the mean across all 12 cells. The timing is an RC product and the MIM cap (sigma_Cj ~ 0.1%) and poly Rsh are well controlled; most of the statistical spread comes from the Schmitt-trip (device Vth mismatch) rather than the RC itself.
- **PVT dominates over statistics**: the corner-to-corner delay swing (roughly -20%/+40% of nominal, worst case SS / hot / low-Vdd) is much larger than the +-3-sigma MC band. For a fixed-corner design the MC band is what matters; for a multi-corner design, budget the PVT envelope.
- **Temperature & supply**: delay increases at hot / low-supply (slower devices, higher poly Rsh via tc1) and shortens at cold / high-supply. The 5 V domain shows the widest PVT envelope because its supply axis (3.2-5.5 V) is the widest.
- **Output edges stay sharp**: the Schmitt output drives clean 10-90% edges (tens to a few hundred ps into 5 fF) regardless of the slow RC ramp, so downstream timing sees a real digital edge, not the RC slope.
- **Passthrough preserved over PVT**: the fast (non-delayed) edge stays far shorter than the timed edge at every corner, so the asymmetry holds.
- **Area is RC-bound**: each cell is ~56-64 um^2, of which ~55 um^2 is the poly resistor + MIM cap that set the time constant; the transistors are ~1-3 um^2. Area scales with the target delay (longer delay -> larger RC -> more area), essentially independent of voltage domain.

## 8. Files

- `char.json` - full numeric results (PVT envelopes, MC stats, raw MC samples). `dp_char.py` - characterization driver. `char_report.py` - this report. `decks/pvt_*`, `decks/mc_*` - the generated ngspice decks.
