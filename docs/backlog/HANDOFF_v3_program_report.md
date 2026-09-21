# Program report: the 12 V refit through Stop A′

**Covers:** rulings X/Y (12 V refit), Z1–Z3, AA1–AA3, AB1–AB2, U1–U5, and the standing autonomy rule
**Branch:** `mc-realism`, `da7e359` → `34fba9f`, twelve commits, all pushed
**Date:** 2026-09-19
**Why this document:** the chat session has received this arc only piecewise, in four separate
handoffs. This is the consolidated picture — what changed, what was measured, and what I got wrong.

---

## 1. The arc in one table

| commit | what landed |
|---|---|
| `da7e359` | 12 V card refit — `k1`, `k2`, `nfactor`, `voff`, `cj`, `cjsw` |
| `e8fa62a` | `A_VT` ladder derived from RDF at `f_RDF` = 0.30 (Z1); Z3(a) anchors removed |
| `1e3998a` | VDMOS gate oxide 13 → 11 nm (Z2/AA1–AA3) |
| `2dd54a1` | σ(VTH) as three derived terms; U1 binary sharing (AB1/AB2) |
| `8b0144d` | U2 — U0 declared, per-class Idsat bands retired, 40 directions re-measured |
| `614d085` | plausibility check as a local pass/fail script (U3) |
| `4f1e8df` | stale VDMOS VTH template refreshed |
| `34fba9f` | Stop A′ |

Net: **16 files, +3226 / −1949**. Four of the twelve commits are handoffs.

## 2. What the PDK says now that it did not before

### 2.1 The 12 V cards were scaled copies, and are not any more

22 of 59 shared parameters were byte-identical to the 5 V cards, including everything that depends
on doping and oxide. Three independent lines of evidence agreed that `k1` was the copied parameter:
body effect vs γ(nch), subthreshold slope vs the `n = 1 + C_dep/C_ox` floor, and `vth0` being
consistent with the *corrected* γ but not with the card's own `k1`.

| quantity | NMOS12 | PMOS12 | target |
|---|---|---|---|
| subthreshold slope | 152.8 → **120.9** mV/dec | 170.2 → **124.4** | 120 ± 10 |
| ΔVth at Vsb = 5 V | 0.825 → **2.090 V** | 0.910 → **2.406 V** | ≈ γ-implied |
| implied `k1_eff`, long device | **1.463 (94 %)** | **1.677 (98 %)** | = γ(nch) |
| Idsat at Vgs = Vds = 12 V | **−5.7…−6.3 %** | same | within 10 % |

Three extraction methods agree on ΔVth (2.090 / 2.078 / 2.044 on NMOS12), so these are not
extraction artefacts.

### 2.2 Mismatch is derived, not interpolated from anyone's measurements

`A_VT = c_RDF·√(t_ox[nm]·k1)` with `c_RDF` = **2.1991** mV·µm/√nm **computed from RDF physics**,
never fitted. The check that it is right: `c_RDF` holds to **3.18 %** across oxides 4.25→31 nm and
dopings 9e16→7.9e17 cm⁻³. A wrong doping exponent would drift it systematically with oxide
thickness; it does not.

Ladder: 3.44 / 3.66 / 4.51 / 4.81 / 5.96 / 6.41 / 15.02 / 15.84 mV·µm.

### 2.3 The VDMOS sit on AutoHV's own oxide

13 nm was the reference process's 5 V oxide. Ours is **11 nm**, and the statistical model had
already been sharing `TOX_50` between the 5 V CMOS and the VDMOS — so the declaration and the model
had been inconsistent. D2 re-ruled. Oxide-linear parameters scaled by 13/11; `ksubthres`, `VTO`,
`rd`/`rs`/`BV` held, each for a stated reason.

| mover | pre-registered | **measured** |
|---|---|---|
| Idsat | +≈18 % | **+4.1 … +10.4 %** |
| Ron | −5 … −10 % | **−1.3 … −8.9 %** |

The pre-registration assumed `kp` alone. Thinner oxide raises drive **and** raises vertical-field
mobility degradation, so `kp` ×1.1818 and `theta` ×1.1818 oppose and roughly half the gain cancels.

### 2.4 Global Vth spread is physics, not a spec window

The previous σ(VTH) values were **LSL/USL spec limits, not model σ** — a category error, and 2–3×
too wide at 5 V. Now three derived terms: fixed oxide charge `Q_f`, effective channel charge, and
an oxide term that is *not* in the private draw but enters through the shared `TOX_<class>` draw so
same-oxide devices correlate.

| device | 1σ mV | | device | 1σ mV |
|---|---|---|---|---|
| NMOS18 / PMOS18 | 10.3 / 11.3 | | NMOS50 / PMOS50 | 16.5 / 17.6 |
| NMOS33 / PMOS33 | 12.5 / 13.6 | | NMOS12 / PMOS12 | 43.0 / 44.5 |
| VDMOS ×13 | 20.0–23.1 | | | |

No automotive tightening factor anywhere — that was rejected in U3.

### 2.5 Nothing is tuned to an outside number any more

U0 used to be *solved* so each group's Idsat swing hit a per-class band. Those bands were
externally sourced and the LDMOS one was invented. Solving against them meant U0 silently absorbed
every error elsewhere — when σ(VTH) narrowed, a trial run inflated U0 from 4.57 % to 6.20 % to keep
hitting the same outside number. U0 is now **declared** at 8 % 3σ and each group's Idsat spread is
whatever its own inputs predict: **6.79–11.96 %**, reported rather than targeted.

