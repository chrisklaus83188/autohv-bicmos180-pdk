# Handoff: MC realism program — pre-start review, questions and concerns

**Responds to:** `HANDOFF_mc_realism_brief.md` (R0–R7, A1–A15 numbering used below)
**Evidence base:** `HANDOFF_monte_carlo.md`, the repo snapshot, and `analysis/corner_precheck.md`
**Date:** 2026-09-14
**Status:** review only. No phase started, no PDK file changed.

## 0. State at review time

| item | value |
|---|---|
| checked-out branch / HEAD | `transmission-gates` @ `61de05f` |
| `main` = `origin/main` | `1040b83`, 1 commit behind `transmission-gates`, unmerged |
| models on HEAD vs `main` | `.lib`, `.inc`, `device_limits.csv` identical |
| uncommitted, not part of this program | `.gitignore`, `docs/backlog/README.md`, 3 xschem designs modified; 5 xschem files untracked |
| local simulator | ngspice-45 |
| MC rig re-run | `01_mc_mirror.py` re-run on 2026-09-14 is byte-identical to the stored JSON (σ/µ = 4.331 %, 200/200 distinct) |

Chris has ruled the transmission-gate work complete and **not blocking**. That waives the brief's
"stop if `main` is behind a branch" condition. The base question that remains is Q1.

## 1. Summary

| # | brief ref | severity | issue in one line | recommended ruling |
|---|---|---|---|---|
| C1 | header, Phase 0.1 | low | tree holds uncommitted non-program edits; `main` behind TG | merge TG to `main`, run the program in a separate worktree |
| C2 | R0, A2b, A4(ii), R3 | **high** | no corner moves any geometry parameter; `PROC_Z_DL/DW` can never be derived | build per-shape structure, test with a harness-only perturbation, defer σ grounding |
| C3 | A2 vs R0 | medium | NF changes Id at TT by up to 2 % through `wint`; A2's 1 % contradicts R0 | compare NF=k to k explicit W/k instances; report delta vs NF=1 |
| C4 | R4, R5 | **high** | wrappers have Vth/W/L terms, no β term; `Z_BETA`/`Z_GEOM` don't map | `Z_VT`, `Z_W`, `Z_L`; no β term this program |
| C5 | R7 | **high** | there are no literal corner cards; `PROC_ON` terms sit inside card expressions | allow rewriting card *expressions* (corner numbers untouched, A13 guards it) |
| C6 | §8 | medium | derived process σ is up to 3.2× the current `PROC_ON` σ; not a pre-registered mover | add to §8 |
| C7 | A12 vs R7.3 | **high** | 93 of 186 expressions fail 1 % by construction under the asymmetry ruling | redefine A12 as exact self-test vs the ruled model plus a card-deviation table |
| C8 | R7.2, A14 | **high** | grouping granularity is undefined and decides whether A14 can pass | group by pattern × family × voltage class; A14 band 3–4.3σ |
| C9 | R3 | **high** | R3 needs coefficients that are not grounded; freeze line says residue is closed | amend the freeze with one scoped R3 item |
| C10 | R2 | medium | "F6 extension lengths" do not exist; wrappers hardcode 0.5 µm | 0.5 µm = stripe width, shared inner stripe split per finger |
| C11 | Phase 1 scope | medium | every HV wrapper already has `M`; VDMOS already scales mismatch with M | keep `M` on HV; fix `AUM2` on NMOS12/PMOS12 |
| C12 | R2 (VDMOS) | medium | ngspice VDMOS has no W/L/AD/AS; `NF` has no electrical lever | no `NF` on VDMOS/LDMOS/DNMOS20; drop A2b VDMOS leg |
| C13 | Phase 3 | medium | `alterparam` reaches top-level params only; hierarchy breaks per-instance z | per-instantiation-path subckt cloning; op-only for v2.3 |
| C14 | header, Phase 5 | medium | CI runs apt ngspice 41–42, not 45; native seeding measured on 45 only | build and cache ngspice-45 in CI |
| C15 | Phase 6 | low | `MM_SIGMA` in 137 files; `M>1` widespread; lib header count stale | enumerate affected artifacts in the results handoff |
| C16 | process | low | checkpoints and push cadence unspecified | review stops after Phase 0 and Phase 3; push branch per phase |

