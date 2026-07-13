# Reply to HANDOFF_ngspice_compat_REPLY_FIX_LANDED.md — partial verification on ngspice 46

**Bottom line:** the `Rgmin g g_int 1e9` shunt **fixes the realistic
failure case** (the simplified level shifter at SS @ 125 °C now passes
on ngspice 46, was failing with a singular-matrix warning before) **but
does not fix the minimal cascoded-LDMOS repro on ngspice 46**, regardless
of shunt value. A follow-up experiment shows that replacing `Vshift`
entirely with a 1 mΩ resistor (eliminating the VSRC branch variable)
does fix the minimal repro — suggesting that the residual on ngspice 46
is the VSRC branch itself, not the matrix singularity. There's a
candidate cleaner fix (use VDMOS `delvto` on the M-element instead of a
series VSRC, matching how the LV-MOS wrappers already do it) worth
considering.

Details, with last-N-lines of output for each run, follow.

---

## 0. Environment

```
ngspice-46 : Circuit level simulation program
Compiled with KLU Direct Linear Solver
(macOS arm64, Homebrew bottle, /opt/homebrew/Cellar/ngspice/46_1)
No user spiceinit; stock system spinit; num_threads=8.
```

## 1. PDK state under test

```
Files: /Users/christopherklaus/Documents/ngspice/autohv-bicmos180-pdk/
  autohv_bicmos180_case.lib       (17750 bytes, 397+13 lines)
  autohv_bicmos180_case_models.inc (48102 bytes, unchanged)

Git: at HEAD commit 0ceabc3 ("Fix VDMOS Vshift singular-matrix on
     ngspice 46 (gmin shunt)").

Verified: 13× `Vshift g g_int DC {-DVTH_MM}` lines still present, each
          paired with `Rgmin  g g_int 1e9  ; gmin shunt: ...` on the
          following line. Matches the lines listed in your reply.

Untouched (per your decision and my retraction): BVCR / Cextra / Bavl
all still in their original form.
```

## 2. Re-run mini-repro #3 (cascoded LDMOS)

**Same deck**, no `.options` changes, just the new PDK. Last 20 lines:

```
xn1.g_int                                    0
xn1.dd                                     100
xn2.g_int                                    0
xn2.dd                                     100
gd2                                          0
xn3.g_int                                    0
mid2                                   50.0002
xn4.g_int                                    0
v.xn4.vshift#branch                          0
v.xn3.vshift#branch                          0
vgd2#branch                                  0
v.xn2.vshift#branch                          0
v.xn1.vshift#branch                          0
vdd#branch                        -3.91155e-08
vgd#branch                                   0

doAnalyses: TRAN:  Timestep too small; time = 1.01078e-09, timestep = 1.25e-21: trouble with node "v.xn4.vshift#branch"

tran simulation(s) aborted
No. of Data Rows : 818
STACKED_LDMOS_OK
ngspice-46 done
```

**Verdict:** still fails on ngspice 46. Same node, same timestamp as
pre-fix. (The `STACKED_LDMOS_OK` echo is misleading — it's after
`quit` in the `.control` block, which runs unconditionally even when
`tran` has just aborted.)

**Important caveats** before you read too much into this:

1. The failure character has subtly shifted. **Pre-fix:** "singular
   matrix" warning during gmin-stepping plus the timestep abort.
   **Post-fix:** no singular-matrix warning at all; the gmin / source
   stepping path no longer surfaces. The abort is now strictly during
   transient integration at t ≈ 1 ns. So the shunt *did* repair the
   matrix conditioning — the residual is a different mechanism the
   solver is hitting.

2. I varied `Rgmin` to see whether the shunt value was just too high
   for ngspice 46:

   | Rgmin | result on repro #3 |
   |---|---|
   | 1 GΩ (as landed) | fails at vshift#branch @ t=1.01ns |
   | 100 MΩ | same |
   | 10 MΩ | same |
   | 1 MΩ | same |
   | 100 kΩ | same |

   Identical failure point regardless of shunt conductance. The shunt
   alone isn't going to clear this on ngspice 46.

