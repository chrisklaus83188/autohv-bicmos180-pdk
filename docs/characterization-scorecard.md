# Characterization Scorecard — AutoHV BiCMOS180 PDK (phase 2 baseline)

**This is the before-picture.** No model fixes landed in phase 2; the PDK was
measured as-is so every later fix can be diffed against this baseline.

- ngspice: `ngspice-45 : Circuit level simulation program`
- generated: 2026-07-24T20:01:28+00:00
- wall time: 6218.3 s
- results: `pdk_validation/characterization/results/characterization-results.json`
- anchors: `docs/anchor-values.json`
- harness: `python pdk_validation/characterization/run_all.py`

## Status policy (anchor doc §8)

| status | meaning |
|---|---|
| `hard-fail` | `[physics]`/`[model]` anchor, measured outside band, **not** predicted by phase 1 |
| `expected-fail` | outside band **and** predicted by a phase-1 finding — the regression tripwires |
| `warn` | `[industry]` anchor outside band — a conversation, not a bug |
| `blocked` | anchor carries `conditional_on`; measured but not asserted |
| `descriptive` | anchor band contested; reported, never scored |
| `artifact` | in `_known_artifacts`; measured, logged, never asserted |
| `pass` | inside band |

## Summary

| status | count |
|---|---|
| `hard-fail` | 19 |
| `warn` | 81 |
| `descriptive` | 4 |
| `artifact` | 28 |
| `error` | 6 |
| `no-anchor` | 130 |
| `pass` | 280 |
| **total** | **548** |

### By family

| family | hard-fail | warn | descriptive | artifact | error | no-anchor | pass |
|---|---|---|---|---|---|---|---|
| BJT | 4 | 12 | 4 | 0 | 6 | 12 | 14 |
| BSIM3 MOS | 2 | 54 | 0 | 0 | 0 | 42 | 40 |
| Diodes/zeners | 5 | 6 | 0 | 0 | 0 | 1 | 16 |
| Other | 0 | 1 | 0 | 2 | 0 | 5 | 13 |
| Passives | 0 | 2 | 0 | 0 | 0 | 9 | 43 |
| VDMOS | 8 | 6 | 0 | 26 | 0 | 61 | 154 |

**Hard-fails not predicted by phase 1: 19.** These are the rows to read first — everything else was already known.

## Unexpected hard-fails

| device | FoM | measured | band | ×target | deck |
|---|---|---|---|---|---|
| DIO_SCH | `tt_transit_time` | 3.019e-10 s | 0 – 1.000e-12 | -- | `pdk_validation/characterization/decks/diodes/DIO_SCH_diffcap.cir` |
| DZ_12 | `cjo_density` | 5.5e+04 fF/um^2 | 0.515 – 2.062 | 5.33e+04× | `pdk_validation/characterization/decks/diodes/DZ_12_cjo.cir` |
| DZ_24 | `cjo_density` | 2.8e+04 fF/um^2 | 0.509 – 2.038 | 2.75e+04× | `pdk_validation/characterization/decks/diodes/DZ_24_cjo.cir` |
| DZ_5V6 | `bv` | 5.243 V | 5.32 – 5.88 | 0.936× | `pdk_validation/characterization/decks/diodes/DZ_5V6_rev_27C.cir` |
| DZ_5V6 | `cjo_density` | 1.200e+05 fF/um^2 | 1.663 – 6.652 | 3.61e+04× | `pdk_validation/characterization/decks/diodes/DZ_5V6_cjo.cir` |
| NDMOS120 | `theta` | 0.7889 1/V | 0.05 – 0.3 | 5.26× | `pdk_validation/characterization/decks/vdmos/NDMOS120_theta.cir` |
| NDMOS200 | `theta` | 1.048 1/V | 0.05 – 0.3 | 6.99× | `pdk_validation/characterization/decks/vdmos/NDMOS200_theta.cir` |
| NDMOS40 | `theta` | 0.4898 1/V | 0.05 – 0.45 | 3.27× | `pdk_validation/characterization/decks/vdmos/NDMOS40_theta.cir` |
| NDMOS60 | `theta` | 0.5736 1/V | 0.05 – 0.45 | 3.82× | `pdk_validation/characterization/decks/vdmos/NDMOS60_theta.cir` |
| NDMOS80 | `theta` | 0.6506 1/V | 0.05 – 0.45 | 4.34× | `pdk_validation/characterization/decks/vdmos/NDMOS80_theta.cir` |
| NMOS12 | `cox` | 1.103 fF/um^2 | 0.95 – 0 | -- | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_caps.cir` |
| NPN_HV | `bvcbo` | 37.84 V | 40.5 – 49.5 | 0.841× | `pdk_validation/characterization/decks/bjt/NPN_HV_bvcbo.cir` |
| NPN_HV | `bvceo_implied` | 24.83 V | 11.25 – 22.5 | 1.65× | `pdk_validation/characterization/decks/bjt/NPN_HV_bvceo.cir` |
| NPN_LV | `bvcbo` | 11.77 V | 12.6 – 15.4 | 0.841× | `pdk_validation/characterization/decks/bjt/NPN_LV_bvcbo.cir` |
| NPN_LV | `bvceo_implied` | 7.465 V | 3.5 – 7 | 1.83× | `pdk_validation/characterization/decks/bjt/NPN_LV_bvceo.cir` |
| PDMOS120 | `theta` | 0.3353 1/V | 0.05 – 0.3 | 2.24× | `pdk_validation/characterization/decks/vdmos/PDMOS120_theta.cir` |
| PDMOS200 | `cjo_per_cell` | 16.97 fF | 20.2 – 247.1 | 0.24× | `pdk_validation/characterization/decks/vdmos/PDMOS200_cap_0p1.cir` |
| PDMOS200 | `theta` | 0.4346 1/V | 0.05 – 0.3 | 2.9× | `pdk_validation/characterization/decks/vdmos/PDMOS200_theta.cir` |
| PMOS12 | `cox` | 1.007 fF/um^2 | 0.95 – 0 | -- | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_caps.cir` |

## BSIM3 MOS

