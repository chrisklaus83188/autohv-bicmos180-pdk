# Handoff: card self-consistency — baseline measured, §1.1's acceptance test cannot pass

**Responds to:** the V1–V4 rulings reply
**Branch:** `mc-realism` @ `cbea981`
**Date:** 2026-09-17
**Status:** §5 step 1 begun and then **stopped before changing anything**, because the §1.1
acceptance test fails by construction on the classes it governs. V4 is confirmed decisively. Two
questions, W1 and W2. No model file has been modified.

## 1. Baseline subthreshold slope, measured before any change

DC sweep at Vds = 0.1 V, W = 10 µm, L = 1 µm, linear fit of Vg against log₁₀(Id) over the
1e-12…1e-9 A decades (23–51 points per card), 27 °C.

| card | measured S | n | repo anchor band | tag | verdict today |
|---|---|---|---|---|---|
| NMOS1V8 | 77.6 mV/dec | 1.30 | 72–96 (target 80) | industry | in |
| PMOS1V8 | 80.7 | 1.35 | 72–96 | industry | in |
| NMOS3V3 | 85.6 | 1.44 | 72–96 | industry | in |
| PMOS3V3 | 89.6 | 1.50 | 72–96 | industry | in |
| NMOS5V0 | 96.6 | 1.62 | 85–100 (target 95) | **grounded** | in |
| PMOS5V0 | 104.3 | 1.75 | 85–100 | **grounded** | **out by 4.3** |
| NMOS12V | 152.8 | 2.56 | 72–96 | industry | **out by 57** |
| PMOS12V | 170.2 | 2.86 | 72–96 | industry | **out by 74** |

Anchors are from the repo's own `docs/anchor-values.json`.

## 2. W1 — the §1.1 acceptance window is unachievable as written

§1.1 requires that after setting `nch = Na(k1)`, the slope "stays inside 70–90 mV/dec for LV/mid
classes at 27 °C and moves by ≤ 15 %".

Three problems, in increasing order of seriousness:

1. **The window disagrees with the repo's own anchors.** The repo has 72–96 (industry) for
   1.8/3.3/12 V and **85–100 grounded** for the 5 V pair. The ruling's 70–90 is narrower than
   either, and the 5 V pair cannot satisfy both — its grounded target is 95.
2. **Two cards are already outside before any change**: PMOS5V0 by 4.3 mV/dec against its grounded
   band, and both 12 V cards by 57–74 against theirs.
3. **The correction pushes every card the wrong way.** Raising `nch` raises `C_dep`, and
   `n = 1 + C_dep/C_ox` with `C_dep ∝ √Na`, so the slope rises. Predicted analytically from the
   measured baseline and the known `Na(k1)/nch` ratios:

| card | ratio | S today | S predicted after | movement | vs ruling 70–90 | vs repo band |
|---|---|---|---|---|---|---|
| NMOS1V8 | 2.83 | 77.6 | ≈ 89.9 | +16 % | at the edge | in |
| PMOS1V8 | 3.16 | 80.7 | ≈ 97.1 | **+20 %** | **out** | **out** |
| NMOS3V3 | 1.78 | 85.6 | ≈ 94.3 | +10 % | **out** | in |
| PMOS3V3 | 2.03 | 89.6 | ≈ 102.3 | +14 % | **out** | **out** |
| NMOS5V0 | 1.14 | 96.6 | ≈ 99.1 | +3 % | **out** | in |
| PMOS5V0 | 1.29 | 104.3 | ≈ 110.3 | +6 % | **out** | **out** |

(Analytic prediction, not simulated — the real numbers will differ somewhat through `voff` and
`vth0` interplay, but the direction and rough size are not in doubt.)

So on the ruling's window, **six of six LV/mid cards fail**; on the repo's own bands, three fail
and three pass. Either way the escape clause in §1.1 — "if a card fails, `k1` is the defective one;
use the `nch`-implied `k1` instead" — would fire on most of the ladder, which would *lower* `k1` by
1.1–3.2× and change the body effect on six cards. That is a much larger designer-visible change
than the `nch` correction it was meant to guard.

I stopped here rather than apply a correction whose acceptance test I can predict will fail.

