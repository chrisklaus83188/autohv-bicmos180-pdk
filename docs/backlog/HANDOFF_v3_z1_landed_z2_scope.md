# Handoff: Z1 landed; Z2 is narrower than drafted — four departures, three questions

**Responds to:** the Z1–Z3 rulings reply, including Chris's §5 addendum
**Branch:** `mc-realism` @ `e8fa62a`, pushed
**Date:** 2026-09-18
**Status:** Z1 applied and committed. Z3(a) done inside it. **Z2 is measured but not committed** —
four items in its drafted scope turned out not to apply to this model, and the departures are large
enough that they need a ruling rather than a note after the fact.

---

## 1. Z1 landed (`e8fa62a`)

The derived ladder reproduced your table exactly, from an independent path:

| card | A_VT mV·µm | card | A_VT mV·µm |
|---|---|---|---|
| NMOS18 | 3.44 | PMOS18 | 3.66 |
| NMOS33 | 4.51 | PMOS33 | 4.81 |
| NMOS50 | 5.96 | PMOS50 | 6.41 |
| NMOS12 | 15.02 | PMOS12 | 15.84 |

`c_RDF` = **2.1991 mV·µm/√nm**, constant to **3.18 %** (2.1661…2.2361) across t_ox 4.25–31 nm and
N_a 9.0e16–7.9e17 cm⁻³. 5 V class lands at **0.542 / 0.583** mV·µm per nm of t_ox. `f_RDF` = 0.30
with the four citations recorded in `_A_VT_derivation`.

The linear band is retired as a target; `anchor-values.json` entries are retargeted on the derived
ladder at ±30 %, tagged `autohv-derived`, with the retired heuristic named in each basis string. The
12 V rung is recorded as the least externally checked.

**Z3(a) done in the same commit:** the eight verbatim `anchors` strings and `_A_VT_note` removed.
External references in `stat_model.json` **28 → 20**; the remaining 20 are the Z3(b) pass.

Diff verified confined before committing: `anchor-values.json` touched only `target`/`lo`/`hi`/
`basis`/`tag` across the eight `avt_1sigma` entries, nothing else.

## 2. Z2 — what actually applies

Confirmed applicable and measured:

| parameter | change | basis |
|---|---|---|
| `kp` | **× 1.1818** | `kp = µ·C_ox·(W_REF/L_ch)`, linear in C_ox |
| `cgs`, `cgdmax`, `cgdmin` | **× 1.1818** | `C_ox·W·(L_ch+Lov)`, linear in C_ox |
| `theta` | **× 1.1818** | `θ ≈ (1…3)e-7 / t_ox[cm]`; confirmed live in this model |
| `rd`, `rs`, `BV` | **untouched** | drift-region, excluded by Z2 |

Supporting checks: C_ox at 13 nm computes to **2.6563 fF/µm²**, matching the CHANGELOG's stated
2.66 — so inverting `kp` recovers the declared mobilities exactly at **400 / 130 cm²/Vs** (ratio
3.08, the recorded P-channel penalty). `theta` is live: `showmod` reads it back and Id falls
monotonically 6.127e-03 → 4.631e-03 as θ goes 0.10 → 0.24.

## 3. Four departures from the drafted scope

### 3.1 `ksubthres` cannot be recomputed — this model has no oxide

ngspice answered directly:

```
unrecognized parameter (tox) - ignored
```

The VDMOS model has no `t_ox` at all. `ksubthres` **is** the subthreshold slope, set literally —
there is no `n = 1 + C_dep/C_ox` chain inside the model to respond to an oxide change. Fitting
`ksubthres` per card by bisection against each card's measured slope returned **the values already
on the cards, to ±0.5 %**, on all thirteen.

I predicted this twice and wrong both times: first that S would fall, then that it would rise to
98.8–105.8 mV/dec. It does neither, because the C_dep/C_ox chain I was computing exists only in my
arithmetic, never in the simulator. **Left untouched.**

### 3.2 `VTO` shift is outside the ruling's scope

Deriving body doping from each `VTO` and moving to 11 nm implies a uniform **−13.1 to −13.6 %**
threshold shift on all ten enhancement cards (e.g. NDMOS20 1.000 → 0.869). Z2's mover list names
`kp`, gate caps, `theta`, `ksubthres` — not `VTO` — and a 13 % threshold move on every LDMOS is far
larger than anything pre-registered.

It also cuts against D2 itself: that declaration's "Vth-vs-tox tension resolved" paragraph exists
specifically to reconcile `vto` = 1.00–1.31 V with a gate-set oxide. Shifting `VTO` would undo a
ruled reconciliation. **Held for AA1.**

### 3.3 VDMOS `A_VT` should not take the Pelgrom ladder

The two wrapper families normalise differently:

| family | form | what `coef` means |
|---|---|---|
| BSIM3 | `AGAUSS(0, coef/√AUM2)`, `AUM2 = (W/1µ)(L/1µ)` | `A_VT`, area-normalised |
| VDMOS | `AGAUSS(0, coef, 3)/√mtot`, `mtot = W/10µ` | **σ(Vth) at the 10 µm cell — width only** |

Conversion chain validated both ways: BSIM3 `coef`/3 reproduces the pre-Z1 `was` column exactly
(0.0105 → 3.50, 0.0120 → 4.00, 0.0330 → 11.00, 0.0930 → 31.00), and the VDMOS 20.0 mV·µm entry
back-converts at the 6 µm² reference cell (10 µm × L_ch 0.6 µm) to **0.0245 V** against a carded
0.0255 — agreement that confirms the reading.

