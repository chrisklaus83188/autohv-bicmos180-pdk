# device_limits.csv v2 — proposed abs-max / SOA schema (pass-3 T2)

**Status: proposal, not applied.** The current `pdk_validation/device_limits.csv` is **geometry-only**
(L/W/M/LCH ranges). A real process ships a per-device **safe-operating-area (SOA) envelope** alongside
geometry — the voltage, current, thermal, and isolation limits a design-rule checker enforces. This
document proposes a v2 schema that adds that envelope, with derived example rows for all 40 AutoHV
devices. Values are scaled/rounded from the SOA pattern of **a commercial 0.25 µm automotive BCD
process** (per the IP rules — no third-party device names or verbatim numbers); they are illustrative
engineering figures for the maintainer to ratify, not measured AutoHV limits.

## What the reference SOA schema looks like

Each reference device section carries an **SOA Checks** table with the columns
`Name · Unit · Node1 · Node2 · Min · Max · Note(duration)`. The structure, generalized:

- **Terminal-pair voltage windows**, one row per pair {ds, gs, gd, gb, bs, bd} (MOS) / {ce, cb, be}
  (BJT) / {reverse, forward} (diode), each at three severities:
  - `absmax` (never exceed, any duration),
  - `dcmax` (continuous / 100 ns-referenced),
  - `vpulse_1ns` / `vpulse_5ns` (short-pulse allowances, between dcmax and absmax).
- **Per-contact current density**: `id_cont_dens` (DC, A/contact) and `idpuls_cont_dens` (pulsed) —
  i.e. current limits are enforced per contact/plug, scaling with device width.
- **Time-to-fail lifetime bins**: `ttf10y / ttf1y / ttf1e6s / ttf1e5s` — reliability, not a hard rail.
- **Junction temperature** ceiling (from the qual range) and, for **isolated** devices, a
  **substrate-isolation voltage** (~44 V-class for the HV isolation tubs; ~10 V for PBL-to-NBL).

Representative reference values that calibrate the scaling below:
- 5 V CMOS: Vds absmax ±7, dcmax ±5.5, vpulse_1ns ±5.75; Vgs same; Vbs/Vbd −9 (fwd-limited).
- 40 V-class (44 V) LDMOS: Vds absmax 46, dcmax 44; Vgs (5 V-gate) absmax ±7, dcmax ±5.5;
  id_cont_dens ±0.47 mA/contact (200 ns), idpuls ±15 mA/contact (~32× the DC value).
- Isolation: NBL→substrate and HVNW→HVPWISO ~44 V; PBL→NBL ~10 V.

## Proposed v2 CSV schema

Keep the existing geometry rows (`L`, `W`, `M`, `LCH`) and **add** SOA-envelope rows. Extend the header
to `device,param,min,max,unit,basis,note` (adds `unit` and `basis`; `basis` ∈ {grounded, scaled,
extrapolated, industry}). New `param` keys:

| param | applies to | meaning |
|---|---|---|
| `Vds_absmax` / `Vds_dcmax` | MOS/VDMOS | drain-source never-exceed / continuous |
| `Vgs_absmax` / `Vgs_dcmax` | MOS/VDMOS | gate-source never-exceed / continuous (set by gate-oxide class) |
| `Vgd_absmax` | VDMOS | gate-drain (matters for HV off-state) |
| `Vce_max` / `Vcb_max` / `Vbe_rev` | BJT | collector-emitter / collector-base / reverse base-emitter |
| `Vr_absmax` / `Vf_max` | diode/zener | reverse blocking / forward |
| `Vz_nom` | zener | nominal breakdown |
| `Vop_max` | resistor/cap | working voltage (cap: continuous << breakdown) |
| `Idc_dens` / `Ipulse_dens` | MOS/VDMOS/BJT/diode | DC / pulsed current density (per µm width, or per AREA for BJT) |
| `Tj_max` | all active | junction-temperature ceiling |
| `Viso` | isolated HV | substrate-isolation voltage (blank = non-isolated) |

