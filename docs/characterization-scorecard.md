# Characterization Scorecard — AutoHV BiCMOS180 PDK (phase 2 baseline)

**This is the before-picture.** No model fixes landed in phase 2; the PDK was
measured as-is so every later fix can be diffed against this baseline.

- ngspice: `ngspice-45 : Circuit level simulation program`
- generated: 2026-07-22T16:42:10+00:00
- wall time: 399.6 s
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
| `hard-fail` | 32 |
| `expected-fail` | 121 |
| `warn` | 62 |
| `descriptive` | 4 |
| `artifact` | 28 |
| `error` | 14 |
| `no-anchor` | 130 |
| `pass` | 157 |
| **total** | **548** |

### By family

| family | hard-fail | expected-fail | warn | descriptive | artifact | error | no-anchor | pass |
|---|---|---|---|---|---|---|---|---|
| BJT | 4 | 4 | 8 | 4 | 0 | 6 | 12 | 14 |
| BSIM3 MOS | 2 | 24 | 42 | 0 | 0 | 8 | 42 | 20 |
| Diodes/zeners | 1 | 7 | 3 | 0 | 0 | 0 | 1 | 16 |
| Other | 2 | 6 | 0 | 0 | 2 | 0 | 5 | 6 |
| Passives | 0 | 10 | 3 | 0 | 0 | 0 | 9 | 32 |
| VDMOS | 23 | 70 | 6 | 0 | 26 | 0 | 61 | 69 |

**Hard-fails not predicted by phase 1: 32.** These are the rows to read first — everything else was already known.

## Unexpected hard-fails

| device | FoM | measured | band | ×target | deck |
|---|---|---|---|---|---|
| DNMOS20 | `gm_over_id_ceiling` | 23.48 1/V | 24 – 32 | 0.839× | `pdk_validation/characterization/decks/vdmos/DNMOS20_subth.cir` |
| DNMOS20 | `rd_tempco` | 1.505e+04 ppm/degC | 4000 – 9000 | 2.32× | `pdk_validation/characterization/decks/vdmos/DNMOS20_ron_150.cir` |
| DZ_5V6 | `bv` | 5.243 V | 5.32 – 5.88 | 0.936× | `pdk_validation/characterization/decks/diodes/DZ_5V6_rev_27C.cir` |
| NDMOS120 | `rd_tempco` | 1.841e+04 ppm/degC | 4000 – 9000 | 2.83× | `pdk_validation/characterization/decks/vdmos/NDMOS120_ron_150.cir` |
| NDMOS20 | `cjo_per_cell` | 132 fF | 19.9 – 124.2 | 2.66× | `pdk_validation/characterization/decks/vdmos/NDMOS20_cap_0p1.cir` |
| NDMOS20 | `gm_over_id_ceiling` | 21.03 1/V | 24 – 32 | 0.751× | `pdk_validation/characterization/decks/vdmos/NDMOS20_subth.cir` |
| NDMOS20 | `rd_tempco` | 1.458e+04 ppm/degC | 4000 – 9000 | 2.24× | `pdk_validation/characterization/decks/vdmos/NDMOS20_ron_150.cir` |
| NDMOS200 | `cjo_per_cell` | 20.74 fF | 28.6 – 178.5 | 0.291× | `pdk_validation/characterization/decks/vdmos/NDMOS200_cap_0p1.cir` |
| NDMOS200 | `gm_over_id_ceiling` | 34.44 1/V | 24 – 32 | 1.23× | `pdk_validation/characterization/decks/vdmos/NDMOS200_subth.cir` |
| NDMOS200 | `rd_tempco` | 2.045e+04 ppm/degC | 4000 – 9000 | 3.15× | `pdk_validation/characterization/decks/vdmos/NDMOS200_ron_150.cir` |
| NDMOS40 | `gm_over_id_ceiling` | 22.71 1/V | 24 – 32 | 0.811× | `pdk_validation/characterization/decks/vdmos/NDMOS40_subth.cir` |
| NDMOS40 | `rd_tempco` | 1.496e+04 ppm/degC | 4000 – 9000 | 2.3× | `pdk_validation/characterization/decks/vdmos/NDMOS40_ron_150.cir` |
| NDMOS60 | `rd_tempco` | 1.645e+04 ppm/degC | 4000 – 9000 | 2.53× | `pdk_validation/characterization/decks/vdmos/NDMOS60_ron_150.cir` |
| NDMOS80 | `rd_tempco` | 1.65e+04 ppm/degC | 4000 – 9000 | 2.54× | `pdk_validation/characterization/decks/vdmos/NDMOS80_ron_150.cir` |
| NMOS18 | `cox` | 7.704 fF/um^2 | 7.719 – 8.531 | 0.948× | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_caps.cir` |
| NPN_HV | `bvcbo` | 37.84 V | 40.5 – 49.5 | 0.841× | `pdk_validation/characterization/decks/bjt/NPN_HV_bvcbo.cir` |
| NPN_HV | `bvceo_implied` | 24.83 V | 11.25 – 22.5 | 1.65× | `pdk_validation/characterization/decks/bjt/NPN_HV_bvceo.cir` |
| NPN_LV | `bvcbo` | 11.77 V | 12.6 – 15.4 | 0.841× | `pdk_validation/characterization/decks/bjt/NPN_LV_bvcbo.cir` |
| NPN_LV | `bvceo_implied` | 7.465 V | 3.5 – 7 | 1.83× | `pdk_validation/characterization/decks/bjt/NPN_LV_bvceo.cir` |
| PDMOS120 | `rd_tempco` | 2.151e+04 ppm/degC | 4000 – 9000 | 3.31× | `pdk_validation/characterization/decks/vdmos/PDMOS120_ron_150.cir` |
| PDMOS20 | `cjo_per_cell` | 141.4 fF | 20.8 – 129.8 | 2.72× | `pdk_validation/characterization/decks/vdmos/PDMOS20_cap_0p1.cir` |
| PDMOS20 | `gm_over_id_ceiling` | 18.15 1/V | 24 – 32 | 0.648× | `pdk_validation/characterization/decks/vdmos/PDMOS20_subth.cir` |
| PDMOS20 | `rd_tempco` | 1.763e+04 ppm/degC | 4000 – 9000 | 2.71× | `pdk_validation/characterization/decks/vdmos/PDMOS20_ron_150.cir` |
| PDMOS200 | `cjo_per_cell` | 16.97 fF | 28.3 – 176.6 | 0.24× | `pdk_validation/characterization/decks/vdmos/PDMOS200_cap_0p1.cir` |
| PDMOS200 | `gm_over_id_ceiling` | 32.01 1/V | 24 – 32 | 1.14× | `pdk_validation/characterization/decks/vdmos/PDMOS200_subth.cir` |
| PDMOS200 | `rd_tempco` | 2.424e+04 ppm/degC | 4000 – 9000 | 3.73× | `pdk_validation/characterization/decks/vdmos/PDMOS200_ron_150.cir` |
| PDMOS40 | `gm_over_id_ceiling` | 20.8 1/V | 24 – 32 | 0.743× | `pdk_validation/characterization/decks/vdmos/PDMOS40_subth.cir` |
| PDMOS40 | `rd_tempco` | 1.789e+04 ppm/degC | 4000 – 9000 | 2.75× | `pdk_validation/characterization/decks/vdmos/PDMOS40_ron_150.cir` |
| PDMOS60 | `gm_over_id_ceiling` | 22.2 1/V | 24 – 32 | 0.793× | `pdk_validation/characterization/decks/vdmos/PDMOS60_subth.cir` |
| PDMOS60 | `rd_tempco` | 1.901e+04 ppm/degC | 4000 – 9000 | 2.92× | `pdk_validation/characterization/decks/vdmos/PDMOS60_ron_150.cir` |
| PDMOS80 | `rd_tempco` | 1.905e+04 ppm/degC | 4000 – 9000 | 2.93× | `pdk_validation/characterization/decks/vdmos/PDMOS80_ron_150.cir` |
| PMOS18 | `cox` | 7.635 fF/um^2 | 7.719 – 8.531 | 0.94× | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_caps.cir` |

## BSIM3 MOS

