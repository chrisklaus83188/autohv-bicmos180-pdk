# Process Declarations — AutoHV BiCMOS180 PDK

## Declarations in force — RULED (phase 3, status `[ruled]`)

The maintainer has ruled. These are fixed inputs to phase 3 and every later phase.

1. **`W_REF = 10 um` is a genuine drawn cell** (D1). `[ruled]`
2. **All VDMOS are 5 V-gate devices: tox = 13 nm, flat across drain classes** (D2). Rated |Vgs| <= 5 V; the harness rated-drive condition is Vov = 3 V. `[ruled]`
3. **BJT/diode `AREA = 1 = 100 um^2`** (D3); `is` kept, cje/cjc reconciled to it. `[ruled]`
4. **BJTs are BCD junction devices** (D4): fT anchor 0.5-2 GHz; `tf` stands. `[ruled]`
5. **F3 fixed in place: BSIM3-convention noise on the level=49 cards** -- no BSIM4 migration this phase. `[ruled]`
6. **NMOS12/PMOS12 are thick-oxide planar 12 V devices: tox = 31 nm, Lmin = 0.5 um** (D6). `[ruled]`
7. **Qualification range -40 to +150 C** (D7), stated in both model-file headers. `[ruled]`
8. **VDMOS Rsp per class -- grounded (P2-1):** anchored to the measured 30 V LDMOS, scaled per class; 80-200 V via silicon-limit scaling anchored at 30 V. `[ruled]`

**Phase 3 applied these** (F1/F2/F-VD3 VDMOS; F6/F3 BSIM3; F7 passives; BJT; D6 NMOS12). See `CHANGELOG.md`, `sizing-guide.md`, and `sizing-open-findings.md`.

---


**What this is.** The AutoHV realism audit (phases 0–2) surfaced a set of *open maintainer
declarations* — process facts the synthetic PDK never states, that several fixes depend on. This
document answers all seven, grounding each against a real commercial process where the evidence
exists and recording the audit default where it does not. **It is the constitution: future sessions
are held to these declarations.**

**Grounding source.** The declarations tagged `[declared-grounded]` are grounded against **a
commercial 0.25 µm mixed-signal BCD process** (design manual, electrical specification, and SPICE
model library). 0.25 µm and 0.18 µm are adjacent generations, so passive, junction, mismatch, and
temperature values carry with light or no scaling; core-device values carry a stated voltage-class
mapping; anything HV/LDMOS is extrapolation and tagged as such. **No third-party values are reproduced
here** — everything below is derived, scaled to the 180 nm/BCD context where needed, and rounded to
sensible engineering figures. The raw crosswalk lives in an uncommitted local file.

**Status tags.** `[declared-grounded]` — set from the reference process. `[declared-default]` — the
reference process was silent; the audit default stands. Every entry states what it unblocks.

**Discipline.** Where a grounded value contradicts something the audit or the repo history previously
argued, both positions are on the record; the maintainer arbitrates.

---

## The headline reframing (read before the seven)

The reference process demonstrates one fact that reorganises three of the seven declarations at once:

> **An LDMOS gate oxide is set by the device's GATE voltage rating, not its DRAIN rating.** In the
> reference process the HV devices are named by both — a 200 V-drain / 5 V-gate LDMOS carries the
> **thin 5 V gate oxide (~13 nm)**, not a thick one. A 40 V-drain / 12 V-gate variant carries the
> 12 V oxide (~31 nm). The drain standoff is handled by the drift region and well spacings, entirely
> separately from the gate dielectric.

This directly contradicts the audit's phase-1 §2.7 *theta*-implied oxide ladder, which assumed the
VDMOS gate oxide **rises with drain voltage** (25–30 nm at 20 V toward 60–100 nm at 200 V). That
assumption is not how a real BCD LDMOS is built. **AutoHV's VDMOS should declare a gate-voltage rating
per device, and set the gate oxide from that — flat across drain-voltage classes, not rising.** This
is carried into D1, D2, and the D4 note below.

---

## D1 — VDMOS `W_REF` meaning · `[declared-default]`, partially grounded

**Question.** Is `W_REF = 10 µm` a genuine 10 µm drawn cell, or a label on a larger power device?

**What the reference process shows `[grounded]`.** It *has* a full LDMOS module — 30 V, 40 V, and
200 V drain classes, plus a 700 V option — so the device family AutoHV models is real, not invented.
Two grounded conventions apply:
- **Width normalization is by fingers, each capped at ~100 µm drawn gate width;** wide power devices
  are multi-finger arrays of ≤100 µm legs. A "10 µm cell" is therefore a perfectly ordinary single
  finger — consistent with `W_REF = 10 µm` being a genuine drawn width, not a power-die label.
