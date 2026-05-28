# PDK ngspice-compatibility handoff

## Goal

Make `autohv_bicmos180_case.lib` simulatable in **ngspice** (currently the
PDK is authored for Qucs-S / Qspice and hits singular-matrix or
timestep-too-small failures in ngspice on any non-trivial transient). The
fix should preserve the existing Qucs-S behavior — ideally the same PDK
file works in both simulators, with the high-fidelity voltage-coefficient
and mismatch modeling gated on a parameter so ngspice can opt out.

You are editing the two files in this directory:

- `autohv_bicmos180_case.lib`        (397 lines — subcircuit wrappers; **all four problems live here**)
- `autohv_bicmos180_case_models.inc` (1444 lines — raw BSIM3 / VDMOS model cards; **these are fine, do not touch**)

## The four problematic patterns

All are behavioral elements (`B` sources or `C={...}`/`V=...` expression
elements) that ngspice's solver handles poorly when their expressions
involve `V(p,n)*V(p,n)+1e-6` style smooth-abs constructs or when they
degenerate to a zero-volt VSRC.

### 1. Resistor voltage-coefficient B-source (5 instances)

Pattern (line numbers in `autohv_bicmos180_case.lib`):

```
287: BVCR mid n V={ V(p,mid)*(VCR1*sqrt(V(p,n)*V(p,n)+1e-6) + VCR2*V(p,n)*V(p,n)) }
299: BVCR mid n V={ ... }    # RPOLY_LO
312: BVCR mid n V={ ... }    # RNWELL
324: BVCR mid n V={ ... }    # RNPLUS
336: BVCR mid n V={ ... }    # RPPLUS
```

The VCR coefficients are ~50–200 ppm/V. In ngspice this `B` source
introduces a branch variable that the solver can't keep stable under fast
transients; the failure mode is `Timestep too small ... trouble with node
"<...>.bvcr#branch"` aborting the run.

### 2. Capacitor voltage-coefficient C= expression (4 instances)

```
351: Cextra p n C={ C0NOM*(VCC1*sqrt(V(p,n)*V(p,n)+1e-6) + VCC2*V(p,n)*V(p,n)) }
366: Cextra p n C={ ... }    # CMIM_HI
380: Cextra p n C={ ... }    # CMOM
395: Cextra p n C={ ... }    # CFRINGE
```

VCC coefficients are ~5–60 ppm/V. The `C={expr}` form is a non-linear
capacitor; ngspice introduces an internal branch (`ecextra#branch`) for
it and the same timestep-too-small abort fires immediately at t=0 for
any deck that includes one of these caps.

### 3. HV LDMOS mismatch-shift VSRC (13 instances)

```
Vshift g g_int DC {-DVTH_MM}
```

Appears in every drift-MOS subckt: `NDMOS20`, `NDMOS40`, `NDMOS60`,
`NDMOS80`, `NDMOS120`, `NDMOS200`, `PDMOS20`, `PDMOS40`, `PDMOS60`,
`PDMOS80`, `PDMOS120`, `PDMOS200`, `DNMOS20`. When `MM_ON=0` (the
default), `DVTH_MM` evaluates to 0 and `Vshift` becomes a 0-V VSRC. Two
LDMOS instances whose gates connect to the same node form a singular
matrix block — ngspice prints `Warning: singular matrix: check nodes
v.x1.xn9.vshift#branch and v.x1.xn5.vshift#branch` and gmin-stepping then
fails. Any HV-stack circuit (level shifters, gate drivers, charge pumps)
hits this immediately.

### 4. BJT avalanche current B-source (4 instances)

```
217: Bavl ci b I={ abs(i(Vsen))*( 1/(1 - (min(max(V(ci,b)/BVCBO,0),0.997))**MAV_BJT) - 1 ) }
226: Bavl ci b I={ ... }    # PNP_LAT
235: Bavl ci b I={ ... }    # NPN_HV
244: Bavl ci b I={ ... }    # PNP_HV
```

Hits the same convergence wall as #1 and #2 once any BJT is exercised
near its Early voltage. Currently unverified end-to-end (no BJT-using
task has been simulated), but the pattern is identical.

## Proposed fix approach

