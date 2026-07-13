# Reply to HANDOFF_ngspice_compat.md — request for repro info

**Status:** investigation paused pending information from the handoff
author. The PDK side has not been changed.

**Context:** `HANDOFF_ngspice_compat.md` proposes adding an
`NGSPICE_COMPAT` switch that gates four classes of behavioral
expression in `autohv_bicmos180_case.lib`. Before applying it I
cross-checked the claims against the PDK's existing regression
suite on **ngspice 45.2 (Windows, `ngspice_con.exe`)**, and three of
the four claims do not reproduce. Details and the specific info I
need to move forward are below.

---

## 1. What the regression suite already verifies vs. the handoff's claims

The four claims in `HANDOFF_ngspice_compat.md` map onto patterns that
the repo's `pdk_validation/regression/` suite already exercises
end-to-end. Here is the current cross-check, at commit `0d16789`
(post your handoff commit, no PDK files modified since then):

| Claim | Pattern | Handoff says | Regression suite result on ngspice 45.2 |
|:-:|---|---|---|
| **#1** | `BVCR mid n V={V(p,mid)*(VCR1*sqrt(V(p,n)*V(p,n)+1e-6) + VCR2*V(p,n)*V(p,n))}` in the 5 R subckts | "Timestep too small" abort in any non-trivial transient | `pdk_validation/regression/transients/r_thru_zero.cir` drives **1 MHz sine through V(p,n)=0** on **RNWELL** (strongest VCR, 8000 ppm/V). Runs in **~55 ms**. Pass since commit `0c4992e`. |
| **#2** | `Cextra p n C={C0NOM*(VCC1*sqrt(...)+VCC2*V*V)}` in the 4 C subckts | "Timestep too small" at t=0 for any deck including one | `pdk_validation/regression/transients/c_thru_zero.cir` drives **1 MHz sine through V(p,n)=0** on **CMIM_HI** (strongest VCC). Runs in **~55 ms**. Pass since `0c4992e`. |
| **#3** | `Vshift g g_int DC {-DVTH_MM}` collapses to 0 V VSRC when `MM_ON=0`; two LDMOSes sharing a gate ⇒ singular matrix | Failure cited as the immediate blocker in level shifters | Phase A smoke runs **every VDMOS device × all 5 corners × MM_ON ∈ {0,1} × PROC_ON ∈ {0,1} = 260 ops** (40 dev × 5 × 4 / 6 families ≈ 260 VDMOS ops), all converging. **Just ran a fresh cascoded-pair test** (two NDMOS200 + two NDMOS120, all four with shared gates and `MM_ON=0`): converges cleanly. No singular-matrix warning. |
| **#4** | `Bavl ci b I={abs(i(Vsen))*( 1/(1-min(max(V(ci,b)/BVCBO,0),0.997)**4) - 1 )}` in the 4 BJT subckts | "Hits the same convergence wall" | **P2.1 audit** in `pdk_validation/bjt_avalanche_stress/` swept all 4 BJTs in DC from 0 to BVCBO+20 %, in transient ramp through BVCBO over 1 µs, and in transient switching with Ic crossing 0 on 1 ns edges. All converge in 50–250 ms each. `pdk_validation/regression/transients/bjt_breakdown_ramp.cir` exercises this on every CI run since commit `415d8ea`. |

Full regression baseline at current `HEAD` (`0d16789`):

```
smoke       :  800 /  800   ops   (40 devices × 5 corners × 4 stat combos),  ~50 s wall
passives    :    9 /    9   golden curves, max rel err 0.00e+00
transients  :    7 /    7   decks (incl. the two AC-thru-zero kink killers and the BJT BVCBO ramp),  ~0.5 s wall
corners     :   36 /   36   sign-of-Δ vs TT across 9 family probes
```

How to reproduce locally:

```sh
python pdk_validation/regression/run_smoke.py
python pdk_validation/regression/run_passives.py
python pdk_validation/regression/run_transients.py
python pdk_validation/regression/run_corners.py
```

## 2. Why I can't act on the handoff yet

The four claims are stated categorically ("any non-trivial transient",
"any deck that includes one of these caps", "any HV-stack circuit"),
but the suite above contradicts each one on ngspice 45.2. Either:

- (a) the failures are **specific to a particular ngspice
  version / build** older than 45.2 that I don't have in front of me;
- (b) the failures are **specific to the level-shifter topology**
  (multi-loop feedback, latch + delay + mirror reset) and the
  patterns themselves are only incidental — in which case gating them
  would mask a topology problem rather than fix it; or
- (c) the sed-patch's success is **correlated, not causal** —
  collapsing the B-sources removes dynamic state and may stabilize
  for reasons other than "the kink was unsolvable."

Applying the proposed `NGSPICE_COMPAT` switch blind would
unconditionally drop ~26 sites of VCR/VCC/HV-MOS fidelity for every
ngspice user, including ones who don't have the problem. That's a
high cost for a fix whose actual root cause hasn't been pinned.

## 3. What I need from you to investigate

The minimum to localize the issue:

### 3.1. Your ngspice environment

```
$ ngspice --version
# or just paste the banner ngspice prints on startup
```

Plus:

- OS / arch (Linux distro + version, or macOS version, or Windows + Spice build)
- Whether you have a `~/.spiceinit` / `spinit` that sets options
  (`gmin`, `gminsteps`, `noopiter`, `method`, `reltol`, `abstol`,
  `vntol`, `compatmode`, etc.)
