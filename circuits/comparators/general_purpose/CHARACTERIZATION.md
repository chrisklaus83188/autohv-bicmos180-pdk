# General-purpose comparator family — characterization report
### AutoHV BiCMOS 180 PDK · 5 V rail · `circuits/comparators/general_purpose/`

Two-stage continuous-time voltage comparator (diff pair + current-mirror load →
common-source gain → rail-to-rail CMOS inverter), in NMOS-input and PMOS-input
flavors, with one design knob (`FIN`) that trades **input offset against area**
with no auto-zeroing or chopping. This report focuses on the input-offset
characterization (500-run Monte Carlo) and the offset↔area trade.

## 1. Conditions & method

| | |
|---|---|
| Simulator | ngspice-45 (KLU), PDK `autohv_bicmos180_case.lib` (BSIM3) |
| Nominal | case=0 (TT), 27 °C, VDD = 5 V, CL = 1 pF, ±100 mV overdrive |
| **Offset** | input-referred 1σ from **500-run Monte Carlo** (`MM_ON=1`); ≈±3 % on σ |
| Gain / tpd / Iq | deterministic, nominal corner; Iq = worst of the two output states |
| Saturation / ICMR | 5 process corners × {−40, +27, +125 °C} × {3.2, 5.0, 5.5 V} |

Reproduce: `python run_comparators.py --mc-n 500` (offset/specs),
`python run_saturation.py --pvt` (ICMR / Vds·Vdsat sign-off).

## 2. The offset↔area knob (`FIN`)

`FIN` scales the **stage-1 matching set** (input pair + load mirror), W and L
together. W/L is held constant, so device **overdrives — and therefore ICMR, gm,
gain, and current — do not change**; only matching (∝ √area) improves:

> **offset ∝ 1/FIN  ·  stage-1 area ∝ FIN²**  →  halving the offset costs ~4× stage-1 area.

| `FIN` | cell | NMOS-in σ (mV) | NMOS area (µm²) | PMOS-in σ (mV) | PMOS area (µm²) |
|------:|------|----------------|-----------------|----------------|-----------------|
| 1 | `gp` (normal)  | **1.76** | 143 | **2.14** | 188 |
| 2 | `lo`           | **0.91** | 323 | **1.13** | 458 |
| 3 | `lo2`          | **0.56** | 623 | **0.70** | 908 |

`gp`→`lo`→`lo2` reduce 1σ offset by ~48 % then ~68 % vs `gp`, for ~2.3× then
~4.4× the area. `FIN` is continuous — set any value (e.g. `FIN=6` ≈ 0.3 mV) for
points between or beyond. Equivalent ±3σ input offset (a common spec basis):

| | `gp` | `lo` | `lo2` |
|---|---|---|---|
| NMOS-in ±3σ | ±5.3 mV | ±2.7 mV | ±1.7 mV |
| PMOS-in ±3σ | ±6.4 mV | ±3.4 mV | ±2.1 mV |

This is purely passive device matching — no auto-zero, chopper, or trim.

## 3. Full variant table

500-MC offset; nominal-corner gain/tpd/Iq/area. `hyst` and `lp` are one-knob
siblings of `gp` (FIN=1).

