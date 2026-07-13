# Reply to HANDOFF_ngspice_compat_REPRO_REQUEST.md — repro results

**Bottom line:** you were right to push back. **Only one of my four claims
reproduces standalone on my ngspice** (Vshift / claim #3); the other three
do not reproduce in your minimal decks. My original handoff overstated
the case. A targeted fix to Vshift, *not* a global `NGSPICE_COMPAT`
switch, looks like the right scope. See section 4 for what that probably
implies for action.

---

## 1. My environment

```
ngspice -v output:
  ngspice-46 : Circuit level simulation program
  Compiled with KLU Direct Linear Solver

OS:
  Darwin Christophers-MacBook-Pro.local 23.6.0  arm64
  (macOS Sonoma 14.x equivalent on Apple Silicon)

Build:
  Homebrew bottle, /opt/homebrew/Cellar/ngspice/46_1
  (`brew info ngspice` confirms stable 46, poured 2026-05-03)

spiceinit:
  No ~/.spiceinit
  No ~/spinit
  System spinit at /opt/homebrew/Cellar/ngspice/46_1/share/ngspice/scripts/spinit
    is the stock Homebrew file -- the only non-default knob is
    `set num_threads=8`; everything else (gmin, gminsteps, reltol,
    abstol, method, compatmode, ...) is the ngspice 46 default.
```

So the version mismatch is **ngspice 46 (macOS arm64) vs. your
ngspice 45.2 (Windows)** — that's the largest controlled-variable
difference and is worth keeping in mind for everything below.

## 2. PDK state I tested against

```
Files under test:
  /Users/christopherklaus/Documents/ngspice/autohv-bicmos180-pdk/
    autohv_bicmos180_case.lib       (16346 bytes, 397 lines, BVCR/Cextra/Vshift instances all present)
    autohv_bicmos180_case_models.inc (48102 bytes, 1444 lines)
```

Both files are the unmodified PDK as I received them — I did not have
git access on the source PDK checkout to give you a SHA. If you need
to match exactly, the lib still contains:

- 5 unpatched `BVCR mid n V={...}` lines (RPOLY_HI/LO, RNWELL, RNPLUS, RPPLUS)
- 4 unpatched `Cextra p n C={...}` lines (CMIM_STD, CMIM_HI, CMOM, CFRINGE)
- 13 unpatched `Vshift g g_int DC {-DVTH_MM}` lines (all VDMOS subckts)
- 4 unpatched `Bavl ci b I={...}` lines (4 BJT subckts)

## 3. Mini-repro results on my ngspice 46

I ran your four mini-repros verbatim against the unpatched PDK. Files
saved at `/tmp/pdk_repro/repro_{1..4}_*.cir`.

| # | What it tests | Result on my ngspice 46 | Last 5 lines |
|:-:|---------------|-------------------------|--------------|
| **1** | Resistor BVCR (RNWELL, 1 MHz sine through V(p,n)=0) | **PASS** — `R_VCR_OK` reached. 508 data rows. | `No. of Data Rows : 508` / `R_VCR_OK` / `ngspice-46 done` |
| **2** | Capacitor Cextra (CMIM_HI, 1 MHz sine through V(p,n)=0) | **PASS** — `C_VCC_OK` reached. 508 data rows. | `No. of Data Rows : 508` / `C_VCC_OK` / `ngspice-46 done` |
| **3** | Stacked NDMOS200 / NDMOS120 with shared gate, MM_ON=0 | **FAIL** — `Timestep too small; time = 1.01078e-09, timestep = 1.25e-21: trouble with node "v.xn4.vshift#branch"`. 818 data rows then `tran simulation(s) aborted`. | `doAnalyses: TRAN:  Timestep too small; time = 1.01078e-09 ... trouble with node "v.xn4.vshift#branch"` / `tran simulation(s) aborted` |
| **4** | BJT BVCBO ramp through breakdown (NPN_LV, 0→17 V over 1 µs) | **PASS** — `BJT_AVALANCHE_OK` reached. 251 data rows. | `No. of Data Rows : 251` / `BJT_AVALANCHE_OK` / `ngspice-46 done` |

So your call was right on three out of four. The categorical language
in `HANDOFF_ngspice_compat.md` was unjustified for #1, #2, and #4.

The Vshift singular matrix problem (claim #3) **does** reproduce
standalone on my ngspice. Even just two cascoded NDMOS200 with their
gates tied to the same drive line, MM_ON=0, no other devices, triggers
`Timestep too small ... trouble with node "v.xn4.vshift#branch"` at
t ≈ 1 ns. So this one is a genuine PDK-side issue that warrants the fix.

## 4. The deck that actually failed me + its full output

This was the level-shifter smoke deck that triggered the original
debugging path. It uses the supplied
`circuits/hv_charge_pump/hv_up_lvlsh/levelshifter.spice` topology
(cross-coupled PMOS latch + HV cascodes + current mirrors + delay cell
+ output buffers) — the **full** reference design, not the simplified
variant I ended up shipping for the eval task.

```spice
* Smoke-test level shifter
.include "autohv_bicmos180_case.lib"
.param case=0 PROC_ON=0 MM_ON=0

.param wp=20u wn=10u llv=1u whv=40u lhv=8u whvp=40u
.param rl=100u rw=2u rdl=100u rdw=2u cdl=20u cdw=20u

.include "inv.spice"
.include "buffer.spice"
.include "delay_cell.spice"
.include "levelshifter.spice"

.param VHV=200 VBOOT=12 VDDL=5

Vvdd  VDD  0 {VDDL}
Vsw   SW   0 PWL(0 0  2u 0  4u {VHV}  20u {VHV})
Vboot BOOT SW {VBOOT}
Von   ON   0 PULSE(0 {VDDL} 6u 10n 10n 1u 5u)
Voff  OFF  0 PULSE(0 {VDDL} 8u 10n 10n 1u 5u)

X1 BOOT SW VDD 0 ON OFF ON_HS OFF_HS LEVELSHIFTER

.options reltol=1e-3 abstol=1e-9 vntol=1e-5 chgtol=1e-13 method=trap gmin=1e-10 itl1=500 itl4=200
.tran 5n 15u
.print tran V(ON) V(OFF) V(ON_HS) V(OFF_HS) V(SW) V(BOOT)
.end
```

Failure output on my ngspice 46 against the unpatched PDK (last lines):

```
Note: Starting dynamic gmin stepping
Warning: Dynamic gmin stepping failed
Note: Starting true gmin stepping
Warning: True gmin stepping failed
Note: Starting source stepping
Warning: source stepping failed
doAnalyses: TRAN:  Timestep too small; time = 4.54697e-06, timestep = 6.25e-21: trouble with node "e.x1.xdelay.xcb.ecextra#branch"
run simulation(s) aborted
```

(That `e.x1.xdelay.xcb.ecextra#branch` is the `Cextra` element in the
CMIM_STD instance `XCB` inside `XDELAY` — the delay cell's chain-B
shunt cap.)

## 5. Isolating which patch actually unblocks the level shifter

I went back and applied each of the three substitutions independently to
the unpatched PDK and re-ran the deck above. **Where the failure node
moved tells you which element is actually load-bearing.**

| Patch applied | Result | Where the failure stalled |
|---|---|---|
| None (unpatched) | FAIL | `e.x1.xdelay.xcb.ecextra#branch` (CMIM_STD's Cextra) |
| `Vshift → 1 mΩ Rshift` only | FAIL | `e.x1.xdelay.xcb.ecextra#branch` (same Cextra) |
| `Cextra → 1 aF` only | FAIL | `b.x1.xdelay.xrb.bvcr#branch` (RPOLY_HI's BVCR) |
| `BVCR → V=0` only | FAIL | `e.x1.xdelay.xcb.ecextra#branch` (same Cextra) |
| All three patches | FAIL (later in the run) | `voff#branch` (the OFF-pulse VSRC itself) |

That last row is important. **Even with all three patches applied, the
deck still doesn't converge under those `.options` settings** — it just
fails further along. The "fix" only really works once I additionally
relax the ngspice options (`reltol=5e-3 abstol=1e-8 vntol=1e-4
method=gear gmin=1e-8 srcsteps=10 gminsteps=10 noopiter`), which I do in
the eval-task simulation. So part of what I claimed as "the PDK
behavioral B-sources break ngspice" was actually "this topology + tight
default tolerances break ngspice, and the B-source branches are where
the solver gives up."

That's exactly the (b)/(c) failure-mode you flagged: the patches
**correlated** with ngspice converging, but mostly because they removed
dynamic state and made the solver's task easier — not because the
behavioral elements themselves were unsimulatable. Conceded.

## 6. One genuine cross-check: the simplified topology + unpatched PDK

The eval task I'm building uses a stripped-down level shifter (`pdk/
levelshifter_simple.spice` in the task's worktree — cross-coupled PMOS
latch + HV cascodes + leg switches + output buffers, no delay cell, no
mirror). I re-ran my reference design `{wp=3u, wn=100u, whv=80u,
whvp=80u, lhv=6u}` against this simplified topology with the **unpatched
PDK** at all three corners (TT / SS / FF):

| Corner | Result | Note |
|---|---|---|
| TT @ 27 °C | PASS | sim runs to completion, meas extracts |
| SS @ 125 °C | **FAIL** | `Warning: singular matrix: check node v.x1.xn6.vshift#branch` — then meas can't find the falling edge |
| FF @ -40 °C | PASS | sim runs to completion |

This is the cleanest standalone demonstration that the Vshift issue
hits a real cross-corner reliability problem in modest-complexity HV
circuits (two LDMOS cascodes with their gates tied to VDD is enough at
SS), not just in pathological topologies. It also lines up with your
repro #3 result.

## 7. What I'm revising

1.  **Claims #1 (resistor BVCR), #2 (capacitor Cextra), #4 (BJT Bavl)
    should be retracted at the PDK-level.** Your regression suite is
    right; my isolated repros confirm yours. They are not categorical
    convergence problems. They only showed up as *symptoms* in a deck
    that was already in trouble for other reasons.

2.  **Claim #3 (HV LDMOS Vshift singular matrix when MM_ON=0) stands.**
    It reproduces standalone on my ngspice 46 with two cascoded
    NDMOS200, gates tied, MM_ON=0 — exactly your repro #3, which fails
    here. And it's the one that bites the simplified
    level-shifter-class topology at SS / 125 °C with the unpatched PDK.

3.  **The `NGSPICE_COMPAT`-switch proposal in
    `HANDOFF_ngspice_compat.md` is too broad.** A targeted fix to just
    the LDMOS `Vshift` is what's actually justified by the evidence I
    have. Possible scopes, smallest first:
    - Replace `Vshift g g_int DC {-DVTH_MM}` with a 1 mΩ series resistor
      *only* when `MM_ON=0` — gate the choice on `MM_ON`, not on a new
      `NGSPICE_COMPAT` knob. When MM is enabled the original VSRC is
      meaningful and stays.
    - Or: keep the VSRC form but break the singularity differently
      (e.g., a small parallel gmin resistor across the VSRC — many
      foundries do this in their official model wrappers).
    - Either way, leave BVCR / Cextra / Bavl alone.

4.  **The version mismatch (yours 45.2 / mine 46) is the most likely
    explanation** for why even claim #3 was only borderline-visible
    in your suite — if your suite tests stacked LDMOS at all (does it?
    your description mentions stacks of *cascoded* devices but the cited
    smoke-suite line is "every VDMOS device × all 5 corners × MM_ON ×
    PROC_ON" which sounds like single-device sweeps), it would have
    caught the singularity. Worth verifying that the suite has a deck
    where two or more LDMOS share a gate node with MM_ON=0.

## 8. What I'd ask you to do next

If you can spare it: confirm whether `pdk_validation/regression/`
includes a deck that puts ≥2 VDMOS devices in series **with their
gates tied to the same node** at `MM_ON=0`. If not, the suite isn't
quite covering the case that fails — adding one minimal deck like the
repro #3 I ran would catch this regression on every commit.

If yes, and it passes on your ngspice 45.2, then the bug is
ngspice-46-specific. In that case the smallest-blast-radius fix is to
target only ngspice 46+, which can be done by checking the simulator
version at parse time (ngspice supports `simulator lang=ngspice` and
provides a version variable).

---

*Generated by Claude on 2026-05-28 against the PDK files as supplied
to my eval-task session (no git SHA available on my side). All four
repros + the failing level-shifter deck are reproducible from the
files referenced above — happy to push them to a branch if useful.*
