# PDK handoff: HV-cascode mismatch-shift element causes a singular matrix when the gate node is driven by a real network

**Models affected:** `NDMOS200`, `PDMOS200` (in `autohv_bicmos180_case.lib`). The same
`Vshift`/`g_int` pattern is also used in `NMOS50`/`PMOS50`, but those have not been observed to
trigger the failure (their gates are not tied to a shared, externally-driven bias node).

**Requested by:** the level-shifter eval task (`xqmfaf10`). Not blocking that task's current
shipment (we are shipping without the affected feature), but it blocks a realistic enhancement
and is the root cause of intermittent convergence "cliffs" — so worth fixing in the PDK.

---

## Symptom

When the **gate terminal of an `NDMOS200`/`PDMOS200` is tied to a bias node that is NOT a
perfectly stiff ideal voltage source** — e.g. a supply pin fed through a series resistor, an
RC decoupling network, or driven by a real CMOS driver — ngspice reports:

```
Warning: singular matrix:  check nodes v.x1.xn5.vshift#branch and v.x1.xn6.vshift#branch
Warning: spice3 gmin stepping failed
Warning: source stepping failed
Note: Transient op started
Note: Transient op finished successfully
doAnalyses: TRAN: Timestep too small ... : trouble with node "..."
run simulation(s) aborted
```

- With `method=gear` (tighter, hardened solver) the run **aborts**.
- With `method=trap` (looser default) it **limps through but the operating point is corrupted** —
  e.g. an average supply current measured as `-25.9 A` (physically impossible). So results are
  silently wrong, not just failed.

This same fragility is the most likely root cause of **intermittent convergence cliffs** in the
level-shifter task: certain off-nominal designs (weak leg switch, gate near the droop boundary)
score `0` (hard-gate sentinel) on the deployed Linux ngspice build but compute fine locally —
i.e. the op-point is on a knife-edge that resolves differently across ngspice builds.

## Root cause

The Vth-mismatch shift is injected as a **0 V behavioral voltage source in series with the
gate**:

```spice
.subckt NDMOS200 d g s params: W=10u L=8u M=1 ZVTH=0
  ...
  .param DVTH_MM={MM_ON*(0.011/3.0)*ZVTH/sqrt(max(mtot,1e-6))}
  Vshift g g_int DC {-DVTH_MM}        ; <-- 0 V source when MM_ON=0
  Rgmin  g g_int 1e9                  ; <-- existing mitigation (see below)
  Rdrift d dd {RDRIFT}
  M0 dd g_int s NDMOS200_INT m={mtot}
.ends
```

When `MM_ON=0` (every nominal / PVT / CMTI run — i.e. almost all sims), `DVTH_MM = 0`, so
`Vshift` is a **0 V source**. Its branch current (`vshift#branch`) is an extra matrix unknown
fixed only by KCL at the internal gate node `g_int`, which connects to nothing but the MOSFET
gate (a capacitance, no DC path) and this 0 V source. That row is well-conditioned **only**
because the external gate node `g` is normally a perfectly stiff ideal source (`Vvdd VDD 0`),
which pins `g` and therefore `g_int`. Put any finite impedance on `g` (series R, decap, real
driver) and the `g_int`/`vshift#branch` subsystem becomes ill-conditioned → singular matrix.

## The existing mitigation is insufficient

A prior fix already added `Rgmin g g_int 1e9` with the comment *"gmin shunt: breaks the singular
matrix when MM_ON=0 (DVTH_MM=0V) for cascoded LDMOS."* That 1 GΩ shunt (conductance 1e-9 S,
i.e. the same order as the default `gmin`) is enough when `g` is a stiff source, but **not**
enough once `g` is driven through a real network — the cascoded case with two such devices
sharing the driven gate node still goes singular (reproduced below).

## Reproduction (minimal)

Instantiate the level-shifter core with its HV-cascode gates (`XN5`/`XN6`, gate = `VDD`) and
drive `VDD` through anything other than a stiff source. Any one of these triggers it:

1. **Series R:** `Vvdd VDDSRC 0 PWL(...)` + `Rvdd VDDSRC VDD 100` (VDD pin behind 100 Ω).
2. **Decap:** add `Cvdd VDD 0 10p` (and especially the PDK `CMIM_STD` subckt — its behavioral
   voltage-coefficient sub-element `Cextra` additionally collapses the timestep on an active node).
3. **Real driver:** drive the leg-switch inputs with `BUFFER` instances powered from `VDD`
   instead of ideal `Von`/`Voff` sources.

All three abort (Gear) or corrupt the op-point (trap) with the `vshift#branch` singular matrix.

## Suggested fixes (in order of preference)

1. **Eliminate the series source — apply the shift via the model's Vth-offset parameter.**
   BSIM3/4 expose `delvto` (a.k.a. `delvt0`) for exactly this. Set it on the `M0` instance:
   `M0 dd g s NDMOS200_INT m={mtot} delvto={-DVTH_MM}` and delete `Vshift`/`g_int`/`Rgmin`
   entirely. No series gate source → no `vshift#branch` unknown → no singularity, and the gate
   connects directly to `g`. This is the clean fix and removes the `Rgmin` kludge.
2. **If the shift must stay as a source,** strengthen the conditioning so it survives a non-stiff
   gate node: lower `Rgmin` from `1e9` to ~`1e6`–`1e7` (still negligible leakage at these bias
   currents), or add an explicit gmin from `g_int` to a fixed node. Verify across the
   reproduction cases above, not just the stiff-source case.

## Verification criteria for the fix

- **Nominal metrics unchanged:** with `MM_ON=0`, the level-shifter reference design's metrics
  (propagation delays, slew, currents, droop/overshoot, CMTI) must be byte-identical (or within
  rounding) before vs. after the change — the fix must be electrically transparent at nominal.
- **Mismatch still works:** with `MM_ON=1` and a nonzero `ZVTH`, the device's effective Vth must
  shift by the same `DVTH_MM` as today (confirm the MC `t_prop_mc` spread is preserved).
- **Robust under real VDD loading:** the level-shifter sim must run to completion (no singular
  matrix, no timestep collapse) with each of the three reproduction cases above, under both
  `method=trap` and `method=gear reltol=1e-3`.
