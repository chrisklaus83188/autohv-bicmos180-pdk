# General-purpose comparators (AutoHV BiCMOS 180, 5 V)

A family of **continuous-time (static)** voltage comparators on the 5 V core
devices (`NMOS50` / `PMOS50`). One topology, one low-area base sizing, with a
single knob (`FIN`) that trades **input offset against area** — so you can get a
lower offset by spending area on the input stage, with no auto-zeroing or other
dynamic-offset-cancellation tricks.

Location: `circuits/comparators/general_purpose/`. Decks include the PDK via
`../../../autohv_bicmos180_case.lib` (three levels up to the PDK root).

## Topology

Two-stage transconductance comparator with a rail-to-rail CMOS output:

```
   Stage 1                 Stage 2              Stage 3
 diff pair + mirror   common-source gain    CMOS inverter
  inp ->|                                        |-> out (0 / VDD)
        | gm, single-ended -> gain+level-shift --|
  inn ->|                                        |
```

- **Polarity:** OUT is HIGH when V(inp) > V(inn) (non-inverting).
- **Output:** full rail-to-rail (VOH 5.000 / VOL 0.000) — drives logic directly.
- **DC gain:** ~90–100 dB.
- **Bias:** one reference current `IREF` into `nb` (`Itail = 2·IREF`, stage-2 = `4·IREF`).

Two input flavours: `CMP_NIN` (NMOS pair, high common mode) and `CMP_PIN`
(PMOS pair, low common mode); as a pair they cover the rail (see sign-off).

## Design knobs (`cmp_gp.lib`)

`CMP_NIN` / `CMP_PIN` params: `IREF`, `WSCALE`, `WIN`, `LIN`, `LANA`, `FIN`, `HYSK`.

- **`FIN` — the offset↔area knob (default 1).** Scales the **stage-1 matching set
  (input pair + load mirror)**, W and L together. Because W/L is held constant,
  Vov (→ICMR) and gm (→gain) are unchanged; only matching improves:
  **offset ∝ 1/FIN, stage-1 area ∝ FIN².** `FIN=1` = low-area "normal";
  `FIN`>1 = lower offset.
- `IREF` sets current → speed/power (offset and area unchanged).
- `WSCALE`, `LANA`, `WIN`, `LIN` are the base geometry (kept fixed across the family).
- `HYSK` = hysteresis current as a fraction of IREF (0 = none); bounded, cannot latch.

**Why this works:** ICMR is set by device *overdrives* (current + W/L ratios);
input offset by absolute gate *area* (W·L). `FIN` grows area at constant W/L, so
offset moves and ICMR/gain hold. (An earlier `WB` bias-mirror-widening knob was
removed — trimming current or sizing the pair is more area-efficient. See
`SATURATION_SIGNOFF.md`.)

## Characterized variants

ngspice-45, TT, 27 °C, VDD 5 V, CL 1 pF, ±100 mV overdrive. `Vos_σ` = input-
referred 1σ offset, 60-run Monte Carlo. Iq = worst case over both output states.

| Variant   | In   | role | Iq (µA) | Vos_σ (mV) | Gain (dB) | tpd↑/↓ (ns) | Hyst (mV) | Area (µm²) |
|-----------|------|------|---------|------------|-----------|-------------|-----------|------------|
| `nin_gp`  | NMOS | normal      | 40.9 | 1.76 | 92  | 54 / 18  | —    | **143** |
| `nin_lo`  | NMOS | lower offset| 40.9 | 0.91 | 98  | 61 / 26  | —    | 323 |
| `nin_lo2` | NMOS | lowest offset| 40.9 | 0.56 | 99 | 66 / 36  | —    | 623 |
| `nin_hyst`| NMOS | + hysteresis| 41.2 | 1.76 | 100 | 59 / 19  | 10.4 | 148 |
| `nin_lp`  | NMOS | low power   | 8.9  | 1.90 | 95  | 217 / 50 | —    | 143 |
| `nin_fast`| NMOS | fast        | 79.0 | 1.77 | 90  | 33 / 13  | —    | 143 |
| `pin_gp`  | PMOS | normal      | 38.3 | 2.14 | 93  | 13 / 36  | —    | **188** |
| `pin_lo`  | PMOS | lower offset| 38.3 | 1.13 | 98  | 20 / 43  | —    | 458 |
| `pin_lo2` | PMOS | lowest offset| 38.3 | 0.70 | 97 | 29 / 50  | —    | 908 |
| `pin_hyst`| PMOS | + hysteresis| 38.7 | 2.18 | 100 | 15 / 44  | 13.2 | 200 |
| `pin_lp`  | PMOS | low power   | 8.0  | 2.35 | 94  | 33 / 142 | —    | 188 |
| `pin_fast`| PMOS | fast        | 75.2 | 1.93 | 90  | 10 / 22  | —    | 188 |

`Vos_σ` is input-referred 1σ from **500-run Monte Carlo** (≈±3 % on σ). The
≈1/FIN trend (offset halves as stage-1 area quadruples) is exact.

