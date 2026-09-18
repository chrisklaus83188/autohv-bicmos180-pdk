# Handoff: §6 channel-doping extraction — 7 of 8 cards fail self-consistency

**Responds to:** the U1–U5 rulings reply, §6 addendum
**Branch:** `mc-realism` @ `5591dcb`
**Date:** 2026-09-17
**Status:** §6 step 1–2 done, and the answer is not the clean one. Step 3 (report as a card defect,
resolve from the measured body effect) is triggered on 7 of the 8 BSIM3 cards, so it is the rule
here rather than the exception. Four questions, V1–V4. No model file changed yet.

## 1. What the cards say

`Na_k1 = (k1·C_ox)² / (2·q·ε_si)`, `C_ox = ε_ox/tox`, compared against the card's own `nch`:

| card | tox nm | k1 | vth0 | `nch` cm⁻³ | `Na(k1)` cm⁻³ | ratio | literature window |
|---|---|---|---|---|---|---|---|
| NMOS18 | 4.25 | 0.5600 | 0.480 | 2.2e17 | 6.24e17 | **2.83** | above 2–5e17 |
| PMOS18 | 4.25 | 0.6300 | −0.520 | 2.5e17 | 7.89e17 | **3.16** | above |
| NMOS33 | 6.75 | 0.6200 | 0.660 | 1.7e17 | 3.03e17 | 1.78 | above 1–3e17 |
| PMOS33 | 6.75 | 0.7000 | −0.740 | 1.9e17 | 3.86e17 | **2.03** | above |
| NMOS50 | 11.00 | 0.6800 | 0.880 | 1.2e17 | 1.37e17 | 1.14 | **in window** |
| PMOS50 | 11.00 | 0.7800 | −0.980 | 1.4e17 | 1.81e17 | 1.29 | above 5e16–1.5e17 |
| NMOS12 | 31.00 | 0.7500 | 1.350 | 9e16 | 2.1e16 | **0.23** | below 3–8e16 |
| PMOS12 | 31.00 | 0.8200 | −1.550 | 1.1e17 | 2.51e16 | **0.23** | below |

Two distinct failure modes, not one:

- **LV and mid classes (1.8 / 3.3 / 5 V):** `k1` implies 1.1–3.2× *more* doping than `nch` states.
  Only NMOS50 passes both the 2× ratio test and the window.
- **12 V pair:** `k1` implies 4× *less* doping than `nch` states — the opposite direction, and
  `Na(k1)` falls below the window while `nch` sits inside it.

## 2. `nch` is not decorative — the cards are internally inconsistent

I previously described `nch` as possibly decorative because ngspice warns *"nsub is ignored because
k1 or k2 is given"*. That is true of `nsub`, but **not** of `nch`: in BSIM3, `nch` sets the surface
potential `φ_s` and the built-in voltage, while `k1` sets the body-effect coefficient directly. Both
are live, and they are being fed two different dopings.

So this is not a question of which parameter the simulator uses. It is that each card's implied
*depletion charge* (from `k1`) disagrees with its implied *surface potential* (from `nch`) — on
seven of eight cards, by up to 4×, in both directions.

## 3. A cleaner anchor for `A_VT` than either number

Pelgrom's coefficient is usually written `A_VT ∝ t_ox·√(q·N_a·W_dep)/ε_ox`. With a self-consistent
depletion width (`W_dm ∝ N_a^{-1/2}`), that reduces to

```
A_VT ∝ t_ox · N_a^{1/4}        and, substituting N_a from k1,        A_VT ∝ √(t_ox · k1)
```

which anchors `A_VT` on the coefficient the simulator actually uses for depletion charge, and
removes `nch` from the derivation altogether. It also means the doping ambiguity matters far less
than feared.

**Correction to the ruling's sensitivity note.** §6 states "`A_VT ∝ √Na`, so a 2× doping
uncertainty is 1.4× on `A_VT`". With the self-consistent depletion width it is `N_a^{1/4}`, so a 2×
doping uncertainty is **1.19×**, and the 4× disagreement on the 12 V pair is 1.41×. Both sit inside
the 0.5–2× plausibility band. The ruling's conclusion holds — oxide dominates — and holds more
strongly than stated. (If `W_dep` is instead held fixed, the √Na form and the 1.4× figure return;
which convention to use is V2.)

## 4. VDMOS

The VDMOS cards carry **no doping and no oxide parameter** — only `vto` and `kp`. So §6.5's
fallback applies: derive body doping from `VTO` and the oxide. Their thresholds:

| device | VTO | device | VTO |
|---|---|---|---|
| NDMOS20 | 1.00 V | PDMOS20 | −1.05 V |
| NDMOS40 | 1.05 | PDMOS40 | −1.10 |
| NDMOS60 | 1.10 | PDMOS60 | −1.15 |
| NDMOS80 | 1.15 | PDMOS80 | −1.20 |
| NDMOS120 | 1.20 | PDMOS120 | −1.25 |
| NDMOS200 | 1.25 | PDMOS200 | −1.31 |
| DNMOS20 | −1.60 (depletion) | | |

**One correction to U4.** It says to use "the 13 nm oxide" for the VDMOS derivation. 13 nm is the
*reference* process's 5 V oxide. AutoHV's own 5 V oxide is **11 nm**, and under the governing rule
the derivation must use ours. I will use 11 nm unless told otherwise (V3).

## 5. Questions

| # | question | my proposal |
|---|---|---|
| **V1** | Seven of eight cards are internally inconsistent between `k1` and `nch`. Which do we treat as the process truth, and does the loser get corrected? | Measure the body effect on each card (sweep `Vsb`, extract `dVth/d√(2φ_F+V_sb)`) and keep whichever parameter the card actually behaves like — that is §6 step 3, just applied eight times instead of once. My expectation is that `k1` wins, since it enters the body-effect term directly. If so, `nch` should be corrected to match on all eight cards and logged in the defaults audit next to `k3`, because a wrong `nch` also shifts `φ_s` and the built-in voltage. That is a second model change of the `k3` kind, so it needs your ruling, not mine. |
| **V2** | `A_VT ∝ t_ox·N_a^{1/4}` (self-consistent `W_dep`) or `∝ t_ox·√N_a` (fixed `W_dep`)? It changes the doping sensitivity from 1.19× to 1.41× per 2×. | Use the `N_a^{1/4}` form: `W_dep` is not fixed across four classes spanning 4.25–31 nm oxide and 2e16–8e17 doping. Anchor it as `A_VT = c·√(t_ox·k1)` with `c` fitted once so the ladder lands in the plausibility band, and record `c` as the single AutoHV-derived constant. |
| **V3** | VDMOS derivation oxide: AutoHV's 11 nm, not the reference's 13 nm. | Use 11 nm. Flagging it because U4 named 13 nm explicitly. |
| **V4** | The 12 V pair fails in the opposite direction to every other class, and its `nch` (not `Na(k1)`) is the one inside the window. | Suspect the 12 V cards were built by scaling a 5 V card without re-deriving `k1`. If the body-effect measurement confirms it, treat it as a card defect and report before deriving anything from it — it would otherwise propagate into `VTH_12`, `A_VT_12`, and the 12 V corner, which is already the weakest-grounded class. |

## 6. Next

On a ruling for V1: measure the body effect on all eight cards, settle the doping per class, then
derive `A_VT` and `σ(VTH)` per §2 of the rulings reply, populate the plausibility booleans from the
local check, re-measure the 40 directions, rebuild the corner table, and bring Stop A′.
