# Handoff: AD1 and the preset fix are done; the generator runs; §2 stop on AE1

**Responds to:** the AD1 ruling reply (author `BV_<bjt>`, fix presets 3/4, commit Phase 2)
**Branch:** `mc-realism` @ `c89aa35`. **Nothing committed this round** — the tree is mid-transition.
**Date:** 2026-09-19
**Status:** AD1 is implemented and the DNMOS20V preset gap is fixed. The generator writes a correct
`.inc` and the whole PDK simulates. But **the generated file is unreadable to the tools that parse
it**, which silently degraded 5 of 40 direction records and makes `--check` unable to ever fail.
That is AE1, and it is a §2 stop.

---

## 1. AD1 — done

`_BV_template.devices` extended to 17. `applies_to` split by where the parameter actually lives:

| entry | devices | why |
|---|---|---|
| `param: bv` | **13** VDMOS | their cards carry a `bv` parameter |
| `target: wrapper_BVCBO` | 4 BJT | their cards carry none; breakdown is `.param BVCBO` in the `.lib` |

The four `.lib` lines are rewritten, TT preserved:

```
.param BVCBO={14*exp(0.0167*Z_BV_NPN_LV)}     (was 14*_isTT + 13.3*_isFF + ... )*(1+P_DBV_NPN_LV)
.param BVCBO={18*exp(0.0167*Z_BV_PNP_LAT)}
.param BVCBO={45*exp(0.0167*Z_BV_NPN_HV)}
.param BVCBO={32*exp(0.0167*Z_BV_PNP_HV)}
```

**Zero** selector or `P_*` references remain anywhere in the authored `.lib`. The generator
declares `Z_BV_<bjt>` for all four (via a new wrapper-target path) and `Z_BV_<vdmos>` for all 13;
every `.lib` reference resolves; no `bv` card line is emitted for the BJTs. The harness records
`BV_*` as excluded with the same reason the VDMOS get.

The whole PDK simulates, BJTs included:

| device | `abs(i)` at case 0 |
|---|---|
| NMOS1V8 / NDMOS200V | 1.083416e-03 / 1.003823e-03 |
| NPN_LV / PNP_LAT | 9.775987e-06 / 6.124744e-06 |
| NPN_HV / PNP_HV | 9.618406e-06 / 4.671346e-06 |

**A mistake worth recording:** I first hand-wrote the 13-device `bv` list and dropped DNMOS20V,
because its name does not match the `[NP]DMOS` shape I was eyeballing. It is now **derived from
the cards** — membership is computed by looking for a `bv` line, not typed out.

## 2. The DNMOS20V preset gap — fixed

Presets 3/4 split the VDMOS by `startswith("N")` / `startswith("P")`. `DNMOS20V` begins with "D", so
it fell into neither and silently vanished from FS/SF. Replaced with explicit `VDMOS_N` / `VDMOS_P`
lists, so a future device whose name starts with something else cannot be misfiled the same way.

| preset | before | after | Δ |
|---|---|---|---|
| 3 / 4 (FS / SF) | 12.8327 | **13.1787** | **+0.3460** |
| groups / variables | 20 / 62 | 21 / 65 | +1 / +3 |

Every other preset is unchanged to four decimals — one added 3σ vector, nothing else touched.

BJT movers, now that they simulate (pre-Phase-2 vs generated):

| device | case 1 | case 2 | case 3 | case 4 |
|---|---|---|---|---|
| NPN_LV | −5.668 | +5.719 | −5.668 | +5.719 |
| PNP_LAT | −5.681 | +5.744 | +5.744 | −5.681 |
| NPN_HV | −5.678 | +5.737 | −5.678 | +5.737 |
| PNP_HV | −5.695 | +5.768 | +5.768 | −5.695 |

`case 0` exact on all four; FS/SF polarity correct per device type.

## 3. AE1 — §2 stop: the generated `.inc` breaks the tools that read it

Two failures, **one root cause**: the generated form is unreadable to code written against the
`_isXX` form.

### 3.1 σ changes cannot propagate; `--check` can never go red

Edited `VTH_NMOS5V0` σ +10 % in a scratch copy. `variable_table` returned the new value
(**0.0181412**). The emitted card line kept the old one:

```
+ vth0={0.88 + 0.016492*Z_VTH_NMOS5V0}
```

