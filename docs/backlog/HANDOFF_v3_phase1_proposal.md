# Handoff: v3 Phase 1 — proposed statistical model, for review before authoring

**Responds to:** the Q-A–Q-E rulings reply (Phase 1 unblocked)
**Brief:** `HANDOFF_v3_stats_brief.md` as amended by that reply
**Branch:** `mc-realism` @ `ebee2ad`; Phase 0 committed and pushed
**Date:** 2026-09-16
**Status:** grounding and bench data gathered; **nothing authored or generated yet.** This is the
proposed content of `stat_model.json` put up for feedback *before* I write it, so Stop A is a
review of a model you have already shaped rather than a surprise.

## 1. Rulings applied, no further questions on them

Q-A (latent direction from measured sensitivities), Q-B (`RSH_GATE` declared, `rgate` kept,
mover added), Q-C (split constrained at each type's golden geometry), Q-D (`--max-runs` +
`--prune N`), Q-E (`AREA` × 100 µm²) are all taken as written. The two §3.1 deviations are
accepted. The `k3` finding became the defaults-audit deliverable (§5).

**One ruling I derived and am applying** (flagged for confirmation as F6): ONC25 states the gate
oxide follows the **gate** rating, not the drain rating (its 200 V LDMOS with a 5 V gate uses the
13 nm oxide). Every one of the 13 AutoHV VDMOS/LDMOS devices is rated ±5.5 V DC / ±7 V absolute
on the gate. **So all 13 load onto `TOX_50`, and `TOX_12` is used only by NMOS12/PMOS12** —
regardless of their 20–200 V drain ratings.

## 2. What the grounding actually supports

From the local ONC25 extraction (values below are derived; the source file stays local):