| device | FoM | measured | units | band | status | ×target | deck |
|---|---|---|---|---|---|---|---|
| NMOS12 | `cox` | 1.103 | fF/um^2 | 0.95 – 0 | **hard-fail** |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_caps.cir` |
| NMOS12 | `cj_area` | 1.82 | fF/um^2 | 0.245 – 0.49 | warn | 5.2× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_caps.cir` |
| NMOS12 | `cjsw_sidewall` | 0.4333 | fF/um | 0.05 – 0.15 | warn | 4.33× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_caps.cir` |
| NMOS12 | `idsat_corner_spread` | 8.485 | percent | 12 – 20 | warn | 0.53× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_corner_TT.cir` |
| NMOS12 | `idsat_density` | 1.018 | mA/um | 0.2 – 0.4 | warn | 3.39× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_idsat.cir` |
| NMOS12 | `subthreshold_swing` | 184.6 | mV/dec | 72 – 96 | warn | 2.31× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_idvg.cir` |
| NMOS12 | `vth_corner_spread` | 80 | mV | 90 – 130 | warn | 0.727× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_corner_TT.cir` |
| NMOS12 | `vth_lin` | 1.466 | V | 1.29 – 1.41 | warn | 1.09× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_idvg.cir` |
| NMOS12 | `idsat_density_L1u` | 0.1854 | mA/um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_idsat.cir` |
| NMOS12 | `mc_avt_implied_1sigma` | 30.9 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS12_mc_s0.cir` |
| NMOS12 | `mc_sigma_di_over_i` | 0.6527 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS12_mc_s0.cir` |
| NMOS12 | `mc_sigma_dvth_1sigma` | 13.82 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS12_mc_s0.cir` |
| NMOS12 | `mc_sigma_vth_per_device_1sigma` | 9.77 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS12_mc_s0.cir` |
| NMOS12 | `vth_model_internal` | 1.327 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_corner_TT.cir` |
| NMOS12 | `cgso_overlap` | 0.2072 | fF/um | 0.09 – 0.24 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_caps.cir` |
| NMOS12 | `flicker_corner` | 5.012e+05 | Hz | 2e+04 – 1.000e+06 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_noise.cir` |
| NMOS12 | `junction_perimeter_set` | 1 | boolean | 1 – 1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_caps.cir` |
| NMOS12 | `vth_tempco` | -1.599 | mV/degC | -1.8 – -1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_temp_150.cir` |
| NMOS18 | `cj_area` | 2.22 | fF/um^2 | 0.7 – 1.4 | warn | 2.22× | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_caps.cir` |
| NMOS18 | `cjsw_sidewall` | 0.5286 | fF/um | 0.05 – 0.15 | warn | 5.29× | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_caps.cir` |
| NMOS18 | `flicker_corner` | 2.512e+06 | Hz | 2e+04 – 1.000e+06 | warn | 12.6× | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_noise.cir` |
| NMOS18 | `idsat_corner_spread` | 25.23 | percent | 12 – 20 | warn | 1.58× | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_corner_TT.cir` |
| NMOS18 | `idsat_density` | 0.5429 | mA/um | 0.55 – 0.6 | warn | 0.944× | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_idsat.cir` |
| NMOS18 | `vth_corner_spread` | 79 | mV | 90 – 130 | warn | 0.718× | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_corner_TT.cir` |
| NMOS18 | `vth_lin` | 0.6301 | V | 0.42 – 0.54 | warn | 1.31× | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_idvg.cir` |
| NMOS18 | `vth_tempco` | -0.9995 | mV/degC | -1.8 – -1 | warn | 0.714× | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_temp_150.cir` |
| NMOS18 | `mc_avt_implied_1sigma` | 3.503 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS18_mc_s0.cir` |
| NMOS18 | `mc_sigma_di_over_i` | 0.9092 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS18_mc_s0.cir` |
| NMOS18 | `mc_sigma_dvth_1sigma` | 1.566 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS18_mc_s0.cir` |
| NMOS18 | `mc_sigma_vth_per_device_1sigma` | 1.108 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS18_mc_s0.cir` |
| NMOS18 | `vth_model_internal` | 0.604 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_corner_TT.cir` |
| NMOS18 | `cgso_overlap` | 0.3198 | fF/um | 0.132 – 0.352 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_caps.cir` |
| NMOS18 | `cox` | 7.704 | fF/um^2 | 7.333 – 8.531 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_caps.cir` |
| NMOS18 | `junction_perimeter_set` | 1 | boolean | 1 – 1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_caps.cir` |
| NMOS18 | `subthreshold_swing` | 79.05 | mV/dec | 72 – 96 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_idvg.cir` |
| NMOS33 | `cj_area` | 2.02 | fF/um^2 | 0.574 – 1.148 | warn | 2.46× | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_caps.cir` |
| NMOS33 | `cjsw_sidewall` | 0.481 | fF/um | 0.05 – 0.15 | warn | 4.81× | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_caps.cir` |
| NMOS33 | `idsat_corner_spread` | 20.6 | percent | 12 – 20 | warn | 1.29× | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_corner_TT.cir` |
| NMOS33 | `idsat_density` | 0.4484 | mA/um | 0.45 – 0.55 | warn | 0.897× | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_idsat.cir` |
| NMOS33 | `vth_corner_spread` | 79.59 | mV | 90 – 130 | warn | 0.724× | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_corner_TT.cir` |
| NMOS33 | `vth_lin` | 0.8095 | V | 0.6 – 0.72 | warn | 1.23× | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_idvg.cir` |
| NMOS33 | `mc_avt_implied_1sigma` | 3.994 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS33_mc_s0.cir` |
| NMOS33 | `mc_sigma_di_over_i` | 0.4257 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS33_mc_s0.cir` |
| NMOS33 | `mc_sigma_dvth_1sigma` | 1.786 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS33_mc_s0.cir` |
| NMOS33 | `mc_sigma_vth_per_device_1sigma` | 1.263 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS33_mc_s0.cir` |
| NMOS33 | `vth_model_internal` | 0.7696 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_corner_TT.cir` |
| NMOS33 | `cgso_overlap` | 0.2896 | fF/um | 0.12 – 0.32 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_caps.cir` |
| NMOS33 | `cox` | 4.996 | fF/um^2 | 4.617 – 5.372 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_caps.cir` |
| NMOS33 | `flicker_corner` | 3.981e+05 | Hz | 2e+04 – 1.000e+06 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_noise.cir` |
| NMOS33 | `junction_perimeter_set` | 1 | boolean | 1 – 1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_caps.cir` |
| NMOS33 | `subthreshold_swing` | 92.51 | mV/dec | 72 – 96 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_idvg.cir` |
| NMOS33 | `vth_tempco` | -1.333 | mV/degC | -1.8 – -1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_temp_150.cir` |
| NMOS50 | `cj_area` | 1.82 | fF/um^2 | 1.1 – 1.6 | warn | 1.3× | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_caps.cir` |
| NMOS50 | `cjsw_sidewall` | 0.4333 | fF/um | 0.05 – 0.15 | warn | 4.33× | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_caps.cir` |
| NMOS50 | `idsat_density` | 0.3054 | mA/um | 0.48 – 0.6 | warn | 0.566× | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_idsat.cir` |
| NMOS50 | `subthreshold_swing` | 121.1 | mV/dec | 85 – 100 | warn | 1.28× | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_idvg.cir` |
| NMOS50 | `vth_corner_spread` | 79.67 | mV | 90 – 130 | warn | 0.724× | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_corner_TT.cir` |
| NMOS50 | `vth_lin` | 1.016 | V | 0.79 – 0.92 | warn | 1.2× | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_idvg.cir` |
| NMOS50 | `mc_avt_implied_1sigma` | 11.48 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS50_mc_s0.cir` |
| NMOS50 | `mc_sigma_di_over_i` | 0.6988 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS50_mc_s0.cir` |
| NMOS50 | `mc_sigma_dvth_1sigma` | 5.134 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS50_mc_s0.cir` |
| NMOS50 | `mc_sigma_vth_per_device_1sigma` | 3.63 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS50_mc_s0.cir` |
| NMOS50 | `vth_model_internal` | 0.9598 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_corner_TT.cir` |
| NMOS50 | `cgso_overlap` | 0.259 | fF/um | 0.108 – 0.288 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_caps.cir` |
| NMOS50 | `cox` | 3.116 | fF/um^2 | 2.833 – 3.296 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_caps.cir` |
| NMOS50 | `flicker_corner` | 1.585e+05 | Hz | 2e+04 – 1.000e+06 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_noise.cir` |
| NMOS50 | `idsat_corner_spread` | 18.46 | percent | 12 – 20 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_corner_TT.cir` |
| NMOS50 | `junction_perimeter_set` | 1 | boolean | 1 – 1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_caps.cir` |
| NMOS50 | `vth_tempco` | -1.599 | mV/degC | -1.8 – -1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_temp_150.cir` |
| PMOS12 | `cox` | 1.007 | fF/um^2 | 0.95 – 0 | **hard-fail** |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_caps.cir` |
| PMOS12 | `cj_area` | 1.92 | fF/um^2 | 0.266 – 0.532 | warn | 5.05× | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_caps.cir` |
| PMOS12 | `cjsw_sidewall` | 0.4571 | fF/um | 0.05 – 0.15 | warn | 4.57× | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_caps.cir` |
| PMOS12 | `idsat_density` | 0.678 | mA/um | 0.12 – 0.25 | warn | 3.67× | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_idsat.cir` |
| PMOS12 | `subthreshold_swing` | 215.1 | mV/dec | 72 – 96 | warn | 2.69× | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_idvg.cir` |
| PMOS12 | `vth_corner_spread` | 80 | mV | 90 – 130 | warn | 0.727× | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_corner_TT.cir` |
| PMOS12 | `vth_lin` | 1.728 | V | 1.49 – 1.61 | warn | 1.12× | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_idvg.cir` |
| PMOS12 | `idsat_density_L1u` | 0.08652 | mA/um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_idsat.cir` |
| PMOS12 | `mc_avt_implied_1sigma` | 29.09 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS12_mc_s0.cir` |
| PMOS12 | `mc_sigma_di_over_i` | 0.6752 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS12_mc_s0.cir` |
| PMOS12 | `mc_sigma_dvth_1sigma` | 13.01 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS12_mc_s0.cir` |
| PMOS12 | `mc_sigma_vth_per_device_1sigma` | 9.198 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS12_mc_s0.cir` |
| PMOS12 | `vth_model_internal` | 1.584 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_corner_TT.cir` |
| PMOS12 | `cgso_overlap` | 0.2172 | fF/um | 0.096 – 0.256 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_caps.cir` |
| PMOS12 | `flicker_corner` | 3.981e+04 | Hz | 2e+04 – 1.000e+06 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_noise.cir` |
| PMOS12 | `idsat_corner_spread` | 12.4 | percent | 12 – 20 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_corner_TT.cir` |
| PMOS12 | `junction_perimeter_set` | 1 | boolean | 1 – 1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_caps.cir` |
| PMOS12 | `vth_tempco` | -1.466 | mV/degC | -1.8 – -1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_temp_150.cir` |
| PMOS18 | `cj_area` | 2.32 | fF/um^2 | 0.735 – 1.47 | warn | 2.21× | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_caps.cir` |
| PMOS18 | `cjsw_sidewall` | 0.5524 | fF/um | 0.05 – 0.15 | warn | 5.52× | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_caps.cir` |
| PMOS18 | `idsat_corner_spread` | 34.27 | percent | 12 – 20 | warn | 2.14× | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_corner_TT.cir` |
| PMOS18 | `idsat_density` | 0.1734 | mA/um | 0.25 – 0.3 | warn | 0.631× | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_idsat.cir` |
| PMOS18 | `vth_corner_spread` | 79.04 | mV | 90 – 130 | warn | 0.719× | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_corner_TT.cir` |
| PMOS18 | `vth_lin` | 0.7143 | V | 0.46 – 0.58 | warn | 1.37× | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_idvg.cir` |
| PMOS18 | `vth_tempco` | -0.9995 | mV/degC | -1.8 – -1 | warn | 0.714× | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_temp_150.cir` |
| PMOS18 | `mc_avt_implied_1sigma` | 3.419 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS18_mc_s0.cir` |
| PMOS18 | `mc_sigma_di_over_i` | 1.003 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS18_mc_s0.cir` |
| PMOS18 | `mc_sigma_dvth_1sigma` | 1.529 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS18_mc_s0.cir` |
| PMOS18 | `mc_sigma_vth_per_device_1sigma` | 1.081 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS18_mc_s0.cir` |
| PMOS18 | `vth_model_internal` | 0.692 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_corner_TT.cir` |
| PMOS18 | `cgso_overlap` | 0.3397 | fF/um | 0.144 – 0.384 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_caps.cir` |
| PMOS18 | `cox` | 7.635 | fF/um^2 | 7.333 – 8.531 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_caps.cir` |
| PMOS18 | `flicker_corner` | 1.585e+05 | Hz | 2e+04 – 1.000e+06 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_noise.cir` |
| PMOS18 | `junction_perimeter_set` | 1 | boolean | 1 – 1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_caps.cir` |
| PMOS18 | `subthreshold_swing` | 83.79 | mV/dec | 72 – 96 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_idvg.cir` |
| PMOS33 | `cj_area` | 2.12 | fF/um^2 | 0.616 – 1.232 | warn | 2.41× | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_caps.cir` |
| PMOS33 | `cjsw_sidewall` | 0.5048 | fF/um | 0.05 – 0.15 | warn | 5.05× | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_caps.cir` |
| PMOS33 | `idsat_corner_spread` | 26.73 | percent | 12 – 20 | warn | 1.67× | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_corner_TT.cir` |
| PMOS33 | `idsat_density` | 0.1569 | mA/um | 0.2 – 0.28 | warn | 0.654× | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_idsat.cir` |
| PMOS33 | `subthreshold_swing` | 108.3 | mV/dec | 72 – 96 | warn | 1.35× | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_idvg.cir` |
| PMOS33 | `vth_corner_spread` | 79.64 | mV | 90 – 130 | warn | 0.724× | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_corner_TT.cir` |
| PMOS33 | `vth_lin` | 0.9125 | V | 0.68 – 0.8 | warn | 1.23× | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_idvg.cir` |
| PMOS33 | `mc_avt_implied_1sigma` | 4.246 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS33_mc_s0.cir` |
| PMOS33 | `mc_sigma_di_over_i` | 0.497 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS33_mc_s0.cir` |
| PMOS33 | `mc_sigma_dvth_1sigma` | 1.899 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS33_mc_s0.cir` |
| PMOS33 | `mc_sigma_vth_per_device_1sigma` | 1.343 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS33_mc_s0.cir` |
| PMOS33 | `vth_model_internal` | 0.8766 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_corner_TT.cir` |
| PMOS33 | `cgso_overlap` | 0.3095 | fF/um | 0.132 – 0.352 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_caps.cir` |
| PMOS33 | `cox` | 4.928 | fF/um^2 | 4.617 – 5.372 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_caps.cir` |
| PMOS33 | `flicker_corner` | 5.012e+04 | Hz | 2e+04 – 1.000e+06 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_noise.cir` |
| PMOS33 | `junction_perimeter_set` | 1 | boolean | 1 – 1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_caps.cir` |
| PMOS33 | `vth_tempco` | -1.333 | mV/degC | -1.8 – -1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_temp_150.cir` |
| PMOS50 | `cj_area` | 1.92 | fF/um^2 | 1.2 – 1.7 | warn | 1.28× | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_caps.cir` |
| PMOS50 | `cjsw_sidewall` | 0.4571 | fF/um | 0.05 – 0.15 | warn | 4.57× | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_caps.cir` |
| PMOS50 | `idsat_corner_spread` | 23.56 | percent | 12 – 20 | warn | 1.47× | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_corner_TT.cir` |
| PMOS50 | `idsat_density` | 0.1204 | mA/um | 0.22 – 0.3 | warn | 0.463× | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_idsat.cir` |
| PMOS50 | `subthreshold_swing` | 146 | mV/dec | 85 – 100 | warn | 1.54× | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_idvg.cir` |
| PMOS50 | `vth_corner_spread` | 79.74 | mV | 90 – 130 | warn | 0.725× | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_corner_TT.cir` |
| PMOS50 | `vth_lin` | 1.144 | V | 0.83 – 0.95 | warn | 1.27× | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_idvg.cir` |
| PMOS50 | `mc_avt_implied_1sigma` | 11.59 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS50_mc_s0.cir` |
| PMOS50 | `mc_sigma_di_over_i` | 0.7863 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS50_mc_s0.cir` |
| PMOS50 | `mc_sigma_dvth_1sigma` | 5.181 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS50_mc_s0.cir` |
| PMOS50 | `mc_sigma_vth_per_device_1sigma` | 3.664 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS50_mc_s0.cir` |
| PMOS50 | `vth_model_internal` | 1.089 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_corner_TT.cir` |
| PMOS50 | `cgso_overlap` | 0.2688 | fF/um | 0.114 – 0.304 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_caps.cir` |
| PMOS50 | `cox` | 3.031 | fF/um^2 | 2.833 – 3.296 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_caps.cir` |
| PMOS50 | `flicker_corner` | 3.162e+04 | Hz | 2e+04 – 1.000e+06 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_noise.cir` |
| PMOS50 | `junction_perimeter_set` | 1 | boolean | 1 – 1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_caps.cir` |
| PMOS50 | `vth_tempco` | -1.466 | mV/degC | -1.8 – -1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_temp_150.cir` |