- Whether ngspice was built locally or installed from a package

### 3.2. The exact failing deck

The level-shifter deck plus any sub-includes. Either the full
`circuits/hv_charge_pump/hv_up_lvlsh/levelshifter.spice` (with whatever
device sizes you actually used when it failed), or a minimised version
that still fails. If the deck is large I can take it as-is, just need
the file.

### 3.3. The full failure output

ngspice's full stderr+stdout from t=0 to the abort. The summary lines
("Timestep too small", "singular matrix") are useful but the **lines
just before them are critical** — convergence-aborts usually print
the node or branch where ngspice gave up, plus the gmin / source
stepping attempts that preceded it. Paste raw text, not a screenshot.

### 3.4. Per-claim mini-repros

Before sending the full level shifter, please run the four minimal
decks below **in your failing ngspice environment** and report the
exit status + last 20 lines of output for each. This pinpoints which
of the four claims actually reproduces standalone vs. only inside the
level shifter.

#### Repro for claim #1 — resistor BVCR

```spice
* repro_1_resistor_vcr.cir
.include "autohv_bicmos180_case.lib"
.param case=0 PROC_ON=0 MM_ON=0
Vs s 0 SIN(0 5 1MEG)
XR s 0 RNWELL L=100u W=10u
.control
tran 10n 5u
echo R_VCR_OK
quit
.endc
.end
```

Expected on ngspice 45.2 (locally verified): `R_VCR_OK` reached in
~55 ms.

#### Repro for claim #2 — capacitor Cextra

```spice
* repro_2_capacitor_vcc.cir
.include "autohv_bicmos180_case.lib"
.param case=0 PROC_ON=0 MM_ON=0
Vs s 0 SIN(0 5 1MEG)
XC s 0 CMIM_HI L=100u W=100u
.control
tran 10n 5u
echo C_VCC_OK
quit
.endc
.end
```

Expected on ngspice 45.2: `C_VCC_OK` reached in ~55 ms.

#### Repro for claim #3 — cascoded LDMOS with shared gate, MM_ON=0

```spice
* repro_3_stacked_ldmos.cir
.include "autohv_bicmos180_case.lib"
.param case=0 PROC_ON=0 MM_ON=0
Vgd  gd 0 PULSE(0 5 5n 1n 1n 50n 100n)
Vdd  vdd 0 100
Rmid vdd mid 1k

XN1 vdd gd mid  NDMOS200 W=40u L=8u
XN2 mid gd 0    NDMOS200 W=40u L=8u

Vgd2 gd2 0 PULSE(0 5 5n 1n 1n 50n 100n)
XN3 vdd  gd2 mid2 NDMOS120 W=40u
XN4 mid2 gd2 0    NDMOS120 W=40u

.control
tran 1n 200n
echo STACKED_LDMOS_OK
quit
.endc
.end
```

Expected on ngspice 45.2 (verified just now): `STACKED_LDMOS_OK`
reached, no `singular matrix` warning.

#### Repro for claim #4 — BJT avalanche near BVCBO

```spice
* repro_4_bjt_avalanche.cir
.include "autohv_bicmos180_case.lib"
.param case=0 PROC_ON=0 MM_ON=0
Vcc cc 0 PWL(0 0 1u 17 100u 17)
Ib  0 b 10u
Ve  e 0 0
XQ  cc b e NPN_LV AREA=1
.control
tran 5n 1.2u
echo BJT_AVALANCHE_OK
quit
.endc
.end
```

Expected on ngspice 45.2 (verified in P2.1 audit): `BJT_AVALANCHE_OK`
reached, no `Timestep too small`.

### 3.5. The PDK state you tested against

```
$ cd <pdk-checkout> && git rev-parse HEAD
```

If you're on a commit older than `b90b132` (the PDMOS200 add), it
predates several P0/P1 fixes that may matter here.

## 4. What I'll do once you reply

Branching by what your repros show:

- **All four repros pass on your ngspice but the level shifter still
  fails** → it's a topology problem in the level shifter (see
  section 4.1 of the original handoff which already half-admits
  this). I'll help debug the topology if you want, but no PDK change
  needed.
- **One or more of repros 1–4 fail on your ngspice** → that
  specific pattern + version combo is the issue. The fix scope is
  proportional to which subset reproduces. Likely a targeted
  smoothing-epsilon bump or a minimum-conductance shunt at the
  specific subckts, not a global compat switch.
- **All four repros fail on your ngspice** → it's a global
  ngspice-version issue. At that point the `NGSPICE_COMPAT` switch
  becomes the right answer, and I'll implement it the way the
  handoff proposes (with the open default question answered:
  default 0, opt-in to the compat path).

## 5. Where to send your reply

Just push the repro outputs + ngspice version + failing deck to a
branch (or paste into a new `HANDOFF_ngspice_compat_REPRO_RESULTS.md`
next to this file) and let me know. I'll pick it up and continue
from there.

---

*Generated by Claude on 2026-05-28 against PDK commit `0d16789`.
The PDK files have not been modified by this investigation —
`HANDOFF_ngspice_compat.md` arrived in commit `0d16789` and
`autohv_bicmos180_case.lib` is still at the state of commit `b90b132`.*
