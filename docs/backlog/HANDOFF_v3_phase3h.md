# Handoff: Phase 3h — three-term junction mismatch, and a knob that never worked

**Responds to:** the 2026-10-15 ruling (B6 bounds relaxed, option 1; autonomy-rule amendment)
**Branch:** `mc-realism` @ `8900a64`, pushed, tree clean, **seven checks green**
**Date:** 2026-10-16
**Status:** Phase 3 ~96 % done. The amendment is recorded and already applied once (§1).
**One pre-existing defect found that invalidates a class of past results** — §3.

---

## 1. The autonomy-rule amendment is in force and was used immediately

B6's two numeric bounds were relaxed to the derived result **with no stop**: old bound, new
bound and derivation recorded, work continued. That is exactly the one-line decisions-table
entry the amendment calls for, and it is also saved to my own standing notes so it survives
this session.

| bound | was | now |
|---|---|---|
| golden-geometry C shift | within 1 % | within 2 %, reported per type (+0.27 / +0.13 / +0.76 / +1.45 %) |
| fringe share | "a few percent" at any size | ≤ 5 % at ≥ 50 µm; at minimum legal geometry reported, not bounded |

No code change; the substantive clauses already passed.

## 2. Three-term junction mismatch (Q4)

The old wrapper had **one** `AREAEFF` term doing all the work. In Gummel-Poon `area` scales
`Is` but **not** `bf` — so that single term was an Is mismatch wearing a general name, and
**β mismatch was absent from this PDK entirely**.

- **Is** rides on `area`, which is exact: an area ratio *is* a Vbe shift of `n·V_T·ln(ratio)`
  at fixed Ic, so it needs no extra node. Sign set so `+Z_VBE` means *higher Vbe* — matching
  the knob's name rather than the parameter it happens to drive.
- **β** has no instance parameter at all, so it needs a circuit: sense `Ib` through a 0 V
  source and return a fraction of it with a CCCS. KCL gives `I_ext = Ib·(1−GB)`, so apparent β
  scales by `1/(1−GB)`; setting `GB = d/(1+d)` makes that **exactly** `1+d`, not a small-signal
  approximation.
- **`A_IS` is derived**, not declared — `A_VBE/(n·V_T)` with `n` read per card, so a Schottky
  (1.08) and a 24 V Zener (1.22) get different coefficients from one declared voltage: 0.0387
  for the NPNs down to 0.0317 for DZ_24V.

Verified on NPN_LV at AREA = 0.04:

| knob | measured | expected |
|---|---|---|
| `Z_VBE=1` | Ic ×0.98066, ΔVbe = 0.505 mV | σ(ΔVbe) = 1.0/√4 = 0.5 mV ✓ |
| `Z_BF=1` | β 91.634 → 92.556 (×1.01007), **Ic unchanged** | ×1.01 ✓, terms independent ✓ |
| `M=4` | Ic ×4.0000 | Is ∝ M ✓ |

No convergence trouble from the CCCS.

## 3. §2-class finding — the mirror characterisation's mismatch knob has never worked

Removing `MM_SIGMA` exposed that **ngspice silently accepts a subckt parameter the subckt does
not declare** — no error, no warning. Chasing what that might now break turned up something
much older.

`circuits/current_mirror_char/mirror_lib.py` writes `MM_SIGMA` only as a **top-level `.param`**,
never on an instance. A subckt parameter default **shadows** a same-named global. Measured
against the pre-Phase-3 wrapper that still declared `MM_SIGMA`:

| | `delvto` |
|---|---|
| top-level `.param MM_SIGMA=3`, not on the instance | **0.0000000000** |
| `MM_SIGMA=3` on the instance | 1.2643069248e-02 |

**Every mirror-characterisation run labelled with a non-zero `mm_sigma` was measuring the
typical device.** This predates the whole MC-realism program — the helper is unchanged in git
history, so any mirror mismatch number in the repo or in past reports should be read as a
typical-device result.

Fixed: `_dev` now passes the knob explicitly on every instance, and the existing `mm_sigma=`
argument keeps its name and finally bites.

**One thing I did not change, because it is a question about the characterisation rather than a
defect in it.** The helper applies the *same* value to every device, which is a **common-mode**
Vth shift — and a mirror ratio is only second-order sensitive to that. Measured: 1.130688e-05 →
1.131143e-05, **0.04 %**. A mirror *mismatch* corner wants opposite signs on input and output,
the way `pdk_validation/regression/transients/mismatch_corner.cir` already does it. Tell me
which you want and I will wire it in Phase 7, where these are regenerated anyway.

## 4. `MM_SIGMA` removal — functional work done, cosmetic work left

No wrapper declares it and no deck passes it to one; all five families are migrated
(250 MOS + 44 VDMOS + 51 resistor + 4 capacitor + 10 junction instance lines). What remains is
text that cannot reach a netlist: live docs that still describe the old knob (`README.md`,
`docs/QUICKSTART.md`, `docs/MISMATCH_CORNERS.md`), `xschem/gen_syms.sh` and the symbols it
emits, and the historical record in `docs/backlog/` and `CHANGELOG.md`, which keeps it
deliberately.

**I will add `MM_SIGMA` to `check_naming`'s forbidden set** with the same historical exemptions
as the retired device names, so it cannot return silently — the silent-acceptance behaviour
above is exactly why.

## 5. What remains in Phase 3

- the docs and symbol cleanup above, plus the `check_naming` guard
- **acceptance B2–B7** as scripts under `pdk_validation/`, N = 200, seed 0, LHS, with the
  relaxed B6 wording
- the minimum-geometry fringe column in `docs/sizing-guide.md`, per your §1

Then Phase 4 (`mc_driver`, `corner_sweep`) → **Stop B** → 5, 6, 7 → `v3.0-stats`.

## 6. State

`8900a64`, pushed, tree clean, seven checks green. Still outstanding and not mine: the stranded
worktree and the six `xschem/designs/*.sch` netlist checks.