## VDMOS

| device | FoM | measured | units | band | status | ×target | deck |
|---|---|---|---|---|---|---|---|
| NDMOS120 | `theta` | 0.7889 | 1/V | 0.05 – 0.3 | **hard-fail** | 5.26× | `pdk_validation/characterization/decks/vdmos/NDMOS120_theta.cir` |
| NDMOS120 | `body_diode_tt` | 8.000e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_card.cir` |
| NDMOS120 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_rcond.cir` |
| NDMOS120 | `bv_corner_FF` | 128.1 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_bv_FF.cir` |
| NDMOS120 | `bv_corner_FS` | 128.1 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_bv_FS.cir` |
| NDMOS120 | `bv_corner_SF` | 141.6 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_bv_SF.cir` |
| NDMOS120 | `bv_corner_SS` | 141.6 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_bv_SS.cir` |
| NDMOS120 | `vth_lin` | 1.151 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_idvg.cir` |
| NDMOS120 | `bv` | 134.9 | V | 124.2 – 148.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_bv_TT.cir` |
| NDMOS120 | `cgdmax_per_cell` | 18.63 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_cap_0p1.cir` |
| NDMOS120 | `cgdmin_per_cell` | 6.906 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_cap_121p5.cir` |
| NDMOS120 | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_cap_0p1.cir` |
| NDMOS120 | `cjo_per_cell` | 33 | fF | 21 – 188.7 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_cap_0p1.cir` |
| NDMOS120 | `gm_over_id_ceiling` | 24.84 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_subth.cir` |
| NDMOS120 | `idsat_density` | 0.2918 | mA/um | 0.2 – 0.4 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_idsat.cir` |
| NDMOS120 | `rd_tempco` | 1.014e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_ron_150.cir` |
| NDMOS120 | `ron_times_w` | 2.62e+04 | Ohm.um | 1.188e+04 – 4.752e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_ron_27.cir` |
| NDMOS120 | `rsp_specific_ron` | 3.93 | mOhm.cm^2 | 1.782 – 8.909 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_ron_27.cir` |
| NDMOS120 | `sigma_vth_1sigma_at_wref` | 9.814 | mV | 6 – 16 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/NDMOS120_mc_s0.cir` |
| NDMOS120 | `subthreshold_swing` | 96.06 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_subth.cir` |
| NDMOS120 | `vto_tempco` | -2.369 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_vth_150.cir` |
| NDMOS20 | `idsat_density` | 0.5903 | mA/um | 0.2 – 0.4 | warn | 1.97× | `pdk_validation/characterization/decks/vdmos/NDMOS20_idsat.cir` |
| NDMOS20 | `body_diode_tt` | 1.800e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_card.cir` |
| NDMOS20 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_rcond.cir` |
| NDMOS20 | `bv_corner_FF` | 23.24 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_bv_FF.cir` |
| NDMOS20 | `bv_corner_FS` | 23.24 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_bv_FS.cir` |
| NDMOS20 | `bv_corner_SF` | 24.44 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_bv_SF.cir` |
| NDMOS20 | `bv_corner_SS` | 24.44 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_bv_SS.cir` |
| NDMOS20 | `vth_lin` | 0.9949 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_idvg.cir` |
| NDMOS20 | `bv` | 23.84 | V | 22.1 – 26.4 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_bv_TT.cir` |
| NDMOS20 | `cgdmax_per_cell` | 18.57 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_cap_0p1.cir` |
| NDMOS20 | `cgdmin_per_cell` | 7.754 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_cap_21p6.cir` |
| NDMOS20 | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_cap_0p1.cir` |
| NDMOS20 | `cjo_per_cell` | 132 | fF | 14.2 – 174 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_cap_0p1.cir` |
| NDMOS20 | `gm_over_id_ceiling` | 26.69 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_subth.cir` |
| NDMOS20 | `rd_tempco` | 1.167e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_ron_150.cir` |
| NDMOS20 | `ron_times_w` | 8279 | Ohm.um | 3099 – 1.24e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_ron_27.cir` |
| NDMOS20 | `rsp_specific_ron` | 0.414 | mOhm.cm^2 | 0.1549 – 0.7747 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_ron_27.cir` |
| NDMOS20 | `sigma_vth_1sigma_at_wref` | 7.82 | mV | 4.8 – 12.8 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/NDMOS20_mc_s0.cir` |
| NDMOS20 | `subthreshold_swing` | 92.87 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_subth.cir` |
| NDMOS20 | `theta` | 0.3787 | 1/V | 0.05 – 0.45 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_theta.cir` |
| NDMOS20 | `vto_tempco` | -2.011 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_vth_150.cir` |
| NDMOS200 | `theta` | 1.048 | 1/V | 0.05 – 0.3 | **hard-fail** | 6.99× | `pdk_validation/characterization/decks/vdmos/NDMOS200_theta.cir` |
| NDMOS200 | `body_diode_tt` | 1.300e-07 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_card.cir` |
| NDMOS200 | `l_drift_for_bv` | 11.25 | um | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_bv_L8u.cir` |
| NDMOS200 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_rcond.cir` |
| NDMOS200 | `bv_corner_FF` | 211.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_bv_FF.cir` |
| NDMOS200 | `bv_corner_FS` | 211.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_bv_FS.cir` |
| NDMOS200 | `bv_corner_SF` | 238.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_bv_SF.cir` |
| NDMOS200 | `bv_corner_SS` | 238.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_bv_SS.cir` |
| NDMOS200 | `cap_reconciliation_ndmos200` | 0 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_recon_repro1_fixed.cir` |
| NDMOS200 | `vth_lin` | 1.186 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_idvg.cir` |
| NDMOS200 | `bv` | 224.9 | V | 207 – 247.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_bv_TT.cir` |
| NDMOS200 | `cgdmax_per_cell` | 18.64 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_cap_0p1.cir` |
| NDMOS200 | `cgdmin_per_cell` | 6.815 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_cap_202p5.cir` |
| NDMOS200 | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_cap_0p1.cir` |
| NDMOS200 | `cjo_per_cell` | 20.74 | fF | 20.4 – 249.9 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_cap_0p1.cir` |
| NDMOS200 | `gm_over_id_ceiling` | 25 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_subth.cir` |
| NDMOS200 | `idsat_density` | 0.2175 | mA/um | 0.2 – 0.4 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_idsat.cir` |
| NDMOS200 | `rd_tempco` | 1.071e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_ron_150.cir` |
| NDMOS200 | `ron_times_w` | 3.764e+04 | Ohm.um | 1.742e+04 – 6.97e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_ron_27.cir` |
| NDMOS200 | `rsp_specific_ron` | 8.282 | mOhm.cm^2 | 3.834 – 19.17 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_ron_27.cir` |
| NDMOS200 | `sigma_vth_1sigma_at_wref` | 11.01 | mV | 6.6 – 17.6 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/NDMOS200_mc_s0.cir` |
| NDMOS200 | `subthreshold_swing` | 98.35 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_subth.cir` |
| NDMOS200 | `vto_tempco` | -2.693 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_vth_150.cir` |
| NDMOS40 | `theta` | 0.4898 | 1/V | 0.05 – 0.45 | **hard-fail** | 3.27× | `pdk_validation/characterization/decks/vdmos/NDMOS40_theta.cir` |
| NDMOS40 | `idsat_density` | 0.4719 | mA/um | 0.2 – 0.4 | warn | 1.57× | `pdk_validation/characterization/decks/vdmos/NDMOS40_idsat.cir` |
| NDMOS40 | `body_diode_tt` | 2.800e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_card.cir` |
| NDMOS40 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_rcond.cir` |
| NDMOS40 | `bv_corner_FF` | 46.41 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_bv_FF.cir` |
| NDMOS40 | `bv_corner_FS` | 46.41 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_bv_FS.cir` |
| NDMOS40 | `bv_corner_SF` | 49.29 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_bv_SF.cir` |
| NDMOS40 | `bv_corner_SS` | 49.29 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_bv_SS.cir` |
| NDMOS40 | `vth_lin` | 1.032 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_idvg.cir` |
| NDMOS40 | `bv` | 47.85 | V | 44.2 – 52.8 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_bv_TT.cir` |
| NDMOS40 | `cgdmax_per_cell` | 18.58 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_cap_0p1.cir` |
| NDMOS40 | `cgdmin_per_cell` | 7.237 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_cap_43p2.cir` |
| NDMOS40 | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_cap_0p1.cir` |
| NDMOS40 | `cjo_per_cell` | 94.28 | fF | 16.4 – 147.6 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_cap_0p1.cir` |
| NDMOS40 | `gm_over_id_ceiling` | 26.26 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_subth.cir` |
| NDMOS40 | `rd_tempco` | 1.017e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_ron_150.cir` |
| NDMOS40 | `ron_times_w` | 1.256e+04 | Ohm.um | 5211 – 2.085e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_ron_27.cir` |
| NDMOS40 | `rsp_specific_ron` | 0.8795 | mOhm.cm^2 | 0.3648 – 1.824 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_ron_27.cir` |
| NDMOS40 | `sigma_vth_1sigma_at_wref` | 8.73 | mV | 5.1 – 13.6 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/NDMOS40_mc_s0.cir` |
| NDMOS40 | `subthreshold_swing` | 92.99 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_subth.cir` |
| NDMOS40 | `vto_tempco` | -2.148 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_vth_150.cir` |
| NDMOS60 | `theta` | 0.5736 | 1/V | 0.05 – 0.45 | **hard-fail** | 3.82× | `pdk_validation/characterization/decks/vdmos/NDMOS60_theta.cir` |
| NDMOS60 | `idsat_density` | 0.4054 | mA/um | 0.2 – 0.4 | warn | 1.35× | `pdk_validation/characterization/decks/vdmos/NDMOS60_idsat.cir` |
| NDMOS60 | `body_diode_tt` | 4.000e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_card.cir` |
| NDMOS60 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_rcond.cir` |
| NDMOS60 | `bv_corner_FF` | 72.23 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_bv_FF.cir` |
| NDMOS60 | `bv_corner_FS` | 72.23 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_bv_FS.cir` |
| NDMOS60 | `bv_corner_SF` | 77.48 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_bv_SF.cir` |
| NDMOS60 | `bv_corner_SS` | 77.48 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_bv_SS.cir` |
| NDMOS60 | `vth_lin` | 1.072 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_idvg.cir` |
| NDMOS60 | `bv` | 74.86 | V | 69 – 82.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_bv_TT.cir` |
| NDMOS60 | `cgdmax_per_cell` | 18.6 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_cap_0p1.cir` |
| NDMOS60 | `cgdmin_per_cell` | 7.05 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_cap_67p5.cir` |
| NDMOS60 | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_cap_0p1.cir` |
| NDMOS60 | `cjo_per_cell` | 70.71 | fF | 16.9 – 151.8 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_cap_0p1.cir` |
| NDMOS60 | `gm_over_id_ceiling` | 25.85 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_subth.cir` |
| NDMOS60 | `rd_tempco` | 1.002e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_ron_150.cir` |
| NDMOS60 | `ron_times_w` | 1.627e+04 | Ohm.um | 7064 – 2.825e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_ron_27.cir` |
| NDMOS60 | `rsp_specific_ron` | 1.465 | mOhm.cm^2 | 0.6357 – 3.179 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_ron_27.cir` |
| NDMOS60 | `sigma_vth_1sigma_at_wref` | 8.719 | mV | 5.4 – 14.4 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/NDMOS60_mc_s0.cir` |
| NDMOS60 | `subthreshold_swing` | 93.31 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_subth.cir` |
| NDMOS60 | `vto_tempco` | -2.205 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_vth_150.cir` |
| NDMOS80 | `theta` | 0.6506 | 1/V | 0.05 – 0.45 | **hard-fail** | 4.34× | `pdk_validation/characterization/decks/vdmos/NDMOS80_theta.cir` |
| NDMOS80 | `body_diode_tt` | 5.500e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_card.cir` |
| NDMOS80 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_rcond.cir` |
| NDMOS80 | `bv_corner_FF` | 91.06 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_bv_FF.cir` |
| NDMOS80 | `bv_corner_FS` | 91.06 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_bv_FS.cir` |
| NDMOS80 | `bv_corner_SF` | 98.66 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_bv_SF.cir` |
| NDMOS80 | `bv_corner_SS` | 98.66 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_bv_SS.cir` |
| NDMOS80 | `vth_lin` | 1.114 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_idvg.cir` |
| NDMOS80 | `bv` | 94.86 | V | 87.4 – 104.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_bv_TT.cir` |
| NDMOS80 | `cgdmax_per_cell` | 18.61 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_cap_0p1.cir` |
| NDMOS80 | `cgdmin_per_cell` | 6.989 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_cap_85p5.cir` |
| NDMOS80 | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_cap_0p1.cir` |
| NDMOS80 | `cjo_per_cell` | 51.85 | fF | 18.3 – 165 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_cap_0p1.cir` |
| NDMOS80 | `gm_over_id_ceiling` | 25.33 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_subth.cir` |
| NDMOS80 | `idsat_density` | 0.3571 | mA/um | 0.2 – 0.4 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_idsat.cir` |
| NDMOS80 | `rd_tempco` | 9656 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_ron_150.cir` |
| NDMOS80 | `ron_times_w` | 1.979e+04 | Ohm.um | 8764 – 3.506e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_ron_27.cir` |
| NDMOS80 | `rsp_specific_ron` | 2.177 | mOhm.cm^2 | 0.9641 – 4.821 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_ron_27.cir` |
| NDMOS80 | `sigma_vth_1sigma_at_wref` | 10.23 | mV | 5.7 – 15.2 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/NDMOS80_mc_s0.cir` |
| NDMOS80 | `subthreshold_swing` | 94.83 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_subth.cir` |
| NDMOS80 | `vto_tempco` | -2.291 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_vth_150.cir` |
| PDMOS120 | `theta` | 0.3353 | 1/V | 0.05 – 0.3 | **hard-fail** | 2.24× | `pdk_validation/characterization/decks/vdmos/PDMOS120_theta.cir` |
| PDMOS120 | `idsat_density` | 0.1921 | mA/um | 0.2 – 0.4 | warn | 0.64× | `pdk_validation/characterization/decks/vdmos/PDMOS120_idsat.cir` |
| PDMOS120 | `body_diode_tt` | 9.500e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_card.cir` |
| PDMOS120 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_rcond.cir` |
| PDMOS120 | `bv_corner_FF` | 122.8 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_bv_FF.cir` |
| PDMOS120 | `bv_corner_FS` | 133 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_bv_FS.cir` |
| PDMOS120 | `bv_corner_SF` | 122.8 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_bv_SF.cir` |
| PDMOS120 | `bv_corner_SS` | 133 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_bv_SS.cir` |
| PDMOS120 | `vth_lin` | -1.229 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_idvg.cir` |
| PDMOS120 | `bv` | 127.9 | V | 117.8 – 140.8 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_bv_TT.cir` |
| PDMOS120 | `cgdmax_per_cell` | 18.64 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_cap_0p1.cir` |
| PDMOS120 | `cgdmin_per_cell` | 6.939 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_cap_115p2.cir` |
| PDMOS120 | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_cap_0p1.cir` |
| PDMOS120 | `cjo_per_cell` | 27.34 | fF | 21.5 – 193.8 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_cap_0p1.cir` |
| PDMOS120 | `gm_over_id_ceiling` | 24.68 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_subth.cir` |
| PDMOS120 | `rd_tempco` | 1.705e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_ron_150.cir` |
| PDMOS120 | `ron_times_w` | 3.209e+04 | Ohm.um | 1.188e+04 – 4.752e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_ron_27.cir` |
| PDMOS120 | `rsp_specific_ron` | 4.814 | mOhm.cm^2 | 1.782 – 8.909 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_ron_27.cir` |
| PDMOS120 | `sigma_vth_1sigma_at_wref` | 9.653 | mV | 6 – 16 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/PDMOS120_mc_s0.cir` |
| PDMOS120 | `subthreshold_swing` | 97.71 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_subth.cir` |
| PDMOS120 | `vto_tempco` | -2.52 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_vth_150.cir` |
| PDMOS20 | `body_diode_tt` | 2.200e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_card.cir` |
| PDMOS20 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_rcond.cir` |
| PDMOS20 | `bv_corner_FF` | 21.27 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_bv_FF.cir` |
| PDMOS20 | `bv_corner_FS` | 22.37 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_bv_FS.cir` |
| PDMOS20 | `bv_corner_SF` | 21.27 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_bv_SF.cir` |
| PDMOS20 | `bv_corner_SS` | 22.37 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_bv_SS.cir` |
| PDMOS20 | `vth_lin` | -1.059 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_idvg.cir` |
| PDMOS20 | `bv` | 21.82 | V | 20.2 – 24.2 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_bv_TT.cir` |
| PDMOS20 | `cgdmax_per_cell` | 18.58 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_cap_0p1.cir` |
| PDMOS20 | `cgdmin_per_cell` | 7.933 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_cap_19p8.cir` |
| PDMOS20 | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_cap_0p1.cir` |
| PDMOS20 | `cjo_per_cell` | 141.4 | fF | 14.8 – 181.7 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_cap_0p1.cir` |
| PDMOS20 | `gm_over_id_ceiling` | 26.29 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_subth.cir` |
| PDMOS20 | `idsat_density` | 0.2639 | mA/um | 0.2 – 0.4 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_idsat.cir` |
| PDMOS20 | `rd_tempco` | 1.97e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_ron_150.cir` |
| PDMOS20 | `ron_times_w` | 1.386e+04 | Ohm.um | 2000 – 1.5e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_ron_27.cir` |
| PDMOS20 | `rsp_specific_ron` | 0.6932 | mOhm.cm^2 | 0.1549 – 0.7747 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_ron_27.cir` |
| PDMOS20 | `sigma_vth_1sigma_at_wref` | 7.665 | mV | 4.8 – 12.8 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/PDMOS20_mc_s0.cir` |
| PDMOS20 | `subthreshold_swing` | 96.1 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_subth.cir` |
| PDMOS20 | `theta` | 0.2159 | 1/V | 0.05 – 0.45 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_theta.cir` |
| PDMOS20 | `vto_tempco` | -1.61 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_vth_150.cir` |
| PDMOS200 | `cjo_per_cell` | 16.97 | fF | 20.2 – 247.1 | **hard-fail** | 0.24× | `pdk_validation/characterization/decks/vdmos/PDMOS200_cap_0p1.cir` |
| PDMOS200 | `theta` | 0.4346 | 1/V | 0.05 – 0.3 | **hard-fail** | 2.9× | `pdk_validation/characterization/decks/vdmos/PDMOS200_theta.cir` |
| PDMOS200 | `idsat_density` | 0.1576 | mA/um | 0.2 – 0.4 | warn | 0.525× | `pdk_validation/characterization/decks/vdmos/PDMOS200_idsat.cir` |
| PDMOS200 | `subthreshold_swing` | 100.2 | mV/dec | 72 – 100 | warn | 1.18× | `pdk_validation/characterization/decks/vdmos/PDMOS200_subth.cir` |
| PDMOS200 | `body_diode_tt` | 1.550e-07 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_card.cir` |
| PDMOS200 | `l_drift_for_bv` | 11.5 | um | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_bv_L8u.cir` |
| PDMOS200 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_rcond.cir` |
| PDMOS200 | `bv_corner_FF` | 216.1 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_bv_FF.cir` |
| PDMOS200 | `bv_corner_FS` | 243.7 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_bv_FS.cir` |
| PDMOS200 | `bv_corner_SF` | 216.1 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_bv_SF.cir` |
| PDMOS200 | `bv_corner_SS` | 243.7 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_bv_SS.cir` |
| PDMOS200 | `vth_lin` | -1.278 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_idvg.cir` |
| PDMOS200 | `bv` | 229.9 | V | 211.6 – 253 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_bv_TT.cir` |
| PDMOS200 | `cgdmax_per_cell` | 18.65 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_cap_0p1.cir` |
| PDMOS200 | `cgdmin_per_cell` | 6.819 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_cap_207.cir` |
| PDMOS200 | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_cap_0p1.cir` |
| PDMOS200 | `gm_over_id_ceiling` | 25 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_subth.cir` |
| PDMOS200 | `rd_tempco` | 1.672e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_ron_150.cir` |
| PDMOS200 | `ron_times_w` | 4.409e+04 | Ohm.um | 1.742e+04 – 6.97e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_ron_27.cir` |
| PDMOS200 | `rsp_specific_ron` | 9.699 | mOhm.cm^2 | 3.834 – 19.17 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_ron_27.cir` |
| PDMOS200 | `sigma_vth_1sigma_at_wref` | 10.9 | mV | 6.6 – 17.6 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/PDMOS200_mc_s0.cir` |
| PDMOS200 | `vto_tempco` | -2.78 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_vth_150.cir` |
| PDMOS40 | `body_diode_tt` | 3.500e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_card.cir` |
| PDMOS40 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_rcond.cir` |
| PDMOS40 | `bv_corner_FF` | 43.48 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_bv_FF.cir` |
| PDMOS40 | `bv_corner_FS` | 46.18 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_bv_FS.cir` |
| PDMOS40 | `bv_corner_SF` | 43.48 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_bv_SF.cir` |
| PDMOS40 | `bv_corner_SS` | 46.18 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_bv_SS.cir` |
| PDMOS40 | `vth_lin` | -1.102 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_idvg.cir` |
| PDMOS40 | `bv` | 44.83 | V | 41.4 – 49.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_bv_TT.cir` |
| PDMOS40 | `cgdmax_per_cell` | 18.59 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_cap_0p1.cir` |
| PDMOS40 | `cgdmin_per_cell` | 7.31 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_cap_40p5.cir` |
| PDMOS40 | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_cap_0p1.cir` |
| PDMOS40 | `cjo_per_cell` | 99 | fF | 16.9 – 152.4 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_cap_0p1.cir` |
| PDMOS40 | `gm_over_id_ceiling` | 25.95 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_subth.cir` |
| PDMOS40 | `idsat_density` | 0.2445 | mA/um | 0.2 – 0.4 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_idsat.cir` |
| PDMOS40 | `rd_tempco` | 1.817e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_ron_150.cir` |
| PDMOS40 | `ron_times_w` | 1.738e+04 | Ohm.um | 5211 – 2.085e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_ron_27.cir` |
| PDMOS40 | `rsp_specific_ron` | 1.217 | mOhm.cm^2 | 0.3648 – 1.824 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_ron_27.cir` |
| PDMOS40 | `sigma_vth_1sigma_at_wref` | 8.199 | mV | 5.1 – 13.6 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/PDMOS40_mc_s0.cir` |
| PDMOS40 | `subthreshold_swing` | 95.92 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_subth.cir` |
| PDMOS40 | `theta` | 0.2386 | 1/V | 0.05 – 0.45 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_theta.cir` |
| PDMOS40 | `vto_tempco` | -2.048 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_vth_150.cir` |
| PDMOS60 | `body_diode_tt` | 5.000e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_card.cir` |
| PDMOS60 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_rcond.cir` |
| PDMOS60 | `bv_corner_FF` | 67.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_bv_FF.cir` |
| PDMOS60 | `bv_corner_FS` | 72.3 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_bv_FS.cir` |
| PDMOS60 | `bv_corner_SF` | 67.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_bv_SF.cir` |
| PDMOS60 | `bv_corner_SS` | 72.3 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_bv_SS.cir` |
| PDMOS60 | `vth_lin` | -1.145 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_idvg.cir` |
| PDMOS60 | `bv` | 69.85 | V | 64.4 – 77 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_bv_TT.cir` |
| PDMOS60 | `cgdmax_per_cell` | 18.61 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_cap_0p1.cir` |
| PDMOS60 | `cgdmin_per_cell` | 7.113 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_cap_63.cir` |
| PDMOS60 | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_cap_0p1.cir` |
| PDMOS60 | `cjo_per_cell` | 61.28 | fF | 17.5 – 157.2 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_cap_0p1.cir` |
| PDMOS60 | `gm_over_id_ceiling` | 25.63 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_subth.cir` |
| PDMOS60 | `idsat_density` | 0.2286 | mA/um | 0.2 – 0.4 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_idsat.cir` |
| PDMOS60 | `rd_tempco` | 1.803e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_ron_150.cir` |
| PDMOS60 | `ron_times_w` | 2.137e+04 | Ohm.um | 7064 – 2.825e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_ron_27.cir` |
| PDMOS60 | `rsp_specific_ron` | 1.923 | mOhm.cm^2 | 0.6357 – 3.179 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_ron_27.cir` |
| PDMOS60 | `sigma_vth_1sigma_at_wref` | 8.582 | mV | 5.4 – 14.4 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/PDMOS60_mc_s0.cir` |
| PDMOS60 | `subthreshold_swing` | 95.3 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_subth.cir` |
| PDMOS60 | `theta` | 0.2616 | 1/V | 0.05 – 0.45 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_theta.cir` |
| PDMOS60 | `vto_tempco` | -2.234 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_vth_150.cir` |
| PDMOS80 | `body_diode_tt` | 6.500e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_card.cir` |
| PDMOS80 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_rcond.cir` |
| PDMOS80 | `bv_corner_FF` | 86.26 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_bv_FF.cir` |
| PDMOS80 | `bv_corner_FS` | 93.46 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_bv_FS.cir` |
| PDMOS80 | `bv_corner_SF` | 86.26 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_bv_SF.cir` |
| PDMOS80 | `bv_corner_SS` | 93.46 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_bv_SS.cir` |
| PDMOS80 | `vth_lin` | -1.188 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_idvg.cir` |
| PDMOS80 | `bv` | 89.86 | V | 82.8 – 99 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_bv_TT.cir` |
| PDMOS80 | `cgdmax_per_cell` | 18.62 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_cap_0p1.cir` |
| PDMOS80 | `cgdmin_per_cell` | 7.031 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_cap_81.cir` |
| PDMOS80 | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_cap_0p1.cir` |
| PDMOS80 | `cjo_per_cell` | 42.43 | fF | 18.8 – 169.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_cap_0p1.cir` |
| PDMOS80 | `gm_over_id_ceiling` | 25.14 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_subth.cir` |
| PDMOS80 | `idsat_density` | 0.2136 | mA/um | 0.2 – 0.4 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_idsat.cir` |
| PDMOS80 | `rd_tempco` | 1.673e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_ron_150.cir` |
| PDMOS80 | `ron_times_w` | 2.518e+04 | Ohm.um | 8764 – 3.506e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_ron_27.cir` |
| PDMOS80 | `rsp_specific_ron` | 2.77 | mOhm.cm^2 | 0.9641 – 4.821 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_ron_27.cir` |
| PDMOS80 | `sigma_vth_1sigma_at_wref` | 9.089 | mV | 5.7 – 15.2 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/PDMOS80_mc_s0.cir` |
| PDMOS80 | `subthreshold_swing` | 96.6 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_subth.cir` |
| PDMOS80 | `theta` | 0.289 | 1/V | 0.05 – 0.45 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_theta.cir` |
| PDMOS80 | `vto_tempco` | -2.373 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_vth_150.cir` |

## BJT

| device | FoM | measured | units | band | status | ×target | deck |
|---|---|---|---|---|---|---|---|
| NPN_HV | `bvcbo` | 37.84 | V | 40.5 – 49.5 | **hard-fail** | 0.841× | `pdk_validation/characterization/decks/bjt/NPN_HV_bvcbo.cir` |
| NPN_HV | `bvceo_implied` | 24.83 | V | 11.25 – 22.5 | **hard-fail** | 1.65× | `pdk_validation/characterization/decks/bjt/NPN_HV_bvceo.cir` |
| NPN_HV | `beta_corner_spread` | 17.19 | percent | 20 – 30 | warn | 0.688× | `pdk_validation/characterization/decks/bjt/NPN_HV_gummel_TT.cir` |
| NPN_HV | `flicker_corner` | 0.3119 | Hz | 100 – 1e+04 | warn | 0.000104× | `pdk_validation/characterization/decks/bjt/NPN_HV_noise_100uA.cir` |
| NPN_HV | `is_corner_spread` | 3.085 | mV | 10 – 30 | warn | 0.154× | `pdk_validation/characterization/decks/bjt/NPN_HV_gummel_TT.cir` |
| NPN_HV | `ft_at_peak` | 1.605 | GHz | 0.5 – 2 | descriptive <br>_anchor band contested (BCD junction BJT vs SiGe-class) -- open maintainer decision_ |  | `pdk_validation/characterization/decks/bjt/NPN_HV_ft.cir` |
| NPN_HV | `flicker_corner_bias_ratio` | 0.2212 |  | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/NPN_HV_noise_100uA.cir` |
| NPN_HV | `is_extracted` | 4.013e-17 | A | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/NPN_HV_gummel_TT.cir` |
| NPN_HV | `n_ideality` | 1.001 |  | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/NPN_HV_gummel_TT.cir` |
| NPN_HV | `beta` | 62.46 |  | 48 – 128 | pass |  | `pdk_validation/characterization/decks/bjt/NPN_HV_gummel_TT.cir` |
| NPN_HV | `early_voltage` | 117.7 | V | 60 – 240 | pass |  | `pdk_validation/characterization/decks/bjt/NPN_HV_early.cir` |
| NPN_HV | `ft_times_bvceo_johnson` | 39.85 | GHz.V | 0 – 200 | pass |  | `pdk_validation/characterization/decks/bjt/NPN_HV_ft.cir` |
| NPN_HV | `vbe_at_100uA` | 0.7392 | V | 0.62 – 0.78 | pass |  | `pdk_validation/characterization/decks/bjt/NPN_HV_gummel_TT.cir` |
| NPN_LV | `bvcbo` | 11.77 | V | 12.6 – 15.4 | **hard-fail** | 0.841× | `pdk_validation/characterization/decks/bjt/NPN_LV_bvcbo.cir` |
| NPN_LV | `bvceo_implied` | 7.465 | V | 3.5 – 7 | **hard-fail** | 1.83× | `pdk_validation/characterization/decks/bjt/NPN_LV_bvceo.cir` |
| NPN_LV | `beta_corner_spread` | 17.81 | percent | 20 – 30 | warn | 0.713× | `pdk_validation/characterization/decks/bjt/NPN_LV_gummel_TT.cir` |
| NPN_LV | `flicker_corner` | 0.2099 | Hz | 100 – 1e+04 | warn | 7e-05× | `pdk_validation/characterization/decks/bjt/NPN_LV_noise_100uA.cir` |
| NPN_LV | `is_corner_spread` | 2.994 | mV | 10 – 30 | warn | 0.15× | `pdk_validation/characterization/decks/bjt/NPN_LV_gummel_TT.cir` |
| NPN_LV | `ft_at_peak` | 3.089 | GHz | 0.5 – 2 | descriptive <br>_anchor band contested (BCD junction BJT vs SiGe-class) -- open maintainer decision_ |  | `pdk_validation/characterization/decks/bjt/NPN_LV_ft.cir` |
| NPN_LV | `flicker_corner_bias_ratio` | 0.1712 |  | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/NPN_LV_noise_100uA.cir` |
| NPN_LV | `is_extracted` | 2.007e-16 | A | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/NPN_LV_gummel_TT.cir` |
| NPN_LV | `n_ideality` | 1.001 |  | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/NPN_LV_gummel_TT.cir` |
| NPN_LV | `beta` | 113 |  | 84 – 224 | pass |  | `pdk_validation/characterization/decks/bjt/NPN_LV_gummel_TT.cir` |
| NPN_LV | `early_voltage` | 72.88 | V | 50 – 120 | pass |  | `pdk_validation/characterization/decks/bjt/NPN_LV_early.cir` |
| NPN_LV | `ft_times_bvceo_johnson` | 23.06 | GHz.V | 0 – 200 | pass |  | `pdk_validation/characterization/decks/bjt/NPN_LV_ft.cir` |
| NPN_LV | `vbe_at_100uA` | 0.6978 | V | 0.62 – 0.78 | pass |  | `pdk_validation/characterization/decks/bjt/NPN_LV_gummel_TT.cir` |
| PNP_HV | `beta_corner_spread` | 19.38 | percent | 20 – 30 | warn | 0.775× | `pdk_validation/characterization/decks/bjt/PNP_HV_gummel_TT.cir` |
| PNP_HV | `flicker_corner` | 0.6487 | Hz | 100 – 1e+04 | warn | 0.000216× | `pdk_validation/characterization/decks/bjt/PNP_HV_noise_100uA.cir` |
| PNP_HV | `is_corner_spread` | 3.705 | mV | 10 – 30 | warn | 0.185× | `pdk_validation/characterization/decks/bjt/PNP_HV_gummel_TT.cir` |
| PNP_HV | `ft_at_peak` | 0.5805 | GHz | 0.5 – 2 | descriptive <br>_anchor band contested (BCD junction BJT vs SiGe-class) -- open maintainer decision_ |  | `pdk_validation/characterization/decks/bjt/PNP_HV_ft.cir` |
| PNP_HV | `bvcbo` | -- | V | 28.8 – 35.2 | error |  | `pdk_validation/characterization/decks/bjt/PNP_HV_bvcbo.cir` |
| PNP_HV | `bvceo_implied` | -- | V | 8 – 16 | error |  | `pdk_validation/characterization/decks/bjt/PNP_HV_bvceo.cir` |
| PNP_HV | `ft_times_bvceo_johnson` | -- | GHz.V | 0 – 200 | error |  | `pdk_validation/characterization/decks/bjt/PNP_HV_ft.cir` |
| PNP_HV | `flicker_corner_bias_ratio` | 0.1843 |  | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/PNP_HV_noise_100uA.cir` |
| PNP_HV | `is_extracted` | 1.004e-16 | A | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/PNP_HV_gummel_TT.cir` |
| PNP_HV | `n_ideality` | 1.032 |  | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/PNP_HV_gummel_TT.cir` |
| PNP_HV | `beta` | 16.31 |  | 11 – 29 | pass |  | `pdk_validation/characterization/decks/bjt/PNP_HV_gummel_TT.cir` |
| PNP_HV | `early_voltage` | 47.26 | V | 25 – 100 | pass |  | `pdk_validation/characterization/decks/bjt/PNP_HV_early.cir` |
| PNP_HV | `vbe_at_100uA` | 0.7386 | V | 0.62 – 0.78 | pass |  | `pdk_validation/characterization/decks/bjt/PNP_HV_gummel_TT.cir` |
| PNP_LAT | `beta_corner_spread` | 19.22 | percent | 20 – 30 | warn | 0.769× | `pdk_validation/characterization/decks/bjt/PNP_LAT_gummel_TT.cir` |
| PNP_LAT | `flicker_corner` | 0.429 | Hz | 100 – 1e+04 | warn | 0.000143× | `pdk_validation/characterization/decks/bjt/PNP_LAT_noise_100uA.cir` |
| PNP_LAT | `is_corner_spread` | 3.325 | mV | 10 – 30 | warn | 0.166× | `pdk_validation/characterization/decks/bjt/PNP_LAT_gummel_TT.cir` |
| PNP_LAT | `ft_at_peak` | 0.7614 | GHz | 0.5 – 2 | descriptive <br>_anchor band contested (BCD junction BJT vs SiGe-class) -- open maintainer decision_ |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_ft.cir` |
| PNP_LAT | `bvcbo` | -- | V | 16.2 – 19.8 | error |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_bvcbo.cir` |
| PNP_LAT | `bvceo_implied` | -- | V | 4.5 – 9 | error |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_bvceo.cir` |
| PNP_LAT | `ft_times_bvceo_johnson` | -- | GHz.V | 0 – 200 | error |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_ft.cir` |
| PNP_LAT | `flicker_corner_bias_ratio` | 0.1385 |  | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_noise_100uA.cir` |
| PNP_LAT | `is_extracted` | 8.021e-16 | A | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_gummel_TT.cir` |
| PNP_LAT | `n_ideality` | 1.023 |  | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_gummel_TT.cir` |
| PNP_LAT | `beta` | 30.68 |  | 21 – 56 | pass |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_gummel_TT.cir` |
| PNP_LAT | `early_voltage` | 32.52 | V | 18 – 70 | pass |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_early.cir` |
| PNP_LAT | `vbe_at_100uA` | 0.6765 | V | 0.62 – 0.78 | pass |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_gummel_TT.cir` |

