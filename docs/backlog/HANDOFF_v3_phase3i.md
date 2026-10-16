# Handoff: Phase 3i — the guard found nothing, then caught my own regression

**Responds to:** the 2026-10-16 ruling (scope the record; differential corner; add the guard)
**Branch:** `mc-realism` @ `e891179`, pushed, tree clean, **eight green** (seven checks + preflight)
**Date:** 2026-10-16
**Status:** Phase 3 ~99 % done. All three ruled items applied. No open questions.
Remaining: B2–B7 scripts and the sizing-guide fringe column, then Phase 4 → Stop B.

---

## 1. §3 — the undeclared-parameter guard

`preflight.py` now fails on any `X` instance passing a parameter its subckt does not declare.

**On the current tree: 3769 instances scanned against 121 subckts from every tracked `.lib`,
0 undeclared.** You asked me to report what it finds, and the honest answer is nothing — the
family migrations were complete.

A guard that has only ever returned zero is not yet a guard, so I verified it against both
failure modes by injection:

| injected | caught |
|---|---|
| stale `MM_SIGMA=3` on an NMOS5V0 instance | ✓ |
| typo'd `Z_VTT=` instead of `Z_VT=` | ✓ |

The typo is the more valuable catch. A misspelled knob name fails in exactly the same silent
way as the original defect, and nothing else in the toolchain would notice.

**Then it immediately caught a regression of my own.** Adding it turned preflight's existing
defaults-equal-minima check red: my generated BJT wrappers hardcoded `AREA=0.04` and lost the
**authored per-device defaults**. PNP_LAT, NPN_HV and PNP_HV are `0.10` — their fabrication
minima — so three wrappers were defaulting *below their own minimum*. The default now comes
from the authored template, the same way the MOS `W`/`L` defaults do.

That is the second time in this phase that running a check immediately after writing it paid
for the check.

## 2. §1 — the scope, in the record, in your words

Written into `MIRROR_CHAR.md` and `CHANGELOG.md`:

| | |
|---|---|
| **invalidated** | runs that set the knob as a top-level `.param` expecting a deterministic ±kσ shift — they measured the **typical device**. The deterministic-corner tables are the casualty. |
| **not invalidated** | `MM_ON=1` runs, where each instance draws its own `AGAUSS`. That path never used the knob, so the MC clouds and σ/µ figures — the 4.33 % included — are live and valid. Their *seeding* claim was separately false, which is reproducibility, not validity. |

## 3. §2 — the differential corner, noted for Phase 7

Recorded in `MIRROR_CHAR.md`: the mirror mismatch corner is **differential** (`+kσ` reference,
`−kσ` output, on `Z_VT` only), the primary result comes from `mc_driver --mode mismatch`, and
the ±3σ pair is a secondary "deterministic worst-case pair" table. Not wired yet — it lands in
Phase 7 where these regenerate anyway, as you scoped it.

## 4. `MM_SIGMA` is retired

No wrapper declares it, no deck passes it, no symbol emits it. `xschem/gen_syms.sh` emits the
per-family knob sets and the 40 symbols are regenerated — **diodes gained their own `DIO_FMT`**,
having no β and having previously shared the BJT format. `check_naming` fails if it returns.

The README now carries a table of knobs per family, which the old single-dial prose could not
express:

| family | knobs |
|---|---|
| BSIM3 MOS | `Z_VT`, `Z_BETA`, `Z_W`, `Z_L` |
| VDMOS / LDMOS | `Z_VT` |
| resistors | `Z_R` |
| capacitors | `Z_C` |
| BJT | `Z_VBE`, `Z_BF` |
| diodes / Zeners | `Z_IS` |

One narrow exemption: `MIRROR_CHAR.md` holds the post-mortem and must name the parameter, so it
is exempt **by path**. README and QUICKSTART tell designers what to *use* and stay guarded —
verified by injecting a mention into README and confirming it still fails.

## 5. What remains in Phase 3

- **acceptance B2–B7** as scripts under `pdk_validation/`, N = 200, seed 0, LHS, with the
  relaxed B6 wording
- the minimum-geometry fringe column in `docs/sizing-guide.md`

Then Phase 4 (`mc_driver`, `corner_sweep`) → **Stop B** → 5, 6, 7 → `v3.0-stats`.

## 6. State

`e891179`, pushed, tree clean. Eight green. Still outstanding and not mine: the stranded
worktree and the six `xschem/designs/*.sch` netlist checks.
