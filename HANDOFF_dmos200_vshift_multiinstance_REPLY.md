# REPLY — `vshift#branch` multi-instance convergence: proposed fixes don't apply to VDMOS; here's one that does

**Re:** `HANDOFF_dmos200_vshift_multiinstance.md` and `HANDOFF_cascode_vshift_singularity.md`
**From:** chuba14f task author
**Status:** breakdown re-rating received and confirmed working (thank you). The **convergence
fix is not in yet**, and I found that *both* fixes proposed in the cascode handoff are dead ends
for these devices. A different one-line fix works — details below so you can land it canonically.

---

## 1. The breakdown re-rating is confirmed ✓
`PDMOS200` FF/SF = 216.2 V is in; VIN=200 V no longer avalanches in my circuit. Nothing more
needed there.

## 2. The proposed convergence fixes do NOT work for `NDMOS200`/`PDMOS200`
Both suggestions in `HANDOFF_cascode_vshift_singularity.md` §"Suggested fixes" were written for
BSIM3/4, but `NDMOS200_INT`/`PDMOS200_INT` are **`VDMOS`** models. Tested on ngspice (the
4-floating-front-end reproducer from my handoff):

- **Fix #1 — `delvto` on `M0`:** ngspice rejects it → **`unknown parameter (delvto)`**. `VDMOS`
  has no per-instance Vth-offset parameter, so the shift cannot move onto the instance. (This is
  almost certainly why the fix couldn't be implemented.)
- **Fix #2 — lower `Rgmin`:** tried `1e7`, `1e6`, `1e5` → **still singular** (`vshift#branch`
  → NaN, timestep collapse). Insufficient for the multi-instance case.

## 3. A fix that works: condition `g_int` to the (determined) source node
The `vshift#branch` row is singular because `g_int` (the internal gate node after the 0 V
`Vshift` source) has **no DC path to any determined node** — `Rgmin` only ties it to `g`, which
in these circuits is itself a floating high-impedance node (a diode-connected mirror gate). Give
`g_int` a high-value path to the **source** terminal `s` (which *is* determined) and the row
becomes well-posed. In both the `NDMOS200` and `PDMOS200` subckts, add one line after `Rgmin`:

```spice
Vshift g g_int DC {-DVTH_MM}
Rgmin  g g_int 1e9
Rcond  g_int s 1e7          ; <-- ADD: DC path from the floating gate-shift node to a determined node
```

**Verified** (ngspice, my 4-front-end reproducer, VIN=200 V, `MM_ON=0`):
- `Rcond` = `1e8`, `1e7`, `1e6` all converge; **2 and 4 floating front-ends both solve** (vs. hard
  singular without it).
- Sane, correctly-ordered sense outputs (1.11 / 1.28 / 1.34 / 1.58 V for the 4.3 / 4.8 / 5.0 /
  5.7 V differentials).
- A single front-end now converges even at `R_pull = 10 MΩ` (previously needed ≤ 100 kΩ).
- Leakage through `Rcond` ≈ 0.1 µA at these bias points (≈ 0.2 % of the ~55 µA mirror current) and
  is common-mode/matched → electrically transparent; the `Vshift` source still carries the
  `MM_SIGMA`/`MM_ON` mismatch unchanged.

`Rcond` is the same *kind* of element as the existing `Rgmin` shunt — just tied to a node that is
actually determined, which is what `Rgmin`'s 1 GΩ-to-`g` could not guarantee once `g` floats.

## 4. Acceptance test (please verify before landing)
```spice
.title PDMOS200 multi-instance floating-mirror convergence (4 front-ends)
.include "autohv_bicmos180_case.lib"
.param case=0 PROC_ON=0 MM_ON=0
.options temp=27
V_vin vin 0 DC 200
V_casc vcasc 0 DC 5
* repeat this block for tags A/B/C/D with V(vin)+5 / +4.3 / +5.7 / +4.8 :
B_cpA  vcpA 0 V=V(vin)+5
X_MrefA refgA refgA vcpA PDMOS200 W=30u L=5u
X_RrefA refgA vin   RPOLY_HI W=1u L=90u
X_MmirA mirdA refgA vcpA PDMOS200 W=30u L=5u
R_pullA mirdA 0 10Meg
X_McascA mirdA vcasc voutA NDMOS200 W=60u L=5u
X_RoutA voutA 0 RPOLY_HI W=1u L=43u
* ...B, C, D...
.control
op
print v(voutA) v(voutB) v(voutC) v(voutD)
.endc
.end
```
Pass = `op` converges with `voutX` ~ 1–2 V (no singular matrix, no timestep collapse).

## 5. Verification criteria (same spirit as the cascode handoff)
- **Nominal transparent:** with `MM_ON=0`, reference-design metrics unchanged (within rounding)
  before vs. after adding `Rcond`.
- **Mismatch preserved:** with `MM_ON=1` / `MM_SIGMA≠0`, the effective Vth shift is unchanged
  (the `Vshift` source is untouched).
- **Self-heating:** I only tested `SH_ON=0`; please confirm `SH_ON=1` still converges (the `g_th`
  path derives from `g_int`, so `Rcond` should help there too).
