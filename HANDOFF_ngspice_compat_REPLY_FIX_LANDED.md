# Reply to HANDOFF_ngspice_compat_REPRO_RESULTS.md — fix landed; please verify on ngspice 46

**Status:** Targeted fix for claim #3 (Vshift singular matrix) is in
the PDK. BVCR / Cextra / Bavl untouched. Awaiting your confirmation
that this resolves the cascoded-LDMOS failure on your ngspice 46.

## What changed

### The lib

Added a 1 GΩ gmin shunt in parallel with each of the 13 VDMOS subckts'
`Vshift` source:

```spice
* before
Vshift g g_int DC {-DVTH_MM}
M0 d g_int s NDMOS200_INT m={mtot}

* after
Vshift g g_int DC {-DVTH_MM}
Rgmin  g g_int 1e9   ; gmin shunt: breaks the singular matrix when MM_ON=0 ...
M0 d g_int s NDMOS200_INT m={mtot}
```

Applied to all 13: `NDMOS20`, `NDMOS40`, `NDMOS60`, `NDMOS80`,
`NDMOS120`, `NDMOS200`, `PDMOS20`, `PDMOS40`, `PDMOS60`, `PDMOS80`,
`PDMOS120`, `PDMOS200`, `DNMOS20`.

The mechanism: when `MM_ON=0`, `Vshift` is a 0 V VSRC and KCL at the
shared external gate becomes 0=0 (dependent equation) ⇒ singular
matrix. The 1 GΩ shunt adds an independent conductance between the
two nodes so KCL has a non-trivial equation regardless of `Vshift`'s
value. 1 GΩ leaks **~1 pA per mV** of `DVTH_MM` — 4 to 6 orders of
magnitude below any real mismatch sigma, so circuit behavior at
`MM_ON=1` is unchanged within solver precision.

This is the foundry-standard idiom for HV mismatch-shift wrappers.

### The regression suite

A new `pdk_validation/regression/transients/cascoded_ldmos.cir` deck
encodes the exact failure pattern: two `NDMOS200` + two `NDMOS120`
with their gates tied to the same drive line, `MM_ON=0`. Runs at
`case=0` in 84 ms on ngspice 45.2. This catches the regression
class on every CI run going forward. **You were right that the suite
was missing this pattern** — the existing smoke + transients only
exercised single VDMOS devices.

## What did NOT change

Per your retraction in `HANDOFF_ngspice_compat_REPRO_RESULTS.md`,
the following are **untouched**:

- `BVCR mid n V={V(p,mid)*(VCR1*sqrt(...)+VCR2*V*V)}` in the 5 R subckts
- `Cextra p n C={C0NOM*(VCC1*sqrt(...)+VCC2*V*V)}` in the 4 C subckts
- `Bavl ci b I={abs(i(Vsen))*(1/(1-...**4)-1)}` in the 4 BJT subckts

These pass your mini-repros 1, 2, and 4 on ngspice 46 and pass the
regression suite on ngspice 45.2. Leaving them alone preserves the
high-fidelity VCR/VCC and BJT-avalanche modeling.

## What I'd like you to verify

If you can, on your **ngspice 46 / macOS arm64** environment, please
re-run:

### 1. Mini-repro #3 (cascoded LDMOS)

Same deck as before. Pull the latest PDK and re-run. Expected:
`STACKED_LDMOS_OK` reached, no `Timestep too small`, no
`singular matrix` warning.

### 2. Your simplified level shifter at SS @ 125 °C

The case that previously failed with
`Warning: singular matrix: check node v.x1.xn6.vshift#branch`.
Expected: converges without that warning. (The deck's other
non-convergence problems under tight `.options` — which you traced
to the level-shifter topology, not the PDK — are still a separate
matter and not addressed here.)

### 3. The full failing level shifter from section 4 of your reply

Realistically this will still fail because, as you documented, the
patches were "correlated, not causal" — the topology + tight
`.options` is the deeper issue. But it's worth confirming that the
**failure mode** has moved (i.e., it no longer fails at a
`v.x.vshift#branch` node). If it now fails at a `Cextra` or `BVCR`
node, that would be new information; if it fails at `voff#branch`
or a similar non-PDK node, that's confirmation the PDK side is done
and the rest is on the level-shifter / `.options` side.

## What to send back

Just paste the `last 20 lines` of ngspice output from each of those
runs + the version banner (in case it shifted), into a new
`HANDOFF_ngspice_compat_REPLY_VERIFIED.md` next to this file. I'll
fold the resolution into the CHANGELOG and close the loop.

If anything is unexpected — e.g. the gmin shunt is too small for
ngspice 46's solver, or some other node becomes the bottleneck —
include that diagnosis and I'll iterate.

## Why not the global `NGSPICE_COMPAT` switch

Two reasons:

1. **Three of the four claims it gates were retracted.** Gating
   patterns that work fine in both ngspice 45.2 and ngspice 46
   would unconditionally drop fidelity for zero benefit.
2. **The remaining real issue (Vshift) is a topology-induced
   matrix singularity, not a behavioral-expression incompatibility.**
   The right fix at the matrix level (gmin shunt) is narrower and
   keeps the original modeling exact.

If a future ngspice version breaks BVCR / Cextra / Bavl for real,
the same evidence-based pattern applies: a targeted fix for the
specific instance and a regression deck to catch the class going
forward. The global switch remains available as a fallback if a
PDK-wide ngspice break ever shows up.

## Where to look

| Path | Purpose |
|---|---|
| `autohv_bicmos180_case.lib` lines 98, 106, 114, 122, 130, 138, 146, 154, 162, 170, 178, 189, 197 | The 13 `Rgmin  g g_int 1e9` shunts (one per VDMOS subckt; line numbers approximate) |
| `pdk_validation/regression/transients/cascoded_ldmos.cir` | The new regression deck |
| `pdk_validation/regression/run_transients.py` | Phase D registry, now 8 entries |
| `docs/CHANGELOG.md` | Entry under `### 2026-05-28 — Fix VDMOS Vshift singular-matrix` |

---

*Generated by Claude on 2026-05-28. PDK is at commit
`<filled-in-after-commit>` once this lands; before that, the diff
against `0d16789` is just `.lib` + `run_transients.py` +
`transients/cascoded_ldmos.cir` + `docs/CHANGELOG.md` + this file.*
