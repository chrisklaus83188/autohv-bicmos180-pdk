# Deterministic mismatch corners: `MM_SIGMA`

This PDK supports a deterministic alternative to Monte Carlo mismatch
analysis: a per-instance parameter `MM_SIGMA` that snaps a device's
mismatch parameters to a specified σ-multiple instead of drawing
randomly from `AGAUSS`. This document covers what it is, how to use
it, and the caveats that matter for valid sign-off.

## 1. Concept

Each device subckt in the lib has historically used `AGAUSS` to inject
per-instance mismatch into Vth, W/L, AREA, sheet R, or cap density. By
HSPICE convention `AGAUSS(0, X, 3)` truncates at ±X (where X is the
3-σ bound), so the true 1-σ value is X / 3 (verified empirically on
ngspice 45.2 in Phase E).

`MM_SIGMA` adds a deterministic term to each mismatch expression:

```
DVTH_MM = MM_ON*AGAUSS(0, X, 3)/scale + MM_SIGMA*X/3/scale
```

- `MM_SIGMA = 0` (the default): the deterministic term is 0, behavior
  is identical to before. Use this for `MM_ON=1` Monte Carlo runs.
- `MM_SIGMA = +3`: the parameter lands at exactly +X / scale = the
  +3-σ bound. Same as the worst-case extreme of an AGAUSS draw.
- `MM_SIGMA = +1`: parameter lands at the +1-σ value.
- `MM_SIGMA` can be any real number — the form is linear in σ-units,
  so sensitivity sweeps (e.g. `.step MM_SIGMA -3 3 0.5`) work natively.

## 2. The intended flow

```
1. Identify the metric you care about (offset, gain mismatch, settling).
2. One-at-a-time sensitivity scan: set each device's MM_SIGMA to ±3
   individually, with all others at 0. Record the sign of the metric
   change for each device. That tells you which sign worsens the metric.
3. Compose the worst-case pattern: set every device to the sign that
   maximises the metric in the bad direction. This is your worst-case
   deterministic corner.
4. Lock the pattern as your testbench's permanent corner suite for
   day-to-day iteration and PR-gating CI.
5. Periodically (at release boundaries) run the Phase E MC harness for
   statistical confidence (catches quadratic / unexpected modes).
```

This flow gives you fast deterministic CI iteration plus periodic
statistical validation, which is the standard practice for analog
design at this kind of complexity.

## 3. Important: set `MM_ON=0` when using `MM_SIGMA`

`MM_ON` and `MM_SIGMA` are independent terms in the expression; if you
set both, you get the sum of a random draw AND a deterministic shift,
which doesn't represent anything physical. The four valid combinations:

| `MM_ON` | `MM_SIGMA` | Meaning |
|---------|------------|---------|
| 0 | 0 | No mismatch. Default. |
| 1 | 0 | Random MC (existing Phase E harness, AGAUSS-driven). |
| 0 | ±k | Deterministic corner at ±k σ on every instance that sets `MM_SIGMA=±k`. |
| 1 | ±k | **Don't do this**. Sum of random + deterministic; not a meaningful condition. |

In practice: when you're using `MM_SIGMA`, set `.param MM_ON=0` at deck
scope. When you're running MC, leave `MM_SIGMA=0` (i.e., just don't
pass it on the X-lines).

## 4. Canonical patterns

### Differential pair (worst-case input offset)

```spice
.param MM_ON=0
* Worst case: matched devices shifted in OPPOSITE directions.
XM1 d1 g1 s b NMOS50 W=100u L=2u MM_SIGMA=+3
XM2 d2 g2 s b NMOS50 W=100u L=2u MM_SIGMA=-3
```

The input offset is `(gm/ID) * 2 * X / 3 / sqrt(W*L_um²)` — the pair
difference is `+X − (−X) = 2X` in 3-σ units.

### Simple current mirror (worst-case ratio error)

```spice
.param MM_ON=0
* Worst case: reference shifts up, all outputs shift down.
XM_REF c c 0 b NMOS50 W=100u L=2u MM_SIGMA=+3
XM_O1  o1 c 0 b NMOS50 W=100u L=2u MM_SIGMA=-3
XM_O2  o2 c 0 b NMOS50 W=100u L=2u MM_SIGMA=-3
```

Each output current's ratio error is bracketed by the gm/ID times the
σ on each leg of the mirror.

### Cascoded current mirror