| device | FoM | measured | units | band | status | ×target | deck |
|---|---|---|---|---|---|---|---|
| NMOS12 | `cj_area` | 0 | fF/um^2 | 0.245 – 0.49 | **expected-fail** <br>_F6_ |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_caps.cir` |
| NMOS12 | `cjsw_sidewall` | 0 | fF/um | 0.072 – 0.192 | **expected-fail** <br>_F6_ |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_caps.cir` |
| NMOS12 | `junction_perimeter_set` | 0 | boolean | 1 – 1 | **expected-fail** <br>_F6 (AD/AS/PD/PS unset on the M0 line)_ |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_caps.cir` |
| NMOS12 | `idsat_density` | 2.302 | mA/um | 0.2 – 0.4 | warn | 7.67× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_idsat.cir` |
| NMOS12 | `subthreshold_swing` | 163 | mV/dec | 72 – 96 | warn | 2.04× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_idvg.cir` |
| NMOS12 | `vth_corner_spread` | 80 | mV | 40 – 60 | warn | 1.6× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_corner_TT.cir` |
| NMOS12 | `vth_lin` | 1.42 | V | 1.29 – 1.41 | warn | 1.05× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_idvg.cir` |
| NMOS12 | `vth_tempco` | -0.3665 | mV/degC | -2 – -1 | warn | 0.244× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_temp_150.cir` |
| NMOS12 | `flicker_corner` | -- | Hz | 2e+04 – 1.000e+06 | error |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_noise.cir` |
| NMOS12 | `idsat_density_L1u` | 0.3132 | mA/um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_idsat.cir` |
| NMOS12 | `mc_avt_implied_1sigma` | 5.827 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS12_mc_s0.cir` |
| NMOS12 | `mc_sigma_di_over_i` | 0.1829 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS12_mc_s0.cir` |
| NMOS12 | `mc_sigma_dvth_1sigma` | 2.606 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS12_mc_s0.cir` |
| NMOS12 | `mc_sigma_vth_per_device_1sigma` | 1.843 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS12_mc_s0.cir` |
| NMOS12 | `vth_model_internal` | 1.314 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_corner_TT.cir` |
| NMOS12 | `cgso_overlap` | 0.2163 | fF/um | 0.09 – 0.24 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_caps.cir` |
| NMOS12 | `cox` | 1.715 | fF/um^2 | 1.64 – 1.813 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_caps.cir` |
| NMOS12 | `idsat_corner_spread` | 14.65 | percent | 10 – 20 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12_corner_TT.cir` |
| NMOS18 | `cox` | 7.704 | fF/um^2 | 7.719 – 8.531 | **hard-fail** | 0.948× | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_caps.cir` |
| NMOS18 | `cj_area` | 0 | fF/um^2 | 0.7 – 1.4 | **expected-fail** <br>_F6_ |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_caps.cir` |
| NMOS18 | `cjsw_sidewall` | 0 | fF/um | 0.168 – 0.448 | **expected-fail** <br>_F6_ |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_caps.cir` |
| NMOS18 | `junction_perimeter_set` | 0 | boolean | 1 – 1 | **expected-fail** <br>_F6 (AD/AS/PD/PS unset on the M0 line)_ |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_caps.cir` |
| NMOS18 | `idsat_corner_spread` | 25.23 | percent | 10 – 20 | warn | 1.68× | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_corner_TT.cir` |
| NMOS18 | `idsat_density` | 0.5429 | mA/um | 0.55 – 0.6 | warn | 0.944× | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_idsat.cir` |
| NMOS18 | `vth_corner_spread` | 79 | mV | 40 – 60 | warn | 1.58× | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_corner_TT.cir` |
| NMOS18 | `vth_lin` | 0.6301 | V | 0.42 – 0.54 | warn | 1.31× | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_idvg.cir` |
| NMOS18 | `vth_tempco` | -0.3665 | mV/degC | -2 – -1 | warn | 0.244× | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_temp_150.cir` |
| NMOS18 | `flicker_corner` | -- | Hz | 2e+04 – 1.000e+06 | error |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_noise.cir` |
| NMOS18 | `mc_avt_implied_1sigma` | 3.58 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS18_mc_s0.cir` |
| NMOS18 | `mc_sigma_di_over_i` | 0.9057 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS18_mc_s0.cir` |
| NMOS18 | `mc_sigma_dvth_1sigma` | 1.601 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS18_mc_s0.cir` |
| NMOS18 | `mc_sigma_vth_per_device_1sigma` | 1.132 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS18_mc_s0.cir` |
| NMOS18 | `vth_model_internal` | 0.604 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_corner_TT.cir` |
| NMOS18 | `cgso_overlap` | 0.3198 | fF/um | 0.132 – 0.352 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_caps.cir` |
| NMOS18 | `subthreshold_swing` | 79.09 | mV/dec | 72 – 96 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS18_idvg.cir` |
| NMOS33 | `cj_area` | 0 | fF/um^2 | 0.574 – 1.148 | **expected-fail** <br>_F6_ |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_caps.cir` |
| NMOS33 | `cjsw_sidewall` | 0 | fF/um | 0.144 – 0.384 | **expected-fail** <br>_F6_ |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_caps.cir` |
| NMOS33 | `junction_perimeter_set` | 0 | boolean | 1 – 1 | **expected-fail** <br>_F6 (AD/AS/PD/PS unset on the M0 line)_ |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_caps.cir` |
| NMOS33 | `idsat_corner_spread` | 20.6 | percent | 10 – 20 | warn | 1.37× | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_corner_TT.cir` |
| NMOS33 | `idsat_density` | 0.4484 | mA/um | 0.45 – 0.55 | warn | 0.897× | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_idsat.cir` |
| NMOS33 | `vth_corner_spread` | 79.59 | mV | 40 – 60 | warn | 1.59× | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_corner_TT.cir` |
| NMOS33 | `vth_lin` | 0.8095 | V | 0.6 – 0.72 | warn | 1.23× | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_idvg.cir` |
| NMOS33 | `vth_tempco` | -0.3665 | mV/degC | -2 – -1 | warn | 0.244× | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_temp_150.cir` |
| NMOS33 | `flicker_corner` | -- | Hz | 2e+04 – 1.000e+06 | error |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_noise.cir` |
| NMOS33 | `mc_avt_implied_1sigma` | 4.221 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS33_mc_s0.cir` |
| NMOS33 | `mc_sigma_di_over_i` | 0.4457 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS33_mc_s0.cir` |
| NMOS33 | `mc_sigma_dvth_1sigma` | 1.888 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS33_mc_s0.cir` |
| NMOS33 | `mc_sigma_vth_per_device_1sigma` | 1.335 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS33_mc_s0.cir` |
| NMOS33 | `vth_model_internal` | 0.7696 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_corner_TT.cir` |
| NMOS33 | `cgso_overlap` | 0.2896 | fF/um | 0.12 – 0.32 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_caps.cir` |
| NMOS33 | `cox` | 4.996 | fF/um^2 | 4.86 – 5.372 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_caps.cir` |
| NMOS33 | `subthreshold_swing` | 93.06 | mV/dec | 72 – 96 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS33_idvg.cir` |
| NMOS50 | `cj_area` | 0 | fF/um^2 | 0.42 – 0.84 | **expected-fail** <br>_F6_ |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_caps.cir` |
| NMOS50 | `cjsw_sidewall` | 0 | fF/um | 0.108 – 0.288 | **expected-fail** <br>_F6_ |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_caps.cir` |
| NMOS50 | `junction_perimeter_set` | 0 | boolean | 1 – 1 | **expected-fail** <br>_F6 (AD/AS/PD/PS unset on the M0 line)_ |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_caps.cir` |
| NMOS50 | `idsat_density` | 0.3054 | mA/um | 0.4 – 0.5 | warn | 0.679× | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_idsat.cir` |
| NMOS50 | `subthreshold_swing` | 122.2 | mV/dec | 72 – 96 | warn | 1.53× | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_idvg.cir` |
| NMOS50 | `vth_corner_spread` | 79.67 | mV | 40 – 60 | warn | 1.59× | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_corner_TT.cir` |
| NMOS50 | `vth_lin` | 1.016 | V | 0.82 – 0.94 | warn | 1.15× | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_idvg.cir` |
| NMOS50 | `vth_tempco` | -0.3665 | mV/degC | -2 – -1 | warn | 0.244× | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_temp_150.cir` |
| NMOS50 | `flicker_corner` | -- | Hz | 2e+04 – 1.000e+06 | error |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_noise.cir` |
| NMOS50 | `mc_avt_implied_1sigma` | 4.608 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS50_mc_s0.cir` |
| NMOS50 | `mc_sigma_di_over_i` | 0.3163 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS50_mc_s0.cir` |
| NMOS50 | `mc_sigma_dvth_1sigma` | 2.061 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS50_mc_s0.cir` |
| NMOS50 | `mc_sigma_vth_per_device_1sigma` | 1.457 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS50_mc_s0.cir` |
| NMOS50 | `vth_model_internal` | 0.9598 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_corner_TT.cir` |
| NMOS50 | `cgso_overlap` | 0.259 | fF/um | 0.108 – 0.288 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_caps.cir` |
| NMOS50 | `cox` | 3.116 | fF/um^2 | 2.982 – 3.296 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_caps.cir` |
| NMOS50 | `idsat_corner_spread` | 18.46 | percent | 10 – 20 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS50_corner_TT.cir` |
| PMOS12 | `cj_area` | 0 | fF/um^2 | 0.266 – 0.532 | **expected-fail** <br>_F6_ |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_caps.cir` |
| PMOS12 | `cjsw_sidewall` | 0 | fF/um | 0.078 – 0.208 | **expected-fail** <br>_F6_ |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_caps.cir` |
| PMOS12 | `junction_perimeter_set` | 0 | boolean | 1 – 1 | **expected-fail** <br>_F6 (AD/AS/PD/PS unset on the M0 line)_ |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_caps.cir` |
| PMOS12 | `idsat_density` | 1.158 | mA/um | 0.12 – 0.25 | warn | 6.26× | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_idsat.cir` |
| PMOS12 | `subthreshold_swing` | 203.6 | mV/dec | 72 – 96 | warn | 2.55× | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_idvg.cir` |
| PMOS12 | `vth_corner_spread` | 80 | mV | 40 – 60 | warn | 1.6× | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_corner_TT.cir` |
| PMOS12 | `vth_lin` | 1.682 | V | 1.49 – 1.61 | warn | 1.09× | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_idvg.cir` |
| PMOS12 | `vth_tempco` | -0.3665 | mV/degC | -2 – -1 | warn | 0.244× | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_temp_150.cir` |
| PMOS12 | `flicker_corner` | -- | Hz | 2e+04 – 1.000e+06 | error |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_noise.cir` |
| PMOS12 | `idsat_density_L1u` | 0.1422 | mA/um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_idsat.cir` |
| PMOS12 | `mc_avt_implied_1sigma` | 5.837 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS12_mc_s0.cir` |
| PMOS12 | `mc_sigma_di_over_i` | 0.1965 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS12_mc_s0.cir` |
| PMOS12 | `mc_sigma_dvth_1sigma` | 2.61 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS12_mc_s0.cir` |
| PMOS12 | `mc_sigma_vth_per_device_1sigma` | 1.846 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS12_mc_s0.cir` |
| PMOS12 | `vth_model_internal` | 1.573 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_corner_TT.cir` |
| PMOS12 | `cgso_overlap` | 0.2252 | fF/um | 0.096 – 0.256 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_caps.cir` |
| PMOS12 | `cox` | 1.567 | fF/um^2 | 1.562 – 1.727 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_caps.cir` |
| PMOS12 | `idsat_corner_spread` | 14.43 | percent | 10 – 20 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12_corner_TT.cir` |
| PMOS18 | `cox` | 7.635 | fF/um^2 | 7.719 – 8.531 | **hard-fail** | 0.94× | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_caps.cir` |
| PMOS18 | `cj_area` | 0 | fF/um^2 | 0.735 – 1.47 | **expected-fail** <br>_F6_ |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_caps.cir` |
| PMOS18 | `cjsw_sidewall` | 0 | fF/um | 0.18 – 0.48 | **expected-fail** <br>_F6_ |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_caps.cir` |
| PMOS18 | `junction_perimeter_set` | 0 | boolean | 1 – 1 | **expected-fail** <br>_F6 (AD/AS/PD/PS unset on the M0 line)_ |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_caps.cir` |
| PMOS18 | `idsat_corner_spread` | 34.27 | percent | 10 – 20 | warn | 2.28× | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_corner_TT.cir` |
| PMOS18 | `idsat_density` | 0.1734 | mA/um | 0.25 – 0.3 | warn | 0.631× | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_idsat.cir` |
| PMOS18 | `vth_corner_spread` | 79.04 | mV | 40 – 60 | warn | 1.58× | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_corner_TT.cir` |
| PMOS18 | `vth_lin` | 0.7143 | V | 0.46 – 0.58 | warn | 1.37× | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_idvg.cir` |
| PMOS18 | `vth_tempco` | -0.3665 | mV/degC | -2 – -1 | warn | 0.244× | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_temp_150.cir` |
| PMOS18 | `flicker_corner` | -- | Hz | 2e+04 – 1.000e+06 | error |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_noise.cir` |
| PMOS18 | `mc_avt_implied_1sigma` | 3.526 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS18_mc_s0.cir` |
| PMOS18 | `mc_sigma_di_over_i` | 1.036 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS18_mc_s0.cir` |
| PMOS18 | `mc_sigma_dvth_1sigma` | 1.577 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS18_mc_s0.cir` |
| PMOS18 | `mc_sigma_vth_per_device_1sigma` | 1.115 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS18_mc_s0.cir` |
| PMOS18 | `vth_model_internal` | 0.692 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_corner_TT.cir` |
| PMOS18 | `cgso_overlap` | 0.3397 | fF/um | 0.144 – 0.384 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_caps.cir` |
| PMOS18 | `subthreshold_swing` | 84.11 | mV/dec | 72 – 96 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS18_idvg.cir` |
| PMOS33 | `cj_area` | 0 | fF/um^2 | 0.616 – 1.232 | **expected-fail** <br>_F6_ |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_caps.cir` |
| PMOS33 | `cjsw_sidewall` | 0 | fF/um | 0.156 – 0.416 | **expected-fail** <br>_F6_ |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_caps.cir` |
| PMOS33 | `junction_perimeter_set` | 0 | boolean | 1 – 1 | **expected-fail** <br>_F6 (AD/AS/PD/PS unset on the M0 line)_ |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_caps.cir` |
| PMOS33 | `idsat_corner_spread` | 26.73 | percent | 10 – 20 | warn | 1.78× | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_corner_TT.cir` |
| PMOS33 | `idsat_density` | 0.1569 | mA/um | 0.2 – 0.28 | warn | 0.654× | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_idsat.cir` |
| PMOS33 | `subthreshold_swing` | 109.2 | mV/dec | 72 – 96 | warn | 1.37× | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_idvg.cir` |
| PMOS33 | `vth_corner_spread` | 79.64 | mV | 40 – 60 | warn | 1.59× | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_corner_TT.cir` |
| PMOS33 | `vth_lin` | 0.9125 | V | 0.68 – 0.8 | warn | 1.23× | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_idvg.cir` |
| PMOS33 | `vth_tempco` | -0.3665 | mV/degC | -2 – -1 | warn | 0.244× | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_temp_150.cir` |
| PMOS33 | `flicker_corner` | -- | Hz | 2e+04 – 1.000e+06 | error |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_noise.cir` |
| PMOS33 | `mc_avt_implied_1sigma` | 4.042 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS33_mc_s0.cir` |
| PMOS33 | `mc_sigma_di_over_i` | 0.4713 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS33_mc_s0.cir` |
| PMOS33 | `mc_sigma_dvth_1sigma` | 1.808 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS33_mc_s0.cir` |
| PMOS33 | `mc_sigma_vth_per_device_1sigma` | 1.278 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS33_mc_s0.cir` |
| PMOS33 | `vth_model_internal` | 0.8766 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_corner_TT.cir` |
| PMOS33 | `cgso_overlap` | 0.3095 | fF/um | 0.132 – 0.352 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_caps.cir` |
| PMOS33 | `cox` | 4.928 | fF/um^2 | 4.86 – 5.372 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS33_caps.cir` |
| PMOS50 | `cj_area` | 0 | fF/um^2 | 0.448 – 0.896 | **expected-fail** <br>_F6_ |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_caps.cir` |
| PMOS50 | `cjsw_sidewall` | 0 | fF/um | 0.114 – 0.304 | **expected-fail** <br>_F6_ |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_caps.cir` |
| PMOS50 | `junction_perimeter_set` | 0 | boolean | 1 – 1 | **expected-fail** <br>_F6 (AD/AS/PD/PS unset on the M0 line)_ |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_caps.cir` |
| PMOS50 | `idsat_corner_spread` | 23.56 | percent | 10 – 20 | warn | 1.57× | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_corner_TT.cir` |
| PMOS50 | `idsat_density` | 0.1204 | mA/um | 0.18 – 0.25 | warn | 0.56× | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_idsat.cir` |
| PMOS50 | `subthreshold_swing` | 147.8 | mV/dec | 72 – 96 | warn | 1.85× | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_idvg.cir` |
| PMOS50 | `vth_corner_spread` | 79.74 | mV | 40 – 60 | warn | 1.59× | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_corner_TT.cir` |
| PMOS50 | `vth_lin` | 1.144 | V | 0.92 – 1.04 | warn | 1.17× | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_idvg.cir` |
| PMOS50 | `vth_tempco` | -0.3665 | mV/degC | -2 – -1 | warn | 0.244× | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_temp_150.cir` |
| PMOS50 | `flicker_corner` | -- | Hz | 2e+04 – 1.000e+06 | error |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_noise.cir` |
| PMOS50 | `mc_avt_implied_1sigma` | 4.707 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS50_mc_s0.cir` |
| PMOS50 | `mc_sigma_di_over_i` | 0.3564 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS50_mc_s0.cir` |
| PMOS50 | `mc_sigma_dvth_1sigma` | 2.105 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS50_mc_s0.cir` |
| PMOS50 | `mc_sigma_vth_per_device_1sigma` | 1.489 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS50_mc_s0.cir` |
| PMOS50 | `vth_model_internal` | 1.089 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_corner_TT.cir` |
| PMOS50 | `cgso_overlap` | 0.2688 | fF/um | 0.114 – 0.304 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_caps.cir` |
| PMOS50 | `cox` | 3.031 | fF/um^2 | 2.982 – 3.296 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS50_caps.cir` |

