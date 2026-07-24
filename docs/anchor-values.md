# Anchor Values — AutoHV BiCMOS180 PDK

**What this is.** The golden figures of merit that phase 2 (simulation characterization) measures and
asserts against. Every entry has a target, a tolerance band, a provenance tag, and a one-line basis.

**Machine-readable twin:** [`anchor-values.json`](anchor-values.json) — same data, keyed
`{device: {fom: {target, lo, hi, units, sigma_convention, basis, tag}}}`. **40 devices, 447 entries.**
Phase 2 loads the JSON directly. The two files are generated together and must stay in sync.

**Derivations and findings:** [`model-realism-audit.md`](model-realism-audit.md). Section references
below (`audit §x.y`) point there.

## How to read a band

The band is **what a realistic 180 nm automotive BCD process would produce**, not what this PDK
currently produces. Where the PDK is already inside the band the entry says so — those are the
regression anchors. Where it is outside, the audit records the factor.

`[model]` read from the PDK · `[physics]` derived, formula given · `[industry]` typical
published/experience value · `[inventory]` from `characterization-inventory.md`.

**Sigma convention — read this before using any mismatch number.** Every mismatch literal *in the PDK*
is a **3σ** bound (HSPICE AGAUSS, `[inventory]` §4.5). Every sigma anchor *in this document* is
**1σ**, and each entry carries `sigma_convention` explicitly. Passive matching coefficients are quoted
in the **pair** convention (σ of the difference of two devices, √2× the per-device σ), because that is
how published A-coefficients are quoted; the PDK implements a per-device σ.

**Temperature range.** The PDK model files state **no qualification range anywhere** (`[inventory]`
§4.4). This document proposes **−40 … +150 °C** `[industry]` as the automotive BCD default. Phase 2
should sweep that range; if the maintainer sets a different one, it is a one-line change here and in
the JSON.

---

## 1. BSIM3 MOS — NMOS/PMOS 12, 18, 33, 50

Per-device entries in the JSON. Common structure, 14 FoM each:

| FoM | Target / band | Units | Tag | Basis |
|---|---|---|---|---|
| `cox` | ε_ox/tox, ±5 % | fF/µm² | `[physics]` | 8.125 (4.25 nm) · 5.116 (6.75) · 3.139 (11) · 1.727 (20) |
| `vth_lin` | card `vth0` ± 60 mV | V | `[industry]` | process-corner expectation for the class |
| `idsat_density` | 0.55–0.60 (N18) · 0.25–0.30 (P18) · 0.45–0.55 (N33) · 0.40–0.50 (N50) · 0.20–0.40 (N12) | mA/µm | `[industry]` | at Vgs = Vrated, L = Lmin |
| `subthreshold_swing` | 80 (72–96) | mV/dec | `[industry]` | S = n·ln10·kT/q, n = 1.2–1.6 |
| **`avt_1sigma`** | **= tox in nm**, ±50 % | **mV·µm** | `[industry]` | A_VT ≈ 1 mV·µm per nm of oxide |
| `cj_area` | 1.00 / 1.05 / 0.82 / … , −30/+40 % | fF/µm² | `[industry]` | 180 nm-era junction doping |
| `cjsw_sidewall` | 0.28 / 0.30 / … , −40/+60 % | fF/µm | `[industry]` | sidewall junction |
| `cgso_overlap` | 0.22 / 0.24 / … , −40/+60 % | fF/µm | `[industry]` | gate overlap |
| `flicker_corner` | 200 k (20 k–1 M) | Hz | `[industry]` | W/L = 10/0.18 at Id = 10 µA, input-referred |
| `idsat_corner_spread` | 15 (10–20) | % | `[industry]` | FF/SS vs TT |
| `vth_corner_spread` | 50 (40–60) | mV | `[industry]` | FF/SS vs TT |
| `vth_tempco` | −1.5 (−2.0…−1.0) | mV/°C | `[industry]` | bulk MOS |
| `mobility_tempco_exponent` | −1.5 (−2.0…−1.2) | — | `[physics]` | µ ∝ T^x, phonon-limited |
| `junction_perimeter_set` | **must be 1** | boolean | `[model]` | AD/AS/PD/PS currently 0 on all 8 (audit §3.5) |

**The A_VT row is where the PDK diverges most.** Implied vs expected, 1σ:

| device | tox | PDK A_VT (1σ) | anchor | ratio | verdict |
|---|---|---|---|---|---|
| NMOS18 / PMOS18 | 4.25 nm | 3.50 mV·µm | 4.25 (2.13–6.38) | 0.82× | **in band** |
| NMOS33 / PMOS33 | 6.75 | 4.00 | 6.75 (3.38–10.13) | 0.59× | just inside |
| NMOS50 / PMOS50 | 11.0 | 4.50 | 11.0 (5.50–16.50) | **0.41×** | **out — 2.4× optimistic** |
| NMOS12 / PMOS12 | 20.0 / 21.0 | 6.00 | 20.0 (10.0–30.0) | **0.30×** | **out — 3.3× optimistic** |

**Phase-2 note on `flicker_corner`:** this anchor is currently unmeasurable as written, because
`noia`/`noib`/`noic` are BSIM4 defaults in BSIM3 cards (audit §3.4, ~6.25e21×). Expect a corner far
above f_T until fix #4 lands. Assert it anyway — it is the only check that would have caught F3.

---

## 2. VDMOS / LDMOS — 13 cards

Per-device entries in the JSON, 15 FoM each. Class-dependent values are computed per card; the table
below shows the structure and gives NDMOS20 / NDMOS200 as worked endpoints.

| FoM | NDMOS20 | NDMOS200 | Units | Tag | Basis |
|---|---|---|---|---|---|
| `rsp_specific_ron` | 0.058 (0.033–0.083) | 15.68 (8.96–22.40) | mΩ·cm² | `[physics]` | 5.9e-9·BV^2.5 × (2–5× RESURF), pitch 5 → 22 µm |
| **`ron_times_w`** | **1054 (666–1665)** | **64 400 (40 730–101 825)** | Ω·µm | `[physics]` | for the W_REF = 10 µm cell. **PDK is 0.7–44 Ω·µm** (audit §2.2) |
| `idsat_density` | 0.15 (0.05–0.30) | same | mA/µm | `[industry]` | HV LDMOS at rated Vgs |
| `bv` | 24 (22.1–26.4) | 225 (207–247.5) | V | `[model]` | worst corner must clear the class name |
| `l_drift_for_bv` | 1.20 (0.96–1.60) | **11.25 (9.00–15.00)** | µm | `[physics]` | 15–25 V/µm lateral sustaining field |
| `cgs_per_cell` | 10.4 (3.5–31.0) | same | fF | `[physics]` | Cox·W_REF·(L_ch + L_ov_s) |
| `cgdmax_per_cell` | 11.5 (3.8–34.5) | same | fF | `[physics]` | Cox·W_REF·L_gd |
| `cgdmin_per_cell` | 2.9 (1.0–8.6) | same | fF | `[physics]` | field-plate oxide ≈ 4× gate oxide |
| **`cjo_per_cell`** | **49.7 (19.9–124)** | **71.4 (28.6–179)** | fF | `[physics]` | **PDK already in band — no action** |
| `sigma_vth_1sigma_at_wref` | 8.00 (4.80–12.80) | 11.00 (6.60–17.60) | mV | `[physics]` | proposed unified ladder (below) |
| `subthreshold_swing` | 85 (72–100) | same | mV/dec | `[industry]` | must **rise** with class; PDK ladder falls to n = 1.01 |
| `theta` | 0.06 (0.02–0.15) | same | 1/V | `[physics]` | (1–3)e-7/tox[cm], band spans tox 20–50 nm |
| `gm_over_id_ceiling` | 28 (24–32) | same | 1/V | `[physics]` | 1/(n·kT/q), n = 1.2–1.5 |
| `body_diode_tt` | 30 n (10 n–500 n) | 130 n (10 n–500 n) | s | `[industry]` | **PDK 18–155 ns in band — no action** (audit §2.10) |
| `vto_tempco` / `rd_tempco` | −2.0 (−3.0…−1.0) mV/°C · 6500 (4000–9000) ppm/°C | | | `[industry]`/`[physics]` | the PDK `TC_*` set is self-flagged `CALIBRATE` |

### The proposed unified mismatch ladder

The PDK has two ladders (audit §2.6). Ladder A (20/60/120 V, plus DNMOS20) lands at 0.65–0.82× of the
tox-based expectation — **in band**. Ladder B (40/80/200 V) is uniformly ~3× optimistic. The anchor
extends A's slope across the whole family:

| class | 20 V | 40 V | 60 V | 80 V | 120 V | 200 V |
|---|---|---|---|---|---|---|
| **proposed X (3σ)** | 0.024 | **0.0255** | 0.027 | **0.0285** | 0.030 | **0.033** |
| **anchor σ_Vth (1σ) at 10 µm** | 8.00 | 8.50 | 9.00 | 9.50 | 10.00 | 11.00 mV |
| implied A_VT (1σ) | 19.6 | 20.8 | 22.1 | 23.3 | 24.5 | 26.9 mV·µm |
| PDK today (3σ) | 0.024 ✓ | **0.0085** ✗ | 0.027 ✓ | **0.0095** ✗ | 0.030 ✓ | **0.011** ✗ |

Bold = changes. The width-only area scaling (`1/√mtot`) is **legitimate** and unchanged — channel
length is fixed at process min and is not a user knob.

### `kp` — conditional on an open decision

`kp` has no unconditional target, because it depends on what `W_REF = 10u` means. JSON key
`_vdmos_kp_conditional`.

**Decision A — `W_REF` is a genuine 10 µm drawn cell (recommended).** This is the convention the
June-2 capacitance fix established, and it is what the `cjo` and body-diode groups independently
imply (audit §1).

| route | target | band | basis |
|---|---|---|---|
| µ·Cox, n-channel | 7.67e-4 | 4.6e-4 – 1.15e-3 A/V² | µ_n = 400 cm²/V·s, tox 20–50 nm, W/L = 10/0.6 `[physics]` |
| µ·Cox, p-channel | 2.49e-4 | 1.5e-4 – 3.7e-4 A/V² | µ_p = 130 cm²/V·s `[physics]` |
| **Idsat density (preferred)** | **2.5e-4** | **8e-5 – 5e-4 A/V²** | kp = 2·Id/Vov² at 0.05–0.3 mA/µm × 10 µm, Vov = 4 V `[industry]` |

The two routes differ by ~3×. **Prefer the Idsat-density band**: LDMOS saturation current is limited
by the drift region, not the channel, so the µ·Cox route overestimates.

**Decision B — `W_REF` labels a power die.** Then `kp`/`rd`/`rs` stay, but `cgs`/`cgdmax`/`cjo` and
every mismatch coefficient must scale **up** by the same factor, and both the wrapper comment and the
`device_limits.csv` W ranges become wrong. **Not recommended** — it contradicts two parameter groups
that already agree on the 10 µm cell.

---

## 3. BJT — NPN_LV, PNP_LAT, NPN_HV, PNP_HV

13 FoM each. Key entries:

| FoM | NPN_LV | PNP_LAT | Units | Tag | Basis |
|---|---|---|---|---|---|
| `beta` | 140 (84–224) | 35 (21–56) | — | `[industry]` | forward β |
| `beta_corner_spread` | 25 (20–30) | same | % | `[industry]` | FF/SS |
| `early_voltage` | 80 (40–160) | 35 (18–70) | V | `[industry]` | VAF |
| `ft_at_peak` | 3.54 (1.77–7.08) | 0.88 (0.44–1.77) | GHz | `[physics]` | 1/(2π·tf) upper bound |
| **`ft_times_bvceo_johnson`** | 14.4 | 6.5 | GHz·V | `[physics]` | **must be ≤ 200** (Johnson limit). All four pass |
| `bvcbo` | 14 (12.6–15.4) | 18 (16.2–19.8) | V | `[model]` | subckt `.param` |
| **`bvceo_implied`** | **4.07** (3.5–7.0) | 7.40 (4.5–9.0) | V | `[physics]` | BVCBO/β^(1/4), n = `MAV_BJT`. **Not modelled or documented anywhere** |
| `is_current_density` | 5e-18 (1e-18–1e-17) | same | A/µm² | `[industry]` | **needs a declared AREA=1 cell** |
| `cje_density` / `cjc_density` | 3.0 (1–5) / 1.0 (0.5–1.5) | same | fF/µm² | `[industry]` | must imply the **same** area as `is` |
| **`flicker_corner`** | **3 k (100–10 k)** | same | Hz | `[industry]` | PDK gives **3.12 MHz**, bias-independent (audit §4.2) |
| `is_corner_spread` | 20 (10–30) | same | % | `[industry]` | should give 5–15 mV of Vbe spread; PDK gives 1.5 mV |
| `vbe_at_100uA` | 0.70 (0.62–0.78) | same | V | `[physics]` | n·Vt·ln(I/is) |

**`bvceo_implied` is the most important row here.** NPN_LV's 4.07 V ceiling is undocumented,
unenforced, and below the PDK's own 5 V rail. The 0.997 clamp in `Bavl` means the model never actually
breaks down — it just gets lossy — so a designer sweeping Vce gets no warning. Phase 2 should measure
it and phase 3 should put it in `device_limits.csv`.