## 2. Verified facts the rulings rest on

| brief assumption | what the repo shows | evidence (paths relative to `repo/`) |
|---|---|---|
| wrappers to modify | **40** subckts: 8 BSIM3 MOS, 13 VDMOS/LDMOS/DNMOS, 4 BJT, 6 diode, 5 R, 4 C. The lib header says 38 (stale). | `autohv_bicmos180_case.lib` |
| `AUM2` defect is MOS-wide | `AUM2` appears in 17 wrappers = 8 BSIM3 MOS + 5 R + 4 C. The MOS ones omit `M`. R and C have **no `M` parameter at all**. | `.lib` lines 15, 25, …, 482+, 544+ |
| HV FETs lack `M` | all 13 VDMOS-family wrappers have `M`, computing `mtot={(W/W_REF)*M}` with `DVTH_MM ∝ 1/sqrt(mtot)` — already R1-correct. NMOS12/PMOS12 are BSIM3 level 49 with the same `AUM2` defect as LV. | `.lib` 74–93, 94–116, 324–352; `.inc` 728–731 |
| MOS mismatch terms | three: `DVTH_MM` (delvto), `DWREL_MM` (W), `DLREL_MM` (L). **No β/mobility term.** All `AGAUSS(0, 3σ, 3)`. | `.lib` 15–18 |
| R/C mismatch | one lumped term each: R applied to L (`L={L*RMM}`), C applied to area (`L*LS`, `W*LS`). No head resistance, no NS. | `.lib` 482–494, 544–558 |
| corners move geometry (R0 prerequisite) | **No.** 0 of 186 corner expressions touch `lint/wint/dwc/dlc/xl/xw/narrow/short`. Those exist as fixed values (table in C2). | `analysis/corner_precheck.md` |
| literal corner cards (R7) | **No.** Each parameter is `((tt*_isTT + ff*_isFF + ss*_isSS + fs*_isFS + sf*_isSF))` with `+P_X` or `*(1+P_X)` inline. VDMOS hoists the same pattern into `*_STAT` `.param`s. | `.inc` 20–24, 338+, 283–285 |
| existing `PROC_ON` path | independent, hand-set `AGAUSS(0,σ3,3)` per class and parameter (e.g. `P_TOX_18`, `P_TOX_33`, `P_TOX_50` separate), not derived from corners | `.inc` from line 26 |
| F6 extension lengths declared | **No.** F6 is MOS junction-cap densities. Wrappers hardcode `AD={WEFF*0.5u}`, `PD={2*(WEFF+0.5u)}`. | `docs/process-declarations.md` (F6 row); `.lib` device lines |
| `rgate`/`rsh_poly` in wrappers | none in any wrapper or BSIM3 card; VDMOS cards carry a fixed `rg=2` | `.lib`, `.inc` |
| VDMOS geometry | ngspice VDMOS takes no W/L/AD/AS. Size enters only through `m=W/10u` (fractional allowed: W=3u → m=0.3). `cjo`, `cgs`, `cgdmax` are absolute per cell. | `.inc` 856–881 |
| resistor TT edge bias | exists: R cards carry fixed `narrow`/`short` (e.g. RPOLY_HI 1.2e-7/1.0e-7, RNWELL 1.8e-7/1.5e-7) | `.inc` 1435–1475 |
| CI simulator | `apt-get install ngspice` on ubuntu-24.04 — 41–42 per inventory item 23, not 45 | `.github/workflows/regression.yml`; `docs/characterization-inventory.md` item 23 |
| preflight | 169 lines, static parsing only; no gate invokes ngspice today | `pdk_validation/preflight.py` |
| synthetic residue | "the residue is three items and nothing else"; "the realism program freezes" | `docs/process-declarations.md`, "Synthetic residue — the freeze line" |

