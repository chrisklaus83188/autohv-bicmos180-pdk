# Characterization Scorecard — AutoHV BiCMOS180 PDK (phase 4 — grounded + fixed)

**This is the after-picture.** The phase-1/2/3 grounding passes and the phase-3/4 fix
batches have landed; the PDK is measured against the amended, literature-grounded anchors
(`anchor-values.json` v4.0-phase4-grounded). Diff against the phase-2 baseline in git history.

- ngspice: `ngspice-45 : Circuit level simulation program`
- generated: 2026-07-25T16:06:10+00:00
- wall time: 352.2 s
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
| `hard-fail` | 20 |
| `warn` | 75 |
| `descriptive` | 4 |
| `artifact` | 28 |
| `error` | 6 |
| `no-anchor` | 130 |
| `pass` | 298 |
| **total** | **561** |

### By family

| family | hard-fail | warn | descriptive | artifact | error | no-anchor | pass |
|---|---|---|---|---|---|---|---|
| BJT | 4 | 12 | 4 | 0 | 6 | 12 | 14 |
| BSIM3 MOS | 2 | 54 | 0 | 0 | 0 | 42 | 40 |
| Diodes/zeners | 4 | 4 | 0 | 0 | 0 | 1 | 19 |
| Other | 0 | 0 | 0 | 2 | 0 | 5 | 15 |
| Passives | 0 | 2 | 0 | 0 | 0 | 9 | 43 |
| VDMOS | 10 | 3 | 0 | 26 | 0 | 61 | 167 |

**Hard-fails not predicted by phase 1: 20.** These are the rows to read first — everything else was already known.

## Unexpected hard-fails

| device | FoM | measured | band | ×target | deck |
|---|---|---|---|---|---|
| DZ_12V | `cjo_density` | 5.5e+04 fF/um^2 | 0.515 – 2.062 | 5.33e+04× | `pdk_validation/characterization/decks/diodes/DZ_12V_cjo.cir` |
| DZ_24V | `cjo_density` | 2.8e+04 fF/um^2 | 0.509 – 2.038 | 2.75e+04× | `pdk_validation/characterization/decks/diodes/DZ_24V_cjo.cir` |
| DZ_5V6 | `bv` | 5.243 V | 5.32 – 5.88 | 0.936× | `pdk_validation/characterization/decks/diodes/DZ_5V6_rev_27C.cir` |
| DZ_5V6 | `cjo_density` | 1.200e+05 fF/um^2 | 1.663 – 6.652 | 3.61e+04× | `pdk_validation/characterization/decks/diodes/DZ_5V6_cjo.cir` |
| NDMOS120V | `theta` | 1.001 1/V | 0.05 – 0.3 | 6.67× | `pdk_validation/characterization/decks/vdmos/NDMOS120V_theta.cir` |
| NDMOS200V | `theta` | 1.339 1/V | 0.05 – 0.3 | 8.93× | `pdk_validation/characterization/decks/vdmos/NDMOS200V_theta.cir` |
| NDMOS40V | `theta` | 0.4898 1/V | 0.05 – 0.45 | 3.27× | `pdk_validation/characterization/decks/vdmos/NDMOS40V_theta.cir` |
| NDMOS60V | `theta` | 0.5975 1/V | 0.05 – 0.45 | 3.98× | `pdk_validation/characterization/decks/vdmos/NDMOS60V_theta.cir` |
| NDMOS80V | `theta` | 0.7386 1/V | 0.05 – 0.45 | 4.92× | `pdk_validation/characterization/decks/vdmos/NDMOS80V_theta.cir` |
| NMOS12V | `cox` | 1.103 fF/um^2 | 0.95 – 0 | -- | `pdk_validation/characterization/decks/bsim3_mos/NMOS12V_caps.cir` |
| NPN_HV | `bvcbo` | 37.84 V | 40.5 – 49.5 | 0.841× | `pdk_validation/characterization/decks/bjt/NPN_HV_bvcbo.cir` |
| NPN_HV | `bvceo_implied` | 24.83 V | 11.25 – 22.5 | 1.65× | `pdk_validation/characterization/decks/bjt/NPN_HV_bvceo.cir` |
| NPN_LV | `bvcbo` | 11.77 V | 12.6 – 15.4 | 0.841× | `pdk_validation/characterization/decks/bjt/NPN_LV_bvcbo.cir` |
| NPN_LV | `bvceo_implied` | 7.465 V | 3.5 – 7 | 1.83× | `pdk_validation/characterization/decks/bjt/NPN_LV_bvceo.cir` |
| PDMOS120V | `theta` | 0.9206 1/V | 0.05 – 0.3 | 6.14× | `pdk_validation/characterization/decks/vdmos/PDMOS120V_theta.cir` |
| PDMOS200V | `cjo_per_cell` | 16.97 fF | 20.2 – 247.1 | 0.24× | `pdk_validation/characterization/decks/vdmos/PDMOS200V_cap_0p1.cir` |
| PDMOS200V | `theta` | 1.341 1/V | 0.05 – 0.3 | 8.94× | `pdk_validation/characterization/decks/vdmos/PDMOS200V_theta.cir` |
| PDMOS60V | `theta` | 0.4958 1/V | 0.05 – 0.45 | 3.31× | `pdk_validation/characterization/decks/vdmos/PDMOS60V_theta.cir` |
| PDMOS80V | `theta` | 0.6388 1/V | 0.05 – 0.45 | 4.26× | `pdk_validation/characterization/decks/vdmos/PDMOS80V_theta.cir` |
| PMOS12V | `cox` | 1.007 fF/um^2 | 0.95 – 0 | -- | `pdk_validation/characterization/decks/bsim3_mos/PMOS12V_caps.cir` |

## BSIM3 MOS