---

## 4. Diodes and zeners

| device | `vf_at_1mA` | `bv` | `tt` | `cjo_density` | notes |
|---|---|---|---|---|---|
| DIO_PN | 0.669 (0.569–0.769) V | 100 V | 6 n (1.8 n–18 n) | 1.0 (0.5–2.0) fF/µm² | in band |
| DIO_FAST | 0.558 (0.474–0.642) | 80 | 2 n (0.6 n–6 n) | same | in band |
| **DIO_SCH** | 0.291 (0.247–0.335) | 45 | **0 (0–1 p)** | same | **`tt` must be 0** — majority-carrier device. PDK has 300 ps → 107 pF spurious C_d at 10 mA (audit §4.6) |

| zener | `bv` | `cjo_density` `[physics]` | `cjo_at_100um2_cell` | **`bv_tempco`** `[industry]` |
|---|---|---|---|---|
| DZ_5V6 | 5.6 ±5 % | 3.326 (1.66–6.65) fF/µm² | 333 (166–665) fF | **0.25 (0.13–0.40) mV/°C** — the crossover part |
| DZ_12 | 12 ±5 % | 1.031 (0.52–2.06) | 103 (52–206) fF | **8.0 (4.0–12.8) mV/°C** |
| DZ_24 | 24 ±5 % | 1.019 (0.51–2.04) | 102 (51–204) fF | **20.0 (10.0–32.0) mV/°C** |

Two things phase 2 must know. **First**, `cjo_at_100um2_cell` is conditional on declaring what
`AREA=1` means — note that DZ_12 and DZ_24 land **nearly equal**, because C ∝ √N flattens above
1e17 cm⁻³. The PDK's smooth 120/55/28 pF ladder cannot be produced by any doping profile, which is how
the audit concluded it was hand-picked rather than derived (§4.4). **Second**, `bv_tempco` is currently
**not modelled at all** — no `tbv1`/`tbv2` anywhere — so all three zeners are temperature-invariant.
Over −40…+150 °C, DZ_24 should move +2.9 to +4.8 V. Phase 2 will measure zero; that is the finding,
not a harness bug.

---

## 5. Passives

| resistor | `rsh` | **`tc1`** | `vcr1` | `matching_A_R` (pair, 1σ) |
|---|---|---|---|---|
| RPOLY_HI | 1200 (1000–2000) Ω/□ | **−1000 (−1500…−500) ppm/°C** | 200 (100–400) ppm/V | 1.5 (0.9–2.7) %·µm |
| RPOLY_LO | 250 (100–400) | +1000 (500–3000) | 50 (25–100) | 1.5 (0.9–2.7) |
| RNWELL | 1800 (1000–2000) | +4000 (3000–6000) | 8000 (4000–16000) | 4.0 (2.4–7.2) |
| RNPLUS | 100 (50–150) | +1500 (1000–2000) | 1500 (750–3000) | 2.5 (1.5–4.5) |
| RPPLUS | 100 (50–150) | +1500 (1000–2500) | 1800 (900–3600) | 2.5 (1.5–4.5) |

**`tc1` on RPOLY_HI is a sign anchor, not just a magnitude anchor.** The PDK has **+600 ppm/°C**; the
physics says negative (audit §5.1). Phase 2 asserting `lo ≤ x ≤ hi` will catch it on the sign alone.

| capacitor | `density` | `implied_dielectric_thickness` | `vcc1` | `tcc_tc1` | `matching_A_C` (pair, 1σ) |
|---|---|---|---|---|---|
| CMIM_STD | 1.0 (1.0–2.0) fF/µm² | 62.0 (43.4–86.8) nm | 30 (12–60) ppm/V | 35 (14–88) ppm/°C | 0.75 (0.45–1.35) %·µm |
| CMIM_HI | 2.0 (2.0–4.0) | 31.0 (21.7–43.4) | 60 (24–120) | 45 (18–113) | 0.75 (0.45–1.35) |
| CMOM | 0.35 (0.3–1.0) | 101.2 (70.8–141.7) | 5 (2–10) | 20 (8–50) | 1.5 (0.9–2.7) |
| CFRINGE | 0.18 (0.1–0.5) | 196.8 (137.8–275.5) | 3 (1–6) | 15 (6–38) | 1.5 (0.9–2.7) |