**Scaling rules used for the example rows** (stated so every value is re-derivable):
`Vds_absmax = rated × 1.15` (VDMOS) or the reference LV pattern (5 V→7, ~1.4×) for thin-oxide MOS;
`Vds_dcmax = rated × 1.10`; `Vgs_absmax/dcmax` from the gate-oxide class (5 V-gate → ±7/±5.5, 12 V-gate
→ ±15/±13); `Idc_dens ≈ 1 mA/µm` (LV thin-oxide ~2 mA/µm), `Ipulse_dens ≈ 30 × Idc` (from the reference
0.47→15 mA/contact ratio); `Tj_max = 150 °C` (D7); `Viso ≈ rated × 1.15` for isolated HV parts.

## Derived example rows — all 40 AutoHV devices

Voltages in V, current density per µm (BJT/diode per unit AREA), Tj in °C. **All `scaled`/`extrapolated`
unless noted.**

### Thin/thick-oxide CMOS (8)
| device | Vds_absmax | Vds_dcmax | Vgs_absmax | Vgs_dcmax | Idc_dens | Ipulse_dens | Tj_max |
|---|---|---|---|---|---|---|---|
| NMOS18 / PMOS18 | 2.3 | 2.0 | ±2.3 | ±2.0 | 2.0 | 40 | 150 |
| NMOS33 / PMOS33 | 4.3 | 3.6 | ±4.3 | ±3.6 | 1.6 | 40 | 150 |
| NMOS50 / PMOS50 | 7.0 | 5.5 | ±7.0 | ±5.5 | 1.2 | 35 | 150 |
| NMOS12 / PMOS12 | 15 | 13.2 | ±15 | ±13.2 | 0.9 | 25 | 150 |

*(NMOS50/PMOS50 Vds/Vgs absmax ±7 / dcmax ±5.5 are `grounded` — the reference 5 V device directly.)*

### N-VDMOS (6) — 5 V-gate, so Vgs_absmax ±7 / Vgs_dcmax ±5.5 for all
| device | class | Vds_absmax | Vds_dcmax | Vgd_absmax | Idc_dens | Ipulse_dens | Viso | Tj_max |
|---|---|---|---|---|---|---|---|---|
| NDMOS20 | 20 | 23 | 22 | 23 | 1.0 | 30 | 23 | 150 |
| NDMOS40 | 40 | 46 | 44 | 46 | 1.0 | 30 | 46 | 150 |
| NDMOS60 | 60 | 69 | 66 | 69 | 0.9 | 27 | 69 | 150 |
| NDMOS80 | 80 | 92 | 88 | 92 | 0.9 | 27 | 92 | 150 |
| NDMOS120 | 120 | 138 | 132 | 138 | 0.8 | 24 | 138 | 150 |
| NDMOS200 | 200 | 230 | 220 | 230 | 0.7 | 20 | 230 | 150 |

*(NDMOS40 absmax 46 / dcmax 44 are `grounded`; 20 V is interpolated; 60–200 V `extrapolated`.)*

### P-VDMOS (6) — same gate/Vgs pattern; magnitudes negative
| device | class | Vds_absmax | Vds_dcmax | Idc_dens | Ipulse_dens | Viso | Tj_max |
|---|---|---|---|---|---|---|---|
| PDMOS20 | 20 | −23 | −22 | 0.4 | 12 | −23 | 150 |
| PDMOS40 | 40 | −46 | −44 | 0.35 | 11 | −46 | 150 |
| PDMOS60 | 60 | −69 | −66 | 0.33 | 10 | −69 | 150 |
| PDMOS80 | 80 | −92 | −88 | 0.30 | 9 | −92 | 150 |
| PDMOS120 | 120 | −138 | −132 | 0.27 | 8 | −138 | 150 |
| PDMOS200 | 200 | −230 | −220 | 0.22 | 7 | −230 | 150 |

*(P current density ≈ N/2.5 — the grounded P/N penalty. PDMOS40 −46/−44 `grounded`.)*

