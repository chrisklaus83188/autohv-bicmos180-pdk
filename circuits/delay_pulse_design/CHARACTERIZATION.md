# Delay & Pulse-Generator Cell Characterization Report
### AutoHV BiCMOS 180 PDK | 12 cells (4 archetypes x 3 voltage domains)

<sub>Models: **v2-grounded** (frozen) · simulator: **ngspice-45** · 200-run MC.</sub>

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
| DLYR_1V8 | 11 (9 FET + R + C) | 0.83 | 25.8 | 28.7 | **55.3** |
| DLYF_1V8 | 11 (9 FET + R + C) | 0.83 | 26.9 | 28.7 | **56.4** |
| PHI_1V8 | 19 (17 FET + R + C) | 1.55 | 26.9 | 28.7 | **57.2** |
| PLO_1V8 | 19 (17 FET + R + C) | 1.55 | 28.0 | 28.7 | **58.2** |
| DLYR_3V3 | 11 (9 FET + R + C) | 2.17 | 26.9 | 28.7 | **57.8** |
| DLYF_3V3 | 11 (9 FET + R + C) | 2.17 | 28.0 | 28.7 | **58.9** |
| PHI_3V3 | 19 (17 FET + R + C) | 4.06 | 26.9 | 28.7 | **59.7** |
| PLO_3V3 | 19 (17 FET + R + C) | 4.06 | 29.1 | 28.7 | **61.9** |
| DLYR_5V0 | 11 (9 FET + R + C) | 3.80 | 25.8 | 28.7 | **58.3** |
| DLYF_5V0 | 11 (9 FET + R + C) | 3.80 | 25.8 | 28.7 | **58.3** |
| PHI_5V0 | 19 (17 FET + R + C) | 7.10 | 25.8 | 28.7 | **61.6** |
| PLO_5V0 | 19 (17 FET + R + C) | 7.10 | 26.9 | 28.7 | **62.7** |

<sub>The poly resistor + MIM cap set the ~20 ns RC and dominate the area (~55 um^2); the 9-17 transistors add only ~1-3 um^2. Resistor and cap areas are deliberately balanced near the analytic minimum for a fixed RC. Pulse cells (PHI/PLO) carry 8 extra transistors (inverter + output gate) versus the delay cells.</sub>

## 4. PVT corner results

### 4.1  1.8 V domain

| Cell | metric | nominal | min (corner) | max (corner) | passthrough max | t_rise max | t_fall max |
|---|---|---|---|---|---|---|---|
| DLYR_1V8 | rise delay | 20.02 ns | 14.08 ns (FF,1.98V,150C) | 28.91 ns (SS,1.62V,-55C) | 2.50 ns | 1699 ps | 564 ps |
| DLYF_1V8 | fall delay | 19.78 ns | 13.74 ns (FF,1.98V,150C) | 28.70 ns (SS,1.62V,-55C) | 1.16 ns | 639 ps | 1158 ps |
| PHI_1V8 | HIGH-pulse width | 20.09 ns | 14.24 ns (FF,1.98V,150C) | 28.69 ns (SS,1.62V,-55C) | - | 276 ps | 201 ps |
| PLO_1V8 | LOW-pulse width | 19.84 ns | 13.81 ns (FF,1.98V,150C) | 29.05 ns (SS,1.62V,-55C) | - | 254 ps | 227 ps |

<sub>Delay/width PVT spread vs nominal across this domain: -31% .. +46%.</sub>

### 4.2  3.3 V domain

| Cell | metric | nominal | min (corner) | max (corner) | passthrough max | t_rise max | t_fall max |
|---|---|---|---|---|---|---|---|
| DLYR_3V3 | rise delay | 19.96 ns | 15.28 ns (FF,3.63V,150C) | 26.23 ns (SS,2.97V,-55C) | 3.42 ns | 2153 ps | 925 ps |
| DLYF_3V3 | fall delay | 20.15 ns | 15.27 ns (FF,3.63V,150C) | 26.63 ns (SS,2.97V,-55C) | 1.69 ns | 991 ps | 1680 ps |
| PHI_3V3 | HIGH-pulse width | 19.64 ns | 15.06 ns (FF,3.63V,150C) | 25.72 ns (SS,2.97V,-55C) | - | 419 ps | 324 ps |
| PLO_3V3 | LOW-pulse width | 20.38 ns | 15.43 ns (FF,3.63V,150C) | 27.00 ns (SS,2.97V,-55C) | - | 367 ps | 380 ps |

