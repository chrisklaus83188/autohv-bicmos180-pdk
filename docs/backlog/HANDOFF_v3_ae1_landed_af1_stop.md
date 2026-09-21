# Handoff: AE1 landed; a §2 stop on what Phase 2 did to the corners

**Responds to:** the AE1 ruling (option 3 — template source plus shared parser; do not revert; land Phase 2)
**Branch:** `mc-realism` @ `b1d333d` (parent `2374161`)
**Date:** 2026-09-20
**Status:** AE1 is implemented, verified and committed. The acceptance bar is met exactly.
The 40-device × case table you asked for then showed something neither of us had measured:
**37 of 40 devices changed their corner response**, and **10 of them now have none at all**.
That is a §2 stop.

---

## 1. AE1 — done, and the acceptance bar is met exactly

Both rules from the ruling are now enforced in code, not just written down.

**A generator never reads the file it writes.** `gen_models.py` transforms a checked-in
`autohv_bicmos180_case_models.inc.in` — byte-identical to the previous authored `.inc`,
1575 lines, 183 `_isTT` markers — and emits the `.inc` (1553 lines, 0 markers). It refuses
to run if the input path resolves to the output path.

**Parsers raise; they do not return `None`.** `tools/inc_parse.py` is the single parser for
all six expression forms, with a unit test. In `measure_stat_directions.tt_of`, "absent from
the card" and "present but unreadable" no longer share a return value.

Evidence, each measured rather than argued:

| check | result |
|---|---|
| generated `.inc` from `.in` vs. the previously generated file | **byte-identical**, 1553 lines |
| σ(`VTH_NMOS5V0`) +10 % → card | `0.016492` → **`0.0181412`** (before: unchanged) |
| σ edit → `--check` | **red**; restore → **green** (before: could never go red) |
| input == output path | **guard fires** |
| `tt_of` on the five degraded records | all read; `kp DNMOS20V_INT` → `0.00145115` via its `_STAT` reference |
| skipped targets in the 40-group run | **none** |

The five degraded records return to their Stop A′ values **exactly**, not merely within the
allowed deltas:

| group | required | measured | terms |
|---|---|---|---|
| NPN_LV | 26.0 % | **26.0 %** | 3 |
| PNP_LAT | 31.4 % | **31.4 %** | 3 |
| NPN_HV | 25.9 % | **25.9 %** | 3 |
| PNP_HV | 32.2 % | **32.2 %** | 3 |
| DNMOS20V | 9.35 % | **9.3540 %** | 3 |

All four checks green: `test_inc_parse`, `gen_models --check`, `stat_model_inventory --check`,
`build_corners --check`. Corner distances unchanged (presets 3/4 at 13.1787).

**On the "eight consumers":** only **three** ever parsed card expressions — `gen_models`,
`measure_stat_directions`, `stat_model_inventory` — and all three are done. The other five
read the file for a verbatim `.model` block lift (`exp_lib`), plain geometry values
(`passives`, where `narrow`/`short` are still deterministic), or packaging (`make_release`,
`run_passives`, `char_lib`). My earlier "eight consumers, six unverified" overstated it.

## 2. §2 STOP — Phase 2 changed the corner response of 37 of 40 devices

`tools/case_table.py` (new) measures every device's classic-bench metric at each case. I ran
it on `b1d333d` and on its parent, so only the notation differs.

### 2.1 The MOS corner spread collapsed by roughly 5×

| device | FF before | FF after | SS before | SS after |
|---|---|---|---|---|
| NMOS1V8 | +24.902 % | **+4.945 %** | −21.745 % | **−4.800 %** |
| PMOS1V8 | +33.839 % | **+7.021 %** | −27.476 % | **−6.643 %** |
| NMOS5V0 | +18.286 % | +6.479 % | −16.567 % | −6.192 % |
| DNMOS20V | +20.010 % | +9.820 % | −18.104 % | −9.059 % |

I believe this is correct and is the point of the program: the new corners equal the
**measured 3σ direction**. NMOS1V8's FF/SS spread is now 9.7 % against a measured 3σ swing of
9.2 %; the old hand-set ±25 % was roughly 5σ of the statistics we now have. But it changes
the result of every existing corner simulation, so I am not calling it silently.

Only three devices (PDMOS80V, NDMOS120V, PDMOS120V) are unchanged within 2 pp.

### 2.2 BJTs and diodes have no corner response on ANY preset — a defect

Resistors and capacitors do not move on cases 1–4, which is by design: presets 1–4 contain
only the 21 MOS/VDMOS groups. They move properly on their own presets —
RNWELL −23.7 % / +31.0 % on 7/8, CMIM_STD −21.3 % / +27.1 % on 9/10.

**BJTs and diodes move by ±0.001 % on presets 11/12 and 13/14 as well.** They are dead
everywhere. The cause is the same class as AD1:

