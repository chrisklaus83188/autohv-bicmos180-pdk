# D1 — VDMOS `kp` convention

## QUESTION

Is ngspice VDMOS saturation current `Id = kp·Vov²` or `Id = (kp/2)·Vov²`?

A factor of two that rescales every `kp` target in `docs/anchor-values.json`
`_vdmos_kp_conditional`, and therefore the size of the F1 finding in audit §2.1.

## METHOD

An isolation copy of `NDMOS200_INT` with `rd`, `rs`, `rq` forced to
`R_ZERO = 1e-9 Ω`, so no series drop can suppress the measured prefactor.
Everything else — `ksubthres` included — is byte-identical to the PDK card.

Bias at `Vov ∈ {1, 2, 3} V` at `Vds = 10 V`: clean strong inversion, well past
`Vdsat = Vov`, where the subthreshold term contributes nothing.

**On `lambda` and `theta`.** Both perturb a raw `Id/Vov²` fit. Rather than
suppress them by biasing at small `Vov` — which would trade a known,
card-stated perturbation for an unknown subthreshold contamination — they are
**divided out analytically** using the card's own values, read back from ngspice
rather than assumed:

```
A_corr = Id · (1 + theta·Vov) / ( Vov² · (1 + lambda·Vds) )
```

The corrections are small (`theta·Vov ≤ 5.4 %`, `lambda·Vds = 1.2 %`) and the
payload reports the uncorrected fit alongside, so the reader can confirm both
land on the same side of a fork whose arms are a factor of two apart.

`A` is fitted by least squares **through the origin** — `Id = A·Vov²` has no
constant term.

## VERDICT

**`kp/2`.**

| quantity | value |
|---|---|
| fitted prefactor `A` (corrected) | **0.11000000 A/V²** |
| card `kp` (NDMOS200, TT) | 0.22 |
| `kp/2` | 0.11 |
| **ratio `A/kp`** | **0.4999999986** |
| max relative residual | 2.8e-7 |
| pointwise `A_corr` spread | 3.9e-5 % |
| uncorrected `A/kp` (robustness) | 0.4816 — same side of the fork |

The agreement is exact to eight significant figures, which also confirms the
model's strong-inversion form is precisely
`Id = (kp/2)·Vov²/(1+theta·Vov)·(1+lambda·Vds)`. D4 re-confirms this
independently on all thirteen cards.

## CONSEQUENCE

**No anchor value changes. No `/2` is needed anywhere.**

Both routes in `_vdmos_kp_conditional.decision_A_10um_cell` already assume the
convention D1 measured:

- **`kp_n` / `kp_p`** are derived from `mu·Cox·(W/L_ch)` with no factor of two.
  That is exactly the SPICE level-1 `KP` definition, in which
  `Id_sat = (KP/2)(W/L)Vov²` — the two lives in the *current equation*, not in
  `KP`. Since VDMOS has no `W` or `L` and folds `W/L` into `kp`, the anchor's
  `kp = mu·Cox·(W/L)` is directly comparable to a card `kp` under the measured
  form. **Consistent.**
- **`kp_from_idsat_density`** states its basis as `kp = 2·Id/Vov²`, the algebraic
  inverse of `Id = (kp/2)Vov²`. **Consistent.**

**Proposed amendment (maintainer applies):** add a `convention` field to
`_vdmos_kp_conditional` recording
`"ngspice VDMOS: Id_sat = (kp/2)·Vov²; measured A/kp = 0.5000 (D1)"`, so the next
reader does not re-derive it. Target values unchanged.

**For the fix worklist:** the F1 implied-width finding of audit §2.1
(287×–5213×) **survives D1 intact**. What D1 removes is the possibility that a
factor of two of it was a bookkeeping error.

## RUN

```
python run.py
```

Decks land in `../../decks/d1_kp_convention/`, the isolation copy in
`../../results/local_models/NDMOS200_d1.mod`.
