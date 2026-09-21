# The AutoHV statistical model

What varies in this PDK, by how much, why, and where the number came from. The machine-readable
form is `models/stat_model.json`; this document is the reading copy. Corner directions and the
`U0` calibration live in `models/stat_directions.json`, produced by
`tools/measure_stat_directions.py`.

Program: brief v3 (`docs/backlog/HANDOFF_v3_stats_brief.md`) as amended by the Phase 0 and
Phase 1 replies. **Status: Stop A draft — approved by nobody yet, and nothing is generated from
it.**

## 1. Shape of the model

Two layers, kept separate because they answer different questions:

- **Global variables** — what moves die-to-die and lot-to-lot. 131 of them across the 40 device
  groups. These build the corners and drive process Monte Carlo. Every model parameter that
  varies is one expression in a unit-normal `Z`: additive for voltages, multiplicative
  (lognormal) for positive-definite quantities like mobility, sheet resistance and capacitance
  density.
- **Local mismatch** — what differs between two devices drawn side by side. Pelgrom form, 1σ
  coefficients in foundry units, per device.

A corner is a *direction* in the global space, not a list of hand-picked multipliers. Each
group's fast direction is measured (§4), scaled to a Mahalanobis length of exactly 3, and
recorded. `SPD_<group>` names that direction; it is never sampled. Monte Carlo samples the
independent variables underneath it.

## 1.1 Which doping the model uses

Every depletion-charge derivation in this model uses each card's **`k1`**, never `nch`. The two
disagree by 1.1–3.2× on the LV/mid cards, which is physical: `k1` reflects the doping averaged
over the depletion region, `nch` the surface doping, and a retrograde or halo profile separates
them. `k1` is the parameter fitted to the device's measured body effect, so it is the one that
describes the depletion charge Pelgrom mismatch depends on. See
`docs/bsim3-defaults-audit.md` §6.1 for the per-card ratios.

**Scope of that rule: `k1` for channel depletion charge; `nch` for junction quantities.**
A source/drain-to-well junction is set by the doping on its lightly-doped side, so junction
capacitance scaling uses `nch`, not the halo-inflated `Na(k1)`. See §7.1 of the audit.

### 1.2 VDMOS body doping

The VDMOS cards carry no `tox` and no `k1`, so their body doping is derived from each card's own
**measured** subthreshold slope rather than from a card parameter:

`n = S/(kT/q·ln10)` → `C_dep = (n−1)·C_ox` → `W_dm = ε_si/C_dep` → `N_a` self-consistently from
`W_dm = √(4ε_si·φ_F/(q·N_a))`.

At the ruled 11 nm oxide this gives **N_a = 1.80e17 … 2.83e17 cm⁻³**, rising with voltage class.
The flat-band voltage falls out of each card's `VTO` and is **solved, not assumed**:
**V_FB = −0.710 … −0.745 V (n-channel), +0.696 … +0.724 V (p-channel)** — tight and near-symmetric
between polarities.

This matters because assuming `V_FB` instead (∓0.95 V) gives 3.6e17–5.7e17 cm⁻³, which contradicts
the doping the phase-3 subthreshold ladder implies (1.3e17–2.7e17) by about 2×. Solving `V_FB`
removes the contradiction: there was never a disagreement between the two derivations, only an
assumed parameter.

## 2. Global variables

### 2.1 Gate oxide — `TOX_18`, `TOX_33`, `TOX_50`, `TOX_12`

Four separate oxide growths, so four independent variables: 4.25, 6.75, 11 and 31 nm nominal.
Each at 4 % 3σ, lognormal, `literature:0.18um-BCD-class`, ±50 %.

ONC25 states no oxide-thickness tolerance anywhere (checked for ruling F4), so the number is
literature rather than grounded — hence the wide error bar. It is 4× what today's cards move
(±1 % across FF/SS), which is why every capacitance, gm and AC number moves when this lands.

**Which oxide each device uses is set by the gate rating, not the drain rating.** Every AutoHV
VDMOS is rated ±5.5 V DC on the gate, so all 13 sit on `TOX_50` — AutoHV's own **11 nm** 5 V
oxide (declaration D2, re-ruled 2026-09-18) — regardless of their 20–200 V drain ratings.
`TOX_12` serves NMOS12/PMOS12 only. VDMOS cards carry no `tox` parameter at all, so the oxide
reaches them through their `KP`/`VTO` loadings and through the couplings in §2.2a.