```spice
.param MM_ON=0
* Mirror pair + cascode pair, each pair shifted opposing.
XM_REF c c x b NMOS50 W=100u L=2u MM_SIGMA=+3
XM_OUT o c y b NMOS50 W=100u L=2u MM_SIGMA=-3
XC_REF x b1 0 b NMOS50 W=100u L=1u MM_SIGMA=+3
XC_OUT y b1 0 b NMOS50 W=100u L=1u MM_SIGMA=-3
```

Note: the cascode pair's contribution to output current error is
typically much smaller (cascode boosts output impedance, not gm), so
this corner is dominated by the mirror pair shift.

### Source follower / level-shifter cascode chain

A long chain of cascoded NMOS with a single gate-drive node: each
device's Vth shift contributes to the cumulative gate-drive headroom
needed. Worst case for SOA on the top device:

```spice
.param MM_ON=0
XM1 d1 gd  0  b NMOS50 W=100u L=2u MM_SIGMA=+3   ; bottom
XM2 d2 gd d1  b NMOS50 W=100u L=2u MM_SIGMA=+3   ; mid
XM3 d3 gd d2  b NMOS50 W=100u L=2u MM_SIGMA=+3   ; top -- needs most headroom
```

All `+3` (all Vth high) maximises the gate-drive headroom requirement
on the top device. Sensitivity scan (step 2 of the flow) confirms the
sign is the same for all instances on this metric.

### Sensitivity sweep on a single device

```spice
.param MM_ON=0
.param SCAN=0
XM1 d g s b NMOS50 W=100u L=2u MM_SIGMA={SCAN}
... rest of testbench ...
.dc Vin <range>
.step SCAN -3 3 0.5
.meas dc offset find v(d) when v(in)=0.5
```

Watch the `offset` measurement as `SCAN` sweeps. The slope at `SCAN=0`
is `(metric_sensitivity to that device's σ)`. Sign of slope = direction
of `MM_SIGMA` that worsens the metric.

## 5. Caveats

These caveats determine when the deterministic flow is sufficient and
when you should fall back to MC.

### 5.1. Joint-σ probability is much rarer than per-device σ

Setting N devices simultaneously to ±3-σ is a (3σ)ᴺ corner in joint
probability space — vastly rarer than the per-device 0.27 %. For 10
devices this is ~10⁻²⁵ — well below any meaningful yield target. Two
ways to interpret this:

- For **bracketing worst case** (the usual use): the deterministic
  corner is *more pessimistic* than any practical yield target, so if
  your circuit passes the corner, you've over-bounded. That's fine.
- For **estimating yield**: the corner doesn't directly correspond to a
  probability you can multiply with anything else. Use MC for yield
  numbers.

Some designers prefer ±2-σ for joint corners (probability ≈ 4.6 % at
3 devices, more realistic) and reserve ±3-σ for single-device sanity.

### 5.2. Linear sensitivity assumption

A ±3-σ shift extrapolates linearly along one mismatch axis. For
metrics dominated by linear small-signal sensitivity (input offset,
gain mismatch, CMRR, low-frequency PSRR), the corner result is tight.

For metrics with non-trivial higher-order dependence — distortion,
settling near switching thresholds, headroom near saturation — the
linearized corner can be optimistic *or* pessimistic vs. full MC by a
meaningful margin.

**Rule of thumb**: corners are accurate for small-signal DC; degrade
for large-signal transient. If transient settling or HV switching SOA
is part of your spec, validate with MC at the release boundary.

### 5.3. Sensitivity sign can flip with operating point

A device that contributes +sensitivity at the nominal bias may
contribute −sensitivity in the triode region, near a switching
threshold, or under different supply conditions. The sensitivity scan
(step 2) needs to be re-done at each operating condition you care
about. For a level shifter that means re-running at multiple points of
the supply ramp, not just at the final operating point.

If you find that the worst-case sign pattern is different at different
operating points, your testbench corner suite needs *multiple* corner
patterns covering the union, not just one.

### 5.4. PROC and MM are independent axes

`MM_SIGMA` only affects per-instance mismatch (the local
component). Global process variation is on a separate axis, controlled
by the 5 named corners (`case=0..4`) and the `PROC_ON` flag. Worst case
is the product space:

- 5 process corners × N MM corner patterns

For most analog designs the cross-product is too large to test
exhaustively. Standard practice:

- Test all MM corners at TT (case=0), validate worst-case mismatch.
- Test FF and SS process corners with `MM_ON=0, MM_SIGMA=0` (no
  mismatch), validate worst-case process.
