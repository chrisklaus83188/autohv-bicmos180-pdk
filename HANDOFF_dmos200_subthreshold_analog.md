# PDK handoff: `NDMOS200`/`PDMOS200` are subthreshold at analog (µA) currents — power-FET `kp`

**To:** AutoHV-BiCMOS180 PDK maintainer
**From:** chuba14f task author (high-side rail-threshold monitor)
**Date:** 2026-06-06
**Models:** `NDMOS200_INT` / `PDMOS200_INT` (the `kp` / `vto` stat params).
**Related (resolved):** `HANDOFF_dmos200_vshift_multiinstance*.md` (Rcond), `HANDOFF_dmos200_breakdown.md`,
`HANDOFF_dynamic_transient_microstepping.md` (Rcond=1e6). Those made the devices *simulatable*; this is
about whether they're *usable as analog devices*.

---

## TL;DR
The 200 V HV DMOS are modeled with **power-FET transconductance** (`KP_PDMOS200 = 0.088 A/V²`,
`KP_NDMOS200 = 0.22 A/V²`). As a result they sit in **subthreshold** at the µA currents an analog HV
front-end runs at, and only reach strong inversion near **5 mA**. A current mirror built from them is
forced to max gm/I, which turns a ~2 mV local Vth mismatch into a **~400 mV (1σ) trip shift** in my
monitor — i.e. the device is unusable as a precision analog mirror at a realistic current budget. If
these are meant to be HV *drift* MOSFETs (not discrete power FETs), the channel transconductance looks
too high. Please advise / re-fit.

## Measured (the core evidence)
`PDMOS200`, W=30 µm L=5 µm, as a self-biased diode at Vds = 200 V (the front-end's operating CM):
```
  I        Vsg(V)   Vov = Vsg-|Vth|   gm/I (1/V)   regime
  10 µA    1.179     -0.131            26.3         subthreshold
  55 µA    1.244     -0.066            26.3         subthreshold
 200 µA    1.297     -0.013            23.8         moderate
   1 mA    1.378     +0.068            17.2         moderate
   5 mA    1.504     +0.194             9.6         strong inversion
```
(`VTO_PDMOS200 = -1.31 V`.) gm/I stays pinned near the subthreshold ceiling (~26/V ≈ 1/(kT/q·n))
until ~mA. A normal analog MOSFET at this W would be at Vov ≈ +0.2 V (strong inversion) by ~50 µA.

## Why it matters
My front-end is a floating HV current mirror (`PDMOS200` M_ref/M_mir) that senses CP−VIN at ~tens of
µA — the CP charge-pump output is current-limited, so the budget is genuinely µA. In subthreshold,
gm/I is maximal, so the mirror's local Vth mismatch (M_ref vs M_mir) is amplified ~80–170× into the
trip threshold. A Monte-Carlo (independent ±1σ per device) gives **σ(trip) ≈ 340–440 mV** — a ½ V-class
monitor instead of a precision one. Sizing barely helps: bigger W lowers the mismatch σ but lowers the
current density further (deeper subthreshold), and running at mA to escape subthreshold blows the
current budget.

## The ask
Is `KP_NDMOS200`/`KP_PDMOS200` representative of an **HV drift MOSFET used as an analog device**, or is
it a discrete-power-FET value? For a drift/LDMOS the long element is the drift region, but the channel
transconductance should still put it in moderate/strong inversion at 10s–100s of µA. Options for you:
1. **Re-fit `kp`** (and `vto`/`theta` as needed) so the channel is in moderate inversion at ~µA — the
   physical analog operating point for HV drift MOSFETs.
2. **Confirm these are power-only** and the PDK needs a separate HV *analog* device for µA-class
   front-ends (none currently exists above 5 V — the core MOS top out at `NMOS50`/`PMOS50`).
3. **Guidance** on the intended analog operating current for this family, if I'm mis-using them.

Also worth a look while you're in there: the DMOS mismatch model scales as `1/√(W/W_REF)` (W only),
not `1/√(W·L)`, so designers can't trade area (length) for matching the usual way — secondary to the
`kp` issue but compounds it for analog use.

## Reproducer (standalone)
```spice
.title PDMOS200 subthreshold-at-uA reproducer
.include "autohv_bicmos180_case.lib"
.param case=0 PROC_ON=0 MM_ON=0
V_s  vs 0 DC 200
X_M  vg vg vs PDMOS200 W=30u L=5u    ; diode: d=g=vg, s=vs
I_load vg 0 DC 55u                   ; sweep 10u / 55u / 200u / 1m / 5m
.control
op
print v(vg)                          ; Vsg = 200 - v(vg); compare to |Vth|=1.31 V -> Vov<0 at uA
.endc
.end
```
Pass = at ~50–100 µA the device shows Vov > 0 (moderate/strong inversion), not the −0.07 V it shows now.
