# Handoff: 12 V refit landed; A_VT ladder derived; three rulings needed

**Responds to:** rulings Y1–Y2
**Branch:** `mc-realism` @ `da7e359`, pushed. Netlist blob `f48f4dd`.
**Date:** 2026-09-18
**Status:** The 12 V card refit is committed. The `A_VT` ladder is derived from RDF theory and the
constant comes out remarkably stable — but it misses the plausibility band by ~2×, and that
disagreement is a real physics question, not a bookkeeping one. Stopped for three rulings rather
than guess at any of them.

---

## 1. Two predictions of mine that were wrong

**The Idsat attribution, twice.** I pre-registered the 12 V refit as moving Idsat ≈ 0 %, "because
`k1` only touches the body-bias term". It moved **−6.0 %**. I then corrected that to `k2` — which
the card diff refutes on sight, because **NMOS12's `k2` was already −0.03 and never changed**, yet
its Idsat moved the full −6.0 %.

Reverting **one** parameter at a time settles it:

| reverted | NMOS12 Idsat | PMOS12 Idsat |
|---|---|---|
| `k1` alone | **0.0 %** (exactly restores 1.854488e-03 / 8.652385e-04) | **0.0 %** |
| `k2` alone | −6.0 % (i.e. no effect) | −6.0 % |
| `voff`, `nfactor`, `cj`/`cjsw` each | −6.0 % (no effect) | −6.0 % |

So the mover is **`k1`**, via BSIM3's bulk-charge factor `Abulk`, which acts at Vbs = 0. Confirmed
by the operating-point split: at Vgs = 12 V, saturation (Vds = 12 V) moves −6.0 % while the linear
current (Vds = 0.1 V) moves only **−0.9 % (N) / −1.1 % (P)**. A threshold shift moves both alike; a
bulk-charge effect moves saturation and barely touches linear.

**The body effect.** "Body effect = γ(nch)" is met **in the declared parameter, not exactly in the
measured ΔVth** — the realized `k1_eff` is **94 % (N) / 98 % (P)** of declared on a long device
(W 50 µm, L 10 µm). `dvt0` accounts for the geometry-dependent part (disabling it moves implied
`k1_eff` 1.383 → 1.465, and the long device independently reproduces 1.463); `k3` and `toxm`
account for none. The rest is BSIM3 evaluating `√(φs − Vbs)` against my closed form's
`√(2φ_F + Vsb)`. Stated plainly in the commit rather than glossed.

## 2. The 12 V refit, landed (`da7e359`)

| | NMOS12 | PMOS12 | target |
|---|---|---|---|
| `k1` | 0.750 → **1.552** | 0.820 → **1.715** | γ(nch, 31 nm) |
| `k2` | −0.03 → −0.03 (**no change**) | −0.04 → **−0.03** | X2 |
| `nfactor` | 1.7000 → **1.0625** | 1.8500 → **0.9713** | — |
| `voff` | −0.0700 → **−0.1544** | −0.0800 → **−0.2015** | — |
| `cj` | 0.0014 → **0.0012124** | 0.0015 → **0.001329** | card-`nch` basis (Y1) |
| `cjsw` | 1e-10 → **8.66e-11** | 1e-10 → **8.86e-11** | card-`nch` basis (Y1) |
| slope | 152.8 → **120.9** mV/dec | 170.2 → **124.4** | 120 ± 10 |
| weak-inv Id | 98 % of before | 100 % | ≥ 90 % |
| ΔVth @ Vsb 5 V | 0.825 → **2.090 V** | 0.910 → **2.406 V** | ≈ γ(nch) |
| Idsat | **−5.7…−6.3 %** (cases 0–4) | same | within 10 % |

Note the `k2` row against my last handoff: I reported it as a uniform "0.0 → −0.03". Both cards
actually carried a **byte-copy of their 5 V counterpart** (NMOS50 −0.03, PMOS50 −0.04), and
NMOS12's copy already equalled the declared value. Only PMOS12 moved. PMOS12 lands at 124.4 mV/dec
per Y2 (accepted rather than over-fitted toward 120).

`anchor-values.json` 12 V `subthreshold_swing`: 72–96 `industry` → **110–130 `autohv-derived`**.
`stat-model.md` now scopes the rule: **`k1` for channel depletion charge, `nch` for junction
quantities.**

## 3. The A_VT ladder, derived rather than fitted

`A_VT(RDF) = (q/C_ox)·√(N_a·W_dep/3)`, with `W_dep` self-consistent and `N_a` from each card's own
`k1`. That collapses to `A_VT = c·√(t_ox[nm]·k1)` with `c` a pure constant — **computed, never
fitted**. Inflated for non-RDF sources by `A_total = A_RDF/√(RDF fraction)`, fraction 0.65.