| device | FoM | measured | units | band | status | ×target | deck |
|---|---|---|---|---|---|---|---|
| NMOS12V | `cox` | 1.103 | fF/um^2 | 0.95 – 0 | **hard-fail** |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12V_caps.cir` |
| NMOS12V | `cj_area` | 1.82 | fF/um^2 | 0.245 – 0.49 | warn | 5.2× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12V_caps.cir` |
| NMOS12V | `cjsw_sidewall` | 0.4333 | fF/um | 0.05 – 0.15 | warn | 4.33× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12V_caps.cir` |
| NMOS12V | `idsat_corner_spread` | 8.485 | percent | 12 – 20 | warn | 0.53× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12V_corner_TT.cir` |
| NMOS12V | `idsat_density` | 1.018 | mA/um | 0.2 – 0.4 | warn | 3.39× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12V_idsat.cir` |
| NMOS12V | `subthreshold_swing` | 184.6 | mV/dec | 72 – 96 | warn | 2.31× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12V_idvg.cir` |
| NMOS12V | `vth_corner_spread` | 80 | mV | 90 – 130 | warn | 0.727× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12V_corner_TT.cir` |
| NMOS12V | `vth_lin` | 1.466 | V | 1.29 – 1.41 | warn | 1.09× | `pdk_validation/characterization/decks/bsim3_mos/NMOS12V_idvg.cir` |
| NMOS12V | `idsat_density_L1u` | 0.1854 | mA/um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12V_idsat.cir` |
| NMOS12V | `mc_avt_implied_1sigma` | 28.21 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS12V_mc_s0.cir` |
| NMOS12V | `mc_sigma_di_over_i` | 0.6063 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS12V_mc_s0.cir` |
| NMOS12V | `mc_sigma_dvth_1sigma` | 12.62 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS12V_mc_s0.cir` |
| NMOS12V | `mc_sigma_vth_per_device_1sigma` | 8.921 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS12V_mc_s0.cir` |
| NMOS12V | `vth_model_internal` | 1.327 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12V_corner_TT.cir` |
| NMOS12V | `cgso_overlap` | 0.2072 | fF/um | 0.09 – 0.24 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12V_caps.cir` |
| NMOS12V | `flicker_corner` | 5.012e+05 | Hz | 2e+04 – 1.000e+06 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12V_noise.cir` |
| NMOS12V | `junction_perimeter_set` | 1 | boolean | 1 – 1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12V_caps.cir` |
| NMOS12V | `vth_tempco` | -1.599 | mV/degC | -1.8 – -1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS12V_temp_150.cir` |
| NMOS1V8 | `cj_area` | 2.22 | fF/um^2 | 0.7 – 1.4 | warn | 2.22× | `pdk_validation/characterization/decks/bsim3_mos/NMOS1V8_caps.cir` |
| NMOS1V8 | `cjsw_sidewall` | 0.5286 | fF/um | 0.05 – 0.15 | warn | 5.29× | `pdk_validation/characterization/decks/bsim3_mos/NMOS1V8_caps.cir` |
| NMOS1V8 | `flicker_corner` | 2.512e+06 | Hz | 2e+04 – 1.000e+06 | warn | 12.6× | `pdk_validation/characterization/decks/bsim3_mos/NMOS1V8_noise.cir` |
| NMOS1V8 | `idsat_corner_spread` | 25.23 | percent | 12 – 20 | warn | 1.58× | `pdk_validation/characterization/decks/bsim3_mos/NMOS1V8_corner_TT.cir` |
| NMOS1V8 | `idsat_density` | 0.5429 | mA/um | 0.55 – 0.6 | warn | 0.944× | `pdk_validation/characterization/decks/bsim3_mos/NMOS1V8_idsat.cir` |
| NMOS1V8 | `vth_corner_spread` | 79 | mV | 90 – 130 | warn | 0.718× | `pdk_validation/characterization/decks/bsim3_mos/NMOS1V8_corner_TT.cir` |
| NMOS1V8 | `vth_lin` | 0.6301 | V | 0.42 – 0.54 | warn | 1.31× | `pdk_validation/characterization/decks/bsim3_mos/NMOS1V8_idvg.cir` |
| NMOS1V8 | `vth_tempco` | -0.9995 | mV/degC | -1.8 – -1 | warn | 0.714× | `pdk_validation/characterization/decks/bsim3_mos/NMOS1V8_temp_150.cir` |
| NMOS1V8 | `mc_avt_implied_1sigma` | 3.362 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS1V8_mc_s0.cir` |
| NMOS1V8 | `mc_sigma_di_over_i` | 0.8353 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS1V8_mc_s0.cir` |
| NMOS1V8 | `mc_sigma_dvth_1sigma` | 1.503 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS1V8_mc_s0.cir` |
| NMOS1V8 | `mc_sigma_vth_per_device_1sigma` | 1.063 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS1V8_mc_s0.cir` |
| NMOS1V8 | `vth_model_internal` | 0.604 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS1V8_corner_TT.cir` |
| NMOS1V8 | `cgso_overlap` | 0.3198 | fF/um | 0.132 – 0.352 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS1V8_caps.cir` |
| NMOS1V8 | `cox` | 7.704 | fF/um^2 | 7.333 – 8.531 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS1V8_caps.cir` |
| NMOS1V8 | `junction_perimeter_set` | 1 | boolean | 1 – 1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS1V8_caps.cir` |
| NMOS1V8 | `subthreshold_swing` | 79.05 | mV/dec | 72 – 96 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS1V8_idvg.cir` |
| NMOS3V3 | `cj_area` | 2.02 | fF/um^2 | 0.574 – 1.148 | warn | 2.46× | `pdk_validation/characterization/decks/bsim3_mos/NMOS3V3_caps.cir` |
| NMOS3V3 | `cjsw_sidewall` | 0.481 | fF/um | 0.05 – 0.15 | warn | 4.81× | `pdk_validation/characterization/decks/bsim3_mos/NMOS3V3_caps.cir` |
| NMOS3V3 | `idsat_corner_spread` | 20.6 | percent | 12 – 20 | warn | 1.29× | `pdk_validation/characterization/decks/bsim3_mos/NMOS3V3_corner_TT.cir` |
| NMOS3V3 | `idsat_density` | 0.4484 | mA/um | 0.45 – 0.55 | warn | 0.897× | `pdk_validation/characterization/decks/bsim3_mos/NMOS3V3_idsat.cir` |
| NMOS3V3 | `vth_corner_spread` | 79.59 | mV | 90 – 130 | warn | 0.724× | `pdk_validation/characterization/decks/bsim3_mos/NMOS3V3_corner_TT.cir` |
| NMOS3V3 | `vth_lin` | 0.8095 | V | 0.6 – 0.72 | warn | 1.23× | `pdk_validation/characterization/decks/bsim3_mos/NMOS3V3_idvg.cir` |
| NMOS3V3 | `mc_avt_implied_1sigma` | 4.149 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS3V3_mc_s0.cir` |
| NMOS3V3 | `mc_sigma_di_over_i` | 0.4488 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS3V3_mc_s0.cir` |
| NMOS3V3 | `mc_sigma_dvth_1sigma` | 1.855 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS3V3_mc_s0.cir` |
| NMOS3V3 | `mc_sigma_vth_per_device_1sigma` | 1.312 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS3V3_mc_s0.cir` |
| NMOS3V3 | `vth_model_internal` | 0.7696 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS3V3_corner_TT.cir` |
| NMOS3V3 | `cgso_overlap` | 0.2896 | fF/um | 0.12 – 0.32 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS3V3_caps.cir` |
| NMOS3V3 | `cox` | 4.996 | fF/um^2 | 4.617 – 5.372 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS3V3_caps.cir` |
| NMOS3V3 | `flicker_corner` | 3.981e+05 | Hz | 2e+04 – 1.000e+06 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS3V3_noise.cir` |
| NMOS3V3 | `junction_perimeter_set` | 1 | boolean | 1 – 1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS3V3_caps.cir` |
| NMOS3V3 | `subthreshold_swing` | 92.51 | mV/dec | 72 – 96 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS3V3_idvg.cir` |
| NMOS3V3 | `vth_tempco` | -1.333 | mV/degC | -1.8 – -1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS3V3_temp_150.cir` |
| NMOS5V0 | `cj_area` | 1.82 | fF/um^2 | 1.1 – 1.6 | warn | 1.3× | `pdk_validation/characterization/decks/bsim3_mos/NMOS5V0_caps.cir` |
| NMOS5V0 | `cjsw_sidewall` | 0.4333 | fF/um | 0.05 – 0.15 | warn | 4.33× | `pdk_validation/characterization/decks/bsim3_mos/NMOS5V0_caps.cir` |
| NMOS5V0 | `idsat_density` | 0.3054 | mA/um | 0.48 – 0.6 | warn | 0.566× | `pdk_validation/characterization/decks/bsim3_mos/NMOS5V0_idsat.cir` |
| NMOS5V0 | `subthreshold_swing` | 121.1 | mV/dec | 85 – 100 | warn | 1.28× | `pdk_validation/characterization/decks/bsim3_mos/NMOS5V0_idvg.cir` |
| NMOS5V0 | `vth_corner_spread` | 79.67 | mV | 90 – 130 | warn | 0.724× | `pdk_validation/characterization/decks/bsim3_mos/NMOS5V0_corner_TT.cir` |
| NMOS5V0 | `vth_lin` | 1.016 | V | 0.79 – 0.92 | warn | 1.2× | `pdk_validation/characterization/decks/bsim3_mos/NMOS5V0_idvg.cir` |
| NMOS5V0 | `mc_avt_implied_1sigma` | 11.19 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS5V0_mc_s0.cir` |
| NMOS5V0 | `mc_sigma_di_over_i` | 0.6704 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS5V0_mc_s0.cir` |
| NMOS5V0 | `mc_sigma_dvth_1sigma` | 5.003 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS5V0_mc_s0.cir` |
| NMOS5V0 | `mc_sigma_vth_per_device_1sigma` | 3.538 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/NMOS5V0_mc_s0.cir` |
| NMOS5V0 | `vth_model_internal` | 0.9598 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS5V0_corner_TT.cir` |
| NMOS5V0 | `cgso_overlap` | 0.259 | fF/um | 0.108 – 0.288 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS5V0_caps.cir` |
| NMOS5V0 | `cox` | 3.116 | fF/um^2 | 2.833 – 3.296 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS5V0_caps.cir` |
| NMOS5V0 | `flicker_corner` | 1.585e+05 | Hz | 2e+04 – 1.000e+06 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS5V0_noise.cir` |
| NMOS5V0 | `idsat_corner_spread` | 18.46 | percent | 12 – 20 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS5V0_corner_TT.cir` |
| NMOS5V0 | `junction_perimeter_set` | 1 | boolean | 1 – 1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS5V0_caps.cir` |
| NMOS5V0 | `vth_tempco` | -1.599 | mV/degC | -1.8 – -1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/NMOS5V0_temp_150.cir` |
| PMOS12V | `cox` | 1.007 | fF/um^2 | 0.95 – 0 | **hard-fail** |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12V_caps.cir` |
| PMOS12V | `cj_area` | 1.92 | fF/um^2 | 0.266 – 0.532 | warn | 5.05× | `pdk_validation/characterization/decks/bsim3_mos/PMOS12V_caps.cir` |
| PMOS12V | `cjsw_sidewall` | 0.4571 | fF/um | 0.05 – 0.15 | warn | 4.57× | `pdk_validation/characterization/decks/bsim3_mos/PMOS12V_caps.cir` |
| PMOS12V | `idsat_density` | 0.678 | mA/um | 0.12 – 0.25 | warn | 3.67× | `pdk_validation/characterization/decks/bsim3_mos/PMOS12V_idsat.cir` |
| PMOS12V | `subthreshold_swing` | 215.1 | mV/dec | 72 – 96 | warn | 2.69× | `pdk_validation/characterization/decks/bsim3_mos/PMOS12V_idvg.cir` |
| PMOS12V | `vth_corner_spread` | 80 | mV | 90 – 130 | warn | 0.727× | `pdk_validation/characterization/decks/bsim3_mos/PMOS12V_corner_TT.cir` |
| PMOS12V | `vth_lin` | 1.728 | V | 1.49 – 1.61 | warn | 1.12× | `pdk_validation/characterization/decks/bsim3_mos/PMOS12V_idvg.cir` |
| PMOS12V | `idsat_density_L1u` | 0.08652 | mA/um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12V_idsat.cir` |
| PMOS12V | `mc_avt_implied_1sigma` | 30.62 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS12V_mc_s0.cir` |
| PMOS12V | `mc_sigma_di_over_i` | 0.7007 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS12V_mc_s0.cir` |
| PMOS12V | `mc_sigma_dvth_1sigma` | 13.69 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS12V_mc_s0.cir` |
| PMOS12V | `mc_sigma_vth_per_device_1sigma` | 9.683 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS12V_mc_s0.cir` |
| PMOS12V | `vth_model_internal` | 1.584 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12V_corner_TT.cir` |
| PMOS12V | `cgso_overlap` | 0.2172 | fF/um | 0.096 – 0.256 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12V_caps.cir` |
| PMOS12V | `flicker_corner` | 3.981e+04 | Hz | 2e+04 – 1.000e+06 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12V_noise.cir` |
| PMOS12V | `idsat_corner_spread` | 12.4 | percent | 12 – 20 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12V_corner_TT.cir` |
| PMOS12V | `junction_perimeter_set` | 1 | boolean | 1 – 1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12V_caps.cir` |
| PMOS12V | `vth_tempco` | -1.466 | mV/degC | -1.8 – -1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS12V_temp_150.cir` |
| PMOS1V8 | `cj_area` | 2.32 | fF/um^2 | 0.735 – 1.47 | warn | 2.21× | `pdk_validation/characterization/decks/bsim3_mos/PMOS1V8_caps.cir` |
| PMOS1V8 | `cjsw_sidewall` | 0.5524 | fF/um | 0.05 – 0.15 | warn | 5.52× | `pdk_validation/characterization/decks/bsim3_mos/PMOS1V8_caps.cir` |
| PMOS1V8 | `idsat_corner_spread` | 34.27 | percent | 12 – 20 | warn | 2.14× | `pdk_validation/characterization/decks/bsim3_mos/PMOS1V8_corner_TT.cir` |
| PMOS1V8 | `idsat_density` | 0.1734 | mA/um | 0.25 – 0.3 | warn | 0.631× | `pdk_validation/characterization/decks/bsim3_mos/PMOS1V8_idsat.cir` |
| PMOS1V8 | `vth_corner_spread` | 79.04 | mV | 90 – 130 | warn | 0.719× | `pdk_validation/characterization/decks/bsim3_mos/PMOS1V8_corner_TT.cir` |
| PMOS1V8 | `vth_lin` | 0.7143 | V | 0.46 – 0.58 | warn | 1.37× | `pdk_validation/characterization/decks/bsim3_mos/PMOS1V8_idvg.cir` |
| PMOS1V8 | `vth_tempco` | -0.9995 | mV/degC | -1.8 – -1 | warn | 0.714× | `pdk_validation/characterization/decks/bsim3_mos/PMOS1V8_temp_150.cir` |
| PMOS1V8 | `mc_avt_implied_1sigma` | 3.4 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS1V8_mc_s0.cir` |
| PMOS1V8 | `mc_sigma_di_over_i` | 0.979 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS1V8_mc_s0.cir` |
| PMOS1V8 | `mc_sigma_dvth_1sigma` | 1.521 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS1V8_mc_s0.cir` |
| PMOS1V8 | `mc_sigma_vth_per_device_1sigma` | 1.075 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS1V8_mc_s0.cir` |
| PMOS1V8 | `vth_model_internal` | 0.692 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS1V8_corner_TT.cir` |
| PMOS1V8 | `cgso_overlap` | 0.3397 | fF/um | 0.144 – 0.384 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS1V8_caps.cir` |
| PMOS1V8 | `cox` | 7.635 | fF/um^2 | 7.333 – 8.531 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS1V8_caps.cir` |
| PMOS1V8 | `flicker_corner` | 1.585e+05 | Hz | 2e+04 – 1.000e+06 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS1V8_noise.cir` |
| PMOS1V8 | `junction_perimeter_set` | 1 | boolean | 1 – 1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS1V8_caps.cir` |
| PMOS1V8 | `subthreshold_swing` | 83.79 | mV/dec | 72 – 96 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS1V8_idvg.cir` |
| PMOS3V3 | `cj_area` | 2.12 | fF/um^2 | 0.616 – 1.232 | warn | 2.41× | `pdk_validation/characterization/decks/bsim3_mos/PMOS3V3_caps.cir` |
| PMOS3V3 | `cjsw_sidewall` | 0.5048 | fF/um | 0.05 – 0.15 | warn | 5.05× | `pdk_validation/characterization/decks/bsim3_mos/PMOS3V3_caps.cir` |
| PMOS3V3 | `idsat_corner_spread` | 26.73 | percent | 12 – 20 | warn | 1.67× | `pdk_validation/characterization/decks/bsim3_mos/PMOS3V3_corner_TT.cir` |
| PMOS3V3 | `idsat_density` | 0.1569 | mA/um | 0.2 – 0.28 | warn | 0.654× | `pdk_validation/characterization/decks/bsim3_mos/PMOS3V3_idsat.cir` |
| PMOS3V3 | `subthreshold_swing` | 108.3 | mV/dec | 72 – 96 | warn | 1.35× | `pdk_validation/characterization/decks/bsim3_mos/PMOS3V3_idvg.cir` |
| PMOS3V3 | `vth_corner_spread` | 79.64 | mV | 90 – 130 | warn | 0.724× | `pdk_validation/characterization/decks/bsim3_mos/PMOS3V3_corner_TT.cir` |
| PMOS3V3 | `vth_lin` | 0.9125 | V | 0.68 – 0.8 | warn | 1.23× | `pdk_validation/characterization/decks/bsim3_mos/PMOS3V3_idvg.cir` |
| PMOS3V3 | `mc_avt_implied_1sigma` | 3.968 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS3V3_mc_s0.cir` |
| PMOS3V3 | `mc_sigma_di_over_i` | 0.4682 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS3V3_mc_s0.cir` |
| PMOS3V3 | `mc_sigma_dvth_1sigma` | 1.775 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS3V3_mc_s0.cir` |
| PMOS3V3 | `mc_sigma_vth_per_device_1sigma` | 1.255 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS3V3_mc_s0.cir` |
| PMOS3V3 | `vth_model_internal` | 0.8766 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS3V3_corner_TT.cir` |
| PMOS3V3 | `cgso_overlap` | 0.3095 | fF/um | 0.132 – 0.352 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS3V3_caps.cir` |
| PMOS3V3 | `cox` | 4.928 | fF/um^2 | 4.617 – 5.372 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS3V3_caps.cir` |
| PMOS3V3 | `flicker_corner` | 5.012e+04 | Hz | 2e+04 – 1.000e+06 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS3V3_noise.cir` |
| PMOS3V3 | `junction_perimeter_set` | 1 | boolean | 1 – 1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS3V3_caps.cir` |
| PMOS3V3 | `vth_tempco` | -1.333 | mV/degC | -1.8 – -1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS3V3_temp_150.cir` |
| PMOS5V0 | `cj_area` | 1.92 | fF/um^2 | 1.2 – 1.7 | warn | 1.28× | `pdk_validation/characterization/decks/bsim3_mos/PMOS5V0_caps.cir` |
| PMOS5V0 | `cjsw_sidewall` | 0.4571 | fF/um | 0.05 – 0.15 | warn | 4.57× | `pdk_validation/characterization/decks/bsim3_mos/PMOS5V0_caps.cir` |
| PMOS5V0 | `idsat_corner_spread` | 23.56 | percent | 12 – 20 | warn | 1.47× | `pdk_validation/characterization/decks/bsim3_mos/PMOS5V0_corner_TT.cir` |
| PMOS5V0 | `idsat_density` | 0.1204 | mA/um | 0.22 – 0.3 | warn | 0.463× | `pdk_validation/characterization/decks/bsim3_mos/PMOS5V0_idsat.cir` |
| PMOS5V0 | `subthreshold_swing` | 146 | mV/dec | 85 – 100 | warn | 1.54× | `pdk_validation/characterization/decks/bsim3_mos/PMOS5V0_idvg.cir` |
| PMOS5V0 | `vth_corner_spread` | 79.74 | mV | 90 – 130 | warn | 0.725× | `pdk_validation/characterization/decks/bsim3_mos/PMOS5V0_corner_TT.cir` |
| PMOS5V0 | `vth_lin` | 1.144 | V | 0.83 – 0.95 | warn | 1.27× | `pdk_validation/characterization/decks/bsim3_mos/PMOS5V0_idvg.cir` |
| PMOS5V0 | `mc_avt_implied_1sigma` | 12.42 | mV.um | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS5V0_mc_s0.cir` |
| PMOS5V0 | `mc_sigma_di_over_i` | 0.8597 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS5V0_mc_s0.cir` |
| PMOS5V0 | `mc_sigma_dvth_1sigma` | 5.553 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS5V0_mc_s0.cir` |
| PMOS5V0 | `mc_sigma_vth_per_device_1sigma` | 3.927 | mV | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos_mc/PMOS5V0_mc_s0.cir` |
| PMOS5V0 | `vth_model_internal` | 1.089 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS5V0_corner_TT.cir` |
| PMOS5V0 | `cgso_overlap` | 0.2688 | fF/um | 0.114 – 0.304 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS5V0_caps.cir` |
| PMOS5V0 | `cox` | 3.031 | fF/um^2 | 2.833 – 3.296 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS5V0_caps.cir` |
| PMOS5V0 | `flicker_corner` | 3.162e+04 | Hz | 2e+04 – 1.000e+06 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS5V0_noise.cir` |
| PMOS5V0 | `junction_perimeter_set` | 1 | boolean | 1 – 1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS5V0_caps.cir` |
| PMOS5V0 | `vth_tempco` | -1.466 | mV/degC | -1.8 – -1 | pass |  | `pdk_validation/characterization/decks/bsim3_mos/PMOS5V0_temp_150.cir` |

## VDMOS

| device | FoM | measured | units | band | status | ×target | deck |
|---|---|---|---|---|---|---|---|
| NDMOS120V | `theta` | 1.001 | 1/V | 0.05 – 0.3 | **hard-fail** | 6.67× | `pdk_validation/characterization/decks/vdmos/NDMOS120V_theta.cir` |
| NDMOS120V | `body_diode_tt` | 8.000e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_card.cir` |
| NDMOS120V | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_rcond.cir` |
| NDMOS120V | `bv_corner_FF` | 128.1 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_bv_FF.cir` |
| NDMOS120V | `bv_corner_FS` | 128.1 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_bv_FS.cir` |
| NDMOS120V | `bv_corner_SF` | 141.6 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_bv_SF.cir` |
| NDMOS120V | `bv_corner_SS` | 141.6 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_bv_SS.cir` |
| NDMOS120V | `vth_lin` | 1.143 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_idvg.cir` |
| NDMOS120V | `bv` | 134.9 | V | 124.2 – 148.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_bv_TT.cir` |
| NDMOS120V | `cgdmax_per_cell` | 18.63 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_cap_0p1.cir` |
| NDMOS120V | `cgdmin_per_cell` | 6.906 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_cap_121p5.cir` |
| NDMOS120V | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_cap_0p1.cir` |
| NDMOS120V | `cjo_per_cell` | 33 | fF | 21 – 188.7 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_cap_0p1.cir` |
| NDMOS120V | `gm_over_id_ceiling` | 24.84 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_subth.cir` |
| NDMOS120V | `idsat_density` | 0.2332 | mA/um | 0.1 – 0.4 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_idsat.cir` |
| NDMOS120V | `rd_tempco` | 9365 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_ron_150.cir` |
| NDMOS120V | `ron_times_w` | 3.445e+04 | Ohm.um | 2.336e+04 – 4.256e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_ron_27.cir` |
| NDMOS120V | `rsp_specific_ron` | 5.167 | mOhm.cm^2 | 2.4 – 12 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_ron_27.cir` |
| NDMOS120V | `sigma_vth_1sigma_at_wref` | 10.6 | mV | 6 – 16 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/NDMOS120V_mc_s0.cir` |
| NDMOS120V | `subthreshold_swing` | 96.1 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_subth.cir` |
| NDMOS120V | `va_class` | 852.1 | V | 300 – 1000 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_va_1.cir` |
| NDMOS120V | `vto_tempco` | -2.361 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS120V_vth_150.cir` |
| NDMOS20V | `idsat_density` | 0.5903 | mA/um | 0.2 – 0.4 | warn | 1.97× | `pdk_validation/characterization/decks/vdmos/NDMOS20V_idsat.cir` |
| NDMOS20V | `body_diode_tt` | 1.800e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_card.cir` |
| NDMOS20V | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_rcond.cir` |
| NDMOS20V | `bv_corner_FF` | 23.24 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_bv_FF.cir` |
| NDMOS20V | `bv_corner_FS` | 23.24 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_bv_FS.cir` |
| NDMOS20V | `bv_corner_SF` | 24.44 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_bv_SF.cir` |
| NDMOS20V | `bv_corner_SS` | 24.44 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_bv_SS.cir` |
| NDMOS20V | `vth_lin` | 0.9949 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_idvg.cir` |
| NDMOS20V | `bv` | 23.84 | V | 22.1 – 26.4 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_bv_TT.cir` |
| NDMOS20V | `cgdmax_per_cell` | 18.57 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_cap_0p1.cir` |
| NDMOS20V | `cgdmin_per_cell` | 7.754 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_cap_21p6.cir` |
| NDMOS20V | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_cap_0p1.cir` |
| NDMOS20V | `cjo_per_cell` | 132 | fF | 14.2 – 174 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_cap_0p1.cir` |
| NDMOS20V | `gm_over_id_ceiling` | 26.69 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_subth.cir` |
| NDMOS20V | `rd_tempco` | 1.167e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_ron_150.cir` |
| NDMOS20V | `ron_times_w` | 8279 | Ohm.um | 3099 – 1.24e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_ron_27.cir` |
| NDMOS20V | `rsp_specific_ron` | 0.414 | mOhm.cm^2 | 0.1549 – 0.7747 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_ron_27.cir` |
| NDMOS20V | `sigma_vth_1sigma_at_wref` | 9.169 | mV | 4.8 – 12.8 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/NDMOS20V_mc_s0.cir` |
| NDMOS20V | `subthreshold_swing` | 92.87 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_subth.cir` |
| NDMOS20V | `theta` | 0.3787 | 1/V | 0.05 – 0.45 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_theta.cir` |
| NDMOS20V | `va_class` | 168.4 | V | 130 – 2000 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_va_1.cir` |
| NDMOS20V | `vto_tempco` | -2.011 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS20V_vth_150.cir` |
| NDMOS200V | `theta` | 1.339 | 1/V | 0.05 – 0.3 | **hard-fail** | 8.93× | `pdk_validation/characterization/decks/vdmos/NDMOS200V_theta.cir` |
| NDMOS200V | `body_diode_tt` | 1.300e-07 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_card.cir` |
| NDMOS200V | `l_drift_for_bv` | 11.25 | um | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_bv_L8u.cir` |
| NDMOS200V | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_rcond.cir` |
| NDMOS200V | `bv_corner_FF` | 211.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_bv_FF.cir` |
| NDMOS200V | `bv_corner_FS` | 211.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_bv_FS.cir` |
| NDMOS200V | `bv_corner_SF` | 238.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_bv_SF.cir` |
| NDMOS200V | `bv_corner_SS` | 238.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_bv_SS.cir` |
| NDMOS200V | `cap_reconciliation_ndmos200` | 0 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_recon_repro1_fixed.cir` |
| NDMOS200V | `vth_lin` | 1.178 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_idvg.cir` |
| NDMOS200V | `bv` | 224.9 | V | 207 – 247.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_bv_TT.cir` |
| NDMOS200V | `cgdmax_per_cell` | 18.64 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_cap_0p1.cir` |
| NDMOS200V | `cgdmin_per_cell` | 6.815 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_cap_202p5.cir` |
| NDMOS200V | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_cap_0p1.cir` |
| NDMOS200V | `cjo_per_cell` | 20.74 | fF | 20.4 – 249.9 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_cap_0p1.cir` |
| NDMOS200V | `gm_over_id_ceiling` | 25.34 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_subth.cir` |
| NDMOS200V | `idsat_density` | 0.1772 | mA/um | 0.1 – 0.4 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_idsat.cir` |
| NDMOS200V | `rd_tempco` | 1.015e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_ron_150.cir` |
| NDMOS200V | `ron_times_w` | 4.78e+04 | Ohm.um | 3.3e+04 – 6e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_ron_27.cir` |
| NDMOS200V | `rsp_specific_ron` | 10.51 | mOhm.cm^2 | 4.95 – 24.75 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_ron_27.cir` |
| NDMOS200V | `sigma_vth_1sigma_at_wref` | 12.47 | mV | 6.6 – 17.6 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/NDMOS200V_mc_s0.cir` |
| NDMOS200V | `subthreshold_swing` | 98.05 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_subth.cir` |
| NDMOS200V | `va_class` | 887 | V | 300 – 1000 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_va_1.cir` |
| NDMOS200V | `vto_tempco` | -2.689 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS200V_vth_150.cir` |
| NDMOS40V | `theta` | 0.4898 | 1/V | 0.05 – 0.45 | **hard-fail** | 3.27× | `pdk_validation/characterization/decks/vdmos/NDMOS40V_theta.cir` |
| NDMOS40V | `idsat_density` | 0.4719 | mA/um | 0.2 – 0.4 | warn | 1.57× | `pdk_validation/characterization/decks/vdmos/NDMOS40V_idsat.cir` |
| NDMOS40V | `body_diode_tt` | 2.800e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_card.cir` |
| NDMOS40V | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_rcond.cir` |
| NDMOS40V | `bv_corner_FF` | 46.41 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_bv_FF.cir` |
| NDMOS40V | `bv_corner_FS` | 46.41 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_bv_FS.cir` |
| NDMOS40V | `bv_corner_SF` | 49.29 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_bv_SF.cir` |
| NDMOS40V | `bv_corner_SS` | 49.29 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_bv_SS.cir` |
| NDMOS40V | `vth_lin` | 1.032 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_idvg.cir` |
| NDMOS40V | `bv` | 47.85 | V | 44.2 – 52.8 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_bv_TT.cir` |
| NDMOS40V | `cgdmax_per_cell` | 18.58 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_cap_0p1.cir` |
| NDMOS40V | `cgdmin_per_cell` | 7.237 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_cap_43p2.cir` |
| NDMOS40V | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_cap_0p1.cir` |
| NDMOS40V | `cjo_per_cell` | 94.28 | fF | 16.4 – 147.6 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_cap_0p1.cir` |
| NDMOS40V | `gm_over_id_ceiling` | 26.26 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_subth.cir` |
| NDMOS40V | `rd_tempco` | 1.017e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_ron_150.cir` |
| NDMOS40V | `ron_times_w` | 1.256e+04 | Ohm.um | 5211 – 2.085e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_ron_27.cir` |
| NDMOS40V | `rsp_specific_ron` | 0.8795 | mOhm.cm^2 | 0.3648 – 1.824 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_ron_27.cir` |
| NDMOS40V | `sigma_vth_1sigma_at_wref` | 8.699 | mV | 5.1 – 13.6 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/NDMOS40V_mc_s0.cir` |
| NDMOS40V | `subthreshold_swing` | 92.99 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_subth.cir` |
| NDMOS40V | `va_class` | 292.6 | V | 130 – 2000 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_va_1.cir` |
| NDMOS40V | `vto_tempco` | -2.148 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS40V_vth_150.cir` |
| NDMOS60V | `theta` | 0.5975 | 1/V | 0.05 – 0.45 | **hard-fail** | 3.98× | `pdk_validation/characterization/decks/vdmos/NDMOS60V_theta.cir` |
| NDMOS60V | `body_diode_tt` | 4.000e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_card.cir` |
| NDMOS60V | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_rcond.cir` |
| NDMOS60V | `bv_corner_FF` | 72.23 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_bv_FF.cir` |
| NDMOS60V | `bv_corner_FS` | 72.23 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_bv_FS.cir` |
| NDMOS60V | `bv_corner_SF` | 77.48 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_bv_SF.cir` |
| NDMOS60V | `bv_corner_SS` | 77.48 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_bv_SS.cir` |
| NDMOS60V | `vth_lin` | 1.071 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_idvg.cir` |
| NDMOS60V | `bv` | 74.86 | V | 69 – 82.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_bv_TT.cir` |
| NDMOS60V | `cgdmax_per_cell` | 18.6 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_cap_0p1.cir` |
| NDMOS60V | `cgdmin_per_cell` | 7.05 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_cap_67p5.cir` |
| NDMOS60V | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_cap_0p1.cir` |
| NDMOS60V | `cjo_per_cell` | 70.71 | fF | 16.9 – 151.8 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_cap_0p1.cir` |
| NDMOS60V | `gm_over_id_ceiling` | 25.85 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_subth.cir` |
| NDMOS60V | `idsat_density` | 0.3912 | mA/um | 0.2 – 0.4 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_idsat.cir` |
| NDMOS60V | `rd_tempco` | 9800 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_ron_150.cir` |
| NDMOS60V | `ron_times_w` | 1.715e+04 | Ohm.um | 1.095e+04 – 1.995e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_ron_27.cir` |
| NDMOS60V | `rsp_specific_ron` | 1.543 | mOhm.cm^2 | 0.675 – 3.375 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_ron_27.cir` |
| NDMOS60V | `sigma_vth_1sigma_at_wref` | 8.902 | mV | 5.4 – 14.4 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/NDMOS60V_mc_s0.cir` |
| NDMOS60V | `subthreshold_swing` | 93.32 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_subth.cir` |
| NDMOS60V | `va_class` | 464.6 | V | 130 – 2000 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_va_1.cir` |
| NDMOS60V | `vto_tempco` | -2.203 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS60V_vth_150.cir` |
| NDMOS80V | `theta` | 0.7386 | 1/V | 0.05 – 0.45 | **hard-fail** | 4.92× | `pdk_validation/characterization/decks/vdmos/NDMOS80V_theta.cir` |
| NDMOS80V | `body_diode_tt` | 5.500e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_card.cir` |
| NDMOS80V | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_rcond.cir` |
| NDMOS80V | `bv_corner_FF` | 91.06 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_bv_FF.cir` |
| NDMOS80V | `bv_corner_FS` | 91.06 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_bv_FS.cir` |
| NDMOS80V | `bv_corner_SF` | 98.66 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_bv_SF.cir` |
| NDMOS80V | `bv_corner_SS` | 98.66 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_bv_SS.cir` |
| NDMOS80V | `vth_lin` | 1.109 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_idvg.cir` |
| NDMOS80V | `bv` | 94.86 | V | 87.4 – 104.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_bv_TT.cir` |
| NDMOS80V | `cgdmax_per_cell` | 18.61 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_cap_0p1.cir` |
| NDMOS80V | `cgdmin_per_cell` | 6.989 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_cap_85p5.cir` |
| NDMOS80V | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_cap_0p1.cir` |
| NDMOS80V | `cjo_per_cell` | 51.85 | fF | 18.3 – 165 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_cap_0p1.cir` |
| NDMOS80V | `gm_over_id_ceiling` | 25.33 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_subth.cir` |
| NDMOS80V | `idsat_density` | 0.3162 | mA/um | 0.2 – 0.4 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_idsat.cir` |
| NDMOS80V | `rd_tempco` | 9116 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_ron_150.cir` |
| NDMOS80V | `ron_times_w` | 2.326e+04 | Ohm.um | 1.533e+04 – 2.793e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_ron_27.cir` |
| NDMOS80V | `rsp_specific_ron` | 2.559 | mOhm.cm^2 | 1.155 – 5.775 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_ron_27.cir` |
| NDMOS80V | `sigma_vth_1sigma_at_wref` | 9.231 | mV | 5.7 – 15.2 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/NDMOS80V_mc_s0.cir` |
| NDMOS80V | `subthreshold_swing` | 94.69 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_subth.cir` |
| NDMOS80V | `va_class` | 711.2 | V | 130 – 2000 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_va_1.cir` |
| NDMOS80V | `vto_tempco` | -2.284 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/NDMOS80V_vth_150.cir` |
| PDMOS120V | `theta` | 0.9206 | 1/V | 0.05 – 0.3 | **hard-fail** | 6.14× | `pdk_validation/characterization/decks/vdmos/PDMOS120V_theta.cir` |
| PDMOS120V | `body_diode_tt` | 9.500e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_card.cir` |
| PDMOS120V | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_rcond.cir` |
| PDMOS120V | `bv_corner_FF` | 122.8 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_bv_FF.cir` |
| PDMOS120V | `bv_corner_FS` | 133 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_bv_FS.cir` |
| PDMOS120V | `bv_corner_SF` | 122.8 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_bv_SF.cir` |
| PDMOS120V | `bv_corner_SS` | 133 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_bv_SS.cir` |
| PDMOS120V | `vth_lin` | -1.194 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_idvg.cir` |
| PDMOS120V | `bv` | 127.9 | V | 117.8 – 140.8 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_bv_TT.cir` |
| PDMOS120V | `cgdmax_per_cell` | 18.64 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_cap_0p1.cir` |
| PDMOS120V | `cgdmin_per_cell` | 6.939 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_cap_115p2.cir` |
| PDMOS120V | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_cap_0p1.cir` |
| PDMOS120V | `cjo_per_cell` | 27.34 | fF | 21.5 – 193.8 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_cap_0p1.cir` |
| PDMOS120V | `gm_over_id_ceiling` | 24.67 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_subth.cir` |
| PDMOS120V | `idsat_density` | 0.08344 | mA/um | 0.05 – 0.25 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_idsat.cir` |
| PDMOS120V | `rd_tempco` | 1.025e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_ron_150.cir` |
| PDMOS120V | `ron_times_w` | 9.795e+04 | Ohm.um | 6.541e+04 – 1.192e+05 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_ron_27.cir` |
| PDMOS120V | `rsp_specific_ron` | 14.69 | mOhm.cm^2 | 6.72 – 33.6 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_ron_27.cir` |
| PDMOS120V | `sigma_vth_1sigma_at_wref` | 10.41 | mV | 6 – 16 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/PDMOS120V_mc_s0.cir` |
| PDMOS120V | `subthreshold_swing` | 97.53 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_subth.cir` |
| PDMOS120V | `va_class` | 854.9 | V | 300 – 1000 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_va_1.cir` |
| PDMOS120V | `vto_tempco` | -2.577 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS120V_vth_150.cir` |
| PDMOS20V | `idsat_density` | 0.2639 | mA/um | 0.05 – 0.25 | warn | 2.2× | `pdk_validation/characterization/decks/vdmos/PDMOS20V_idsat.cir` |
| PDMOS20V | `body_diode_tt` | 2.200e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_card.cir` |
| PDMOS20V | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_rcond.cir` |
| PDMOS20V | `bv_corner_FF` | 21.27 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_bv_FF.cir` |
| PDMOS20V | `bv_corner_FS` | 22.37 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_bv_FS.cir` |
| PDMOS20V | `bv_corner_SF` | 21.27 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_bv_SF.cir` |
| PDMOS20V | `bv_corner_SS` | 22.37 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_bv_SS.cir` |
| PDMOS20V | `vth_lin` | -1.059 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_idvg.cir` |
| PDMOS20V | `bv` | 21.82 | V | 20.2 – 24.2 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_bv_TT.cir` |
| PDMOS20V | `cgdmax_per_cell` | 18.58 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_cap_0p1.cir` |
| PDMOS20V | `cgdmin_per_cell` | 7.933 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_cap_19p8.cir` |
| PDMOS20V | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_cap_0p1.cir` |
| PDMOS20V | `cjo_per_cell` | 141.4 | fF | 14.8 – 181.7 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_cap_0p1.cir` |
| PDMOS20V | `gm_over_id_ceiling` | 26.29 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_subth.cir` |
| PDMOS20V | `rd_tempco` | 1.97e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_ron_150.cir` |
| PDMOS20V | `ron_times_w` | 1.386e+04 | Ohm.um | 2000 – 1.5e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_ron_27.cir` |
| PDMOS20V | `rsp_specific_ron` | 0.6932 | mOhm.cm^2 | 0.1549 – 0.7747 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_ron_27.cir` |
| PDMOS20V | `sigma_vth_1sigma_at_wref` | 7.787 | mV | 4.8 – 12.8 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/PDMOS20V_mc_s0.cir` |
| PDMOS20V | `subthreshold_swing` | 96.1 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_subth.cir` |
| PDMOS20V | `theta` | 0.2159 | 1/V | 0.05 – 0.45 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_theta.cir` |
| PDMOS20V | `va_class` | 155.2 | V | 130 – 2000 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_va_1.cir` |
| PDMOS20V | `vto_tempco` | -1.61 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS20V_vth_150.cir` |
| PDMOS200V | `cjo_per_cell` | 16.97 | fF | 20.2 – 247.1 | **hard-fail** | 0.24× | `pdk_validation/characterization/decks/vdmos/PDMOS200V_cap_0p1.cir` |
| PDMOS200V | `theta` | 1.341 | 1/V | 0.05 – 0.3 | **hard-fail** | 8.94× | `pdk_validation/characterization/decks/vdmos/PDMOS200V_theta.cir` |
| PDMOS200V | `body_diode_tt` | 1.550e-07 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_card.cir` |
| PDMOS200V | `l_drift_for_bv` | 11.5 | um | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_bv_L8u.cir` |
| PDMOS200V | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_rcond.cir` |
| PDMOS200V | `bv_corner_FF` | 216.1 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_bv_FF.cir` |
| PDMOS200V | `bv_corner_FS` | 243.7 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_bv_FS.cir` |
| PDMOS200V | `bv_corner_SF` | 216.1 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_bv_SF.cir` |
| PDMOS200V | `bv_corner_SS` | 243.7 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_bv_SS.cir` |
| PDMOS200V | `vth_lin` | -1.238 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_idvg.cir` |
| PDMOS200V | `bv` | 229.9 | V | 211.6 – 253 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_bv_TT.cir` |
| PDMOS200V | `cgdmax_per_cell` | 18.65 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_cap_0p1.cir` |
| PDMOS200V | `cgdmin_per_cell` | 6.819 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_cap_207.cir` |
| PDMOS200V | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_cap_0p1.cir` |
| PDMOS200V | `gm_over_id_ceiling` | 26.04 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_subth.cir` |
| PDMOS200V | `idsat_density` | 0.06005 | mA/um | 0.05 – 0.25 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_idsat.cir` |
| PDMOS200V | `rd_tempco` | 1.077e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_ron_150.cir` |
| PDMOS200V | `ron_times_w` | 1.442e+05 | Ohm.um | 9.855e+04 – 1.796e+05 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_ron_27.cir` |
| PDMOS200V | `rsp_specific_ron` | 31.73 | mOhm.cm^2 | 14.85 – 74.25 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_ron_27.cir` |
| PDMOS200V | `sigma_vth_1sigma_at_wref` | 10.95 | mV | 6.6 – 17.6 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/PDMOS200V_mc_s0.cir` |
| PDMOS200V | `subthreshold_swing` | 99.98 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_subth.cir` |
| PDMOS200V | `va_class` | 889.5 | V | 300 – 1000 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_va_1.cir` |
| PDMOS200V | `vto_tempco` | -2.811 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS200V_vth_150.cir` |
| PDMOS40V | `body_diode_tt` | 3.500e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_card.cir` |
| PDMOS40V | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_rcond.cir` |
| PDMOS40V | `bv_corner_FF` | 43.48 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_bv_FF.cir` |
| PDMOS40V | `bv_corner_FS` | 46.18 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_bv_FS.cir` |
| PDMOS40V | `bv_corner_SF` | 43.48 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_bv_SF.cir` |
| PDMOS40V | `bv_corner_SS` | 46.18 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_bv_SS.cir` |
| PDMOS40V | `vth_lin` | -1.102 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_idvg.cir` |
| PDMOS40V | `bv` | 44.83 | V | 41.4 – 49.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_bv_TT.cir` |
| PDMOS40V | `cgdmax_per_cell` | 18.59 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_cap_0p1.cir` |
| PDMOS40V | `cgdmin_per_cell` | 7.31 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_cap_40p5.cir` |
| PDMOS40V | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_cap_0p1.cir` |
| PDMOS40V | `cjo_per_cell` | 99 | fF | 16.9 – 152.4 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_cap_0p1.cir` |
| PDMOS40V | `gm_over_id_ceiling` | 25.95 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_subth.cir` |
| PDMOS40V | `idsat_density` | 0.2445 | mA/um | 0.05 – 0.25 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_idsat.cir` |
| PDMOS40V | `rd_tempco` | 1.817e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_ron_150.cir` |
| PDMOS40V | `ron_times_w` | 1.738e+04 | Ohm.um | 5211 – 2.085e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_ron_27.cir` |
| PDMOS40V | `rsp_specific_ron` | 1.217 | mOhm.cm^2 | 0.3648 – 1.824 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_ron_27.cir` |
| PDMOS40V | `sigma_vth_1sigma_at_wref` | 8.143 | mV | 5.1 – 13.6 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/PDMOS40V_mc_s0.cir` |
| PDMOS40V | `subthreshold_swing` | 95.92 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_subth.cir` |
| PDMOS40V | `theta` | 0.2386 | 1/V | 0.05 – 0.45 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_theta.cir` |
| PDMOS40V | `va_class` | 245.7 | V | 130 – 2000 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_va_1.cir` |
| PDMOS40V | `vto_tempco` | -2.048 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS40V_vth_150.cir` |
| PDMOS60V | `theta` | 0.4958 | 1/V | 0.05 – 0.45 | **hard-fail** | 3.31× | `pdk_validation/characterization/decks/vdmos/PDMOS60V_theta.cir` |
| PDMOS60V | `body_diode_tt` | 5.000e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_card.cir` |
| PDMOS60V | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_rcond.cir` |
| PDMOS60V | `bv_corner_FF` | 67.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_bv_FF.cir` |
| PDMOS60V | `bv_corner_FS` | 72.3 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_bv_FS.cir` |
| PDMOS60V | `bv_corner_SF` | 67.4 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_bv_SF.cir` |
| PDMOS60V | `bv_corner_SS` | 72.3 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_bv_SS.cir` |
| PDMOS60V | `vth_lin` | -1.124 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_idvg.cir` |
| PDMOS60V | `bv` | 69.85 | V | 64.4 – 77 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_bv_TT.cir` |
| PDMOS60V | `cgdmax_per_cell` | 18.61 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_cap_0p1.cir` |
| PDMOS60V | `cgdmin_per_cell` | 7.113 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_cap_63.cir` |
| PDMOS60V | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_cap_0p1.cir` |
| PDMOS60V | `cjo_per_cell` | 61.28 | fF | 17.5 – 157.2 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_cap_0p1.cir` |
| PDMOS60V | `gm_over_id_ceiling` | 25.63 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_subth.cir` |
| PDMOS60V | `idsat_density` | 0.1479 | mA/um | 0.05 – 0.25 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_idsat.cir` |
| PDMOS60V | `rd_tempco` | 1.156e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_ron_150.cir` |
| PDMOS60V | `ron_times_w` | 4.475e+04 | Ohm.um | 2.738e+04 – 4.988e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_ron_27.cir` |
| PDMOS60V | `rsp_specific_ron` | 4.027 | mOhm.cm^2 | 1.688 – 8.438 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_ron_27.cir` |
| PDMOS60V | `sigma_vth_1sigma_at_wref` | 9.048 | mV | 5.4 – 14.4 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/PDMOS60V_mc_s0.cir` |
| PDMOS60V | `subthreshold_swing` | 95.17 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_subth.cir` |
| PDMOS60V | `va_class` | 473.1 | V | 130 – 2000 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_va_1.cir` |
| PDMOS60V | `vto_tempco` | -2.281 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS60V_vth_150.cir` |
| PDMOS80V | `theta` | 0.6388 | 1/V | 0.05 – 0.45 | **hard-fail** | 4.26× | `pdk_validation/characterization/decks/vdmos/PDMOS80V_theta.cir` |
| PDMOS80V | `body_diode_tt` | 6.500e-08 | s | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_card.cir` |
| PDMOS80V | `rcond_gate_current` | 5.000e-06 | A | -- | artifact <br>_anchor _known_artifacts_ |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_rcond.cir` |
| PDMOS80V | `bv_corner_FF` | 86.26 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_bv_FF.cir` |
| PDMOS80V | `bv_corner_FS` | 93.46 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_bv_FS.cir` |
| PDMOS80V | `bv_corner_SF` | 86.26 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_bv_SF.cir` |
| PDMOS80V | `bv_corner_SS` | 93.46 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_bv_SS.cir` |
| PDMOS80V | `vth_lin` | -1.162 | V | -- | no-anchor |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_idvg.cir` |
| PDMOS80V | `bv` | 89.86 | V | 82.8 – 99 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_bv_TT.cir` |
| PDMOS80V | `cgdmax_per_cell` | 18.62 | fF | 3.8 – 34.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_cap_0p1.cir` |
| PDMOS80V | `cgdmin_per_cell` | 7.031 | fF | 1 – 8.6 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_cap_81.cir` |
| PDMOS80V | `cgs_per_cell` | 23.91 | fF | 3.5 – 31 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_cap_0p1.cir` |
| PDMOS80V | `cjo_per_cell` | 42.43 | fF | 18.8 – 169.5 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_cap_0p1.cir` |
| PDMOS80V | `gm_over_id_ceiling` | 25.14 | 1/V | 24 – 32 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_subth.cir` |
| PDMOS80V | `idsat_density` | 0.1172 | mA/um | 0.05 – 0.25 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_idsat.cir` |
| PDMOS80V | `rd_tempco` | 1.031e+04 | ppm/degC | 8000 – 2e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_ron_150.cir` |
| PDMOS80V | `ron_times_w` | 6.332e+04 | Ohm.um | 4.062e+04 – 7.401e+04 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_ron_27.cir` |
| PDMOS80V | `rsp_specific_ron` | 6.965 | mOhm.cm^2 | 3.061 – 15.3 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_ron_27.cir` |
| PDMOS80V | `sigma_vth_1sigma_at_wref` | 10.06 | mV | 5.7 – 15.2 | pass |  | `pdk_validation/characterization/decks/vdmos_mc/PDMOS80V_mc_s0.cir` |
| PDMOS80V | `subthreshold_swing` | 96.52 | mV/dec | 72 – 100 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_subth.cir` |
| PDMOS80V | `va_class` | 714 | V | 130 – 2000 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_va_1.cir` |
| PDMOS80V | `vto_tempco` | -2.425 | mV/degC | -3 – -1 | pass |  | `pdk_validation/characterization/decks/vdmos/PDMOS80V_vth_150.cir` |

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
| DIO_SCH | `cjo_density` | 140 | fF/um^2 | 0.5 – 2 | warn | 140× | `pdk_validation/characterization/decks/diodes/DIO_SCH_cjo.cir` |
| DIO_SCH | `qrr_at_10mA` | 6.163e-15 | C | -- | no-anchor |  | `pdk_validation/characterization/decks/diodes/DIO_SCH_diffcap.cir` |
| DIO_SCH | `bv` | 45.1 | V | 38.2 – 51.7 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_SCH_rev.cir` |
| DIO_SCH | `n_ideality` | 1.075 |  | 1.03 – 1.15 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_SCH_fwd.cir` |
| DIO_SCH | `tt_transit_time` | 6.163e-13 | s | 0 – 1.000e-12 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_SCH_diffcap.cir` |
| DIO_SCH | `vf_at_1mA` | 0.2914 | V | 0.247 – 0.335 | pass |  | `pdk_validation/characterization/decks/diodes/DIO_SCH_fwd.cir` |
| DZ_12V | `cjo_density` | 5.5e+04 | fF/um^2 | 0.515 – 2.062 | **hard-fail** | 5.33e+04× | `pdk_validation/characterization/decks/diodes/DZ_12V_cjo.cir` |
| DZ_12V | `bv` | 11.73 | V | 11.4 – 12.6 | pass |  | `pdk_validation/characterization/decks/diodes/DZ_12V_rev_27C.cir` |
| DZ_12V | `bv_tempco` | 7.119 | mV/degC | 4 – 12.8 | pass |  | `pdk_validation/characterization/decks/diodes/DZ_12V_rev_150C.cir` |
| DZ_12V | `tt_transit_time` | 5.518e-08 | s | 1.000e-08 – 1.000e-07 | pass |  | `pdk_validation/characterization/decks/diodes/DZ_12V_diffcap.cir` |
| DZ_24V | `cjo_density` | 2.8e+04 | fF/um^2 | 0.509 – 2.038 | **hard-fail** | 2.75e+04× | `pdk_validation/characterization/decks/diodes/DZ_24V_cjo.cir` |
| DZ_24V | `bv` | 23.77 | V | 22.8 – 25.2 | pass |  | `pdk_validation/characterization/decks/diodes/DZ_24V_rev_27C.cir` |
| DZ_24V | `bv_tempco` | 19.27 | mV/degC | 10 – 32 | pass |  | `pdk_validation/characterization/decks/diodes/DZ_24V_rev_150C.cir` |
| DZ_24V | `tt_transit_time` | 7.492e-08 | s | 1.000e-08 – 1.000e-07 | pass |  | `pdk_validation/characterization/decks/diodes/DZ_24V_diffcap.cir` |
| DZ_5V6 | `bv` | 5.243 | V | 5.32 – 5.88 | **hard-fail** | 0.936× | `pdk_validation/characterization/decks/diodes/DZ_5V6_rev_27C.cir` |
| DZ_5V6 | `cjo_density` | 1.200e+05 | fF/um^2 | 1.663 – 6.652 | **hard-fail** | 3.61e+04× | `pdk_validation/characterization/decks/diodes/DZ_5V6_cjo.cir` |
| DZ_5V6 | `bv_tempco` | 0.5267 | mV/degC | 1 – 2 | warn | 0.351× | `pdk_validation/characterization/decks/diodes/DZ_5V6_rev_150C.cir` |
| DZ_5V6 | `tt_transit_time` | 4.054e-08 | s | 1.000e-08 – 1.000e-07 | pass |  | `pdk_validation/characterization/decks/diodes/DZ_5V6_diffcap.cir` |

