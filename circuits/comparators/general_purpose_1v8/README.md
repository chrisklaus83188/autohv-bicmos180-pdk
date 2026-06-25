# General-purpose comparators — 1.8 V rail (AutoHV BiCMOS 180)

The 1.8 V port of the [`general_purpose`](../general_purpose/) (5 V) comparator
family. **Same topology, knobs, and tooling** — core devices are the 1.8 V class
(`NMOS18` / `PMOS18`). Topology + re-tuning guide:
[`../general_purpose/DESIGN_NOTES.md`](../general_purpose/DESIGN_NOTES.md).

- Two input flavours: `CMP_NIN` (high CM), `CMP_PIN` (low CM).
- Offset↔area knob `FIN` (gp/lo/lo2), plus `hyst`, `lp`, `fast` — 12 cells.
- **Supply range: 1.8 V ±10 % (1.62–1.98 V).**
- **Saturation rule: Vds/Vdsat > 1.1** — a *deliberate relaxation* from the 5 V
  rule of > 1.4. At 1.8 V, |Vth| ≈ 0.5–0.6 V is ~⅓ of the rail, so the 1.4 comfort
  margin can't be held while still covering mid-rail; > 1.1 keeps the current
  sources safely in saturation (just past the knee) with a little margin. See the
  5 V `SATURATION_SIGNOFF.md` discussion of the rule.

## Characterized variants

ngspice-45, TT, 27 °C, VDD 1.8 V, CL 1 pF, ±100 mV overdrive. `Vos_σ` = input-
referred 1σ, 200-run Monte Carlo (≈±7 %). Iq = worst case over output states.

| Variant | In | role | Iq (µA) | Vos_σ (mV) | Gain (dB) | tpd ↑/↓ (ns) | Hyst (mV) | Area (µm²) |
|---|---|---|---|---|---|---|---|---|
| `nin_gp`  | NMOS | normal      | 36.5 | 1.51 | 100 | 35 / 13  | —    | 143 |
| `nin_lo`  | NMOS | lower offset| 36.5 | 0.79 | 100 | 35 / 19  | —    | 323 |
| `nin_lo2` | NMOS | lowest      | 36.5 | 0.53 | 100 | 36 / 28  | —    | 623 |
| `nin_hyst`| NMOS | hysteresis  | 36.9 | 1.52 | 100 | 39 / 14  | 10.5 | 148 |
| `nin_lp`  | NMOS | low power   | 7.4  | 1.78 | 100 | 155 / 37 | —    | 143 |
| `nin_fast`| NMOS | fast        | 72.4 | 1.31 | 100 | 19 / 9   | —    | 143 |
| `pin_gp`  | PMOS | normal      | 35.8 | 2.10 | 100 | 9 / 21   | —    | 188 |
| `pin_lo`  | PMOS | lower offset| 35.8 | 1.08 | 100 | 14 / 21  | —    | 458 |
| `pin_lo2` | PMOS | lowest      | 35.8 | 0.72 | 100 | 21 / 25  | —    | 908 |
| `pin_hyst`| PMOS | hysteresis  | 36.3 | 1.93 | 100 | 10 / 25  | 12.2 | 200 |
| `pin_lp`  | PMOS | low power   | 7.2  | 2.27 | 100 | 24 / 90  | —    | 188 |
| `pin_fast`| PMOS | fast        | 71.3 | 2.09 | 100 | 6 / 12   | —    | 188 |

(High gain — 100 dB — from the high-mobility 1.8 V devices; fastest of the three
domains. Offset and the ≈1/FIN trend match the other supplies.)

## Saturation / ICMR (Vds/Vdsat > 1.1, across 5 corners, −40/+125 °C, 1.62–1.98 V)

All 12 cells pass the ≥ 1.1 rule over their ICMR. The `gp`/`lo`/`lo2`/`hyst` set
shares an ICMR; per-VDD (gp):

| | 1.62 V | 1.80 V | 1.98 V |
|---|---|---|---|
| NMOS-in ICMR | 0.84–1.28 | 0.84–1.49 | 0.84–1.69 |
| PMOS-in ICMR | 0.20–0.66 | 0.20–0.84 | 0.21–1.02 |
| **Joint (pair)** | 0.20–1.28 **(gap 0.66–0.84)** | **0.20–1.49 (continuous)** | **0.21–1.69 (continuous)** |

**Mid-rail coverage is continuous at nominal (1.8 V) and +10 %.** At the **−10 %
brown-out corner (1.62 V)** a ~0.18 V band around mid-rail (0.66–0.84 V) is covered
by neither flavour — the headroom floor of a single tail+pair stage at that rail
(|Vth| eats too much of 1.62 V). Notes:
- It's a *coverage* gap between the NIN and PIN cells, **not** a hole in either
  cell's ICMR (each is continuous). A design whose common mode sits in its NIN or
  PIN range is unaffected.
- In the gap the comparator still functions; the tail just dips below the 1.1
  margin. If the 1.8 V rail has its own UVLO above ~1.65 V (as the 5 V rail does at
  3.2 V), this corner never occurs. If mid-rail at 1.62 V must be covered, drop the
  current (`lp` ≈ 1 µA closes it) or use a rail-to-rail front end.

Reproduce: `python run_comparators.py` (specs) · `python run_saturation.py --pvt`
(ICMR; default threshold is 1.1 here). `VSUP=1.8` in `run_comparators.py`; supply
range auto-derives to ±10 %.

## Files
`cmp_gp.lib` (NMOS18/PMOS18) · `run_comparators.py` · `run_saturation.py` ·
`tb_example.cir` · `comparator_results.json`. Topology + tuning: the 5 V
`DESIGN_NOTES.md`.