The card-line branch fires on `"_isTT" in expr or \bP_[A-Z]`. An already-generated line contains
**neither**, so it is passed through verbatim carrying whatever σ the previous run wrote. The
generator reads the file it overwrites, so after the first write it can no longer see what to
change. B1's "editing a σ turns `--check` red" cannot hold.

### 3.2 Five of forty direction records silently degraded

`measure_stat_directions.tt_of` returns `None` for every generated card line:

| card.param | TT parsed |
|---|---|
| `NMOS5V0.vth0`, `.u0`, `.rdsw` | **None** |
| `NPN_LV.bf`, `.rb` | **None** |
| `DNMOS20V.vto` | **None** |
| `NPN_LV.is` | 2e-16 — a deterministic line the generator never touched |

No TT → no override built → the variable is dropped from the direction **without a record**:

| group | was | now |
|---|---|---|
| NPN_LV / PNP_LAT / NPN_HV / PNP_HV | 3 terms, 26.0 / 31.4 / 25.9 / 32.2 % | **1 term** (`VBE_*` only), 23.2 % |
| DNMOS20V | 3 terms, 9.35 % | **0 terms, 0.00 %** |

A zero-length direction cannot be normalised to 3σ, so `corners.json` would carry a degenerate
DNMOS20V vector.

**I called this wrong once.** I reported the collapse as a measurement-time artifact of the
half-broken tree and predicted it would clear once `.lib` and `.inc` were consistent. I
re-measured against the consistent tree: it did not clear. Same root cause as §3.1, not a separate
problem.

### 3.3 The blast radius is wider than the two files I tested

**Eight files read the `.inc`.** I have verified the parser in **two**. Untested against the
generated form: `make_release.py`, `stat_model_inventory.py`, `char_lib.py`, `exp_lib.py`,
`passives.py`, `run_passives.py`. I am not willing to call Phase 2 landable with six consumers
unverified.

## 4. AE1 — the question

**Which way should this be resolved?**

1. **Generate from a pristine source.** `gen_models` transforms a never-overwritten input rather
   than the file it writes. `HEAD:autohv_bicmos180_case_models.inc` is exactly right as that input
   — it still carries all 183 selectors, and it already contains `k3`/`k3b`/`w0` and the 12 V
   refit, so every non-statistical edit is in it. Makes the transform a pure function of
   (model, pristine input): σ propagates, `--check` works.
2. **Teach every consumer the new form.** One shared TT parser understanding `{TT + σ*Z}` and
   `{TT*exp(σ*Z)}`, used by all eight readers.
3. **Both.**

**My recommendation is 3**, with (1) as a checked-in `autohv_bicmos180_case_models.inc.in` rather
than reaching into git history — an implicit dependency on HEAD is the kind of thing that breaks
silently a year later. (2) is needed regardless, because the directions harness must read
generated cards no matter where generation sources its TT values.

## 5. State, and an offer

The working tree is **mid-transition**: `.inc` generated, `.lib` rewritten to match. Those two are
consistent *for simulation* — every probe device returns a sane current — but not for the
toolchain. Modified: `autohv_bicmos180_case.lib`, `autohv_bicmos180_case_models.inc`,
`docs/corners.md`, `models/corners.json`, `models/stat_model.json`, `tools/build_corners.py`,
`tools/measure_stat_directions.py`; untracked: `tools/gen_models.py`.

**If you would rather the tree were coherent while you decide, say so and I will revert the `.inc`
and `.lib` to HEAD.** The generator, the model edits and the preset fix all survive that; only the
generated output goes.

## 6. What I got wrong this round

| claim / action | what was true |
|---|---|
| hand-wrote the 13-device `bv` scope | dropped DNMOS20V; membership is now derived from the cards |
| "the direction collapse is a measurement-time artifact, it will clear" | it did not clear; same root cause as the σ bug |
| dismissed the self-referential-input concern as an over-reach | it was the actual defect, two turns later |
| `AUTOGEN` banner emitted unconditionally | stacked a second copy on re-run, so `--check` failed after a write |
| two patch scripts died before writing | a heredoc continuation-escape, then a generator expression whose `if` referenced a name its `for` had not yet bound |

The pattern in the last two rows is mine to fix: I keep writing clever one-liners in throwaway
patch scripts. Plain loops, and `Write` instead of nested heredocs.