(Iq is state-dependent ~2:1 — single-ended stage-2 conducts in one output state;
worst case shown. tpd is asymmetric and flips sign N↔P — quote the slow edge.)

## Offset vs area — the `FIN` study

Sweeping `FIN` on the base sizing (everything else fixed):

| `FIN` | role | NIN: Vos_σ / area | PIN: Vos_σ / area | gain |
|-------|------|-------------------|-------------------|------|
| 1 | `gp` (normal) | 1.76 mV / 143 µm² | 2.14 mV / 188 µm² | 92–93 dB |
| 2 | `lo`          | 0.91 mV / 323     | 1.13 mV / 458     | 98 dB |
| 3 | `lo2`         | 0.56 mV / 623     | 0.70 mV / 908     | 97–99 dB |
| 4 | (knob, est.)  | ~0.45 mV / 1042   | ~0.55 mV / 1538   | 99–100 dB |

(FIN 1–3 are 500-run MC; FIN=4 is an unshipped illustration of the knob.)
The classic matching law: **offset ∝ 1/FIN, stage-1 area ∝ FIN²** — to halve the
offset, ~4× the stage-1 area. Iq is dead constant across `FIN`; ICMR is unchanged
(W/L preserved); gain rises ~6 dB from `gp`→`lo` then plateaus; systematic offset
also collapses (NIN +0.40→0.02 mV). Pick the point you need, or set any `FIN` —
e.g. `FIN=6` ≈ 0.3 mV for ~2300 µm². It's all passive matching, no auto-zero.

## Picking a variant

- **Default:** `nin_gp` / `pin_gp` — smallest, ~1.6–1.8 mV offset.
- **Lower offset, no auto-zero:** `*_lo` (~0.9–1.1 mV, ~2.4× area) or `*_lo2`
  (~0.56–0.70 mV, ~4.5× area). Bump `FIN` further for less.
- **Noisy input:** `*_hyst` — ~10–13 mV hysteresis at normal size.
- **Power-critical:** `*_lp` — ~8 µA (slower; note offset rises in weak inversion).
- **Speed-critical:** `*_fast` — ~1.6× faster than `gp` (NIN 33/13, PIN 10/22 ns)
  at ~2× current, same area, holds Vds/Vdsat > 1.4 across 3.2–5.5 V — at a narrower ICMR.
- N vs P by common mode (NIN high, PIN low; see sign-off for ICMR).

**On `fast`:** speed comes from current *density* (higher overdrive), **not** from
current-scaling — scaling current and width together keeps I/C on the internal
nodes constant and does not speed it up (verified: 4× current-scaled = 51 vs 54 ns).
`fast` raises density ~2× (IREF 5→10 µA at the same widths): ~1.6× faster, but the
higher Vdsat narrows the ICMR (e.g. PIN at 3.2 V → 0.24–0.95 V vs gp's 0.21–1.26 V).
Pushing density to 4× is ~2.5× faster but fails the 1.4 rule at 3.2 V — not shipped.

## Saturation sign-off (Vds/Vdsat > 1.4)

Every device intended to run in saturation holds **Vds/Vdsat > 1.4 across all 5
process corners, −40/+125 °C, and 3.2–5.5 V** over each part's rated input
common-mode range (ICMR; inputs-balanced). The whole `gp`/`lo`/`lo2`/`hyst` set
**shares an ICMR** (`FIN` preserves overdrives); `lp` is a touch wider (less
current), `fast` a touch narrower. Per-VDD ICMR (NIN ≈ [1.7, VDD−0.2];
PIN ≈ [0.2, VDD−1.9]) and full methodology are in
[`SATURATION_SIGNOFF.md`](SATURATION_SIGNOFF.md).

**Joint NIN+PIN coverage:** continuous **0.2 V → ~VDD−0.2** at 5.0/5.5 V. At
**3.2 V** there is a **~0.4 V gap at mid-rail** (PIN to ~1.3 V, NIN from ~1.7 V) —
the headroom limit of a single tail+pair stage at low supply. The parts still
function through it; the tail just dips below the 1.4 margin. Raise `IREF` there
if you need it.

## Files

- `cmp_gp.lib` — the two parameterized cells (`CMP_NIN`, `CMP_PIN`).
- `DESIGN_NOTES.md` — topology explanation + how to re-tune/re-architect for other specs.
- `tb_example.cir` — runnable demo: `ngspice -b tb_example.cir`.
- `run_comparators.py` — characterization (offset/gain/Iq/tpd/hyst, MC offset).
- `run_saturation.py` — Vds/Vdsat sign-off (`--pvt`, `--cm-scan`, `--thresh`).
- `CHARACTERIZATION.md` — characterization report (500-MC offset, offset↔area study).
- `SATURATION_SIGNOFF.md` — the saturation result in full.
- `comparator_results.json` — machine-readable results (500-MC offset + specs).

## Notes

- Sizings are validated against the PDK BSIM3 models, not silicon.
- No ESD/clamp, glitch suppression, or offset trim — add per application.
- Bias `nb` expects a clean `IREF` (PTAT/bandgap-derived in a real system).
- `NGSPICE_BIN` is auto-detected; override if your `ngspice_con` is elsewhere.