### 2.2 Threshold voltage — `VTH_<device>`

One per device, additive, in volts, and **derived from AutoHV's own physics** (ruling AB1). The
private draw is the quadrature sum of two terms; the oxide term is separate and lives in §2.2a.

- **Fixed oxide charge.** `σ(V_FB) = q·σ(Q_f)/C_ox`, with `Q_f` = 5e10 cm⁻² typical for a thermal
  oxide on (100) Si (`literature`) and its wafer-to-wafer variation declared.
- **Effective channel charge.** `σ = k1·√(2φ_F)·(σ_Qdep/2)`, since Vth's depletion-charge term
  goes as `√Q_dep`. `σ(Q_dep)/Q_dep` = 10 % 3σ — *effective* charge, not dose alone: implant
  energy, profile position and anneal thermal budget all move the charge that sets Vth, and a fab
  controls the result, not the dose.

| device | 1σ mV | 3σ mV |
|---|---|---|
| NMOS18 | 10.3 | 30.8 |
| PMOS18 | 11.3 | 33.9 |
| NMOS33 | 12.5 | 37.5 |
| PMOS33 | 13.6 | 40.7 |
| NMOS50 | 16.5 | 49.5 |
| PMOS50 | 17.6 | 52.7 |
| NMOS12 | 43.0 | 128.9 |
| PMOS12 | 44.5 | 133.4 |
| NDMOS20 | 20.0 | 60.1 |
| NDMOS200 | 21.6 | 64.9 |

VDMOS `k1` comes from each card's own measured subthreshold slope at 11 nm (§1.2), since those
cards carry no `k1`. All entries are `autohv-derived`, ±50 %.

**What this replaced.** The previous values (88 / 114 / 135 / 150 / 130 mV 3σ) were **spec
windows — LSL/USL limits, not model σ**, which is a category error: a spec limit is a screening
boundary, not a standard deviation. They were 2–3× too wide at 5 V. No automotive "tightening
factor" is applied anywhere; that idea was considered and rejected.

### 2.2a Where the oxide part of Vth lives

`VTH_<device>` is the **private** draw and holds two terms in quadrature: fixed oxide charge
(`σ(V_FB) = q·σ(Q_f)/C_ox`) and effective channel charge (`k1·√(2φ_F)·σ_Qdep/2`). The **oxide**
term is deliberately *not* in it — it enters through the shared `TOX_<class>` draw, so that
devices on the same oxide correlate in Monte Carlo:

| parameter | follows | expression |
|---|---|---|
| `vth0` | `TOX_<class>` | `Δvth0 = k1·√(2φ_F)·(Δt_ox/t_ox)` |
| `k1` | `TOX_<class>` | `Δk1/k1 = Δt_ox/t_ox` |
| `VTO_<vdmos>_STAT` | `TOX_50` | as `vth0`, with `k1_equiv` from §1.2 |

**This coupling must be applied by the generator; BSIM3 does not do it.** `showmod` confirms
`vth0` and `k1` are explicit card parameters and do not move when `tox` does — `k1` reads back
unchanged, so its residual is exactly 0 and it takes the full relative coupling.

`vth0` is different: BSIM3 *does* move the threshold when `tox` moves, through the short-channel
(`dvt0/1/2` via `lt`) and narrow-width (`k3`) terms. So the coefficient the generator applies is

> `applied = analytic − bsim3_residual`

measured per card at its own classic bench, from the model's own `@m.xm1.m0[vth]` with no
extraction criterion:

| card | analytic | BSIM3 residual | applied |
|---|---|---|---|
| NMOS18 / PMOS18 | 7.18 / 8.13 mV | **−1.60 / −1.59** | 8.78 / 9.72 |
| NMOS33 / PMOS33 | 7.78 / 8.85 | −0.98 / −0.96 | 8.77 / 9.81 |
| NMOS50 / PMOS50 | 8.34 / 9.65 | −1.17 / −1.12 | 9.51 / 10.77 |
| NMOS12 / PMOS12 | 18.79 / 20.89 | −1.90 / −1.92 | 20.69 / 22.81 |