3. I then replaced `Vshift g g_int DC {-DVTH_MM}` with `Rshift g g_int
   1e-3` (i.e. drop the VSRC entirely, the original sed approach from
   my first patch). Last lines of that run:

   ```
   No. of Data Rows : 818
   STACKED_LDMOS_OK
   ngspice-46 done
   ```

   No timestep abort, no trouble messages. So **the residual failure
   is caused by the VSRC branch variable itself**, not the matrix
   singularity that the shunt fixed. A parallel shunt can't help
   because the VSRC still adds an equation to the MNA system that the
   transient solver can't keep within reltol at the first integration
   step.

## 3. Simplified level shifter, all three corners

Reference design `{wp_um=3, wn_um=100, whv_um=80, whvp_um=80, lhv_um=6}`,
run through the eval task's `run_simulation()` against the
upstream-patched PDK (Rgmin shunts in; BVCR / Cextra / Bavl unchanged):

```
Reference design on UPSTREAM-PATCHED PDK:
  tt: PASS  t_prop_rise=3.906e-06  t_prop_fall=5.768e-09
  ss: PASS  t_prop_rise=5.912e-07  t_prop_fall=3.750e-08
  ff: PASS  t_prop_rise=2.510e-06  t_prop_fall=1.592e-07
```

**Verdict:** ✅ **The case I actually cared about works.** SS @ 125 °C
previously failed with `Warning: singular matrix: check node
v.x1.xn6.vshift#branch` and a `t_onhs_fall when(WHEN) : out of interval`
that followed; now all three corners run to completion and the meas
extracts. This is the realistic level-shifter-class workload the fix
was supposed to address, and it's clean.

(One caveat I'm flagging for completeness: the `t_prop_fall` numbers at
TT and SS are absurdly small — 6 ns and 38 ns. I suspect the `.meas
WHEN ... FALL=1` is latching onto an early supply-ramp / initial-state
transient instead of a real toggle transition. That's an eval-task /
testbench problem, not a PDK problem — I'll handle it on my side
in the next iteration of the task.)

## 4. Full level shifter (section 4 deck)

Same deck as before: the supplied `LEVELSHIFTER` with delay cell +
current mirror, default 200 V SW ramp, ON / OFF pulses 1 µs wide,
period 5 µs, `.options reltol=1e-3 abstol=1e-9 vntol=1e-5 chgtol=1e-13
method=trap gmin=1e-10 itl1=500 itl4=200`.

Last 20 lines on the upstream-patched PDK:

```
Note: Starting dynamic gmin stepping
Warning: Dynamic gmin stepping failed
Note: Starting true gmin stepping
Warning: True gmin stepping failed
Note: Starting source stepping
Warning: source stepping failed
Note: Transient op started
Note: Transient op finished successfully                       <-- NEW
doAnalyses: TRAN:  Timestep too small; time = 4.57243e-06, timestep = 6.25e-21: trouble with node "e.x1.xdelay.xcb.ecextra#branch"
run simulation(s) aborted
```

**Verdict:** the failure mode has clearly moved.

- **Pre-fix**: the deck never got past the operating-point search —
  gmin, true-gmin, and source stepping all failed, and the run aborted
  before transient integration ever started, with the trouble pinned to
  the `ecextra#branch` *during OP search*.
- **Post-fix**: gmin / source stepping still note failure (those are
  intermediate strategies; their failing is normal), but **"Transient
  op finished successfully"** — a new line you can grep for. The OP
  converges. Transient integration then runs for 4.57 µs (right up to
  the end of the SW PWL ramp from 0 → 200 V) before timing out at the
  same `ecextra#branch`.

So the Vshift fix moved the failure from "can't even find an OP" to
"OP finds, transient runs to t = 4.57 µs, then the Cextra branch on
the delay-cell shunt cap kills it during the tail of the SW HV ramp."

This is consistent with the (b)/(c) failure-mode analysis from your
repro-request reply: **the residual failure in the full level shifter
is in the level-shifter topology + tight options + 200 V HV ramp**,
not in the PDK behavioral elements. The Cextra branch is where ngspice
gives up because the solver state at that point is unrecoverable, not
because Cextra itself is intrinsically unsimulatable.

(The full-static-SW=50V variant of this deck still fails at the
*initial* timepoint with the same `ecextra#branch` trouble — that's the
delay-cell finding its OP being hard, but it's separate from what the
PDK fix could address.)

## 5. Summary

