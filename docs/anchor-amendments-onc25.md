# Anchor Amendments from Process Grounding — AutoHV BiCMOS180 PDK

**What this is.** Proposed amendments to [`anchor-values.json`](anchor-values.json) from grounding the
audit's `[industry]` guesses against **a commercial 0.25 µm mixed-signal BCD process**. Each entry:
the anchor key, its current band, the proposed band, a derivation note, and the new tag `[grounded]`.

**Not applied.** Do not edit `anchor-values.json` from this file. The maintainer applies these
**together with** the outstanding phase-2 audit amendments in
[`audit-vs-measurement-discrepancies.md`](audit-vs-measurement-discrepancies.md), and with the
declarations in [`process-declarations.md`](process-declarations.md) they depend on.

**Provenance.** `[grounded]` = derived from the reference process, scaled to the 180 nm/BCD context
where noted, rounded to 2 significant figures. No third-party values are reproduced — the raw crosswalk
is in an uncommitted local file. Where a grounded band contradicts the audit, both are shown.

**Convention reminder.** AutoHV mismatch literals are **3σ**; the reference process's are **1σ**. All
mismatch amendments below are stated **1σ** (the anchor convention) with the 3× reconciliation noted.

---

## 1. Passives — the strongest grounding

### 1a. Resistor sheet resistance `rsh`

Adjacent generations; sheet resistances carry directly (silicidation and doping, not lithography).

Grounded nominals (rounded to 2 sig figs); proposed bands rounded to clean engineering figures, not
the reference tolerance windows.

| device | anchor `rsh` band | proposed `[grounded]` | grounded nominal + note |
|---|---|---|---|
| RPOLY_HI | 1000 – 2000 Ω/□ | **1000 – 2000** (hold) | ~1.5 kΩ/□ high-res poly. AutoHV's 1200 nominal is low-of-center; ~1.5 k would center it. A **~5 kΩ/□ ultra-high-res option also exists** — worth a second AutoHV device. |
| RPOLY_LO | 100 – 400 Ω/□ | **200 – 400** | ~300 Ω/□ standard unsilicided poly. **AutoHV's 25 Ω/□ is confirmed wrong** — that is silicide-strap territory (silicided poly is single-digit Ω/□); a real poly resistor is a few hundred. |
| RNPLUS | 50 – 150 Ω/□ | **50 – 90** | ~60 Ω/□ n+ diffusion. AutoHV's 32 is low. |
| RPPLUS | 50 – 150 Ω/□ | **80 – 140** | ~110 Ω/□ p+ diffusion. AutoHV's 58 is low; and p+ > n+ (~110 vs ~60) — AutoHV has the ordering right in sign. |
| RNWELL | 1000 – 2000 Ω/□ | **1000 – 1600** | ~1.2 kΩ/□ n-well-under-STI. Confirms AutoHV's 1800 is defensible, slightly high. |

### 1b. Resistor TC1 — F7, the decisive grounding

| device | anchor `tc1` band | proposed `[grounded]` | note |
|---|---|---|---|
| **RPOLY_HI** | −1500 … −500 ppm/°C | **−2000 … −1000** | Reference high-res poly TC1 ≈ **−1400 ppm/°C**, and the poly TC crosses zero at a few hundred Ω/□, going more negative with sheet. At AutoHV's ~1200 Ω/□ the grounded expectation is ≈ **−1900 ppm/°C**. **AutoHV's measured +656 is wrong-sign, now against real silicon.** This is the highest-confidence amendment in the set. |
| RPOLY_LO | +500 … +3000 | **−100 … +600** | The zero-crossover is ~250 Ω/□. At AutoHV's declared 25 Ω/□ (silicide-strap) TC is weakly positive; at a corrected ~280 Ω/□ it is near zero to slightly negative. The current +500…+3000 band is too high — real low-res poly TC is small. Reference low-TC poly option is −34 ppm/°C by design. |
| RNWELL | +3000 … +6000 | **+3000 … +4500** | n-well STI TC1 ≈ +3560 ppm/°C. Tightens toward the low half. |
| RNPLUS / RPPLUS | +1000 … +2000 / +1000 … +2500 | **+1200 … +1800** (both) | p+ active TC1 ≈ +1560 ppm/°C; confirms the positive diffusion TC. |

