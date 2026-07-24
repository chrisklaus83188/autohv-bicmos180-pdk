# Model Realism Audit — AutoHV BiCMOS180 PDK (Phase 1, static)

**Method:** read the model definitions, check against device physics and industry-typical 180 nm BCD
values. No ngspice was run; no PDK file was modified. All numbers are reading plus arithmetic.
**Companion outputs:** [`anchor-values.md`](anchor-values.md) and [`anchor-values.json`](anchor-values.json) — the golden bands phase 2 asserts against.
**Prerequisite reading:** [`characterization-inventory.md`](characterization-inventory.md).

**Provenance tags** on every claim: `[model]` read from the PDK · `[physics]` derived, formula shown ·
`[industry]` typical published/experience value, basis stated · `[inventory]` cited from the inventory.

**Sigma convention.** Every mismatch literal in this PDK is a **3σ** bound (HSPICE AGAUSS,
`[inventory]` §4.5). All Pelgrom comparisons below convert to **1σ = X/3** first, and every quoted
sigma states which it is.

---

## 0. Executive summary

Seven findings block realism. Ranked by severity × breadth:

| # | Finding | Devices | Factor | Severity |
|---|---|---|---|---|
| **F1** | **LDMOS DC scale confirmed across all 13 cards** — and `kp` and `rd`/`rs` are displaced by *different amounts in opposite directions*, so this is **not one slip** | 13 VDMOS | `rd`+`rs` ~10³× uniformly; `kp` 287×–3649×, sloped | blocks-realism |
| **F2** | **VDMOS capacitances are still 3–48× too large after the June-2 ÷1000 fix**, and the residual is voltage-class-sloped. The fix was verified on NDMOS200 — the one card where ÷1000 was nearly right | 13 VDMOS | `cgs` 3.3×–48×; `cgdmax` 2.3×–35× | blocks-realism |
| **F3** | **BSIM3 flicker parameters are verbatim BSIM4 defaults in `level=49` cards** | 8 BSIM3 | ~6.25×10²¹ | blocks-realism |
| **F4** | **BJT `kf`/`af` placeholder** → flicker corner 3.12 MHz, current-independent | 4 BJT | 312–3121× | blocks-realism |
| **F5** | **Zener `cjo` is a hand-picked ladder, not derived** — residual after doping is non-uniform (101×/133×/196×), so no single divisor fixes it | 3 zeners | ~100–200× | blocks-realism |
| **F6** | **`AD/AS/PD/PS` unset on all 8 BSIM3 wrappers** → 100 % of junction capacitance and junction leakage absent | 8 BSIM3 | 74–83 % of drain node missing | distorts-results |
| **F7** | **RPOLY_HI `tc1 = +600 ppm/°C` has the wrong sign** for lightly-doped high-sheet poly | RPOLY_HI | sign | distorts-results |

Two checklist items came back **softer than the brief assumed** — reported as such in §2.7 and §2.8:
the VDMOS `theta` values and the body-diode `tt` values are defensible once the oxide/doping
assumptions are made explicit. One inventory finding is **withdrawn**: US Pat 12,464,737 is real (§6).

**What is genuinely good and should survive any fix:** the BJT avalanche `Bavl` construction and every
BVCEO/BVCBO ratio; the whole PNP_LAT DC parameter set; the Schottky thermionic-emission parameters;
all four capacitor densities and all VCC/TCC values; the BSIM3 18 V/33 V junction-cap trends; the
resistor VCR block; NDMOS200's `cjo` (the one VDMOS cap that lands in band).

---

## 1. The cross-family structural test

The test that caught both known scale bugs: **within one subcircuit, the transconductance, resistance,
capacitance, mismatch, and body-diode parameter groups must all imply the same device size.** Run on
all 13 VDMOS, `W_REF = 10 µm` `[model]`:

| Group | Implied size vs the drawn 10 µm | Shape across the ladder |
|---|---|---|
| `rd` + `rs` | **~950×–2660× (2× RESURF) / 2380×–6650× (5×)** | **roughly flat** — uniform slip signature |
| `kp` | **3649× (20 V) → 287× (200 V)** | **steeply sloped, 12.7× swing** |
| `cgs` / `cgdmax` | **48× (20 V) → 3.3× (200 V)** | **sloped, opposite direction to `kp`** |
| `cjo` | **0.25×–2.9×** | **flat and in band — correct** |
| mismatch (A_VT) | **0.65×–0.82× (20/60/120) vs 0.23×–0.30× (40/80/200)** | **bimodal — two ladders** |
| body diode `is` | 0.1×–10× of the Js band | flat, in band |

**This is the central result of the audit.** Five groups inside the same subcircuit imply five
different device sizes, and only two of them (`cjo`, body diode `is`) are consistent with the drawn
10 µm cell. `[inventory]` §6.1 records `BRIEF_pdk_realism.md` finding the `kp` and `R_on` routes
agreeing "to within ~2×" for the 200 V pair — **that agreement does not hold across the family.**

---

## 2. Tier 1 — VDMOS (13 cards)

### 2.1 F1 — implied width from `kp`

`[physics]` ngspice `VDMOS` has no W/L; size enters only through `m`. So
`Id_sat = (kp/2)(Vgs−vto)² · m`, and `kp = µ·Cox·(W/L_ch)` for the reference cell:

```
W_implied = kp · L_ch / (µ · Cox)        Cox = ε_ox/tox,  ε_ox = 3.9 × 8.854e-12 F/m
```

Inputs: `L_ch = 0.6 µm` `[model]` (`device_limits.csv`: *"gate/channel length (um); fixed at process
min"*); `µ_n = 400`, `µ_p = 130 cm²/V·s` `[industry]` (LDMOS p-body channel, below core NMOS because
of the high body doping needed for punchthrough control); `tox = 30 nm` nominal, band 20–50 nm
`[industry]`.

Worked example, NDMOS20: `Cox = 3.453e-11/30e-9 = 1.151e-3 F/m²`; `µCox = 400e-4 × 1.151e-3 =
4.604e-5 A/V²`; `W = 2.8 / 4.604e-5 × 0.6 µm = 36 489 µm`.

| device | `kp` [model] | W @20 nm | **W @30 nm** | W @50 nm | **ratio vs 10 µm** |
|---|---|---|---|---|---|
| NDMOS20 | 2.800 | 24 326 | **36 489** | 60 814 | **3649×** |
| PDMOS20 | 1.300 | 34 751 | **52 127** | 86 878 | **5213×** |
| DNMOS20 | 1.000 | 8 688 | **13 032** | 21 719 | **1303×** |
| NDMOS40 | 1.900 | 16 507 | **24 760** | 41 267 | **2476×** |
| PDMOS40 | 0.850 | 22 722 | **34 083** | 56 805 | **3408×** |
| NDMOS60 | 1.200 | 10 425 | **15 638** | 26 063 | **1564×** |
| PDMOS60 | 0.550 | 14 702 | **22 054** | 36 756 | **2205×** |
| NDMOS80 | 0.800 | 6 950 | **10 425** | 17 376 | **1043×** |
| PDMOS80 | 0.380 | 10 158 | **15 237** | 25 395 | **1524×** |
| NDMOS120 | 0.450 | 3 909 | **5 864** | 9 774 | **586×** |
| PDMOS120 | 0.210 | 5 614 | **8 420** | 14 034 | **842×** |
| NDMOS200 | 0.220 | 1 911 | **2 867** | 4 778 | **287×** |
| PDMOS200 | 0.088 | 2 352 | **3 529** | 5 881 | **353×** |

**Verdict: wrong, 287×–5213×. Severity: blocks-realism.** The ratio is *not constant* — it falls
12.7× from the 20 V to the 200 V card. A single uniform divisor **cannot** fix `kp`, unlike the
capacitance case.

### 2.2 F1 — implied width from `rd` + `rs`

`[physics]` 1-D unipolar silicon limit `Rsp,ideal = 5.9e-9 · BV^2.5 Ω·cm²`.
`[industry]` lateral RESURF penalty 2–5× over the ideal vertical limit.
`[industry]` cell pitch: 5 µm (20 V) → 7 / 9 / 11 / 15 / 22 µm (200 V).

```
Ron_physics(10 µm cell) = Rsp / A ,  A = 10 µm × pitch
W_implied = 10 µm × Ron_physics / Ron_model
```

