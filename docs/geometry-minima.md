# Geometry Minima & Defaults — AutoHV BiCMOS180 PDK

**Two floors per device, and honest placement defaults.** This is the summary artifact of the
`v2.2-defaults` program. It answers the question the program exists to close: *"am I oversizing,
and how small can I legally go?"*

- **Fabrication floor** — the hard geometric minimum below which the device cannot be built
  (`device_limits.csv`, basis-tagged). Placing a device *is* this size now (see Defaults).
- **Analog floor** — the minimum *sensible* size for matched/precision use, derived from the PDK's
  own measured mismatch data. **Guidance, not a hard rule.** A device between the two floors is
  buildable but will not match well.

**Analog-floor thresholds (stated):** matched-pair **σ(ΔI/I) = 20 %** for MOS (at the device's
lowest guide current) · **σ(ΔR/R), σ(ΔC/C) = 1 %** for passives. These are the sizing guide's
"min sensible (matched)" columns (`docs/sizing-guide.md`, v5.0-v2.2-defaults).

**Basis tags** (ground rule 3): `[grounded]` = reference catalog (0.25 µm BCD DRM/device catalog,
scaled/mapped) · `[derived]` = first-principles (T2 column) · `[declared]` = neither (listed below).
Verbatim reference values + page refs live in the uncommitted `LOCAL_onc25_extraction.md` (IP
discipline). **Models/anchors frozen at `v2-grounded` — this program touched only wrapper defaults,
`device_limits.csv`, xschem symbol defaults, the limits-reader, the sizing guide, and docs.**

**Convention change (ruled):** wrapper + symbol **defaults are now the fabrication minima**. An
unthinking placement yields the *smallest buildable* device; sizing up is a conscious act informed
by the analog column. (Before: `W=10u L=1u` — an unthinking placement gave a 10 µm transistor.)

---

## The two-floor table

*"Fab min" = the `device_limits.csv` minimum (= the new default). "T2 cross-check" = the
first-principles derivation. "Analog min" = min sensible for matched use (σ threshold above).
Read the two floors together: where analog < fab, the fab floor governs and matched use is fine at
minimum; where analog > fab, you must size up for matching.*

### MOS (BSIM3 core) — W / L (µm)

| device | fab Wmin | fab Lmin | tag | one-line basis | T2 cross-check (Wmin) | analog min W (σ<20%) | default |
|---|---|---|---|---|---|---|---|
| NMOS18/PMOS18 | 0.22 | 0.18 | `[grounded]` | ONC25 2.5 V-core DRM 0.30/0.24 × 0.72 (0.25→0.18 node) | contact 0.22 + 2×enc 0.06 ≈ 0.34 (thin-ox; within 2×) | 0.17 / 0.06 | W=0.22u L=0.18u |
| NMOS33/PMOS33 | 0.30 | 0.35 | `[grounded]` | ONC25 3.3 V DRM 0.40/0.35 × 0.72 | ≈ 0.36 | 0.13 / 0.04 | W=0.30u L=0.35u |
| NMOS50/PMOS50 | 0.40 | 0.50 | `[grounded]` | ONC25 5 V DRM 0.60/0.50 (thick-ox, W scaled) | ≈ 0.40 (thick-ox relaxed ×1.2) | 0.45 / 0.19 | W=0.40u L=0.50u |
| NMOS12/PMOS12 | 0.22 | 0.50 | `[grounded]` | 12 V has no planar Lmin → nearest planar = 5 V's 0.50; W core-scaled | ≈ 0.34 | 1.91 / 1.88 | W=0.22u L=0.50u |

*NMOS50 analog (0.45) slightly exceeds its fab floor (0.40): a 5 V matched pair wants the fab min or a
hair more. NMOS12/PMOS12 analog (~1.9) is ~9× the fab floor — the high 12 V-oxide A_VT means matched
12 V pairs must be sized up hard.*

### VDMOS (LDMOS + depletion) — W (µm), min gate finger

| device | fab Wmin | tag | one-line basis | T2 cross-check | analog min W (σ<20%) | default |
|---|---|---|---|---|---|---|
| NDMOS/PDMOS 20/40/60/80/120/200 | **3.0** | `[grounded]` | ONC25 DRM **HV min gate width 3.0 µm** | contact row + body tie + gate finger ≈ 3 µm | 1.1 – 2.4 | W=3u (200: +L=5.4u) |
| DNMOS20 (depletion) | **3.0** | `[grounded]` | same HV min gate finger | ≈ 3 µm | n/a (Idss self-bias) | W=3u |

