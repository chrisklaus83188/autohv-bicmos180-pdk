# Sizing Guide -- AutoHV BiCMOS180 PDK

**What sizes make sense at uA-level currents and nominal supplies.** Generated from the phase-3
characterization harness (MOS) and analytical from the fixed sheet/density/mismatch values (R/C/BJT).
TT / 27 C at class-nominal supply.

**How to choose (per family):**

- **MOS:** find your device + bias current. `W` is the **mirror/reference** width (gm/Id ~ 6). For a
  **general gm stage** size ~2x narrower (gm/Id 12-16); for **low-power** ~4x wider (gm/Id >= 20).
  `sigma(dI/I)` is the matched-pair 1-sigma -- halve it by quadrupling area. VDMOS use L = L_REF; BSIM3 at Lmin.
- **Resistors:** pick the row's layer; poly for stability, n-well only for large values off signal.
- **Capacitors:** MIM for precision (matching-limited bits shown), MOM/fringe for density-insensitive.
- **BJT:** AREA multiple sets Vbe; beta is flat across the recommended Ic window.

The trigger this was built for: **200 V NMOS, 100 uA mirror -> NDMOS200, W ~ 13 um, Vov ~ 0.47 V,
gm/Id ~ 6.4, sigma(dI/I) ~ 9%** -- an ordinary strong-inversion front end. (Before the fix: subthreshold,
sigma(trip) 340-440 mV.)

---

## MOS -- mirror sizing (gm/Id ~ 6)

| device | supply | I(lo) | W | Vgs | gm/Id | sig(dI/I) | I(mid) | W | Vgs | gm/Id | sig | I(hi) | W | Vgs | gm/Id | sig |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NDMOS20 | 10.0V | 10uA | 1.3 | 1.287 | 5.89 | 18.52% | 100uA | 13.4 | 1.302 | 6.37 | 6.24% | 1000uA | 106.2 | 1.343 | 5.72 | 1.99% |
| NDMOS40 | 10.0V | 10uA | 1.3 | 1.349 | 5.88 | 19.64% | 100uA | 13.4 | 1.366 | 6.39 | 6.64% | 1000uA | 106.2 | 1.412 | 5.74 | 2.12% |
| NDMOS60 | 10.0V | 10uA | 1.3 | 1.412 | 5.87 | 20.76% | 100uA | 13.4 | 1.432 | 6.4 | 7.05% | 1000uA | 106.2 | 1.482 | 5.76 | 2.25% |
| NDMOS80 | 10.0V | 10uA | 1.3 | 1.475 | 5.85 | 21.82% | 100uA | 13.4 | 1.499 | 6.4 | 7.44% | 1000uA | 106.2 | 1.554 | 5.77 | 2.38% |
| NDMOS120 | 10.0V | 10uA | 1.3 | 1.556 | 5.83 | 22.9% | 100uA | 13.4 | 1.585 | 6.42 | 7.85% | 1000uA | 106.2 | 1.651 | 5.79 | 2.51% |
| NDMOS200 | 10.0V | 10uA | 1.3 | 1.675 | 5.78 | 24.98% | 100uA | 13.4 | 1.717 | 6.41 | 8.63% | 1000uA | 106.2 | 1.806 | 5.8 | 2.77% |
| PDMOS20 | 10.0V | 10uA | 4.7 | 1.306 | 6.39 | 10.5% | 100uA | 37.7 | 1.359 | 6.1 | 3.56% | 1000uA | 388.1 | 1.356 | 6.23 | 1.13% |
| PDMOS40 | 10.0V | 10uA | 4.7 | 1.357 | 6.37 | 11.13% | 100uA | 37.7 | 1.412 | 6.12 | 3.79% | 1000uA | 388.1 | 1.409 | 6.25 | 1.21% |
| PDMOS60 | 10.0V | 10uA | 4.7 | 1.41 | 6.36 | 11.76% | 100uA | 37.7 | 1.467 | 6.14 | 4.02% | 1000uA | 388.1 | 1.464 | 6.27 | 1.28% |
| PDMOS80 | 10.0V | 10uA | 4.7 | 1.462 | 6.33 | 12.36% | 100uA | 37.7 | 1.522 | 6.14 | 4.25% | 1000uA | 299.5 | 1.568 | 5.52 | 1.36% |
| PDMOS120 | 10.0V | 10uA | 4.7 | 1.519 | 6.32 | 12.98% | 100uA | 37.7 | 1.583 | 6.16 | 4.49% | 1000uA | 299.5 | 1.632 | 5.55 | 1.43% |
| PDMOS200 | 10.0V | 10uA | 4.7 | 1.596 | 6.28 | 14.19% | 100uA | 37.7 | 1.67 | 6.16 | 4.94% | 1000uA | 299.5 | 1.727 | 5.56 | 1.58% |
| NMOS18 | 1.8V | 1uA | 1.0 | 0.694 | 16.86 | 8.28% | 10uA | 1.3 | 0.883 | 6.37 | 2.77% | 100uA | 10.3 | 0.86 | 5.67 | 0.87% |
| PMOS18 | 1.8V | 1uA | 1.0 | 0.832 | 10.01 | 4.91% | 10uA | 3.7 | 0.925 | 5.8 | 1.5% | 100uA | 37.7 | 0.875 | 6.01 | 0.48% |
| NMOS33 | 3.3V | 1uA | 1.0 | 0.983 | 12.86 | 7.21% | 10uA | 2.2 | 1.126 | 5.77 | 2.21% | 100uA | 22.4 | 1.035 | 6.01 | 0.72% |
| PMOS33 | 3.3V | 1uA | 1.0 | 1.187 | 7.22 | 4.05% | 10uA | 6.1 | 1.18 | 5.57 | 1.27% | 100uA | 63.2 | 1.124 | 5.75 | 0.41% |
| NMOS50 | 5.0V | 1uA | 1.0 | 1.366 | 8.61 | 5.44% | 10uA | 4.7 | 1.36 | 5.7 | 1.67% | 100uA | 48.8 | 1.264 | 5.91 | 0.54% |
| PMOS50 | 5.0V | 1uA | 1.3 | 1.578 | 5.55 | 3.1% | 10uA | 13.4 | 1.413 | 5.9 | 1.03% | 100uA | 137.6 | 1.364 | 6.06 | 0.33% |
| NMOS12 | 12.0V | 1uA | 1.3 | 2.053 | 5.89 | 4.39% | 10uA | 13.4 | 1.777 | 6.24 | 1.45% | 100uA | 137.6 | 1.698 | 6.4 | 0.46% |
| PMOS12 | 12.0V | 1uA | 2.8 | 2.198 | 5.75 | 2.91% | 10uA | 29.1 | 1.968 | 6.02 | 0.95% | 100uA | 299.5 | 1.923 | 6.15 | 0.3% |