Worked example, NDMOS20: `Rsp,ideal = 5.9e-9 × 24^2.5 = 1.665e-5 Ω·cm²`; at 2× RESURF `3.33e-5`;
`A = 10e-4 × 5e-4 = 5e-7 cm²`; `Ron_physics = 66.6 Ω` against `rd+rs = 0.070 Ω` `[model]` → **951×**.

| device | `rd+rs` | BV | pitch | Rsp ideal | Ron@2× | **ratio@2×** | ratio@5× |
|---|---|---|---|---|---|---|---|
| NDMOS20 | 0.070 | 24 | 5 | 0.0166 mΩ·cm² | 66.6 Ω | **951×** | 2378× |
| PDMOS20 | 0.110 | 22 | 5 | 0.0134 | 53.6 | **487×** | 1218× |
| DNMOS20 | 0.180 | 24 | 5 | 0.0166 | 66.6 | **370×** | 925× |
| NDMOS40 | 0.135 | 48 | 7 | 0.0942 | 269.1 | **1993×** | 4983× |
| PDMOS40 | 0.250 | 45 | 7 | 0.0801 | 229.0 | **916×** | 2290× |
| NDMOS60 | 0.240 | 75 | 9 | 0.2874 | 638.7 | **2661×** | 6653× |
| PDMOS60 | 0.530 | 70 | 9 | 0.2419 | 537.5 | **1014×** | 2535× |
| NDMOS80 | 0.380 | 95 | 11 | 0.5190 | 943.6 | **2483×** | 6208× |
| PDMOS80 | 0.830 | 90 | 11 | 0.4534 | 824.3 | **993×** | 2483× |
| NDMOS120 | 0.800 | 135 | 15 | 1.2494 | 1665.8 | **2082×** | 5206× |
| PDMOS120 | 1.730 | 128 | 15 | 1.0936 | 1458.2 | **843×** | 2107× |
| NDMOS200 | 1.750 | 225 | 22 | 4.4803 | 4073.0 | **2327×** | 5819× |
| PDMOS200 | 4.380 | 230 | 22 | 4.7334 | 4303.1 | **982×** | 2456× |

Stated the other way: **the model's specific on-resistance is 370×–2660× below the 1-D unipolar
silicon limit.** No lateral RESURF device can beat that limit; only a superjunction can, and not by
three orders of magnitude.

**Verdict: wrong, ~10³×. Severity: blocks-realism.** Unlike `kp`, the ratio is roughly **flat**
(N-channel: 951 / 1993 / 2661 / 2483 / 2082 / 2327 — a 2.8× spread with no trend above 40 V). This is
the clean uniform-slip signature. **A single divisor is a defensible fix for `rd`/`rs`; it is not for
`kp`.**

### 2.3 Conflict with `BRIEF_pdk_realism.md` — its `[assumed]` R_on is below the silicon limit

`[inventory]` §6.1 records the brief's `[assumed]` **2 mΩ·cm² specific R_on for the 200 V class**,
which it uses to back out an implied width of 2235 µm for NDMOS200.

`[physics]` the 1-D unipolar limit at 225 V is `5.9e-9 × 225^2.5 = 4.48 mΩ·cm²`.

**The assumed value is 2.24× below the ideal limit, and 4.48× below a 2×-RESURF lateral device.**
That assumption is not attainable by the device class in question. Presenting both positions as
required: the brief's R_on route is optimistic by ≥2.2×, which means the **true** disagreement between
its `kp` and `R_on` routes is larger than the 2.7× it reported — and the family-wide picture (§2.1 vs
§2.2) shows the two routes diverging by up to 12×, not converging. The brief's *conclusion* stands and
is strengthened; its supporting arithmetic on this one input should be corrected before it is filed.

### 2.4 F2 — capacitances re-derived from process densities

The June-2 fix `[inventory]` §3 applied a uniform ÷1000 **assuming** the 10 µm cell. Suggestion #1 of
`HANDOFF_vdmos_caps.md` — regenerate from process capacitance densities — was never carried out
`[inventory]` §6.2. Doing it now.

`[physics]`, assumptions stated so they can be attacked: gate oxide **30 nm**, field-plate oxide
**120 nm**, `L_ch = 0.6 µm`, source overlap `L_ov_s = 0.3 µm`, gate-over-drift `L_gd = 1.0 µm`,
drift doping from the RESURF condition `N_d ≈ 1e17 × (20/BV) cm⁻³`, `V_bi = 0.7 V`.

```
Cgs_der    = Cox_gate · W_REF · (L_ch + L_ov_s) = 1.151 fF/µm² × 10 µm × 0.9 µm = 10.4 fF
Cgdmax_der = Cox_gate · W_REF · L_gd            = 1.151 × 10 × 1.0            = 11.5 fF
Cgdmin_der = Cox_fp   · W_REF · L_gd            = 0.288 × 10 × 1.0            =  2.9 fF
cjo_der    = A_cell · sqrt(q·ε_si·N_d/(2·V_bi)) ,  A_cell = W_REF × pitch
```

| device | `cgs` [model] | derived | **×** | `cgdmax` [model] | derived | **×** | `cgdmin` | **×** | `cjo` [model] | derived | **×** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NDMOS20 | 499.2 fF | 10.4 | **48.2×** | 403.2 fF | 11.5 | **35.0×** | 35.0 fF | **12.2×** | 140 fF | 49.7 | 2.8× |
| PDMOS20 | 403.2 | 10.4 | **38.9×** | 345.6 | 11.5 | **30.0×** | 30.0 | **10.4×** | 150 | 51.9 | 2.9× |
| DNMOS20 | 201.6 | 10.4 | **19.5×** | 144.0 | 11.5 | **12.5×** | 12.0 | 4.2× | 70 | 49.7 | 1.4× |
| NDMOS40 | 336.0 | 10.4 | **32.4×** | 252.0 | 11.5 | **21.9×** | 22.0 | 7.7× | 100 | 49.2 | 2.0× |
| PDMOS40 | 252.0 | 10.4 | **24.3×** | 192.0 | 11.5 | **16.7×** | 17.0 | 5.9× | 105 | 50.8 | 2.1× |
| NDMOS60 | 211.2 | 10.4 | **20.4×** | 153.6 | 11.5 | **13.3×** | 14.0 | 4.9× | 75 | 50.6 | 1.5× |
| PDMOS60 | 144.0 | 10.4 | **13.9×** | 115.2 | 11.5 | **10.0×** | 10.0 | 3.5× | 65 | 52.4 | 1.2× |
| NDMOS80 | 135.0 | 10.4 | **13.0×** | 100.0 | 11.5 | 8.7× | 8.5 | 3.0× | 55 | 55.0 | **1.0×** |
| PDMOS80 | 95.0 | 10.4 | 9.2× | 75.0 | 11.5 | 6.5× | 7.0 | 2.4× | 45 | 56.5 | **0.8×** |
| NDMOS120 | 86.4 | 10.4 | 8.3× | 62.4 | 11.5 | 5.4× | 5.0 | 1.7× | 35 | 62.9 | 0.6× |
| PDMOS120 | 61.0 | 10.4 | 5.9× | 47.0 | 11.5 | 4.1× | 4.0 | 1.4× | 29 | 64.6 | 0.4× |
| **NDMOS200** | 48.0 | 10.4 | **4.6×** | 35.0 | 11.5 | **3.0×** | 3.0 | **1.0×** | 22 | 71.4 | 0.3× |
| **PDMOS200** | 34.0 | 10.4 | **3.3×** | 26.0 | 11.5 | **2.3×** | 2.5 | **0.9×** | 18 | 70.6 | 0.3× |

**Three results, and the third is the important one.**

1. **`cjo` is correct** — 0.25×–2.9× across the whole family, well inside assumption error. `[model]`
   NDMOS80's `cjo = 55 fF` against a derived 55.0 fF is an exact hit. **Verdict: OK. No action.**
2. **`cgs` and `cgdmax` are still too large by 3.3×–48×** even after the ÷1000. Anything beyond ~3× is
   a finding per the brief's own threshold; twelve of thirteen `cgs` values exceed it.
3. **The residual is strongly voltage-class-sloped** — 48× at 20 V falling monotonically to 3.3× at
   200 V. **The ÷1000 was approximately right for the 200 V pair and left the 20 V pair ~48× off.**

