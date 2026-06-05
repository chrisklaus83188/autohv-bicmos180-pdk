# PDK handoff: `PDMOS200` breakdown is below its 200 V class (and below `NDMOS200`)

**Models affected:** `PDMOS200` (and a sanity question on `NDMOS200`) — the `PDMOS200_INT` /
`NDMOS200_INT` `bv=` lines in `autohv_bicmos180_case_models.inc`.
**Requested by:** the high-side rail-threshold monitor eval task (`chuba14f`).
**Relationship:** independent of the convergence issue in
[`HANDOFF_dmos200_vshift_multiinstance.md`](HANDOFF_dmos200_vshift_multiinstance.md) — this one is
purely about the breakdown rating. Both touch the same devices.

---

## TL;DR
`PDMOS200` avalanche breakdown at the **FF/SF** corners is **194.58 V** — *below* 200 V, and below
`NDMOS200`'s worst corner (211.5 V). A high-side circuit that puts the full rail across one HV
device therefore avalanches at FF when VIN ≳ 195 V. Heads-up + a request to confirm whether
`PDMOS200` is meant to be a true 200 V part. **No action is strictly required for my task** (I'm
capping VIN at 160 V, comfortable margin), but you may want to re-rate the P-device.

## The data (current model card values)
```
            TT       FF       SS       FS       SF      worst
NDMOS200  225 V   211.5 V  238.5 V  211.5 V  238.5 V   211.5  (FF/FS)
PDMOS200  207 V   194.58V  219.42V  219.42V  194.58V   194.58 (FF/SF)   <-- below 200 V
```

## Why it matters (consuming circuit)
The monitor's front-end is a floating high-side current mirror that level-shifts a 5–VINmax
common-mode signal to ground. Because the cascode gate is ground-referenced (≤ 5.5 V), the cascode
cannot hold its drain high, so **the PMOS mirror sustains essentially the entire common-mode VIN as
Vds** — inherent to a single-stage HV level-shifter. Measured at FF / 125 °C, sweeping VIN, the
mirror avalanches at ~195 V (Vds clamps at `bv`, current ~doubles, sense output corrupts). LEVEL=1
hid this entirely (no `bv`).

## Standalone reproducer
```spice
.include "autohv_bicmos180_case.lib"
.param case=1 PROC_ON=0 MM_ON=0        ; FF
.options temp=125
V_low  vlow  0 DC 200
V_high vhigh 0 DC 205                   ; CP-VIN = 5 V differential
V_casc vcasc 0 DC 5
X_Mref refg refg vhigh PDMOS200 W=30u L=5u
X_Rref refg vlow  RPOLY_HI W=1u L=90u
X_Mmir mird refg vhigh PDMOS200 W=30u L=5u
R_pull mird 0 100k
X_Mcasc mird vcasc vout NDMOS200 W=60u L=5u
X_Rout  vout 0 RPOLY_HI W=1u L=43u
.control
op
print v(vout) v(mird) v(vhigh) i(V_high)   ; v_out should be ~2 V; reads ~4 V (avalanche) at FF
.endc
.end
```
(`R_pull` lowered to 100 kΩ here so the single front-end converges past the `vshift#branch` issue —
see the convergence handoff.)

## What I'd like you to decide
1. **Is `PDMOS200` intended to be a true 200 V device?** If yes, raise FF/SF `bv` to give margin
   above 200 V (e.g. ≥ 215 V) so a 200 V single-device level-shifter is feasible again.
2. **Is 194.58 V the correct silicon?** p-LDMOS often *do* break down lower than the n-side, so it
   may be right — if so, please confirm and note in the reference manual that `PDMOS200` is a
   ~190 V-class part so downstream HV designs cap VIN accordingly.
3. **The N/P asymmetry in which corners are weak** (`NDMOS200` weak at FF & FS, `PDMOS200` at FF &
   SF) is worth a sanity check — intended, or a corner-selector copy-paste? (Does not affect my
   task; FF is the common worst corner either way.)

## What my task does meanwhile
Caps **VINmax = 160 V** (mirror Vds ≈ 163 V at FF, ~31 V margin to 194.58 V — verified clean). If
you re-rate `PDMOS200` to a true 200 V part, ping me and I can raise VIN back toward 200 V (the task
is intentionally flexible on VINmax).
