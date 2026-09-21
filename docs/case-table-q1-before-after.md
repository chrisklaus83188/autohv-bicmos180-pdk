# Corner response before and after ruling Q1

`b1d333d` (joint-3σ construction, `VBE_*`/`VF_*` unrealised) against the per-variable
±3σ construction with `is` carrying the BJT/diode draw. Same benches, same deck
builders, same harness — only the PDK files differ. Percentages are against each
device's own case 0.

`n/a` marks a preset the device does not participate in; presets 1–4 move the MOS
groups only, which is by design (ruling Q3).

| device | kind | FF (1) before | after | SS (2) before | after | slow-all (13) before | after |
|---|---|---:|---:|---:|---:|---:|---:|
| NMOS18 | mos | +4.95% | +13.06% | -4.80% | -11.69% | -4.80% | -11.69% |
| PMOS18 | mos | +7.02% | +14.31% | -6.64% | -12.66% | -6.64% | -12.66% |
| NMOS33 | mos | +6.13% | +12.50% | -5.88% | -11.26% | -5.88% | -11.26% |
| PMOS33 | mos | +7.75% | +13.16% | -7.26% | -11.78% | -7.26% | -11.78% |
| NMOS50 | mos | +6.48% | +12.32% | -6.19% | -11.13% | -6.19% | -11.13% |
| PMOS50 | mos | +7.86% | +12.81% | -7.35% | -11.51% | -7.35% | -11.51% |
| NMOS12 | mos | +5.88% | +8.66% | -5.69% | -8.20% | -5.69% | -8.20% |
| PMOS12 | mos | +7.25% | +10.24% | -6.84% | -9.44% | -6.84% | -9.44% |
| NDMOS20 | vdmos | +7.69% | +12.76% | -7.16% | -11.43% | -7.16% | -11.43% |
| PDMOS20 | vdmos | +8.39% | +11.16% | -7.76% | -10.09% | -7.76% | -10.09% |
| NDMOS40 | vdmos | +8.52% | +13.99% | -7.97% | -12.38% | -7.97% | -12.38% |
| PDMOS40 | vdmos | +7.90% | +11.96% | -7.34% | -10.76% | -7.34% | -10.76% |
| NDMOS60 | vdmos | +9.42% | +14.71% | -8.79% | -12.92% | -8.79% | -12.92% |
| PDMOS60 | vdmos | +8.82% | +14.35% | -8.24% | -12.65% | -8.24% | -12.65% |
| NDMOS80 | vdmos | +9.78% | +11.59% | -9.29% | -10.75% | -9.29% | -10.75% |
| PDMOS80 | vdmos | +9.86% | +14.88% | -9.20% | -13.12% | -9.20% | -13.12% |
| NDMOS120 | vdmos | +11.34% | +12.87% | -10.51% | -11.69% | -10.51% | -11.69% |
| PDMOS120 | vdmos | +11.05% | +12.57% | -10.30% | -11.46% | -10.30% | -11.46% |
| NDMOS200 | vdmos | +12.30% | +13.66% | -11.22% | -12.25% | -11.22% | -12.25% |
| PDMOS200 | vdmos | +12.27% | +13.63% | -11.21% | -12.22% | -11.21% | -12.22% |
| DNMOS20 | vdmos | +9.82% | +16.33% | -9.06% | -14.28% | -9.06% | -14.28% |
| RPOLY_HI | resistor | +0.00% | n/a | +0.00% | n/a | -18.11% | -18.14% |
| RPOLY_LO | resistor | +0.00% | n/a | +0.00% | n/a | -13.89% | -13.93% |
| RNWELL | resistor | +0.00% | n/a | +0.00% | n/a | -23.66% | -23.66% |
| RNPLUS | resistor | +0.00% | n/a | +0.00% | n/a | -10.43% | -10.43% |
| RPPLUS | resistor | +0.00% | n/a | +0.00% | n/a | -13.93% | -13.93% |
| CMIM_STD | capacitor | +0.00% | n/a | +0.00% | n/a | -21.34% | -21.34% |
| CMIM_HI | capacitor | +0.00% | n/a | +0.00% | n/a | -21.34% | -21.34% |
| CMOM | capacitor | +0.00% | n/a | +0.00% | n/a | -32.98% | -32.98% |
| CFRINGE | capacitor | +0.00% | n/a | +0.00% | n/a | -32.80% | -32.80% |
| NPN_LV | bjt | +0.00% | n/a | +0.00% | n/a | -0.00% | -20.71% |
| PNP_LAT | bjt | +0.00% | n/a | +0.00% | n/a | -0.01% | -20.72% |
| NPN_HV | bjt | +0.00% | n/a | +0.00% | n/a | -0.00% | -20.72% |
| PNP_HV | bjt | +0.00% | n/a | +0.00% | n/a | -0.02% | -20.73% |
| DIO_PN | diode | +0.00% | n/a | +0.00% | n/a | -0.00% | -26.61% |
| DIO_FAST | diode | +0.00% | n/a | +0.00% | n/a | -0.00% | -26.62% |
| DIO_SCH | diode | +0.00% | n/a | +0.00% | n/a | -0.00% | -26.63% |
| DZ_5V6 | diode | +0.00% | n/a | +0.00% | n/a | -0.00% | -26.60% |
| DZ_12 | diode | +0.00% | n/a | +0.00% | n/a | -0.00% | -26.58% |
| DZ_24 | diode | +0.00% | n/a | +0.00% | n/a | -0.00% | -26.56% |

## What moved

- **MOS/VDMOS**: FF/SS widened from ±4.8–12.3 % to ±8.2–14.9 %, the `√k` pessimism of
  the sign-off convention. NMOS18 lands at +13.06 %/−11.69 %, inside the ±10–13 %
  the ruling predicted.
- **BJT and diode**: from flat everywhere to −20.7 % (BJT) and −26.6 % (diode) on the
  all-device corners — the `_VBE_template`/`_VF_template` realisation.
- **Resistors and capacitors**: unchanged on case 13/14; they were already correct, and
  per-variable ±3σ does not change a single-variable group's corner.