**Ruling (maintainer-confirmed):** W < 3 µm is **clamped** — a fractional finger has no physical
construction, so sub-3 µm is *not* an extrapolation region. `m<1` is disallowed. The sizing guide's
VDMOS low-current mirror rows (gm/Id-6 width < 3 µm) are Wmin-clamped to 3 µm and flagged (the σ is
recomputed at the larger area). This is the change the program was written to make: AutoHV previously
allowed W = 2 µm (a fifth of the 10 µm characterization cell). VDMOS analog floors (1.1–2.4 µm) sit
*below* the 3 µm fab floor, so the fab floor governs — a min-finger VDMOS pair already matches to <20 %.

### BJT — AREA (relative, AREA=1 ≡ 100 µm² cell)

| device | fab AREAmin | tag | one-line basis | T2 cross-check | default |
|---|---|---|---|---|---|
| NPN_LV | **0.04** | `[grounded]` | min emitter 2×2 µm (4 µm²) / 100 µm² cell | contactable emitter 2 µm → 4 µm² = 0.04 | AREA=0.04 |
| NPN_HV / PNP_HV / PNP_LAT | **0.10** | `[grounded]` | min emitter 3.2×3.2 µm (10 µm²) / 100 µm² | 3.2 µm HV emitter → 10 µm² = 0.10 | AREA=0.10 |

*Reference emitter menu is quantized (2 / 5 / 10 µm → AREA 0.04 / 0.25 / 1.0); AutoHV stays continuous
with the menu listed as guidance.*

### Diodes / zeners — AREA (relative)

| device | fab AREAmin | tag | one-line basis | default |
|---|---|---|---|---|
| DIO_PN / DIO_FAST / DIO_SCH | **0.04** | `[derived]` | catalog silent on min junction area; min contactable junction ≈ BJT emitter fraction | AREA=0.04 |
| DZ_5V6 / DZ_12 / DZ_24 | **0.04** | `[derived]` | buried junction; catalog silent on min area | AREA=0.04 |

### Resistors / capacitors — W / L (µm)

| device | fab Wmin | fab Lmin | tag | one-line basis | T2 cross-check | analog min area (σ<1%) | default |
|---|---|---|---|---|---|---|---|
| RPOLY_HI/LO, RNWELL, RNPLUS, RPPLUS | 0.5 | 0.5 | `[derived]` | catalog silent on drawn-min; contactable poly head (1 contact + enclosure) at 180 nm | head-dominated below ~2 squares → analog min L = 2×W | 2.25 µm² (1 %-match) | L=0.5u W=0.5u |
| CMIM_STD/HI, CMOM, CFRINGE | 2.0 | 2.0 | `[derived]` | catalog silent; perimeter/corner-effect dominance below ~2–4 µm plate | ~2 µm plate | 0.56 µm² (1 %-match) | L=2u W=2u |

---

## `[declared]` entries (basis neither grounded nor derived)

Per acceptance, every `[declared]` minimum is listed with a reason. The only ones are structural
**M (device-multiplier) floors** — `M ≥ 1` on all MOS/VDMOS wrappers:

- **`<device>.M` min = 1 `[declared]`** (21 rows): the multiplier is an integer array count; its floor
  of 1 is a structural/arithmetic minimum, not a fabricated *size*. It is neither a catalog value nor a
  first-principles-derived length, hence `[declared]`. No physical geometry rides on it beyond "≥ 1
  instance."

No other device has a `[declared]` size floor — every W/L/AREA minimum is `[grounded]` or `[derived]`.

---

## Enforcement

- **`pdk_validation/preflight.py`** asserts **every wrapper default == its `device_limits` fabrication
  minimum** (`check_defaults_equal_minima`; negative-tested) and that rated operating points sit inside
  the SOA. Wired into the regression run (a hard gate in `regression.yml` and at `run_smoke.py` startup).
- **Sizing guide** (`docs/sizing-guide.md`) carries both floors per row; **no row sits below the fab
  floor** (VDMOS clamped to 3 µm; BSIM sizing-sweep floor 1 µm sits above the smaller fab Wmin, now
  shown explicitly).
- **Defaults flip is electrically invisible:** every repo instantiation is explicit (verified by grep,
  0 default-reliant), so regression is green with unchanged numbers through the flip.