## 3. Concerns in detail

### C1 — Base and working tree

`main` is at `1040b83`; `transmission-gates` is `61de05f`, one commit ahead and pushed. The
working tree also carries uncommitted xschem/`.gitignore`/backlog edits that are not part of this
program. Phase 0.1 says "commit or stash" them. I should not decide the fate of edits that aren't mine.

**Q1.** Merge `transmission-gates` into `main`, then branch `mc-realism` from `main` in a separate
`git worktree`, leaving the main tree's uncommitted edits untouched? (Recommended.)

### C2 — R0 prerequisite fails: no geometry lever in any corner

Fixed geometry offsets per BSIM3 card (none corner-dependent):

| card | wint (m) | lint (m) |
|---|---|---|
| NMOS18 | 5e-9 | 1.2e-8 |
| PMOS18 | 7e-9 | 1.5e-8 |
| NMOS33 | 8e-9 | 1.8e-8 |
| PMOS33 | 1.0e-8 | 2.0e-8 |
| NMOS50 | 1.2e-8 | 2.5e-8 |
| PMOS50 | 1.4e-8 | 2.8e-8 |
| NMOS12 | 1.5e-8 | 3.0e-8 |
| PMOS12 | 1.6e-8 | 3.2e-8 |

Consequences the brief does not state:
- R7 derives variables only from corner deltas, so **`PROC_Z_DL` / `PROC_Z_DW` will not exist**.
  A2b ("corner card or `PROC_Z_DW=+3`") and A4(ii) ("corner or `PROC_Z_DL=+3`") have no driver.
- R3's `DL_bias`/`DW_bias` "shifted by corners and by Phase-4 DL/DW" have a TT value (the R cards'
  `short`/`narrow`) but no σ source.
- Adding geometry movement means either editing corner cards (frozen) or adding a non-derived
  stat variable (contradicts R7).

The structure is still worth building. With `W={W/NF}` and `m={NF*M}`, BSIM3 applies `wint` per copy,
so width bias is amplified per finger automatically.

**Q2.** Build the per-shape structure, and verify A2b/A4(ii) with a *harness-only* perturbation of
`wint`/`lint`/`narrow`/`short` in a scratch copy of the `.inc`? Edge-bias σ grounding would be deferred
to a later program. (Recommended.) The alternative is for Chris to ground a DL/DW σ now, which needs
a ruling on where a non-derived variable lives.

### C3 — A2 (Id within 1 % across NF) contradicts R0 at TT

Total effective width with `W/NF` fingers is `W − 2·NF·wint`, versus `W − 2·wint` at NF=1. The loss is
`2(NF−1)·wint`, before any narrow-width Vth shift on the narrower fingers:

| device, W = 4.7 µm | NF=2 | NF=4 |
|---|---|---|
| NMOS18 (wint 5e-9) | 10 nm, 0.21 % | 30 nm, 0.64 % |
| NMOS50 (wint 1.2e-8) | 24 nm, 0.51 % | 72 nm, 1.53 % |
| PMOS12 (wint 1.6e-8) | 32 nm, 0.68 % | 96 nm, 2.04 % |

(First-order width loss; Id tracks it roughly linearly in strong inversion.)

**Q3.** Change A2 to: `NF=k` must equal k explicitly instantiated `W/k` devices (an independent
construction; exact), and the delta vs `NF=1` is *reported* alongside the analytic `2(NF−1)·wint/W`
prediction, as A3 already does for `M`? σ(delvto) invariance stays; it's exact by construction since
`NF` is not in `AUM2`. (Recommended.)

### C4 — Knob and constant names don't map onto the wrapper terms