| card | t_ox nm | `k1` | N_a cm⁻³ | W_dep nm | **A_VT derived** | in JSON today | band lo / target / hi | in band? |
|---|---|---|---|---|---|---|---|---|
| NMOS18 | 4.25 | 0.560 | 6.237e17 | 43.9 | **2.336** | 4.60 | 2.12 / 4.25 / 6.38 | yes |
| PMOS18 | 4.25 | 0.630 | 7.893e17 | 39.3 | **2.486** | 3.85 | 2.12 / 4.25 / 6.38 | yes |
| NMOS33 | 6.75 | 0.620 | 3.031e17 | 61.7 | **3.066** | 6.17 | 3.38 / 6.75 / 10.12 | **no** |
| PMOS33 | 6.75 | 0.700 | 3.863e17 | 55.0 | **3.269** | 5.14 | 3.38 / 6.75 / 10.12 | **no** |
| NMOS50 | 11.00 | 0.680 | 1.373e17 | 89.5 | **4.051** | 6.89 | 5.50 / 11.0 / 16.5 | **no** |
| PMOS50 | 11.00 | 0.780 | 1.806e17 | 78.7 | **4.357** | 5.63 | 5.50 / 11.0 / 16.5 | **no** |
| NMOS12 | 31.00 | 1.552 | 9.004e16 | 109.1 | **10.207** | 15.03 | 20.0 / 31.0 / 35.0 | **no** |
| PMOS12 | 31.00 | 1.715 | 1.099e17 | 99.3 | **10.763** | 12.07 | 20.0 / 31.0 / 35.0 | **no** |

**The strong result:** `c` comes out **1.4716…1.5191, constant to 3.18 %** (mean **1.4940**
mV·µm/√nm) across oxides spanning 4.25→31 nm and dopings spanning 9e16→7.9e17. That near-constancy
is the validation of V2's `N_a^{1/4}` form — a wrong exponent would drift `c` systematically with
`t_ox`, and it does not. The values are entirely ours: they replace an ONC25-anchored ladder
(3.85→15.03) with one generated from our own cards.

**The problem:** the derived ladder is ~0.5 mV·µm per nm of `t_ox` against bands built on a
`1 mV·µm/nm` rule. Six of eight land below `lo`.

### 3.1 A fitted `c` *is* feasible — I was wrong to imply otherwise

Solving `lo ≤ c·√(t_ox·k1) ≤ hi` across all eight cards:

> **a single fitted `c` ∈ [2.883, 3.899] satisfies every band** (midpoint 3.391), bound below by
> NMOS12 and above by PMOS18.

So V2's fitted route works. The derived constant sits **1.93×–2.61× below** that window.

### 3.2 What the gap actually means

The two laws differ in *slope* as well as scale: the band rule is linear in `t_ox`, RDF gives
`A_VT ∝ t_ox·N_a^{1/4}`, and since `N_a` falls 6.9× as `t_ox` rises across our ladder, the
derived/target ratio degrades **0.550 (NMOS18) → 0.329 (NMOS12)**.

To lift the derived `c` into the feasible window, the **RDF variance fraction would have to be
9.5–17.5 %, not 65 %.**

That is the crux. **Three propositions cannot all hold:**

1. RDF dominates Vth mismatch (~65 % of variance) — the standing assumption;
2. the Stolk/Mizuno closed form `(q/C_ox)·√(N_a·W_dep/3)`;
3. the `1 mV·µm/nm` plausibility band.

I verified (2) is implemented correctly — hand-check at t_ox 4 nm, N_a 6e17 reproduces
W_dep 44.7 nm and A_RDF 1.75 mV·µm independently. So the tension is real, not an arithmetic slip.

---

## 4. Rulings needed

**Z1 — derived `c` or fitted `c`?** V2 says fit `c` "so the ladder lands in the plausibility band";
the later handoffs say take `c` "from the RDF expression". I have done the second and it misses the
band ~2×. **My recommendation: keep derived `c` = 1.494 and re-examine the band instead.** The band
is tagged `industry` with basis "A_VT ~ 1 mV·µm per nm of tox (±50 %)" — a rule of thumb that ruling
G1 already overrode once on the grounds that a measured coefficient outranks a foundry's own
rule-of-thumb footnote. A derived constant that holds to 3.18 % across four oxide classes is
stronger evidence than a ±50 % rule. But if you prefer the fitted route, `c` = 3.391 is the
band-feasible midpoint and I'll apply it with `source: autohv-fitted`.

Note the alternative I am *not* proposing: quietly raising the RDF fraction to ~15 % to make the
derivation hit the band. That would be fitting while calling it deriving.

**Z2 — VDMOS gate oxide: 13 nm or 11 nm?** My task list says "VDMOS doping at AutoHV's **11 nm**".
But `docs/process-declarations.md` **D2 is `[ruled]`: 13 nm flat across drain classes**, and
`CHANGELOG.md` records `kp`, caps, `theta` and `ksubthres` **already re-derived at 13 nm**. I think
"11 nm" was my own shorthand for *our 5 V card's oxide is 11 nm, where the reference process uses
13* — which would make VDMOS follow our own process and serve the uniqueness constraint. But that
re-opens a ruled declaration and invalidates four sets of card values, so I have not touched it.
VDMOS cards carry **no `t_ox` and no `k1`**, so `c·√(t_ox·k1)` cannot be evaluated for them at all
until this is settled; `kp = µ·C_ox` is the route to `C_ox` once the oxide is fixed.

**Z3 — scope for removing ONC25 content.** `models/stat_model.json` carries **28 ONC25
references**, several quoting measured values verbatim: section E/GG `A_VT` anchors, section HH Vth
bands, per-class Idsat bands, poly/well/diffusion tolerances. Under the "not ours to copy"
constraint these should all become AutoHV-derived. The `A_VT` block is ready to replace now. Do you
want (a) `A_VT` only in this commit, or (b) a single pass replacing all 28? I'd suggest (a) now and
(b) as its own reviewed change, since each remaining anchor needs its own derivation method.

## 5. Queued behind these

`σ(VTH)` per U5 via `k1` (depends on Z1's coefficient); plausibility booleans as a local script
emitting only `{within_band, band}`; re-measure all 40 directions; rebuild `corners.json`;
**Stop A′**.