## Diodes/zeners

| device | FoM | measured | units | band | status | ×target | deck |
|---|---|---|---|---|---|---|---|
| DIO_FAST | `cjo_density` | 180 | fF/um^2 | 0.5 – 2 | warn | 180× | `pdk_validation/characterization/decks/diodes/DIO_FAST_cjo.cir` |
| DIO_FAST | `bv` | 79.91 | V | 68 – 92 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_FAST_rev.cir` |
| DIO_FAST | `n_ideality` | 1.031 |  | 0.98 – 1.1 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_FAST_fwd.cir` |
| DIO_FAST | `tt_transit_time` | 2.000e-09 | s | 6.000e-10 – 6.000e-09 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_FAST_diffcap.cir` |
| DIO_FAST | `vf_at_1mA` | 0.5588 | V | 0.474 – 0.642 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_FAST_fwd.cir` |
| DIO_PN | `cjo_density` | 280 | fF/um^2 | 0.5 – 2 | warn | 280× | `pdk_validation/characterization/decks/diodes/DIO_PN_cjo.cir` |
| DIO_PN | `bv` | 99.93 | V | 85 – 115 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_PN_rev.cir` |
| DIO_PN | `n_ideality` | 1.051 |  | 1 – 1.12 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_PN_fwd.cir` |
| DIO_PN | `tt_transit_time` | 5.996e-09 | s | 1.800e-09 – 1.800e-08 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_PN_diffcap.cir` |
| DIO_PN | `vf_at_1mA` | 0.6702 | V | 0.569 – 0.769 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_PN_fwd.cir` |
| DIO_SCH | `tt_transit_time` | 3.019e-10 | s | 0 – 1.000e-12 | **hard-fail** |  | `pdk_validation/characterization/decks/diodes/DIO_SCH_diffcap.cir` |
| DIO_SCH | `cjo_density` | 140.3 | fF/um^2 | 0.5 – 2 | warn | 140× | `pdk_validation/characterization/decks/diodes/DIO_SCH_cjo.cir` |
| DIO_SCH | `qrr_at_10mA` | 3.019e-12 | C | -- | no-anchor |  | `pdk_validation/characterization/decks/diodes/DIO_SCH_diffcap.cir` |
| DIO_SCH | `bv` | 45.1 | V | 38.2 – 51.7 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_SCH_rev.cir` |
| DIO_SCH | `n_ideality` | 1.075 |  | 1.03 – 1.15 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_SCH_fwd.cir` |
| DIO_SCH | `vf_at_1mA` | 0.2914 | V | 0.247 – 0.335 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_SCH_fwd.cir` |
| DZ_12 | `cjo_density` | 5.5e+04 | fF/um^2 | 0.515 – 2.062 | **hard-fail** | 5.33e+04× | `pdk_validation/characterization/decks/diodes/DZ_12_cjo.cir` |
| DZ_12 | `bv_tempco` | -0.8814 | mV/degC | 4 – 12.8 | warn | -0.11× | `pdk_validation/characterization/decks/diodes/DZ_12_rev_150C.cir` |
| DZ_12 | `bv` | 11.73 | V | 11.4 – 12.6 | pass |  | `pdk_validation/characterization/decks/diodes/DZ_12_rev_27C.cir` |
| DZ_12 | `tt_transit_time` | 5.518e-08 | s | 1.000e-08 – 1.000e-07 | pass |  | `pdk_validation/characterization/decks/diodes/DZ_12_diffcap.cir` |
| DZ_24 | `cjo_density` | 2.8e+04 | fF/um^2 | 0.509 – 2.038 | **hard-fail** | 2.75e+04× | `pdk_validation/characterization/decks/diodes/DZ_24_cjo.cir` |
| DZ_24 | `bv_tempco` | -0.7309 | mV/degC | 10 – 32 | warn | -0.0365× | `pdk_validation/characterization/decks/diodes/DZ_24_rev_150C.cir` |
| DZ_24 | `bv` | 23.77 | V | 22.8 – 25.2 | pass |  | `pdk_validation/characterization/decks/diodes/DZ_24_rev_27C.cir` |
| DZ_24 | `tt_transit_time` | 7.492e-08 | s | 1.000e-08 – 1.000e-07 | pass |  | `pdk_validation/characterization/decks/diodes/DZ_24_diffcap.cir` |
| DZ_5V6 | `bv` | 5.243 | V | 5.32 – 5.88 | **hard-fail** | 0.936× | `pdk_validation/characterization/decks/diodes/DZ_5V6_rev_27C.cir` |
| DZ_5V6 | `cjo_density` | 1.200e+05 | fF/um^2 | 1.663 – 6.652 | **hard-fail** | 3.61e+04× | `pdk_validation/characterization/decks/diodes/DZ_5V6_cjo.cir` |
| DZ_5V6 | `bv_tempco` | -1.173 | mV/degC | 0.12 – 0.4 | warn | -4.69× | `pdk_validation/characterization/decks/diodes/DZ_5V6_rev_150C.cir` |
| DZ_5V6 | `tt_transit_time` | 4.054e-08 | s | 1.000e-08 – 1.000e-07 | pass |  | `pdk_validation/characterization/decks/diodes/DZ_5V6_diffcap.cir` |

## Passives

| device | FoM | measured | units | band | status | ×target | deck |
|---|---|---|---|---|---|---|---|
| CFRINGE | `golden_crosscheck` | -3.336e-08 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/CFRINGE_cv.cir` |
| CFRINGE | `density` | 0.181 | fF/um^2 | 0.1 – 0.5 | pass |  | `pdk_validation/characterization/decks/passives/CFRINGE_cv.cir` |
| CFRINGE | `implied_dielectric_thickness` | 195.7 | nm | 137.8 – 275.5 | pass |  | `pdk_validation/characterization/decks/passives/CFRINGE_cv.cir` |
| CFRINGE | `matching_A_C_pair_1sigma` | 1.397 | %.um | 0.9 – 2.7 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| CFRINGE | `tcc_tc1` | 16.12 | ppm/degC | 6 – 38 | pass |  | `pdk_validation/characterization/decks/passives/CFRINGE_temp_150.cir` |
| CFRINGE | `vcc1` | 2.982 | ppm/V | 1 – 6 | pass |  | `pdk_validation/characterization/decks/passives/CFRINGE_cv.cir` |
| CMIM_HI | `golden_crosscheck` | -3.295e-10 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/CMIM_HI_cv.cir` |
| CMIM_HI | `density` | 2 | fF/um^2 | 2 – 4 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_HI_cv.cir` |
| CMIM_HI | `implied_dielectric_thickness` | 30.99 | nm | 21.7 – 43.4 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_HI_cv.cir` |
| CMIM_HI | `matching_A_C_pair_1sigma` | 0.7005 | %.um | 0.45 – 1.35 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| CMIM_HI | `tcc_tc1` | 48.36 | ppm/degC | 18 – 112 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_HI_temp_150.cir` |
| CMIM_HI | `vcc1` | 59.97 | ppm/V | 24 – 120 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_HI_cv.cir` |
| CMIM_STD | `golden_crosscheck` | 7.726e-11 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/CMIM_STD_cv.cir` |
| CMIM_STD | `density` | 1 | fF/um^2 | 0.9 – 1.1 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_STD_cv.cir` |
| CMIM_STD | `implied_dielectric_thickness` | 61.98 | nm | 43.4 – 86.8 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_STD_cv.cir` |
| CMIM_STD | `matching_A_C_pair_1sigma` | 0.7377 | %.um | 0.45 – 1.35 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| CMIM_STD | `tcc_tc1` | 37.8 | ppm/degC | 0 – 45 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_STD_temp_150.cir` |
| CMIM_STD | `vcc1` | 29.99 | ppm/V | 0 – 30 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_STD_cv.cir` |
| CMOM | `golden_crosscheck` | -7.136e-08 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/CMOM_cv.cir` |
| CMOM | `density` | 0.35 | fF/um^2 | 0.3 – 1 | pass |  | `pdk_validation/characterization/decks/passives/CMOM_cv.cir` |
| CMOM | `implied_dielectric_thickness` | 101.2 | nm | 70.8 – 141.7 | pass |  | `pdk_validation/characterization/decks/passives/CMOM_cv.cir` |
| CMOM | `matching_A_C_pair_1sigma` | 1.559 | %.um | 0.9 – 2.7 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| CMOM | `tcc_tc1` | 21.68 | ppm/degC | 8 – 50 | pass |  | `pdk_validation/characterization/decks/passives/CMOM_temp_150.cir` |
| CMOM | `vcc1` | 4.998 | ppm/V | 2 – 10 | pass |  | `pdk_validation/characterization/decks/passives/CMOM_cv.cir` |
| RNPLUS | `tc1` | 984 | ppm/degC | 1000 – 2000 | warn | 0.656× | `pdk_validation/characterization/decks/passives/RNPLUS_temp_150.cir` |
| RNPLUS | `golden_crosscheck` | 1.008e-07 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/RNPLUS_rv.cir` |
| RNPLUS | `matching_A_R_pair_1sigma` | 2.68 | %.um | 1.5 – 4.5 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| RNPLUS | `rsh` | 60.01 | Ohm/sq | 50 – 90 | pass |  | `pdk_validation/characterization/decks/passives/RNPLUS_rsh.cir` |
| RNPLUS | `rsh_corner_spread` | 12 | percent | 10 – 25 | pass |  | `pdk_validation/characterization/decks/passives/RNPLUS_corner_TT.cir` |
| RNPLUS | `vcr1` | 1500 | ppm/V | 750 – 3000 | pass |  | `pdk_validation/characterization/decks/passives/RNPLUS_rv.cir` |
| RNWELL | `rsh` | 1801 | Ohm/sq | 1000 – 1600 | warn | 1.5× | `pdk_validation/characterization/decks/passives/RNWELL_rsh.cir` |
| RNWELL | `golden_crosscheck` | -2.155e-08 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/RNWELL_rv.cir` |
| RNWELL | `matching_A_R_pair_1sigma` | 3.931 | %.um | 2.4 – 7.2 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| RNWELL | `rsh_corner_spread` | 12 | percent | 10 – 25 | pass |  | `pdk_validation/characterization/decks/passives/RNWELL_corner_TT.cir` |
| RNWELL | `tc1` | 4280 | ppm/degC | 3000 – 6000 | pass |  | `pdk_validation/characterization/decks/passives/RNWELL_temp_150.cir` |
| RNWELL | `vcr1` | 8000 | ppm/V | 4000 – 1.6e+04 | pass |  | `pdk_validation/characterization/decks/passives/RNWELL_rv.cir` |
| RPOLY_HI | `golden_crosscheck` | -5.146e-08 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/RPOLY_HI_rv.cir` |
| RPOLY_HI | `matching_A_R_pair_1sigma` | 1.616 | %.um | 0.9 – 2.7 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| RPOLY_HI | `rsh` | 1200 | Ohm/sq | 1000 – 2000 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_HI_rsh.cir` |
| RPOLY_HI | `rsh_corner_spread` | 12 | percent | 10 – 25 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_HI_corner_TT.cir` |
| RPOLY_HI | `tc1` | -1344 | ppm/degC | -2000 – -1000 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_HI_temp_150.cir` |
| RPOLY_HI | `vcr1` | 200 | ppm/V | 100 – 400 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_HI_rv.cir` |
| RPOLY_LO | `golden_crosscheck` | -9.247e-08 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/RPOLY_LO_rv.cir` |
| RPOLY_LO | `matching_A_R_pair_1sigma` | 1.532 | %.um | 0.9 – 2.7 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| RPOLY_LO | `rsh` | 300 | Ohm/sq | 200 – 400 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_LO_rsh.cir` |
| RPOLY_LO | `rsh_corner_spread` | 12 | percent | 10 – 25 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_LO_corner_TT.cir` |
| RPOLY_LO | `tc1` | 12 | ppm/degC | -100 – 600 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_LO_temp_150.cir` |
| RPOLY_LO | `vcr1` | 50 | ppm/V | 25 – 100 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_LO_rv.cir` |
| RPPLUS | `golden_crosscheck` | -6.350e-09 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/RPPLUS_rv.cir` |
| RPPLUS | `matching_A_R_pair_1sigma` | 2.641 | %.um | 1.5 – 4.5 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| RPPLUS | `rsh` | 110 | Ohm/sq | 80 – 140 | pass |  | `pdk_validation/characterization/decks/passives/RPPLUS_rsh.cir` |
| RPPLUS | `rsh_corner_spread` | 12 | percent | 10 – 25 | pass |  | `pdk_validation/characterization/decks/passives/RPPLUS_corner_TT.cir` |
| RPPLUS | `tc1` | 1190 | ppm/degC | 1000 – 2500 | pass |  | `pdk_validation/characterization/decks/passives/RPPLUS_temp_150.cir` |
| RPPLUS | `vcr1` | 1800 | ppm/V | 900 – 3600 | pass |  | `pdk_validation/characterization/decks/passives/RPPLUS_rv.cir` |