## Resistors -- value to layer / squares / area / matching / drift

| target | layer | squares | area (um2) | sig(dR/R) | tc1 (ppm/C) | drift -40..150 C |
|---|---|---|---|---|---|---|
| 1000 Ohm | RPOLY_HI | 0.8 | 3.0 | 0.82% | -1400 | -26.6% |
| 10000 Ohm | RNWELL | 5.6 | 22.0 | 0.85% | 4000 | 76.0% |
| 100000 Ohm | RNWELL | 55.6 | 222.0 | 0.27% | 4000 | 76.0% |
| 1e+06 Ohm | RNWELL | 555.6 | 2222.0 | 0.08% | 4000 | 76.0% |

## Capacitors -- value to layer / area / matching

| target | layer | area (um2) | side (um) | sig(dC/C) | matching bits |
|---|---|---|---|---|---|
| 0.1pF | CMIM_HI | 50.0 | 7.1 | 0.106% | 8.1 |
| 1pF | CMIM_HI | 500.0 | 22.4 | 0.034% | 9.8 |
| 10pF | CMIM_HI | 5000.0 | 70.7 | 0.011% | 11.4 |

## BJT -- AREA per decade of Ic

| device | 10uA Vbe/beta | 100uA Vbe/beta | 1mA Vbe/beta | pair sig(dVbe) |
|---|---|---|---|---|
| NPN_LV | 0.637V/140 | 0.696V/140 | 0.756V/140 | 0.15 mV |
| PNP_LAT | 0.601V/35 | 0.661V/35 | 0.72V/35 | 0.15 mV |
| NPN_HV | 0.678V/80 | 0.738V/80 | 0.797V/80 | 0.15 mV |
| PNP_HV | 0.655V/18 | 0.714V/18 | 0.774V/18 | 0.15 mV |

---

*Machine-readable: `docs/sizing-guide.json`. Regenerate: `python pdk_validation/characterization/sizing_guide.py {vdmos,bsim}`.*