| brief (R4/R5) | wrapper term today | mapping |
|---|---|---|
| `A_VT`, `Z_VT` | `DVTH_MM` | clean |
| `A_BETA`, `Z_BETA` | **none** | no existing term |
| `A_W` | `DWREL_MM` | clean |
| `A_L` | `DLREL_MM` | clean |
| `Z_GEOM` | both `DWREL_MM` and `DLREL_MM`? | one knob on two terms makes them perfectly correlated — the flaw HANDOFF_monte_carlo §4 flagged in the prototype |

If `Z_BETA` means a *new* mobility term, it is a value change. That breaks R4's
"< 1e-6, notation only" acceptance and §8's "sizing-guide σ, M=1 unchanged", and it needs a
grounded `A_BETA`.

Non-MOS devices also carry `MM_SIGMA` and need knob names that R5 does not give:

| family | mismatch term today | proposed knob |
|---|---|---|
| VDMOS/LDMOS/DNMOS | gate `Vshift` = `DVTH_MM` | `Z_VT` |
| BJT, diode | `AREAEFF` relative | `Z_AREA` |
| resistor | `RMM` (lumped; split by R3) | `Z_R` (as R3 says) |
| capacitor | `CMM` | `Z_C` |

**Q4.** MOS knobs `Z_VT`, `Z_W`, `Z_L`, with no β term in this program, and the non-MOS names
above? (Recommended.)

### C5 — There are no literal corner cards to derive from "without editing"

Every corner-dependent parameter is an inline expression, and the current `PROC_ON` perturbation
lives inside the same expression:

```
vth0={((0.48*_isTT + 0.4*_isFF + 0.56*_isSS + 0.4*_isFS + 0.56*_isSF))+P_DVTH_NMOS18}
u0={((420*_isTT + 495.6*_isFF + 352.8*_isSS + 495.6*_isFS + 352.8*_isSF))*(1+P_DU0_NMOS18)}
.param VTO_NDMOS20_STAT={(((1*_isTT + 0.96*_isFF + 1.06*_isSS + 0.96*_isFS + 1.06*_isSF))+P_DVTO_NDMOS20)}
```

Derivation is straightforward: the generator evaluates each expression per case. But "rewire only
the `PROC_ON=1` path" requires rewriting all 186 expressions. The corner numbers stay identical, and
A13 (byte-identical 36-corner regression) guards that.

A second question hides here. Today `case=1` and `PROC_ON=1` compose: process spread is applied
around the FF card. After rewiring, R7.4 centres the stat model at TT.

**Q5a.** Is rewriting the card *expressions* (numbers untouched, A13 as the guard) within "cards are
frozen"? (Recommended: yes.)
**Q5b.** With `PROC_ON=1`, should `case≠0` be rejected, or should the spread centre on the selected
corner? (Recommended: reject, with a preflight error; a corner and a statistical run are different
questions.)

### C6 — Process σ moves substantially; not in §8

1σ values, current `PROC_ON` vs derived `σ=(FF−SS)/6`:

| parameter | current 1σ | derived 1σ | ratio |
|---|---|---|---|
| NMOS18 vth0 | 8.33 mV | 26.7 mV | 3.2× |
| NMOS18 u0 | 3.33 % | 5.67 % | 1.7× |
| PMOS18 u0 | 3.33 % | 6.33 % | 1.9× |
| tox (18/33/50 V classes) | 0.333 %, three independent | 0.333 %, one shared (cards move tox ±1.000 % identically in all classes) | 1.0× (correlation changes) |
| NDMOS20 vto | 13.3 mV | 16.7 mV | 1.25× |
| NDMOS20 kp | 3.33 % | 5.00 % | 1.5× |