## Measurement errors (6)

| device | FoM | error |
|---|---|---|
| PNP_LAT | `bvceo_implied` | BVCEO is not measurable: the collector current never leaves the leakage floor (max |I| = 1.03e-11 A) anywhere in the sweep, so there is no breakdown to find. ROOT CAUSE (PDK defect, not a harness failure): the Bavl avalanche branch in the .subckt uses min(max(V(ci,b)/BVCBO,0),0.997) with a POSITIVE BVCBO .param. On a PNP the collector is below the base in normal operation, so V(ci,b) < 0, the max(...,0) clamps the argument to zero, and the multiplication factor is identically 1. The branch is dead code on both PNPs: PNP_LAT and PNP_HV have NO modelled collector breakdown at any voltage. The expression is the NPN one copy-pasted without a sign flip. This is unmeasurable until the wrapper is fixed. |
| PNP_LAT | `bvcbo` | BVCBO is not measurable: the collector current never leaves the leakage floor (max |I| = 1.03e-11 A) anywhere in the sweep, so there is no breakdown to find. ROOT CAUSE (PDK defect, not a harness failure): the Bavl avalanche branch in the .subckt uses min(max(V(ci,b)/BVCBO,0),0.997) with a POSITIVE BVCBO .param. On a PNP the collector is below the base in normal operation, so V(ci,b) < 0, the max(...,0) clamps the argument to zero, and the multiplication factor is identically 1. The branch is dead code on both PNPs: PNP_LAT and PNP_HV have NO modelled collector breakdown at any voltage. The expression is the NPN one copy-pasted without a sign flip. This is unmeasurable until the wrapper is fixed. |
| PNP_LAT | `ft_times_bvceo_johnson` | needs both ft_at_peak and bvceo_implied; ft=761384970.1125875 bvceo=None |
| PNP_HV | `bvceo_implied` | BVCEO is not measurable: the collector current never leaves the leakage floor (max |I| = 1.73e-11 A) anywhere in the sweep, so there is no breakdown to find. ROOT CAUSE (PDK defect, not a harness failure): the Bavl avalanche branch in the .subckt uses min(max(V(ci,b)/BVCBO,0),0.997) with a POSITIVE BVCBO .param. On a PNP the collector is below the base in normal operation, so V(ci,b) < 0, the max(...,0) clamps the argument to zero, and the multiplication factor is identically 1. The branch is dead code on both PNPs: PNP_LAT and PNP_HV have NO modelled collector breakdown at any voltage. The expression is the NPN one copy-pasted without a sign flip. This is unmeasurable until the wrapper is fixed. |
| PNP_HV | `bvcbo` | BVCBO is not measurable: the collector current never leaves the leakage floor (max |I| = 1.73e-11 A) anywhere in the sweep, so there is no breakdown to find. ROOT CAUSE (PDK defect, not a harness failure): the Bavl avalanche branch in the .subckt uses min(max(V(ci,b)/BVCBO,0),0.997) with a POSITIVE BVCBO .param. On a PNP the collector is below the base in normal operation, so V(ci,b) < 0, the max(...,0) clamps the argument to zero, and the multiplication factor is identically 1. The branch is dead code on both PNPs: PNP_LAT and PNP_HV have NO modelled collector breakdown at any voltage. The expression is the NPN one copy-pasted without a sign flip. This is unmeasurable until the wrapper is fixed. |
| PNP_HV | `ft_times_bvceo_johnson` | needs both ft_at_peak and bvceo_implied; ft=580517832.2741886 bvceo=None |

## Delta vs the phase-1 static audit

Every FoM where the measurement disagrees with the phase-1 static prediction
by more than 2× or crosses a verdict boundary is listed in
[`audit-vs-measurement-discrepancies.md`](audit-vs-measurement-discrepancies.md),
with the measured value declared authoritative and the corrected anchor entry
spelled out. That document is the input to the next anchor revision.