**The residual is negative**, so `applied` is 9–22 % *larger* than the analytic value. An L-sweep
on NMOS50 shows why: as carded it runs −1.171 mV at L = 0.5 µm, −0.222 at 1 µm, then +0.035…+0.049
at L ≥ 2 µm; with `dvt0/dvt1/dvt2/k3` zeroed it collapses to ≈0 at every length. BSIM3's implicit
oxide-to-threshold coupling *is* those terms, and at bench lengths they dominate and reverse the
depletion-charge trend.

### 2.3 Mobility — `U0_<device>`, declared

Lognormal, one per device, **declared at 8 % 3σ** (`literature`: mobility spread for a
0.18–0.25 µm BCD flow), ±50 %, floored at 3 % 3σ.

**It used to be solved, and no longer is (ruling U2).** The previous procedure fitted each `U0` σ
so the group's 3σ Idsat swing hit a per-class Idsat band. Those bands were externally sourced, and
the LDMOS one was invented outright. Solving against them meant `U0` silently absorbed every error
elsewhere in the model — when §2.2 narrowed, the solve simply inflated `U0` to keep hitting the
same external number. Now every variable is declared or derived on its own evidence, and each
group's Idsat spread is **whatever its own inputs predict**, reported rather than targeted.

| group | `U0` 1σ | `U0` slope | dominant | predicted 3σ Idsat |
|---|---|---|---|---|
| NMOS18 | 2.67 | 0.650 | U0 | **9.24 %** |
| PMOS18 | 2.67 | 0.867 | U0 | **11.72 %** |
| NMOS33 | 2.67 | 0.703 | U0 | **7.03 %** |
| PMOS33 | 2.67 | 0.881 | U0 | **8.55 %** |
| NMOS50 | 2.67 | 0.719 | U0 | **6.68 %** |
| PMOS50 | 2.67 | 0.878 | U0 | **7.95 %** |
| NMOS12 | 2.67 | 0.726 | U0 | **6.75 %** |
| PMOS12 | 2.67 | 0.858 | U0 | **7.78 %** |
| NDMOS20 | 2.67 | 0.693 | U0 | **7.30 %** |
| PDMOS20 | 2.67 | 0.957 | U0 | **7.97 %** |
| NDMOS40 | 2.67 | 0.554 | U0 | **8.08 %** |
| PDMOS40 | 2.67 | 0.863 | U0 | **7.52 %** |
| NDMOS60 | 2.67 | 0.459 | U0 | **8.91 %** |
| PDMOS60 | 2.67 | 0.524 | U0 | **8.35 %** |
| NDMOS80 | 0.00 | 0.365 | RDSW | **9.32 %** |
| PDMOS80 | 2.67 | 0.412 | U0 | **9.32 %** |
| NDMOS120 | 0.00 | 0.265 | RDSW | **10.66 %** |
| PDMOS120 | 0.00 | 0.285 | RDSW | **10.42 %** |
| NDMOS200 | 0.00 | 0.212 | RDSW | **11.47 %** |
| PDMOS200 | 0.00 | 0.216 | RDSW | **11.46 %** |
| DNMOS20 | 2.67 | 0.837 | U0 | **9.35 %** |

**`U0` and `RD` are independent draws (separate implants).** The fast corner direction moves
both — higher mobility, lower drift resistance — because both raise current. That is a property of
the *direction*, not a correlation in the *process*. A shared signed draw is a legitimate
alternative structure used by some libraries; it is not adopted here for lack of a physical basis
in AutoHV's declared flow, where channel mobility is set by the body implant and drift resistance
by the drift implant.

**`σ(KP) = 0` where the drift region dominates.** Measured per device as `d ln(Id)/d ln(U0)` on its
own classic bench; below 0.4 the mobility lever is not meaningful and a non-zero `σ(KP)` would
describe the model rather than the device. Five devices qualify — NDMOS80 (0.365), NDMOS120
(0.265), PDMOS120 (0.285), NDMOS200 (0.212), PDMOS200 (0.216). The 80 V pair straddles the
boundary: NDMOS80 is drift-dominated and PDMOS80 (0.412) is not, so this is recorded per device
rather than per voltage class.