| quantity | ONC25 says | grounds |
|---|---|---|
| gate-oxide ladder | 6.4 / 7.5 / 13.1 / 31.1 nm for 2.5 / 3.3 / 5 / 12 V | the TOX variable split, and the oxide-by-gate-rating rule |
| Pelgrom A_VT | **≈ 1 mV·µm per nm of oxide** (foundry's own footnote, "based upon 1 V·Tox") | A_VT for every MOS class |
| Vth spread (uncorrelated bands) | ±88 mV (2.5 V), ±114 (3.3 V), ±128 (5 V) | global `VTH_<dev>` σ |
| Idsat FF/SS | ±20 % / ±20 % / ±14 % by class | calibration target for `U0_<dev>` |
| resistor sheet tolerance | high-res poly ±20 %, p+/n+ poly ±12–15 %, n-well STI ±27 %, n+ diff ±11 %, p+ diff ±15 % | `RSH_<layer>` σ, per layer |
| MIM / MOM density | ±12 % / ±20–25 % | `CDEN_<diel>` σ |
| BJT β | 20–30 % class band | `BF_<bjt>` σ |
| diode BV | ±3 % (P+NW), ±5 % (N+PW) | `BV_<vdmos>`, diode BV |
| silence | resistor VCR, MIM matching, BJT Is/area, contact-head resistance | these stay `declared` with error bars |

## 3. Proposed global variables

Roughly 90 variables across 40 groups. σ is quoted as 3σ for readability; the JSON stores 1σ.

| variable | 3σ | distribution | source | error bar |
|---|---|---|---|---|
| `TOX_18` / `TOX_33` / `TOX_50` / `TOX_12` | 4 % | lognormal | literature (0.18 µm BCD) | ±50 % |
| `VTH_N18`,`VTH_P18` | 88 mV | normal | onc25 (2.5 V band) | ±25 % |
| `VTH_N33`,`VTH_P33` | 114 mV | normal | onc25 | ±25 % |
| `VTH_N50`,`VTH_P50` | 128 mV | normal | onc25 | ±25 % |
| `VTH_N12`,`VTH_P12` | 150 mV | normal | declared (12 V extrapolation) | ±50 % |
| `VTH_<vdmos>` × 13 | 5 % of VTO | normal | declared | ±50 % |
| `U0_<dev>` × 21 | **calibrated** (§4.2) | lognormal | onc25-derived | ±25 % |
| `RDSW_<dev>` (VDMOS: `RD`,`RS`) | 15 % | lognormal | declared | ±50 % |
| `DL_POLY` | 10 nm | normal | literature | ±50 % |
| `DW_ACT_LV` / `DW_ACT_HV` | 15 nm / 20 nm | normal | declared | ±50 % |
| `RSH_RPOLY_HI` | 20 % | lognormal | onc25 high-res poly | ±20 % |
| `RSH_RPOLY_LO` | 15 % | lognormal | onc25 p+/n+ poly | ±20 % |
| `RSH_RNWELL` | 27 % | lognormal | onc25 n-well STI | ±20 % |
| `RSH_RNPLUS` | 11 % | lognormal | onc25 n+ diff | ±20 % |
| `RSH_RPPLUS` | 15 % | lognormal | onc25 p+ diff | ±20 % |
| `RSH_GATE` (8 Ω/□ nominal) | 20 % | lognormal | literature (Q-B) | ±50 % |
| `RHEAD_<layer>` × 5 | 30 % | lognormal | declared | ±100 % |
| `CDEN_MIM` (STD, HI) | 12 % | lognormal | onc25 | ±20 % |
| `CDEN_MOM` (CMOM, CFRINGE) | 20 % | lognormal | onc25 | ±25 % |
| `CPER_<type>` × 4 | 25 % | lognormal | declared | ±100 % |
| `IS_<bjt>` × 4 | 6 % | lognormal | declared (carries today's corner) | ±50 % |
| `BF_<bjt>` × 4 | 25 % | lognormal | onc25 β band | ±20 % |
| `IS_<dio>` / `RS_<dio>` / `CJ_<dio>` × 6 | 6 % / 20 % / 3 % | lognormal | mixed | ±50 % |
| `BV_<vdmos>` × 13 | 5 % | normal | onc25 diode BV | ±50 % |

`pclm`, `vsat`, `js`, `cjsw`, `eta0` and similar are **not** given variables. They either follow
TOX/VTH with a declared sensitivity or stay at TT with a reason, per brief §3.1.

### 3.1 Local mismatch (1σ, foundry units)

| device family | today | proposed | note |
|---|---|---|---|
| A_VT, 1.8 V | 3.5 mV·µm | **4.25** | oxide rule (4.25 nm); value change |
| A_VT, 3.3 V | 4.0 mV·µm | **6.75** | oxide rule (6.75 nm); value change |
| A_VT, 5 V | 11.0 mV·µm | 11.0 | already exactly on the rule |
| A_VT, 12 V | 31.0 mV·µm | 31.0 | already exactly on the rule |
| A_BETA, all MOS | — | **1.5 %·µm** | new term, brief §3.3; value change |
| A_W / A_L | 0.25 / 0.15 %·µm | unchanged | |
| resistors | one lumped coefficient (RPOLY_HI 1.06 %·µm) | split into `A_RSH`/`A_W`/`A_LEND`/`SIG_HEAD`, constrained at 10×10 µm | see **F1** |
| capacitors | `A_C` 0.53 %·µm (MIM) | unchanged; `A_CPER` new | |
| BJT | area-only | `A_VBE` **1.0 mV·µm** | reproduces today's 0.15 mV pair σ, so not a value change |

That the 5 V and 12 V A_VT values already sit exactly on the foundry's oxide rule (11 ↔ 11 nm,
31 ↔ 31 nm) while 1.8 V and 3.3 V do not is the main reason I propose moving the latter two
rather than inventing a new rule.

## 4. How the corners get built (Q-A, as I intend to implement it)

### 4.1 Benches come from the repo, not from me

Each group's reference bench is its own `docs/sizing-guide.json` entry: the 10 µA `mirror_points`
row (W, Vgs, gm/Id ≈ 6) for BSIM3 devices, the listed VDMOS rows, RPOLY_HI at 2 µm width for
resistors, CMIM_HI for capacitors, and the BJT 10 µA point. Bench, bias and the measured `g`
vector all get written into `corners.json`.

### 4.2 Two measurement passes

1. **Calibration.** With VTH and TOX fixed at their grounded σ, choose each `U0_<dev>` σ so the
   group's own 3σ Idsat swing equals the ONC25 band for its class (±20 / ±20 / ±14 %). This makes
   the corner's Idsat grounded rather than asserted — and is the part of §3 I most want feedback
   on (**F3**), because it makes `U0` a derived σ rather than an independently grounded one.
2. **Direction.** Perturb every variable the group depends on by ±1σ on its bench, measure
   `g_i = d lnIdsat/dz_i` (`d lnR`, `d lnC`, `d lnIc` for passives and BJTs), then
   `z_fast = 3·g/|g|`, `z_slow = −z_fast`. Mahalanobis length is exactly 3 by construction.

Scale: about 90 variables × 2 runs on ~40 benches, so roughly 700 op points, a couple of minutes.

## 5. BSIM3 defaults audit (data in hand)

All 8 BSIM3 cards declare the same parameter set. **Eighteen audit-list parameters are undeclared
in all 8**, so BSIM3 defaults are live. Read out of this ngspice build directly rather than from
memory:

| undeclared, default active | value | significance |
|---|---|---|
| `k3` | **80** | narrow-width Vth. Fitted 0.18 µm values are single digits — **ground it** |
| `k3b` / `w0` | 0 / 2.5e-6 | partners of `k3`; ground with it |
| `nlx` | 1.74e-7 | lateral non-uniform doping |
| `dvt0w`/`dvt1w`/`dvt2w` | 0 / 5.3e6 / −0.032 | narrow-width Vth, small-W only |
| `keta` | −0.047 | bulk-charge body effect |
| `b0` / `b1` | 0 / 0 | W-dependence of bulk charge — inactive at 0 |
| `pdiblcb` / `dsub` | 0 / 0.35 | DIBL |
| `pscbe1` / `pscbe2` | 4.24e8 / 1e-5 | substrate-current body effect |
| `kt2` | 0.022 | Vth tempco, second order |
| `ua1`/`ub1`/`uc1` | 4.31e-9 / −7.61e-18 / −5.6e-11 | mobility tempco |

Declared in all 8 (no audit action): `dvt0 dvt1 dvt2 dwg dwb pdiblc1 pdiblc2 drout prwg prwb a0
ags eta0 etab ute kt1`.

`k3 = 80` is what made d lnI/d lnW come out at 1.096 instead of 1.004 in the Phase 0 diagnosis.
Grounding it moves every narrow device in the sizing guide, which §11 should pre-register.

## 6. Points I want feedback on

| # | point | my proposal |
|---|---|---|
| **F1** | **Resistor matching normalization disagrees by ~23×.** ONC25's spec column reads 0.045 %·µm for high-res poly, but its *model* Pelgrom coefficient is 1.1–1.55, and AutoHV's current lumped value is 1.06 %·µm. The spec column is evidently a different normalization. | Ground the split on the **model-form** coefficient (1.1–1.55, consistent with today's 1.06), not the spec column, and record the discrepancy. Confirm. |
| **F2** | Global Vth σ: ONC25's bands (88 / 114 / 128 mV 3σ) are **wider than the brief's** §3.2 starting range of 60–90 mV. | Use ONC25 per class (it is measurement-grounded); 12 V declared at 150 mV. |
| **F3** | Calibrating `U0` σ to hit the ONC25 Idsat band makes it derived, not independently grounded. The alternative is to ground `U0` directly and let Idsat land where it lands. | Calibrate (§4.2), and record `U0` as `source: onc25-derived`. |
| **F4** | `TOX` σ at 4 % 3σ is **4× today's cards** (which move tox ±1 % across FF/SS). Every capacitance, gm and AC number moves. | Take the physical value; add "all Cgg/gm/AC numbers move" to §11. |
| **F5** | Moving 1.8 V and 3.3 V A_VT onto the oxide rule (3.5 → 4.25, 4.0 → 6.75 mV·µm) changes published mismatch σ for those classes by +21 % and +69 %. | Do it — the rule is the grounded one and the 5 V/12 V values already obey it. Pre-register both. |
| **F6** | The gate-rating oxide rule puts all 13 VDMOS on `TOX_50`. | Confirm. |
| **F7** | `RHEAD_<layer>`, `CPER_<type>`, `DW_ACT_*`, `RSH_GATE` have no source and carry ±50–100 % error bars. | They go in the JSON as `declared` with those bars, and the generated residue table in `process-declarations.md` lists them. |
| **F8** | **Which bias defines "fast"?** The corner direction depends on the metric. At the sizing-guide bench (gm/Id ≈ 6, analog) the direction differs from classic Idsat at Vgs = Vds = supply. | Use classic Idsat (Vgs = Vds = class supply) for the corner direction, since that is what "FF/SS" conventionally means, and report the analog-bench direction alongside in `corners.json`. |

## 7. After feedback

I author `models/stat_model.json`, `docs/stat-model.md`, `docs/bsim3-defaults-audit.md`, run the
two measurement passes, and bring the preset table with Mahalanobis distances to Stop A. Nothing
is generated until you approve it there.