The carded VDMOS ladder spans **19.60–26.94 mV·µm** and is deliberately per-class (0.024 / 0.0255 /
0.027 / 0.0285 / 0.030 / 0.033). `c·√(t_ox·k1_equiv)` gives a nearly **flat 6.43–7.20**. Applying it
would flatten a fitted ladder using a quantity these wrappers do not consume. **Recommend leaving
it; held for AA2.**

### 3.4 The pre-registered movers are missed

Measured before/after on all thirteen cards, at Vov = 3 V:

| quantity | pre-registered | **measured** |
|---|---|---|
| Idsat | +≈18 % | **+4.1 … +10.4 %** |
| Ron | −5 … −10 % | **−1.3 … −8.9 %** |

`kp` × 1.1818 and `theta` × 1.1818 push **opposite ways** — more drive, more mobility degradation —
so roughly half the expected gain cancels. The effect is class-dependent: PDMOS20 +10.4 %,
NDMOS200 +4.1 %. Ron reaches the pre-registered band only at the low-voltage end; above 60 V it is
drift-dominated and `rd`/`rs` are (correctly) untouched.

## 4. One finding that is not Z2's doing

The phase-3 trigger case does not reproduce. Conditions identical to the record
(`CHANGELOG.md:370`: NDMOS200, W = 10 µm, diode-connected, 100 µA), measured on the **committed
13 nm cards before any rescale**:

| | recorded | measured |
|---|---|---|
| Vov | ~0.57 V | **0.4646 V** |
| gm/Id | 5.6 | **3.30** (operating-point), 4.07 (two-point secant) |

I first assumed my secant estimator was at fault; the proper operating-point measurement came out
*lower*, so that explanation was wrong. The qualitative claim survives — gm/Id 3.30 is firmly
strong-inversion, nowhere near the subthreshold collapse that triggered the original audit — but the
numbers do not, and I am not going to report it as "re-reported, unchanged".
`characterization-inventory.md` already flags NDMOS200 as **contested**, with its mismatch
coefficient "assigned, never validated". Pre-existing and independent of Z2.

## 5. Work behind these numbers, including what went wrong

- **The VDMOS slope harness took four passes.** Pass 1 fit a fixed 1e-12…1e-9 A window and returned
  357–678 mV/dec — it was fitting the numerical floor, not subthreshold. Pass 2 anchored the window
  on each card's own `VTO` and got 11 of 13. Pass 3 fixed the depletion card (DNMOS20, `VTO` −1.60)
  but broke all six PMOS cards, because I sorted by signed voltage and differentiated in ascending-V
  order — for a p-channel the current rises as Vg goes *more negative*, so the derivative was
  negative everywhere. Pass 4 differentiates along each device's own overdrive direction and adds a
  physical ceiling (reject any fit above 200 mV/dec, i.e. n > 3.4 at 300 K): **13 of 13, 90.6–97.3
  mV/dec**, monotonic with class — the recorded 85→95 ladder, reproduced.
- **The phase-2 mapping `S ≈ 1.17·1000·ksubthres` is not a constant.** Against the cards it runs
  1.066 → 0.992 (N) and 1.085 → 1.024 (P), drifting with class. Inverting it would have baked a
  1–8 % class-dependent error into a new ladder, which is why `ksubthres` was fitted by bisection
  instead — and the bisection then showed no change was needed at all.
- **My `V_FB` assumption was the source of a factor-of-2 scare.** Assuming ∓0.95 V gave body doping
  3.6e17–5.7e17, contradicting the 1.3e17–2.7e17 the phase-3 subthreshold ladder implies. Solving
  `V_FB` from the measured slopes instead gives **−0.710…−0.745 (N) / +0.696…+0.724 (P)** — tight,
  near-symmetric, physically sensible — and the two doping derivations then agree at
  **1.80e17–2.83e17**. There was never a conflict; there was an assumed parameter.
- **A write bug of mine:** I rewrote both JSONs without `newline="\n"` and produced CRLF, which made
  the diffstat untrustworthy until corrected. Fixed before committing; the landed diff is LF and
  confined.

## 6. Rulings needed

**AA1 — accept the reduced Z2?** Apply `kp`, `cgs`/`cgdmax`/`cgdmin`, `theta` × 1.1818 with
`ksubthres`, `VTO`, `A_VT` and `rd`/`rs`/`BV` untouched, and the measured movers (+4.1…+10.4 % Idsat,
−1.3…−8.9 % Ron) replacing the pre-registration in the CHANGELOG? Or do you want `VTO` shifted and
D2's reconciliation paragraph rewritten to match?

**AA2 — VDMOS `A_VT`:** leave the carded width-normalised ladder (my recommendation, with the
reasoning recorded), or convert it to an 11 nm basis by some route other than `c·√(t_ox·k1)`?

**AA3 — the trigger-case drift:** log it as a finding for the Z3(b)/Stop A′ pass, or investigate now
before Z2 lands?

Nothing for Z2 is committed. On a ruling it lands as one commit with D2 amended (11 nm, with the
reason), the CHANGELOG entry, and acceptance tabulated.

## 7. Queued behind these

`σ(VTH)` per U5 via `k1` — with the RDF-vs-total logic **not** applied, per §4, since global Vth
spread is implant-dose-driven; plausibility booleans as a local pass/fail script; re-measure the 40
directions; rebuild `corners.json`; **Stop A′**. Then the §5 naming pass (inventory, disposition,
renames, CI guard `tools/check_no_reference_names.py`, provenance taxonomy) before Phase 2 generates
anything that would carry the names forward.
