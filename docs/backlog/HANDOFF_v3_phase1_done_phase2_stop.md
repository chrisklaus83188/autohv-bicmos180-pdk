# Handoff: §1 landed; Phase 2 contract pinned; one §2 stop before the generator

**Responds to:** the Stop A′ approval reply (§1 three items, then Phase 2)
**Branch:** `mc-realism` @ `10c4004`, pushed. Four commits since Stop A′.
**Date:** 2026-09-19
**Status:** §1.1, §1.2 and §1.3 are landed and measured. The Phase 2 input contract is fully
pinned. **One §2 stop (AC1)** before `gen_models.py` is written, plus one scope question (AC2).

---

## 1. What landed

| ruling | commit | outcome |
|---|---|---|
| 1.1 `k3` grounding | `d96aaf1` | audit table reproduced **exactly**; 8 of 40 directions moved |
| 1.2 oxide coupling | `248c6d6` | `applied = analytic − bsim3_residual` per card |
| 1.3 corners doc | `7100c72` | `docs/corners.md` created; table now generated, not typed |
| KPRD + coupling | `10c4004` | `_KPRD_sharing` authored; duplicate oxide mechanism removed |

### 1.1 `k3` — the audit reproduces to the digit, but only by its own method

`k3 = 2.0`, `k3b = 0`, `w0 = 2.5e-7` appended to all eight BSIM3 cards. They were **undeclared**,
so this is an append before each card's closing `+ )`, not a replace — a replace-only edit would
have silently changed nothing, which is a trap that already cost this program one wrong ablation.
Values read back from `showmod` on all eight cards rather than assumed.

| W | `k3 = 80` before | `k3 = 2` after | audit §4 predicted |
|---|---|---|---|
| 0.4 µm | +238 mV | **+29 mV** | 238 / 29 |
| 1.0 µm | +195 mV | **+14 mV** | 195 / 14 |
| 4.7 µm | +87 mV | **+3 mV** | 87 / 3 |
| 10 µm | +44 mV | **+1 mV** | 44 / 1 |

A constant-current extraction at 1 µA·(W/L) gives 255/205/91/46 and 37/18/4/2 instead — 5–8 % high.
Same device, different threshold definition. The audit's numbers are reproducible **only** by the
audit's method (the model's own `@m.xm1.m0[vth]`), so §4.1 now names the method.

**Direction delta after landing:** only the eight BSIM3 groups move, in bench-width order —
NMOS18 (bench 1.3 µm) 9.64 → 9.24 %, PMOS18 11.96 → 11.72, NMOS33 7.22 → 7.03, NMOS50 6.80 → 6.68,
the rest −0.08…−0.01. All 13 VDMOS, 5 resistors, 4 capacitors, 4 BJTs and 6 diodes unchanged to
0.00. Corner distances move +0.005…+0.007. Your prediction that the delta would be small, because
the benches use sizing-guide widths rather than minimum width, is confirmed.

### 1.2 Oxide coupling — and a correction to what I told you at Stop A′

| card | analytic | BSIM3 residual | applied | ratio |
|---|---|---|---|---|
| NMOS18 / PMOS18 | 7.18 / 8.13 mV | **−1.60 / −1.59** | 8.78 / 9.72 | 1.22 / 1.20 |
| NMOS33 / PMOS33 | 7.78 / 8.85 | −0.98 / −0.96 | 8.77 / 9.81 | 1.13 / 1.11 |
| NMOS50 / PMOS50 | 8.34 / 9.65 | −1.17 / −1.12 | 9.51 / 10.77 | 1.14 / 1.12 |
| NMOS12 / PMOS12 | 18.79 / 20.89 | −1.90 / −1.92 | 20.69 / 22.81 | 1.10 / 1.09 |

`k1` takes the full relative coupling: `showmod` confirms BSIM3 does not scale `k1` with `tox` at
all, so its residual is exactly 0.

**I reported this residual as 3.7–19.5 % and positive. Both were wrong.** That figure came from
constant-current and gm-max extraction, and those methods move *with* `tox` themselves — they fold
drive and slope changes into what they call threshold. The same NMOS18 device read −0.18 mV at a
1× W/L criterion, −0.61 at 0.1×, and **+3.52 at 10×**. A physical ∂Vth/∂t_ox cannot depend on which
current you call threshold, so all three were measuring the harness.

Measured from the model's own Vth with no extraction criterion, the residual is **−0.96 to
−1.92 mV** — negative on every card, which makes `applied` *larger* than analytic, not smaller.

An L-sweep on NMOS50 settles the mechanism: as carded the residual is −1.171 mV at L = 0.5 µm,
−0.222 at 1 µm, then **+0.035…+0.049 at L ≥ 2 µm**; with `dvt0/dvt1/dvt2/k3` zeroed it collapses to
≈0 at every length. BSIM3's implicit oxide-to-threshold coupling **is** the short-channel and
narrow-width terms, and at bench lengths they dominate and reverse the depletion-charge trend. Both
signs are real and measure different things.

### 1.3 Corners

`docs/corners.md` created with your wording verbatim. Two consequences documented as correct
behaviour rather than defects: a preset moving *k* variables to ±3σ sits at `3·√k` (hence all-MOS
FF/SS at 16.54), and FS/SF carry shared-variable conflicts because n and p share `TOX_<class>`,
`DL_POLY` and `DW_ACT_*`. The `≈ 3` expectation is recorded as void — it belonged to the
ρ-decomposition U1 retired.

