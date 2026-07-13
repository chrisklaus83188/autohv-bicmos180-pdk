# PDK handoff: the `vshift#branch` singularity also blocks multi-instance floating HV current mirrors

**Models affected:** `NDMOS200`, `PDMOS200` (`autohv_bicmos180_case.lib`).
**Requested by:** the high-side rail-threshold monitor eval task (`chuba14f`).
**Relationship:** This is the **same root cause** as
[`HANDOFF_cascode_vshift_singularity.md`](HANDOFF_cascode_vshift_singularity.md) — the
`Vshift`/`g_int` 0 V series-gate source — now hit in a **multi-instance floating current-mirror**
configuration. This is a second, independent reproducer and a strong vote for that handoff's
**fix #1 (`delvto`)**. No new device model is needed; the realistic `VDMOS` is fine once the
`vshift#branch` unknowns are gone.

---

## TL;DR
A high-side sense architecture needs **several floating HV current-mirror front-ends** at once
(each = diode-connected `PDMOS200` mirror + `NDMOS200` cascode, floating at VIN up to 160–200 V).
With **two or more**, the operating-point solve goes singular on the `vshift#branch` unknowns and
collapses — even with stiff ideal gate/bias sources and the existing `Rgmin` mitigation. One
front-end converges; two never do above VIN ≈ 12 V. The `delvto` fix removes every `vshift#branch`
unknown, so multiplicity can no longer make the matrix singular.

## Confirmed: it is the `vshift#branch` singularity
The 2-front-end reproducer below aborts with exactly the matrix the cascode handoff predicts — the
`vshift#branch` rows go NaN on **every floating gate, mirror and cascode alike**, across all
instances:
```
Note: Starting dynamic gmin stepping
Warning: Dynamic gmin stepping failed
Warning: True gmin stepping failed
Warning: source stepping failed
Error: Transient op failed, timestep too small
doAnalyses: OP: Timestep too small; trouble with pdmos200_int-instance m.x_mrefb.m0
v.x_mcascb.vshift#branch   nan
v.x_mmirb.vshift#branch    nan
v.x_mrefb.vshift#branch    nan
v.x_mcasca.vshift#branch   nan
...
```
The new wrinkle vs. the cascode-only report: it is **not only the cascode gate**. Each
`PDMOS200`/`NDMOS200` in a floating front-end adds a `vshift#branch` unknown — the diode mirror
(`x_mref`), the mirror (`x_mmir`) **and** the cascode (`x_mcasc`). With several front-ends the
unknown count multiplies until the system is singular, and stiff `vcasc`/supply nodes no longer
rescue it. So the conditioning problem scales with the number of floating instances, not just with
gate-node stiffness.

## Why the task needs multiple floating HV front-ends
The monitor compares `CP − VIN` against three thresholds. With real (common-mode-dependent)
devices, **VIN-independent trip accuracy** requires each threshold's reference to pass through a
front-end matched to the signal front-end at the *same* VIN common mode — i.e. 4 floating HV
current-mirror front-ends (1 signal + 3 reference), each sustaining the full VIN as mirror Vds.
Ground-referenced references instead drift the trips ~0.5 V with VIN (unusable). So multi-instance
floating HV operation is intrinsic to the function.

## Boundary (measured, VIN = 160 V)
| Config | Result |
|---|---|
| 1 `PDMOS200` diode+mirror, drain loaded 50 kΩ to gnd | converges (device alone is fine at 165 V Vds) |
| 1 full front-end (mirror→cascode→Rout), `R_pull` = 10 MΩ | fails (`vshift#branch` singular) |
| …same, `R_pull` = 100 kΩ (floating node stabilized) | converges |
| **2** full front-ends, `R_pull` = 100 kΩ | **fails** |
| **4** full front-ends (full comparator circuit) | converges only at VIN ≤ 12 V; fails ≥ 16 V |

So the device is fine standalone, a single front-end is rescuable with a stronger floating-node
pull, but **2+ floating front-ends are intractable** — which is the operational requirement.

## Convergence aids that did NOT help (≥ 2 instances)
`.nodeset` on the sense nodes *and* the floating internal `refg`/`mird` nodes; `.options
gminsteps`/`srcsteps`; `cshunt` 1e-13…1e-10; slow VIN soft-start (50–100 µs); cshunt + soft-start;
and a VIN continuation `.dc` sweep from 0. All collapse the OP timestep on the `vshift#branch`
rows. This matches the cascode handoff's finding that the 1 GΩ `Rgmin` shunt is insufficient.

## Reproducer (standalone, references the PDK `.lib`)
Two floating HV current-mirror front-ends — the OP collapses. Delete the "B" block and it
converges; that one-vs-two boundary is the whole problem.
```spice
.title PDMOS200 multi-instance floating-mirror convergence repro
.include "autohv_bicmos180_case.lib"
.param case=0 PROC_ON=0 MM_ON=0
.options temp=27
V_vin  vin   0 DC 160
V_casc vcasc 0 DC 5
* --- front-end A (signal): floats at VIN, mirror sustains ~160 V Vds ---
B_cpA  vcpA 0 V=V(vin)+5
X_MrefA refgA refgA vcpA PDMOS200 W=30u L=5u
X_RrefA refgA vin   RPOLY_HI W=1u L=90u
X_MmirA mirdA refgA vcpA PDMOS200 W=30u L=5u
R_pullA mirdA 0 100k
X_McascA mirdA vcasc voutA NDMOS200 W=60u L=5u
X_RoutA voutA 0 RPOLY_HI W=1u L=43u
* --- front-end B (reference): identical, also floating at VIN ---
B_cpB  vcpB 0 V=V(vin)+4.3
X_MrefB refgB refgB vcpB PDMOS200 W=30u L=5u
X_RrefB refgB vin   RPOLY_HI W=1u L=90u
X_MmirB mirdB refgB vcpB PDMOS200 W=30u L=5u
R_pullB mirdB 0 100k
X_McascB mirdB vcasc voutB NDMOS200 W=60u L=5u
X_RoutB voutB 0 RPOLY_HI W=1u L=43u
.control
op
print v(voutA) v(voutB)
.endc
.end
```

## The fix
**Fix #1 from `HANDOFF_cascode_vshift_singularity.md` (move the Vth-mismatch shift onto the `M0`
instance via BSIM `delvto` and delete `Vshift`/`g_int`/`Rgmin`)** should resolve this too: it
removes the `vshift#branch` matrix unknown from *every* `NDMOS200`/`PDMOS200`, so no number of
floating instances can make those rows singular. It is electrically transparent at nominal
(`MM_ON = 0`), so the realistic `VDMOS` I–V, output resistance, breakdown, and `MM_SIGMA` mismatch
all stay exactly as they are. Please verify the fix against **both** reproducers — the cascode one
and this multi-instance one.

## Acceptance criterion (chuba14f)
The reproducer above `op`-converges at VIN = 160 V when extended to **4 front-ends** (add C and D
referenced to `V(vin)+5.7` and `V(vin)+4.8`), in a few seconds, returning sane `voutX` (~1–3 V).
Once that holds I can re-enable VIN-referenced thresholds and finalize the task at full voltage.