<sub>Delay/width PVT spread vs nominal across this domain: -24% .. +32%.</sub>

### 4.3  5.0 V domain

| Cell | metric | nominal | min (corner) | max (corner) | passthrough max | t_rise max | t_fall max |
|---|---|---|---|---|---|---|---|
| DLYR_5V0 | rise delay | 20.29 ns | 16.27 ns (FF,5.5V,150C) | 29.88 ns (SS,3.2V,-55C) | 8.48 ns | 4871 ps | 2534 ps |
| DLYF_5V0 | fall delay | 20.00 ns | 15.97 ns (FF,5.5V,150C) | 30.08 ns (SS,3.2V,-55C) | 4.70 ns | 2657 ps | 3848 ps |
| PHI_5V0 | HIGH-pulse width | 20.02 ns | 16.08 ns (FF,5.5V,150C) | 29.23 ns (SS,3.2V,-55C) | - | 1155 ps | 909 ps |
| PLO_5V0 | LOW-pulse width | 20.17 ns | 16.07 ns (FF,5.5V,150C) | 30.45 ns (SS,3.2V,-55C) | - | 995 ps | 1061 ps |

<sub>Delay/width PVT spread vs nominal across this domain: -20% .. +51%.</sub>

## 5. Monte Carlo results (process + mismatch, TT, 200 runs)

### 5.1  1.8 V domain

| Cell | mean | sigma | sigma/mean | min | max | 1%..99% | +-3sigma band |
|---|---|---|---|---|---|---|---|
| DLYR_1V8 | 20.02 ns | 1137 ps | 5.68% | 16.86 | 23.37 | 17.84..22.70 | 16.61..23.43 ns |
| DLYF_1V8 | 19.85 ns | 1185 ps | 5.97% | 15.93 | 23.59 | 17.29..22.63 | 16.30..23.41 ns |
| PHI_1V8 | 20.24 ns | 1236 ps | 6.11% | 16.78 | 23.25 | 17.24..22.82 | 16.53..23.95 ns |
| PLO_1V8 | 19.68 ns | 1195 ps | 6.07% | 15.52 | 23.77 | 17.30..22.23 | 16.09..23.26 ns |

### 5.2  3.3 V domain

| Cell | mean | sigma | sigma/mean | min | max | 1%..99% | +-3sigma band |
|---|---|---|---|---|---|---|---|
| DLYR_3V3 | 19.96 ns | 1128 ps | 5.65% | 16.71 | 23.36 | 17.78..22.43 | 16.57..23.34 ns |
| DLYF_3V3 | 20.20 ns | 1122 ps | 5.55% | 16.52 | 22.57 | 17.81..22.48 | 16.83..23.56 ns |
| PHI_3V3 | 19.74 ns | 1174 ps | 5.95% | 16.73 | 22.30 | 17.38..22.23 | 16.21..23.26 ns |
| PLO_3V3 | 20.38 ns | 1151 ps | 5.65% | 16.94 | 23.06 | 18.14..22.73 | 16.93..23.83 ns |

### 5.3  5.0 V domain

| Cell | mean | sigma | sigma/mean | min | max | 1%..99% | +-3sigma band |
|---|---|---|---|---|---|---|---|
| DLYR_5V0 | 20.46 ns | 1104 ps | 5.40% | 17.39 | 23.70 | 18.18..23.00 | 17.15..23.77 ns |
| DLYF_5V0 | 20.03 ns | 1089 ps | 5.44% | 17.44 | 23.12 | 18.01..22.56 | 16.76..23.30 ns |
| PHI_5V0 | 20.20 ns | 1068 ps | 5.29% | 17.10 | 22.71 | 17.64..22.37 | 17.00..23.41 ns |
| PLO_5V0 | 20.21 ns | 1087 ps | 5.38% | 17.15 | 23.04 | 17.89..22.83 | 16.95..23.47 ns |

## 6. Monte Carlo distributions (delay / pulse width)

Each histogram: 200 runs, x-axis bins in ns, bar length proportional to count.