**Consequence, pre-registered.** LV/mid Idsat 3σ roughly halves against the retired bands — 5 V
13.8 → 6.8 %, 1.8 V 19.9 → 9.6 %. This is the intended correction, not a regression: the old
figure was tuned to an outside number, this one is what AutoHV's own σ produce.

### 2.4 Series resistance — `RDSW_<device>`

15 % 3σ, lognormal, declared, ±50 %. For VDMOS the same variable drives `RD` and `RS`, which come
from one drift module. Its measured lever on Idsat is small at these benches (|g| ≈ 7e-4), so it
barely tilts the corner direction.

### 2.5 Critical dimensions — `DL_POLY`, `DW_ACT_LV`, `DW_ACT_HV`

`DL_POLY` is the poly gate CD: 10 nm 3σ, normal, literature, ±50 %, shared by every poly-gated
MOS *and* by the poly resistors — where it acts on the drawn **width**, because the same poly
edge defines both. `DW_ACT_LV` (15 nm) and `DW_ACT_HV` (20 nm) are the active-area CDs, declared.

These are the variables the wrapper edge-bias terms consume, and they are why fingering and
segmentation behave differently from a single large shape.

### 2.6 Resistors — `RSH_<layer>`, `RHEAD_<layer>`

Sheet resistance per layer, lognormal, from ONC25's own tolerance table: high-res poly 20 % 3σ,
doped poly 15 %, n-well 27 %, n+ diffusion 11 %, p+ diffusion 15 %, each ±20 %. These are the
best-grounded numbers in the model.

Contact-head resistance `RHEAD_<layer>` is 7.5 Ω/contact nominal at 30 % 3σ, **declared**, ±100 %.
ONC25 carries a contact-head *temperature coefficient* but no resistance value (checked for
ruling F7), so this is literature for silicided contacts (5–10 Ω).

### 2.7 Gate poly sheet — `RSH_GATE`

8 Ω/□ nominal, 20 % 3σ, lognormal, literature, ±50 %. **A new layer.** This PDK has no gate-poly
sheet resistance: its only poly layers are the resistor ones at 1200 and 300 Ω/□, and using
either for gate resistance would overstate it by 20–100×. Introduced by ruling Q-B solely to
feed the wrapper `rgate` term.

### 2.8 Capacitors — `CDEN_<dielectric>`, `CPER_<type>`