**All four densities, all VCC values and all TCC values are already in band — these are regression
anchors, not fix targets.** The `matching_A` rows are the exception: every passive is **3–14×
optimistic** (audit §5.2), and the ordering the `.lib` claims does hold even though the absolute scale
does not.

---

## 6. Known-artifact register

**Phase 2 must not file any of these as bugs.** JSON key `_known_artifacts` — 8 entries, each with
`where`, `magnitude`, `physical_truth`, `corrupts`, `why_present`, `tag`.

| artifact | magnitude | corrupts | why it is there |
|---|---|---|---|
| **`Rcond g_int s 1e6`** (13 VDMOS) | **1.8 µA @1.8 V · 5.0 µA @5 V · 12.0 µA @12 V** — ~6 orders above a real gate | VDMOS gate-drive static current; any Iq or standby measurement on an HV gate node; high-Z gate DC levels | fixes the multi-instance floating-mirror singular matrix (`4b05308`, `454959e`) |
| `Rgmin g g_int 1e9` (13 VDMOS) | 1.8 nA @1.8 V, 5.0 nA @5 V | nothing measurable | fixes the cascoded-LDMOS singular matrix at MM_ON=0 (`0ceabc3`) |
| self-heating scope (SH_ON=1) | Vth feedback only | thermal runaway; Rdson vs T under self-heating; inter-device coupling (absent) | documented first-cut limitation |
| `B_pdiss` includes `Rdrift` (200 V pair) | power uses `V(d,s)`, which spans the external drift resistor | junction temperature on the 200 V parts, overestimated | artifact of the `Rdrift` wrapper construction |
| VDMOS caps not corner-parametrized | fixed across all 5 corners | **switching-time corner spread on every VDMOS is identically zero** | `HANDOFF_vdmos_caps.md` suggestion #3, never implemented |
| NMOS12/PMOS12 frozen `tox`/`cj`/`cjsw`/`js` | bare constants, no corner or stat term | all 12 V dynamic corner spread is identically zero; FF mobility sits on TT oxide | Level-3 → BSIM3 migration residue |
| AGAUSS consumed when `MM_SIGMA ≠ 0` | one RNG draw per instance | reproducibility of an MC sequence run alongside corner sims | ngspice `.param` has no comparison operators |
| `MM_ON` and `MM_SIGMA` **add** | the two terms sum | any run with both non-zero — explicitly "don't do this" | documented contract, `MISMATCH_CORNERS.md` |

---

## 7. Open maintainer decisions

Five anchors are conditional. JSON key `_open_maintainer_decisions`.

| decision | what it sets | audit recommendation |
|---|---|---|
| **VDMOS scale** — is `W_REF=10u` a real 10 µm cell or a power-die label? | `kp`, `rd`, `rs`, `rq` targets | **10 µm cell.** `cjo` and the body diode already agree with it |
| **BJT/diode reference cell** — what area is `AREA=1`? | `is`, `cje`, `cjc`, `cjo` targets for 4 BJTs + 6 diodes | must be declared; currently `is` implies 4–80 µm² and `cje`/`cjc` imply 300–900 µm² |
| **BSIM3 vs BSIM4** — fix `noia`/`noib`/`noic`, or migrate the cards to `level=54`? | flicker anchors on all 8 BSIM3 | either is defensible; the current values are exactly right for BSIM4 |
| **NMOS12 device type** — thick-oxide 12 V gate or drain-extended? | `tox`, `rdsw`, `Lmin` | the wrapper (plain `M0`, no drift element) says thick-oxide → `tox` 24–30 nm |
| **Qualification temperature range** | every tempco sweep in phase 2 | −40 … +150 °C |

Where a decision is unresolved, the JSON carries a `conditional_on` field on the affected entry.
Phase 2 should skip those assertions and report them as *blocked on decision*, not as failures.

---

## 8. Suggested phase-2 assertion policy

- **Hard-fail** on anything tagged `[physics]` or `[model]` outside its band — these are arithmetic or
  direct reads and there is no judgement in them.
- **Warn** on `[industry]` bands. They carry real uncertainty; a 1.2× miss is a conversation, not a bug.
- **Skip and report** anything with `conditional_on` set.
- **Never assert** on anything in `_known_artifacts` — measure and log it, so drift is visible, but do
  not gate on it.
- **Assert the `flicker_corner` and `junction_perimeter_set` rows even though they will fail today.**
  They are the two anchors that would have caught F3 and F6, and the whole point of phase 2 is that
  the next occurrence gets caught by a machine rather than a reading pass.