## 3. V4 confirmed: the 12 V `k1` is wrong, and by almost exactly the predicted factor

First principles, `γ = tox·√(2qε_si·Na)/ε_ox` using each card's own `nch` and 31 nm oxide:

| card | nch | γ(nch) | card `k1` | ratio | ΔVth at Vsb = 5 V, γ vs card |
|---|---|---|---|---|---|
| NMOS12V | 9.0e16 | 1.552 | 0.750 | **2.07** | 2.05 V vs 0.99 V — card understates by 1.06 V |
| PMOS12V | 1.1e17 | 1.715 | 0.820 | **2.09** | 2.26 V vs 1.08 V — understates by 1.18 V |

The ruling predicted ≈1.5 V^½ and roughly 2×; both land there. The measured subthreshold slope is
independent corroboration from a third direction: n ≈ 2.56–2.86 is what a high `C_dep` (high `nch`)
device does, so `nch` is the trustworthy parameter on these two cards, exactly as §1.2 concluded.

## 4. W2 — the 12 V `vth0` also fails its sanity check

§1.2 asked for a first-principles long-channel Vth within ±0.3 V of the card. Using each card's
`nch`, 31 nm oxide, and an n+/p+ poly gate assumption:

| card | first-principles Vth | card `vth0` | delta |
|---|---|---|---|
| NMOS12V | 2.12 V | 1.350 | **+0.77 V** |
| PMOS12V | −2.33 V | −1.550 | **−0.78 V** |

Outside the ±0.3 V window by more than 2.5×. Combined with §3 and the out-of-band slope, the 12 V
pair now has **three independently suspect parameters**: `k1`, `vth0`, and a subthreshold slope
60–75 % above its anchor.

## 5. Copy audit (§4 of the ruling)

22 of 59 shared parameters are byte-identical between the 12 V and 5 V cards:

```
NMOS12V vs NMOS5V0:  a0 af capmod cj cjsw ef elm em k2 kt1 level mobmod nfactor
                   noib noic noimod nqsmod tnom ute version voff wr
PMOS12V vs PMOS5V0:  same list, with ub identical instead of nfactor
```

`k2` is on that list, which §1.2 explicitly asked me to check: an identical `k2` sitting next to a
`k1` that is wrong by 2× is consistent with the scaled-copy theory. `voff` and `nfactor` being
identical also bear directly on the subthreshold slope, so they are not innocuous.

## 6. Questions

| # | question | my proposal |
|---|---|---|
| **W1** | §1.1's window (70–90 mV/dec, ≤ 15 % movement) cannot be met: six of six LV/mid cards fail it after the `nch` correction, and the repo's own anchors say 72–96 / 85–100 instead. | Use the repo's per-class anchors as the acceptance bands, and **cap the `nch` correction** at whatever keeps each class inside its own band, reporting the residual `k1`/`nch` disagreement as a recorded card defect rather than forcing one of them. That keeps both parameters' physics visible. The alternative — firing §1.1's escape clause and lowering `k1` on six cards — changes the body effect across the whole LV ladder and should not happen as a side effect of a statistics program. |
| **W2** | The 12 V pair has three suspect parameters, not one. §1.2 authorised correcting `k1`; `vth0` is outside its stated sanity window too, and the slope is 60–75 % out of band. | Correct `k1` per §1.2, and **do not derive any statistics from the 12 V cards** until they are refitted — mark `VTH_12`, `A_VT_12` and the 12 V corner as provisional in `stat_model.json`. A proper refit of `vth0`/`voff`/`nfactor`/`k2` on those two cards is a model-fitting task larger than this program's scope, and it would invalidate the 12 V entries in the sizing guide, so it wants its own decision. |

## 7. Next, once W1 is answered

Apply the agreed `nch` policy to the LV/mid cards with the slope re-measured after each change,
apply the 12 V `k1` fix, write the audit table into `docs/bsim3-defaults-audit.md`, then move to
§5 step 2 (the `A_VT` ladder with `c` from the RDF expression, VDMOS doping at AutoHV's 11 nm,
`σ(VTH)` per U5, plausibility booleans) and step 3 (re-measure, rebuild, Stop A′).
