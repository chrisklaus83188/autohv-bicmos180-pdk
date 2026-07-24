# Process Declarations — AutoHV BiCMOS180 PDK

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

## D3 — BJT/diode `AREA = 1` cell · `[declared-default]`

**Question.** What physical area does `AREA = 1` correspond to?

**What the reference process shows.** Bipolar devices are specified by named size variants (a "5"
and a "10" flavour) but the **emitter unit geometry, Is/area, cje and cjc are not stated** — silence.
Diode Is/area and cjo/area are likewise not given. So the reference docs cannot ground the unit-cell
area directly.

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