## Passives

| device | FoM | measured | units | band | status | ×target | deck |
|---|---|---|---|---|---|---|---|
| CFRINGE | `golden_crosscheck` | -3.336e-08 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/CFRINGE_cv.cir` |
| CFRINGE | `density` | 0.181 | fF/um^2 | 0.1 – 0.5 | pass |  | `pdk_validation/characterization/decks/passives/CFRINGE_cv.cir` |
| CFRINGE | `implied_dielectric_thickness` | 195.7 | nm | 137.8 – 275.5 | pass |  | `pdk_validation/characterization/decks/passives/CFRINGE_cv.cir` |
| CFRINGE | `matching_A_C_pair_1sigma` | 1.429 | %.um | 0.9 – 2.7 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| CFRINGE | `tcc_tc1` | 16.12 | ppm/degC | 6 – 38 | pass |  | `pdk_validation/characterization/decks/passives/CFRINGE_temp_150.cir` |
| CFRINGE | `vcc1` | 2.982 | ppm/V | 1 – 6 | pass |  | `pdk_validation/characterization/decks/passives/CFRINGE_cv.cir` |
| CMIM_HI | `golden_crosscheck` | -3.295e-10 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/CMIM_HI_cv.cir` |
| CMIM_HI | `density` | 2 | fF/um^2 | 2 – 4 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_HI_cv.cir` |
| CMIM_HI | `implied_dielectric_thickness` | 30.99 | nm | 21.7 – 43.4 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_HI_cv.cir` |
| CMIM_HI | `matching_A_C_pair_1sigma` | 0.7614 | %.um | 0.45 – 1.35 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| CMIM_HI | `tcc_tc1` | 48.36 | ppm/degC | 18 – 112 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_HI_temp_150.cir` |
| CMIM_HI | `vcc1` | 59.97 | ppm/V | 24 – 120 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_HI_cv.cir` |
| CMIM_STD | `golden_crosscheck` | 7.726e-11 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/CMIM_STD_cv.cir` |
| CMIM_STD | `density` | 1 | fF/um^2 | 0.9 – 1.1 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_STD_cv.cir` |
| CMIM_STD | `implied_dielectric_thickness` | 61.98 | nm | 43.4 – 86.8 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_STD_cv.cir` |
| CMIM_STD | `matching_A_C_pair_1sigma` | 0.7832 | %.um | 0.45 – 1.35 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| CMIM_STD | `tcc_tc1` | 37.8 | ppm/degC | 0 – 45 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_STD_temp_150.cir` |
| CMIM_STD | `vcc1` | 29.99 | ppm/V | 0 – 30 | pass |  | `pdk_validation/characterization/decks/passives/CMIM_STD_cv.cir` |
| CMOM | `golden_crosscheck` | -7.136e-08 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/CMOM_cv.cir` |
| CMOM | `density` | 0.35 | fF/um^2 | 0.3 – 1 | pass |  | `pdk_validation/characterization/decks/passives/CMOM_cv.cir` |
| CMOM | `implied_dielectric_thickness` | 101.2 | nm | 70.8 – 141.7 | pass |  | `pdk_validation/characterization/decks/passives/CMOM_cv.cir` |
| CMOM | `matching_A_C_pair_1sigma` | 1.607 | %.um | 0.9 – 2.7 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| CMOM | `tcc_tc1` | 21.68 | ppm/degC | 8 – 50 | pass |  | `pdk_validation/characterization/decks/passives/CMOM_temp_150.cir` |
| CMOM | `vcc1` | 4.998 | ppm/V | 2 – 10 | pass |  | `pdk_validation/characterization/decks/passives/CMOM_cv.cir` |
| RNPLUS | `tc1` | 984 | ppm/degC | 1000 – 2000 | warn | 0.656× | `pdk_validation/characterization/decks/passives/RNPLUS_temp_150.cir` |
| RNPLUS | `golden_crosscheck` | 1.008e-07 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/RNPLUS_rv.cir` |
| RNPLUS | `matching_A_R_pair_1sigma` | 2.898 | %.um | 1.5 – 4.5 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| RNPLUS | `rsh` | 60.01 | Ohm/sq | 50 – 90 | pass |  | `pdk_validation/characterization/decks/passives/RNPLUS_rsh.cir` |
| RNPLUS | `rsh_corner_spread` | 12 | percent | 10 – 25 | pass |  | `pdk_validation/characterization/decks/passives/RNPLUS_corner_TT.cir` |
| RNPLUS | `vcr1` | 1500 | ppm/V | 750 – 3000 | pass |  | `pdk_validation/characterization/decks/passives/RNPLUS_rv.cir` |
| RNWELL | `rsh` | 1801 | Ohm/sq | 1000 – 1600 | warn | 1.5× | `pdk_validation/characterization/decks/passives/RNWELL_rsh.cir` |
| RNWELL | `golden_crosscheck` | -2.155e-08 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/RNWELL_rv.cir` |
| RNWELL | `matching_A_R_pair_1sigma` | 4.093 | %.um | 2.4 – 7.2 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| RNWELL | `rsh_corner_spread` | 12 | percent | 10 – 25 | pass |  | `pdk_validation/characterization/decks/passives/RNWELL_corner_TT.cir` |
| RNWELL | `tc1` | 4280 | ppm/degC | 3000 – 6000 | pass |  | `pdk_validation/characterization/decks/passives/RNWELL_temp_150.cir` |
| RNWELL | `vcr1` | 8000 | ppm/V | 4000 – 1.6e+04 | pass |  | `pdk_validation/characterization/decks/passives/RNWELL_rv.cir` |
| RPOLY_HI | `golden_crosscheck` | -5.146e-08 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/RPOLY_HI_rv.cir` |
| RPOLY_HI | `matching_A_R_pair_1sigma` | 1.551 | %.um | 0.9 – 2.7 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| RPOLY_HI | `rsh` | 1200 | Ohm/sq | 1000 – 2000 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_HI_rsh.cir` |
| RPOLY_HI | `rsh_corner_spread` | 12 | percent | 10 – 25 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_HI_corner_TT.cir` |
| RPOLY_HI | `tc1` | -1344 | ppm/degC | -2000 – -1000 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_HI_temp_150.cir` |
| RPOLY_HI | `vcr1` | 200 | ppm/V | 100 – 400 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_HI_rv.cir` |
| RPOLY_LO | `golden_crosscheck` | -9.247e-08 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/RPOLY_LO_rv.cir` |
| RPOLY_LO | `matching_A_R_pair_1sigma` | 1.534 | %.um | 0.9 – 2.7 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| RPOLY_LO | `rsh` | 300 | Ohm/sq | 200 – 400 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_LO_rsh.cir` |
| RPOLY_LO | `rsh_corner_spread` | 12 | percent | 10 – 25 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_LO_corner_TT.cir` |
| RPOLY_LO | `tc1` | 12 | ppm/degC | -100 – 600 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_LO_temp_150.cir` |
| RPOLY_LO | `vcr1` | 50 | ppm/V | 25 – 100 | pass |  | `pdk_validation/characterization/decks/passives/RPOLY_LO_rv.cir` |
| RPPLUS | `golden_crosscheck` | -6.350e-09 | percent | -- | no-anchor |  | `pdk_validation/characterization/decks/passives/RPPLUS_rv.cir` |
| RPPLUS | `matching_A_R_pair_1sigma` | 2.616 | %.um | 1.5 – 4.5 | pass |  | `pdk_validation/characterization/decks/passives_mc/passives_mc_s0.cir` |
| RPPLUS | `rsh` | 110 | Ohm/sq | 80 – 140 | pass |  | `pdk_validation/characterization/decks/passives/RPPLUS_rsh.cir` |
| RPPLUS | `rsh_corner_spread` | 12 | percent | 10 – 25 | pass |  | `pdk_validation/characterization/decks/passives/RPPLUS_corner_TT.cir` |
| RPPLUS | `tc1` | 1190 | ppm/degC | 1000 – 2500 | pass |  | `pdk_validation/characterization/decks/passives/RPPLUS_temp_150.cir` |
| RPPLUS | `vcr1` | 1800 | ppm/V | 900 – 3600 | pass |  | `pdk_validation/characterization/decks/passives/RPPLUS_rv.cir` |