Every `PROC_ON=1` result in the repo (for example the mirror's process+mismatch 1.344 %) will move.

**Q6.** Accept these as pre-registered movers and add them to §8? (Recommended.)

### C7 — A12 fails by construction under the asymmetry ruling

Many corners are built as reciprocal multipliers, e.g. PMOS18 `rdsw` = 180 TT, 150 FF (=TT/1.2),
219.512 SS (=TT/0.82). With `σ=(FF−SS)/6` centred at TT, `z=±3` cannot land on both cards. Full table
in `analysis/corner_precheck.md`.

| σ form | expressions over 1 % | worst | worst case |
|---|---|---|---|
| linear, centred at TT (brief R7.3) | 93 / 186 | 3.17 % | reciprocal-multiplier params (BJT `tr/rb/rc/re`, diode `rs`, `rdsw`) |
| log-space, `TT·exp(s·z)`, `s=ln(FF/SS)/6` | 15 / 186 | 1.42 % | NMOS18 `vth0` (additive, symmetric; log hurts it) |
| better of the two per parameter | 13 / 186 | 1.13 % | — |

Linear-form failures by parameter: `u0` 8/8, `rdsw` 8/8, VDMOS `RD` 13/13 and `RS` 13/13, BJT
`bf/rb/rc/re/tf/tr` 4/4 each, diode `rs` 6/6, `tt` 5/5, resistor `rsh` 5/5, plus some VDMOS `KP`/`VTO`.
Exact or within 1 %: `vth0`, `tox`, `vsat`, `pclm`, `js`, `cj`, `cjsw`, `cjo`, `bv`, `is`, `BVCBO`.

All 186 expressions fall into exactly three patterns (details in C8). None needs the brief's
"corner-only, leave out" escape clause.

**Q7.** Choose one:
- **(a)** keep linear σ; A12 becomes an exact self-test against the *ruled* model value
  (`TT ± 3σ`), and the per-parameter card deviation is tabulated, not failed. (Recommended: preserves
  the ruling, and A12 then tests the generator.)
- **(b)** log-space σ for multiplicatively built parameters and linear for additive ones, with A12
  tolerance 1.5 %. This is a σ-form change, which the brief defers to Chris.

### C8 — Grouping granularity decides whether A14 can pass

Patterns found (`analysis/corner_precheck.md`):

| pattern | count | members |
|---|---|---|
| FS=FF, SF=SS (N-type speed) | 67 | NMOS18/33/50/12 `vth0/u0/vsat/rdsw`; all NDMOS/DNMOS `VTO/KP/RD/RS/bv`; NPN `bf/is/rb/rc/re/tf/tr`, NPN `BVCBO` |
| FS=SS, SF=FF (P-type speed) | 62 | PMOS mirror of the above; PDMOS; PNP |
| FF/SS only (shared candidate) | 57 | LV `tox/pclm/js`; all diode params; all resistor `rsh`; all capacitor `cj/cjsw` |

Read by pattern alone, R7.2 produces three global variables. That makes NPN β 100 % correlated with
NMOS Vth, and poly sheet resistance 100 % correlated with gate oxide. R7.2 also says passives and
BJTs "get their own variable", so granularity needs a rule. The brief's example names (`VTHN` and `U0N`
separate) contradict co-movement, because vth0/u0/vsat/rdsw have identical patterns.

Effect on A14's "FF/SS Idsat at ≈ ±3σ": with independent contributors of sizes aᵢ, all at z=+3 in FF,
FF sits at `3·Σaᵢ/√(Σaᵢ²)` σ, which is 3σ for one dominant contributor and 3√k σ for k equal ones.

| granularity | NMOS50 Idsat contributors | FF position |
|---|---|---|
| (i) pattern × family | N-MOS speed + shared TOX group | 3–4.24σ |
| (ii) pattern × family × voltage class | N50 speed + shared TOX group | 3–4.24σ |
| (iii) pattern × parameter | vth0, u0, vsat, rdsw, tox, pclm | up to 7.3σ |

**Q8.** Use (ii): per-type speed variable per family and voltage class; one shared TOX group (the
cards move tox identically across classes); separate variables per resistor type, capacitor type,
diode, NPN, PNP. Change A14's band to "FF/SS within 3–4.3σ, value reported"? (Recommended.)

### C9 — R3 requires coefficients the grounding does not have; the freeze line is closed

What the local ONC25 extraction offers for R3 (categories only; the file is third-party data and is
not in this package):