Add a top-level switch `NGSPICE_COMPAT` (default 0) at the top of
`autohv_bicmos180_case_models.inc` and gate every B-source / behavioral C
on it. When `NGSPICE_COMPAT=1`, each behavioral element collapses to a
benign passive (short, tiny linear cap, tiny resistor). When 0, the
original high-fidelity expression is used and Qucs-S keeps its current
behavior.

Sketch for the resistor case:

```spice
.param NGSPICE_COMPAT=0

# inside RPOLY_HI subckt — replace the existing BVCR line with:
BVCR mid n V={ (1-NGSPICE_COMPAT) * V(p,mid)*(VCR1*sqrt(V(p,n)*V(p,n)+1e-6) + VCR2*V(p,n)*V(p,n)) }
```

If multiplying the expression by zero still doesn't satisfy ngspice (some
ngspice versions still walk the expression tree even when the outer term
is 0), the safer fallback is to branch the **element type** itself, which
requires a small subckt restructure — duplicate the subckt body inside an
`.if`/`.elseif` (ngspice supports `.if`/`.elseif`/`.endif` at netlist
scope) or split into two subckts and pick one via a top-level
`.if (NGSPICE_COMPAT==1) .include rpoly_ngspice.inc .else ... .endif`.

For the `Vshift` mismatch source (#3), the simplest ngspice-clean
substitute is a 1 mΩ series resistor — it carries the same gate current
without the singular-matrix problem, and the 1 mΩ drop is negligible
versus any real signal. Gate this on `NGSPICE_COMPAT` so Qucs-S keeps the
ideal-VSRC form when MM is on.

## What's already been verified

In a parallel task workspace I'm shipping a sed-patched copy of this
`.lib` with these three substitutions:

```
s|^BVCR mid n V=.*|BVCR mid n V=0|
s|^Cextra p n C=.*|Cextra p n 1e-18|
s|^Vshift g g_int DC {-DVTH_MM}|Rshift g g_int 1e-3|
```

That patch lets ngspice converge on a high-side level-shifter test deck.
It's hacky (drops the modeling fidelity unconditionally) and only covers
the subcircuits that task happens to use, but it confirms the **failure
modes are exactly the four listed above** and that linearizing them fixes
ngspice. The proper PDK-level fix should preserve the Qucs-S
behavior under a switch.

## Verification protocol

After your changes, smoke-test in **both** simulators using a minimal
deck that touches one of each problem class. Put this at
`tests/smoke_ngspice.spice` (create the directory) and confirm ngspice
runs it to completion without `Timestep too small` or `singular matrix`
errors when `NGSPICE_COMPAT=1`:

```spice
* ngspice-compat smoke test
.include "autohv_bicmos180_case.lib"
.param case=0 PROC_ON=0 MM_ON=0 NGSPICE_COMPAT=1

V1 vdd 0 5
V2 in  0 PULSE(0 5 100n 1n 1n 500n 1u)

* Class 3: HV LDMOS with mismatch Vshift collapsed
XN1 d1 in 0 NDMOS200 W=40u L=8u
R1  vdd d1 100

* Class 1: resistor VCR collapsed
XR1 vdd n2 RPOLY_HI L=100u W=2u

* Class 2: capacitor VCC collapsed
XC1 n2 0 CMIM_STD L=20u W=20u

.tran 1n 2u
.print tran V(d1) V(n2)
.end
```

Then re-run the same deck with `NGSPICE_COMPAT=0` in Qucs-S to confirm
the original behavior is unchanged. If you have BJT test coverage,
extend the smoke deck with an `NPN_LV` instance.

## Out of scope

- The supplied `circuits/hv_charge_pump/hv_up_lvlsh/levelshifter.spice`
  reference design has a separate, unrelated issue: under default sizing
  its mirror+delay-cell reset path doesn't reliably toggle the latch in
  both directions across all corners in ngspice. That's a topology /
  sizing problem, not a PDK problem — ignore it for this handoff.
- `autohv_bicmos180_case_models.inc`'s `Bavl` BJT avalanche, `agauss(...)`
  process-stat params, and the `_isTT`/`_isFF` one-hot corner selector
  are all fine and should not be touched.

## Open question for you to decide

Should `NGSPICE_COMPAT` default to 0 (preserve current Qucs-S users,
opt-in for ngspice) or to 1 (preserve ngspice users, opt-in for Qucs-S
high-fidelity)? My recommendation is **default 0** because the existing
Qucs-S users haven't been notified, but flag this back to the PDK owner
before shipping.