## VDMOS

| device | FoM | measured | units | band | status | ×target | deck |
|---|---|---|---|---|---|---|---|
| NDMOS120 | `rd_tempco` | 1.841e+04 | ppm/degC | 4000 – 9000 | **hard-fail** | 2.83× | `pdk_validation/characterization/decks/vdmos/NDMOS120_ron_150.cir` |
| NDMOS120 | `cgdmax_per_cell` | 39.54 | fF | 3.8 – 34.5 | **expected-fail** <br>_F2_ | 3.44× | `pdk_validation/characterization/decks/vdmos/NDMOS120_cap_0p1.cir` |
| NDMOS120 | `cgs_per_cell` | 86.4 | fF | 3.5 – 31 | **expected-fail** <br>_F2 (caps rescaled, not re-derived)_ | 8.31× | `pdk_validation/characterization/decks/vdmos/NDMOS120_cap_0p1.cir` |
| NDMOS120 | `idsat_density` | 244.3 | mA/um | 0.05 – 0.3 | **expected-fail** <br>_F1_ | 1.63e+03× | `pdk_validation/characterization/decks/vdmos/NDMOS120_idsat.cir` |
| NDMOS120 | `ron_times_w` | 20.17 | Ohm.um | 1.666e+04 – 4.165e+04 | **expected-fail** <br>_F1 (LDMOS DC scale)_ | 0.000766× | `pdk_validation/characterization/decks/vdmos/NDMOS120_ron_27.cir` |
| NDMOS120 | `rsp_specific_ron` | 0.003026 | mOhm.cm^2 | 2.499 – 6.247 | **expected-fail** <br>_F1_ | 0.000692× | `pdk_validation/characterization/decks/vdmos/NDMOS120_ron_27.cir` |
| NDMOS120 | `body_diode_tt` | 8.000e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_card.cir` |
| NDMOS120 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_rcond.cir` |
| NDMOS120 | `bv_corner_FF` | 128.1 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_bv_FF.cir` |
| NDMOS120 | `bv_corner_FS` | 128.1 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_bv_FS.cir` |
| NDMOS120 | `bv_corner_SF` | 141.6 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_bv_SF.cir` |
| NDMOS120 | `bv_corner_SS` | 141.6 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_bv_SS.cir` |
| NDMOS120 | `vth_lin` | 1.206 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_idvg.cir` |
| NDMOS120 | `bv` | 134.9 | V | 124.2 – 148.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_bv_TT.cir` |
| NDMOS120 | `cgdmin_per_cell` | 5.765 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_cap_121p5.cir` |
| NDMOS120 | `cjo_per_cell` | 33 | fF | 25.1 – 157.2 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_cap_0p1.cir` |
| NDMOS120 | `gm_over_id_ceiling` | 28.56 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_subth.cir` |
| NDMOS120 | `sigma_vth_1sigma_at_wref` | 9.815 | mV | 6 – 16 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/NDMOS120_mc_s0.cir` |
| NDMOS120 | `subthreshold_swing` | 81.89 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_subth.cir` |
| NDMOS120 | `theta` | 0.123 | 1/V | 0.02 – 0.15 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_theta.cir` |
| NDMOS120 | `vto_tempco` | -2.451 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120_vth_150.cir` |
| NDMOS20 | `cjo_per_cell` | 132 | fF | 19.9 – 124.2 | **hard-fail** | 2.66× | `pdk_validation/characterization/decks/vdmos/NDMOS20_cap_0p1.cir` |
| NDMOS20 | `gm_over_id_ceiling` | 21.03 | 1/V | 24 – 32 | **hard-fail** | 0.751× | `pdk_validation/characterization/decks/vdmos/NDMOS20_subth.cir` |
| NDMOS20 | `rd_tempco` | 1.458e+04 | ppm/degC | 4000 – 9000 | **hard-fail** | 2.24× | `pdk_validation/characterization/decks/vdmos/NDMOS20_ron_150.cir` |
| NDMOS20 | `cgdmax_per_cell` | 255.4 | fF | 3.8 – 34.5 | **expected-fail** <br>_F2_ | 22.2× | `pdk_validation/characterization/decks/vdmos/NDMOS20_cap_0p1.cir` |
| NDMOS20 | `cgdmin_per_cell` | 55.58 | fF | 1 – 8.6 | **expected-fail** <br>_F2_ | 19.2× | `pdk_validation/characterization/decks/vdmos/NDMOS20_cap_21p6.cir` |
| NDMOS20 | `cgs_per_cell` | 499.2 | fF | 3.5 – 31 | **expected-fail** <br>_F2 (caps rescaled, not re-derived)_ | 48× | `pdk_validation/characterization/decks/vdmos/NDMOS20_cap_0p1.cir` |
| NDMOS20 | `idsat_density` | 1674 | mA/um | 0.05 – 0.3 | **expected-fail** <br>_F1_ | 1.12e+04× | `pdk_validation/characterization/decks/vdmos/NDMOS20_idsat.cir` |
| NDMOS20 | `ron_times_w` | 2.31 | Ohm.um | 665.9 – 1665 | **expected-fail** <br>_F1 (LDMOS DC scale)_ | 0.00219× | `pdk_validation/characterization/decks/vdmos/NDMOS20_ron_27.cir` |
| NDMOS20 | `rsp_specific_ron` | 1.155e-04 | mOhm.cm^2 | 0.0333 – 0.0832 | **expected-fail** <br>_F1_ | 0.00198× | `pdk_validation/characterization/decks/vdmos/NDMOS20_ron_27.cir` |
| NDMOS20 | `subthreshold_swing` | 110.9 | mV/dec | 72 – 100 | warn | 1.31× | `pdk_validation/characterization/decks/vdmos/NDMOS20_subth.cir` |
| NDMOS20 | `body_diode_tt` | 1.800e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_card.cir` |
| NDMOS20 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_rcond.cir` |
| NDMOS20 | `bv_corner_FF` | 23.24 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_bv_FF.cir` |
| NDMOS20 | `bv_corner_FS` | 23.24 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_bv_FS.cir` |
| NDMOS20 | `bv_corner_SF` | 24.44 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_bv_SF.cir` |
| NDMOS20 | `bv_corner_SS` | 24.44 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_bv_SS.cir` |
| NDMOS20 | `vth_lin` | 1.004 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_idvg.cir` |
| NDMOS20 | `bv` | 23.84 | V | 22.1 – 26.4 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_bv_TT.cir` |
| NDMOS20 | `sigma_vth_1sigma_at_wref` | 7.427 | mV | 4.8 – 12.8 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/NDMOS20_mc_s0.cir` |
| NDMOS20 | `theta` | 0.1103 | 1/V | 0.02 – 0.15 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_theta.cir` |
| NDMOS20 | `vto_tempco` | -1.93 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20_vth_150.cir` |
| NDMOS200 | `cjo_per_cell` | 20.74 | fF | 28.6 – 178.5 | **hard-fail** | 0.291× | `pdk_validation/characterization/decks/vdmos/NDMOS200_cap_0p1.cir` |
| NDMOS200 | `gm_over_id_ceiling` | 34.44 | 1/V | 24 – 32 | **hard-fail** | 1.23× | `pdk_validation/characterization/decks/vdmos/NDMOS200_subth.cir` |
| NDMOS200 | `rd_tempco` | 2.045e+04 | ppm/degC | 4000 – 9000 | **hard-fail** | 3.15× | `pdk_validation/characterization/decks/vdmos/NDMOS200_ron_150.cir` |
| NDMOS200 | `cgs_per_cell` | 48 | fF | 3.5 – 31 | **expected-fail** <br>_F2 (caps rescaled, not re-derived)_ | 4.62× | `pdk_validation/characterization/decks/vdmos/NDMOS200_cap_0p1.cir` |
| NDMOS200 | `idsat_density` | 117.7 | mA/um | 0.05 – 0.3 | **expected-fail** <br>_F1_ | 785× | `pdk_validation/characterization/decks/vdmos/NDMOS200_idsat.cir` |
| NDMOS200 | `ron_times_w` | 44.74 | Ohm.um | 4.073e+04 – 1.018e+05 | **expected-fail** <br>_F1 (LDMOS DC scale)_ | 0.000695× | `pdk_validation/characterization/decks/vdmos/NDMOS200_ron_27.cir` |
| NDMOS200 | `rsp_specific_ron` | 0.009844 | mOhm.cm^2 | 8.961 – 22.4 | **expected-fail** <br>_F1_ | 0.000628× | `pdk_validation/characterization/decks/vdmos/NDMOS200_ron_27.cir` |
| NDMOS200 | `sigma_vth_1sigma_at_wref` | 3.479 | mV | 6.6 – 17.6 | **expected-fail** <br>_F-VD3 (ladder-B mismatch ~3x optimistic)_ | 0.316× | `pdk_validation/characterization/decks/vdmos_mc/NDMOS200_mc_s0.cir` |
| NDMOS200 | `subthreshold_swing` | 70.69 | mV/dec | 72 – 100 | warn | 0.832× | `pdk_validation/characterization/decks/vdmos/NDMOS200_subth.cir` |
| NDMOS200 | `body_diode_tt` | 1.300e-07 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_card.cir` |
| NDMOS200 | `l_drift_for_bv` | 11.25 | um | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_bv_L8u.cir` |
| NDMOS200 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_rcond.cir` |
| NDMOS200 | `bv_corner_FF` | 211.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_bv_FF.cir` |
| NDMOS200 | `bv_corner_FS` | 211.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_bv_FS.cir` |
| NDMOS200 | `bv_corner_SF` | 238.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_bv_SF.cir` |
| NDMOS200 | `bv_corner_SS` | 238.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_bv_SS.cir` |
| NDMOS200 | `cap_reconciliation_ndmos200` | 0 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_recon_repro1_fixed.cir` |
| NDMOS200 | `vth_lin` | 1.258 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_idvg.cir` |
| NDMOS200 | `bv` | 224.9 | V | 207 – 247.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_bv_TT.cir` |
| NDMOS200 | `cgdmax_per_cell` | 22.28 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_cap_0p1.cir` |
| NDMOS200 | `cgdmin_per_cell` | 3.279 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_cap_202p5.cir` |
| NDMOS200 | `theta` | 0.1253 | 1/V | 0.02 – 0.15 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_theta.cir` |
| NDMOS200 | `vto_tempco` | -2.768 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200_vth_150.cir` |
| NDMOS40 | `gm_over_id_ceiling` | 22.71 | 1/V | 24 – 32 | **hard-fail** | 0.811× | `pdk_validation/characterization/decks/vdmos/NDMOS40_subth.cir` |
| NDMOS40 | `rd_tempco` | 1.496e+04 | ppm/degC | 4000 – 9000 | **hard-fail** | 2.3× | `pdk_validation/characterization/decks/vdmos/NDMOS40_ron_150.cir` |
| NDMOS40 | `cgdmax_per_cell` | 159.9 | fF | 3.8 – 34.5 | **expected-fail** <br>_F2_ | 13.9× | `pdk_validation/characterization/decks/vdmos/NDMOS40_cap_0p1.cir` |
| NDMOS40 | `cgdmin_per_cell` | 28.89 | fF | 1 – 8.6 | **expected-fail** <br>_F2_ | 9.96× | `pdk_validation/characterization/decks/vdmos/NDMOS40_cap_43p2.cir` |
| NDMOS40 | `cgs_per_cell` | 336 | fF | 3.5 – 31 | **expected-fail** <br>_F2 (caps rescaled, not re-derived)_ | 32.3× | `pdk_validation/characterization/decks/vdmos/NDMOS40_cap_0p1.cir` |
| NDMOS40 | `idsat_density` | 1089 | mA/um | 0.05 – 0.3 | **expected-fail** <br>_F1_ | 7.26e+03× | `pdk_validation/characterization/decks/vdmos/NDMOS40_idsat.cir` |
| NDMOS40 | `ron_times_w` | 3.83 | Ohm.um | 2691 – 6727 | **expected-fail** <br>_F1 (LDMOS DC scale)_ | 0.0009× | `pdk_validation/characterization/decks/vdmos/NDMOS40_ron_27.cir` |
| NDMOS40 | `rsp_specific_ron` | 2.681e-04 | mOhm.cm^2 | 0.1884 – 0.4709 | **expected-fail** <br>_F1_ | 0.000813× | `pdk_validation/characterization/decks/vdmos/NDMOS40_ron_27.cir` |
| NDMOS40 | `sigma_vth_1sigma_at_wref` | 2.512 | mV | 5.1 – 13.6 | **expected-fail** <br>_F-VD3 (ladder-B mismatch ~3x optimistic)_ | 0.296× | `pdk_validation/characterization/decks/vdmos_mc/NDMOS40_mc_s0.cir` |
| NDMOS40 | `subthreshold_swing` | 102.8 | mV/dec | 72 – 100 | warn | 1.21× | `pdk_validation/characterization/decks/vdmos/NDMOS40_subth.cir` |
| NDMOS40 | `body_diode_tt` | 2.800e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_card.cir` |
| NDMOS40 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_rcond.cir` |
| NDMOS40 | `bv_corner_FF` | 46.41 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_bv_FF.cir` |
| NDMOS40 | `bv_corner_FS` | 46.41 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_bv_FS.cir` |
| NDMOS40 | `bv_corner_SF` | 49.29 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_bv_SF.cir` |
| NDMOS40 | `bv_corner_SS` | 49.29 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_bv_SS.cir` |
| NDMOS40 | `vth_lin` | 1.054 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_idvg.cir` |
| NDMOS40 | `bv` | 47.85 | V | 44.2 – 52.8 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_bv_TT.cir` |
| NDMOS40 | `cjo_per_cell` | 94.28 | fF | 19.7 – 123 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_cap_0p1.cir` |
| NDMOS40 | `theta` | 0.1164 | 1/V | 0.02 – 0.15 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_theta.cir` |
| NDMOS40 | `vto_tempco` | -2.131 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40_vth_150.cir` |
| NDMOS60 | `rd_tempco` | 1.645e+04 | ppm/degC | 4000 – 9000 | **hard-fail** | 2.53× | `pdk_validation/characterization/decks/vdmos/NDMOS60_ron_150.cir` |
| NDMOS60 | `cgdmax_per_cell` | 97.78 | fF | 3.8 – 34.5 | **expected-fail** <br>_F2_ | 8.5× | `pdk_validation/characterization/decks/vdmos/NDMOS60_cap_0p1.cir` |
| NDMOS60 | `cgdmin_per_cell` | 16.87 | fF | 1 – 8.6 | **expected-fail** <br>_F2_ | 5.82× | `pdk_validation/characterization/decks/vdmos/NDMOS60_cap_67p5.cir` |
| NDMOS60 | `cgs_per_cell` | 211.2 | fF | 3.5 – 31 | **expected-fail** <br>_F2 (caps rescaled, not re-derived)_ | 20.3× | `pdk_validation/characterization/decks/vdmos/NDMOS60_cap_0p1.cir` |
| NDMOS60 | `idsat_density` | 672.8 | mA/um | 0.05 – 0.3 | **expected-fail** <br>_F1_ | 4.49e+03× | `pdk_validation/characterization/decks/vdmos/NDMOS60_idsat.cir` |
| NDMOS60 | `ron_times_w` | 6.454 | Ohm.um | 6387 – 1.597e+04 | **expected-fail** <br>_F1 (LDMOS DC scale)_ | 0.000639× | `pdk_validation/characterization/decks/vdmos/NDMOS60_ron_27.cir` |
| NDMOS60 | `rsp_specific_ron` | 5.809e-04 | mOhm.cm^2 | 0.5748 – 1.437 | **expected-fail** <br>_F1_ | 0.000577× | `pdk_validation/characterization/decks/vdmos/NDMOS60_ron_27.cir` |
| NDMOS60 | `body_diode_tt` | 4.000e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_card.cir` |
| NDMOS60 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_rcond.cir` |
| NDMOS60 | `bv_corner_FF` | 72.23 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_bv_FF.cir` |
| NDMOS60 | `bv_corner_FS` | 72.23 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_bv_FS.cir` |
| NDMOS60 | `bv_corner_SF` | 77.48 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_bv_SF.cir` |
| NDMOS60 | `bv_corner_SS` | 77.48 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_bv_SS.cir` |
| NDMOS60 | `vth_lin` | 1.106 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_idvg.cir` |
| NDMOS60 | `bv` | 74.86 | V | 69 – 82.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_bv_TT.cir` |
| NDMOS60 | `cjo_per_cell` | 70.71 | fF | 20.2 – 126.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_cap_0p1.cir` |
| NDMOS60 | `gm_over_id_ceiling` | 24.99 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_subth.cir` |
| NDMOS60 | `sigma_vth_1sigma_at_wref` | 9.429 | mV | 5.4 – 14.4 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/NDMOS60_mc_s0.cir` |
| NDMOS60 | `subthreshold_swing` | 93.4 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_subth.cir` |
| NDMOS60 | `theta` | 0.1189 | 1/V | 0.02 – 0.15 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_theta.cir` |
| NDMOS60 | `vto_tempco` | -2.237 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60_vth_150.cir` |
| NDMOS80 | `rd_tempco` | 1.65e+04 | ppm/degC | 4000 – 9000 | **hard-fail** | 2.54× | `pdk_validation/characterization/decks/vdmos/NDMOS80_ron_150.cir` |
| NDMOS80 | `cgdmax_per_cell` | 63.48 | fF | 3.8 – 34.5 | **expected-fail** <br>_F2_ | 5.52× | `pdk_validation/characterization/decks/vdmos/NDMOS80_cap_0p1.cir` |
| NDMOS80 | `cgdmin_per_cell` | 10.1 | fF | 1 – 8.6 | **expected-fail** <br>_F2_ | 3.48× | `pdk_validation/characterization/decks/vdmos/NDMOS80_cap_85p5.cir` |
| NDMOS80 | `cgs_per_cell` | 135 | fF | 3.5 – 31 | **expected-fail** <br>_F2 (caps rescaled, not re-derived)_ | 13× | `pdk_validation/characterization/decks/vdmos/NDMOS80_cap_0p1.cir` |
| NDMOS80 | `idsat_density` | 449 | mA/um | 0.05 – 0.3 | **expected-fail** <br>_F1_ | 2.99e+03× | `pdk_validation/characterization/decks/vdmos/NDMOS80_idsat.cir` |
| NDMOS80 | `ron_times_w` | 10.14 | Ohm.um | 9436 – 2.359e+04 | **expected-fail** <br>_F1 (LDMOS DC scale)_ | 0.00068× | `pdk_validation/characterization/decks/vdmos/NDMOS80_ron_27.cir` |
| NDMOS80 | `rsp_specific_ron` | 0.001116 | mOhm.cm^2 | 1.038 – 2.595 | **expected-fail** <br>_F1_ | 0.000614× | `pdk_validation/characterization/decks/vdmos/NDMOS80_ron_27.cir` |
| NDMOS80 | `sigma_vth_1sigma_at_wref` | 2.97 | mV | 5.7 – 15.2 | **expected-fail** <br>_F-VD3 (ladder-B mismatch ~3x optimistic)_ | 0.313× | `pdk_validation/characterization/decks/vdmos_mc/NDMOS80_mc_s0.cir` |
| NDMOS80 | `body_diode_tt` | 5.500e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_card.cir` |
| NDMOS80 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_rcond.cir` |
| NDMOS80 | `bv_corner_FF` | 91.06 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_bv_FF.cir` |
| NDMOS80 | `bv_corner_FS` | 91.06 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_bv_FS.cir` |
| NDMOS80 | `bv_corner_SF` | 98.66 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_bv_SF.cir` |
| NDMOS80 | `bv_corner_SS` | 98.66 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_bv_SS.cir` |
| NDMOS80 | `vth_lin` | 1.157 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_idvg.cir` |
| NDMOS80 | `bv` | 94.86 | V | 87.4 – 104.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_bv_TT.cir` |
| NDMOS80 | `cjo_per_cell` | 51.85 | fF | 22 – 137.4 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_cap_0p1.cir` |
| NDMOS80 | `gm_over_id_ceiling` | 26.66 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_subth.cir` |
| NDMOS80 | `subthreshold_swing` | 87.6 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_subth.cir` |
| NDMOS80 | `theta` | 0.115 | 1/V | 0.02 – 0.15 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_theta.cir` |
| NDMOS80 | `vto_tempco` | -2.346 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80_vth_150.cir` |
| PDMOS120 | `rd_tempco` | 2.151e+04 | ppm/degC | 4000 – 9000 | **hard-fail** | 3.31× | `pdk_validation/characterization/decks/vdmos/PDMOS120_ron_150.cir` |
| PDMOS120 | `cgs_per_cell` | 61 | fF | 3.5 – 31 | **expected-fail** <br>_F2 (caps rescaled, not re-derived)_ | 5.87× | `pdk_validation/characterization/decks/vdmos/PDMOS120_cap_0p1.cir` |
| PDMOS120 | `idsat_density` | 110.8 | mA/um | 0.05 – 0.3 | **expected-fail** <br>_F1_ | 739× | `pdk_validation/characterization/decks/vdmos/PDMOS120_idsat.cir` |
| PDMOS120 | `ron_times_w` | 45.35 | Ohm.um | 1.458e+04 – 3.645e+04 | **expected-fail** <br>_F1 (LDMOS DC scale)_ | 0.00197× | `pdk_validation/characterization/decks/vdmos/PDMOS120_ron_27.cir` |
| PDMOS120 | `rsp_specific_ron` | 0.006802 | mOhm.cm^2 | 2.187 – 5.468 | **expected-fail** <br>_F1_ | 0.00178× | `pdk_validation/characterization/decks/vdmos/PDMOS120_ron_27.cir` |
| PDMOS120 | `body_diode_tt` | 9.500e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_card.cir` |
| PDMOS120 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_rcond.cir` |
| PDMOS120 | `bv_corner_FF` | 122.8 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_bv_FF.cir` |
| PDMOS120 | `bv_corner_FS` | 133 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_bv_FS.cir` |
| PDMOS120 | `bv_corner_SF` | 122.8 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_bv_SF.cir` |
| PDMOS120 | `bv_corner_SS` | 133 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_bv_SS.cir` |
| PDMOS120 | `vth_lin` | -1.251 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_idvg.cir` |
| PDMOS120 | `bv` | 127.9 | V | 117.8 – 140.8 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_bv_TT.cir` |
| PDMOS120 | `cgdmax_per_cell` | 29.9 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_cap_0p1.cir` |
| PDMOS120 | `cgdmin_per_cell` | 4.645 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_cap_115p2.cir` |
| PDMOS120 | `cjo_per_cell` | 27.34 | fF | 25.8 – 161.4 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_cap_0p1.cir` |
| PDMOS120 | `gm_over_id_ceiling` | 25.94 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_subth.cir` |
| PDMOS120 | `sigma_vth_1sigma_at_wref` | 10.61 | mV | 6 – 16 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/PDMOS120_mc_s0.cir` |
| PDMOS120 | `subthreshold_swing` | 90.18 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_subth.cir` |
| PDMOS120 | `theta` | 0.1327 | 1/V | 0.02 – 0.15 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_theta.cir` |
| PDMOS120 | `vto_tempco` | -2.556 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120_vth_150.cir` |
| PDMOS20 | `cjo_per_cell` | 141.4 | fF | 20.8 – 129.8 | **hard-fail** | 2.72× | `pdk_validation/characterization/decks/vdmos/PDMOS20_cap_0p1.cir` |
| PDMOS20 | `gm_over_id_ceiling` | 18.15 | 1/V | 24 – 32 | **hard-fail** | 0.648× | `pdk_validation/characterization/decks/vdmos/PDMOS20_subth.cir` |
| PDMOS20 | `rd_tempco` | 1.763e+04 | ppm/degC | 4000 – 9000 | **hard-fail** | 2.71× | `pdk_validation/characterization/decks/vdmos/PDMOS20_ron_150.cir` |
| PDMOS20 | `cgdmax_per_cell` | 219.2 | fF | 3.8 – 34.5 | **expected-fail** <br>_F2_ | 19.1× | `pdk_validation/characterization/decks/vdmos/PDMOS20_cap_0p1.cir` |
| PDMOS20 | `cgdmin_per_cell` | 50.48 | fF | 1 – 8.6 | **expected-fail** <br>_F2_ | 17.4× | `pdk_validation/characterization/decks/vdmos/PDMOS20_cap_19p8.cir` |
| PDMOS20 | `cgs_per_cell` | 403.2 | fF | 3.5 – 31 | **expected-fail** <br>_F2 (caps rescaled, not re-derived)_ | 38.8× | `pdk_validation/characterization/decks/vdmos/PDMOS20_cap_0p1.cir` |
| PDMOS20 | `idsat_density` | 801.3 | mA/um | 0.05 – 0.3 | **expected-fail** <br>_F1_ | 5.34e+03× | `pdk_validation/characterization/decks/vdmos/PDMOS20_idsat.cir` |
| PDMOS20 | `ron_times_w` | 4.793 | Ohm.um | 535.8 – 1339 | **expected-fail** <br>_F1 (LDMOS DC scale)_ | 0.00566× | `pdk_validation/characterization/decks/vdmos/PDMOS20_ron_27.cir` |
| PDMOS20 | `rsp_specific_ron` | 2.396e-04 | mOhm.cm^2 | 0.0268 – 0.067 | **expected-fail** <br>_F1_ | 0.00511× | `pdk_validation/characterization/decks/vdmos/PDMOS20_ron_27.cir` |
| PDMOS20 | `subthreshold_swing` | 128.5 | mV/dec | 72 – 100 | warn | 1.51× | `pdk_validation/characterization/decks/vdmos/PDMOS20_subth.cir` |
| PDMOS20 | `body_diode_tt` | 2.200e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_card.cir` |
| PDMOS20 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_rcond.cir` |
| PDMOS20 | `bv_corner_FF` | 21.27 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_bv_FF.cir` |
| PDMOS20 | `bv_corner_FS` | 22.37 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_bv_FS.cir` |
| PDMOS20 | `bv_corner_SF` | 21.27 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_bv_SF.cir` |
| PDMOS20 | `bv_corner_SS` | 22.37 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_bv_SS.cir` |
| PDMOS20 | `vth_lin` | -1.049 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_idvg.cir` |
| PDMOS20 | `bv` | 21.82 | V | 20.2 – 24.2 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_bv_TT.cir` |
| PDMOS20 | `sigma_vth_1sigma_at_wref` | 8.293 | mV | 4.8 – 12.8 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/PDMOS20_mc_s0.cir` |
| PDMOS20 | `theta` | 0.09675 | 1/V | 0.02 – 0.15 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_theta.cir` |
| PDMOS20 | `vto_tempco` | -2.069 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20_vth_150.cir` |
| PDMOS200 | `cjo_per_cell` | 16.97 | fF | 28.3 – 176.6 | **hard-fail** | 0.24× | `pdk_validation/characterization/decks/vdmos/PDMOS200_cap_0p1.cir` |
| PDMOS200 | `gm_over_id_ceiling` | 32.01 | 1/V | 24 – 32 | **hard-fail** | 1.14× | `pdk_validation/characterization/decks/vdmos/PDMOS200_subth.cir` |
| PDMOS200 | `rd_tempco` | 2.424e+04 | ppm/degC | 4000 – 9000 | **hard-fail** | 3.73× | `pdk_validation/characterization/decks/vdmos/PDMOS200_ron_150.cir` |
| PDMOS200 | `cgs_per_cell` | 34 | fF | 3.5 – 31 | **expected-fail** <br>_F2 (caps rescaled, not re-derived)_ | 3.27× | `pdk_validation/characterization/decks/vdmos/PDMOS200_cap_0p1.cir` |
| PDMOS200 | `idsat_density` | 46.69 | mA/um | 0.05 – 0.3 | **expected-fail** <br>_F1_ | 311× | `pdk_validation/characterization/decks/vdmos/PDMOS200_idsat.cir` |
| PDMOS200 | `ron_times_w` | 115.9 | Ohm.um | 4.303e+04 – 1.076e+05 | **expected-fail** <br>_F1 (LDMOS DC scale)_ | 0.0017× | `pdk_validation/characterization/decks/vdmos/PDMOS200_ron_27.cir` |
| PDMOS200 | `rsp_specific_ron` | 0.02549 | mOhm.cm^2 | 9.467 – 23.67 | **expected-fail** <br>_F1_ | 0.00154× | `pdk_validation/characterization/decks/vdmos/PDMOS200_ron_27.cir` |
| PDMOS200 | `sigma_vth_1sigma_at_wref` | 3.621 | mV | 6.6 – 17.6 | **expected-fail** <br>_F-VD3 (ladder-B mismatch ~3x optimistic)_ | 0.329× | `pdk_validation/characterization/decks/vdmos_mc/PDMOS200_mc_s0.cir` |
| PDMOS200 | `body_diode_tt` | 1.550e-07 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_card.cir` |
| PDMOS200 | `l_drift_for_bv` | 11.5 | um | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_bv_L8u.cir` |
| PDMOS200 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_rcond.cir` |
| PDMOS200 | `bv_corner_FF` | 216.1 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_bv_FF.cir` |
| PDMOS200 | `bv_corner_FS` | 243.7 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_bv_FS.cir` |
| PDMOS200 | `bv_corner_SF` | 216.1 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_bv_SF.cir` |
| PDMOS200 | `bv_corner_SS` | 243.7 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_bv_SS.cir` |
| PDMOS200 | `vth_lin` | -1.315 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_idvg.cir` |
| PDMOS200 | `bv` | 229.9 | V | 211.6 – 253 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_bv_TT.cir` |
| PDMOS200 | `cgdmax_per_cell` | 16.67 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_cap_0p1.cir` |
| PDMOS200 | `cgdmin_per_cell` | 2.71 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_cap_207.cir` |
| PDMOS200 | `subthreshold_swing` | 76.71 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_subth.cir` |
| PDMOS200 | `theta` | 0.1279 | 1/V | 0.02 – 0.15 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_theta.cir` |
| PDMOS200 | `vto_tempco` | -2.836 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200_vth_150.cir` |
| PDMOS40 | `gm_over_id_ceiling` | 20.8 | 1/V | 24 – 32 | **hard-fail** | 0.743× | `pdk_validation/characterization/decks/vdmos/PDMOS40_subth.cir` |
| PDMOS40 | `rd_tempco` | 1.789e+04 | ppm/degC | 4000 – 9000 | **hard-fail** | 2.75× | `pdk_validation/characterization/decks/vdmos/PDMOS40_ron_150.cir` |
| PDMOS40 | `cgdmax_per_cell` | 122 | fF | 3.8 – 34.5 | **expected-fail** <br>_F2_ | 10.6× | `pdk_validation/characterization/decks/vdmos/PDMOS40_cap_0p1.cir` |
| PDMOS40 | `cgdmin_per_cell` | 22.88 | fF | 1 – 8.6 | **expected-fail** <br>_F2_ | 7.89× | `pdk_validation/characterization/decks/vdmos/PDMOS40_cap_40p5.cir` |
| PDMOS40 | `cgs_per_cell` | 252 | fF | 3.5 – 31 | **expected-fail** <br>_F2 (caps rescaled, not re-derived)_ | 24.2× | `pdk_validation/characterization/decks/vdmos/PDMOS40_cap_0p1.cir` |
| PDMOS40 | `idsat_density` | 491.8 | mA/um | 0.05 – 0.3 | **expected-fail** <br>_F1_ | 3.28e+03× | `pdk_validation/characterization/decks/vdmos/PDMOS40_idsat.cir` |
| PDMOS40 | `ron_times_w` | 8.309 | Ohm.um | 2290 – 5725 | **expected-fail** <br>_F1 (LDMOS DC scale)_ | 0.00229× | `pdk_validation/characterization/decks/vdmos/PDMOS40_ron_27.cir` |
| PDMOS40 | `rsp_specific_ron` | 5.816e-04 | mOhm.cm^2 | 0.1603 – 0.4007 | **expected-fail** <br>_F1_ | 0.00207× | `pdk_validation/characterization/decks/vdmos/PDMOS40_ron_27.cir` |
| PDMOS40 | `sigma_vth_1sigma_at_wref` | 2.95 | mV | 5.1 – 13.6 | **expected-fail** <br>_F-VD3 (ladder-B mismatch ~3x optimistic)_ | 0.347× | `pdk_validation/characterization/decks/vdmos_mc/PDMOS40_mc_s0.cir` |
| PDMOS40 | `subthreshold_swing` | 112.2 | mV/dec | 72 – 100 | warn | 1.32× | `pdk_validation/characterization/decks/vdmos/PDMOS40_subth.cir` |
| PDMOS40 | `body_diode_tt` | 3.500e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_card.cir` |
| PDMOS40 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_rcond.cir` |
| PDMOS40 | `bv_corner_FF` | 43.48 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_bv_FF.cir` |
| PDMOS40 | `bv_corner_FS` | 46.18 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_bv_FS.cir` |
| PDMOS40 | `bv_corner_SF` | 43.48 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_bv_SF.cir` |
| PDMOS40 | `bv_corner_SS` | 46.18 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_bv_SS.cir` |
| PDMOS40 | `vth_lin` | -1.101 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_idvg.cir` |
| PDMOS40 | `bv` | 44.83 | V | 41.4 – 49.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_bv_TT.cir` |
| PDMOS40 | `cjo_per_cell` | 99 | fF | 20.3 – 127 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_cap_0p1.cir` |
| PDMOS40 | `theta` | 0.1108 | 1/V | 0.02 – 0.15 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_theta.cir` |
| PDMOS40 | `vto_tempco` | -2.269 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40_vth_150.cir` |
| PDMOS60 | `gm_over_id_ceiling` | 22.2 | 1/V | 24 – 32 | **hard-fail** | 0.793× | `pdk_validation/characterization/decks/vdmos/PDMOS60_subth.cir` |
| PDMOS60 | `rd_tempco` | 1.901e+04 | ppm/degC | 4000 – 9000 | **hard-fail** | 2.92× | `pdk_validation/characterization/decks/vdmos/PDMOS60_ron_150.cir` |
| PDMOS60 | `cgdmax_per_cell` | 73.22 | fF | 3.8 – 34.5 | **expected-fail** <br>_F2_ | 6.37× | `pdk_validation/characterization/decks/vdmos/PDMOS60_cap_0p1.cir` |
| PDMOS60 | `cgdmin_per_cell` | 12.5 | fF | 1 – 8.6 | **expected-fail** <br>_F2_ | 4.31× | `pdk_validation/characterization/decks/vdmos/PDMOS60_cap_63.cir` |
| PDMOS60 | `cgs_per_cell` | 144 | fF | 3.5 – 31 | **expected-fail** <br>_F2 (caps rescaled, not re-derived)_ | 13.8× | `pdk_validation/characterization/decks/vdmos/PDMOS60_cap_0p1.cir` |
| PDMOS60 | `idsat_density` | 301.7 | mA/um | 0.05 – 0.3 | **expected-fail** <br>_F1_ | 2.01e+03× | `pdk_validation/characterization/decks/vdmos/PDMOS60_idsat.cir` |
| PDMOS60 | `ron_times_w` | 14.79 | Ohm.um | 5375 – 1.344e+04 | **expected-fail** <br>_F1 (LDMOS DC scale)_ | 0.00174× | `pdk_validation/characterization/decks/vdmos/PDMOS60_ron_27.cir` |
| PDMOS60 | `rsp_specific_ron` | 0.001331 | mOhm.cm^2 | 0.4838 – 1.209 | **expected-fail** <br>_F1_ | 0.00157× | `pdk_validation/characterization/decks/vdmos/PDMOS60_ron_27.cir` |
| PDMOS60 | `subthreshold_swing` | 105.1 | mV/dec | 72 – 100 | warn | 1.24× | `pdk_validation/characterization/decks/vdmos/PDMOS60_subth.cir` |
| PDMOS60 | `body_diode_tt` | 5.000e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_card.cir` |
| PDMOS60 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_rcond.cir` |
| PDMOS60 | `bv_corner_FF` | 67.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_bv_FF.cir` |
| PDMOS60 | `bv_corner_FS` | 72.3 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_bv_FS.cir` |
| PDMOS60 | `bv_corner_SF` | 67.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_bv_SF.cir` |
| PDMOS60 | `bv_corner_SS` | 72.3 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_bv_SS.cir` |
| PDMOS60 | `vth_lin` | -1.149 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_idvg.cir` |
| PDMOS60 | `bv` | 69.85 | V | 64.4 – 77 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_bv_TT.cir` |
| PDMOS60 | `cjo_per_cell` | 61.28 | fF | 21 – 131 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_cap_0p1.cir` |
| PDMOS60 | `sigma_vth_1sigma_at_wref` | 7.804 | mV | 5.4 – 14.4 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/PDMOS60_mc_s0.cir` |
| PDMOS60 | `theta` | 0.125 | 1/V | 0.02 – 0.15 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_theta.cir` |
| PDMOS60 | `vto_tempco` | -2.374 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60_vth_150.cir` |
| PDMOS80 | `rd_tempco` | 1.905e+04 | ppm/degC | 4000 – 9000 | **hard-fail** | 2.93× | `pdk_validation/characterization/decks/vdmos/PDMOS80_ron_150.cir` |
| PDMOS80 | `cgdmax_per_cell` | 47.9 | fF | 3.8 – 34.5 | **expected-fail** <br>_F2_ | 4.17× | `pdk_validation/characterization/decks/vdmos/PDMOS80_cap_0p1.cir` |
| PDMOS80 | `cgs_per_cell` | 95 | fF | 3.5 – 31 | **expected-fail** <br>_F2 (caps rescaled, not re-derived)_ | 9.13× | `pdk_validation/characterization/decks/vdmos/PDMOS80_cap_0p1.cir` |
| PDMOS80 | `idsat_density` | 205.8 | mA/um | 0.05 – 0.3 | **expected-fail** <br>_F1_ | 1.37e+03× | `pdk_validation/characterization/decks/vdmos/PDMOS80_idsat.cir` |
| PDMOS80 | `ron_times_w` | 22.62 | Ohm.um | 8243 – 2.061e+04 | **expected-fail** <br>_F1 (LDMOS DC scale)_ | 0.00174× | `pdk_validation/characterization/decks/vdmos/PDMOS80_ron_27.cir` |
| PDMOS80 | `rsp_specific_ron` | 0.002488 | mOhm.cm^2 | 0.9068 – 2.267 | **expected-fail** <br>_F1_ | 0.00157× | `pdk_validation/characterization/decks/vdmos/PDMOS80_ron_27.cir` |
| PDMOS80 | `sigma_vth_1sigma_at_wref` | 3.172 | mV | 5.7 – 15.2 | **expected-fail** <br>_F-VD3 (ladder-B mismatch ~3x optimistic)_ | 0.334× | `pdk_validation/characterization/decks/vdmos_mc/PDMOS80_mc_s0.cir` |
| PDMOS80 | `body_diode_tt` | 6.500e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_card.cir` |
| PDMOS80 | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_rcond.cir` |
| PDMOS80 | `bv_corner_FF` | 86.26 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_bv_FF.cir` |
| PDMOS80 | `bv_corner_FS` | 93.46 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_bv_FS.cir` |
| PDMOS80 | `bv_corner_SF` | 86.26 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_bv_SF.cir` |
| PDMOS80 | `bv_corner_SS` | 93.46 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_bv_SS.cir` |
| PDMOS80 | `vth_lin` | -1.201 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_idvg.cir` |
| PDMOS80 | `bv` | 89.86 | V | 82.8 – 99 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_bv_TT.cir` |
| PDMOS80 | `cgdmin_per_cell` | 8.332 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_cap_81.cir` |
| PDMOS80 | `cjo_per_cell` | 42.43 | fF | 22.6 – 141.2 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_cap_0p1.cir` |
| PDMOS80 | `gm_over_id_ceiling` | 24.36 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_subth.cir` |
| PDMOS80 | `subthreshold_swing` | 95.9 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_subth.cir` |
| PDMOS80 | `theta` | 0.1265 | 1/V | 0.02 – 0.15 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_theta.cir` |
| PDMOS80 | `vto_tempco` | -2.462 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80_vth_150.cir` |

