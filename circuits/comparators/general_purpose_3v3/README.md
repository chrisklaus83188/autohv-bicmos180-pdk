# General-purpose comparators — 3.3 V rail (AutoHV BiCMOS 180)

The 3.3 V port of the [`general_purpose`](../general_purpose/) (5 V) comparator
family. **Same topology, knobs, and tooling** — only the core devices change to
the 3.3 V class (`NMOS33` / `PMOS33`). For the topology explanation and the
re-tuning guide, see [`../general_purpose/DESIGN_NOTES.md`](../general_purpose/DESIGN_NOTES.md).

- Two input flavours: `CMP_NIN` (high CM), `CMP_PIN` (low CM).
- Offset↔area knob `FIN` (gp/lo/lo2), plus `hyst`, `lp`, `fast` — 12 cells.
- **Supply range: 3.3 V ±10 % (2.97–3.63 V).** Saturation rule: **Vds/Vdsat > 1.4**
  (same as 5 V — 3.3 V has the headroom; no relaxation needed).

## Characterized variants

ngspice-45, TT, 27 °C, VDD 3.3 V, CL 1 pF, ±100 mV overdrive. `Vos_σ` = input-
referred 1σ, 200-run Monte Carlo (≈±7 %). Iq = worst case over output states.

| Variant | In | role | Iq (µA) | Vos_σ (mV) | Gain (dB) | tpd ↑/↓ (ns) | Hyst (mV) | Area (µm²) |
|---|---|---|---|---|---|---|---|---|
| `nin_gp`  | NMOS | normal      | 38.2 | 1.55 | 96  | 48 / 15  | —    | 143 |
| `nin_lo`  | NMOS | lower offset| 38.2 | 0.79 | 100 | 50 / 22  | —    | 323 |
| `nin_lo2` | NMOS | lowest      | 38.2 | 0.48 | 100 | 53 / 31  | —    | 623 |
| `nin_hyst`| NMOS | hysteresis  | 38.6 | 1.56 | 100 | 53 / 16  | 10.1 | 148 |
| `nin_lp`  | NMOS | low power   | 7.9  | 1.70 | 100 | 209 / 45 | —    | 143 |
| `nin_fast`| NMOS | fast        | 75.3 | 1.61 | 99  | 27 / 10  | —    | 143 |
| `pin_gp`  | PMOS | normal      | 36.8 | 2.21 | 98  | 10 / 30  | —    | 188 |
| `pin_lo`  | PMOS | lower offset| 36.8 | 1.01 | 99  | 16 / 33  | —    | 458 |
| `pin_lo2` | PMOS | lowest      | 36.8 | 0.79 | 100 | 24 / 37  | —    | 908 |
| `pin_hyst`| PMOS | hysteresis  | 37.2 | 2.18 | 100 | 12 / 37  | 12.2 | 200 |
| `pin_lp`  | PMOS | low power   | 7.5  | 2.53 | 100 | 29 / 128 | —    | 188 |
| `pin_fast`| PMOS | fast        | 73.0 | 1.99 | 99  | 8 / 18   | —    | 188 |

(Offset/area trend ≈1/FIN holds; gains run a touch higher than 5 V from the lower-
Vth devices. Same knobs/behaviour as the 5 V family.)

## Saturation / ICMR (Vds/Vdsat > 1.4, across 5 corners, −40/+125 °C, 2.97–3.63 V)

All 12 cells pass. The `gp`/`lo`/`lo2`/`hyst` set shares an ICMR; per-VDD (gp):

| | 2.97 V | 3.3 V | 3.63 V |
|---|---|---|---|
| NMOS-in ICMR | 1.24–2.65 | 1.24–3.02 | 1.25–3.38 |
| PMOS-in ICMR | 0.21–1.55 | 0.21–1.88 | 0.21–2.21 |
| **Joint (pair)** | **0.21–2.65** | **0.21–3.02** | **0.21–3.38** |

**Continuous coverage, no mid-rail gap across the full ±10 %** — unlike the 5 V
part (which gaps at its 3.2 V brown-out corner) and the 1.8 V part. At 3.3 V the
~0.9 V/side stage budget leaves ample overlap.

Reproduce: `python run_comparators.py` (specs) · `python run_saturation.py --pvt`
(ICMR / Vds·Vdsat). `VSUP=3.3` is set in `run_comparators.py`; the saturation
supply range auto-derives to ±10 %.

## Files
`cmp_gp.lib` (NMOS33/PMOS33) · `run_comparators.py` · `run_saturation.py` ·
`tb_example.cir` · `comparator_results.json`. Topology + tuning: the 5 V
`DESIGN_NOTES.md`; sign-off method: the 5 V `SATURATION_SIGNOFF.md`.
