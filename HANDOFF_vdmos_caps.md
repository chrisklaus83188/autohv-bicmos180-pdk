# PDK handoff: VDMOS terminal capacitances are ~1000x too large

## Summary

Every VDMOS `.model … _INT` card in `autohv_bicmos180_case_models.inc` has
`cgs`, `cgdmax`, `cgdmin`, and `cjo` set ~3 orders of magnitude too large for
the `W_REF=10µm` reference cell. A 40µm-wide NDMOS200 (a typical cascode size)
presents **172 pF** of drain capacitance at low Vds by direct AC measurement;
the physical number for an on-chip 40µm 200V LDMOS is tens of fF.

This is not a fidelity nicety — it produces a **real SOA violation** in any
HV-cascode circuit (the oversized drain–source `cjo` couples the HV drain slew
straight onto high-impedance cascode source nodes), and it also distorts
switching speed. The earlier ngspice-compat handoff said *"models.inc … these
are fine, do not touch"* — that was about the behavioral B/C/Vshift patterns in
the **subckt wrappers**. This is a different, parametric issue in the **model
cards** themselves.

NB: the **diode** cjo values in the same file (lines ~1332–1362, e.g.
`DIO_PN cjo≈2.8e-13`) are physically sane *and* corner-parametrized. Only the
**VDMOS** caps are wrong, which is what points at the generator step for those
cards specifically.

## The numbers

All 13 VDMOS flavors, as currently in `autohv_bicmos180_case_models.inc`
(values are absolute Farads for the `W_REF=10µm` cell; `mtot=W/W_REF` scales
them linearly):

| Model (`.model` line) | cgdmax | cgs | cjo |
|---|---|---|---|
| NDMOS20_INT (839)  | 4.032e-10 | 4.992e-10 | 1.4e-10 |
| PDMOS20_INT (865)  | 3.456e-10 | 4.032e-10 | 1.5e-10 |
| NDMOS40_INT (995)  | 2.52e-10  | 3.36e-10  | 1.0e-10 |
| PDMOS40_INT (1021) | 1.92e-10  | 2.52e-10  | 1.05e-10 |
| NDMOS60_INT (891)  | 1.536e-10 | 2.112e-10 | 7.5e-11 |
| PDMOS60_INT (917)  | 1.152e-10 | 1.44e-10  | 6.5e-11 |
| NDMOS80_INT (1047) | 1.0e-10   | 1.35e-10  | 5.5e-11 |
| PDMOS80_INT (1073) | 7.5e-11   | 9.5e-11   | 4.5e-11 |
| NDMOS120_INT (943) | 6.24e-11  | 8.64e-11  | 3.5e-11 |
| PDMOS120_INT (969) | 4.7e-11   | 6.1e-11   | 2.9e-11 |
| NDMOS200_INT (1099)| 3.5e-11   | 4.8e-11   | 2.2e-11 |
| PDMOS200_INT (1125)| 2.6e-11   | 3.4e-11   | 1.8e-11 |
| DNMOS20_INT (1151) | 1.44e-10  | 2.016e-10 | 7e-11 |

For NDMOS200_INT the exact lines are: cgdmax@1108, cgdmin@1109, cgs@1111,
cjo@1112.

**Why these are unphysical.** `cgs=4.8e-11` and `cjo=2.2e-11` on a *10µm-wide*
device imply ~2–5 pF/µm of terminal capacitance. For reference, the LV
`NMOS50` BSIM model in the same PDK uses overlap densities of ~0.2 fF/µm
(`cgso≈2e-10 F/m`) — i.e. the VDMOS cards are ~10,000× denser than the LV
devices. A 200µm-wide NMOS50 (5× wider than the cascode in question) has only
~1.6 pF of gate capacitance; the model claims the *narrow* HV device has ~100×
more than that.

**Likely root cause.** The values are monotonic in voltage class, so they were
generated systematically, not fat-fingered. A uniform `÷1000` lands every
device in the physical range (NDMOS200: cgs 48fF, cjo 22fF; NDMOS20: cgs 0.5pF,
cjo 0.14pF). That is exactly the signature of a **pF-vs-fF unit slip**
(`e-11` written where `e-14` was intended) applied across the VDMOS cap
generator. Please confirm against whatever source data / script produced these
cards.

## Reproduction (self-contained, needs only `autohv_bicmos180_case.lib`)

### Repro 1 — direct AC capacitance (the smoking gun)

