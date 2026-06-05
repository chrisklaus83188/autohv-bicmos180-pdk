# PDK handoff: fast transients on multiple floating HV LDMOS micro-step into timeouts above ~100 V

**To:** AutoHV-BiCMOS180 PDK maintainer
**From:** chuba14f task author (high-side rail-threshold monitor)
**Date:** 2026-06-05
**Models:** `NDMOS200` / `PDMOS200` (`VDMOS`-based).
**Related (both resolved):** `HANDOFF_dmos200_vshift_multiinstance.md` (+ `_REPLY`) — the DC
`vshift#branch` singularity, fixed by `Rcond`; and `HANDOFF_dmos200_breakdown.md` — the FF
breakdown re-rating. **This is the time-domain analog of the vshift issue and is the last
blocker for running the task at its full 200 V range.**

---

## TL;DR
With the `Rcond` fix the circuit now solves cleanly in **DC and in quasi-static transients** at
200 V. But any **fast** transient (a step edge or a 10 V/µs slew) on the 4 floating HV LDMOS
front-ends **micro-steps into a timeout above ~100 V** — the solver drives the timestep toward
zero tracking displacement currents on the floating high-Vds devices. The quasi-static trip
survives because it never applies a fast edge. I've exhausted the testbench/tolerance/option
space (list below) without success and could not find a PDK lever (I tried softening the VDMOS
Cgd transition — no effect). Requesting your investigation: **is there a way to make these
devices transient-tractable for fast transients at high Vds**, analogous to how `Rcond` made
them DC-tractable? If it's genuinely inherent, a confirmation lets me cap VIN at the simulatable
limit with confidence.

## Reproducers (in this repo root — run them directly)
Generated from the actual task grader. Each is the full chuba14f topology (4 floating
`PDMOS200`/`NDMOS200` current-mirror front-ends + 5 V comparators + bias), brought up with a
dV/dt-matched VIN soft-start, then the dynamic stimulus.

```
cd <this repo>
ngspice -b repro_slew_vin100.cir    # 10 V/us VIN slew, VIN=100 : completes in ~0.6 s
ngspice -b repro_slew_vin200.cir    # 10 V/us VIN slew, VIN=200 : micro-steps, never finishes (Ctrl-C after ~1 min)
ngspice -b repro_delay_vin100.cir   # fast CP-VIN edge,  VIN=100 : completes in ~0.6 s
ngspice -b repro_delay_vin200.cir   # fast CP-VIN edge,  VIN=200 : micro-steps, never finishes
```
The 100 V / 200 V pairs are identical except for the VIN level — that's the whole signature.

## The boundary (measured, FF/-40 C; all three analyses)
```
VIN     trip            delay           slew
100     OK / 0.4 s      OK / 0.6 s      OK / 0.6 s
120     OK / 0.4 s      timeout         timeout
200     OK / 0.4 s      timeout         timeout
```
Sharp: 100 V all-clear, 120 V the dynamics die; the quasi-static trip is unaffected at any VIN.

## What I isolated
- **It's the measurement window, not the bring-up.** I ran the soft-start at a *coarse* timestep
  (fast) and forced fine resolution *only* in the measurement window via dense PWL breakpoints —
  it still times out. The fast transient itself is where the timestep collapses.
- **Not the slew rate.** 2 V/µs times out too, so it isn't `dV/dt` magnitude.
- **It's the floating HV LDMOS.** The dynamic stimulus swings the device drains fast at high Vds
  (`vcp = VIN + CP-VIN` moves with the edge/slew); with 4 such devices above ~100 V the solver
  micro-steps. The 5 V comparators (`NMOS50`/`PMOS50`) are not implicated (they're low-voltage).

## What I exhausted (so you don't repeat it)
Faster soft-start (4–8 V/µs), **softening the VDMOS Cgd transition** (`a=0.22→0.05` on
`NDMOS200_INT`/`PDMOS200_INT` — no effect, and it broke the trip), removing the HV coupling caps,
`.options chgtol`=1e-12…1e-10 / `trtol`=50…100 / `cshunt` / `method=gear`, a gentle 100 ns delay
edge, a 2 V small-excursion slew, coarse global tstep, `tstart`+`tmax` split-resolution, and
breakpoint-localized fine stepping. Every one times out at VIN ≥ ~120 V.

## Hypothesis + the ask
The likely culprit is the interaction of the `VDMOS` **nonlinear voltage-dependent junction
capacitances** (Cgd/Cds) with the **floating high-impedance internal nodes** (the diode-mirror
`refg` and `mird`) when the drain swings fast at high Vds — the same node structure that needed
`Rcond` in DC, now stressed dynamically. **Please investigate whether the model (cap formulation,
an internal series/shunt conditioning, charge-model smoothing, or a transient-friendly
macromodel) can take a fast drain transient at 150–200 V Vds with several floating instances
without the timestep collapsing.** To isolate, the comparators can be deleted from the reproducers
(strip the `X_c_*` lines and the `CMP` subckt) — the 4 front-ends + the slew alone should still
exhibit it.

## Acceptance criterion
`ngspice -b repro_slew_vin200.cir` and `repro_delay_vin200.cir` **complete in a few seconds**
(like their 100 V counterparts), with a physical slew glitch / prop delay. Then I can run the
task end-to-end at the full 200 V range.