- Cross-check the few combinations you suspect will be marginal
  (typically SS process + worst-case mismatch on offset-sensitive
  circuits).

### 5.5. AGAUSS still gets evaluated when `MM_SIGMA ≠ 0`

The expression form is `MM_ON*AGAUSS(...) + MM_SIGMA*X/3/scale`. Even
when `MM_SIGMA = +3` and `MM_ON = 0`, the `AGAUSS(...)` call is still
evaluated (its result then multiplied by 0). This consumes an AGAUSS
draw from the underlying RNG per instance.

For pure deterministic corner sims this doesn't affect correctness or
results (the draw goes to 0). It does mean you can't perfectly inter-
leave corner sims and MC sims in one deck and expect bit-exact MC
sequence reproducibility — the corner sims will perturb the draw
sequence. In practice this is irrelevant because you run corners and
MC in separate deck invocations anyway.

## 6. When to use corners vs. MC

| | **MM_SIGMA corners** | **MC harness (Phase E)** |
|---|---|---|
| Speed | One sim per corner. Seconds. | N iterations (typically 100-1000). Minutes-hours. |
| Determinism | Bit-exact reproducible. | Time-seeded; reproducible only with explicit seed handling (not currently supported). |
| CI gating | Suitable. Pass/fail is deterministic. | Not suitable. Statistical noise on N=200. |
| Bounds linear sensitivity | Yes (the bracketing extrema). | Yes (with tolerance for σ estimation). |
| Captures quadratic / non-linear effects | Approximate. | Yes. |
| Reveals unexpected modes | No (you'd have to suspect them and test). | Yes (by design — random sampling covers the space). |
| Yield estimation | No. | Yes. |

The standard split: **corners every commit, MC at release boundaries**.

## 7. How the mechanism is implemented

For reference, here's the form used in each device subckt.

**BSIM3 MOS** (8 devices: NMOS/PMOS 12/18/33/50):
```
.param DVTH_MM = MM_ON*AGAUSS(0, X/sqrt(AUM2+1e-12), 3)
              + MM_SIGMA*X/3/sqrt(AUM2+1e-12)
```
Same form for DWREL_MM and DLREL_MM (one MM_SIGMA, three params).

**VDMOS** (13 devices: NDMOS/PDMOS 20/40/60/80/120/200, DNMOS20):
```
.param DVTH_MM = MM_ON*AGAUSS(0, X, 3)/sqrt(max(mtot,1e-6))
              + MM_SIGMA*X/3/sqrt(max(mtot,1e-6))
```
Single DVTH_MM term; subckt then applies it via the Vshift VSRC.

**BJT and Diode** (10 devices: NPN_LV/HV, PNP_LAT/HV, DIO_*, DZ_*):
```
.param AREAEFF = AREA*(1 + MM_ON*AGAUSS(0, 0.012/sqrt(AREA+1e-12), 3)
                          + MM_SIGMA*0.012/3/sqrt(AREA+1e-12))
```
Effective AREA is multiplied by 1 + δ, where δ is the mismatch.

**Behavioral resistor** (5 devices: RPOLY_HI/LO, RNWELL, RNPLUS, RPPLUS):
```
.param RMM = 1 + MM_ON*AGAUSS(0, X/sqrt(AUM2+1e-12), 3)
               + MM_SIGMA*X/3/sqrt(AUM2+1e-12)
```
Resistance is multiplied by `RMM`.

**Behavioral capacitor** (4 devices: CMIM_STD/HI, CMOM, CFRINGE):
```
.param CMM = 1 + MM_ON*AGAUSS(0, X/sqrt(AUM2+1e-12), 3)
               + MM_SIGMA*X/3/sqrt(AUM2+1e-12)
.param LS  = sqrt(CMM)
```
Capacitance scales as `CMM`; linear dimensions scale as `sqrt(CMM)`.

The X value (3-σ bound) varies by device class. See the lib for
specific values per device.

## 8. Regression coverage

`pdk_validation/regression/transients/mismatch_corner.cir` exercises
the mechanism end-to-end: two NMOS50 in saturation at MM_SIGMA=±3 with
MM_ON=0, asserts that `log(I1/I2)` matches the analytic prediction
within ±10 %. This catches any future regression in the deterministic
term computation.

Smoke (Phase A) and the Phase E MC harness both run unchanged with
`MM_SIGMA=0` default, confirming backward compatibility on every CI
run.