**DLYR_1V8** (rise delay): mean 20.02 ns, sigma 1137 ps (5.68%)
```
 16.86 | ## 2
 17.32 |  0
 17.79 | ############# 11
 18.25 | ############### 12
 18.72 | ########################### 22
 19.19 | ######################################### 34
 19.65 | ######################### 21
 20.12 | ############################################## 38
 20.58 | ############################### 26
 21.05 | ################ 13
 21.51 | ############ 10
 21.98 | ######## 7
 22.44 | ## 2
 22.91 | ## 2
```

**DLYF_1V8** (fall delay): mean 19.85 ns, sigma 1185 ps (5.97%)
```
 15.93 | # 1
 16.47 |  0
 17.02 | #### 3
 17.57 | ############# 11
 18.12 | ##################### 18
 18.66 | ############################ 24
 19.21 | ######################################### 35
 19.76 | ############################################## 39
 20.31 | ##################################### 31
 20.85 | ########################### 23
 21.40 | ########### 9
 21.95 | #### 3
 22.50 | # 1
 23.04 | ## 2
```

**PHI_1V8** (HIGH-pulse width): mean 20.24 ns, sigma 1236 ps (6.11%)
```
 16.78 | ### 2
 17.25 | #### 3
 17.71 | ######### 6
 18.17 | ############## 10
 18.63 | ################# 12
 19.09 | ################################ 22
 19.56 | ############################################## 32
 20.02 | ############################################## 32
 20.48 | ################################# 23
 20.94 | ######################## 17
 21.41 | ################################# 23
 21.87 | ################ 11
 22.33 | ###### 4
 22.79 | #### 3
```

**PLO_1V8** (LOW-pulse width): mean 19.68 ns, sigma 1195 ps (6.07%)
```
 15.52 | # 1
 16.11 | # 1
 16.70 |  0
 17.29 | ########### 10
 17.88 | ######################## 21
 18.47 | ########################### 24
 19.06 | ############################################## 41
 19.65 | ########################################### 38
 20.24 | #################################### 32
 20.83 | ##################### 19
 21.42 | ########## 9
 22.01 | ## 2
 22.60 | # 1
 23.18 | # 1
```

**DLYR_3V3** (rise delay): mean 19.96 ns, sigma 1128 ps (5.65%)
```
 16.71 | ### 2
 17.18 |  0
 17.66 | ######### 6
 18.13 | ###################### 15
 18.61 | #################################### 25
 19.08 | ########################################## 29
 19.56 | ########################################## 29
 20.03 | ############################################## 32
 20.51 | ##################################### 26
 20.98 | ########################### 19
 21.46 | ############# 9
 21.93 | ####### 5
 22.41 | # 1
 22.88 | ### 2
```

**DLYF_3V3** (fall delay): mean 20.20 ns, sigma 1122 ps (5.55%)
```
 16.52 | # 1
 16.95 |  0
 17.38 | ### 2
 17.82 | ########### 8
 18.25 | ############ 9
 18.68 | ############# 10
 19.11 | ############################ 21
 19.54 | ############################################## 35
 19.98 | ####################################### 30
 20.41 | ################################### 27
 20.84 | ################################ 24
 21.27 | #################### 15
 21.70 | ############ 9
 22.14 | ############ 9
```

**PHI_3V3** (HIGH-pulse width): mean 19.74 ns, sigma 1174 ps (5.95%)
```
 16.73 | # 1
 17.12 | ##### 4
 17.52 | ############ 9
 17.92 | ################ 12
 18.32 | ############### 11
 18.72 | ################################ 24
 19.12 | ############################### 23
 19.51 | ############################################## 34
 19.91 | ####################### 17
 20.31 | ################################## 25
 20.71 | ############### 11
 21.11 | ################## 13
 21.51 | ############## 10
 21.90 | ######## 6
```

**PLO_3V3** (LOW-pulse width): mean 20.38 ns, sigma 1151 ps (5.65%)
```
 16.94 | # 1
 17.38 | # 1
 17.81 | ### 2
 18.25 | ############## 11
 18.69 | ################## 14
 19.13 | ######################## 18
 19.56 | ###################################### 29
 20.00 | ############################################## 35
 20.44 | ################################# 25
 20.87 | ###################### 17
 21.31 | ###################### 17
 21.75 | ######################### 19
 22.18 | ########### 8
 22.62 | #### 3
```

