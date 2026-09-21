# Corner response: the Q1 and Finding-A changes, device by device

Three states of the same 40 benches, same harness — only the PDK files differ:

1. **`b1d333d`** — joint-3σ construction, `VBE_*`/`VF_*` unrealised.
2. **after Q1** — per-variable ±3σ corners, `is` carrying the BJT/diode draw with a
   single folded `σ/V_T`.
3. **after Finding A** — the emission coefficient `n` read per card, in both the
   generator and the harness, followed by a re-measure and corner rebuild.

Percentages are against each device's own case 0. `n/a` marks a preset the device does
not participate in; presets 1–4 move the MOS groups only (ruling Q3).

| device | kind | FF (1) b1d333d | after Q1 | after A | SS (2) b1d333d | after Q1 | after A | slow-all (13) b1d333d | after Q1 | after A |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| NMOS1V8 | mos | +4.95% | +13.06% | +13.06% | -4.80% | -11.69% | -11.69% | -4.80% | -11.69% | -11.69% |
| PMOS1V8 | mos | +7.02% | +14.31% | +14.31% | -6.64% | -12.66% | -12.66% | -6.64% | -12.66% | -12.66% |
| NMOS3V3 | mos | +6.13% | +12.50% | +12.50% | -5.88% | -11.26% | -11.26% | -5.88% | -11.26% | -11.26% |
| PMOS3V3 | mos | +7.75% | +13.16% | +13.16% | -7.26% | -11.78% | -11.78% | -7.26% | -11.78% | -11.78% |
| NMOS5V0 | mos | +6.48% | +12.32% | +12.32% | -6.19% | -11.13% | -11.13% | -6.19% | -11.13% | -11.13% |
| PMOS5V0 | mos | +7.86% | +12.81% | +12.81% | -7.35% | -11.51% | -11.51% | -7.35% | -11.51% | -11.51% |
| NMOS12V | mos | +5.88% | +8.66% | +8.66% | -5.69% | -8.20% | -8.20% | -5.69% | -8.20% | -8.20% |
| PMOS12V | mos | +7.25% | +10.24% | +10.24% | -6.84% | -9.44% | -9.44% | -6.84% | -9.44% | -9.44% |
| NDMOS20V | vdmos | +7.69% | +12.76% | +12.76% | -7.16% | -11.43% | -11.43% | -7.16% | -11.43% | -11.43% |
| PDMOS20V | vdmos | +8.39% | +11.16% | +11.16% | -7.76% | -10.09% | -10.09% | -7.76% | -10.09% | -10.09% |
| NDMOS40V | vdmos | +8.52% | +13.99% | +13.99% | -7.97% | -12.38% | -12.38% | -7.97% | -12.38% | -12.38% |
| PDMOS40V | vdmos | +7.90% | +11.96% | +11.96% | -7.34% | -10.76% | -10.76% | -7.34% | -10.76% | -10.76% |
| NDMOS60V | vdmos | +9.42% | +14.71% | +14.71% | -8.79% | -12.92% | -12.92% | -8.79% | -12.92% | -12.92% |
| PDMOS60V | vdmos | +8.82% | +14.35% | +14.35% | -8.24% | -12.65% | -12.65% | -8.24% | -12.65% | -12.65% |
| NDMOS80V | vdmos | +9.78% | +11.59% | +11.59% | -9.29% | -10.75% | -10.75% | -9.29% | -10.75% | -10.75% |
| PDMOS80V | vdmos | +9.86% | +14.88% | +14.88% | -9.20% | -13.12% | -13.12% | -9.20% | -13.12% | -13.12% |
| NDMOS120V | vdmos | +11.34% | +12.87% | +12.87% | -10.51% | -11.69% | -11.69% | -10.51% | -11.69% | -11.69% |
| PDMOS120V | vdmos | +11.05% | +12.57% | +12.57% | -10.30% | -11.46% | -11.46% | -10.30% | -11.46% | -11.46% |
| NDMOS200V | vdmos | +12.30% | +13.66% | +13.66% | -11.22% | -12.25% | -12.25% | -11.22% | -12.25% | -12.25% |
| PDMOS200V | vdmos | +12.27% | +13.63% | +13.63% | -11.21% | -12.22% | -12.22% | -11.21% | -12.22% | -12.22% |
| DNMOS20V | vdmos | +9.82% | +16.33% | +16.33% | -9.06% | -14.28% | -14.28% | -9.06% | -14.28% | -14.28% |
| RPOLY_HI | resistor | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -18.11% | -18.14% | -18.14% |
| RPOLY_LO | resistor | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -13.89% | -13.93% | -13.93% |
| RNWELL | resistor | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -23.66% | -23.66% | -23.66% |
| RNPLUS | resistor | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -10.43% | -10.43% | -10.43% |
| RPPLUS | resistor | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -13.93% | -13.93% | -13.93% |
| CMIM_STD | capacitor | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -21.34% | -21.34% | -21.34% |
| CMIM_HI | capacitor | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -21.34% | -21.34% | -21.34% |
| CMOM | capacitor | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -32.98% | -32.98% | -32.98% |
| CFRINGE | capacitor | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -32.80% | -32.80% | -32.80% |
| NPN_LV | bjt | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -0.00% | -20.71% | -20.71% |
| PNP_LAT | bjt | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -0.01% | -20.72% | -20.36% |
| NPN_HV | bjt | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -0.00% | -20.72% | -20.72% |
| PNP_HV | bjt | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -0.02% | -20.73% | -20.20% |
| DIO_PN | diode | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -0.00% | -26.61% | -25.52% |
| DIO_FAST | diode | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -0.00% | -26.62% | -25.96% |
| DIO_SCH | diode | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -0.00% | -26.63% | -24.93% |
| DZ_5V6 | diode | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -0.00% | -26.60% | -23.59% |
| DZ_12V | diode | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -0.00% | -26.58% | -23.06% |
| DZ_24V | diode | +0.00% | n/a | n/a | +0.00% | n/a | n/a | -0.00% | -26.56% | -22.38% |

## What each change did

- **Q1 (per-variable ±3σ)** widened MOS/VDMOS FF/SS from ±4.8–12.3 % to ±8.2–14.9 %,
  the `√k` pessimism of the sign-off convention, and took BJTs and diodes from flat
  everywhere to responding on the all-device corners.
- **Finding A (`n` per card)** narrowed the diode and PNP corners only, by exactly `1/n`
  on the `VF`/`VBE`-dominated part: DZ_24V by −18.0 % relative (1/1.22 = −18.03 %),
  DIO_PN by −4.8 % (1/1.05 = −4.76 %). The two NPNs carry `nf` = 1 and are
  bit-identical, which is the check that the change touched nothing it should not.
- MOS, VDMOS, resistors and capacitors are untouched by Finding A — none carries an
  emission coefficient.