- **Drift-length scale:** ~1.7 µm (40 V/5 V-gate) rising to ~2.1 µm (40 V/12 V-gate); the 200 V
  standoff is set by ~20 µm well spacings, not a short drift. AutoHV's `L_REF = 8 µm` / RESURF window
  is in the right regime for the higher classes.

**Pass-2 update — F1 magnitude closed for the medium-voltage class by simulation.** The reference
model library is runnable for its 30 V LDMOS (the higher-voltage devices use a Verilog-A drift module
this ngspice build cannot compile). Local TT simulation on the 30 V device, normalized to the 10 µm
cell, gives **Ron·W ≈ 8400 Ω·µm, Idsat ≈ 0.33 mA/µm, BVdss ≈ 33.5 V** — see amendment
[`P2-1`](anchor-amendments-onc25.md). AutoHV's phase-2-measured NDMOS20 (Ron·W ≈ 2–6 Ω·µm, Idsat
≈ 1674 mA/µm) is ~3600× low on Ron·W and ~5000× high on Idsat, so **F1's ~10³× magnitude is now
grounded against a real medium-voltage LDMOS**, and fix #2/#3 have a measured target rather than only a
silicon-limit estimate. The **100–200 V** magnitude is not runnable (Verilog-A) and reverts to
maintainer declaration (silicon-limit ×2–5), now anchored to this 30 V point.

**What the electrical spec does not show.** No specific on-resistance (Rsp), BVdss, or cell-pitch value
is stated *in the spec tables* — that gap is what pass 2 closed by simulating the library instead.

**Declaration.** `W_REF = 10 µm` **is a genuine 10 µm drawn finger** — the audit's recommended
default, now positively supported by the finger-width convention. The power-die reading is rejected.
**Unblocks:** the F1 `kp`/`rd`/`rs` fix direction (10 µm-cell targets in the anchor stand); the fix
magnitude still needs either silicon Rsp or the maintainer's process assumption, which the reference
docs do not supply.

**Phase-4 Step-0 ruling — the 100–200 V ladder, now literature-bracketed.** Pass-3 grounded the
reference-process ladder only to 40 V (specific-Ron ∝ class^0.73). A survey of **published, production-class
0.18 µm-BCD LDMOS data** (openly citable — these are ISPSD/IEDM-class publications, unlike the reference
process) closes the extrapolation:
- In **Rsp space** the exponent is **two-regime**: ~0.73 below ~40 V (fixed overheads dominate), but
  **~1.9–2.2 above** (drift-dominant, measured across published 55–128 V BVdss ladders).
- **Cell pitch grows ~linearly** with class, so in **per-width Ron·W space** the high regime flattens to
  exponent **~1.0–1.2**.
- Production-class **200 V silicon lands at Rsp ≈ 6–12 mΩ·cm²** (1.3–2.7× the 1-D ideal limit), i.e.
  **Ron·W ≈ 33–60 kΩ·µm** at a ~20 µm pitch.

**Ruling (implemented phase-4):** the per-width Ron·W ladder is **two-regime, continuous at the grounded
30 V / 8400 Ω·µm anchor** — exponent **0.73 below 40 V** `[grounded]`, **~1.0–1.2 above 40 V**
`[literature]`. Rungs: 60 V ≈ 15, 80 V ≈ 21, 120 V ≈ 32, 200 V ≈ 45 kΩ·µm (band 33–60). The pass-3
single-exponent 200 V value (33 kΩ·µm) is now the optimistic band edge; the retired BV^1.2 value
(86 kΩ·µm) stays retired. P-channel carries the grounded 2.5×→~3× rising mobility penalty on top.

Supporting public literature (citable openly):
1. J. A. Appels & H. M. J. Vaes, "High Voltage Thin Layer Devices (RESURF Devices)," *IEDM Tech. Dig.*, 1979, pp. 238–241 — the RESURF principle that flattens Rsp-vs-BV below the 1-D limit.
2. C. Hu, "Optimum Doping Profile for Minimum Ohmic Resistance and High Breakdown Voltage," *IEEE Trans. Electron Devices*, vol. ED-26, no. 3, 1979 — the ideal silicon-limit Rsp ∝ BV^~2.5 the drift regime approaches.
3. B. J. Baliga, *Fundamentals of Power Semiconductor Devices*, 2nd ed., Springer, 2019 — specific on-resistance vs breakdown scaling and pitch normalization for lateral (LDMOS/RESURF) devices.

---

## D2 — VDMOS gate-oxide ladder · `[declared-grounded]`

**Question.** What is the VDMOS gate-oxide thickness per class, and does it rise with voltage?