Result 3 explains why the error survived: `HANDOFF_vdmos_caps.md` diagnosed on a **40 µm NDMOS200**,
the CHANGELOG verified on the **same device**, and the permanent regression `coss_check.cir` tests
**only NDMOS200** with a threshold (`Cdrain < 1 pF` against a ~105 fF baseline) that is ~10× loose
`[inventory]` §2.3. The fix was validated on the one card where a uniform ÷1000 was nearly correct,
by a guard that cannot see the other twelve. This is a **coverage** failure as much as a modelling one.

**Verdict: `cgs`/`cgdmax` wrong, 3–48×, sloped. Severity: blocks-realism** (switching loss, gate
charge, dv/dt immunity and Miller plateau are all set by these). **`cgdmin` marginal** (0.9×–12×,
in band above 80 V). **`cjo` OK.**

### 2.5 F1 addendum — implied geometry disagreement, summarised

| device | W from `kp` | W from `rd`+`rs` (2×–5×) | **kp/rd disagreement** |
|---|---|---|---|
| NDMOS20 | 3649× | 951×–2378× | 2.43× |
| PDMOS20 | 5213× | 487×–1218× | 6.77× |
| NDMOS40 | 2476× | 1993×–4983× | 0.79× |
| NDMOS60 | 1564× | 2661×–6653× | 0.37× |
| NDMOS80 | 1043× | 2483×–6208× | 0.27× |
| NDMOS120 | 586× | 2082×–5206× | 0.18× |
| **NDMOS200** | **287×** | **2327×–5819×** | **0.08×** |
| PDMOS200 | 353× | 982×–2456× | 0.23× |

The two routes cross near 40 V and diverge to **12×** at 200 V. **Conclusion: `rd`/`rs` carry a clean
uniform ~10³ slip; `kp` carries a slip *and* a wrong ladder slope.** They are two separate defects
that happen to overlap, which is why a single-device analysis could see them as one.

### 2.6 F-VD3 — the non-monotonic mismatch ladder, resolved

`[model]` VDMOS: `DVTH_MM = MM_ON·AGAUSS(0,X,3)/sqrt(mtot)`, `mtot = (W/W_REF)·M`. So `X` is a **3σ
bound in volts at the 10 µm reference cell**.

`[physics]` 1σ = X/3; Pelgrom `σ_Vth = A_VT/sqrt(W·L)` → `A_VT = (X/3)·sqrt(W_REF · L_ch)`, with
`sqrt(10 × 0.6) = 2.449 µm`.
`[industry]` `A_VT ≈ 1 mV·µm per nm of tox, ±50 %` → at tox = 30 nm, expect **30 mV·µm (band 15–45)**.

Note the width-only area scaling is **legitimate** here — the channel length is fixed at process min
and is not a user knob, so `1/√mtot` is the correct form. That is not a finding.

| group | devices | X (3σ) | σ 1σ @10 µm | **implied A_VT (1σ)** | vs 30 mV·µm | verdict |
|---|---|---|---|---|---|---|
| **A** | 20 V, DNMOS20 | 0.0240 | 8.00 mV | **19.6 mV·µm** | 0.65× | **in band** |
| **A** | 60 V | 0.0270 | 9.00 mV | **22.1 mV·µm** | 0.73× | **in band** |
| **A** | 120 V | 0.0300 | 10.00 mV | **24.5 mV·µm** | 0.82× | **in band** |
| **B** | 40 V | 0.0085 | 2.83 mV | **6.94 mV·µm** | 0.23× | **3.2× optimistic** |
| **B** | 80 V | 0.0095 | 3.17 mV | **7.76 mV·µm** | 0.26× | **3.1× optimistic** |
| **B** | 200 V | 0.0110 | 3.67 mV | **8.98 mV·µm** | 0.30× | **2.9× optimistic** |

**Answer to checklist item 3: ladder A (20/60/120) is the physical one.** It lands at 0.65–0.82× of the
tox-based expectation — inside the ±50 % band, and correctly rising with voltage class (thicker oxide
→ larger A_VT). Ladder B is uniformly ~3× optimistic and is the defective one.

**Proposed single consistent ladder** — extend A's slope (A_VT rises ~1.25× from the 20 V to the
120 V class; continue linearly in class):

| class | 20 V | 40 V | 60 V | 80 V | 120 V | 200 V |
|---|---|---|---|---|---|---|
| X (3σ), proposed | 0.024 | **0.0255** | 0.027 | **0.0285** | 0.030 | **0.033** |
| implied A_VT (1σ) | 19.6 | 20.8 | 22.1 | 23.3 | 24.5 | 26.9 mV·µm |

This changes only the six ladder-B devices and leaves ladder A untouched. **Severity of the current
state: blocks-realism** for the 40/80/200 V classes — and note the 200 V pair is exactly where
`[inventory]` records the σ(trip) ≈ 340–440 mV downstream problem, so mismatch there is currently
*optimistic* by 3× while `kp` makes the circuit *pessimistic*. The two errors partially mask each
other, which is worth knowing before either is fixed alone.

### 2.7 `theta` — softer than the brief assumed

`[physics]` empirical `θ[1/V] ≈ (1…3)e-7 / tox[cm]`. At 30 nm → **0.033–0.100 /V**.

| device | `theta` [model] | expected @30 nm | ratio | **tox implied if θ is right** |
|---|---|---|---|---|
| NDMOS20 | 0.040 | 0.033–0.100 | 0.69× | 25–75 nm |
| NDMOS60 | 0.030 | 0.033–0.100 | 0.52× | 33–100 nm |
| NDMOS120 | 0.022 | 0.033–0.100 | 0.38× | 45–136 nm |
| **NDMOS200** | **0.018** | 0.033–0.100 | **0.31×** | **56–167 nm** |

**Correction to the brief's framing.** `[inventory]`/`BRIEF_pdk_realism.md` treats `theta = 0.018` on
the 200 V card as an established finding. On my arithmetic it is **low by ~3×** against a 30 nm oxide,
which is within the honest uncertainty of the empirical constant — **not** a clear defect. The whole
`theta` ladder is monotonic and correctly ordered.

What `theta` *is* good for is as an **independent probe of `tox`**, which the PDK never states. It
implies 25–75 nm at 20 V rising to 56–167 nm at 200 V. That is in tension with `vto = 1.00–1.31 V`
`[model]`, which for LDMOS body doping suggests a *thinner* oxide. **Recommendation: state `tox` per
VDMOS class explicitly; it is currently unknowable and three separate findings depend on it.**
**Verdict: suspect, ~3×, low confidence. Severity: cosmetic pending a stated `tox`.**

### 2.8 `ksubthres` — the ladder slope has the wrong sign

`[physics]` `n = ksubthres / (kT/q · ln10)`; `kT/q · ln10 = 0.05961 V/dec` at 300 K.
`[industry]` `n = 1.2–1.6`, `S = 72–96 mV/dec`.

| device | `ksubthres` | S (mV/dec) | **n** | verdict |
|---|---|---|---|---|
| NDMOS20 | 0.095 | 95.0 | 1.59 | OK (ceiling) |
| PDMOS20 | 0.110 | 110.0 | **1.85** | **out, 1.16×** |
| NDMOS40 | 0.088 | 88.0 | 1.48 | OK |
| PDMOS40 | 0.096 | 96.0 | **1.61** | out (edge) |
| NDMOS60 | 0.080 | 80.0 | 1.34 | OK |
| NDMOS80 | 0.075 | 75.0 | 1.26 | OK |
| NDMOS120 | 0.070 | 70.0 | **1.17** | **out** |
| **NDMOS200** | **0.060** | **60.0** | **1.01** | **out — essentially ideal** |
| PDMOS200 | 0.065 | 65.0 | **1.09** | **out** |

Two findings. First, **NDMOS200's `n = 1.01` is unphysical** — it says the depletion capacitance is
zero, i.e. a perfect gate. No bulk MOSFET achieves this; 60 mV/dec is the room-temperature Boltzmann
floor.

Second and more structural: **the ladder slopes the wrong way.** `[physics]` `n = 1 + C_dep/Cox`, and
Cox *falls* with the thicker oxide of the higher-voltage devices, so `n` must **rise** with voltage
class. `[model]` it falls monotonically, 1.59 → 1.01. This is the same defect the BSIM3 agent found on
the thick-oxide cards (§3.1), with the opposite sign — there `nfactor` was held constant and let `n`
inflate; here `ksubthres` was hand-laddered downward. Both come from treating the swing as a free
smooth parameter rather than deriving it from Cox.

