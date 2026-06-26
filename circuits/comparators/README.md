# Comparators — AutoHV BiCMOS 180

Continuous-time CMOS comparators for the AutoHV process, in two architectures,
each provided for the 5 V, 3.3 V, and 1.8 V rails. All share the same conventions,
tooling, and the saturation sign-off rule.

## What's here

| Folder | Architecture | Rail | Input CM coverage |
|---|---|---|---|
| [`general_purpose/`](general_purpose/) | two-stage, NMOS- & PMOS-input | 5 V | partial (two flavours) |
| [`general_purpose_3v3/`](general_purpose_3v3/) | " | 3.3 V | partial |
| [`general_purpose_1v8/`](general_purpose_1v8/) | " | 1.8 V | partial |
| [`rail_to_rail_5v0/`](rail_to_rail_5v0/) | folded-cascode, rail-to-rail input | 5 V | **full 0→VDD** |
| [`rail_to_rail_3v3/`](rail_to_rail_3v3/) | " | 3.3 V | **full 0→VDD** |
| [`rail_to_rail_1v8/`](rail_to_rail_1v8/) | " | 1.8 V | **full 0→VDD** |

The single design/tuning reference is
**[`general_purpose/DESIGN_NOTES.md`](general_purpose/DESIGN_NOTES.md)** (topology,
what sets each spec, tuning recipes, gotchas, knob reference, and § 7 on the
rail-to-rail variant). Each folder's own `README.md` has the characterized numbers
for that cell.

### One-file library

For convenience, **[`comparators_all.lib`](comparators_all.lib)** is a single
consolidated SPICE library holding **all nine subckts** — every cell renamed with
a rail suffix so they coexist: `CMP_{NIN,PIN}_{5V0,3V3,1V8}` (general-purpose) and
`CMP_RR_{5V0,3V3,1V8}` (rail-to-rail). Drop-in usage:

```
.include "<...>/autohv_bicmos180_case.lib"   ; PDK device models
.include "comparators_all.lib"               ; all comparators
X1 inp inn out vdd 0 ibp_5uA vdd CMP_RR_5V0 IREF=5u FIN=1   ; last net = EN (vdd = enabled)
Ib vdd ibp_5uA 5u
```

It is auto-generated (bodies copied verbatim, so it's electrically identical to
the per-folder libs). Edit the per-folder `.lib` files and regenerate with
`python gen_comparators_all.py` — don't hand-edit the combined file.

## The two architectures

### 1. General-purpose two-stage (`CMP_NIN` / `CMP_PIN`)

`diff pair + current-mirror load → common-source gain stage → CMOS inverter`.
Two flavours because a single pair only senses part of the rail:
- **`CMP_NIN`** — NMOS input pair, senses the **upper** common-mode range.
- **`CMP_PIN`** — PMOS input pair, senses the **lower** common-mode range.

Lean (~37 µA), simple, good offset/gain. 12 cells per rail: the offset↔area trio
`gp`/`lo`/`lo2` (knob `FIN`) plus `hyst` (built-in hysteresis), `lp` (low power),
`fast`. **Use when** your input common mode lives in one half of the rail (the
usual case), or you want the lowest Iq / area / a hysteretic or low-power option.
Caveat: at the brown-out corner the NIN and PIN ranges can leave a mid-rail
*coverage gap* (documented per rail).

### 2. Rail-to-rail input (`CMP_RR`)

`complementary NMOS+PMOS pairs → folded-cascode current sum → CS gain → inverter`.
One cell whose input common mode spans the **whole supply** (0 → VDD): the two
pairs hand off across CM and their currents sum, so there's gm everywhere. Costs
~2× the Iq (~75–92 µA, second pair + fold) and is a bit slower. 3 cells per rail
(`gp`/`lo`/`lo2`, knob `FIN`). **Use when** the input common mode can be anywhere
rail to rail, or you need to cover mid-rail at brown-out (it closes the GP gap).
Key design point — the cascode bias is **VDD-referenced** so the front end keeps
saturation headroom as the rail sags (see DESIGN_NOTES § 7).

Both are non-inverting: **OUT is HIGH when V(inp) > V(inn)**.