**Grounded facts.** The reference process's gate-oxide ladder, by **gate** voltage class, is
approximately **6, 7.5, 13, and 31 nm for the 2.5, 3.3, 5, and 12 V classes** — a highly consistent
**~2.5 nm/V reliability slope** (electrical; ~2.0–2.5 nm/V physical). The 12 V oxide is a real, thick,
dedicated dielectric — not an extrapolation.

**Declaration.** AutoHV VDMOS devices should **declare a gate-voltage rating** and take the gate oxide
from the ~2.5 nm/V slope at that rating — **not** from the drain rating:
- a **5 V-gate** LDMOS (the common case) → **~13 nm** gate oxide, *flat across all drain classes*
  (20 V…200 V);
- a **12 V-gate** LDMOS → **~31 nm**.

**Contradiction with the audit, both positions recorded.** Phase-1 §2.7 proposed a *theta*-implied
oxide **rising with drain voltage** (25–30 nm at 20 V → 60–100 nm at 200 V), and phase-2 D4 built its
"6 numbers vs 13 derivations" analysis on that rising ladder. **The reference process contradicts the
rising ladder:** real LDMOS gate oxide is set by the gate rating and is flat across drain classes.
Two readings of the *theta* evidence remain open for the maintainer:
1. If AutoHV's VDMOS are intended as **5 V-gate** devices, the correct declaration is **~13 nm flat**.
   The audit's *theta* fit then reflects series resistance and short-channel effects, not a true oxide
   ladder, and the phase-1 §2.1 kp residual is the **flat-tox 12.7×** — i.e. the larger fix (per-class
   trim, ~6 numbers, per phase-2 D4 hypothesis (a)).
2. If they are **12 V-gate** devices, **~31 nm flat**.

Either way the ladder is **flat by gate class, not rising by drain class.** **This is the single most
important thing the maintainer must decide, and the reference process says the axis the audit used was
the wrong one.**

**Vth-vs-tox tension resolved.** The audit noted AutoHV's `vto = 1.00–1.31 V` sits awkwardly against a
thick rising oxide. Grounded: a 5 V-gate LDMOS in the reference process has `vth0 ≈ 0.89 V` on the
13 nm oxide — a ~1 V threshold on a ~13 nm gate is entirely ordinary, so the tension dissolves once
the oxide is read as gate-set and flat. **Unblocks:** fix #2 scoping (D4), and the `theta`/`ksubthres`
re-ladder work.

---

## D3 — BJT/diode `AREA = 1` cell · `[declared-default]` → **`[declared-grounded]` (pass 3)**

**Question.** What physical area does `AREA = 1` correspond to?

**What the spec/library showed (passes 1–2).** Bipolar devices are specified by named size variants (a "5"
and a "10" flavour) but the **emitter unit geometry, Is/area, cje and cjc were not stated** — silence.
Diode Is/area and cjo/area likewise not given.

**Pass-3 grounding — the device catalog gives the emitter geometry.** The bipolar sections state the
supported emitter sizes directly: **square emitters, minimum 2×2 µm (4 µm²), and named variants at
5×5 µm (25 µm²) and 10×10 µm (100 µm²)**. **AutoHV's `AREA = 1 ≡ 100 µm²` is exactly the large "10"
variant (10×10 µm) — a real, supported emitter geometry, not an invented round number.** D3 therefore
regrades from `[declared-default]` to **`[declared-grounded]`**: the reference emitter menu spans
4–100 µm² and AutoHV's default sits at the top of it. The residual `is`-vs-`cje`/`cjc` internal
disagreement (below) is unchanged — that is an internal-consistency fix, now with a grounded cell size.

**Indirect grounding.** They *do* pin the electrical behaviour a unit device must reproduce — β in the
mid-teens, VAF ≈ 60–70 V, Vbe ≈ 0.7 V in the µA range (see D4). Whatever `AREA = 1` is declared to be, it must land
those. AutoHV's `is`-implied area (4–80 µm²) and its `cje`/`cjc`-implied area (300–900 µm²) disagree
by 27–88× (phase-1 §4.1); the reference process gives no basis to prefer one over the other, so the
disagreement must be resolved by internal consistency, not by grounding.

**Declaration.** **`AREA = 1 ≡ 100 µm²`** as the audit default (a round, mid-scale emitter), pending a
maintainer choice. **Unblocks:** nothing new — this stays an open internal-consistency fix
(reconcile `is` vs `cje`/`cjc`), now with grounded *electrical* targets (D4) it must hit.

---

## D4 — BJT class (fT) · `[declared-grounded]`