| Variant | In | role | Iq (µA) | Vos σ (mV) | Vos_sys (mV) | Gain (dB) | tpd ↑/↓ (ns) | Hyst (mV) | Area (µm²) |
|---------|----|------|---------|------------|--------------|-----------|--------------|-----------|------------|
| `nin_gp`  | NMOS | normal       | 40.9 | 1.76 | +0.40 | 92  | 54 / 18  | —    | 143 |
| `nin_lo`  | NMOS | lower offset | 40.9 | 0.91 | +0.02 | 98  | 61 / 26  | —    | 323 |
| `nin_lo2` | NMOS | lowest offset| 40.9 | 0.56 | −0.03 | 99  | 66 / 36  | —    | 623 |
| `nin_hyst`| NMOS | + hysteresis | 41.2 | 1.76 | +0.39 | 100 | 59 / 19  | 10.4 | 148 |
| `nin_lp`  | NMOS | low power    | 8.9  | 1.90 | +0.37 | 95  | 217 / 50 | —    | 143 |
| `nin_fast`| NMOS | fast        | 79.0 | 1.77 | +0.44 | 90  | 33 / 13  | —    | 143 |
| `pin_gp`  | PMOS | normal       | 38.3 | 2.14 | −0.68 | 93  | 13 / 36  | —    | 188 |
| `pin_lo`  | PMOS | lower offset | 38.3 | 1.13 | −0.08 | 98  | 20 / 43  | —    | 458 |
| `pin_lo2` | PMOS | lowest offset| 38.3 | 0.70 | −0.02 | 97  | 29 / 50  | —    | 908 |
| `pin_hyst`| PMOS | + hysteresis | 38.7 | 2.18 | −0.59 | 100 | 15 / 44  | 13.2 | 200 |
| `pin_lp`  | PMOS | low power    | 8.0  | 2.35 | −0.62 | 94  | 33 / 142 | —    | 188 |
| `pin_fast`| PMOS | fast        | 75.2 | 1.93 | −0.78 | 90  | 10 / 22  | —    | 188 |

Notes: Iq is state-dependent (~2:1, single-ended stage-2); worst case shown. tpd
asymmetric, flips sign N↔P — quote the slow edge. `lp` offset is higher because
its low current pushes the pair toward weak inversion (load contributes more).
Systematic offset collapses with FIN (bigger devices match better).

**`fast` — speed vs the saturation rule.** Speed comes from current *density*
(higher overdrive on the internal nodes), not from current-scaling: scaling
current and width together holds I/C constant on the high-impedance nodes, so a 4×
current-scaled cell is the same speed at 4× power/area (verified: 51 vs 54 ns).
`fast` instead raises density ~2× (IREF 5→10 µA, same widths): ~1.6× faster, same
area. But higher overdrive raises Vdsat, so the ICMR narrows (PIN at 3.2 V:
0.24–0.95 V vs gp 0.21–1.26 V) — the price of speed against the Vds/Vdsat margin.
A 4× density cell is ~2.5× faster but fails the 1.4 rule at 3.2 V, so it is not
shipped.

## 4. ICMR & saturation (summary)

Every device meant to be saturated holds **Vds/Vdsat > 1.4** across all 5 corners,
−40/+125 °C, and 3.2–5.5 V, over each part's rated input common-mode range. The
`gp`/`lo`/`lo2`/`hyst` set shares an ICMR (FIN preserves overdrives):

| | 3.2 V | 5.0 V | 5.5 V |
|---|---|---|---|
| NMOS-in ICMR | 1.71–2.72 | 1.71–4.73 | 1.70–5.27 |
| PMOS-in ICMR | 0.21–1.26 | 0.22–3.07 | 0.22–3.58 |

As a complementary pair: continuous 0.2 V→~VDD−0.2 at 5.0/5.5 V; a ~0.45 V gap at
mid-rail at 3.2 V (tail headroom limit). Full methodology, per-variant bands, the
device-role analysis, and the dropped-`WB`/`fast` rationale are in
[`SATURATION_SIGNOFF.md`](SATURATION_SIGNOFF.md).

## 5. Limits

- BSIM3 model sign-off, not silicon. No ESD/clamp, glitch suppression, or trim.
- `fast` is density-limited by the 1.4 rule (see the `fast` note in §3): ~1.6× over
  `gp` is the saturation-clean ceiling across 3.2–5.5 V; more speed needs a higher
  supply floor or a different topology.
- The bias pin (`ibp_5uA` / `ibn_5uA`) expects a clean `IREF` (PTAT/bandgap-derived in a real system).