## BJT

| device | FoM | measured | units | band | status | ×target | deck |
|---|---|---|---|---|---|---|---|
| NPN_HV | `bvcbo` | 37.84 | V | 40.5 – 49.5 | **hard-fail** | 0.841× | `pdk_validation/characterization/decks/bjt/NPN_HV_bvcbo.cir` |
| NPN_HV | `bvceo_implied` | 24.83 | V | 11.25 – 22.5 | **hard-fail** | 1.65× | `pdk_validation/characterization/decks/bjt/NPN_HV_bvceo.cir` |
| NPN_HV | `flicker_corner` | 3.016e+06 | Hz | 100 – 1e+04 | **expected-fail** <br>_F4 (kf/af placeholder, bias-independent)_ | 1.01e+03× | `pdk_validation/characterization/decks/bjt/NPN_HV_noise_100uA.cir` |
| NPN_HV | `beta_corner_spread` | 17.19 | percent | 20 – 30 | warn | 0.688× | `pdk_validation/characterization/decks/bjt/NPN_HV_gummel_TT.cir` |
| NPN_HV | `is_corner_spread` | 3.085 | mV | 10 – 30 | warn | 0.154× | `pdk_validation/characterization/decks/bjt/NPN_HV_gummel_TT.cir` |
| NPN_HV | `ft_at_peak` | 1.232 | GHz | 0.88 – 3.54 | descriptive <br>_anchor band contested (BCD junction BJT vs SiGe-class) -- open maintainer decision_ |  | `pdk_validation/characterization/decks/bjt/NPN_HV_ft.cir` |
| NPN_HV | `flicker_corner_bias_ratio` | 0.565 |  | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/NPN_HV_noise_100uA.cir` |
| NPN_HV | `is_extracted` | 4.013e-17 | A | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/NPN_HV_gummel_TT.cir` |
| NPN_HV | `n_ideality` | 1.001 |  | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/NPN_HV_gummel_TT.cir` |
| NPN_HV | `beta` | 62.46 |  | 48 – 128 | pass |  | `pdk_validation/characterization/decks/bjt/NPN_HV_gummel_TT.cir` |
| NPN_HV | `early_voltage` | 117.7 | V | 60 – 240 | pass |  | `pdk_validation/characterization/decks/bjt/NPN_HV_early.cir` |
| NPN_HV | `ft_times_bvceo_johnson` | 30.57 | GHz.V | 0 – 200 | pass |  | `pdk_validation/characterization/decks/bjt/NPN_HV_ft.cir` |
| NPN_HV | `vbe_at_100uA` | 0.7392 | V | 0.62 – 0.78 | pass |  | `pdk_validation/characterization/decks/bjt/NPN_HV_gummel_TT.cir` |
| NPN_LV | `bvcbo` | 11.77 | V | 12.6 – 15.4 | **hard-fail** | 0.841× | `pdk_validation/characterization/decks/bjt/NPN_LV_bvcbo.cir` |
| NPN_LV | `bvceo_implied` | 7.465 | V | 3.5 – 7 | **hard-fail** | 1.83× | `pdk_validation/characterization/decks/bjt/NPN_LV_bvceo.cir` |
| NPN_LV | `flicker_corner` | 2.966e+06 | Hz | 100 – 1e+04 | **expected-fail** <br>_F4 (kf/af placeholder, bias-independent)_ | 989× | `pdk_validation/characterization/decks/bjt/NPN_LV_noise_100uA.cir` |
| NPN_LV | `beta_corner_spread` | 17.81 | percent | 20 – 30 | warn | 0.713× | `pdk_validation/characterization/decks/bjt/NPN_LV_gummel_TT.cir` |
| NPN_LV | `is_corner_spread` | 2.994 | mV | 10 – 30 | warn | 0.15× | `pdk_validation/characterization/decks/bjt/NPN_LV_gummel_TT.cir` |
| NPN_LV | `ft_at_peak` | 2.703 | GHz | 1.77 – 7.07 | descriptive <br>_anchor band contested (BCD junction BJT vs SiGe-class) -- open maintainer decision_ |  | `pdk_validation/characterization/decks/bjt/NPN_LV_ft.cir` |
| NPN_LV | `flicker_corner_bias_ratio` | 0.4413 |  | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/NPN_LV_noise_100uA.cir` |
| NPN_LV | `is_extracted` | 2.007e-16 | A | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/NPN_LV_gummel_TT.cir` |
| NPN_LV | `n_ideality` | 1.001 |  | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/NPN_LV_gummel_TT.cir` |
| NPN_LV | `beta` | 113 |  | 84 – 224 | pass |  | `pdk_validation/characterization/decks/bjt/NPN_LV_gummel_TT.cir` |
| NPN_LV | `early_voltage` | 72.88 | V | 40 – 160 | pass |  | `pdk_validation/characterization/decks/bjt/NPN_LV_early.cir` |
| NPN_LV | `ft_times_bvceo_johnson` | 20.17 | GHz.V | 0 – 200 | pass |  | `pdk_validation/characterization/decks/bjt/NPN_LV_ft.cir` |
| NPN_LV | `vbe_at_100uA` | 0.6978 | V | 0.62 – 0.78 | pass |  | `pdk_validation/characterization/decks/bjt/NPN_LV_gummel_TT.cir` |
| PNP_HV | `flicker_corner` | 2.855e+06 | Hz | 100 – 1e+04 | **expected-fail** <br>_F4 (kf/af placeholder, bias-independent)_ | 952× | `pdk_validation/characterization/decks/bjt/PNP_HV_noise_100uA.cir` |
| PNP_HV | `beta_corner_spread` | 19.38 | percent | 20 – 30 | warn | 0.775× | `pdk_validation/characterization/decks/bjt/PNP_HV_gummel_TT.cir` |
| PNP_HV | `is_corner_spread` | 3.705 | mV | 10 – 30 | warn | 0.185× | `pdk_validation/characterization/decks/bjt/PNP_HV_gummel_TT.cir` |
| PNP_HV | `ft_at_peak` | 0.4705 | GHz | 0.32 – 1.27 | descriptive <br>_anchor band contested (BCD junction BJT vs SiGe-class) -- open maintainer decision_ |  | `pdk_validation/characterization/decks/bjt/PNP_HV_ft.cir` |
| PNP_HV | `bvcbo` | -- | V | 28.8 – 35.2 | error |  | `pdk_validation/characterization/decks/bjt/PNP_HV_bvcbo.cir` |
| PNP_HV | `bvceo_implied` | -- | V | 8 – 16 | error |  | `pdk_validation/characterization/decks/bjt/PNP_HV_bvceo.cir` |
| PNP_HV | `ft_times_bvceo_johnson` | -- | GHz.V | 0 – 200 | error |  | `pdk_validation/characterization/decks/bjt/PNP_HV_ft.cir` |
| PNP_HV | `flicker_corner_bias_ratio` | 0.5599 |  | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/PNP_HV_noise_100uA.cir` |
| PNP_HV | `is_extracted` | 1.004e-16 | A | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/PNP_HV_gummel_TT.cir` |
| PNP_HV | `n_ideality` | 1.032 |  | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/PNP_HV_gummel_TT.cir` |
| PNP_HV | `beta` | 16.31 |  | 11 – 29 | pass |  | `pdk_validation/characterization/decks/bjt/PNP_HV_gummel_TT.cir` |
| PNP_HV | `early_voltage` | 47.21 | V | 25 – 100 | pass |  | `pdk_validation/characterization/decks/bjt/PNP_HV_early.cir` |
| PNP_HV | `vbe_at_100uA` | 0.7386 | V | 0.62 – 0.78 | pass |  | `pdk_validation/characterization/decks/bjt/PNP_HV_gummel_TT.cir` |
| PNP_LAT | `flicker_corner` | 2.760e+06 | Hz | 100 – 1e+04 | **expected-fail** <br>_F4 (kf/af placeholder, bias-independent)_ | 920× | `pdk_validation/characterization/decks/bjt/PNP_LAT_noise_100uA.cir` |
| PNP_LAT | `beta_corner_spread` | 19.22 | percent | 20 – 30 | warn | 0.769× | `pdk_validation/characterization/decks/bjt/PNP_LAT_gummel_TT.cir` |
| PNP_LAT | `is_corner_spread` | 3.325 | mV | 10 – 30 | warn | 0.166× | `pdk_validation/characterization/decks/bjt/PNP_LAT_gummel_TT.cir` |
| PNP_LAT | `ft_at_peak` | 0.5566 | GHz | 0.44 – 1.77 | descriptive <br>_anchor band contested (BCD junction BJT vs SiGe-class) -- open maintainer decision_ |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_ft.cir` |
| PNP_LAT | `bvcbo` | -- | V | 16.2 – 19.8 | error |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_bvcbo.cir` |
| PNP_LAT | `bvceo_implied` | -- | V | 4.5 – 9 | error |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_bvceo.cir` |
| PNP_LAT | `ft_times_bvceo_johnson` | -- | GHz.V | 0 – 200 | error |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_ft.cir` |
| PNP_LAT | `flicker_corner_bias_ratio` | 0.4358 |  | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_noise_100uA.cir` |
| PNP_LAT | `is_extracted` | 8.021e-16 | A | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_gummel_TT.cir` |
| PNP_LAT | `n_ideality` | 1.023 |  | -- | no-anchor |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_gummel_TT.cir` |
| PNP_LAT | `beta` | 30.68 |  | 21 – 56 | pass |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_gummel_TT.cir` |
| PNP_LAT | `early_voltage` | 32.23 | V | 18 – 70 | pass |  | `pdk_validation/characterization/decks/bjt/PNP_LAT_early.cir` |
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
| DIO_SCH | `tt_transit_time` | 3.019e-10 | s | 0 – 1.000e-12 | **expected-fail** <br>_audit 4.6 (Schottky tt must be 0; majority-carrier device)_ |  | `pdk_validation/characterization/decks/diodes/DIO_SCH_diffcap.cir` |
| DIO_SCH | `cjo_density` | 140.3 | fF/um^2 | 0.5 – 2 | warn | 140× | `pdk_validation/characterization/decks/diodes/DIO_SCH_cjo.cir` |
| DIO_SCH | `qrr_at_10mA` | 3.019e-12 | C | -- | no-anchor |  | `pdk_validation/characterization/decks/diodes/DIO_SCH_diffcap.cir` |
| DIO_SCH | `bv` | 45.1 | V | 38.2 – 51.7 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_SCH_rev.cir` |
| DIO_SCH | `n_ideality` | 1.075 |  | 1.03 – 1.15 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_SCH_fwd.cir` |
| DIO_SCH | `vf_at_1mA` | 0.2914 | V | 0.247 – 0.335 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_SCH_fwd.cir` |
| DZ_12 | `bv_tempco` | -0.8814 | mV/degC | 4 – 12.8 | **expected-fail** <br>_audit 4.5 (no tbv1/tbv2 on the zener cards)_ | -0.11× | `pdk_validation/characterization/decks/diodes/DZ_12_rev_150C.cir` |
| DZ_12 | `cjo_density` | 5.5e+04 | fF/um^2 | 0.515 – 2.062 | **expected-fail** <br>_audit 4.4 (zener cjo is a hand-picked ladder)_ | 5.33e+04× | `pdk_validation/characterization/decks/diodes/DZ_12_cjo.cir` |
| DZ_12 | `bv` | 11.73 | V | 11.4 – 12.6 | pass |  | `pdk_validation/characterization/decks/diodes/DZ_12_rev_27C.cir` |
| DZ_12 | `tt_transit_time` | 5.518e-08 | s | 1.000e-08 – 1.000e-07 | pass |  | `pdk_validation/characterization/decks/diodes/DZ_12_diffcap.cir` |
| DZ_24 | `bv_tempco` | -0.7309 | mV/degC | 10 – 32 | **expected-fail** <br>_audit 4.5 (no tbv1/tbv2 on the zener cards)_ | -0.0365× | `pdk_validation/characterization/decks/diodes/DZ_24_rev_150C.cir` |
| DZ_24 | `cjo_density` | 2.8e+04 | fF/um^2 | 0.509 – 2.038 | **expected-fail** <br>_audit 4.4 (zener cjo is a hand-picked ladder)_ | 2.75e+04× | `pdk_validation/characterization/decks/diodes/DZ_24_cjo.cir` |
| DZ_24 | `bv` | 23.77 | V | 22.8 – 25.2 | pass |  | `pdk_validation/characterization/decks/diodes/DZ_24_rev_27C.cir` |
| DZ_24 | `tt_transit_time` | 7.492e-08 | s | 1.000e-08 – 1.000e-07 | pass |  | `pdk_validation/characterization/decks/diodes/DZ_24_diffcap.cir` |
| DZ_5V6 | `bv` | 5.243 | V | 5.32 – 5.88 | **hard-fail** | 0.936× | `pdk_validation/characterization/decks/diodes/DZ_5V6_rev_27C.cir` |
| DZ_5V6 | `bv_tempco` | -1.173 | mV/degC | 0.12 – 0.4 | **expected-fail** <br>_audit 4.5 (no tbv1/tbv2 on the zener cards)_ | -4.69× | `pdk_validation/characterization/decks/diodes/DZ_5V6_rev_150C.cir` |
| DZ_5V6 | `cjo_density` | 1.200e+05 | fF/um^2 | 1.663 – 6.652 | **expected-fail** <br>_audit 4.4 (zener cjo is a hand-picked ladder)_ | 3.61e+04× | `pdk_validation/characterization/decks/diodes/DZ_5V6_cjo.cir` |
| DZ_5V6 | `tt_transit_time` | 4.054e-08 | s | 1.000e-08 – 1.000e-07 | pass |  | `pdk_validation/characterization/decks/diodes/DZ_5V6_diffcap.cir` |