| template | `applies_to` | realized in a card? |
|---|---|---|
| `_BF_template` | `bf` | yes |
| `_RPAR_template` | `rb`/`rc`/`re` | yes |
| `_RS_DIO_template` | `rs` | yes |
| `_CJ_DIO_template` | `cjo` | yes |
| `_BV_template` | `bv` + `.lib` wrapper (AD1) | yes |
| **`_VBE_template`** | **null** | **no** |
| **`_VF_template`** | **null** | **no** |

`VBE_*` and `VF_*` are the **dominant** term in all ten BJT and diode directions, and neither
has an `applies_to`. So the generator emits nothing and the card keeps a deterministic
`is=2e-16`, while `corners.json` faithfully assigns `VBE_NPN_LV = −2.6725`. Nothing consumes
it. `bf` does carry a draw, but at a fixed-V_BE bench the collector current is set by `is`,
not `bf` — hence the ±0.001 %.

Quantified: **NPN_LV at preset 11 should move −18.68 %** (σ_VBE = 2 mV, σ/V_T = 0.0774, z =
−2.6725). It moves −0.001 %.

This predates Phase 2 — the `_isXX` notation moved BJTs at FF/SS because each card carried
hand-set corner values, which masked the fact that no *statistical* variable ever reached
`is`. Phase 2 did not break it; it removed the cover.

### 2.3 Why neither of us caught this earlier

`corners.json` could not have shown it. **Every group is renormalised to exactly 3σ**, so a
group contributes 3.0 to the Mahalanobis distance whether it has one term or six — I verified
all 40 are exactly 3.0000. The distance table is structurally blind both to a degraded
direction and to a variable that is declared but realized nowhere. The AD1 gain of +0.3460
was precisely √(12.8327² + 3²): "one more group", independent of its contents.

## 3. Smaller findings

- **A literal backspace byte in `gen_models.py`.** The `P_` guard read `re.search(r"\bP_[A-Z]")`
  in my source but held `chr(8)` in the file — a patch script had written `"\b"` in a non-raw
  string. The arm had been dead the whole time. It matches no template line today, so output
  is unaffected; fixed and now the only control character in the toolchain.
- **`inc_parse._strip` stripped braces before the trailing `$` comment**, so an annotated
  generated card would have failed to parse. No line hits it today. Ordering fixed, case tested.
- **A vacuous invariant.** `stat_model_inventory`'s "no corner moves geometry" (the R0
  prerequisite) was counting a set that matched nothing after Phase 2 — it passed trivially. It
  now counts both notations, tests all 137 statistical expressions, and still returns 0.
- **Diode `V_f` must be solved once at case 0 and held.** Re-solving per case re-hits the target
  current by construction and reports zero movement for every diode.

## 4. What I got wrong this round

| claim / action | what was true |
|---|---|
| measured "HEAD" for the before/after table *after* committing | HEAD was by then the Phase 2 file; I compared it with itself and got all zeros. Caught only because it contradicted an earlier run — the two disagreeing measurements are the only reason I looked. |
| "eight consumers read the `.inc`, six unverified" | three parse expressions; the other five do block lifts, plain values or packaging |
| my first `migrate_gen.py` search string | assumed the fix I thought I had applied; the file held a control character instead |

## 5. Questions

1. **The MOS spread collapse (§2.1) — confirm intended.** Corners now equal the measured 3σ
   rather than the legacy hand-set ≈5σ. Every existing corner sim changes. Is that the intended
   landing point, or do you want a documented multiplier on top of 3σ for sign-off corners?

2. **`_VBE_template` / `_VF_template` `applies_to` (§2.2).** This is the AD1 shape again. My
   proposal: `{"param": "is", "form": "exp_v"}`, realized as
   `is={IS_TT*exp((σ_VBE/V_T)*Z_VBE_<dev>)}` with σ/V_T folded at generation (0.0774 for BJTs,
   0.1033 for diodes), so the card carries a plain multiplicative draw and `V_T` does not appear
   in the model file. That matches how the directions harness already measures VBE
   (`form="exp_v"`, `scale=1/V_T`). Confirm the form, and whether the 27 °C `V_T` should be
   frozen at generation or made temperature-dependent.

3. **Case numbering.** `case` now indexes 17 presets, but the `.lib` header still documents
   `0=TT 1=FF 2=SS 3=FS 4=SF`. Do designers get the full 0–16 menu, or should 1–4 remain
   "everything fast/slow" by having presets 1–4 include all 40 groups? I did not touch the
   header because the right wording depends on your answer.

4. **A CI assertion on per-group term counts.** Since distance is blind to degradation (§2.3),
   I propose asserting each group's expected term count in `build_corners --check` — the check
   that would have caught AE1 on day one. Worth adding, or does it over-constrain Phase 3?

## 6. State

`b1d333d` on `mc-realism`, working tree clean. New: `autohv_bicmos180_case_models.inc.in`,
`tools/inc_parse.py`, `tools/test_inc_parse.py`, `tools/gen_models.py`, `tools/case_table.py`,
`docs/case-table.md`.

I have **not** touched `_VBE_template`/`_VF_template` or the `.lib` header, pending your ruling.
The naming pass and Phase 3 are still queued behind this.
