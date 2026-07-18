# Rail-to-rail input comparator — 5 V rail (AutoHV BiCMOS 180)

A single comparator (`CMP_RR`) whose **input common-mode range spans the full
supply, rail to rail** (0 → VDD), unlike the [`general_purpose`](../general_purpose/)
cells whose NMOS- and PMOS-input flavours each cover only part of the rail. This
is the reference 5 V design; the [3.3 V](../rail_to_rail_3v3/) and
[1.8 V](../rail_to_rail_1v8/) ports are device-swapped from it.

## How it works

Two input pairs run in parallel — an NMOS pair (carries high CM) and a PMOS pair
(carries low CM) — and their transconductances are **summed through a
folded-cascode stage**, so there is gm everywhere from rail to rail (both pairs
active mid-rail, one near each rail). The key reason it must sum at the *current*
level: a pair starved near a rail contributes ~zero current, whereas simply
OR-ing two separate comparators fails — the off comparator's output rails to a
stuck, opposite state and corrupts the result.

```
  Stage 1 : NMOS pair (Xn1/2) + PMOS pair (Xp1/2)
            -> top fold sources (Xf1/2) + PMOS cascodes (Xcp1/2)
            -> bottom NMOS mirror (Xmm1/2)            single-ended at 'b'
  Stage 2 : NMOS common-source + PMOS current-source load
  Stage 3 : CMOS inverter                              rail-to-rail digital out
```
Polarity: **OUT high when V(inp) > V(inn)**. Topology + tuning, and the bias
lesson below, are written up in [`../general_purpose/DESIGN_NOTES.md`](../general_purpose/DESIGN_NOTES.md) (§ rail-to-rail).

The one design subtlety: the PMOS cascode gate `vcp` is generated **VDD-referenced**
(VDD − 2|Vsg|), *not* ground-referenced. A ground-referenced bias pins the
NMOS-pair drains at a fixed level, so when VDD sags to brown-out the top fold
sources lose all their Vds and drop out of saturation. Referencing `vcp` to VDD
makes that node track the rail, holding the fold-source headroom across the whole
supply range (the single most headroom-critical spot in the cell).

## Enable (EN)

Active-high enable pin. `EN=1` = normal; `EN=0` shuts the cell down by **killing the bias**
(the core stays on the true rails): a 2-inverter buffer drives a series switch + gate-short
on the bias references (`ibp`/`pmd`) → every branch off → **zero static Iq** (leakage only).
The series switch also isolates the bias pin, so Iq is ~0 even with the external bias on. A
clamp on the stage-2 output holds `OUT` high when disabled. Tie `EN` high if unused.
The EN buffer uses the PDK async-logic `INV_*` cells, so decks must also include
`circuits/async_logic_design/cells.lib`.

## Offset ↔ area knob

The only knob is `FIN`, which scales **both input pairs and the bottom load
mirror** (W and L together, constant W/L → gm and the hand-off points held).
Matching area ∝ FIN², input-referred offset ≈ 1/FIN. Same idea as the GP family.

## Characterized variants

ngspice-45, TT, 27 °C, VDD 5 V, CL 1 pF, ±100 mV overdrive. `Vos_σ` = input-
referred 1σ offset, 200-run Monte Carlo at mid-rail (≈±7 %). Iq = worst case over
output states.

| Variant | FIN | role | Iq (µA) | Vos_σ (mV) | Gain (dB) | tpd ↑/↓ (ns) | Area (µm²) |
|---|---|---|---|---|---|---|---|
| `gp`  | 1 | normal / low area | 91.9 | 1.54 | 93  | 10 / 44 | 725 |
| `lo`  | 2 | lower offset      | 91.9 | 1.00 | 99  | 15 / 52 | 1565 |
| `lo2` | 3 | lowest offset     | 91.9 | 0.76 | 100 | 22 / 58 | 2965 |

Notes:
- **Iq ≈ 92 µA** is ~2× a GP cell — the cost of two input pairs + the fold/cascode
  and extra bias legs. The price of a rail-to-rail front end.
- **tpd is asymmetric** (fast ↑, slow ↓) from the single-ended stage-2; the slow
  edge is ~44–58 ns. If speed matters more than offset, raise IREF.
- **Systematic offset is small but CM-dependent** (gm imbalance between the pairs).
  For `gp`, the DC trip runs −3.5 / −1.1 / −0.7 mV at low / mid / high CM; it
  shrinks with FIN (`lo2`: −0.8 / −0.2 / −0.1 mV).

## Rail-to-rail saturation sign-off (Vds/Vdsat > 1.4)

`python run_saturation.py --pvt` — every **always-on** signal device (fold
sources, cascodes, load mirror, stage-2) holds **Vds/Vdsat > 1.4 over the entire
0→5 V input common mode, across 5 corners, −40/+125 °C, and 3.2–5.5 V**:

| VDD | always-on min Vds/Vdsat | binding corner |
|---|---|---|
| 3.2 V (UVLO) | **1.49** | SS / +125 °C |
| 5.0 V | 3.41 | FF / +125 °C |
| 5.5 V | 3.36 | FF / +125 °C |

The 3.2 V case is the harshest (a 36 % sag, far worse than ±10 %) yet still clears
1.4. The input pairs are exempt where they intentionally hand off (an off pair near
a rail is by design); they are saturated in their sole-active range and only dip in
the hand-off transition / skew-corner rail edges.

## Files
`cmp_rr.lib` (CMP_RR, NMOS50/PMOS50) · `run_rr.py` (specs/MC) ·
`run_saturation.py` (`--pvt` sign-off) · `tb_example.cir` (rail-to-rail demo) ·
`comparator_results.json`. Topology + tuning: `../general_purpose/DESIGN_NOTES.md`.