**Verdict: wrong. Severity: distorts-results** — this directly sets the subthreshold gm/Id ceiling,
which is precisely the quantity the open `HANDOFF_dmos200_subthreshold_analog.md` backlog item turns on.

### 2.9 BV vs drift length

`[physics]` lateral sustaining field 15–25 V/µm → `L_drift = BV / E_sust`.

| device | BV [model] | L needed @25 V/µm | L needed @15 V/µm | L in model | verdict |
|---|---|---|---|---|---|
| NDMOS20…PDMOS120 (11 cards) | 22–135 | 0.9–5.4 µm | 1.5–9.0 µm | **no L knob at all** | BV asserted, not derived |
| **NDMOS200** | 225 | **9.0 µm** | **15.0 µm** | `L_REF = 8 µm`, `L_MIN = 5 µm` | **too short** |
| **PDMOS200** | 230 | **9.2 µm** | **15.3 µm** | same | **too short** |

At `L = L_REF = 8 µm` the implied sustaining field is `225/8 = 28 V/µm`, above the 15–25 band. At
`L_MIN = 5 µm` it is **45 V/µm** — a device that cannot physically hold 225 V, yet the model reports
full breakdown voltage there.

This quantifies the known constant-BV-vs-L defect `[inventory]`: **the `L` knob is penalty-only.**
Above `L_REF` it adds `RDRIFT` and nothing else; below `L_REF` it is dead (`Leff = max(L, L_MIN)`
clamps, and BV never moves). `README.md` states the limitation honestly — *"Breakdown is held at the
model card rating regardless of L"* — but a designer who shortens L to save area gets a free lunch in
simulation and a failed part in silicon. **Severity: blocks-realism** for any HV layout-area trade study.

Recommended anchor for phase 2 and beyond: make `bv` a function of `Leff`, e.g.
`bv = min(bv_rated, 20 V/µm × Leff)` `[industry]`, which at `L_REF = 8 µm` gives 160 V and forces
`L ≈ 11–15 µm` for a genuine 225 V rating.

### 2.10 Body diode — defensible; a second correction to the brief

`[physics]` `Js` for a lightly-doped silicon junction ~1e-15…1e-13 A/µm²; `A_cell = W_REF × pitch`.

| device | `is` [model] | A_cell | implied Js | verdict | `tt` [model] | `[industry]` expected |
|---|---|---|---|---|---|---|
| NDMOS20 | 5.0e-13 | 50 µm² | 1.0e-14 | **in band** | 18 ns | 10–100 ns ✓ |
| NDMOS60 | 1.2e-13 | 90 | 1.3e-15 | in band (edge) | 40 ns | 10–100 ns ✓ |
| NDMOS120 | 5.0e-14 | 150 | 3.3e-16 | 3× below | 80 ns | 50–500 ns ✓ |
| NDMOS200 | 2.5e-14 | 220 | 1.1e-16 | **9× below** | **130 ns** | **50–500 ns ✓** |
| PDMOS200 | 3.6e-14 | 220 | 1.6e-16 | 6× below | 155 ns | 50–500 ns ✓ |

**Correction to the brief's framing.** The brief lists *"the 130 ns-class values are a known smell on
VDMOS body diodes"*. **I disagree.** For a 225 V device the drift region is long and lightly doped,
minority-carrier lifetime is correspondingly long, and 130–155 ns is exactly what a fast-recovery HV
body diode looks like `[industry]`. The `tt` ladder is monotonic, correctly ordered, and in band on
every card. **Verdict: OK, no action.** (The standalone `DIO_SCH` **is** a real finding — §4.)

`is` drifts up to ~9× below the Js band at the 200 V end — mild, direction-consistent with lighter
drift doping. **Verdict: marginal. Severity: cosmetic.**

### 2.11 Quasi-saturation `rq` / `vq`

`[model]` `vq/BV` is remarkably constant at **1.04×–1.21×** across all 13 cards, i.e. the
quasi-saturation onset voltage tracks breakdown. That is a defensible construction. `rq` scales with
`rd` (0.12 → 1.33 Ω), so it inherits the §2.2 scale error by construction: **once `rd` is rescaled,
`rq` must be rescaled by the same factor** or the quasi-saturation knee moves to the wrong current.
**Verdict: structurally OK, carries F1. Severity: follows F1.**

---

## 3. Tier 1 — BSIM3 MOS

Full workup in the per-device tables below; derivation and arithmetic are as computed.

### 3.1 NMOS18 / PMOS18 — the healthiest cards in the PDK

| parameter | [model] | expected + tag + basis | verdict | severity |
|---|---|---|---|---|
| `tox` | 4.25 nm | 4–4.5 nm `[industry]` 180 nm core | OK | — |
| Cox | 8.125 fF/µm² `[physics]` ε_ox/tox | — | OK | — |
| `u0` | 420 / 145 cm²/V·s | 300–600 / 80–150 `[industry]` | OK | — |
| Idsat/W @1.8 V | 0.79–1.65 / 0.35–0.54 mA/µm `[physics]` | 0.55–0.60 / 0.25–0.30 `[industry]` | 1.2–1.4× high, OK | — |
| `vth0` | 0.48 / −0.52 V | 0.4–0.5 `[industry]` | OK | — |
| S | 76.7 / 79.4 mV/dec `[physics]` n=1+nfactor·C_dep/Cox | 72–96 | OK | — |
| `cj` / `cjsw` / `cgso` | 1.00 fF/µm² / 0.28 fF/µm / 0.22 fF/µm | 0.8–1.2 / 0.2–0.5 / 0.2–0.4 `[industry]` | OK | — |
| **A_VT** (1σ) | **3.50 mV·µm** (X=0.0105, 3σ) | 4.25 ±50 % `[industry]` 1 mV·µm/nm tox | **0.82× — OK** | — |
| **`noia`** | **6.25e41** | BSIM3 default 1e20 | **F3, 6.25e21×** | **blocks-realism** |
| **`AD/AS/PD/PS`** | **unset** | must be set | **F6, 100 % of C_j missing** | distorts-results |

### 3.2 NMOS50 / PMOS50

As above, plus: **A_VT = 4.50 mV·µm (1σ) against 11.0 expected → 2.4× optimistic**, `blocks-realism`.
`S = 95.0 / 102.1 mV/dec` — PMOS50 out of band. `u0 = 190 / 80` OK for the oxide. Idsat in band.

### 3.3 NMOS12 / PMOS12 — the worst BSIM3 cards

| parameter | [model] | expected + tag + basis | verdict | severity |
|---|---|---|---|---|
| `vth0` | 1.35 / −1.55 V | 0.8–1.5 `[industry]` 12 V thick-ox; consistent with tox=20 nm, k1=0.75, nch=9e16 `[physics]` | **OK — defensible** | — |
| **`u0`** | **120** cm²/V·s | 200–300 `[industry]` degraded thick-ox n-channel | **LOW 1.7–2.5×** — below PMOS18's 145, i.e. an n-channel less mobile than a p-channel | distorts-results |
| **`rdsw`** | **30** Ω·µm | family is 120 (18 V) → 160 (33) → 280 (50); should rise with class `[physics]` | **LOW ~10×**, breaks a clean monotone trend | distorts-results |
| `vsat` | 75 000 m/s | 6–9e4 surface-channel `[industry]`; family 140k→110k→80k→75k monotone | **OK** | — |
| **S** | **115.9 / 130.3** mV/dec | 72–96 | **out 1.21–1.36×** — `nfactor` held ~constant while Cox falls 4.9× `[physics]` | distorts-results |
| **A_VT** (1σ) | **6.00 mV·µm** | 20.0 `[industry]` | **3.3× optimistic** | blocks-realism |
| **`u0` double draw** | `(1+P_DUO)·(1+P_DKP)`, 3σ 0.10 and 0.12 | one term | **σ inflated 1.56×** `[physics]` RSS √(0.0333²+0.04²)=0.0521 vs 0.0333 | distorts-results |
| **`tox`,`cj`,`cjsw`,`js`** | **hard constants**, no corner or stat term | corner-dependent like the other 6 | **12 V corner set is internally inconsistent**; dynamic corner spread is identically zero | blocks-realism (corners) |
| stale `P_DVTO_`/`P_DVMAX_`/`P_DRSH_` names | applied to `vth0`/`vsat`/`rdsw` | — | cosmetic, but defeats grep audits | cosmetic |
| missing `binunit=1` | — | — | cosmetic (no bins defined anyway) | cosmetic |