### 1c. Resistor matching `matching_A_R_pair_1sigma`

Reference process quotes resistor matching in %·µm (best-layout): high-res poly ~0.05, standard poly
~0.04, diffusion ~0.01–0.04, n-well ~0.36. **These are far tighter than AutoHV's current anchor bands**
(1.5–4.0 %·µm) — but they are *best-case* inter-digitated/common-centroid figures, and the reference
convention (1σ vs 3σ) is not stated at spec level. **No amendment proposed** — the audit's phase-2
finding (AutoHV is 4–11× optimistic) already flags these, and the reference best-layout numbers cannot
be compared cleanly without the convention. Recorded as a grounding *touchpoint*, not a band change.

### 1d. MIM capacitor

| device | anchor entry | current | proposed `[grounded]` | note |
|---|---|---|---|---|
| CMIM_STD | `density` | 1.0 – 2.0 fF/µm² | **0.9 – 1.1** | Reference MIM ≈ **1.0 fF/µm² ±12 %** — AutoHV's 1.0 nominal is an **exact match**; tighten the band. Nitride εr 7.5, ~67 nm — same construction as AutoHV's implied 62 nm. |
| CMIM_STD | `vcc1` | 12 – 60 ppm/V | **0 – 30** | Reference MIM VCC ≈ **0 ppm/V**. AutoHV's 30 is conservative but fine; band could tighten toward 0. |
| CMIM_STD | `tcc_tc1` | 14 – 88 ppm/°C | **0 – 45** | Reference MIM TCC ≈ **0 ppm/°C**. AutoHV models +35 — conservative; both defensible. |

---

## 2. MOS DC — direct pair at 5 V, scaled at core

### 2a. Idsat density (direct 5 V pair; core needs scaling)

| device | anchor `idsat_density` | proposed `[grounded]` | note |
|---|---|---|---|
| NMOS50 | 0.40 – 0.50 mA/µm | **0.48 – 0.60** | Reference 5 V NMOS ≈ **0.54 mA/µm** (direct 5 V↔5 V pair). AutoHV's measured 0.305 is weak; the anchor should center near 0.54. |
| PMOS50 | 0.18 – 0.25 mA/µm | **0.22 – 0.30** | Reference 5 V PMOS ≈ **0.26 mA/µm**. |
| NMOS18 | 0.55 – 0.60 mA/µm | **hold; note** | Reference has no 1.8 V class. Nearest is 2.5 V core at ~0.49 mA/µm. **2.5 V↔1.8 V is not a direct pair** (scale by tox/Vdd) — the audit's 0.55–0.60 is reasonable for a thinner-oxide 1.8 V device. No change, but flag as non-grounded. |
| NMOS33/PMOS33 | 0.45–0.55 / 0.20–0.28 | **hold; touchpoint** | Reference 3.3 V ≈ 0.52 / 0.27 mA/µm — brackets the current bands well. Optional tighten to 0.48–0.56 / 0.24–0.30. |

### 2b. Subthreshold swing

| device | anchor `subthreshold_swing` | proposed `[grounded]` | note |
|---|---|---|---|
| NMOS50 / PMOS50 | 72 – 96 mV/dec | **85 – 100** | Reference 5 V S ≈ **95 mV/dec** (both n & p). AutoHV's PMOS50 measured 102 is only just out; the grounded band centers higher than the audit's generic 72–96. 2.5/3.3 V S not specified (silence) — hold those. |

### 2c. Vth linear

| device | anchor `vth_lin` | proposed `[grounded]` | note |
|---|---|---|---|
| NMOS50 | 0.82 – 0.94 V | **0.79 – 0.92** | Reference 5 V Vtlin ≈ 0.79–0.85 V. Consistent; minor recentre. |
| PMOS50 | 0.92 – 1.04 V | **0.83 – 0.95** | Reference 5 V PMOS Vtlin ≈ −0.86 to −0.87 V. AutoHV's band is ~0.1 V high. |
| NMOS33/PMOS33 | per audit | **touchpoint** | Reference 3.3 V ≈ 0.58 / −0.80 V — brackets current bands. |