```spice
* coss_check.spice — terminal C at the drain of a 40um NDMOS200, channel off
.include "autohv_bicmos180_case.lib"
.param case=0 PROC_ON=0 MM_ON=0 SOA_ON=1
VB  d 0 DC {VBIAS} AC 1
Vg  g 0 DC 0
XN5 d g 0 NDMOS200 W=40u L=8u
.param VBIAS=0.1
.ac lin 1 1meg 1meg
.control
  foreach vb 0.1 12 100 200
    alter VB dc=$vb
    run
    let cdrain = abs(i(VB))/(2*3.14159265*1e6*1)
    echo "Vds=$vb" ; print cdrain
  end
.endc
.end
```

Current models give: **172 pF @0.1V**, 52 pF @12V, 18.7 pF @200V. Expected
after fix: ≤ ~0.1 pF.

### Repro 2 — the in-circuit consequence (SOA on a 5V node)

A HV NMOS cascode (gate=VDD=5) over an LV pulldown is supposed to self-limit
its source node at `VDD−Vth ≈ 4V` (once the source rises, Vgs≤Vth shuts the
channel off). It does — for DC. But `cjo` couples the drain bring-up slew onto
the high-Z source as displacement current `cjo·dV/dt`, with no DC discharge
path, so the node parks far above 4V. **No switching happens in this deck** —
the pulldown gate is held at 0 the whole time:

```spice
* pump_check.spice
.include "autohv_bicmos180_case.lib"
.param case=0 PROC_ON=0 MM_ON=0 SOA_ON=1
VDD VDD 0 5
VON ON  0 0
VD5 D5  0 PWL(0 0  1u 211)            ; HV drain bring-up (200V rail + headroom)
XN5 D5 VDD S5  NDMOS200 W=40u L=8u    ; cascode, gate=VDD
XN7 S5 ON  0   0 NMOS50  W=200u L=1u  ; pulldown, gate held LOW (off)
CL  S5 0 50f                          ; representative high-Z load (next-stage gate)
.tran 1n 5u
.meas tran s5_final FIND v(S5) AT=5u
.end
```

Current models: `s5_final ≈ 14V` on a node that drives 5V devices. Setting
`cjo→0` in NDMOS200_INT collapses it to **3.96V** (= the intended `VDD−Vth`),
which isolates `cjo` as the coupling element. A full uniform `÷1000` on all
VDMOS caps brings the source nodes in a real level-shifter deck down to ~4V
(self-limit), *and* speeds up switching, *and* removes a spurious first-cycle
latch-toggle miss.

## Suggested fix

1. Regenerate `cgs / cgdmax / cgdmin / cjo` for all 13 VDMOS `_INT` cards from
   process capacitance densities at the `W_REF=10µm` cell. The relative
   ordering (monotonic decrease with voltage class) looks correct — it's the
   absolute scale that's off by ~1000×.
2. Verify with Repro 1: AC drain capacitance of a 40µm NDMOS200 should be in
   the tens-of-fF range (≤ ~0.1 pF), not 172 pF.
3. Consider corner-parametrizing the VDMOS caps with the `_isTT/_isFF/...`
   one-hot selector the way the diode `cjo` cards already are — right now the
   VDMOS caps are fixed across corners.

## Why it matters / cross-reference

- The original ngspice-compat handoff listed, under *Out of scope*, that the
  `levelshifter.spice` reference *"mirror+delay-cell reset path doesn't
  reliably toggle in both directions … a topology/sizing problem, not a PDK
  problem."* Part of that is **downstream of these caps**: with physical-range
  caps the toggle is clean from the first edge and prop delays drop. Worth
  re-checking that conclusion once the caps are fixed — some of it was a PDK
  artifact, not topology.
- Any HV-stack design (level shifters, gate drivers, charge pumps) that relies
  on cascode source-node self-limiting will currently show false SOA failures
  on its LV nodes purely from this cap error.

## Scope / what I did not touch

- I only have direct evidence for the **VDMOS MOSFET** caps (proven via AC
  measurement + the cjo→0 and ÷1000 experiments above). The **diode** PN cjo
  values look physically reasonable; I did not deeply exercise the **zener**
  cjo's (DZ_5V6/12/24 at lines ~1377–1407 are larger — may be fine for
  large-area zeners, worth a sanity glance while you're in there).
- I made no edits to the canonical PDK files. All experiments were run against
  throwaway copies in a separate test bench.