### Depletion (1)
| device | class | Vds_absmax | Vds_dcmax | Vgs_absmax | Idc_dens | Tj_max |
|---|---|---|---|---|---|---|
| DNMOS20 | 20 | 23 | 22 | ±7 | 1.0 (Idss ~0.1 at Vgs=0) | 150 |

### Bipolar (4) — current density per unit AREA (=100 µm² cell, D3 grounded)
| device | Vce_max | Vcb_max | Vbe_rev | Idc (mA/AREA) | Ipulse (mA/AREA) | Tj_max |
|---|---|---|---|---|---|---|
| NPN_LV | 7 | 18 | 4 | 5 | 150 | 150 |
| NPN_HV | 25 | 60 | 5 | 5 | 150 | 150 |
| PNP_HV | −22 | −22 | 4 | 3 | 90 | 150 |
| PNP_LAT | −13 | −18 | 4 | 3 | 90 | 150 |

*(Vce/Vcb `grounded` to the reference NPN/PNP breakdown menu: LV NPN BVceo ~8/BVcbo ~18; HV NPN
BVceo ~25/BVcbo ~60; PNP ~18–22. Per-contact-current pattern 0.47→15 mA maps to the AREA figures above.)*

### Diodes (3) & Zeners (3)
| device | Vr_absmax | Vf_max | Vz_nom | Idc_dens | Tj_max |
|---|---|---|---|---|---|
| DIO_PN | 100 | 1.0 | — | 1.0 | 150 |
| DIO_FAST | 40 | 1.0 | — | 1.0 | 150 |
| DIO_SCH | 40 | 0.45 | — | 1.0 | 150 |
| DZ_5V6 | (working < 5.6) | 1.0 | 5.6 | 0.5 | 150 |
| DZ_12 | (< 12) | 1.0 | 12 | 0.5 | 150 |
| DZ_24 | (< 24) | 1.0 | 24 | 0.5 | 150 |

*(Schottky Vf 0.45 / BV pattern `grounded` — reference DSCH Vf ~0.2 @1 µA, BV 25/38/50 for the 18/30/40 V
Schottky classes. Zener Vz `grounded`.)*

### Resistors (5) & Capacitors (4)
| device | Vop_max | note | Tj_max |
|---|---|---|---|
| RPOLY_HI / RPOLY_LO | ±(depends on L; ~a few V/µm of body) | poly-body voltage; VCR **synthetic** (see freeze line) | 150 |
| RNWELL | ±(structural, VCR large) | well resistor — keep off signal nodes | 150 |
| RNPLUS / RPPLUS | ± diffusion working | diffusion resistors | 150 |
| CMIM_STD / CMIM_HI | **15 continuous, 26 absmax** | `grounded`: reference MIM breakdown 26.8 V, cont SOA <15 V | 150 |
| CMOM / CFRINGE | metal-stack working (tens of V) | fringe caps between metals | 150 |

## How to apply (maintainer)

1. Extend the CSV header to `device,param,min,max,unit,basis,note`; keep all existing geometry rows.
2. Add the SOA rows above as `min,max` pairs (e.g. `NDMOS40,Vds_dcmax,0,44,V,grounded,continuous`),
   tagging `basis` per the scaling rules. Symmetric limits use `−x,+x`.
3. Wire the checker to warn when a bias in a testbench exceeds `dcmax` and error above `absmax`.
4. The **only `grounded` rows** are the 5 V CMOS and 40 V-class LDMOS voltage limits, the Schottky/zener
   voltages, the BJT breakdowns, and the MIM cap voltages; everything else is `scaled`/`extrapolated`
   and should be treated as a starting envelope, not a spec.

This closes T2: the schema shape is grounded against a real catalog's SOA structure, and all 40 devices
have a first derived envelope. Refining the extrapolated HV rows shares the freeze line's error bar
(±~30 % above the 40 V class — see `process-declarations.md` §"Synthetic residue").
