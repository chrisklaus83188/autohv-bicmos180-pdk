# Handoff: refit prep — PMOS5V0 fitted, `vth0` cleared, 12 V slope target needs correcting

**Responds to:** the W1–W2 rulings reply (§1.1 withdrawn, 12 V refit authorised)
**Branch:** `mc-realism` @ `811fca2`
**Date:** 2026-09-17
**Status:** §1's PMOS5V0 fit is solved and ready to apply. Two numbers in the ruling need
correcting first — one of mine, one of the reply's. Three requests, X1–X3. **No model file has
been changed yet**; the 12 V `nfactor`/`voff` fit is held because it targets the band in X1.

## 1. W2's `vth0` concern is withdrawn — the error was mine

The ruling was right to suspect the φ_ms convention. Recomputed with φ_ms = −0.95 V as specified,
using each card's own `k1`:

| card | first-principles Vth | card `vth0` | delta | verdict |
|---|---|---|---|---|
| NMOS12V | +1.50 V | +1.350 | **+0.15** | inside ±0.3 |
| PMOS12V | −1.60 V | −1.550 | **−0.05** | inside ±0.3 |

My earlier +0.77 / −0.78 came from using φ_ms = −(0.56 + φ_F) ≈ −1.32 V instead. **`vth0` on the
12 V pair is consistent and is not a finding.** That drops the 12 V suspect list from three
parameters to two: `k1` and the subthreshold slope.

### 1.1 A coupling worth recording before the refit

Substituting the *corrected* γ(nch) into the same expression gives +2.49 V / −2.71 V, about
1.15 V from the card. **That is not a second defect.** BSIM3 uses `vth0` as a fitted zero-bias
threshold, and `k1` scales only the body-bias term
(`Vth = vth0 + k1(√(φs−Vbs) − √φs) − k2·Vbs + …`). So correcting `k1`:

- leaves Vth at Vbs = 0 exactly where it is,
- therefore leaves Idsat at Vgs = Vds = 12 V essentially unchanged — the refit's "within 10 %"
  acceptance is pre-satisfied by construction, not by luck,
- and changes only body-bias behaviour, which is the intended effect.

Worth stating in the audit so the 1.15 V gap is not later read as a defect.

## 2. X1 — the 12 V slope target in §2 does not follow from the cards

§2 sets the refit target at "`n = 1 + C_dep/C_ox ≈ 1.8–1.9`, i.e. ≈ 105–115 mV/dec". Worked
through with each card's own `nch` and its 31 nm oxide:

| quantity | NMOS12V | PMOS12V |
|---|---|---|
| `Na` (card `nch`) | 9.0e16 cm⁻³ | 1.1e17 cm⁻³ |
| `C_ox = ε_ox/tox` | 1.114e-3 F/m² | 1.114e-3 F/m² |
| `W_dm = √(2ε_si·2φ_F/(q·Na))` | 148 nm | 134 nm |
| `C_dep = ε_si/W_dm` | 7.003e-4 F/m² | 7.716e-4 F/m² |
| **n = 1 + C_dep/C_ox** | **1.629** | **1.693** |
| **S = n·ln10·kT/q at 27 °C** | **96.9 mV/dec** | **100.8 mV/dec** |

So the derived band is **≈ 95–105 mV/dec**, not 105–115. To reach n = 1.8–1.9 at this oxide you
would need `Na` ≈ 1.6–2.0e17, roughly double what the cards declare.

This matters because the refit fits `nfactor`/`voff` *to* this target: aiming at 105–115 would
pull the 12 V cards about 8 % past their own physics. Measured today is 152.8 / 170.2, so either
target is a large correction; the question is only where it lands.

**Request:** confirm the band as 95–105 (derivation above), or tell me the 1.8–1.9 figure comes
from an input I don't have.

## 3. §1 is solved and ready to apply

**PMOS5V0 `nfactor`**, fitted by bisection against the measured slope, everything else untouched:

| nfactor | measured S |
|---|---|
| 1.9000 (today) | 104.3 mV/dec |
| **1.5055 (proposed)** | **95.32 mV/dec** |
| 1.4876 | 94.81 mV/dec |

Target is the grounded 95 ± 3, so 1.5055 lands 0.32 off centre. `k1`, `nch` and `vth0` are not
touched.

The rest of §1 is bookkeeping I'll apply in the same commit: the `k1`/`nch` ratio per card
recorded as "retrograde-profile consistent, retained", the baseline slope table, and the
statement in `docs/stat-model.md` that every depletion-charge derivation uses `k1` and never
`nch`.

## 4. X2 and X3 — two smaller items in the refit scope

**X2 — `k2` on the 12 V pair.** §2 offers a choice: re-derive from the BSIM3 relation to `k1`
and the substrate-bias range, or set a typical small negative value (−0.02 to −0.05) with a note.
Since `k2` is currently a byte-copy from the 5 V card and there is no 12 V extraction data to
re-derive against, I propose **−0.03 with a note**, unless you prefer the derivation.

**X3 — `cj`/`cjsw` on the 12 V pair.** §2 says ground from the F6 junction-cap densities if the
12 V class is stated there, else scale by `√(Na_5V/Na_12V)`. I have not yet checked whether F6
covers the 12 V class; I'll look before applying, and use the scaling fallback with a note if it
doesn't. Flagging it because the fallback changes junction capacitance on every 12 V device and
should not pass unnoticed.

## 5. Order I will work in, once X1 is answered

1. §1 commit: PMOS5V0 `nfactor`, audit entries, `stat-model.md` statement.
2. 12 V refit commit: `k1` = 1.552 / 1.715 (γ from `nch`), `k2` per X2, `nfactor`/`voff` fitted to
   the X1 band, `cj`/`cjsw` per X3, plus the acceptance set — body effect equals γ(nch), slope in
   band, Idsat within 10 % (expected ≈ 0 % per §1.1), 12 V corner regression re-run with movers
   tabulated, and `anchor-values.json` updated to the derived band tagged `autohv-derived`.
3. Resume: `A_VT` ladder from `c·√(tox·k1)` with `c` from the RDF expression, VDMOS doping at
   AutoHV's 11 nm, `σ(VTH)` per U5 through `k1`, plausibility booleans.
4. Re-measure the 40 directions, rebuild `corners.json`, **Stop A′**.