**Device-type ambiguity, unresolved by the card.** A true 12 V gate wants tox ≈ 24–30 nm
(`[industry]` ~2 nm/V for 10-year TDDB; at 20 nm, E_ox = 6.0 MV/cm `[physics]`, above the ~5 MV/cm
target). A drain-extended device would want ~11 nm. Evidence is contradictory: `xj = 500 nm` says
drain-extended; the wrapper is a plain `M0` with **no drift element** (unlike NDMOS20's explicit
`Rdrift`) which says true thick-oxide. **The wrapper is decisive → Reading 1 → `tox` should be
24–30 nm, not 20.** `rdsw = 30` fits neither reading.

**Separate finding, outside the card: `device_limits.csv` gives NMOS12/PMOS12 `Lmin = 0.15 µm` —
shorter than NMOS18's 0.18 µm, on a 20 nm oxide, with `xj = 500 nm` (junction depth 3.3× the channel
length).** Physically impossible; punchthrough control at 12 V needs L ≥ 0.8–1.5 µm `[industry]`. This
single CSV row is what makes the 12 V Idsat estimate blow out to 1.17–7.83 mA/µm; at a realistic
L = 2 µm the card lands at 0.41 mA/µm, in band. **Severity: blocks-realism.**

Note the partial cancellation that hid this: `u0` low by ~2× and `rdsw` low by ~10× push DC drive
current in opposite directions, which is plausibly why `tb_nmos12_idvg.sch`'s 2.7 mA at Vgs=12 V
`[inventory]` looked acceptable. They do not cancel in output resistance or any small-signal quantity.

### 3.4 F3 — the flicker parameters are BSIM4 defaults

| | PDK NMOS18 | BSIM4 default | ratio | BSIM3 default | ratio |
|---|---|---|---|---|---|
| `noia` | 6.25e41 | **6.25e41** | **1.000** | 1e20 | 6.25e21 |
| `noib` | 3.125e26 | **3.125e26** | **1.000** | 5e4 | 6.25e21 |
| `noic` | 8.75e9 | **8.75e9** | **1.000** | −1.4e-12 | −6.25e21 |

PMOS18 matches the BSIM4 p-channel defaults equally exactly, including the distinctive non-round
`6.188e40` and `1.4e8`. **These cards are `level=49 version=3.3.0` — BSIM3.** The two models use
different unit conventions for oxide-trap density (BSIM3 ~1e20 m⁻³eV⁻¹; BSIM4 a rescaled ~1e41 form),
so the values are **~6.25e21× too large in the convention the simulator will apply**, and BSIM3
additionally expects a *negative* `noic` for NMOS.

**Conflict to record, per the brief's instruction.** `docs/CHANGELOG.md` describes these as *"the
standard 180nm reference values commonly seen in published model cards"* and *"engineered values, not
silicon-fit"*. My reading is that they are verbatim BSIM4 defaults, not values engineered from a
180 nm library. Supporting the reading: `[inventory]` §5 records `noia` as *"assigned in `a4f2eaa`,
never measured"*, and `noise_check.cir` only checks that the parameters parse and the transient
converges — it asserts no magnitude, so nothing in CI could catch this.

**Secondary, smaller finding — the tox scaling arithmetic does not close either:**

| card | (4.25/tox)² `[physics]` | stated in the card comment | **actual value ratio** |
|---|---|---|---|
| NMOS33 | 0.3964 | 0.40 ✓ | **0.5008** |
| NMOS50 | 0.1493 | 0.15 ✓ | **0.2496** |
| NMOS12 | 0.0452 | 0.05 ✓ | **0.1501** |
| PMOS33 / PMOS50 | 0.3964 / 0.1493 | 0.50 / 0.25 ✗ | 0.4994 / 0.2505 |

The NMOS comments quote the intended physics; the PMOS comments quote the delivered value. Both
conventions collide at the 12 V card where both say ~0.05 and the delivered ratio is 0.15 — **3.3×
off**. Delivered ratios 0.50/0.25/0.15 fit no power law (implied exponents 1.50/1.46/1.22). They are
round numbers. This contradicts the CHANGELOG's *"scaled as 1/tox²"* claim.

### 3.5 F6 — missing `AD/AS/PD/PS`

Confirmed by direct read: all 8 instance lines are
`M0 d g s b <DEV>_INT W={WEFF} L={LEFF} M={M} delvto={DVTH_MM}` — no area or perimeter on any.
Hence the `b3v33check.log` warnings on three different PMOS cards (`pmos18/33/50_int`), i.e. a
family-wide omission.

`[physics]` for W = 10 µm, L = 1 µm, 0.5 µm diffusion extension: `AD = 5.00 µm²`, `PD = 21.0 µm`.

| device | `cj·AD` | `cjsw·PD` | **C_j total missing** | sidewall share | `cgdo·W` modelled | **drain node: true → modelled** |
|---|---|---|---|---|---|---|
| NMOS18 | 5.00 fF | 5.88 fF | **10.88 fF** | 54 % | 2.20 fF | 13.08 → 2.20 fF (**17 %**) |
| NMOS50 | 3.00 | 3.78 | **6.78** | 56 % | 1.80 | 8.58 → 1.80 (**21 %**) |
| NMOS12 | 1.75 | 2.52 | **4.27** | 59 % | 1.50 | 5.77 → 1.50 (**26 %**) |

**100 % of junction capacitance is missing, not a partial error** — the simulator sees only the gate
overlap, i.e. **17–26 % of the true drain node; 74–83 % absent.** The sidewall term is the larger half,
so `PD = 0` costs more than `AD = 0`. All transient/delay/slew results on these devices are
optimistically fast, worst on NMOS18 where the missing 10.9 fF is 5× the modelled 2.2 fF. Junction
leakage is also identically zero (`I_leak = js·AD + jsw·PD`).

**Conflict to record.** `circuits/current_mirror_char/MIRROR_CHAR.md` §8 flags this and concludes the
100 nA design point is *"real, not a modelling artefact; its dominant risk is mismatch, not leakage."*
That conclusion is **correct for leakage and correct for that study** — the arithmetic is sound and
honestly self-tagged `[projection]`. It does not address the **capacitive** consequence, which is 4–6×
larger than the capacitance actually modelled. §8 should not be read as clearing the omission generally.

### 3.6 `DWREL` / `DLREL` — dimensionally wrong form

3σ 0.0075 / 0.0045 → **1σ 0.0025 / 0.0015** relative, scaled `1/√(W·L)`.
`[physics]` `σ(ΔW) = 0.0025·√(W/L) µm`, `σ(ΔL) = 0.0015·√(L/W) µm`.

| W, L | σ(ΔW) | σ(ΔL) |
|---|---|---|
| 1, 1 µm | 2.50 nm | 1.50 nm |
| 10, 1 (wrapper default) | 7.91 nm | 0.47 nm |
| **100, 0.18** | **58.9 nm** | **0.06 nm** |

`[industry]` litho + line-edge-roughness σ is **1–5 nm and only weakly geometry-dependent** — LER is
set by resist/etch statistics, not by aspect ratio. **Plausible at square geometries, divergent as
√(W/L).** At W/L = 100/0.18 it predicts 12× too much width sigma and 20× too little length sigma —
which is exactly the geometry designers use for wide output devices.
**Verdict: cosmetic at default geometry, distorts-results for wide-short devices.**

---

## 4. Tier 1 — BJT and the deferred zener question

### 4.1 NPN_LV

