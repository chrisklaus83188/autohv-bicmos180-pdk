# Handoff: history rewritten and force-pushed; device rename landed

**Responds to:** the history-rewrite / device-rename ruling (Chris, 2026-09-20)
**Branch:** `mc-realism` @ `4a15035`, pushed. All four branches rewritten and pushed.
**Date:** 2026-09-20
**Status:** Both packages done. **Everyone must re-clone.** Two things need Chris.

---

## 1. The blast radius was wider than "13 commits on mc-realism"

Step 1 of the ruling asked which branches were affected. The answer changed the job:

| commits | reachable from |
|---|---|
| 10 of 13 | `mc-realism` only |
| **3 of 13** (`88f1f3b`, `fb92e09`, `11fb404`) | **`main`, `delay-pulse-cells`, `transmission-gates` and `mc-realism`** |

So every branch's SHAs changed from those commits onward, and **4 of 5 tags moved**
(`v0` predates them). `git filter-repo` was not installed; installed via pip and run as
`python -m git_filter_repo`.

**Backups.** Branch backups on all four, plus a verified bundle **kept** at
`../autohv-bicmos180-pdk-PRE-REWRITE-2026-09-20.bundle` (3.5 MB, "records a complete
history"). Backup branches deleted only after the fresh-clone verification below.

**The rewrite touched messages and nothing else**, and that is checked, not asserted:

| check | result |
|---|---|
| commits before / after | 157 / 157 |
| **tree hash at each branch tip, old vs new** | **IDENTICAL on all four** |
| message occurrences | 25 → 0 |

An identical tree hash is the strongest available statement that not one byte of file
content moved.

**Verification from a clean clone of the pushed remote**, across every branch: 0 hits in
tracked files, 0 in paths, 0 in 3999 lines of commit messages.

`check_naming.py --stdin` was added for this and kept, as ruled — it is the CI check on
messages from now on (`git log --format=%B <range> | tools/check_naming.py --stdin`).

### A gap the ruling did not anticipate, and I fixed

The file-level naming pass had landed on **`mc-realism` only**. `main`,
`delay-pulse-cells` and `transmission-gates` still carried **14 occurrences in 5 files each,
including the filename** `docs/anchor-amendments-<ref>.md`. Cleaning only the messages would
have left the names sitting in `main`'s files — the opposite of "nothing left behind". The
pass is now applied and committed on all four branches.

The stale `CHANGELOG.md` pointer is reworded to "grounding notes held locally", no filename,
on every branch.

## 2. Device rename

`models/device_rename_map.json` is the single source of truth. **14027 occurrences across
1326 files, and 1026 file renames**, in one pass.

The tool needed two properties, and neither comes free:

- **Underscore is a word character**, so `\bNMOS18\b` does *not* match `NMOS18_INT`. A
  word-boundary rule would have silently left every composite behind — `VTH_NMOS18`,
  `Z_VTH_NMOS18`, `c_NMOS18`, `KP_NDMOS20_STAT`, `TC_KP_NDMOS20`. The rule is
  `(?<![A-Za-z0-9])<old>(?![A-Za-z0-9])`, which treats `_` as a separator while still
  refusing to match `NDMOS20` inside `NDMOS200`.
- **One simultaneous pass**, never sequential — rewriting `NDMOS20` then `NDMOS200` over the
  same text can double-apply.

### No number moved — checked three ways

| check | result |
|---|---|
| `corners.json` regenerated from renamed inputs vs text-renamed file | **0 structural, 0 numeric differences** |
| regenerated `.inc` vs text-renamed `.inc` | identical multiset of lines (only `c_<GROUP>` order differs) |
| **40 × case 0–16 table from before the rename, map applied, vs measured after** | **byte-identical** |
| `sizing-guide.{json,md}` regenerated vs text-renamed | identical |

Six checks green: `inc_parse`, `check_naming`, `gen_models`, `expected_terms`,
`build_corners`, `stat_model_inventory`.

### The guard earned its place immediately

`check_naming.py` now reads the map and fails on any retired name in a tracked path or file.
It **caught 26 real misses on its first run**: I had excluded all of `xschem/autohv/` as
"generated", but only the `.sym` files there are — `README.md` and `examples/*.sch` are
hand-authored and had been silently skipped. Exclusion narrowed to `xschem/autohv/*.sym`.

Two exemptions, both principled rather than convenient:

- **Frozen baselines** keep the old names (2878 occurrences). A baseline you are willing to
  rewrite cannot tell you that something moved. `pdk_validation/baselines/README.md` now says
  so and shows the three lines that apply the map when reading them.
- **`docs/CHANGELOG.md`** is exempt from the *retired-device* scan only — recording what a
  thing used to be called is a changelog's job. The reference-process rule still applies to
  it, verified by injecting one and confirming it is still caught.

### Symbols

`xschem/autohv/*.sym` regenerated from `xschem/gen_syms.sh` after renaming the generator,
with the 23 stale symbols deleted: 40 symbols, every renamed device has one, none missing.
`qucs-s_symbols/` has **no** generator (`make_release.py` only packages it), so those 40 are
static sources and were renamed as files.

## 3. Two things for Chris

**1. Every clone and worktree must be re-cloned or reset.** All four branches and four tags
were force-pushed; any local copy is now on abandoned history.

**The other worktree is the live case.** `…/autohv-bicmos180-pdk` is on `transmission-gates`
with **31 modified files** under `circuits/transmission_gates/` — uncommitted work, possibly
another session's. I did not touch it, and git itself refused my one attempt to move that
branch ("cannot force update the branch 'transmission-gates' used by worktree at …"), which
is the behaviour I wanted. **Those 31 files are safe on disk**, but that worktree's branch
points at history that no longer exists on the remote. It needs the work committed or copied
out *before* any reset or re-clone.

**2. `xschem/designs/*.sch` are renamed but NOT netlist-verified.** xschem is not on PATH
here. What I could check, I did: every PDK symbol reference in all six schematics resolves to
a file that exists, including the renamed `NMOS5V0`, `NDMOS200V`, `PDMOS200V`. The
unresolved references are xschem's own built-ins (`ipin`, `iopin`, `opin`, `lab_wire`,
`noconn`), which live in its installation library. Files to open and confirm:
`CP_PowerFETs.sch`, `CP_PowerStage.sch`, `CP_VoltageMonitor.sch`, `LevelShifter.sch`,
`LevelShifter_DelayBlock.sch`, `resistor_string.sch`.

## 4. One judgement call to flag

The rename also rewrote device names inside **historical handoff documents** — a Stop A′
record now reads `DZ_24V` where the measurement was taken under `DZ_24`. It is the same
device and "nothing left behind" argued for it, but it does edit the record. Say if you would
rather `docs/backlog/` had been frozen like the baselines.

## 5. State

`4a15035` on `mc-realism`, tree clean, pushed. Remote verified from a clean clone: no
reference name, no retired device name, taxonomy-prefixed sources, clean history.

Phase 3 is next: wrappers (`M/NF/NS`, perimeter caps, contact heads, `A_BETA`, gate R, edge
bias, the MOS/BJT/diode knobs), the Zener bench and `BV_DZ_*`, then re-measure and rebuild.
Stop B after Phase 4.