**Question.** What fT does a 0.25 µm-generation junction (non-SiGe) bipolar actually deliver — is
AutoHV's 3.5 GHz NPN period-typical?

**Grounded facts.** The reference process's vertical NPNs deliver **fT ≈ 1 GHz-class** (roughly 0.7–1.3 GHz), with
**β in the mid-teens** and **VAF ≈ 60–70 V**; its substrate PNPs are tens of MHz, β ≈ 2–3. These are deliberately
robust, low-β BCD bipolars.

**Declaration and the two positions.**
- **fT:** a real junction bipolar in this generation tops out around **~1 GHz**. AutoHV's NPN_LV at
  3.5 GHz is therefore **at or beyond the optimistic edge**, not conservative — the phase-1 expectation
  ("3.5 GHz is period-typical") is **partly overturned**: 3.5 GHz is high for a non-SiGe junction NPN,
  ~3× this reference process. Grounded fT anchor: **1 GHz-class, band ~0.5–2 GHz** for a BCD junction NPN.
- **β:** the reference process runs β in the mid-teens; AutoHV uses β = 140. **These do not agree, and both
  positions belong on the record:** this particular BCD process trades β for HV robustness and runs
  low, but many general-purpose BiCMOS flows do reach β = 100–200. β is a design/architecture choice,
  not a generation constant, so it is **not** grounded to 17 — AutoHV's 140 is defensible for a
  general-purpose NPN. **What is grounded is fT and VAF**, which are physics-limited.

**Unblocks:** the `ft_at_peak` anchor (currently marked contested/descriptive) can move to a grounded
~0.5–2 GHz band; F-BJT1's severity is confirmed but reframed — the *modelled* 3.5 GHz tf ceiling is
itself optimistic, so the effective-fT collapse to 265 MHz at 100 µA is doubly a concern.

---

## D5 — flicker noise · `[declared-grounded]` (F3), partially

**Question.** Grounded BSIM-convention flicker parameters, and grounded flicker-corner bands.

**Decisive fact (corrected in pass 2).** AutoHV's BSIM3 (level 49) MOS cards carry the flicker
oxide-trap triplet `noia`/`noib`/`noic` at the values that are the **stock BSIM4 defaults** — the
canonical `level=54` default set for n- and p-channel. They are placed in BSIM3 (`level=49`) shells,
where the model interprets that triplet in a different unit convention (~6×10²¹ off). F3 is therefore
**BSIM4 default noise parameters in a BSIM3 card**, a units/model-level mismatch — not invented values.

Pass 2 checked this against the reference process's own model library and found the reference is
**not** the source: its p-channel `noia` is a custom value it does *not* share with AutoHV, and its
n-channel third coefficient differs from AutoHV's as well. So nothing was "lifted" from any specific
process — both AutoHV and the reference simply start from the BSIM4 defaults, and the reference then
customised where AutoHV did not. (The pass-1 draft of this section stated the values matched the
reference "digit-for-digit"; that was both inaccurate and an over-disclosure, and is retracted.)

**Declaration.** Two grounded fix paths, maintainer's choice (this is F3's open decision, now sharpened):
1. **Migrate the 8 MOS cards to BSIM4 (level 54)** — then the existing `noia/noib/noic` are *correct*
   as-is, because that is the model whose defaults they are. This is also what the reference process
   runs (level 54). Lowest-surprise, and gains a better core model.
2. **Keep BSIM3 (level 49)** and convert the three coefficients to BSIM3 units (`noia` ~10²⁰-class).

Either lands the flicker corner in a physical band. **Flicker-corner anchor `[grounded]`:** the
reference process specifies no 1/f corner frequency directly (silence on the corner Hz), so the
`[industry]` 100 kHz–1 MHz class band **stands as a default**, but the *parameter* fix is now fully
grounded. **BJT flicker (F4):** the reference bipolar spec gives no KF/AF — silence; AutoHV's F4 fix
(`kf ≈ 1e-15`, `af ≈ 1.5–2`) remains the audit default. **Unblocks:** F3 (fully), the level-49-vs-54
decision; F4 stays default.

---

## D6 — NMOS12 device type · `[declared-grounded]`

**Question.** Is AutoHV's 12 V pair a thick-oxide planar MOS or a drain-extended device, and what are
its `tox` / `Lmin`?

**Grounded facts.**
- The reference process's 12 V devices are **drain-extended only** — there is **no planar 12 V MOS**.
  The 12 V rating always comes with a thick (~31 nm) gate oxide on an LDMOS/STI-drain structure.
- The absolute **poly-width floor is 0.24 µm**, and the thinnest planar Lmin (the 5 V device) is
  **0.50 µm**.