| parameter | [model] | expected + tag + basis | verdict | severity |
|---|---|---|---|---|
| `bf` | 140 (FF 168 / SS 114.8) | 100–200 `[industry]` | OK, ±20/−18 % spread OK | — |
| `is` | 2e-16 A per AREA | 1e-18–1e-17 A/µm² `[industry]` | implies **20–200 µm²** emitter; Vbe@100 µA = 696 mV `[physics]` — textbook | see 4.3 |
| `vaf` | 80 V | 30–100 `[industry]`; β·VA = 11 200 V | OK (top of the 2000–10 000 FoM band) | cosmetic |
| **`tf`** | 45 ps → **fT 3.54 GHz** | 10–40 GHz `[industry]` 180 nm BiCMOS LV NPN | **3–11× slow** | distorts-results |
| **`cje` / `cjc`** | 1.6 pF / 550 fF | 1–5 / 0.5–1.5 fF/µm² `[industry]` | **implies 533 / 550 µm² vs 20 µm² from `is` → 27× disagreement** | **blocks-realism** |
| Johnson check | fT·BVCEO = **14.4 GHz·V** | ≤ ~200 GHz·V `[physics]` E_max·v_sat/2π | **OK, 7 % of limit** | — |
| implied BVCEO | **4.07 V** `[physics]` BVCBO/β^(1/4), n = `MAV_BJT` = 4 | ratio 0.291, in the 0.25–0.5 band | ratio OK; **the 4 V ceiling is undocumented** | blocks-realism |
| **`kf`/`af`** | 1e-12 / 1 | see 4.2 | **fc 3.12 MHz, 312–3121× high** | **blocks-realism** |
| `is` corner | +6.0 / −5.4 % | 10–30 % `[industry]` | **tight ~3–5×** → only 1.5 mV of Vbe spread `[physics]` vs 5–15 mV real | distorts-results |

**F-BJT1 — the `cje`/`cjc` vs `is` disagreement is the same structural class as F1.** Both `is` and
`C_j0` are linear in emitter area `[physics]`, so one transistor must give one answer. It does not:
27× for NPN_LV, 11.7× for PNP_LAT, **75–88× for NPN_HV**, 45× for PNP_HV — **and the factor is not
uniform**, so this is not one rescale.

Quantified consequence: real `fT = 1/(2π(tf + (cje+cjc)/gm))`, `gm = Ic/Vt`:

| Ic | (cje+cjc)/gm | **effective fT** |
|---|---|---|
| 100 µA | 556 ps | **265 MHz** |
| 1 mA | 55.6 ps | **1.58 GHz** |
| 10 mA | 5.6 ps | 3.15 GHz |

**NPN_LV does not reach its own 3.5 GHz `tf` ceiling until 10 mA.** A designer biasing at 100 µA sees
a 265 MHz device. Every small-signal bandwidth, Miller estimate and phase margin in the BJT half of
the PDK is wrong.

### 4.2 F4 — BJT flicker

`[physics]` `S_ib,flicker = kf·Ib^af/f`; shot `2q·Ib`; crossover
`fc = kf·Ib^(af−1)/(2q)`. **With `af = 1` the exponent is zero and Ib cancels identically:**

```
fc = 1e-12 / (2 × 1.602177e-19) = 3.12 MHz,  at every bias
```

`[industry]` real BJT flicker corners are **a few Hz to low kHz** — the low 1/f corner is precisely why
bipolar input stages are chosen for low-noise DC-coupled work. **312–3121× too high**, and `af = 1`
also has the wrong functional form: `[physics]` BJT flicker arises from EB surface/interface trapping
and scales roughly as Ib² (af ≈ 1.5–2), so fc should *rise with bias*. **The model asserts a 1 µA and a
100 µA device have the same corner.** `kf = 1e-12, af = 1` is identical on all four BJTs — a
placeholder signature. To land fc in the kHz range, `kf ≈ 1e-15`. **This inverts the fundamental
BJT-vs-CMOS noise trade-off.**

### 4.3 The undeclared BJT reference cell

`[model]` every wrapper takes `AREA=1` and `device_limits.csv` calls it *"relative area multiplier
(unitless)"*. **Nothing in the PDK states what physical area AREA=1 is** — there is no BJT analogue of
the MOS `W_REF = 10u` convention. Worse, back-solving from `is` gives a *different* cell per device:
**20 µm² (NPN_LV), 80 (PNP_LAT), 4 (NPN_HV), 10 (PNP_HV)** — so AREA is not even self-consistent
between devices, which defeats the one thing a relative multiplier is for.
**Severity: distorts-results** (a documentation defect with numerical consequences).

### 4.4 F5 — the deferred zener investigation, closed

`[inventory]` §6.2 left this open: zener `cjo` = 120 / 55 / 28 pF vs signal-diode 280 fF → 429× / 196× /
100×; the CHANGELOG noted it is *not* the 1000× VDMOS slip and recommended a dedicated investigation.

**How much is legitimately doping?** `[physics]` one-sided abrupt junction:
`C_j0/A = sqrt(q·ε_si·N_eff/(2·V_bi))`. A heavily-doped zener genuinely *does* have far higher
capacitance per area — thinner depletion — but the dependence is only **√N**.

| junction | N_eff `[industry]` | V_bi (card `vj`) | **C_j0/A** |
|---|---|---|---|
| DZ_5V6 | 1e18 cm⁻³ | 0.75 | **3.326 fF/µm²** |
| DZ_12 | 1e17 | 0.78 | 1.031 |
| DZ_24 | 1e17 | 0.80 | 1.019 |
| DIO_PN | 1e16 | 0.78 | 0.326 |

Doping legitimately explains **3.2×–10.2×**. It cannot explain more: reaching 429× from doping alone
needs `N_eff` = 429² = 184 000× that of DIO_PN ≈ 1.8e21 cm⁻³ — **above the solid-solubility limit of
any dopant in silicon**. That junction would be a tunnel diode, not a 5.6 V zener.

**Implied areas at each device's own correct density:**

| device | `cjo` [model] | its C/A | **implied area** | as a square |
|---|---|---|---|---|
| DZ_5V6 | 120 pF | 3.326 | **36 070 µm² = 0.036 mm²** | **190 × 190 µm** |
| DZ_12 | 55 pF | 1.031 | 53 320 µm² | 231 × 231 µm |
| DZ_24 | 28 pF | 1.019 | 27 490 µm² | 166 × 166 µm |
| DIO_PN | 280 fF | 1.031 | 272 µm² | 16.5 × 16.5 µm |

**Answer: no, 120 pF is not defensible at any sane on-chip area, and it is a distinct scale slip.**
At the default `AREA=1` a 5.6 V zener would be 190 µm on a side; `device_limits.csv` permits AREA up
to 1000, i.e. 36 mm² and 120 nF.

**Is the factor uniform?** Normalising each implied area to DIO_PN's (doping fully removed):
**DZ_24 101.3× · DZ_5V6 132.9× · DZ_12 196.4×** — a **1.94× spread, and non-monotonic in `bv`.**

**This settles the question the CHANGELOG left open.** A uniform factor would indicate a generator
slip, fixable by one divisor as the VDMOS caps were. A varying, non-monotonic factor indicates the
three values were **hand-picked onto a smooth-looking ladder (120/55/28 pF, each ≈ half the last)**
rather than derived. The physics ladder is *not* geometric — C/A goes 3.33/1.03/1.02, flattening above
1e17 because C ∝ √N. The two ladders have different shapes, which is why no single factor reconciles
them. **A uniform divisor cannot be the fix here.** At a declared 100 µm² unit cell the correct TT
values are **333 / 103 / 102 fF** — note the 12 V and 24 V parts land nearly equal, which is the
physically right answer and which no smooth ladder would produce.

### 4.5 Zener `bv` has no temperature coefficient

Grep of the three cards for `tbv1`/`tbv2`/`tcv`: **zero hits.** `eg`/`xti` govern saturation current,
not `bv`. `[physics]` the mechanism switches with voltage and **the tempco changes sign**: below ~5 V
tunneling dominates (heating narrows the gap → bv falls, **negative**); above ~6 V avalanche dominates
(heating shortens the mean free path → bv rises, **positive**).

| device | expected sign | `[industry]` magnitude |
|---|---|---|
| DZ_5V6 | ≈ 0 (transition zone) | 0 to +0.5 mV/°C — **this is why 5.6 V zeners are the classic near-zero-tempco reference** |
| DZ_12 | positive | +6 to +10 mV/°C |
| DZ_24 | positive | +15 to +25 mV/°C |

Over −40…+150 °C, DZ_24 should move **+2.9 to +4.8 V**; the model holds it at 24.0 V, and wrong in the
unsafe direction (a real clamp passes more voltage hot than simulated). And the model gives **no way to
distinguish the good reference part from the bad ones**, since all three are equally flat.
**Severity: distorts-results, rising to blocks-realism for OVP/clamp/reference sign-off across temperature.**