| R3 coefficient | available | status if R3 proceeds |
|---|---|---|
| `A_RSH` / `A_W` / `A_LEND` split | one lumped matching coefficient per resistor type | split is synthetic |
| `σ_head` | not found | synthetic |
| `R_head` nominal | a contact-head temperature coefficient only, no resistance value found | synthetic |
| `R_link` | not found | ≈ 0 permitted by R3 |
| `DL_bias`/`DW_bias` TT | R cards' fixed `short`/`narrow` | existing, not new |
| `DL_bias`/`DW_bias` σ | not found; corners don't move them (C2) | synthetic or deferred |
| `A_C` for MIM | explicitly silent | wrapper already carries a literature value |

`process-declarations.md` states that after phase 4 "the residue is three items and nothing else" and
that the realism program "freezes". R3 adds at least four synthetic numbers.

**Q9.** Amend the freeze with a single fourth item, "resistor mismatch decomposition and contact head
(R3)", with error bars? Constrain the sheet/width/end split so that at a declared reference geometry
(NS=1, M=1) the combined σ reproduces today's lumped coefficient exactly, which keeps existing
resistor matching results unchanged. (Recommended.)

### C10 — "F6 extension lengths" do not exist

F6 in `process-declarations.md` is MOS junction-cap densities. The only diffusion geometry in the PDK is
the hardcoded `0.5u` in `AD={WEFF*0.5u}`, `PD={2*(WEFF+0.5u)}`.

**Q10.** Treat 0.5 µm as the drawn diffusion-stripe width for both outer and shared inner stripes (not a
new number), with each shared inner stripe's area and perimeter split half to each adjacent finger,
and the drain/source stripe count split by NF parity? (Recommended.) Or does "inner stripes half"
mean the inner stripe is drawn at 0.25 µm?

### C11 — Phase 1 scope table: HV `M`

The scope table says HV FETs get **no** `M`, but every HV wrapper already has one, and the VDMOS family
already scales mismatch with `1/√mtot`. Removing `M` would break existing instances, which the no-shims
rule forbids papering over. NMOS12/PMOS12 are BSIM3 wrappers with exactly the LV `AUM2` defect.

**Q11.** Keep `M` on all HV wrappers, and apply the R1 `AUM2` fix to NMOS12/PMOS12 as well as LV?
(Recommended.)

### C12 — VDMOS `NF` has no electrical lever (R2's stop-and-report case)

ngspice VDMOS has no W, L, AD, AS or per-finger geometry. The wrapper maps width to a fractional
`m=W/10u`, and junction/gate capacitances are absolute per cell. An `NF` parameter would change nothing
electrically, so A2's junction-cap monotonicity and A2b's width-bias leg cannot be met. A parameter that
silently does nothing is exactly the kind of trap this program exists to remove.

- **(a)** `NF` as bookkeeping only: the limits reader enforces `W/NF ≥ 3 µm`; no electrical effect.
- **(b)** no `NF` on VDMOS/LDMOS/DNMOS20 in this program; A2b runs on LV NMOS, LV PMOS and NMOS12
  instead of VDMOS.

**Q12.** (b)? (Recommended.)

### C13 — Driver: hierarchy and analysis scope

`alterparam` changes top-level `.param`s, not per-instance subckt parameters. The §4 prototype worked
by binding `MM_SIGMA={S1}` to a top-level param per instance. In a hierarchical deck, a user subckt
instantiated twice shares one body text, so both copies of an inner device would receive the same z.
That violates the brief's `(seed, hierarchical instance name)` determinism.

Options: flatten the deck (probe paths like `@m.x1.m0[delvto]` change names), or clone each user subckt
per instantiation path (`AMP` → `AMP__x1`, `AMP__x2`), each binding its own top-level z params. Cloning
preserves hierarchical instance names and probe paths.

**Q13a.** Per-path subckt cloning? (Recommended.)
**Q13b.** Is the v2.3 driver `op`-only as §4 describes, or are `dc`/`ac`/`tran` probes in scope?
(Recommended: `op` only; `tran` later.)