## Discrimination experiments (§D)

Full payloads in the results JSON under `_experiments`; verdicts in
`pdk_validation/characterization/experiments/README.md`.

| experiment | verdict |
|---|---|
| `d1_kp_convention` | {'convention': 'kp/2', 'one_word': 'kp/2', 'measured_ratio_A_over_kp': 0.5000000037756673, 'statement': 'ngspice-45 VDMOS saturation current is Id = (kp/2)*Vov^2. The fitted prefactor is 0.00088542 A/V^2 against a card kp of 0.00177084, a ratio of 0.5000 -- indistinguishable from 1/2, so the model carries the standard SPICE factor-of-two internally and kp is a TRANSCONDUCTANCE PARAMETER, not the saturation prefactor.', 'corrected_and_uncorrected_agree': True, 'robustness': 'The uncorrected fit gives A/kp = 0.3930 and the theta/lambda-corrected fit 0.5000. Both land on the same side of the fork, so the verdict does not depend on the correction -- the two candidates are a factor of two apart and the corrections are single-digit percent.'} |
| `d2_ksubthres` | {'semantics': 'ksubthres is a per-DECADE slope; the natural-log (ln10) reading is excluded. Measured S ~= 1.249 * (1000*ksubthres) mV/dec, R^2 = 0.5806 over 13 cards.', 'phase1_2_8_slope_finding': 'does not survive', 'phase1_2_8_sub_boltzmann_finding': 'OVERTURNED -- NDMOS200V n = 1.65, not 1.36', 'overturns_phase_1': True, 'plain_statement': "Audit 2.8 made two claims and D2 splits them.\n  The STRUCTURAL claim -- that the swing ladder slopes the wrong way with voltage class, when n = 1 + C_dep/Cox demands it rise -- is NOT confirmed.\n  The HEADLINE claim -- that NDMOS200V sits at n = 1.01, 'essentially ideal', below the room-temperature Boltzmann floor and therefore physically impossible -- is OVERTURNED. It came from reading ksubthres as if it were S in V/dec. Measured, NDMOS200V swings at 98.0 mV/dec for n = 1.65. Low, but ordinary -- there is no perfect gate and nothing unphysical. Every one of the 13 cards sits above n = 1 once measured.\nPhase 1 had to assume the semantics because nothing in the PDK states them. D2 measured them, twice, by independent routes that agree. Where they conflict, the measurement wins.", 'consequence_for_worklist': "The 'NDMOS200V is sub-Boltzmann' line item should be STRUCK from the fix worklist -- there is nothing to fix. The 'ksubthres ladder slopes the wrong way' item stands, and its severity is unchanged (it sets the subthreshold gm/Id ceiling, which is what HANDOFF_dmos200_subthreshold_analog.md turns on). Any re-laddering of ksubthres must be done against MEASURED S, not against 1000*ksubthres: the conversion is S ~= 1.249 * 1000 * ksubthres, so a card targeting S = 90 mV/dec needs ksubthres ~= 0.0720, not 0.090.", 'consequence_for_anchor': "docs/anchor-values.json: add the measured mapping S_mV_per_dec = 1.249 * 1000 * ksubthres (D2, R^2 = 0.5806, 13 cards) next to the subthreshold_swing entry, and correct any note that asserts 'the card's ksubthres IS S in V/dec by construction' -- families/vdmos.py carries exactly that wording in _do_idvg's model_ksubthres_note and it is off by 25%. No anchor BAND changes: the measured swings land where the anchor already expected them to."} |
| `d3_rdrs_isolation` | {'series_share_of_measured_ron': {'NDMOS20V': 0.5204519855658732, 'NDMOS200V': 0.9021316912967476}, 'channel_only_ron_times_w_ohm_um': {'NDMOS20V': 3970.218596265692, 'NDMOS200V': 4677.633846984307}, 'disagreement_swing_across_family_before_x': 30.375, 'disagreement_swing_across_family_after_x': 53.9258628465939, 'one_line': 'SERIES-RESISTANCE INTERACTION -- the disagreement is substantially an artifact', 'statement': "The decomposition is clean: subtracting the rd=rs=0 on-resistance from the stock one recovers the card's own rd+rs to 0.15% (NDMOS20V) and 0.00% (NDMOS200V), so Ron really does separate into a channel term and a series term and the split below can be trusted.\nSeries resistance is only 52.0% of NDMOS20V's Ron and 90.2% of NDMOS200V's -- the CHANNEL dominates both, which audit 2.2 did not allow for.\nTwo consequences, pulling in opposite directions.\n  (1) The kp route is CLEAN. Removing rd/rs lifts Idsat density by 1.419x on NDMOS20V and 5.643x on NDMOS200V, against implied-width gaps of 3649x and 287x. Series resistance explains under 0.2% of the kp finding. F1's kp half cannot be blamed on rd/rs.\n  (2) The Ron route was MISATTRIBUTED. Audit 2.2 took the card's whole on-resistance to be rd+rs, but rd+rs are only 52%/90% of it, so its implied widths are overstated by 1.92x and 1.11x. Re-cast on the total measured Ron they become 495x and 2099x.\nThe disagreement therefore does not collapse -- it MOVES. It goes from 2.43x/0.08x to 7.37x/0.14x, and the swing across the family widens from 30x to 54x. The correction is large enough that audit 2.5's numbers should not be quoted as they stand.", 'channel_only_number_for_the_rd_rs_rederivation': 'NDMOS20V 3970 Ohm.um, NDMOS200V 4678 Ohm.um, at Vov = 4 V and Vds = 0.1 V. This is a FLOOR. Whatever rd/rs are re-derived to, total Ron*W can never fall below these, because this is the channel resistance the same kp that sets Idsat also sets. Two things follow. First, any rd/rs proposal must be checked against it -- a divisor that would drive total Ron*W near or below the channel-only value is arithmetically impossible, not merely optimistic. Second, and more awkwardly, the channel-only floor is itself set by the same defective kp: fixing kp downward RAISES this floor, so fix #2 and fix #3 are coupled through it even though the defects are independent. Re-derive rd/rs AFTER kp, not before.', 'consequence': "For the fix worklist:\n  * Fix #2 (kp) is untouched by rd/rs and can be scoped on its own evidence. D3 closes off 'maybe it is just series resistance'.\n  * Fix #3 (rd/rs) needs audit 2.2's implied-width table RECOMPUTED, because that table divided by rd+rs where it should have divided by the full on-resistance. The correction is 1.92x at 20 V and 1.11x at 200 V -- not uniform, so it also slightly steepens what audit 2.2 called a flat ratio. That does not overturn the 'one divisor' verdict for rd/rs (a 1.3x tilt inside a ~10^3 slip is noise), but the table should be reissued with the measured split.\n  * Ordering: re-derive kp first, then rd/rs against the resulting channel-only floor."} |
| `d4_kp_ladder_shape` | {'spread_all_13': {'a_flat_tox_x': 1.442169557781578, 'b_theta_tox_x': 2.407958850957107, 'flattening_factor': 0.5989178582550735}, 'spread_n_channel': {'a_flat_tox_x': 1.442169557781578, 'b_theta_tox_x': 2.3841779071675777, 'flattening_factor': 0.6048917546991646}, 'spread_p_channel': {'a_flat_tox_x': 1.0, 'b_theta_tox_x': 1.6566426555945097}, 'one_line': 'NEITHER -- fewer than thirteen, more than one', 'statement': 'The theta-implied oxide ladder FLATTENS the residual substantially but does not flatten it to one number.\n  Hypothesis (a), tox = 30 nm flat: the implied-width ratio spans 1.4x across the n-channel cards (2x down to 2x) and 1.4x across all thirteen.\n  Hypothesis (b), theta-implied tox ladder: 2.4x n-channel, 2.4x across all thirteen.\nSo the tox ladder removes 0.6x of the 1.4x n-channel slope -- most of it -- but leaves 2.4x behind. That is the answer to the question as posed: the sloped residual is REAL but it is mostly an artifact of the flat-tox assumption, not mostly a real kp ladder error.\nMechanically the result is simple. Under (b), tox ~ 1/theta, so Cox ~ theta and W ~ kp/theta. kp falls 12.7x across the n-channel family while theta falls 2.2x, so the residual falls by the ratio. The kp ladder and the theta ladder are laddered together but not proportionally.', 'ruling_on_fix_2': "NOT thirteen re-derivations. A 2.4x spread does not justify thirteen independent physical derivations -- it is the same order as the 2.8x spread audit 2.2 was willing to call 'roughly flat' and fix with a single divisor for rd/rs. It is also not cleanly one divisor: a single divisor would leave a 2.4x residual, which is more than the measurement error and would show up as a real drive-current ladder error across voltage classes.\nRECOMMENDATION: one divisor plus a per-class trim -- six numbers (one per voltage class), not thirteen, and not one. Derive the divisor from the family geometric mean and let the per-class trim absorb the residual ladder. If the maintainer will accept a 2x drive-current error at the extremes of the family, one divisor is defensible and fix #2 becomes as cheap as fix #3.", 'MAINTAINER_DECISION_REQUIRED': '*** THIS EXPERIMENT DOES NOT DECIDE THE OXIDE LADDER. ***\nEverything above is conditional on the maintainer DECLARING tox per VDMOS voltage class. The PDK never states it, and audit 2.7 already recommends stating it because three separate findings depend on it. D4 tells the maintainer what each declaration implies:\n  * Declare tox = 30 nm flat  -> implied-width residual spans 1.4x n-channel -> fix #2 is a per-card job, thirteen re-derivations, as phase 1 scoped it.\n  * Declare the theta-implied rising ladder -> residual spans 2.4x -> fix #2 collapses to one divisor plus at most a per-class trim.\nThe theta-implied ladder is the better-supported of the two -- it is derived from a card parameter rather than assumed, it is monotonic and correctly ordered, and a rising tox with voltage class is what the process would actually do. But it is in tension with the vto = 1.00-1.31 V the cards carry, which for LDMOS body doping suggests a THINNER oxide, and D4 cannot resolve that tension. It is a process-declaration question, not a simulation question.\nDo not apply fix #2 in either scoping until tox is declared.', 'consequence_for_anchor': 'docs/anchor-values.json: _vdmos_kp_conditional currently forks on decision_A_10um_cell vs decision_B_power_die. D4 shows a SECOND, orthogonal fork -- the oxide ladder -- that changes the SHAPE of the kp fix rather than its magnitude. Propose adding a `_vdmos_tox_conditional` block alongside it recording the two hypotheses, their measured residual spreads (1.4x flat vs 2.4x laddered, n-channel), and the theta-implied tox band per class from the table above. The existing kp_n/kp_p targets are computed at tox 20-50 nm and would need restating per class under the laddered hypothesis. MAINTAINER APPLIES; do not edit the anchor from this experiment.'} |

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
