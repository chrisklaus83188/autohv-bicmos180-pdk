# Sizing Guide -- AutoHV BiCMOS180 PDK

**What sizes make sense at uA-level currents and nominal supplies.** MOS rows from the phase-3
characterization harness (diode-connected mirror, gm/Id ~ 6); R/C/BJT analytical from the fixed
sheet/density/mismatch values. TT / 27 C at class-nominal supply. Regenerated from the final
(phase-3b) model state -- **no known-optimistic columns**.

**How to choose:** MOS -- your device + bias current gives the **mirror** width W (gm/Id ~ 6);
for a gm stage size ~2x narrower (gm/Id 12-16), low-power ~4x wider (>= 20). sigma(dI/I) is the
matched-pair 1-sigma; halve it by 4x-ing area. Resistors default to **RPOLY_HI** (precision poly).
Capacitors: MIM for precision. BJT: AREA sets Vbe.

Trigger case: **200 V NMOS, 100 uA mirror -> NDMOS200, W ~ 13 um, Vov ~ 0.47 V, gm/Id ~ 6.4,
sigma(dI/I) ~ 9%** -- an ordinary strong-inversion front end (was: subthreshold, sigma(trip) 340-440 mV).

---

## MOS -- mirror sizing (gm/Id ~ 6)  [21 devices]

| device | supply | I(lo) W/Vgs/gmId/sig | I(mid) W/Vgs/gmId/sig | I(hi) W/Vgs/gmId/sig |
|---|---|---|---|---|
| NDMOS20 | 10.0V | 10uA: 1.3um / 1.289 / 5.89 / 18.51% | 100uA: 13.4um / 1.304 / 6.37 / 6.24% | 1000uA: 106.2um / 1.346 / 5.72 / 1.99% |
| NDMOS40 | 10.0V | 10uA: 1.3um / 1.346 / 5.88 / 19.64% | 100uA: 13.4um / 1.363 / 6.39 / 6.64% | 1000uA: 106.2um / 1.408 / 5.74 / 2.12% |
| NDMOS60 | 10.0V | 10uA: 1.3um / 1.401 / 5.87 / 20.77% | 100uA: 13.4um / 1.42 / 6.4 / 7.05% | 1000uA: 106.2um / 1.467 / 5.76 / 2.25% |
| NDMOS80 | 10.0V | 10uA: 1.3um / 1.457 / 5.85 / 21.84% | 100uA: 13.4um / 1.477 / 6.4 / 7.44% | 1000uA: 106.2um / 1.526 / 5.77 / 2.38% |
| NDMOS120 | 10.0V | 10uA: 1.3um / 1.517 / 5.84 / 22.96% | 100uA: 13.4um / 1.54 / 6.42 / 7.85% | 1000uA: 106.2um / 1.593 / 5.79 / 2.51% |
| NDMOS200 | 10.0V | 10uA: 1.3um / 1.586 / 5.82 / 25.13% | 100uA: 13.4um / 1.614 / 6.42 / 8.64% | 1000uA: 106.2um / 1.674 / 5.8 / 2.77% |
| PDMOS20 | 10.0V | 10uA: 4.7um / 1.306 / 6.39 / 10.5% | 100uA: 37.7um / 1.359 / 6.1 / 3.56% | 1000uA: 388.1um / 1.356 / 6.23 / 1.13% |
| PDMOS40 | 10.0V | 10uA: 4.7um / 1.357 / 6.37 / 11.13% | 100uA: 37.7um / 1.411 / 6.12 / 3.79% | 1000uA: 388.1um / 1.408 / 6.25 / 1.21% |
| PDMOS60 | 10.0V | 10uA: 4.7um / 1.407 / 6.36 / 11.76% | 100uA: 37.7um / 1.463 / 6.14 / 4.02% | 1000uA: 388.1um / 1.46 / 6.27 / 1.28% |
| PDMOS80 | 10.0V | 10uA: 4.7um / 1.457 / 6.33 / 12.37% | 100uA: 37.7um / 1.515 / 6.14 / 4.25% | 1000uA: 299.5um / 1.558 / 5.52 / 1.36% |
| PDMOS120 | 10.0V | 10uA: 4.7um / 1.509 / 6.32 / 12.99% | 100uA: 37.7um / 1.568 / 6.16 / 4.49% | 1000uA: 299.5um / 1.613 / 5.55 / 1.43% |
| PDMOS200 | 10.0V | 10uA: 4.7um / 1.573 / 6.29 / 14.21% | 100uA: 37.7um / 1.636 / 6.16 / 4.94% | 1000uA: 299.5um / 1.683 / 5.56 / 1.58% |
| NMOS18 | 1.8V | 1uA: 1.0um / 0.694 / 16.86 / 8.28% | 10uA: 1.3um / 0.883 / 6.37 / 2.77% | 100uA: 10.3um / 0.86 / 5.67 / 0.87% |
| PMOS18 | 1.8V | 1uA: 1.0um / 0.832 / 10.01 / 4.91% | 10uA: 3.7um / 0.925 / 5.8 / 1.5% | 100uA: 37.7um / 0.875 / 6.01 / 0.48% |
| NMOS33 | 3.3V | 1uA: 1.0um / 0.983 / 12.86 / 7.21% | 10uA: 2.2um / 1.126 / 5.77 / 2.21% | 100uA: 22.4um / 1.035 / 6.01 / 0.72% |
| PMOS33 | 3.3V | 1uA: 1.0um / 1.187 / 7.22 / 4.05% | 10uA: 6.1um / 1.18 / 5.57 / 1.27% | 100uA: 63.2um / 1.124 / 5.75 / 0.41% |
| NMOS50 | 5.0V | 1uA: 1.0um / 1.366 / 8.61 / 13.29% | 10uA: 4.7um / 1.36 / 5.7 / 4.08% | 100uA: 48.8um / 1.264 / 5.91 / 1.32% |
| PMOS50 | 5.0V | 1uA: 1.3um / 1.578 / 5.55 / 7.58% | 10uA: 13.4um / 1.413 / 5.9 / 2.51% | 100uA: 137.6um / 1.364 / 6.06 / 0.8% |
| NMOS12 | 12.0V | 1uA: 2.8um / 2.059 / 6.3 / 16.45% | 10uA: 22.4um / 1.794 / 5.73 / 5.31% | 100uA: 231.1um / 1.716 / 5.85 / 1.69% |
| PMOS12 | 12.0V | 1uA: 6.1um / 2.143 / 6.25 / 11.06% | 10uA: 63.2um / 1.93 / 6.43 / 3.55% | 100uA: 503.0um / 1.94 / 5.79 / 1.13% |