### 2d. Vth temperature coefficient (grounds phase-2 finding #6)

| device (all 8 BSIM3) | anchor `vth_tempco` | proposed `[grounded]` | note |
|---|---|---|---|
| all | −2.0 … −1.0 mV/°C | **−1.8 … −1.0** | Reference `kt1` gives dVth/dT ≈ **−1.0 mV/°C** (core) to **−1.6 mV/°C** (5 V). Confirms the audit band and, critically, that AutoHV's measured **−0.37 mV/°C is wrong** (it is the unset-`kt1` default). The fix should target `kt1 ≈ −0.4 V` (5 V) so dVth/dT ≈ −1.5 mV/°C. |
| all | `mobility_tempco_exponent` | −2.0 … −1.2 | **−1.4 … −1.1** | Reference `ute ≈ −1.2` (µ∝T^−1.2), flatter than the audit's −1.5 center. Note: still **conditional** — AutoHV's cards leave `ute` unset, so measuring it returns the simulator default (phase-2 finding #6). |

### 2e. Mismatch AVT (the convention grounding)

| device | anchor `avt_1sigma` | proposed `[grounded]` | note |
|---|---|---|---|
| NMOS18/PMOS18 | 4.25 ±50 % mV·µm | **hold** | Reference rule **AVT ≈ 1 mV·µm per nm oxide** (foundry footnote) = exactly the audit's assumption. At 4.25 nm → 4.25 mV·µm. **Confirmed, no change** — AutoHV's low-voltage AVT (measured 3.5) is fine. |
| NMOS50/PMOS50 | 11.0 mV·µm | **hold band, confirm defect** | Rule gives 11 mV·µm at 11 nm; AutoHV measured 4.5 (2.4× optimistic) — grounding **confirms the F-anchor defect**, band unchanged. |
| NMOS12/PMOS12 | 20.0 mV·µm | **31 (band 20–35)** | With the corrected ~31 nm oxide (D6), the rule gives **~31 mV·µm**, not 20. AutoHV measured 6.0 → now ~5× optimistic, not 3.3×. Recentre the anchor on the grounded oxide. |
| all | **convention note** | — | **Add to every mismatch entry:** the reference process implements AVT as a **1σ** coefficient normalized by √(W·L) in µm; AutoHV's literals are **3σ**. The 3× is real and must be applied when comparing. This resolves the standing convention ambiguity in the anchor `sigma_convention` fields. |

---

## 3. BJT (grounds D4)

| device | anchor entry | current | proposed `[grounded]` | note |
|---|---|---|---|---|
| NPN_LV | `ft_at_peak` | contested / descriptive | **0.5 – 2 GHz** `[grounded]` | Reference junction NPN fT ≈ **1 GHz-class**. Removes the "contested" status: a non-SiGe BCD NPN is ~1 GHz-class. AutoHV's 3.5 GHz is **optimistic**, ~3× — reframes F-BJT1 (the tf ceiling itself is high). |
| NPN_LV | `early_voltage` | 40 – 160 V | **50 – 120** | Reference VAF ≈ 60–70 V. Tightens; AutoHV's 80 is fine. |
| NPN_LV | `beta` | 84 – 224 | **hold, note** | Reference runs β in the mid-teens (low-β BCD NPN by design); AutoHV's 140 is a **legitimate general-purpose choice** — β is architecture, not generation. Both positions recorded; **no change**. |
| NPN_HV | `ft_at_peak` | contested | **0.3 – 1.5 GHz** `[grounded]` | Extrapolated down from the LV number for a higher-BV NPN. |
| all BJT | `vbe_at_100uA` | 0.62 – 0.78 V | **hold** | Reference Vbe ≈ 0.7 V in the µA range → ~0.72 V at 100 µA. Confirms the band. |
| all BJT | `flicker_corner` | 100 – 10000 Hz | **hold** | Reference bipolar KF/AF not specified (silence). F4 fix stays audit default (`kf ≈ 1e-15`, `af ≈ 1.5–2`). |

---

## 4. Zeners (grounds the missing-tempco fix)

Reference buried zeners establish the **mechanism and slope**, not a table: bv tempco is **positive,
rises with bv, with a zero-TC crossover near ~6 V**, at a slope of roughly **+1 mV/°C per volt above
the crossover** (a low-single-digit mV/°C in the 5–7 V range, climbing linearly with bv). This is the
textbook tunneling→avalanche crossover.

| device | anchor `bv_tempco` | proposed `[grounded]` | note |
|---|---|---|---|
| DZ_5V6 (5.6 V) | 0.13 – 0.40 mV/°C | **+0.5 – +1.5** | Just below the crossover → weakly positive, ~+1 mV/°C. AutoHV models 0 → fix target ~+1. |
| DZ_12 (12 V) | 4.0 – 12.8 mV/°C | **+5 – +9** | ~+1 mV/°C per volt above the ~6 V crossover → ~+6 mV/°C at 12 V. Confirms the audit band, centers it. |
| DZ_24 (24 V) | 10.0 – 32.0 mV/°C | **+15 – +22** | ~+18 mV/°C at 24 V by the same slope. Tightens the audit band. |
| all zeners | `cjo_density` | per audit | **hold** | Reference gives no zener cjo/area (silence). The hand-picked-ladder finding (audit 4.4) stands unground-able. |

**Sign and crossover both grounded** — the reference process's 6.2 V zero-TC part is the textbook
tunneling/avalanche crossover, exactly the mechanism the audit predicted. AutoHV's flat-zero zeners
are confirmed wrong, and the fix now has a grounded slope.

---

## 5. What is deliberately NOT amended (grounding was silent)

Per the gaps list in `process-declarations.md`, no amendment is proposed for: VDMOS Rsp / Ron·W / `kp`
magnitude (no LDMOS electrical data); MOS junction cap densities `cj_area` / `cjsw_sidewall` (F6 fix
targets — not tabulated); resistor VCR; BJT/diode Is-per-area, cje/cjc, cjo/area; MIM matching;
flicker-corner frequency; correlated corner spreads. These stay at their audit `[industry]`/`[physics]`
values and remain the synthetic content of the PDK.

---

## Application order (maintainer)

1. Resolve the **D2 gate-oxide declaration** (5 V-gate → ~13 nm flat, or 12 V-gate → ~31 nm flat) —
   it gates the VDMOS `kp`/`theta` anchors and the whole F1/F2 fix shape.
2. Apply §1 (passives) — highest confidence, no dependencies. **F7 sign flip is the headline.**
3. Apply §2d/§2e (MOS tempco + mismatch convention) — grounds two phase-2 findings.
4. Apply §3/§4 (BJT fT, zener tempco) — grounds two open fixes.
5. Apply §2a–2c (MOS DC) after confirming the 5 V-pair mapping.
6. Add the **mismatch 1σ/3σ convention note** to every mismatch anchor `sigma_convention` field.

Apply alongside the phase-2 audit amendments, not before them — where they touch the same entry (e.g.
mismatch), the phase-2 measured value and this grounded band must be reconciled into one band.

---
---

# Pass 2 — model-library + LDMOS-simulation amendments

**Pass-2 summary.** Pass 1 read the spec tables and used the model library selectively; pass 2 mined
the library systematically, ran local simulation on the reference LDMOS, and synthesized corner bands
from the spec limit columns. All values below are `[grounded]` and marked **(P2)**. Not applied.

**What the library closed** (pass-1 "silence" that was actually in the library): MOS S/D junction cap
densities (F6), diode Is/n/cjo, MOS Vth tempco + mobility exponent + 2.5/3.3 V subthreshold params,
the noise-parameter provenance (Task 4), and — by simulation — the medium-voltage LDMOS Ron·W / Idsat /
BVdss (the F1 magnitude, for the 30 V class).

**What stayed silent after checking both spec and library:** resistor VCR (no `vc1/vc2` coefficient;
diffusion-R voltage dependence is structural), BJT `kf/af` (F4 — absent in both), BJT Is-per-area and
cje/cjc (composite subckt, no clean device density), MIM matching, flicker-corner frequency (Hz).

**F1-magnitude status: GROUNDED BY SIMULATION for the medium-voltage class** (30 V LDMOS: Ron·W ~8400
Ω·µm, Idsat ~0.33 mA/µm, BVdss ~33.5 V). The 40/200 V LDMOS drift is a Verilog-A module this ngspice
build cannot run — those revert to maintainer declaration (silicon-limit ×2–5), now anchored to the
measured 30 V point rather than to nothing.

---

## P2-1. VDMOS DC magnitude (F1) — grounded by simulation `[grounded]`

Reference 30 V medium-voltage LDMOS, TT, 10 µm cell (per-µm = the AutoHV `W_REF` cell directly):

| FoM (new anchors) | current AutoHV | proposed `[grounded]` (P2) | note |
|---|---|---|---|
| `ron_times_w` (HV NMOS, MV class) | ~2–6 Ω·µm (phase-2 measured, F1) | **3×10³ – 1×10⁴ Ω·µm** | 30 V ref = ~8400 Ω·µm at Vgs=5/Vds=0.1; AutoHV NDMOS20 is ~3600× low. Scale mildly down for the 20 V class. |
| `idsat_density` (HV NMOS, MV class) | anchor 0.05–0.30 mA/µm; AutoHV measures ~1674 | **0.2 – 0.4 mA/µm** | 30 V ref = 0.33 mA/µm at Vgs=Vds=5. Confirms the anchor's upper band; AutoHV is ~5000× high. |
| `bv` (30 V class) | — | **~33 V** for a 30 V-rated device | ref BVdss 33.5 V (gate off, 1 µA). Worst-corner must clear the class name — matches AutoHV's own bv convention. |
| `cgs_per_cell` / drain cap (MV) | F2 targets | **~4 fF/µm gate, ~20 fF/µm drain** | ref 30 V Cgg 4.08, Cdd 21.1 fF/µm. Order-of-magnitude check on the F2 cap re-derivation. |

**This closes the item both pass 1 and the audit called the unclosable synthetic heart of the PDK —
for the medium-voltage class.** The `kp` re-derivation (fix #2) now has a measured Idsat/Ron target,
not just a silicon-limit estimate. HV (100–200 V) remains extrapolation (Verilog-A not runnable),
pinned to the silicon-limit ×2–5 default anchored at this 30 V point.

## P2-2. MOS S/D junction cap density (F6) — grounded by simulation `[grounded]`

Pass 1 declared these ungrounded ("not tabulated"). Simulated on the reference S/D parasitic diode,
two geometries, solved C = cj·A + cjsw·P:

| anchor | current | proposed `[grounded]` (P2) | note |
|---|---|---|---|
| NMOS50 `cj_area` | 0.42–0.90 fF/µm² | **1.1 – 1.6 fF/µm²** | n+/pwell 5 V ref ≈ 1.4 fF/µm². AutoHV's 5 V-class cj is low; recentre higher. |
| PMOS50 `cj_area` | 0.45–0.90 fF/µm² | **1.2 – 1.7 fF/µm²** | p+/nwell 5 V ref ≈ 1.5 fF/µm². |
| NMOS50/PMOS50 `cjsw_sidewall` | 0.11–0.29 fF/µm | **0.05 – 0.15 fF/µm** | ref ≈ 0.09–0.10 fF/µm — lower than the audit band (STI sidewall). |
| all MOS junction | `pb`/`mj` | vj ≈ 0.8 (n+/pw), 0.95 (p+/nw); m ≈ 0.38 / 0.43 | grading grounded; abrupt-ish p+/nw, graded n+/pw. |

**F6 fix targets are now grounded** (they were the phase-2 "cj/cjsw ungrounded" gap). Note the fix
still requires AutoHV to *set* AD/AS/PD/PS on the instance lines (F6 is that they are unset) — these
are the densities to use once it does. The 5 V grounded value should scale up ~1.3× for the 1.8 V core
(thinner junction, higher doping).

## P2-3. MOS Vth tempco + mobility exponent + subthreshold — grounded `[grounded]`

| anchor | current | proposed `[grounded]` (P2) | note |
|---|---|---|---|
| all 8 `vth_tempco` | −2.0…−1.0 mV/°C (pass-1) | **−1.6 … −1.0 mV/°C** | ref dVth/dT = kt1/Tnom: −1.0 (core) to −1.6 (5 V). Tightens; confirms AutoHV's −0.37 (unset-kt1 default) is wrong. Fix: `kt1 ≈ −0.3` (core) to −0.48 (5 V). |
| all 8 `mobility_tempco_exponent` | −1.4…−1.1 (pass-1) | **−1.2 … −1.6** | ref `ute` = −1.2 to −1.6 across classes (not a single −1.5). Still conditional (AutoHV leaves ute unset). |
| NMOS18/33 `subthreshold_swing` | 72–96 (generic) | **hold; grounded nfactor** | ref `nfactor` ≈ 1.2 (3.3 V n), voff ≈ −0.12; consistent with 72–96 mV/dec. 2.5 V n nfactor is unusually low (0.1) — a device-specific fit, not general. |

## P2-4. Diodes — grounded `[grounded]`

| anchor | current | proposed `[grounded]` (P2) | note |
|---|---|---|---|
| DIO_PN `n_ideality` | 1.0–1.12 | **1.00 – 1.03** | ref junction diodes n ≈ 1.0–1.02 (near-ideal). Tightens; AutoHV's 1.05 is slightly high. |
| DIO_PN `cjo_density` | 0.5–2.0 fF/µm² (AREA-conditional) | **~1.4 fF/µm²** (n+/pw), **~1.5** (p+/nw) | grounded from the same junction sim as F6. Still conditional on the AREA=1 cell declaration (D3). |
| DIO_PN `bv` | per audit | ref n+/pw ≈ 9.3 V, p+/nw ≈ 7.9 V (5 V-class junctions) | a 5 V-class junction breaks down ~8–9 V; AutoHV's 100 V DIO_PN is a different (deep) junction — no change, noted. |

## P2-5. Corner spreads (Task 3) — grounded from LSL/Nom/USL `[grounded]`

Synthesized from the spec's independent limit columns (FF ≈ USL-Idsat/LSL-|Vth|, SS ≈ reverse).
These bound **uncorrelated** per-parameter limits, so they sit at or slightly **wide** of a correlated
FF/SS bundle — an upper bound on the true spread.

| anchor | current | proposed `[grounded]` (P2) | note |
|---|---|---|---|
| `idsat_corner_spread` (5 V class) | 10–20 % | **12 – 20 %** | ref 5 V ±14 %; 2.5/3.3 V ±20 %. AutoHV's measured 14–34 % (phase-2) — the high end exceeds even this. |
| `vth_corner_spread` (all MOS) | 40–60 mV | **±90 – 130 mV (uncorrelated upper bound)** | ref: 2.5 V ±88, 3.3 V ±114, 5 V ±128 mV. **AutoHV's phase-2 measured ~79 mV is INSIDE this — so the 40–60 mV anchor was too tight, not the model.** Widen the anchor. |
| `beta_corner_spread` | per audit | not synthesized | spec gives BetaM min/max but pass-2 did not tabulate; hold. |

**This upgrades the corner anchors from sign-checked to magnitude-checked**, and in doing so overturns
one phase-2 concern: the `vth_corner_spread` "fail" was an anchor that was too tight, not a model defect.

## P2-6. Noise provenance (Task 4) — no band change, disclosure only

No anchor band changes. The finding is textual (see `process-declarations.md` D5, rewritten): AutoHV's
noise triplet is the **stock BSIM4 default set** in BSIM3 cards — not lifted from the reference process
(whose PMOS noia is a custom value AutoHV does not use). The F3 fix (BSIM3-convention values, or migrate
to level 54) is unchanged. The reference does add per-class `kf/af` on its 3.3/5 V devices — an optional
refinement, not required for the fix.

---

## Application order (pass-2 additions)

7. Apply **P2-1** (VDMOS MV DC magnitude) with the D2 gate-oxide decision — it is the measured target
   for fix #2 (`kp`) and fix #3 (`rd`/`rs`) at the medium-voltage class.
8. Apply **P2-2** (junction cap density) as the F6 fix densities, once AD/AS/PD/PS are set.
9. Apply **P2-3** (tempco/mobility) — grounds the phase-2 `vth_tempco` finding with per-class `kt1`.
10. Apply **P2-5** (corner spreads) — **widen `vth_corner_spread`**; it was too tight.
11. **P2-6 is a text fix already applied in `process-declarations.md` D5**, not an anchor change.