### C14 — CI simulator version

CI installs ngspice from apt on ubuntu-24.04, which inventory item 23 records as 41–42. The native
seeding behaviour (HANDOFF C2–C5b) was measured only on 45, so Phase 5's native liveness gate may
behave differently in CI. The driver path does not depend on ngspice's RNG, so its determinism is
version-independent.

**Q14.** Is building and caching ngspice-45 in the CI workflow in scope for this program? (Recommended:
yes, as a Phase 0 item, so every later acceptance runs on the same simulator locally and in CI.) The
final scorecard on CI requires pushing a branch.

### C15 — Blast radius for Phase 6

- `MM_SIGMA` appears in 137 files, including xschem symbols and designs (78), generated mirror netlists (32), and caches.
- `M=2…43` appears in hundreds of places across `circuits/` and `xschem/` (raw grep, not all device
  instances). Nominal results for `M>1` do not change (`M` already reaches the device). **Only their MC σ
  changes.** This also corrects HANDOFF_monte_carlo §6.1, which said the fix "invalidates published
  mismatch numbers": only `M>1` instances are affected.
- The lib header says "All 38 .SUBCKT devices"; there are 40.

No ruling needed. The results handoff will list every regenerated artifact.

### C16 — Checkpoints and pushing

**Q15.** Stop for review after Phase 0 (the inventory will surface wrapper-specific cases) and after
Phase 3 (before Phase 4 rewrites card expressions)? Push the `mc-realism` branch at each phase commit,
with the tag and `git ls-remote --tags` verification only at close-out? (Recommended.)

## 4. Errata to my earlier verbal review

| earlier statement | corrected |
|---|---|
| "all 17 MOS wrappers" carry the `AUM2` defect | 17 wrappers compute `AUM2`: 8 BSIM3 MOS (defect) + 5 R + 4 C (which have no `M` at all) |
| A2 width loss "1.3–2.0 %" | 0.64 % (NMOS18) to 2.04 % (PMOS12) at NF=4, W=4.7 µm; NMOS50 1.53 % |
| VDMOS uses "a separate `*_STAT` mechanism" | same corner-plus-`P_*` pattern, hoisted into `.param`s |

## 5. Rulings requested (answer "accept recommendations" to take every default)

| Q | question | recommended default |
|---|---|---|
| Q1 | base and working tree | merge TG → `main`; `mc-realism` branch in a separate worktree |
| Q2 | R0 edge bias | structure now, harness-only perturbation tests, σ grounding deferred |
| Q3 | A2 criterion | NF=k ≡ k explicit W/k devices; report delta vs NF=1 with analytic prediction |
| Q4 | knobs | MOS `Z_VT/Z_W/Z_L`, no β; VDMOS `Z_VT`, BJT/diode `Z_AREA`, R `Z_R`, C `Z_C` |
| Q5a | card expressions | rewriting expressions allowed; numbers untouched; A13 guards |
| Q5b | `case≠0` with `PROC_ON=1` | reject in preflight |
| Q6 | process σ movers | add C6 table to §8 |
| Q7 | A12 | (a) linear σ kept; exact self-test vs ruled model; card deviation tabulated |
| Q8 | grouping; A14 | pattern × family × voltage class, shared TOX; A14 band 3–4.3σ |
| Q9 | residue freeze | add one R3 item with error bars; split constrained to today's lumped σ at reference geometry |
| Q10 | diffusion geometry | 0.5 µm stripe for outer and shared inner; shared stripe split half per finger |
| Q11 | HV `M` | keep; fix `AUM2` on NMOS12/PMOS12 |
| Q12 | VDMOS `NF` | omit; A2b on LV NMOS, LV PMOS, NMOS12 |
| Q13 | driver | per-path subckt cloning; `op` only |
| Q14 | CI | build and cache ngspice-45 in CI as a Phase 0 item |
| Q15 | cadence | review stops after Phase 0 and Phase 3; push branch per phase |