## Passives

| device | FoM | measured | units | band | status | ×target | deck |
|---|---|---|---|---|---|---|---|
| CFRINGE | `matching_A_C_pair_1sigma` | 0.3273 | %.um | 0.9 – 2.7 | **expected-fail** <br>_audit 5.2_ | 0.218× | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| CFRINGE | `golden_crosscheck` | -3.336e-08 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/CFRINGE_cv.cir` |
| CFRINGE | `density` | 0.181 | fF/um^2 | 0.1 – 0.5 | pass |  | `pdk_validation/characterization/decks/passives/CFRINGE_cv.cir` |
| CFRINGE | `implied_dielectric_thickness` | 195.7 | nm | 137.8 – 275.5 | pass |  | `pdk_validation/characterization/decks/passives/CFRINGE_cv.cir` |
| CFRINGE | `tcc_tc1` | 16.12 | ppm/degC | 6 – 38 | pass |  | `pdk_validation/characterization/decks/passives/CFRINGE_temp_150.cir` |
| CFRINGE | `vcc1` | 2.982 | ppm/V | 1 – 6 | pass |  | `pdk_validation/characterization/decks/passives/CFRINGE_cv.cir` |
| CMIM_HI | `matching_A_C_pair_1sigma` | 0.09361 | %.um | 0.45 – 1.35 | **expected-fail** <br>_audit 5.2_ | 0.125× | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| CMIM_HI | `golden_crosscheck` | -3.295e-10 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/CMIM_HI_cv.cir` |
| CMIM_HI | `density` | 2 | fF/um^2 | 2 – 4 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_HI_cv.cir` |
| CMIM_HI | `implied_dielectric_thickness` | 30.99 | nm | 21.7 – 43.4 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_HI_cv.cir` |
| CMIM_HI | `tcc_tc1` | 48.36 | ppm/degC | 18 – 112 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_HI_temp_150.cir` |
| CMIM_HI | `vcc1` | 59.97 | ppm/V | 24 – 120 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_HI_cv.cir` |
| CMIM_STD | `matching_A_C_pair_1sigma` | 0.07106 | %.um | 0.45 – 1.35 | **expected-fail** <br>_audit 5.2_ | 0.0947× | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| CMIM_STD | `golden_crosscheck` | 7.726e-11 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/CMIM_STD_cv.cir` |
| CMIM_STD | `density` | 1 | fF/um^2 | 1 – 2 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_STD_cv.cir` |
| CMIM_STD | `implied_dielectric_thickness` | 61.98 | nm | 43.4 – 86.8 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_STD_cv.cir` |
| CMIM_STD | `tcc_tc1` | 37.8 | ppm/degC | 14 – 88 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_STD_temp_150.cir` |
| CMIM_STD | `vcc1` | 29.99 | ppm/V | 12 – 60 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_STD_cv.cir` |
| CMOM | `matching_A_C_pair_1sigma` | 0.2991 | %.um | 0.9 – 2.7 | **expected-fail** <br>_audit 5.2_ | 0.199× | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| CMOM | `golden_crosscheck` | -7.136e-08 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/CMOM_cv.cir` |
| CMOM | `density` | 0.35 | fF/um^2 | 0.3 – 1 | pass |  | `pdk_validation/characterization/decks/passives/CMOM_cv.cir` |
| CMOM | `implied_dielectric_thickness` | 101.2 | nm | 70.8 – 141.7 | pass |  | `pdk_validation/characterization/decks/passives/CMOM_cv.cir` |
| CMOM | `tcc_tc1` | 21.68 | ppm/degC | 8 – 50 | pass |  | `pdk_validation/characterization/decks/passives/CMOM_temp_150.cir` |
| CMOM | `vcc1` | 4.998 | ppm/V | 2 – 10 | pass |  | `pdk_validation/characterization/decks/passives/CMOM_cv.cir` |
| RNPLUS | `matching_A_R_pair_1sigma` | 0.236 | %.um | 1.5 – 4.5 | **expected-fail** <br>_audit 5.2 (passive matching 3-14x optimistic)_ | 0.0944× | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| RNPLUS | `rsh` | 32 | Ohm/sq | 50 – 150 | warn | 0.32× | `pdk_validation/characterization/decks/passives/RNPLUS_rsh.cir` |
| RNPLUS | `tc1` | 984 | ppm/degC | 1000 – 2000 | warn | 0.656× | `pdk_validation/characterization/decks/passives/RNPLUS_temp_150.cir` |
| RNPLUS | `golden_crosscheck` | 1.008e-07 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/RNPLUS_rv.cir` |
| RNPLUS | `rsh_corner_spread` | 12 | percent | 10 – 25 | pass |  | `pdk_validation/characterization/decks/passives/RNPLUS_corner_TT.cir` |
| RNPLUS | `vcr1` | 1500 | ppm/V | 750 – 3000 | pass |  | `pdk_validation/characterization/decks/passives/RNPLUS_rv.cir` |
| RNWELL | `matching_A_R_pair_1sigma` | 0.6675 | %.um | 2.4 – 7.2 | **expected-fail** <br>_audit 5.2 (passive matching 3-14x optimistic)_ | 0.167× | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| RNWELL | `golden_crosscheck` | -2.155e-08 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/RNWELL_rv.cir` |
| RNWELL | `rsh` | 1801 | Ohm/sq | 1000 – 2000 | pass |  | `pdk_validation/characterization/decks/passives/RNWELL_rsh.cir` |
| RNWELL | `rsh_corner_spread` | 12 | percent | 10 – 25 | pass |  | `pdk_validation/characterization/decks/passives/RNWELL_corner_TT.cir` |
| RNWELL | `tc1` | 4280 | ppm/degC | 3000 – 6000 | pass |  | `pdk_validation/characterization/decks/passives/RNWELL_temp_150.cir` |
| RNWELL | `vcr1` | 8000 | ppm/V | 4000 – 1.6e+04 | pass |  | `pdk_validation/characterization/decks/passives/RNWELL_rv.cir` |
| RPOLY_HI | `matching_A_R_pair_1sigma` | 0.3638 | %.um | 0.9 – 2.7 | **expected-fail** <br>_audit 5.2 (passive matching 3-14x optimistic)_ | 0.243× | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| RPOLY_HI | `tc1` | 656 | ppm/degC | -1500 – -500 | **expected-fail** <br>_F7 (lightly-doped poly tc1 sign)_ | -0.656× | `pdk_validation/characterization/decks/passives/RPOLY_HI_temp_150.cir` |
| RPOLY_HI | `golden_crosscheck` | -5.146e-08 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/RPOLY_HI_rv.cir` |
| RPOLY_HI | `rsh` | 1200 | Ohm/sq | 1000 – 2000 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_HI_rsh.cir` |
| RPOLY_HI | `rsh_corner_spread` | 12 | percent | 10 – 25 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_HI_corner_TT.cir` |
| RPOLY_HI | `vcr1` | 200 | ppm/V | 100 – 400 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_HI_rv.cir` |
| RPOLY_LO | `matching_A_R_pair_1sigma` | 0.1466 | %.um | 0.9 – 2.7 | **expected-fail** <br>_audit 5.2 (passive matching 3-14x optimistic)_ | 0.0978× | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| RPOLY_LO | `rsh` | 25 | Ohm/sq | 100 – 400 | warn | 0.1× | `pdk_validation/characterization/decks/passives/RPOLY_LO_rsh.cir` |
| RPOLY_LO | `golden_crosscheck` | 6.181e-08 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/RPOLY_LO_rv.cir` |
| RPOLY_LO | `rsh_corner_spread` | 12 | percent | 10 – 25 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_LO_corner_TT.cir` |
| RPOLY_LO | `tc1` | 1112 | ppm/degC | 500 – 3000 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_LO_temp_150.cir` |
| RPOLY_LO | `vcr1` | 50 | ppm/V | 25 – 100 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_LO_rv.cir` |
| RPPLUS | `matching_A_R_pair_1sigma` | 0.2779 | %.um | 1.5 – 4.5 | **expected-fail** <br>_audit 5.2 (passive matching 3-14x optimistic)_ | 0.111× | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| RPPLUS | `golden_crosscheck` | 2.320e-07 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/RPPLUS_rv.cir` |
| RPPLUS | `rsh` | 58.01 | Ohm/sq | 50 – 150 | pass |  | `pdk_validation/characterization/decks/passives/RPPLUS_rsh.cir` |
| RPPLUS | `rsh_corner_spread` | 12 | percent | 10 – 25 | pass |  | `pdk_validation/characterization/decks/passives/RPPLUS_corner_TT.cir` |
| RPPLUS | `tc1` | 1190 | ppm/degC | 1000 – 2500 | pass |  | `pdk_validation/characterization/decks/passives/RPPLUS_temp_150.cir` |
| RPPLUS | `vcr1` | 1800 | ppm/V | 900 – 3600 | pass |  | `pdk_validation/characterization/decks/passives/RPPLUS_rv.cir` |

## Discrimination experiments (§D)

Full payloads in the results JSON under `_experiments`; verdicts in
`pdk_validation/characterization/experiments/README.md`.

| experiment | verdict |
|---|---|
| `d1_kp_convention` | {'convention': 'kp/2', 'one_word': 'kp/2', 'measured_ratio_A_over_kp': 0.49999999862503397, 'statement': 'ngspice-45 VDMOS saturation current is Id = (kp/2)*Vov^2. The fitted prefactor is 0.11 A/V^2 against a card kp of 0.22, a ratio of 0.5000 -- indistinguishable from 1/2, so the model carries the standard SPICE factor-of-two internally and kp is a TRANSCONDUCTANCE PARAMETER, not the saturation prefactor.', 'corrected_and_uncorrected_agree': True, 'robustness': 'The uncorrected fit gives A/kp = 0.4816 and the theta/lambda-corrected fit 0.5000. Both land on the same side of the fork, so the verdict does not depend on the correction -- the two candidates are a factor of two apart and the corrections are single-digit percent.'} |
| `d2_ksubthres` | {'semantics': 'ksubthres is a per-DECADE slope; the natural-log (ln10) reading is excluded. Measured S ~= 1.171 * (1000*ksubthres) mV/dec, R^2 = 0.9998 over 13 cards.', 'phase1_2_8_slope_finding': 'SURVIVES -- the ladder still slopes wrong', 'phase1_2_8_sub_boltzmann_finding': 'OVERTURNED -- NDMOS200 n = 1.19, not 1.01', 'overturns_phase_1': True, 'plain_statement': "Audit 2.8 made two claims and D2 splits them.\n  The STRUCTURAL claim -- that the swing ladder slopes the wrong way with voltage class, when n = 1 + C_dep/Cox demands it rise -- is CONFIRMED. It is the real defect, it is unaffected by the semantics correction, and it is what the fix worklist should act on.\n  The HEADLINE claim -- that NDMOS200 sits at n = 1.01, 'essentially ideal', below the room-temperature Boltzmann floor and therefore physically impossible -- is OVERTURNED. It came from reading ksubthres as if it were S in V/dec. Measured, NDMOS200 swings at 70.7 mV/dec for n = 1.19. Low, but ordinary -- there is no perfect gate and nothing unphysical. Every one of the 13 cards sits above n = 1 once measured.\nPhase 1 had to assume the semantics because nothing in the PDK states them. D2 measured them, twice, by independent routes that agree. Where they conflict, the measurement wins.", 'consequence_for_worklist': "The 'NDMOS200 is sub-Boltzmann' line item should be STRUCK from the fix worklist -- there is nothing to fix. The 'ksubthres ladder slopes the wrong way' item stands, and its severity is unchanged (it sets the subthreshold gm/Id ceiling, which is what HANDOFF_dmos200_subthreshold_analog.md turns on). Any re-laddering of ksubthres must be done against MEASURED S, not against 1000*ksubthres: the conversion is S ~= 1.171 * 1000 * ksubthres, so a card targeting S = 90 mV/dec needs ksubthres ~= 0.0769, not 0.090.", 'consequence_for_anchor': "docs/anchor-values.json: add the measured mapping S_mV_per_dec = 1.171 * 1000 * ksubthres (D2, R^2 = 0.9998, 13 cards) next to the subthreshold_swing entry, and correct any note that asserts 'the card's ksubthres IS S in V/dec by construction' -- families/vdmos.py carries exactly that wording in _do_idvg's model_ksubthres_note and it is off by 17%. No anchor BAND changes: the measured swings land where the anchor already expected them to."} |
| `d3_rdrs_isolation` | {'series_share_of_measured_ron': {'NDMOS20': 0.30309929057233653, 'NDMOS200': 0.39154844758848323}, 'channel_only_ron_times_w_ohm_um': {'NDMOS20': 1.6099207178443289, 'NDMOS200': 27.224781956721312}, 'disagreement_swing_across_family_before_x': 30.375, 'disagreement_swing_across_family_after_x': 40.1891128512613, 'one_line': 'TWO INDEPENDENT SLIPS -- the disagreement survives', 'statement': "The decomposition is clean: subtracting the rd=rs=0 on-resistance from the stock one recovers the card's own rd+rs to 0.03% (NDMOS20) and 0.11% (NDMOS200), so Ron really does separate into a channel term and a series term and the split below can be trusted.\nSeries resistance is only 30.3% of NDMOS20's Ron and 39.2% of NDMOS200's -- the CHANNEL dominates both, which audit 2.2 did not allow for.\nTwo consequences, pulling in opposite directions.\n  (1) The kp route is CLEAN. Removing rd/rs lifts Idsat density by 1.239x on NDMOS20 and 1.411x on NDMOS200, against implied-width gaps of 3649x and 287x. Series resistance explains under 0.2% of the kp finding. F1's kp half cannot be blamed on rd/rs.\n  (2) The Ron route was MISATTRIBUTED. Audit 2.2 took the card's whole on-resistance to be rd+rs, but rd+rs are only 30%/39% of it, so its implied widths are overstated by 3.30x and 2.55x. Re-cast on the total measured Ron they become 288x and 911x.\nThe disagreement therefore does not collapse -- it MOVES. It goes from 2.43x/0.08x to 12.66x/0.31x, and the swing across the family widens from 30x to 40x. These are two genuinely independent defects, as audit 2.5 concluded, and the correction makes the case stronger rather than weaker.", 'channel_only_number_for_the_rd_rs_rederivation': 'NDMOS20 1.61 Ohm.um, NDMOS200 27.22 Ohm.um, at Vov = 4 V and Vds = 0.1 V. This is a FLOOR. Whatever rd/rs are re-derived to, total Ron*W can never fall below these, because this is the channel resistance the same kp that sets Idsat also sets. Two things follow. First, any rd/rs proposal must be checked against it -- a divisor that would drive total Ron*W near or below the channel-only value is arithmetically impossible, not merely optimistic. Second, and more awkwardly, the channel-only floor is itself set by the same defective kp: fixing kp downward RAISES this floor, so fix #2 and fix #3 are coupled through it even though the defects are independent. Re-derive rd/rs AFTER kp, not before.', 'consequence': "For the fix worklist:\n  * Fix #2 (kp) is untouched by rd/rs and can be scoped on its own evidence. D3 closes off 'maybe it is just series resistance'.\n  * Fix #3 (rd/rs) needs audit 2.2's implied-width table RECOMPUTED, because that table divided by rd+rs where it should have divided by the full on-resistance. The correction is 3.30x at 20 V and 2.55x at 200 V -- not uniform, so it also slightly steepens what audit 2.2 called a flat ratio. That does not overturn the 'one divisor' verdict for rd/rs (a 1.3x tilt inside a ~10^3 slip is noise), but the table should be reissued with the measured split.\n  * Ordering: re-derive kp first, then rd/rs against the resulting channel-only floor."} |
| `d4_kp_ladder_shape` | {'spread_all_13': {'a_flat_tox_x': 18.181818181818176, 'b_theta_tox_x': 7.0895724661410355, 'flattening_factor': 2.5645859843668153}, 'spread_n_channel': {'a_flat_tox_x': 12.727272727272725, 'b_theta_tox_x': 5.475262931186852, 'flattening_factor': 2.324504391337766}, 'spread_p_channel': {'a_flat_tox_x': 14.772727272727273, 'b_theta_tox_x': 6.715547004009489}, 'one_line': 'NEITHER -- fewer than thirteen, more than one', 'statement': 'The theta-implied oxide ladder FLATTENS the residual substantially but does not flatten it to one number.\n  Hypothesis (a), tox = 30 nm flat: the implied-width ratio spans 12.7x across the n-channel cards (3649x down to 287x) and 18.2x across all thirteen.\n  Hypothesis (b), theta-implied tox ladder: 5.5x n-channel, 7.1x across all thirteen.\nSo the tox ladder removes 2.3x of the 12.7x n-channel slope -- most of it -- but leaves 5.5x behind. That is the answer to the question as posed: the sloped residual is REAL but it is mostly an artifact of the flat-tox assumption, not mostly a real kp ladder error.\nMechanically the result is simple. Under (b), tox ~ 1/theta, so Cox ~ theta and W ~ kp/theta. kp falls 12.7x across the n-channel family while theta falls 2.2x, so the residual falls by the ratio. The kp ladder and the theta ladder are laddered together but not proportionally.', 'ruling_on_fix_2': "NOT thirteen re-derivations. A 5.5x spread does not justify thirteen independent physical derivations -- it is the same order as the 2.8x spread audit 2.2 was willing to call 'roughly flat' and fix with a single divisor for rd/rs. It is also not cleanly one divisor: a single divisor would leave a 5.5x residual, which is more than the measurement error and would show up as a real drive-current ladder error across voltage classes.\nRECOMMENDATION: one divisor plus a per-class trim -- six numbers (one per voltage class), not thirteen, and not one. Derive the divisor from the family geometric mean and let the per-class trim absorb the residual ladder. If the maintainer will accept a 2x drive-current error at the extremes of the family, one divisor is defensible and fix #2 becomes as cheap as fix #3.", 'MAINTAINER_DECISION_REQUIRED': '*** THIS EXPERIMENT DOES NOT DECIDE THE OXIDE LADDER. ***\nEverything above is conditional on the maintainer DECLARING tox per VDMOS voltage class. The PDK never states it, and audit 2.7 already recommends stating it because three separate findings depend on it. D4 tells the maintainer what each declaration implies:\n  * Declare tox = 30 nm flat  -> implied-width residual spans 12.7x n-channel -> fix #2 is a per-card job, thirteen re-derivations, as phase 1 scoped it.\n  * Declare the theta-implied rising ladder -> residual spans 5.5x -> fix #2 collapses to one divisor plus at most a per-class trim.\nThe theta-implied ladder is the better-supported of the two -- it is derived from a card parameter rather than assumed, it is monotonic and correctly ordered, and a rising tox with voltage class is what the process would actually do. But it is in tension with the vto = 1.00-1.31 V the cards carry, which for LDMOS body doping suggests a THINNER oxide, and D4 cannot resolve that tension. It is a process-declaration question, not a simulation question.\nDo not apply fix #2 in either scoping until tox is declared.', 'consequence_for_anchor': 'docs/anchor-values.json: _vdmos_kp_conditional currently forks on decision_A_10um_cell vs decision_B_power_die. D4 shows a SECOND, orthogonal fork -- the oxide ladder -- that changes the SHAPE of the kp fix rather than its magnitude. Propose adding a `_vdmos_tox_conditional` block alongside it recording the two hypotheses, their measured residual spreads (12.7x flat vs 5.5x laddered, n-channel), and the theta-implied tox band per class from the table above. The existing kp_n/kp_p targets are computed at tox 20-50 nm and would need restating per class under the laddered hypothesis. MAINTAINER APPLIES; do not edit the anchor from this experiment.'} |

## Measurement errors (14)

| device | FoM | error |
|---|---|---|
| NMOS18 | `flicker_corner` | no crossover in 1Hz-1GHz (consistent with F3) |
| PMOS18 | `flicker_corner` | no crossover in 1Hz-1GHz (consistent with F3) |
| NMOS33 | `flicker_corner` | no crossover in 1Hz-1GHz (consistent with F3) |
| PMOS33 | `flicker_corner` | no crossover in 1Hz-1GHz (consistent with F3) |
| NMOS50 | `flicker_corner` | no crossover in 1Hz-1GHz (consistent with F3) |
| PMOS50 | `flicker_corner` | no crossover in 1Hz-1GHz (consistent with F3) |
| NMOS12 | `flicker_corner` | no crossover in 1Hz-1GHz (consistent with F3) |
| PMOS12 | `flicker_corner` | no crossover in 1Hz-1GHz (consistent with F3) |
| PNP_LAT | `bvceo_implied` | BVCEO is not measurable: the collector current never leaves the leakage floor (max |I| = 2.08e-11 A) anywhere in the sweep, so there is no breakdown to find. ROOT CAUSE (PDK defect, not a harness failure): the Bavl avalanche branch in the .subckt uses min(max(V(ci,b)/BVCBO,0),0.997) with a POSITIVE BVCBO .param. On a PNP the collector is below the base in normal operation, so V(ci,b) < 0, the max(...,0) clamps the argument to zero, and the multiplication factor is identically 1. The branch is dead code on both PNPs: PNP_LAT and PNP_HV have NO modelled collector breakdown at any voltage. The expression is the NPN one copy-pasted without a sign flip. This is unmeasurable until the wrapper is fixed. |
| PNP_LAT | `bvcbo` | BVCBO is not measurable: the collector current never leaves the leakage floor (max |I| = 6.08e-11 A) anywhere in the sweep, so there is no breakdown to find. ROOT CAUSE (PDK defect, not a harness failure): the Bavl avalanche branch in the .subckt uses min(max(V(ci,b)/BVCBO,0),0.997) with a POSITIVE BVCBO .param. On a PNP the collector is below the base in normal operation, so V(ci,b) < 0, the max(...,0) clamps the argument to zero, and the multiplication factor is identically 1. The branch is dead code on both PNPs: PNP_LAT and PNP_HV have NO modelled collector breakdown at any voltage. The expression is the NPN one copy-pasted without a sign flip. This is unmeasurable until the wrapper is fixed. |
| PNP_LAT | `ft_times_bvceo_johnson` | needs both ft_at_peak and bvceo_implied; ft=556567183.0288107 bvceo=None |
| PNP_HV | `bvceo_implied` | BVCEO is not measurable: the collector current never leaves the leakage floor (max |I| = 3.62e-11 A) anywhere in the sweep, so there is no breakdown to find. ROOT CAUSE (PDK defect, not a harness failure): the Bavl avalanche branch in the .subckt uses min(max(V(ci,b)/BVCBO,0),0.997) with a POSITIVE BVCBO .param. On a PNP the collector is below the base in normal operation, so V(ci,b) < 0, the max(...,0) clamps the argument to zero, and the multiplication factor is identically 1. The branch is dead code on both PNPs: PNP_LAT and PNP_HV have NO modelled collector breakdown at any voltage. The expression is the NPN one copy-pasted without a sign flip. This is unmeasurable until the wrapper is fixed. |
| PNP_HV | `bvcbo` | BVCBO is not measurable: the collector current never leaves the leakage floor (max |I| = 6.02e-11 A) anywhere in the sweep, so there is no breakdown to find. ROOT CAUSE (PDK defect, not a harness failure): the Bavl avalanche branch in the .subckt uses min(max(V(ci,b)/BVCBO,0),0.997) with a POSITIVE BVCBO .param. On a PNP the collector is below the base in normal operation, so V(ci,b) < 0, the max(...,0) clamps the argument to zero, and the multiplication factor is identically 1. The branch is dead code on both PNPs: PNP_LAT and PNP_HV have NO modelled collector breakdown at any voltage. The expression is the NPN one copy-pasted without a sign flip. This is unmeasurable until the wrapper is fixed. |
| PNP_HV | `ft_times_bvceo_johnson` | needs both ft_at_peak and bvceo_implied; ft=470539481.6459603 bvceo=None |

## Delta vs the phase-1 static audit

Every FoM where the measurement disagrees with the phase-1 static prediction
by more than 2× or crosses a verdict boundary is listed in
[`audit-vs-measurement-discrepancies.md`](audit-vs-measurement-discrepancies.md),
with the measured value declared authoritative and the corrected anchor entry
spelled out. That document is the input to the next anchor revision.
