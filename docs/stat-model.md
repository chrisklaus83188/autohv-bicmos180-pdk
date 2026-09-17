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

## 2. Global variables

### 2.1 Gate oxide — `TOX_18`, `TOX_33`, `TOX_50`, `TOX_12`

Four separate oxide growths, so four independent variables: 4.25, 6.75, 11 and 31 nm nominal.
Each at 4 % 3σ, lognormal, `literature:0.18um-BCD-class`, ±50 %.

ONC25 states no oxide-thickness tolerance anywhere (checked for ruling F4), so the number is
literature rather than grounded — hence the wide error bar. It is 4× what today's cards move
(±1 % across FF/SS), which is why every capacitance, gm and AC number moves when this lands.

**Which oxide each device uses is set by the gate rating, not the drain rating.** ONC25 is
explicit: its 200 V LDMOS with a 5 V gate uses the 13 nm 5 V oxide. Every AutoHV VDMOS is rated
±5.5 V DC on the gate, so all 13 sit on `TOX_50` regardless of their 20–200 V drain ratings.
`TOX_12` serves NMOS12/PMOS12 only. VDMOS cards carry no `tox` parameter at all, so the oxide
reaches them through their `KP`/`VTO` loadings.

### 2.2 Threshold voltage — `VTH_<device>`

One per device, additive, in volts. 1.8 V: 88 mV 3σ. 3.3 V: 114 mV. 5 V: 135 mV. 12 V: 150 mV.
VDMOS: 130 mV.

The 1.8 V and 3.3 V numbers are ONC25's per-class LSL/USL bands. The 5 V number is ONC25's
measured bundle (Vth 0.657 / 0.792 / 0.927), used in place of the ±128 mV synthesis that ruling
F2 quoted — same source, tighter provenance. The 12 V band is an extrapolation and the VDMOS
band borrows the LV anchor, because ONC25's only LDMOS threshold figures are for its *depletion*
family (−1.65 V, −2.2/−1.1), which is the wrong device to anchor on. Both carry ±50 %.

### 2.3 Mobility — `U0_<device>`, solved not declared

Lognormal, one per device, and the only variable whose σ is **derived**. Fab statistical models
are fitted so that the corner reproduces the measured Idsat band, and that is what this does:
with `VTH`, `TOX`, `DL_POLY`, `DW_ACT` and `RDSW` held at their grounded σ, `U0` σ is solved so
the group's 3σ Idsat swing along its own fast direction equals the ONC25 class band
(±20 % at 1.8 V and 3.3 V, ±14 % at 5 V and 12 V). Floored at 3 % 3σ.

Measured result, 8 BSIM3 groups (`models/stat_directions.json`):

| group | class band | fixed set alone | solved `U0` 1σ | achieved swing | error |
|---|---|---|---|---|---|
| NMOS18 | 20 % | 16.0 % | 4.29 % | 19.9 % | −0.6 % |
| PMOS18 | 20 % | 17.0 % | 3.57 % | 19.9 % | −0.3 % |
| NMOS33 | 20 % | 10.4 % | 6.42 % | 19.6 % | −1.9 % |
| PMOS33 | 20 % | 11.2 % | 5.76 % | 19.7 % | −1.6 % |
| NMOS50 | 14 % | 7.7 % | 4.57 % | 13.8 % | −1.2 % |
| PMOS50 | 14 % | 8.4 % | 3.98 % | 13.9 % | −0.9 % |
| NMOS12 | 14 % | 3.6 % | 5.45 % | 13.7 % | −2.0 % |
| PMOS12 | 14 % | 3.8 % | 4.98 % | 13.8 % | −1.8 % |

No group hit the floor. The residual ≤ 2 % is left alone deliberately: the band it matches
carries a ±25 % error bar, so driving it to zero would be false precision.

**Caveat on the 12 V class.** The fixed set covers 16–17 % of the 20 % band at 1.8 V but only
3.6–3.8 % of the 14 % band at 12 V, so `U0` carries almost the entire 12 V corner. That follows
from the 12 V `VTH` σ being declared rather than measured. The 12 V corner is therefore the
weakest-grounded of the four classes and should be read that way.

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
`VF` at 8 mV, with `IS` derived as `IS_TT·exp(−ΔV/V_T)`. Today's cards move `IS` ±6 %, which is a
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

1σ Pelgrom coefficients. MOS: `A_VT` per class, `A_BETA` 1.5 %·µm (new), `A_W` 0.25 %·µm and
`A_L` 0.15 %·µm carried over. VDMOS `A_VT` 20 mV·µm, from ONC25's measured LDMOS
σ(ΔVth) = 8.2 mV at 12 µm² — about 3× the CMOS coefficient. BJT `A_VBE` 1.0 mV·µm, which
reproduces today's 0.15 mV pair σ. Areas follow the `AREA × 100 µm²` convention (ruling Q-E), so
`AREA = 0.04` means 4 µm².

**`A_VT` is the one open item (F9).** The file is authored as ruling F5 directs — 1 mV·µm per nm
of oxide, giving 4.25 / 6.75 / 11.0 / 31.0 mV·µm. But ONC25 *measures* 5 V CMOS at 6.35 mV·µm
(NMOS) and 5.1 (PMOS) on a 13.1 nm oxide, i.e. 0.48 mV·µm per nm. The rule only holds for their
2.5 V devices (0.78–0.94). On that evidence AutoHV's 5 V value is 1.7–2.2× too wide and its
agreement with the oxide rule is coincidence. The alternative — anchoring on the measurement and
scaling by oxide — gives 3.4 / 5.5 / 5.3 / 15.0 mV·µm. This is one number per device to change.

### 3.1 Resistor matching: a discrepancy left on the record

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

- **32 of 40 groups have no measured direction.** The harness implements the MOS bench only. The
  13 VDMOS drive statistics through `*_STAT` top-level params rather than card parameters;
  resistors, capacitors, BJTs and diodes need `ln R`, `ln C`, `ln Ic` and `ln If` metrics. Until
  that second pass runs, presets 7–12 (passives, bipolar) cannot be built.
- **The preset table and its Mahalanobis distances** therefore do not exist yet.
- **`A_VT` (F9)** awaits a ruling.
- **`k3`** is proposed for grounding at 2.0 in `docs/bsim3-defaults-audit.md`; the model assumes
  that lands.