## Picking one

| Need | Pick |
|---|---|
| CM in upper half of rail | `general_purpose` → `CMP_NIN` |
| CM in lower half of rail | `general_purpose` → `CMP_PIN` |
| CM anywhere rail-to-rail / mid-rail at brown-out | `rail_to_rail_*` → `CMP_RR` |
| Lowest Iq / area | `general_purpose` `gp` (or `lp` for ~1 µA) |
| Lowest offset (within a family) | `lo` / `lo2` (larger `FIN`) |
| Built-in hysteresis | `general_purpose` `hyst` (knob `HYSK`) |
| Fastest | `general_purpose` `fast` (or raise `IREF`) |

## How to adjust a design for different specs

All cells are parameterized; re-size with these per-instance knobs, then re-run the
two characterization scripts. Full recipes and trade-offs are in DESIGN_NOTES.md.

| Param | Scales | Moves | Holds | Where |
|---|---|---|---|---|
| `IREF` | all bias currents | speed, power, ICMR | offset, area | both |
| `FIN`  | input pair (+ load mirror) W&L | **offset ≈ 1/FIN**, area ∝ FIN² | gm, ICMR, ~gain | both |
| `HYSK` | steered hysteresis current | hysteresis window | — | GP |
| `WSCALE`,`WIN`,`LIN`,`LANA` | mirror/tail/stage geometry | drive, gain, offset, area | (ratios) | GP |

Rules of thumb (details + the "when knobs aren't enough" topology table in
DESIGN_NOTES §§ 3–5):
- **Lower offset:** raise `FIN` (more matched area). ~1/FIN, area ~FIN².
- **Faster:** raise `IREF` (current density); costs power and a little headroom.
- **Lower power / wider ICMR:** lower `IREF` (also lowers Vdsat → more headroom).
- **More gain:** longer `LANA` (GP) or move to a cascoded/3-stage front end.
- **Different rail:** swap the device class (NMOS50/33/18, PMOS50/33/18), re-bias,
  re-check (the ports in this directory are exactly this).
- **Beyond these** (sub-100 µV offset, ps-class clocked, HV sense): topology change
  — see DESIGN_NOTES § 5; the PDK's separate Cells A–D set covers those roles.

## Conventions (all cells)

- **Ports:** `inp inn out vdd vss <bias> EN` — the bias pin is **`ibp_5uA`** on `CMP_NIN`/`CMP_RR`
  (source 5 uA *into* it, from vdd) or **`ibn_5uA`** on `CMP_PIN` (sink 5 uA *out* of it, to vss).
  Drive it with a matching current source (e.g. `Ib vdd ibp_5uA 5u`); `vdd`/`vss` are the only
  supply rails (`vss` = ground). The `lp`/`fast` GP variants push 1 uA/10 uA into that same pin.
- **Enable (`EN`):** active-high. `EN=1` = normal; `EN=0` disables the cell — an
  on-chip 2-inverter buffer (`ENB=/EN`, `ENbuf=EN`) drives a PMOS header + NMOS footer
  that power-gate the analog core (**zero static Iq**, leakage only) and **force `OUT`
  low**. Tie `EN` high if unused; the external bias should also be gated off when `EN=0`.
- **Saturation sign-off:** every device meant to be saturated keeps **Vds/Vdsat >
  1.4** (5 V & 3.3 V) or **> 1.1** (1.8 V, the documented low-voltage relaxation),
  across process corners, −40/+125 °C, and the rail's supply range. Switches
  (output inverter, hysteresis steering) and the RR input pairs in their hand-off
  are exempt.
- **Supply range:** 5 V rail = 3.2–5.5 V (3.2 = chip UVLO); 3.3 V and 1.8 V = ±10 %.

## Reproduce

```
cd <cell folder>
python run_comparators.py   # GP families: specs + Monte-Carlo offset
python run_rr.py            # rail-to-rail families: specs + MC offset
python run_saturation.py --pvt   # both: Vds/Vdsat / ICMR sign-off across PVT
ngspice -b tb_example.cir   # runnable demo
```
`NGSPICE_BIN` selects the ngspice binary (auto-detected if unset).