- The 12 V gate oxide is **~31 nm** (~2.6 nm/V, on the ladder slope).

**Declaration.**
- **`tox ≈ 31 nm`** for a true 12 V gate — the audit's "thick-oxide, 24–30 nm" ruling is **confirmed
  and tightened**. AutoHV's current 20 nm is too thin by ~1.5×.
- **`Lmin`:** the current **0.15 µm is impossible** — below the 0.24 µm poly floor, and a 12 V device
  is not planar in a real process. Declare **`Lmin = 0.50 µm`** (the 5 V planar floor) at minimum, or
  reclassify NMOS12 as drain-extended. `device_limits.csv` must be corrected.
- **Idsat / u0 / rdsw:** scale from the reference 5 V device (µ0 ≈ 490 n / 130 p cm²/V·s; the 12 V
  device's thicker oxide lowers Cox → lower drive), tightening the four phase-2 NMOS12 fix targets.

**Unblocks:** the NMOS12 fix cluster (tox, Lmin, u0, rdsw) and the `device_limits.csv` Lmin correction.

---

## D7 — qualification temperature range · `[declared-default]`

**Question.** What operating/qualification temperature range should the PDK declare?

**What the reference process shows.** **Silence** — no single stated operating/qualification range,
no AEC-Q grade. The highest temperature referenced anywhere is **150 °C** (10-year reliability tables
at 27/125/150 °C; electromigration reference 110 °C). No lower bound is stated.

**Declaration.** **−40 … +150 °C** — the audit default (automotive BCD), now with the note that the
reference process references **150 °C as its ceiling** and states no low end. Adopt directly; state it
explicitly in the model files (currently absent — phase-1 §4.4). **Unblocks:** every tempco sweep and
the qualification-range statement the model files lack.

---

## Grounding sweep → anchor amendments

Beyond the seven, the same documents ground a large fraction of the 447 anchor entries — sheet
resistances, poly TC signs (F7), MOS Idsat/Vth/S, mismatch AVT and its convention, MIM density/VCC/TCC,
and zener bv tempco. Those are written up as proposed band changes in
[`anchor-amendments-onc25.md`](anchor-amendments-onc25.md), **not applied here** — the maintainer
applies them together with the outstanding phase-2 audit amendments.

The three highest-value grounded results feeding that file:
1. **F7 (poly TC sign) — decisively grounded.** The reference process's poly TC crosses zero at
   ~250 Ω/□ and goes to **−1400 ppm/°C at high sheet**; AutoHV's RPOLY_HI (+656) is wrong-sign, now
   against real silicon.
2. **Mismatch AVT convention — grounded.** The foundry's own rule is **AVT ≈ 1 mV·µm per nm of oxide**
   (their footnote), and the model implements it as a **1σ** coefficient — reconciling AutoHV's **3σ**
   literals is a factor-of-3, now anchored.
3. **Zener bv tempco — grounded.** Real buried zeners run **+1 to +3.6 mV/°C, rising with bv, zero-TC
   crossover near 6.2 V**; AutoHV models 0. Directly grounds the missing-tempco fix.

---

## Gaps — dispositions after checking BOTH the spec and the model library

**Updated in pass 2.** Pass 1 declared several items "silent" from the spec alone. Pass 2 mined the
model library and ran local LDMOS simulation. Each pass-1 gap now carries an explicit disposition:
**closed** (grounded value found, in the amendments) or **confirmed silent** (checked spec *and*
library, genuinely absent). "Silent" is only claimed where both places were checked.

| pass-1 gap | pass-2 disposition | grounded value / fallback |
|---|---|---|
| **VDMOS Ron·W, Idsat, BVdss (MV class)** | **CLOSED — simulation** | 30 V LDMOS: Ron·W ~8400 Ω·µm, Idsat ~0.33 mA/µm, BVdss ~33.5 V (amendment P2-1). Closes the F1 magnitude for the medium-voltage class. |
| **VDMOS Rsp/BVdss/pitch (HV 100–200 V)** | **confirmed silent (sim)** — drift is a Verilog-A module this ngspice cannot run | silicon-limit ×2–5, now anchored to the measured 30 V point |
| **VDMOS `kp` absolute magnitude** | **CLOSED for MV** (has a measured Idsat/Ron target); HV still declaration | amendment P2-1 + D2 oxide decision |
| **MOS junction cap densities (cj, cjsw)** — F6 | **CLOSED — simulation** | n+/pw ~1.4 fF/µm², p+/nw ~1.5, cjsw ~0.1 fF/µm, vj/m grounded (amendment P2-2) |
| **Diode Is/area, ideality n, cjo/area** | **CLOSED — library + sim** | is ~2.6e-19, n ~1.0, cjo ~1.4–1.5 fF/µm² (amendment P2-4); cjo/area still AREA-conditional (D3) |
| **MOS Vth tempco, mobility exponent** | **CLOSED — library** | dVth/dT −1.0…−1.6 mV/°C (`kt1`), `ute` −1.2…−1.6 (amendment P2-3) |
| **Subthreshold slope 2.5/3.3 V** | **CLOSED — library** | `nfactor`/`voff` per class extracted; consistent with 72–96 mV/dec |
| **Correlated FF/SS corner definitions** | **CLOSED as bands** | synthesized from LSL/Nom/USL (amendment P2-5); uncorrelated upper bound |
| **BJT `kf`/`af` (F4)** | **confirmed silent — spec + library** | absent in both; F4 fix stays audit default (`kf ≈ 1e-15`, `af ≈ 1.5–2`) |
| **BJT Is/area, cje, cjc, emitter geometry** | **confirmed silent** — composite subckt, GP sub-cards give no clean device density | audit default; D3 `AREA=1≡100 µm²`; VAF/tf are grounded |
| **Resistor voltage coefficient (VCR)** | **confirmed silent** — no `vc1/vc2` in the models; diffusion-R voltage dependence is *structural* (JFET pinch), not a coefficient | AutoHV's explicit VCR stays **fully synthetic** |
| **MIM matching (%·µm)** | **confirmed silent — spec + library** | audit `[industry]` |
| **Flicker corner frequency (Hz)** | **confirmed silent** — parameters grounded (BSIM4-default noise; per-class `kf/af`), corner-Hz not specified | `[industry]` 100 kHz–1 MHz default |
| **Anything above 12 V not in the LDMOS module** | **confirmed silent** — reference HV is all drain-extended | audit defaults, tagged extrapolation |

**Net after two passes:** the grounding now reaches the passive TC/sheet/matching, MOS
Vth/Idsat/S/tempco/mismatch/junction-caps, diode Is/n/cjo, MIM, zener tempco, corner-spread magnitudes,
and — by simulation — the **medium-voltage LDMOS DC magnitude (the F1 core, for the 30 V class)**. What
remains genuinely synthetic, confirmed silent in both spec and library: the **100–200 V LDMOS DC scale**
(Verilog-A, not runnable), the **BJT/diode absolute per-cell scale** (composite devices, no unit
geometry), and the **resistor VCR** (structural, no coefficient). Those close only by silicon or explicit
maintainer assumption.

---

# Pass 3 — the Device Catalog: regrades, the ladder ruling, and the freeze line

A third reference source — the process's full **device catalog** (per-device datasheet sections) — was
mined for exactly the items passes 1–2 marked "silent for simulation" (the ≥40 V LDMOS, whose drift is a
Verilog-A module the local build can't run) and "silent electrically" (specific Ron, BVdss, emitter
geometry, zener/Schottky detail, output conductance). It closed most of them. The proposed band changes
are in [`anchor-amendments-onc25.md`](anchor-amendments-onc25.md) §"Pass 3"; this section records the
**status regrades**, the **ladder-exponent ruling**, the **D2 external validation**, the **final gaps
dispositions**, and the **synthetic-residue freeze line**.

## Status regrades (pass 3)

| declaration | was | now | basis |
|---|---|---|---|
| **D3** BJT/diode `AREA=1≡100 µm²` | `[declared-default]` | **`[declared-grounded]`** | the catalog states the emitter menu: 2×2 / 5×5 / 10×10 µm. 100 µm² = the real 10×10 emitter. |
| **D1** HV LDMOS DC scale (100–200 V) | confirmed silent (Verilog-A) | **`[extrapolated-fitted]`** on a **grounded exponent** | the 40 V class is now tabulated directly (Rsp/BVdss/JDLIN); the Ron·W-vs-class exponent is fitted (0.73±0.07). Absolute 100–200 V still extrapolation, but no longer a guess. |
| **D4** BJT class | `[declared-grounded]` (fT/VAF; β contested) | **`[declared-grounded]`, β framing refined** | the catalog's HV NPN reaches β≈65 and fT tops at ~1.4 GHz — see the D4 note below. |
| **D2** VDMOS gate-oxide ladder | `[declared-grounded]` | **`[declared-grounded]` + externally validated** | the same drain class ships in 5 V-gate and 12 V-gate variants — see the D2 note below. |

## The Ron·W ladder-exponent ruling (T1) — **BV^0.75 confirmed, BV^1.2 retired**

Phase 3 shipped a `Ron·W = 8400·(BV/30)^1.2` ladder; phase 3b replaced it with `^0.75`. The two differ
~2.4× in on-resistance at 200 V, and the choice was previously an engineering judgement (physical
lateral-RESURF favours the lower exponent) with no direct data.

**The catalog now supplies the data.** Extracting characterized specific on-resistance and BVdss for the
real N-LDMOS ladder at 12/24/30/40 V drain classes (plus the pass-2 simulated 30 V point, which lands
exactly on the catalog 30 V value), a log-log least-squares fit of specific-Ron vs drain class across the
architecturally-consistent RESURF family gives an exponent of **+0.73 ± 0.07 (R² = 0.99)**. The
P-channel extended-drain ladder gives 0.76–0.89.

> **Ruling proposal: the reference data confirms `BV^0.75`. Phase-3's `BV^1.2` is retired** — it predicts
> a 200 V on-resistance 2.35× too high and lies far outside the fitted 0.73 ± 0.07 band. The 30 V
> anchor (8400 Ω·µm) is dead-on the real 8500–8700 Ω·µm. The N and P ladders share the exponent within
> error; the **P/N per-µm penalty ≈ 2.5×** (area basis) is confirmed, rising mildly to ~2.7–3.2× by 40 V.
> **20–40 V rungs are `[grounded]`; 60–200 V ride the grounded exponent on extrapolated absolute values
> (`[extrapolated-fitted]`), with no claim of grounding above 40 V drain / ~55 V measured breakdown.**

## D2 external validation (two-gate-flavor structure)

The catalog confirms the D2 headline directly and independently: **the same drain class appears in both a
5 V-gate and a 12 V-gate variant** (e.g. a 44 V-drain device exists as both a 5 V-gate part, |Vgs|≤5.5 V,
and a 12 V-gate part, |Vgs|≤12 V). The gate oxide tracks the **gate** rating — 5 V-gate → ~13 nm class
(the SOA gate limits, ±7 V absolute / ±5.5 V DC, imply ~2.5 nm/V × 5.5 ≈ 13.7 nm), 12 V-gate → ~31 nm
class — while the drain standoff is handled entirely by the drift/well spacings. This is exactly the
"oxide follows gate, not drain" reframing D2 rests on, now confirmed by a device the process actually
ships in both flavors. **AutoHV's 13/31 nm gate-oxide ladder is externally validated.**

## D4 β-framing refinement

Passes 1–2 characterized the reference NPN as "mid-teens β, deliberately low-β BCD." The catalog's fuller
menu refines this: the HV NPN flavor reaches **β ≈ 65**, the low-β HV flavor β ≈ 18, the LV NPN β mid-teens,
and the substrate/isolated PNPs β ≈ 2.8–5.5. So the reference **does** offer a moderate-β (65) NPN — the
menu spans β 2.8–65. Peak **fT tops out at ~1.4 GHz** (LV NPN), the HV flavors at 0.3–0.56 GHz. This
narrows the AutoHV gap: NPN_LV's **β = 140 is ~2× the best real NPN** (was framed as ~8× vs mid-teens),
and its **fT = 3.5 GHz is ~2.5× the fastest real junction NPN** (~1.4 GHz). The D4 conclusion stands —
fT is physics-limited and AutoHV sits at the optimistic edge; β is a design choice and remains defensible
— but the β gap is smaller than passes 1–2 implied.

## T6 — the last flattering parameter (output conductance)

The catalog reports device λ directly, and local simulation of the runnable 5 V CMOS and 30 V LDMOS
reproduces it (λ 0.05 vs catalog 0.06 for the 5 V NMOS; λ 0.0079 for the 30 V LDMOS at full drive). Real
output resistance is far lower than AutoHV's: **5 V CMOS VA ~17–20 V at Lmin; MV LDMOS VA ~130 V (drive)
to ~1800 V (near-threshold)**. AutoHV's 200 V device measured **VA ≈ 3900 V sits above the entire real
envelope at every bias** — the known remaining flattery is now quantified and given a re-fit target
(VA ~300–1000 V), amendment P3-4.

## Final gaps table — every remaining gap gets a terminal disposition

Pass 3 is the last grounding pass. Each item is now **closed**, or **permanently synthetic** with its
declared error bar. Nothing is left "open for a later pass."

| item | disposition after pass 3 | grounded value / permanent error bar |
|---|---|---|
| **VDMOS Ron·W / BVdss / Idsat, MV (30–40 V)** | **CLOSED — catalog + sim** | 30 V Ron·W 8500 Ω·µm, 40 V 9500; BVdss 1.2–1.4× class; exponent 0.73±0.07 |
| **VDMOS DC scale, 60–200 V** | **closed — literature-bracketed (phase-4 Step-0)** | two-regime ladder: 0.73 below 40 V (grounded), ~1.0–1.2 above (published 0.18 µm-BCD data); 200 V band 33–60 kΩ·µm, ±~35 %. |
| **BJT emitter geometry / `AREA=1` cell** | **CLOSED — catalog** | square emitters 2×2 / 5×5 / 10×10 µm; `AREA=1≡100 µm²` = the 10×10 device (D3 grounded) |
| **Output conductance λ / VA (CMOS + LDMOS)** | **CLOSED — catalog + sim** | 5 V CMOS VA ~17–20 V; MV LDMOS VA ~130–1800 V; 200 V re-fit target ~300–1000 V |
| **Depletion LDMOS Idss / Vth** | **CLOSED — catalog** | Idss ~100 µA/µm (Vgs=0), Vth ~−1.65 V; DNMOS20 54.7 µA/µm is ~2× low |
| **Zener bv tempco (sign + magnitude)** | **CLOSED — catalog** | +1.1…+3.6 mV/K, rising with bv, zero-TC crossover ~6.2 V |
| **Schottky Vf / BV / recovery** | **CLOSED — catalog** | BV 25/38/50 V, Vf ~0.2 V @1 µA; **no recovery term (majority-carrier) → DIO_SCH tt≈0**, not 300 ps |
| **Per-device matching (AVT)** | **CLOSED — catalog** | 5 V CMOS AVT ~6/5 mV·µm, LDMOS ~20 mV·µm; confirms the v1-sized coefficients |
| **Corner bundles (one MOS class)** | **CLOSED — catalog** | 5 V LSL/USL: Vth ±135 mV, Idsat ±14 % — confirms the pass-2 synthesis |
| **Zener cjo / area** | **permanently synthetic** — buried in the reference subcircuit, no density row | bound to the junction-diode density class, ~1–1.5 fF/µm² × junction area (±2× bar) |
| **Resistor VCR (voltage coefficient)** | **permanently synthetic** — no coefficient in spec, model, or catalog; diffusion-R dependence is structural | AutoHV's explicit VCR remains invented (±100 % of itself) |
| **Flicker corner frequency (Hz)** | **permanently default** — parameters grounded, corner-Hz stated nowhere | `[industry]` 100 kHz–1 MHz |
| **BJT/diode absolute `is`-per-cell** | **internal-consistency, not grounded** — cell size now grounded (D3), `is`-vs-`cje`/`cjc` split still unresolved by any source | reconcile internally to the 100 µm² cell |

## Synthetic residue — the freeze line

**This is the definitive list of what in this PDK is invented rather than grounded, and by how much.**
After three grounding passes plus the phase-4 public-literature ladder ruling, everything else in the
anchor set is tied to a real commercial 0.25 µm automotive BCD process (directly, by class-mapped
scaling, or by grounded-exponent extrapolation) or to open ISPSD/IEDM-class literature. **After phase-4
the residue is three items and nothing else:**

1. **200 V absolute on-resistance/breakdown scale** — *literature-bracketed* (no longer purely
   extrapolated). The two-regime ladder is anchored ≤40 V to reference silicon and 60–200 V to published
   0.18 µm-BCD LDMOS data (Appels-Vaes RESURF; Hu silicon-limit; Baliga). **Error bar: ±~35 % on Ron·W at
   200 V** (the published 33–60 kΩ·µm band). Tightening further needs a specific 200 V production part.
2. **BJT/diode per-area absolutes at the declared 100 µm² cell** — the emitter geometry is grounded
   (100 µm² = the real 10×10 emitter, D3), but the `is`-vs-`cje`/`cjc` split within that cell is an
   internal-consistency choice no source tabulates. **Error bar: the per-area `is` factor, ±cell-choice.**
3. **Resistor voltage coefficient (VCR)** — *structural stand-in*. No VCR coefficient appears in spec,
   model, or catalog; the real diffusion-R dependence is structural (JFET pinch). **Error bar: ±100 % —
   order-of-magnitude only.**

Two further items are grounded-parameter / industry-default, not "invented," and are noted for
completeness only: **flicker corner-frequency** (parameters grounded; corner Hz an industry 100 kHz–1 MHz
default) and **NPN β = 140** (a declared design choice above the reference menu's 65 — physics permits it;
general-purpose BiCMOS reaches 100–200 — flagged so no one mistakes it for grounded).

**Everything not on this list is grounded, class-mapped-scaled, or literature-bracketed.** With this,
the realism program **freezes**: subsequent work on this PDK is design work, and model changes ride the
normal fix process against these frozen anchors. All three reference sources (spec, model library, full
device catalog) plus the public 100–200 V literature have now been mined; no further grounding passes
are planned.