### 4.6 `DIO_SCH` has non-zero `tt`

`[model]` `tt = 3e-10` (300 ps). `[physics]` `tt` models **minority-carrier stored charge**; a Schottky
is a majority-carrier device with no injection, no stored charge, and no reverse recovery — that is the
entire reason it is used as a rectifier or clamp. Correct value is **0**. At 10 mA forward the model
adds `C_d = tt·I/(n·Vt) = 107 pF` of spurious diffusion capacitance, growing linearly with current,
worst exactly where a Schottky would be chosen. Everything else about DIO_SCH is excellent
(`is` 6.18 decades over PN, `vj = 0.45`, `m = 0.22`, `eg = 0.69`, `xti = 2` — thermionic emission done
correctly). **Severity: distorts-results.**

---

## 5. Tier 1 — passives

### 5.1 RPOLY_HI

| parameter | [model] | expected + tag + basis | verdict | severity |
|---|---|---|---|---|
| `rsh` | 1200 Ω/□ | 1–2 kΩ/□ `[industry]` high-res poly module | **OK, mid-band** | — |
| **`tc1`** | **+600 ppm/°C** | **−500 to −1500** `[industry]`/`[physics]` — lightly-doped poly conducts by thermionic emission over grain-boundary barriers, ρ ∝ exp(qΦ_B/kT), so dρ/dT < 0 | **F7 — WRONG SIGN** | distorts-results |
| `tc2` | +1 ppm/°C² | 20 % of the tc1 term at ΔT=123 `[physics]` | OK | — |
| `VCR1` / `VCR2` | 200e-6 / 10e-6 | tens–low hundreds ppm/V `[industry]`; comment says ~200 ✓ | **OK, comment matches** | — |
| **matching** | X = 0.0075 (3σ) → **A_R = 0.354 %·µm (pair, 1σ)** `[physics]` √2·100·X/3 | 1–2 %·µm `[industry]` | **2.8–5.7× optimistic** | distorts-results |
| contact resistance | **absent** | 20–80 Ω per contact head `[industry]` | missing; <1 % here, 10–30 % on RPOLY_LO | cosmetic here |

**F7 quantified** `[physics]` `R(T)/R(27) = 1 + tc1·ΔT + tc2·ΔT²`: at 150 °C the model gives **+8.9 %**
where real high-res poly gives roughly **−6 % to −18 %**. Wrong sign on a 15–27 % swing across the
automotive range. Any bias network, RC time constant or bandgap trim leaning on RPOLY_HI temperature
behaviour is qualitatively wrong, not merely miscalibrated.

Note the `.lib` is half-aware: the RPOLY_LO comment correctly says *"high tc1 (heavily-doped poly
trends metallic/positive)"* but the contrapositive is never applied to RPOLY_HI, which gets a *smaller
positive* TC instead of the opposite sign. And the very patent the `.inc` cites (US 6,313,516,
verified §6) exists to engineer *around* the negative TCR of lightly-doped poly — **the citation's own
physics contradicts the model it is attached to.**

### 5.2 CMIM_STD

| parameter | [model] | expected + tag + basis | verdict | severity |
|---|---|---|---|---|
| `cj` | 1e-3 F/m² = **1.00 fF/µm²** `[physics]` 1 F/m² = 1e3 fF/µm² | 1–2 `[industry]` MIM | **OK** | — |
| implied dielectric t | **62.0 nm** `[physics]` t = ε_r·ε₀/C, ε_r = 7 | 30–60 nm nitride `[industry]` | **OK — conservative, buildable** | — |
| `VCC1`/`VCC2` | 30e-6 / 20e-6 → 650 ppm @5 V | <100 ppm/V linear `[industry]` | **OK, comment matches** | — |
| `tc1` (TCC) | +35 ppm/°C | \|TCC\| < 100 `[industry]` | **OK** — the brief's hypothesis that TCC is absent is **incorrect; it is modelled on all four caps** | — |
| **matching** | X = 0.0015 (3σ) → **A_C = 0.071 %·µm (pair, 1σ)** | 0.5–1 `[industry]` | **7.1–14.1× optimistic** | distorts-results |

**Consequence** `[physics]`: a 10 × 10 µm pair gets σ(ΔC/C) = 0.071/√100 = **71 ppm**, implying a
**13.5-bit** untrimmed capacitor DAC from 100 µm² unit caps. Real silicon delivers 9–10 bit. A
converter signed off on this model misses INL/DNL by 3–4 bits.

**Systematic passive finding:** *all nine* passives are optimistically matched by **3–14× (pair
convention)**. Even reading X as a 1σ rather than 3σ — a 3× more pessimistic reading — RPOLY_HI only
reaches the *bottom* of the band. **The sigma convention alone does not explain the gap.** The relative
*ordering* the `.lib` claims does hold (RPOLY_LO < N+ < P+ < RPOLY_HI < RNWELL; MIM ≪ MOM); only the
absolute scale is wrong.

---

## 6. Citation verification

| citation | verdict |
|---|---|
| **US Pat 6,313,516** (`.inc` ~L205) | **VERIFIED.** Real — TSMC, *"Method for making high-sheet-resistance polysilicon resistors for integrated circuits"*. Exactly on-topic. **But its premise contradicts F7:** the patent exists to minimise the temperature and voltage coefficients of lightly-doped high-sheet poly, whose TCR the art treats as negative. |
| **US Pat 12,464,737** (`.lib` L473) | **VERIFIED — `[inventory]` §6.5 #19 should be WITHDRAWN.** Real: Texas Instruments, *"Polysilicon resistors with high sheet resistance"*, granted 2025-11-04; pre-grant publication US20220399434A1. The quoted claim (*"resistance and matching coeff are inversely related"*) is a near-verbatim paraphrase of the patent's own background. The inventory's reasoning was arithmetically stale — US 12,000,000 issued 2024-06-04, and at ~6000–6500 grants/week number 12,464,737 falls ≈Q4 2025. |
| **Allen, *CMOS Analog Circuit Design*** | **3 of 4 VERIFIED** (poly ±30 % absolute, n-well ±40 %, poly VCR ~100 ppm/V). The n-well *"~8000 ppm/V"* is **likely Allen's 8000 ppm/°C temperature coefficient mislabelled as a voltage coefficient** — the model's own `RNWELL` tc1 is 4000 ppm/°C, not 8000. The value passes on its own merits; the attribution is probably wrong. No edition/page asserted. |
| **"Subramanian et al."** (`.lib` CMIM_STD) | **UNVERIFIABLE.** Not identifiable from a bare surname with no year, venue or title. Inconclusive, not disproven. Separately, the quoted 6.5× MIM/MOM sigma ratio contradicts the 4.0× the code implements, and no realistic MIM area reproduces the quoted 0.1 %. |

**Nothing was found to be fabricated.** Citation hygiene is better than the inventory suggested; the
weaknesses are in the physics values, not the sourcing.

---

## 7. Tier 2 — checklist

