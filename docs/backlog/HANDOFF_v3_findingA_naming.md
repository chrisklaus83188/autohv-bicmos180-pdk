# Handoff: Finding A landed; the naming pass is done and enforced

**Responds to:** the Findings A/B ruling (`n` per device in both tools; `BV_DZ_*` to Phase 3; §5 kept)
**Branch:** `mc-realism` @ `3aa48eb` (`174dae8` Finding A, `3aa48eb` naming pass)
**Date:** 2026-09-20
**Status:** Both done. Six checks green. One item is explicitly **Chris's call**, not mine or
yours: 13 commit messages name the reference, and rewriting history is a §2 stop.

---

## 1. Finding A — `n` in both tools, and the ruling's premise was slightly wrong

Applied `scale = 1/(n·V_T)` in `measure_stat_directions` and the folded coefficient in
`gen_models`, in **one commit**, `n` read from the card via `inc_parse`. Re-measured all 40
directions and rebuilt.

**The ruling expected BJT `nf` = 1 throughout. Reading rather than typing found otherwise:**
`PNP_LAT` carries `nf` = 1.02 and `PNP_HV` `nf` = 1.03, so both PNPs moved too. Only the two
NPNs are `nf` = 1 — and they came back **bit-identical**, which is the evidence the change
touched nothing it should not.

The narrowing is exactly `1/n` on the `VF`/`VBE`-dominated part of each swing:

| device | `n` | 3σ swing before | after | relative | `1/n` predicts |
|---|---|---|---|---|---|
| DIO_FAST | 1.03 | 30.89 % | 29.99 % | −2.9 % | −2.91 % |
| DIO_PN | 1.05 | 30.85 % | 29.38 % | −4.8 % | −4.76 % |
| DIO_SCH | 1.08 | 30.93 % | 28.64 % | −7.4 % | −7.41 % |
| DZ_5V6 | 1.15 | 30.80 % | 26.78 % | −13.0 % | −13.04 % |
| DZ_12 | 1.18 | 30.73 % | 26.04 % | −15.3 % | −15.25 % |
| DZ_24 | 1.22 | 30.64 % | 25.12 % | **−18.0 %** | −18.03 % |
| PNP_LAT | 1.02 | 31.37 % | 31.03 % | −1.1 % | diluted, 3 terms |
| PNP_HV | 1.03 | 32.22 % | 31.74 % | −1.5 % | diluted, 3 terms |
| NPN_LV | 1.00 | 26.04 % | 26.04 % | 0.0 % | — |
| NPN_HV | 1.00 | 25.92 % | 25.92 % | 0.0 % | — |

MOS, VDMOS, resistors and capacitors are untouched — none carries an emission coefficient. The
case table still reports no group flat on a preset it belongs to.
`docs/case-table-q1-before-after.md` now shows **all three states** (`b1d333d` → Q1 → Finding A)
so the two effects stay separable.

Recorded per the ruling: `stat-model.md` states that σ_VBE/σ_VF are 27 °C, `n`-inclusive voltage
quotes of an `is`-type variable, and why freezing `V_T` is correct rather than a compromise.

## 2. The naming pass — 104 occurrences, now zero, and guarded

The constraint was being violated **104 times across 18 tracked files**, plus one filename.

| class | occurrences | disposition |
|---|---|---|
| A. `models/stat_model.json` provenance fields and notes | 18 lines | rewritten; taxonomy below |
| B. live documentation (5 files) | 22 lines | rewritten; `docs/anchor-amendments-<ref>.md` renamed to `anchor-amendments-reference.md` |
| C. historical handoffs (11 files) | 50 lines | **redacted in place, not deleted** |
| D. `.gitignore` comment | 1 line | rewritten |

On class C I made a judgement call: the prose is ours and the substance is the program record,
so only the name had to go. Deleting them would have cost the history; leaving them would have
kept the violation. Say if you would rather they were removed entirely.

**The pass changed 40 values in `stat_model.json` and not one of them is a number** — verified
by structural diff against HEAD, 0 numeric differences. That was the property I most wanted to
be able to state.

### The provenance taxonomy

Free text is *how the name got in*: `<vendor>:beta-class-band` is a name wearing a provenance
label. Every `source` now starts with one of eight prefixes — `measured`, `derived`,
`autohv-derived`, `literature`, `reference-class`, `declared`, `carried-over`, `default`.

`reference-class` is the load-bearing one. It records that a value was anchored on a comparable
commercial class, while the magnitude stays in a gitignored `LOCAL_*` file and only the boolean
band check reaches the repo. The prefix tells a reader the one thing they need — *how much
should I trust this number* — without identifying whose data it was checked against.

### The guard

`tools/check_naming.py --check` enforces both rules: no forbidden name in any tracked path or
file, and every `source` taxonomy-prefixed. **Verified by injecting each violation class** — a
name in a tracked doc, and a free-text source — and confirming both are caught.

It exempts exactly one file, its own, which must spell the names to express the rule. I made
that exemption explicit rather than leave it to luck: the guard currently passes on itself only
because the regex escapes happen to break the match (`\bonsemi\b` puts a word character before
the name), which a differently spelled pattern would silently undo.

## 3. For Chris, not for either of us

**13 of 154 commit messages name the reference; 25 occurrences.** Rewriting git history is a §2
stop and I did not attempt it. The commits, oldest last:

```
34fba9f 8b0144d 7d5a6d5 5591dcb cc506cc 73b659b ad6032b
9d55c13 d21c0da 23e6a01 88f1f3b fb92e09 11fb404
```

Options, for Chris to choose: leave them (the working tree is clean and a reader browsing files
sees nothing); rewrite the messages with `filter-branch`/`filter-repo`, which changes every SHA
from the oldest hit onward and breaks any reference to them; or squash the affected range. If
this repo is ever published, only the second and third actually remove the name.

**Also for Chris:** `docs/CHANGELOG.md` points at a local file that does not exist on disk —
now `LOCAL_reference_extraction.md`, previously the same name with the reference in it. The
pointer was already stale before this pass; my rename carried it forward rather than fixing it,
because I do not know whether the file was renamed, folded into
`LOCAL_HANDOFF_v3_<ref>_methodology.md`, or deleted. The `LOCAL_*` files on disk keep their
original names, which is correct — that is where reference material is supposed to live.

## 4. Finding B — not started, as scoped

`BV_DZ_*` at 5 % 3σ lognormal, the reverse-bias Zener bench (metric `ln V_z`, terms `BV`
dominant and `RS`, `VF` excluded with a reason), diodes getting `BV_*` excluded like the VDMOS,
and the three case-table acceptance rows. Queued as the first Phase 3 item per your §2.

## 5. State

`3aa48eb` on `mc-realism`, tree clean. Six checks green: `inc_parse`, `check_naming`,
`gen_models`, `expected_terms`, `build_corners`, `stat_model_inventory`.

New this round: `tools/check_naming.py`, `LOCAL_naming_inventory.md` (gitignored, carries the
full 104-line detail). Phase 3 is next.
