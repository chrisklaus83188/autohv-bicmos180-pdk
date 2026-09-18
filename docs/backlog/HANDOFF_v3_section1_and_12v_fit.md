# Handoff: §1 landed, 12 V fit solved, one contradiction blocking the refit

**Responds to:** the X1–X3 rulings reply
**Branch:** `mc-realism` @ `a9e41c7`, pushed
**Date:** 2026-09-18
**Status:** §1 is applied and committed. The 12 V `nfactor`/`voff` fit is solved and lands in the
ruled band. The refit commit is **held on one question (Y1)** because §3's instruction and its own
pre-registration disagree. Two corrections of mine are recorded below.

## 1. Two corrections I owe, both in the ruling's favour

**The units bug was mine and the ruling's arithmetic was right.** I computed φ_F with `Na` in m⁻³
against `ni` in cm⁻³, inflating φ_F by `kT·ln(10⁶)` = 0.357 V. Corrected:

| quantity | my last handoff | corrected | ruling's figure |
|---|---|---|---|
| φ_F (NMOS12) | 0.762 V | **0.404 V** | 0.414 |
| `W_dm` | 148 nm | **107.8 nm** | 109 |
| n | 1.629 | **1.863** | 1.85 |
| S | 96.9 mV/dec | **110.9** | 110 |
| NMOS50 cross-check | — | **80.4** | 80 |

So X1's 120 ± 10 target stands on correct arithmetic, and my proposed 95–105 band is withdrawn.

**The `vth0` reasoning in my last handoff was also wrong — and fixing it strengthens §1.2.** With
φ_F correct, the 12 V `vth0` is consistent with the **corrected** γ(nch), not with the card's `k1`:

| card | using card `k1` | using γ(nch) | card `vth0` |
|---|---|---|---|
| NMOS12 | +0.53 V (Δ −0.82, **out**) | **+1.25 V (Δ −0.10, in ±0.3)** | +1.350 |
| PMOS12 | −0.61 V (Δ +0.94, **out**) | **−1.42 V (Δ +0.13, in ±0.3)** | −1.550 |

`vth0` was fitted for a device whose body effect really is γ ≈ 1.55 — a **third independent line of
evidence** that `k1` is the copied, wrong parameter. My earlier "W2 withdrawn" conclusion was right
but for the wrong reason, and the audit will say so.

Also corrected: ΔVth at Vsb = 5 V is understated by **1.21 V (NMOS12) / 1.35 V (PMOS12)**, not the
1.06/1.18 I reported.

## 2. §1 applied and committed (`a9e41c7`)

- **PMOS50 `nfactor` 1.9000 → 1.5055**, giving **95.32 mV/dec** against the grounded 95 ± 3 target.
  `k1`, `nch`, `vth0` untouched.
- **`k1`/`nch` retained on all six LV/mid cards** as retrograde-profile consistent, with the ratio
  table and measured baseline slopes in `docs/bsim3-defaults-audit.md` §6.
- `docs/stat-model.md` §1.1 now states that every depletion-charge derivation uses `k1`, never
  `nch`.

## 3. The 12 V fit is solved

Fitted by bisection against the measured slope, then `voff` to restore weak-inversion continuity:

| card | `nfactor` | `voff` | S mV/dec | Id at `vth0` − 0.3 V |
|---|---|---|---|---|
| NMOS12 today | 1.7000 | −0.0700 | 152.8 | 8.826e-11 A |
| **NMOS12 fitted** | **1.0625** | **−0.1544** | **120.7** | 8.643e-11 (**98 %** of today) |
| PMOS12 today | 1.8500 | −0.0800 | 170.2 | 6.872e-11 A |
| **PMOS12 fitted** | **0.9713** | **−0.2015** | **123.9** | 6.856e-11 (**100 %** of today) |

Both inside the ruled 120 ± 10, both satisfying the ≤ 10 % continuity condition.

My first attempt had the `voff` bisection inverted — in BSIM3 subthreshold
`Ids ∝ exp((Vgs − Vth − voff)/(n·vt))`, so Id *falls* as `voff` rises, and my loop walked the wrong
way and crushed the current to 0.4 % of today. Caught and corrected; the numbers above are from the
corrected search.

## 4. Y1 — the X3 instruction contradicts its own pre-registration

§3 says scale the 12 V junction densities by `√(Na_5V/Na_12V)` using the **`k1`-implied** dopings,
and pre-registers the result as **−10 to −25 %**. Those cannot both hold:

| basis | Na 5 V → 12 V | scale | `cj` change |
|---|---|---|---|
| card `nch` | 1.20e17 → 9.0e16 (N), 1.40e17 → 1.10e17 (P) | 0.866 / 0.886 | **−13 % / −11 %** |
| `k1`-implied | 1.37e17 → 2.10e16 (N), 1.81e17 → 2.51e16 (P) | 0.392 / 0.372 | **−61 % / −63 %** |

Only the `nch` basis lands in the pre-registered range.

**My recommendation is the card-`nch` basis, on physics rather than on matching the
pre-registration.** Junction capacitance is set by the doping on the *lightly-doped side* of the
junction — the well — and `nch` is the closer proxy for it. `Na(k1)` is the depletion-averaged
**channel** doping, inflated by halo, which has no bearing on a source/drain-to-well junction. The
`k1`-not-`nch` rule from §1 of the W-reply was scoped to *depletion-charge* derivations (Pelgrom
`A_VT`, `σ(VTH)`); junction capacitance is not one of those.

Supporting detail: the cards already distinguish the 12 V junction in `xj` (5e-7 m vs the 5 V
card's 2.6e-7) while carrying byte-identical `cj` and `cjsw` — consistent with the densities being
the copied part and the depth being genuine.

## 5. Y2 — a minor acceptance question

PMOS12 lands at **123.9 mV/dec**, 3.9 above the 120 centre but inside ±10. I propose taking it
rather than over-fitting a third parameter to chase the centre. Say if you want it nearer 120.

`k2` = −0.03 with a note is applied per X2, replacing the 5 V copy.

## 6. Ready to land the moment Y1 is answered

One "12 V card refit" commit containing: `k1` 1.552 / 1.715; `k2` −0.03; `nfactor`/`voff` from §3;
`cj`/`cjsw` per Y1; the audit table; `anchor-values.json` 12 V band → 110–130 tagged
`autohv-derived` with the textbook floor noted and the retired 72–96 thin-oxide anchor recorded.
Acceptance measured and reported in the commit: body effect equals γ(nch); slope in band; Idsat at
Vgs = Vds = 12 V within 10 % (expected ≈ 0 %, since `k1` moves only the body-bias term); 12 V corner
regression re-run with movers tabulated.

Then: `A_VT` ladder `c·√(tox·k1)` with `c` from the RDF expression, VDMOS doping at AutoHV's 11 nm,
`σ(VTH)` via `k1`, plausibility booleans, re-measure the 40 directions, rebuild `corners.json`,
**Stop A′**.