### DNMOS20 (depletion) -- Vgs=0 self-biased current source
Idss = **54.742 uA/um** at Vgs=0. Not a mirror-Vov device; size for self-biased duty:

| target I | W (Vgs=0) | sigma(dI/I) | note |
|---|---|---|---|
| 1 uA | 0.018 um | 26.47% | < 1um drawn-min: use W=1um + source-degen R to trim Idss |
| 10 uA | 0.183 um | 8.37% | < 1um drawn-min: use W=1um + source-degen R to trim Idss |
| 100 uA | 1.8 um | 2.65% | direct |

## Resistors -- default RPOLY_HI (precision poly)

| target | layer | squares | area (um2) | sigma(dR/R) | tc1 (ppm/C) | drift -40..150C | area-saving alt |
|---|---|---|---|---|---|---|---|
| 1000 Ohm | **RPOLY_HI** | 0.8 | 3.0 | 0.82% | -1400 | -26.6% | RNWELL 0.6sq (WARN: 76.0% drift, structural VCR -- off signal only) |
| 10000 Ohm | **RPOLY_HI** | 8.3 | 33.0 | 0.26% | -1400 | -26.6% | RNWELL 5.6sq (WARN: 76.0% drift, structural VCR -- off signal only) |
| 100000 Ohm | **RPOLY_HI** | 83.3 | 333.0 | 0.08% | -1400 | -26.6% | RNWELL 55.6sq (WARN: 76.0% drift, structural VCR -- off signal only) |
| 1e+06 Ohm | **RPOLY_HI** | 833.3 | 3333.0 | 0.03% | -1400 | -26.6% | RNWELL 555.6sq (WARN: 76.0% drift, structural VCR -- off signal only) |

## Capacitors

| target | layer | area (um2) | side (um) | sigma(dC/C) | matching bits |
|---|---|---|---|---|---|
| 0.1pF | CMIM_HI | 50.0 | 7.1 | 0.106% | 8.1 |
| 1pF | CMIM_HI | 500.0 | 22.4 | 0.034% | 9.8 |
| 10pF | CMIM_HI | 5000.0 | 70.7 | 0.011% | 11.4 |

## BJT -- AREA per decade of Ic

| device | 10uA Vbe/beta | 100uA Vbe/beta | 1mA Vbe/beta | pair sig(dVbe) | eff fT |
|---|---|---|---|---|---|
| NPN_LV | 0.637/140 | 0.696/140 | 0.756/140 | 0.15 mV | ~1 GHz-class |
| PNP_LAT | 0.601/35 | 0.661/35 | 0.72/35 | 0.15 mV | ~1 GHz-class |
| NPN_HV | 0.678/80 | 0.738/80 | 0.797/80 | 0.15 mV | ~1 GHz-class |
| PNP_HV | 0.655/18 | 0.714/18 | 0.774/18 | 0.15 mV | ~1 GHz-class |

---

*Machine-readable: `docs/sizing-guide.json` (v2.0-phase3b). Regenerate: `sizing_guide.py {vdmos,bsim}` then `gen_sizing_docs.py`.*