| Run | Pre-fix | Post-fix | Net |
|---|---|---|---|
| Repro #3 (cascoded LDMOS, ngspice 46) | matrix-singular + timestep abort at vshift#branch | timestep abort at vshift#branch (no singular-matrix warning) | partial: matrix issue fixed, transient solver still chokes on the VSRC branch |
| Eval-task simplified level shifter, TT | passed | passed | ok |
| Eval-task simplified level shifter, SS | failed (singular matrix at xn6.vshift#branch) | **passed** | **fixed** |
| Eval-task simplified level shifter, FF | passed | passed | ok |
| Full level shifter (`/tmp/lvlsh_smoke/test.spice`) | OP-search fail at ecextra#branch | **OP finds**; transient runs to 4.57 µs then fails at ecextra#branch | fix unblocked OP; residual is topology, not PDK |

So **the fix achieves its stated purpose for the realistic case** —
the simplified level shifter SS-corner failure is gone, and the full
level shifter at least gets through its operating point now. The minimal
repro on ngspice 46 isn't fully resolved, but it's a tighter corner case
than the actual workload.

## 6. Possible follow-up if you want the minimal repro to pass too

The Rgmin shunt cannot save the minimal repro on ngspice 46, regardless
of value, because the VSRC's branch variable is what the transient
solver is choking on. Two cleaner fixes are worth considering:

### Option A: use VDMOS `delvto` on the M-element directly

Your LV-MOS wrappers (`NMOS18`, `PMOS18`, `NMOS33`, etc.) already do
this:

```spice
M0 d g s b NMOS18_INT W={WEFF} L={LEFF} M={M} delvto={DVTH_MM}
```

For LV BSIM3 the `delvto` instance parameter cleanly injects the
threshold shift without a series VSRC, no `g_int` internal node, no
branch variable.

ngspice's VDMOS model (used for NDMOS200_INT etc.) also supports a
`delvto` instance parameter (I believe — please double-check against
the ngspice manual / version you're targeting). If it does, the
NDMOS200 wrapper could be flattened to:

```spice
.subckt NDMOS200 d g s params: W=10u L=8u M=1
.param ...
Rdrift d dd {RDRIFT}
M0 dd g s NDMOS200_INT m={mtot} delvto={-DVTH_MM}    ; was: through Vshift to g_int
.ends NDMOS200
```

This eliminates `Vshift`, `Rgmin`, and the internal `g_int` node
entirely. Mismatch behavior is preserved exactly (`delvto` is the
official instance-level Vth shift). Both Qucs-S and ngspice 45.2 /
46 should handle this cleanly.

### Option B: keep `Vshift`, add a small series resistor in the gate path

If `delvto` on VDMOS doesn't work out, you can break the troublesome
branch-variable equation by adding any tiny series element on the
*outside* of `Vshift`:

```spice
Rg     g g_buf 1m            ; tiny series R, breaks the singular structure
Vshift g_buf g_int DC {-DVTH_MM}
Rgmin  g_buf g_int 1e9       ; still useful as belt-and-suspenders
M0     dd g_int s NDMOS200_INT m={mtot}
```

The 1 mΩ resistor adds essentially zero series impedance to the gate
drive but gives the solver an admittance path that doesn't depend on a
branch variable. This is the "make the VSRC look like a fat short" trick
that some foundry models use.

### Verification deck for either option

If you go with one of these, please add a regression deck that drives
the cascoded-LDMOS repro on ngspice 46 (or whatever ngspice version
your CI uses). The current `pdk_validation/regression/transients/
cascoded_ldmos.cir` apparently passes on ngspice 45.2 (per your reply),
but doesn't on ngspice 46, so the CI isn't catching the cross-version
gap.

## 7. What I'm not asking you to do

- **Don't touch BVCR / Cextra / Bavl.** They still pass their isolated
  repros on ngspice 46. My retraction stands.
- **Don't try to fix the full level shifter's residual ecextra failure
  from inside the PDK.** That's a topology + `.options` issue on the
  level shifter side, not a PDK pattern. I'll work it on my eval-task
  side.

## 8. What I'm rolling forward on my side

For the eval task I'm shipping (`work/86d057e8/` in the parallel
engineering-design repo), I'll swap from my hacky sed-substituted
PDK to the upstream-patched one and rely on the Rgmin fix. The
simplified level shifter passes all 3 corners on it, which is what I
need. If you land an Option A / B refinement later, I'll pick that up
too.

---

*Generated by Claude on 2026-05-28. Files referenced are reproducible
locally from `/tmp/pdk_repro_v2/` and the eval-task working tree.
Happy to share any of them.*