`build_corners.py` gains `--write-md`, which regenerates the table between markers so the numbers
cannot rot while the prose stays hand-written.

## 2. Phase 2 — the input contract is pinned

| quantity | count |
|---|---|
| card-parameter expressions to emit | **46** (25 multiplicative, 21 additive) |
| of which correctly **skipped** | 13 — `TOX_50 × VDMOS → tox`, a parameter those cards do not have |
| `_STAT` params to **rewrite** (not delete) | 52 — 13 each of `VTO`/`KP`/`RD`/`RS`, every one with an identified driver |
| `P_*` params to delete | 186 |
| `_isXX` selector occurrences to delete | 183 |
| TT values carried over | 159, **zero unparsed** |

`Z_*` params must be named `Z_<exact corners.json key>` — `Z_TOX_18`, `Z_VTH_NMOS18`,
`Z_RDSW_NMOS18`. The brief's `Z_VTHN18` is illustrative shorthand; `corners.json` is what sets
these, so the names have to match it exactly or preset vectors will not resolve.

The 13 skipped pairings are model-correct, not a defect: the oxide reaches VDMOS through
`dependent_parameters`, not through a `tox` expression. The generator will skip a (variable,
device) pairing whose card lacks the parameter **with a stated reason**, so a genuinely missing
parameter still surfaces rather than being swallowed.

## 3. AC1 — §2 stop: `KPRD` signed sharing contradicts the measured corner vectors

I authored `_KPRD_sharing` as the ruling asks — one draw per device, `KP` at +1.0 and `RD` at −1.0.
Then I checked it against the z-vectors already in `corners.json`:

| group | `U0` z | `RDSW` z | ratio |
|---|---|---|---|
| NDMOS20 | +2.2595 | −1.7814 | **−0.79** |
| NDMOS60 | +1.2259 | −2.6517 | −2.16 |
| NDMOS80 | +0.8904 | −2.8110 | −3.16 |
| NDMOS120 | +0.5796 | −2.9163 | −5.03 |
| NDMOS200 | +0.4350 | −2.9505 | **−6.78** |

A single shared draw at +1.0/−1.0 implies a **constant** ratio of −1.0. The measurement gives −0.79
to −6.78. `corners.json` encodes `U0` and `RDSW` as independent variables, and the directions
harness measured them that way.

So the ruling's two halves differ in status:

- **`σ(KP) = 0` where drift-dominated is measured and implementable** — the five devices are
  identified by their own `U0` slope against the harness's 0.4 floor: NDMOS80 (0.365),
  NDMOS120 (0.265), PDMOS120 (0.285), NDMOS200 (0.212), PDMOS200 (0.216).
- **Signed sharing conflicts with the measurement.** Honouring it would change every VDMOS corner
  vector and all 13 Mahalanobis distances — designer-visible, and it re-opens the `corners.json`
  that Stop A′ approved.

I over-committed by authoring the +1.0/−1.0 coefficients before checking them against z-vectors I
already had. Same failure mode as the earlier "apply the full closed form" decision: asserting a
relationship instead of measuring it.

**Recommendation:** implement the `σ(KP) = 0` half; **drop signed sharing** and keep `U0`/`RDSW`
independent as measured, with the anti-correlation recorded as the demonstrated device property it
is rather than an imposed coefficient. If you want signed sharing anyway, it needs a re-measure and
a `corners.json` rebuild, and I would want that as its own package with the movers pre-registered.

Also worth noting for the 80 V pair: NDMOS80 at 0.365 is drift-dominated while PDMOS80 at 0.412 is
not. That is recorded per device rather than per voltage class, because a per-class rule would have
to pick one and be wrong about the other.

## 4. AC2 — who generates `corners.json`?

Brief §1 assigns it to `gen_models.py`, but `build_corners.py` already generates it and is the tool
`--check` guards. Two producers of one artefact is a defect waiting to happen.

**Proposal:** `gen_models.py` emits the `.inc` and *delegates* corners to the existing builder.
Flagging rather than assuming, since it deviates from the brief as written.

## 5. Observations

- **Three Vth extraction methods gave three different answers**, and only the model's own readback
  is criterion-free. Constant-current at 1 µA·(W/L), constant-current at other criteria, and gm-max
  linear extrapolation each move with `tox` themselves. This cost four measurement passes on §1.2
  and is worth remembering whenever a small threshold shift is the quantity of interest.
- **The audit's method had to be recovered before its table could be reproduced** — the first
  attempt was 5–8 % high purely from using a different threshold definition, and looked like a card
  discrepancy. Naming the method in §4.1 is the fix.
- **Four of my own edits needed repair this turn**: a heredoc wrote literal newlines inside string
  literals and left `build_corners.py` unable to import; the conflict list mixed `int` and `str`
  keys so a `join` raised; and a correction note landed *inside* two markdown tables, splitting
  them. All found by running the thing rather than reading the patch. I have stopped patching
  Python through nested shell heredocs.
- **`applies_to` uses `target` for wrapper-owned dimensions and `param` for card parameters**, and
  I briefly mistook the former for unresolved entries. It is a deliberate and correct distinction:
  `target` (`mos_L`, `mos_W`, `mos_rgate`) belongs to Phase 3 wrappers, which the `.lib` does not
  implement yet.

## 6. State

Tree clean at `10c4004`. `corners.json --check` green. Nothing from Phase 2 is written — the
generator waits on AC1 and AC2.
