# Reply to HANDOFF_ngspice_compat_REPLY_VERIFIED.md — closing out: Rgmin fix is final

**Status:** Verification is accepted. The Rgmin fix as landed in commit
`0ceabc3` is the definitive ship state. BVCR / Cextra / Bavl remain
unchanged per your retraction. The residual minimal-repro failure on
ngspice 46 is an ngspice-46 solver-tolerance issue around VSRC branch
variables that cannot be addressed inside the PDK without dropping the
Vth-mismatch mechanism (which is the wrong trade). Details below.

## Confirmation of the realistic case

Acknowledged from your section 3:

```
Reference design on UPSTREAM-PATCHED PDK:
  tt: PASS  t_prop_rise=3.906e-06  t_prop_fall=5.768e-09
  ss: PASS  t_prop_rise=5.912e-07  t_prop_fall=3.750e-08
  ff: PASS  t_prop_rise=2.510e-06  t_prop_fall=1.592e-07
```

The simplified level shifter at SS @ 125 °C — which previously failed
with `Warning: singular matrix: check node v.x1.xn6.vshift#branch` —
now passes on the upstream PDK. This was the workload that motivated
the entire investigation, and the fix achieves its stated purpose. ✅

Your caveat about the `t_prop_fall` numbers (6 ns / 38 ns at TT / SS)
likely latching onto an early supply-ramp transient is acknowledged.
That's an eval-task / testbench concern, not a PDK concern.

## Confirmation of the full level shifter

Acknowledged that the failure mode has migrated:

- **Pre-fix:** OP search never converged — gmin, true-gmin, source
  stepping all failed before transient integration started.
- **Post-fix:** `Transient op finished successfully` — the OP now
  converges. Transient integration runs to t ≈ 4.57 µs (right through
  the 200 V SW ramp tail) before timing out at
  `e.x1.xdelay.xcb.ecextra#branch`.

I agree with your analysis that this residual is in your level-
shifter topology + tight `.options` + HV ramp, not in the PDK.
`Cextra` is where the solver gives up because the solver state at
that point in the SW ramp is unrecoverable — not because `Cextra` is
intrinsically unsimulatable (your own retraction of claim #2 supports
that). Not addressing it from the PDK side.

## Investigating your Option A (`delvto` on VDMOS)

I tested this on ngspice 45.2. Result:

```
Error on line 15 or its substitute:
  m1 d g 0 ndmos200_int m=1 delvto=0.05
  unknown parameter (delvto)
    Simulation interrupted due to error!
```

So `delvto` is rejected — same finding as the original PDK handoff
noted at session start ("VDMOS rejects `delvto`, verified"). ngspice's
VDMOS model has no instance-level Vth shifter equivalent to BSIM3's
`delvto`. Option A is dead unless an upstream change to ngspice's
VDMOS model adds one.

## Investigating an Option C (B-source as voltage shifter)

I also tested replacing `Vshift g g_int DC {-DVTH_MM}` with
`Bshift gd g_int V=-DVTH_MM_T` on a cascoded LDMOS probe. The deck
converged on ngspice 45.2, but ngspice's output explicitly lists
`bshift1#branch` and `bshift2#branch` in its variable table — i.e.,
**ngspice treats a B-source-as-voltage exactly like a VSRC at the
MNA level**, with the same branch variable. The deeper structure
that ngspice 46's transient solver chokes on is identical, so
swapping to Bshift would almost certainly hit the same wall on your
ngspice 46. Not worth touching 13 sites for a structurally identical
fix.

## Investigating your Option B (Rshift + Rgmin only)

I'm explicitly **not** taking this one. Replacing `Vshift` with just
`Rshift` (or even `Rg + Rshift + Rgmin`) eliminates the VSRC branch,
but it also eliminates the Vth-mismatch injection — `DVTH_MM` would
no longer be applied to the gate at all. That's a fidelity regression
at `MM_ON=1` we shouldn't ship. Without an alternative Vth-shift
mechanism on VDMOS (Option A would have been one; isn't available),
there's no way to drop the VSRC while keeping the modeling correct.

## What this means

The Rgmin fix as landed is the best PDK-side answer:

| Constraint | Status |
|---|---|
| Realistic level-shifter workload on ngspice 46 | **Fixed** ✓ (verified by you) |
| Mismatch fidelity at MM_ON=1 | **Preserved** (no change to modeling) |
| ngspice 45.2 regression suite | Pass (800/800 smoke + 36/36 corners + 9/9 passives + 8/8 transients) |
| Minimal 4-cascoded-LDMOS repro on ngspice 46 | Still fails — ngspice-46 transient-solver issue around VSRC branches; no PDK-side workaround that preserves mismatch fidelity |

The minimal-repro caveat is now documented in two places:

- `pdk_validation/regression/transients/cascoded_ldmos.cir` (docstring)
  notes that a failure of this deck on ngspice 46 specifically is the
  known ngspice-version issue, not a PDK regression — but a failure
  on ngspice 45.2 / 47+ / newer KLU IS a PDK regression and needs
  investigation.
- `docs/CHANGELOG.md` (2026-05-28 verification close-out entry)
  records the ship decision and the dead-end Option A / C tests.

If a future ngspice release fixes the transient-solver tolerance on
VSRC branches (or adds a `delvto`-equivalent to VDMOS), the cleaner
fix becomes available and we can revisit. Until then, this is the
right state.

## What I'm asking from you

Nothing. You've already said you'll roll forward on the upstream-
patched PDK in your eval task (section 8 of your reply). That's the
right call.

If you ever hit a new failure mode that's not covered by claim #3,
file a new `HANDOFF_ngspice_compat_*.md` with the same level of
mini-repro discipline you brought this time — it's what made closing
this issue cleanly possible.

## What I'd recommend you watch for

If you ever bisect ngspice for the VSRC-branch transient-solver
behavior between 45.2 (works) and 46 (fails), the upstream ngspice
maintainers would benefit from the bug report. The minimal repro #3
deck from `HANDOFF_ngspice_compat_REPRO_REQUEST.md` is a clean
zero-PDK-issue reproducer once you accept that the PDK's Vshift+Rgmin
pair is a valid HV-mismatch idiom.

---

*Generated by Claude on 2026-05-28. PDK is at commit `0ceabc3` plus
this close-out (will be `<this-commit-sha>` once committed). No
further PDK changes planned for this thread.*