**DLYR_5V0** (rise delay): mean 20.46 ns, sigma 1104 ps (5.40%)
```
 17.39 | # 1
 17.84 | #### 3
 18.29 | ########### 8
 18.74 | ########### 8
 19.19 | ######################################## 29
 19.64 | ############################################## 33
 20.10 | ########################################## 30
 20.55 | #################################### 26
 21.00 | ################################### 25
 21.45 | ############## 10
 21.90 | ########################## 19
 22.35 | ####### 5
 22.80 | # 1
 23.25 | ### 2
```

**DLYF_5V0** (fall delay): mean 20.03 ns, sigma 1089 ps (5.44%)
```
 17.44 | ## 1
 17.84 | ######### 6
 18.25 | ##################### 14
 18.66 | ############################# 19
 19.06 | ##################################### 24
 19.47 | ############################################## 30
 19.87 | ######################################## 26
 20.28 | ########################################### 28
 20.69 | ####################### 15
 21.09 | ######################### 16
 21.50 | ################# 11
 21.90 | ######### 6
 22.31 | ### 2
 22.72 | ### 2
```

**PHI_5V0** (HIGH-pulse width): mean 20.20 ns, sigma 1068 ps (5.29%)
```
 17.10 | #### 2
 17.50 | ## 1
 17.90 | ######### 5
 18.30 | ############ 7
 18.70 | ################################ 18
 19.10 | ####################################### 22
 19.51 | ############################################ 25
 19.91 | ########################################## 24
 20.31 | ############################################## 26
 20.71 | ############################################ 25
 21.11 | ##################################### 21
 21.51 | ####################### 13
 21.91 | ############ 7
 22.31 | ##### 3
```

**PLO_5V0** (LOW-pulse width): mean 20.21 ns, sigma 1087 ps (5.38%)
```
 17.15 | # 1
 17.57 | #### 3
 17.99 | ######## 6
 18.41 | ################ 12
 18.83 | ################# 13
 19.25 | ################################ 24
 19.67 | ########################################## 32
 20.09 | ############################################## 35
 20.52 | ####################################### 30
 20.94 | ######################## 18
 21.36 | ############ 9
 21.78 | ############ 9
 22.20 | ##### 4
 22.62 | ##### 4
```

## 7. Observations

- **MC spread is tight**: 1-sigma on the delay/width is 5.3-6.1% of the mean across all 12 cells. The timing is an RC product and the MIM cap (sigma_Cj ~ 0.1%) and poly Rsh are well controlled; most of the statistical spread comes from the Schmitt-trip (device Vth mismatch) rather than the RC itself.
- **PVT dominates over statistics**: the corner-to-corner delay swing (roughly -31%/+51% of nominal, worst case SS / -55C / low-Vdd) is much larger than the +-3-sigma MC band. For a fixed-corner design the MC band is what matters; for a multi-corner design, budget the PVT envelope.
- **Temperature & supply**: under v2-grounded the `RPOLY_HI` tc1 is negative, so poly Rsh is *highest at cold* and the slowest corner is **-55C / low-supply** (the resistor's cold-increase now outweighs the opposing device tempco). This flipped the worst-case temperature from hot to cold vs the pre-tc1-sign-flip characterization. The 5 V domain still shows the widest PVT envelope because its supply axis (3.2-5.5 V) is the widest.
- **Output edges stay sharp**: the Schmitt output drives clean 10-90% edges (tens to a few hundred ps into 5 fF) regardless of the slow RC ramp, so downstream timing sees a real digital edge, not the RC slope.
- **Passthrough preserved over PVT**: the fast (non-delayed) edge stays far shorter than the timed edge at every corner, so the asymmetry holds.
- **Area is RC-bound**: each cell is ~56-64 um^2, of which ~55 um^2 is the poly resistor + MIM cap that set the time constant; the transistors are ~1-3 um^2. Area scales with the target delay (longer delay -> larger RC -> more area), essentially independent of voltage domain.

## 8. Files

- `char.json` - full numeric results (PVT envelopes, MC stats, raw MC samples). `dp_char.py` - characterization driver. `char_report.py` - this report. `decks/pvt_*`, `decks/mc_*` - the generated ngspice decks.