**Provenance of the statistical layer today:** 30 `autohv-derived`, 11 `declared`, 8 `literature`,
**9 external remaining** (resistor/capacitor/BJT/diode tolerances — the Z3(b) scope).

## 3. Findings that were not asked for

- **`k1` moves saturation current at Vbs = 0.** Not through the body-bias term — through BSIM3's
  bulk-charge factor `Abulk`. Proven by the operating-point split: saturation −6.0 %, linear
  −0.9 %/−1.1 %. A threshold shift would move both alike.
- **ngspice's VDMOS model has no oxide at all** — `unrecognized parameter (tox) - ignored`. So
  `ksubthres` *is* the slope, set literally, and "recompute it at 11 nm" has no referent. A
  bisection fit against each card's measured slope returned the carded values to ±0.5 %.
- **BSIM3 does not couple oxide to threshold.** `showmod` confirms `vth0` and `k1` do not move when
  `tox` does. BSIM3 *does* move the threshold through its short-channel and narrow-width terms,
  so the generator applies `analytic − bsim3_residual`. (The 3.7–19.5 % figure first reported
  here was an extraction artefact; corrected in §5.)
- **The U0/Rd anti-correlation is a measurable device property.** `dominant_variable` flips from
  `U0` to `RDSW` exactly where drift resistance takes over (NDMOS80 onward, as the U0 slope falls
  through 0.4). On a 200 V LDMOS, mobility barely moves the current at all.
- **The phase-2 mapping `S ≈ 1.17·1000·ksubthres` is not a constant** — it drifts 0.99–1.09 with
  voltage class. Retired.
- **The phase-3 trigger case does not reproduce** on unchanged cards: Vov 0.4646 V and gm/Id 3.30
  against a recorded ~0.57 V and 5.6. Pre-existing, logged for Phase 7 per AA3.

## 4. What I got wrong, and how it was caught

| claim | what was true | caught by |
|---|---|---|
| "Idsat won't move; `k1` only touches the body-bias term" | it moved −6.0 % | measurement |
| then "the mover is `k2`" | NMOS12's `k2` never changed yet its Idsat moved fully | the card diff |
| "σ(VTH) dose-only is the answer" | 6–20× too narrow on all 21 devices | plausibility check |
| "U1 must land before the re-measure or distances shift" | nothing reads the ρ layer | `grep` |
| plausibility bands for the 1.8 V and 12 V classes | invented by copying/spanning unrelated rows | re-reading the source |
| "external refs 28 → 19 → 14 → 12 → 11" | mixed case-sensitive and -insensitive greps | one consistent definition |
| harness measured 357–678 mV/dec slopes | fitting the numerical floor, not subthreshold | sanity of the value |
| pass 3 "fixed" the harness | broke all six PMOS cards (derivative direction) | the regression itself |

Four more were my own edits: a duplicate `## D2` heading, a duplicate `### 3.1`, CRLF written into
two JSONs, and a stale `_VTH_VDMOS_template` carrying a retired σ that disagreed with every entry
it described.

The VDMOS slope harness took **four passes** to measure 13 of 13 cards. The final rule — fit over
1e-10…1e-7 A, reject anything above 200 mV/dec as unphysical (n > 3.4 at 300 K), fall back to the
derivative-peak window — resolves every card without hand-picking.

## 5. Acceptance at Stop A′

| check | result |
|---|---|
| directions measured | 40 of 40 |
| `corners.json --check` | clean |
| plausibility | 17 checked, **2 reported misses**, 4 no comparable class |
| oxide coupling validated against ngspice | yes — residual 3.7–19.5 % |
| plausibility script vs the AB1 generator | **zero diff** on all 21 variables |
| `--apply` with no local magnitudes | refused, exit 1 |

> **Corrected 2026-09-19.** The 3.7–19.5 % residual quoted above is wrong. It came from
> constant-current and gm-max extraction, both of which move with `tox` themselves and gave
> criterion-dependent, sign-unstable results (NMOS18 read −0.18 mV at a 1× W/L criterion,
> −0.61 at 0.1×, +3.52 at 10×). Measured from the model's own `@m.xm1.m0[vth]` at bench
> geometry the residual is **negative**, −0.96 to −1.92 mV, i.e. 9–22 %, which makes
> `applied = analytic − residual` *larger* than analytic rather than smaller. See
> `docs/stat-model.md` §2.2a.

**The reported miss:** NMOS33/PMOS33 at 0.26× and 0.28× of the comparable midpoint. Reported, not
clamped, per U3. Worth noting the comparable for 3.3 V is *wider* than the one for 5 V, which is
backwards for a thinner oxide.

**Corner distances moved** because the oxide coupling puts `TOX` in every MOS direction: FF/SS
13.84 → **16.54** (same-polarity presets pull each shared oxide together), FS/SF 13.38 → **12.83**
(opposite-polarity presets fight over it, reported as shared-variable conflicts on presets 3 and 4).

## 6. The naming pass is bigger than the model file

One definition — case-insensitive `<reference-name pattern>` across tracked files — gives **100 occurrences in
16 files**. `models/stat_model.json` holds 19 and `docs/stat-model.md` 9; the largest single file is
a committed backlog handoff at 22. §5 of the naming rule explicitly includes those, so the pass is
mostly documentation rather than model content.

## 7. Queued

Phase 2 (`tools/gen_models.py`) honouring the `follows` couplings — recorded in
`dependent_parameters` as a contract, with nothing generating perturbed cards from them yet. Then
the naming pass, then Phases 3–7. Open and unchanged: `k3` grounding at 2.0 awaits the audit
landing; the NDMOS200 trigger-case drift is logged for Phase 7.