| device | check | verdict | severity |
|---|---|---|---|
| NMOS33/PMOS33 | Cox 5.116 fF/µm²; u0 300/115; Idsat 0.75–1.53 / 0.37–0.55 mA/µm; vth0 0.66/−0.74; S 84.4/88.1; A_VT 4.00 vs 6.75 expected (**0.59×**) | mostly OK; A_VT marginal; PMOS33 vth0 slightly high | cosmetic |
| DNMOS20 | vto −0.90 (depletion ✓); shares ladder-A mismatch (OK); `kp` implies 1303×; caps 19.5× | carries F1, F2 | blocks-realism |
| NPN_HV | bf 80, vaf 120 V, fT 1.77 GHz (just under band), Johnson 26.6 GHz·V ✓, BVCEO 15.05 V ✓; **cje/cjc 75–88× vs `is`** — worst in family | carries F-BJT1, F4 | blocks-realism |
| PNP_HV | bf 18, vaf 50 V, fT 0.64 GHz ✓, BVCEO 15.54 V ✓; cje/cjc 45× | carries F-BJT1, F4 | blocks-realism |
| DIO_PN | is 2e-14, n 1.05, Vf@1 mA = 669 mV `[physics]` ✓, bv 100 V, tt 6 ns (2–17× fast vs 10–100 band) | OK; tt marginal | cosmetic |
| DIO_FAST | n 1.03, Vf 558 mV, tt 2 ns ✓ | OK (n slightly low vs DIO_PN is odd) | cosmetic |
| DIO_SCH | is 6.18 decades over PN ✓, vj 0.45 ✓, m 0.22 ✓, eg 0.69/xti 2 ✓ — **but tt = 300 ps ≠ 0** | §4.6 | distorts-results |
| DZ_5V6/12/24 | `bv` ladder, `nbv` softening at low bv ✓, `ibv`↓ `rs`↑ ✓, tt 40–75 ns ✓ | breakdown physics good; **`cjo` §4.4, no tempco §4.5** | blocks-realism |
| RPOLY_LO | **rsh = 25 Ω/□** vs 100–400 `[industry]` — silicide-strap territory, not a resistor layer; a 10 kΩ needs 400 squares | **4–16× low** | distorts-results |
| RNWELL | rsh 1800 Ω/□ (band 1–2 k ✓); **tc1 +4000 ppm/°C ✓ mid-band**; VCR 8000 ppm/V ✓ | **best-modelled resistor in the set** | — |
| RNPLUS | rsh 32 Ω/□ vs 50–150 | 1.6–4.7× low (P+/N+ ratio 1.81× is correct, so the pair looks scaled down together) | distorts-results |
| RPPLUS | rsh 58 Ω/□ | OK, bottom edge | — |
| CMIM_HI | 2.00 fF/µm², implied t = 31.0 nm ✓ buildable, VCC 1300 ppm @5 V, TCC +45 | OK; matching 5.3–10.6× optimistic | distorts-results |
| CMOM | 0.35 fF/µm² ✓; **card says `di=7.5` (nitride) while `.lib` comment says SiO₂** | 1.88× provenance contradiction; inert today (`cj` explicit) | cosmetic |
| CFRINGE | 0.18 fF/µm² ✓; same `di` contradiction | as CMOM | cosmetic |

---

## 8. Fix worklist, ordered by severity × effort

Proposals only — **nothing has been applied.**

| # | Fix | Finding | Effort | Notes |
|---|---|---|---|---|
| 1 | **Rescale VDMOS `rd`/`rs`/`rq` by a single ~10³ divisor** to land Rsp at 2–5× the silicon limit | §2.2 | **low** — 39 numbers, uniform | The ratio is flat across the family, so one divisor works. Same shape as the June-2 cap fix. |
| 2 | **Re-derive VDMOS `kp` per card** from `µ·Cox·(W/L_ch)` at the 10 µm cell | §2.1 | **medium** — 13 numbers, **not** uniform | A single divisor will *not* work; the ladder slope is wrong too. Targets in `anchor-values.md`. |
| 3 | **Re-derive VDMOS `cgs`/`cgdmax`/`cgdmin` from process densities** — carry out `HANDOFF_vdmos_caps.md` suggestion #1 at last | §2.4 | **medium** — 39 numbers, sloped residual | Also do suggestion #3 (corner-parametrize) while there. |
| 4 | **Replace `noia`/`noib`/`noic` on all 8 BSIM3 cards** with BSIM3-convention values | §3.4 | **low** — 24 numbers | Or migrate the cards to `level=54` (BSIM4), where the current values are correct. Decide which. |
| 5 | **Set `kf ≈ 1e-15`, `af ≈ 1.5–2` on all 4 BJTs** | §4.2 | **low** — 8 numbers | `af` matters as much as `kf`: it restores the bias dependence. |
| 6 | **Regenerate zener `cjo` from junction physics + a declared unit area** | §4.4 | **medium** — 3 numbers, but needs the area decision first | A uniform divisor is *not* available. At 100 µm²: 333/103/102 fF. |
| 7 | **Add `AD/AS/PD/PS` to all 8 BSIM3 wrappers** as geometry expressions | §3.5 | **low** — 8 instance lines | e.g. `AD={W*0.5u} PD={2*(W+0.5u)}`. Recovers 74–83 % of the drain node. |
| 8 | **Flip `RPOLY_HI` `tc1` to −500…−1500 ppm/°C** | §5.1 | **low** — 1 number | Also revisit whether `RPOLY_LO`'s +1000 is right for the same module. |
| 9 | **Unify the VDMOS mismatch ladder** onto the proposed A-slope | §2.6 | **low** — 6 numbers | Only ladder B changes. |
| 10 | **Fix `device_limits.csv` NMOS12/PMOS12 `Lmin` 0.15 → ~1.0 µm**; add PDMOS120/PDMOS200 rows | §3.3 | **low** — 3 rows | The single row causing the 12 V Idsat blow-out. |
| 11 | **Fix `ksubthres` ladder slope** — derive `n` from Cox per class rather than hand-laddering | §2.8 | medium — 13 numbers | NDMOS200's `n = 1.01` is below the Boltzmann floor. |
| 12 | **Declare the BJT/diode reference cell** (what AREA=1 means), and reconcile `is` vs `cje`/`cjc` | §4.1, §4.3 | **high** — needs a decision then 4 cards | The `cje`/`cjc` route says 300–900 µm²; `is` says 4–80. Pick one and re-derive the other. |
| 13 | **Add zener `bv` tempco** | §4.5 | **high** — ngspice level-1 D has no `tbv1`; needs level-3 or a behavioural series source | Likely why it was never done. |
| 14 | **Make VDMOS `bv` a function of `Leff`** | §2.9 | **high** — model restructure | e.g. `min(bv_rated, 20 V/µm · Leff)`. Removes the free-lunch short-L device. |
| 15 | Raise `RPOLY_LO` `rsh` 25 → 100–400 Ω/□; `RNPLUS` 32 → 50–150 | §7 | low — 2 numbers | Both currently read as silicide straps. |
| 16 | **Widen all passive matching coefficients ~3–14×**; widen BJT `is` corner spread ~3× | §5.2, §4.1 | medium — 9 + 4 numbers | Systematic optimism; affects every MC result. |
| 17 | Set `DIO_SCH` `tt = 0`; fix NMOS12 `u0` and `rdsw`; state `tox` per VDMOS class; add a qualification temperature range | §4.6, §3.3, §2.7, `[inventory]` §4.4 | low each | Housekeeping cluster. |
| 18 | Correct `BRIEF_pdk_realism.md`'s 2 mΩ·cm² assumption before filing; withdraw `[inventory]` §6.5 #19 | §2.3, §6 | trivial | Both are documentation-only. |

**Two cautions for whoever executes this list.** (i) Fixes 1, 2 and 9 interact: `kp` currently makes
the 200 V devices *pessimistic* (subthreshold at µA) while the ladder-B mismatch makes them
*optimistic* by 3×. Fixing either alone will move `σ(trip)` in a direction that looks wrong until the
other lands. (ii) Fix 3 changes switching behaviour on every VDMOS, so the Phase D transient wall-time
baselines `[inventory]` §4.7 will shift; re-baseline rather than treating the shift as a regression.

---

## 9. Confidence statement

**Held firmly** (arithmetic, insensitive to assumptions): F3 (BSIM4-default identification — exact
digit match); F6 (AD/PD absent — direct read); the `u0` double-draw 1.56× inflation; F4's 3.12 MHz and
its bias-independence; every A_VT conversion; the zener non-uniform residual; the Johnson-limit checks;
the citation verdicts.

**Held with stated bands** (assumption-dependent): F1's absolute factors depend on `µ`, `tox`, pitch
and the RESURF penalty — but the *conclusion* (10²–10³× and two routes disagreeing by up to 12×)
survives any plausible choice within the stated bands, and the **shape** of each ladder is
assumption-independent. F2 likewise: the absolute ratios move with the assumed oxide, but the
**48× → 3.3× slope** does not.

**Low confidence, flagged as such**: §2.7 `theta` (the empirical constant spans 3×, and the answer
depends on an unstated `tox`); the VDMOS cell-pitch ladder; the exact BJT emitter area.

**Where I disagree with an existing repo document**, both positions are on the record: the CHANGELOG's
1/tox² and "engineered from published libraries" claims (§3.4); `MIRROR_CHAR.md` §8's scope (§3.5);
`BRIEF_pdk_realism.md`'s 2 mΩ·cm² assumption (§2.3) and its `tt` and `theta` framing (§2.7, §2.10);
`[inventory]` §6.5 #19 on the patent number (§6).