MIM density 12 % 3σ and MOM 20 %, both ONC25-grounded, lognormal. `CPER_<type>` is the new
perimeter term, 25 % 3σ, declared, ±100 %. The `CDEN`/`CPER` split for each type is constrained
so total C is unchanged at that type's regression-golden geometry (ruling Q-C), so the goldens
stay valid and only the size-dependence changes. Three distinct geometries are in play and
must not be conflated: the capacitor goldens are **100×100 µm** (10 000 µm², giving CMIM_STD's
10 pF), the resistor goldens are **100×10 µm** (10 squares, giving RPOLY_HI's 12.3 kΩ), and the
local-mismatch reference in `passives_mc_s0.cir` is **10×10 µm**. The capacitor split is
constrained at the first, the resistor σ split at the last.

### 2.9 Bipolar and diodes — `VBE_<bjt>`, `BF_<bjt>`, `RPAR_<bjt>`, `VF_<dio>`, `RS_<dio>`, `CJ_<dio>`

The physical variable is the junction voltage, not the saturation current: `VBE` at 6 mV 3σ and
`VF` at 8 mV, with `IS` derived as `IS_TT·exp(−ΔV/(n·V_T))`.

**What the quoted σ means.** σ_VBE and σ_VF are *voltage quotes at 27 °C, inclusive of the card's
own emission coefficient*, of a variable that is physically the saturation current — the way a
datasheet quotes a junction spread. The realisation is therefore a fixed multiplier on `is`, with
`σ/(n·V_T)` folded at generation, so `V_T` never appears in a model card. Two consequences, both
intended:

- **Frozen at 27 °C is not a compromise.** A fixed `IS` multiplier is the same physics at every
  temperature; its *equivalent* voltage spread narrows with `V_T` as the die heats, which is
  correct behaviour rather than an artefact.
- **`n` is per card, read not typed.** The six diodes run `n` = 1.03 to 1.22 and two of the four
  BJTs carry `nf` = 1.02/1.03, so one shared coefficient would be wrong by up to 22 %, worst on
  the Zeners. `tools/gen_models.py` and `tools/measure_stat_directions.py` both read it from the
  card, and they must always change together: if the two disagree, the cards and the measured
  directions describe different distributions and nothing reports it.

Today's cards move `IS` ±6 %, which is a
±1.5 mV Vbe shift — far tighter than any real bipolar process. Current gain `BF` is 25 % 3σ from
ONC25's β band. `RPAR_<bjt>` covers `rb`/`rc`/`re` together at 20 % 3σ, since they come from one
module.

### 2.10 Breakdown and junctions — `BV_<vdmos>`, `JS_MOS`

`BV` at 5 % 3σ per VDMOS, anchored on ONC25's diode BV tolerances (±3 % and ±5 %). `JS_MOS` at
20 % 3σ covers source/drain junction leakage; it stays in the model but is **excluded from corner
directions**, because at the corner benches junction leakage is picoamps against a hundred
microamps and has no lever on Idsat.

### 2.11 Parameters that are not variables

`vsat`, `pclm`, `eta0` and `etab` are held at TT: no corner or spread data exists for them and
they are second-order at the corner metric. `cj` and `cjsw` follow the group's `VTH` at 0.3×
relative, since junction depth and implant dose move together. `tf`, `tr` and `tt` are held at
TT. `BVCBO` follows `BV` one-for-one — the same avalanche physics.

## 3. Local mismatch

1σ Pelgrom coefficients. MOS: `A_VT` per device, **derived** (below), `A_BETA` 1.5 %·µm (new),
`A_W` 0.25 %·µm and `A_L` 0.15 %·µm carried over. BJT `A_VBE` 1.0 mV·µm, which reproduces today's
0.15 mV pair σ. Areas follow the `AREA × 100 µm²` convention (ruling Q-E), so `AREA = 0.04` means
4 µm². VDMOS mismatch is **not** a Pelgrom coefficient — see §3.2.

### 3.1 `A_VT`, derived from RDF physics

`A_VT = c_RDF·√(t_ox[nm]·k1)`, with `c_RDF` = 2.1991 mV·µm/√nm **computed, never fitted**:

> `A_VT(RDF) = (q/C_ox)·√(N_a·W_dep/3)`, with `N_a = (k1·C_ox)²/(2qε_si)` from the card's own `k1`
> and `W_dep` self-consistent; the total is `A_VT(RDF)/√f_RDF`.

Substituting `N_a(k1)` collapses the whole expression to `c_RDF·√(t_ox·k1)`, so the constant falls
out of the physics rather than being chosen. `f_RDF` = 0.3: random dopant fluctuation carries
roughly half of σ(Vth) at this node, i.e. ~0.25–0.35 of the variance. The ~0.65 share often quoted
applies at ≤ 45 nm.

| device | `A_VT` mV·µm |
|---|---|
| NMOS18 | 3.44 |
| PMOS18 | 3.66 |
| NMOS33 | 4.51 |
| PMOS33 | 4.81 |
| NMOS50 | 5.96 |
| PMOS50 | 6.41 |
| NMOS12 | 15.02 |
| PMOS12 | 15.84 |

**The check that it is right:** `c_RDF` holds to 3.18 % across t_ox 4.25–31 nm and
N_a 9.0e16–7.9e17 cm⁻³. A wrong doping exponent would drift it systematically with oxide
thickness, and it does not.

**Retired with it:** the `A_VT ≈ 1 mV·µm per nm of oxide` heuristic, which is a thin-oxide rule of
thumb, and the externally anchored ladder that preceded it. Ruling F9 is closed.

### 3.2 Two mismatch normalisations — do not convert one into the other

The wrappers use **two different** local-mismatch forms, and they are not interchangeable:

| family | wrapper form | what the coefficient means |
|---|---|---|
| BSIM3 MOS | `AGAUSS(0, coef/√AUM2)`, `AUM2 = (W/1µ)·(L/1µ)` | `A_VT`, area-normalised, in V·µm |
| VDMOS | `AGAUSS(0, coef, 3)/√mtot`, `mtot = (W/W_REF)·M` | **σ(Vth) at the W_REF = 10 µm cell**, in V |

The conversion chain was validated in both directions before this was written down. BSIM3
`coef`/3 reproduces the pre-Z1 `A_VT` values exactly — 0.0105 → 3.50, 0.0120 → 4.00,
0.0330 → 11.00, 0.0930 → 31.00 mV·µm. On the VDMOS side, converting at the 6 µm² reference cell
(W_REF 10 µm × `L_ch` 0.6 µm) turns a 20 mV·µm figure into a 0.0245 V cell coefficient, against a
carded 0.0255 — agreement that confirms the reading.

**The trap:** a VDMOS coefficient looks like a Pelgrom coefficient and is not one. It carries no
length dependence, because W is the only size knob on these cells — channel and drift length are
fixed at the process minimum. Applying the `A_VT = c_RDF·√(t_ox·k1)` ladder of §3 to them would
both use the wrong normalisation and flatten a deliberate per-class ladder.

### 3.3 Resistor matching: a discrepancy left on the record

ONC25 gives resistor matching two ways that disagree by a factor of ~23: a spec-table column
(high-res poly 0.045 %·µm) and its own model-form Pelgrom coefficient (1.1–1.55 %·µm). AutoHV's
current lumped value is 1.06 %·µm, consistent with the model form. Per ruling F1 the model form
is used and the spec column is not.

The hypothesis check F1 asked for **fails**: if the spec column were the same quantity under a
different area normalization, the ratio would be constant across layers. It is not — 23.6×
(high-res poly), 25.3× (doped poly), 7.8× (n-well), 188× (n+ diffusion), 44× (p+ diffusion), a
24× spread. The relative ordering disagrees too: ONC25 has n+ diffusion matching best and n-well
worst; AutoHV has high-res poly best and n+ diffusion mid-pack. Recorded as unexplained. It is
also a flag on AutoHV's own per-layer matching values, which do not reproduce ONC25's ordering.

## 4. How corner directions are measured

Each group has a reference bench taken from `docs/sizing-guide.json` rather than invented: the
10 µA mirror point for MOS (W, Vgs, gm/Id ≈ 6), RPOLY_HI at 2 µm width, CMIM_HI, and the BJT
10 µA point. Two biases are measured for every group:

- **classic** — Vgs = Vds = class supply. This defines the corner direction (ruling F8), because
  that is what FF/SS means to a fab and to anyone using `case`.
- **analog** — the gm/Id ≈ 6 mirror point, reported alongside.

They differ, and materially. On NMOS50 the threshold sensitivity is −0.025 on the classic bench
but −0.269 on the analog bench — a factor of ten. A corner picked for digital drive strength is
not the worst point for a gm/Id-biased analog circuit, which is exactly why the exhaustive sweep
and Monte Carlo exist alongside the presets.

Direction: `g_i = d ln(metric)/d z_i` for every variable the group depends on, then
`z_fast = 3·g/|g|`, `z_slow = −z_fast`. Length is 3 by construction.

## 5. What is not done yet

- **`k3`** is proposed for grounding at 2.0 in `docs/bsim3-defaults-audit.md`; the model assumes
  that lands.
- **The couplings in §2.2a are a generator contract, not yet generated.** They are recorded in
  `dependent_parameters` and honoured in Phase 2; nothing writes perturbed cards from them today.
- **The 3.3 V class reports a plausibility miss** (≈0.3× its comparable magnitude). Reported, not
  chased.
- **The 1.8 V and 12 V classes have no comparable magnitude at all**, so their plausibility
  entries carry `band: null`. Their justification is the derivation itself, plus the fact that the
  same three-term formula lands in band for every class that *can* be checked.

Closed since the last revision: all 40 groups now have measured directions; the preset table and
its Mahalanobis distances exist (`models/corners.json`, 17 cases); `A_VT` is ruled and derived.
