#!/usr/bin/env python3
"""
Passive R/C characterization -- phase-2 harness family module.

Covers the nine behavioral passive wrappers in autohv_bicmos180_case.lib:

    resistors   RPOLY_HI, RPOLY_LO, RNWELL, RNPLUS, RPPLUS
    capacitors  CMIM_STD, CMIM_HI, CMOM, CFRINGE

FoM keys match docs/anchor-values.json exactly, plus one extra diagnostic key
per device with no anchor band:

    golden_crosscheck    percent difference between the value this harness
                         measures and the stored phase-C regression golden
                         (pdk_validation/regression/goldens/<DEV>.json) at a
                         bias point that is on the golden's own V-grid.

Headline finding carried by this module:
  * F7 -- RPOLY_HI_INT sets tc1=+6e-4 (+600 ppm/degC). Lightly-doped poly
    conducts by thermionic emission over grain-boundary barriers, so
    rho ~ exp(q*PhiB/kT) and dR/dT must be NEGATIVE. The anchor band is
    -1500..-500 ppm/degC. tc1 is measured, not asserted, and comes out
    positive. See docs/model-realism-audit.md 5.1.
  * 5.2 -- all nine wrappers are optimistically matched. The measured
    A_R / A_C pair coefficients land 3-14x below the industry bands.

Read-only with respect to the PDK.

METHOD NOTES
------------
Resistors.  The wrapper is R0 (an ngspice R-model instance) in series with
BVCR, a behavioral source contributing V(p,mid)*(VCR1*|V| + VCR2*V^2), so the
two-terminal law is

    R(V) = R_geo * (1 + VCR1*|V| + VCR2*V^2)

R is read from a DC operating point as V/(-i(Vp)), and the R(V) sweep reuses
the phase-C regression pattern exactly (`dc Vp -5 5 0.25`).

Sheet resistance.  The ngspice R model applies the `narrow` and `short` edge
de-bias to BOTH edges of each dimension:

    R_geo = rsh * (L - 2*short) / (W - 2*narrow)

`narrow` and `short` are read out of autohv_bicmos180_case_models.inc (they
are set on all five cards) and inverted, so the reported rsh is the CARD's
rsh, not the ~2.3% biased R*W/L. The uncorrected number is carried in
conditions as rsh_uncorrected_ohm_per_sq for comparison.

Capacitors.  Measured by AC probe (1 V ac, 1 MHz) at a DC bias, i.e. the true
small-signal dQ/dV. This deliberately differs from the phase-C golden, which
uses the PWL-ramp-in-.tran method. THE TWO DISAGREE BY 10x ON THE BIAS TERM:
at V=5 the AC probe reads C/C(0)-1 = 6.494e-4, exactly the wrapper's
VCC1*5 + VCC2*25 = 6.50e-4, while the tran-ramp golden reads 6.50e-5. The
ramp method under-reads the `Cextra` behavioral-capacitor contribution by 10x
in this ngspice build, so an ac-based VCC1 is the one that recovers the
wrapper's own coefficient. The zero-bias capacitance agrees between the two
methods to 3e-8 relative, which is what golden_crosscheck asserts.

ngspice-45 gotchas honoured throughout:
  * every .control block sets `width=1000` -- `print` otherwise truncates at
    80 columns and SILENTLY drops trailing vectors;
  * every .control block sets `numdgt=12` -- the 6-significant-digit default
    quantizes a 50 ppm mismatch draw into ~50 steps;
  * DC-sweep rows are `index sweepvar vec...`, so the sweep variable is never
    itself printed.
"""
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

from char_lib import (header, run_deck, deck_path, parse_dc_sweep, parse_prints,
                      ngspice_errored, Collector, linfit, tempco_ppm, mc_run,
                      cap_from_ac, CORNER_CASE, load_anchors, REPO_ROOT, EPS0)

DEVICES = ["RPOLY_HI", "RPOLY_LO", "RNWELL", "RNPLUS", "RPPLUS",
           "CMIM_STD", "CMIM_HI", "CMOM", "CFRINGE"]

RESISTORS = DEVICES[:5]
CAPACITORS = DEVICES[5:]

SUBDIR = "passives"

MC_N = 200
CAP_FREQ = 1.0e6

# Low-bias operating point for the sheet-resistance read: small enough that
# the VCR1*|V| term contributes 20 ppm (RPOLY_HI) to 800 ppm (RNWELL), which
# is backed out analytically below.
R_LOW_BIAS = 0.1

# Golden crosscheck bias points. Both are ON the stored golden's V-grid
# (R: -5..5 step 0.25; C: 0..5 step 0.25) so no interpolation is needed.
R_GOLDEN_V = 1.0
C_GOLDEN_V = 0.0

# Geometry. Resistors and capacitors are characterized at the same geometry
# the phase-C goldens use, so golden_crosscheck needs no re-run.
R_L_UM, R_W_UM = 100.0, 10.0
C_L_UM, C_W_UM = 100.0, 100.0

# Matched-pair Monte Carlo geometry: W*L = 100 um^2 so sqrt(W*L) = 10 um and
# the Pelgrom normalization is exact.
MC_L_UM, MC_W_UM = 10.0, 10.0
MC_AREA_UM2 = MC_L_UM * MC_W_UM

# Cap C(V) bias ladder for the VCC1/VCC2 fit (V).
C_BIASES = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]

TEMPS = [-40.0, 27.0, 150.0]

# --------------------------------------------------------------------------
# per-device constants read out of the PDK (NEVER written back)
# --------------------------------------------------------------------------
# narrow/short: ngspice R-model edge de-bias, from
#   autohv_bicmos180_case_models.inc  .model <DEV>_INT R
# mm3s: the wrapper's own AGAUSS 3-sigma coefficient, from
#   autohv_bicmos180_case.lib  .subckt <DEV>  .param RMM/CMM
# vcr/vcc: the wrapper's own declared coefficients, for comparison only --
#   this module MEASURES them, it does not consume them.
RES = {
    "RPOLY_HI": dict(narrow=1.2e-7, short=1.0e-7, mm3s=0.0075,
                     card_rsh=1200.0, card_tc1=6.0e-4, card_tc2=1e-6,
                     card_vcr1=200e-6, card_vcr2=10e-6),
    "RPOLY_LO": dict(narrow=1.5e-7, short=1.2e-7, mm3s=0.003,
                     card_rsh=25.0, card_tc1=1.0e-3, card_tc2=2e-6,
                     card_vcr1=50e-6, card_vcr2=2e-6),
    "RNWELL":   dict(narrow=1.8e-7, short=1.5e-7, mm3s=0.013,
                     card_rsh=1800.0, card_tc1=4.0e-3, card_tc2=5e-6,
                     card_vcr1=8000e-6, card_vcr2=400e-6),
    "RNPLUS":   dict(narrow=1.8e-7, short=1.4e-7, mm3s=0.005,
                     card_rsh=32.0, card_tc1=9.0e-4, card_tc2=1.5e-6,
                     card_vcr1=1500e-6, card_vcr2=80e-6),
    "RPPLUS":   dict(narrow=1.8e-7, short=1.4e-7, mm3s=0.0055,
                     card_rsh=58.0, card_tc1=1.1e-3, card_tc2=1.6e-6,
                     card_vcr1=1800e-6, card_vcr2=90e-6),
}

CAP = {
    "CMIM_STD": dict(mm3s=0.0015, eps_r=7.0, dielectric="silicon nitride",
                     card_cj=1.0e-3, card_tc1=3.5e-5, card_tc2=5e-8,
                     card_vcc1=30e-6, card_vcc2=20e-6),
    "CMIM_HI":  dict(mm3s=0.002, eps_r=7.0, dielectric="silicon nitride",
                     card_cj=2.0e-3, card_tc1=4.5e-5, card_tc2=6e-8,
                     card_vcc1=60e-6, card_vcc2=40e-6),
    "CMOM":     dict(mm3s=0.006, eps_r=4.0, dielectric="SiO2",
                     card_cj=3.5e-4, card_tc1=2.0e-5, card_tc2=3e-8,
                     card_vcc1=5e-6, card_vcc2=2e-6),
    "CFRINGE":  dict(mm3s=0.0075, eps_r=4.0, dielectric="SiO2",
                     card_cj=1.8e-4, card_tc1=1.5e-5, card_tc2=2e-8,
                     card_vcc1=3e-6, card_vcc2=1e-6),
}

F7_NOTE = (
    "F7 (docs/model-realism-audit.md 5.1). RPOLY_HI_INT carries tc1=+6e-4, "
    "so R RISES with temperature. Lightly-doped high-sheet poly conducts by "
    "thermionic emission over grain-boundary barriers, rho ~ exp(q*PhiB/kT), "
    "which makes dR/dT NEGATIVE; the anchor band is -1500..-500 ppm/degC. "
    "The wrong SIGN over a 190 degC automotive span is a qualitative error, "
    "not a calibration offset."
)

MATCH_NOTE_TAIL = (
    "CONVENTION: this is the PAIR sigma. It is measured as "
    "stdev((X1-X2)/mean(X)) over N independent matched-pair samples, i.e. the "
    "sigma of the DIFFERENCE of two devices. That IS the pair convention the "
    "anchor is written in, so it is NOT multiplied by sqrt(2) again -- the "
    "sqrt(2) is already inside the measured difference. The wrapper models a "
    "PER-DEVICE draw with 1-sigma = coeff/3/sqrt(W*L um^2); the per-device "
    "number recovered as sigma_pair/sqrt(2) is carried in conditions so the "
    "two conventions can be read side by side."
)


# --------------------------------------------------------------------------
# small numerical helpers
# --------------------------------------------------------------------------

def _fnum(x: float) -> str:
    return repr(float(x))


def _solve(a: list[list[float]], b: list[float]) -> list[float]:
    """Gaussian elimination with partial pivoting on a small dense system."""
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(m[r][c]))
        if abs(m[piv][c]) < 1e-300:
            raise RuntimeError("singular design matrix in polynomial fit")
        m[c], m[piv] = m[piv], m[c]
        for r in range(n):
            if r == c:
                continue
            f = m[r][c] / m[c][c]
            for k in range(c, n + 1):
                m[r][k] -= f * m[c][k]
    return [m[i][n] / m[i][i] for i in range(n)]


def _polyfit_basis(xs, ys, basis) -> list[float]:
    """Least-squares fit y = sum_k coeff[k] * basis[k](x)."""
    nb = len(basis)
    if len(xs) < nb:
        raise RuntimeError(f"need >={nb} points for a {nb}-term fit, got {len(xs)}")
    phi = [[f(x) for f in basis] for x in xs]
    ata = [[sum(p[i] * p[j] for p in phi) for j in range(nb)] for i in range(nb)]
    atb = [sum(p[i] * y for p, y in zip(phi, ys)) for i in range(nb)]
    return _solve(ata, atb)


def _check(out: str, what: str) -> None:
    err = ngspice_errored(out)
    if err:
        raise RuntimeError(f"{what}: ngspice error: {err}")


def _need(prints: dict, key: str, what: str) -> float:
    if key not in prints:
        raise RuntimeError(f"{what}: '{key}' missing from ngspice output")
    return prints[key]


def _ctl(body: str) -> str:
    """.control block with the two ngspice-45 output gotchas neutralized."""
    return (".control\n"
            "set width=1000\n"      # else `print` truncates at 80 cols
            "set numdgt=12\n"       # else 6 sig figs quantizes ppm-level deltas
            + body +
            ".endc\n.end\n")


# --------------------------------------------------------------------------
# golden crosscheck
# --------------------------------------------------------------------------

GOLDEN_DIR = REPO_ROOT / "pdk_validation" / "regression" / "goldens"


def _golden(dev: str, v: float) -> tuple[float, dict]:
    """Return (golden value at bias v, provenance dict). Exact grid hit only."""
    p = GOLDEN_DIR / f"{dev}.json"
    if not p.exists():
        raise RuntimeError(f"golden not found: {p}")
    with open(p, encoding="utf-8") as f:
        g = json.load(f)
    grid = g.get("v_grid") or []
    vals = g.get("values") or []
    if len(grid) != len(vals) or not grid:
        raise RuntimeError(f"golden {dev}.json malformed")
    best = min(range(len(grid)), key=lambda i: abs(grid[i] - v))
    if abs(grid[best] - v) > 1e-9:
        raise RuntimeError(f"bias {v} V is not on the golden V-grid for {dev}")
    return vals[best], {
        "golden_file": p.relative_to(REPO_ROOT).as_posix(),
        "golden_device": g.get("device"),
        "golden_type": g.get("type"),
        "golden_ngspice_version": g.get("ngspice_version"),
        "golden_bias_V": grid[best],
        "golden_value": vals[best],
    }


def _emit_crosscheck(col: Collector, dev: str, measured: float | None,
                     v: float, deck: str, cond: dict, method_note: str) -> None:
    try:
        if measured is None:
            raise RuntimeError("nominal measurement unavailable")
        gval, prov = _golden(dev, v)
        if gval == 0:
            raise RuntimeError("golden value is zero")
        pct = (measured - gval) / gval * 100.0
        col.derived(dev, "golden_crosscheck", pct, "percent",
                    conditions=dict(cond, measured_value=measured, **prov),
                    deck=deck,
                    note=("ties the phase-2 harness to the phase-C regression "
                          "golden: 100*(harness - golden)/golden at a bias "
                          "point on the golden's own V-grid, at the golden's "
                          "own geometry. " + method_note))
    except Exception as e:                                    # noqa: BLE001
        col.derived(dev, "golden_crosscheck", None, "percent", conditions=cond,
                    deck=deck, error=str(e))


# --------------------------------------------------------------------------
# deck builders -- resistors
# --------------------------------------------------------------------------

def _deck_r_op(dev: str, v: float, corner: str = "TT",
               temp: float | None = None) -> str:
    """Single-bias DC operating point on one resistor."""
    ttl = (f"{dev} R at Vp={v} V, L={R_L_UM}u W={R_W_UM}u, corner {corner}"
           + (f", T={temp} degC" if temp is not None else ""))
    d = header(ttl, instruments="Vp -- ideal DC source (forcing terminal bias)",
               case=CORNER_CASE[corner], temp=temp)
    d += f"Vp p 0 dc {_fnum(v)}\n"
    d += f"X1 p 0 {dev} L={R_L_UM}u W={R_W_UM}u\n"
    d += _ctl("op\nprint i(Vp)\n")
    return d


def _deck_r_sweep(dev: str) -> str:
    """R(V) over -5..+5 V -- the phase-C regression sweep, verbatim."""
    d = header(f"{dev} R(V) sweep -5..+5 V, L={R_L_UM}u W={R_W_UM}u",
               instruments="Vp -- ideal DC source (swept)")
    d += "Vp p 0 dc 1\n"
    d += f"X1 p 0 {dev} L={R_L_UM}u W={R_W_UM}u\n"
    # DC-sweep rows are `index sweepvar vec...`; print ONLY the dependent
    # vector, never the sweep variable.
    d += _ctl("dc Vp -5 5 0.25\n"
              "let iload = -i(Vp)\n"
              "echo TBL_BEGIN\n"
              "print iload\n"
              "echo TBL_END\n")
    return d


# --------------------------------------------------------------------------
# deck builders -- capacitors
# --------------------------------------------------------------------------

def _deck_c_cv(dev: str, temp: float | None = None,
               corner: str = "TT") -> str:
    """One isolated AC testbench per DC bias, all in one invocation.

    Each instance hangs off its own source and shares only ground, so the AC
    probes do not superpose into each other's branch currents.
    """
    ttl = (f"{dev} C(V) by AC probe at {CAP_FREQ:g} Hz, L={C_L_UM}u "
           f"W={C_W_UM}u, corner {corner}"
           + (f", T={temp} degC" if temp is not None else ""))
    d = header(ttl,
               instruments="Vb<k> -- ideal DC bias + 1 V AC probe, one per bias",
               case=CORNER_CASE[corner], temp=temp)
    for k, v in enumerate(C_BIASES):
        d += f"Vb{k} p{k} 0 dc {_fnum(v)} ac 1\n"
        d += f"X{k} p{k} 0 {dev} L={C_L_UM}u W={C_W_UM}u\n"
    body = f"ac lin 1 {CAP_FREQ:g} {CAP_FREQ:g}\n"
    for k in range(len(C_BIASES)):
        body += f"print imag(i(Vb{k}))\n"
    return d + _ctl(body)


# --------------------------------------------------------------------------
# deck builder -- one Monte Carlo deck for all nine devices
# --------------------------------------------------------------------------

def _deck_mc(_i: int) -> str:
    """All nine matched pairs in ONE deck, at W=L=10u (W*L = 100 um^2).

    Each .subckt instance evaluates its own `.param RMM/CMM` AGAUSS draw, so
    18 independent draws happen per invocation. Bundling them costs nothing in
    accuracy (the instances share only ground) and turns 9 x 200 = 1800
    ngspice invocations into 200.

    Both families are read from a single AC analysis at 1 MHz with every
    source at DC 0 and AC 1 V:
        resistors   R = -1/real(i(V))   (at V=0 the VCR term contributes
                                         VCR1*1e-3, i.e. <10 ppm)
        capacitors  C = |imag(i(V))|/(2*pi*f)
    """
    d = header(f"Monte Carlo matched pairs, all 9 passives, "
               f"W=L={MC_W_UM}u (W*L={MC_AREA_UM2:g} um^2), MM_ON=1 PROC_ON=0",
               instruments="Vr*/Vc* -- ideal 1 V AC probes at DC 0",
               proc=0, mm=1)
    for dev in RESISTORS:
        for s in ("a", "b"):
            d += (f"V{dev}{s} n{dev}{s} 0 dc 0 ac 1\n"
                  f"X{dev}{s} n{dev}{s} 0 {dev} "
                  f"L={MC_L_UM}u W={MC_W_UM}u\n")
    for dev in CAPACITORS:
        for s in ("a", "b"):
            d += (f"V{dev}{s} n{dev}{s} 0 dc 0 ac 1\n"
                  f"X{dev}{s} n{dev}{s} 0 {dev} "
                  f"L={MC_L_UM}u W={MC_W_UM}u\n")
    body = f"ac lin 1 {CAP_FREQ:g} {CAP_FREQ:g}\n"
    for dev in RESISTORS:
        body += f"print real(i(V{dev}a)) real(i(V{dev}b))\n"
    for dev in CAPACITORS:
        body += f"print imag(i(V{dev}a)) imag(i(V{dev}b))\n"
    return d + _ctl(body)


def _mc_extract(out: str) -> dict[str, float]:
    p = parse_prints(out)
    vals: dict[str, float] = {}
    for dev in RESISTORS:
        for s in ("a", "b"):
            g = p.get(f"real(i(v{dev.lower()}{s}))")
            if g is None or g == 0:
                return {}
            vals[f"{dev}_{s}"] = -1.0 / g
    for dev in CAPACITORS:
        for s in ("a", "b"):
            im = p.get(f"imag(i(v{dev.lower()}{s}))")
            if im is None:
                return {}
            # IN fF, NOT F. char_lib.mc_run's non-degeneracy check compares
            # round(v, 15), i.e. quantizes to 1e-15 ABSOLUTE. A 10x10 um cap
            # is ~1e-13 F, so every sample would round to the same value and
            # a perfectly healthy MC run would be flagged degenerate. Working
            # in fF puts the values at ~100 with ppm-level detail intact.
            # Only relative spread is used downstream, so units cancel.
            vals[f"{dev}_{s}"] = cap_from_ac(im, CAP_FREQ) / 1e-15
    return vals


# --------------------------------------------------------------------------
# resistor driver
# --------------------------------------------------------------------------

def _run_resistor(col: Collector, dev: str, anchors: dict) -> None:
    c = RES[dev]
    narrow_um = c["narrow"] * 1e6
    short_um = c["short"] * 1e6
    l_eff = R_L_UM - 2.0 * short_um
    w_eff = R_W_UM - 2.0 * narrow_um
    geom = dict(L_um=R_L_UM, W_um=R_W_UM, M=1)

    # ---------------- R at low bias -> rsh
    nm = f"{dev}_rsh"
    dp = deck_path(nm, SUBDIR)
    cond = dict(geom, bias_V=R_LOW_BIAS, temp_C=27, corner="TT",
                PROC_ON=0, MM_ON=0,
                model_narrow_um=narrow_um, model_short_um=short_um,
                L_eff_um=l_eff, W_eff_um=w_eff,
                edge_debias_correction="R_geo = rsh*(L-2*short)/(W-2*narrow)",
                card_rsh_ohm_per_sq=c["card_rsh"])
    r_low: float | None = None
    try:
        out, _ = run_deck(_deck_r_op(dev, R_LOW_BIAS), nm, SUBDIR)
        _check(out, nm)
        i_vp = _need(parse_prints(out), "i(vp)", nm)
        if i_vp == 0:
            raise RuntimeError("zero current at the low-bias operating point")
        r_low = R_LOW_BIAS / (-i_vp)
        # back out the VCR term so rsh is not contaminated by the bias
        # coefficient: R(V) = R_geo*(1 + VCR1*|V| + VCR2*V^2)
        vcr_infl = (c["card_vcr1"] * R_LOW_BIAS
                    + c["card_vcr2"] * R_LOW_BIAS ** 2)
        rsh_unc = r_low * R_W_UM / R_L_UM
        rsh = r_low * w_eff / l_eff
        col.measured(dev, "rsh", rsh, "Ohm/sq",
                     conditions=dict(cond, R_measured_ohm=r_low,
                                     rsh_uncorrected_ohm_per_sq=rsh_unc,
                                     vcr_influence_at_bias=vcr_infl),
                     deck=dp,
                     note=("EDGE DE-BIAS CORRECTED. The ngspice R model shrinks "
                           "BOTH edges of both dimensions, so the physical "
                           "geometry is L-2*short by W-2*narrow. Reported rsh = "
                           "R*(W-2*narrow)/(L-2*short); the naive R*W/L is in "
                           "conditions as rsh_uncorrected_ohm_per_sq and runs "
                           f"{(rsh_unc/rsh - 1)*100:+.2f}% off. Measured at "
                           f"{R_LOW_BIAS} V, where the wrapper's VCR terms add "
                           f"{vcr_infl*1e6:.0f} ppm -- below the resolution of "
                           "the anchor band, so no VCR de-embedding is applied."))
    except Exception as e:                                    # noqa: BLE001
        col.measured(dev, "rsh", None, "Ohm/sq", conditions=cond, deck=dp,
                     error=str(e))

    # ---------------- tc1  (THE F7 HEADLINE)
    nm_t = f"{dev}_temp"
    cond_t = dict(geom, bias_V=R_LOW_BIAS, corner="TT", PROC_ON=0, MM_ON=0,
                  temps_C=TEMPS,
                  method="char_lib.tempco_ppm: (R150 - R_m40)/190/R27",
                  card_tc1=c["card_tc1"], card_tc2=c["card_tc2"])
    tdecks: dict[str, str] = {}
    try:
        rt: dict[float, float] = {}
        for t in TEMPS:
            tag = "m40" if t < 0 else f"{int(t)}"
            n2 = f"{nm_t}_{tag}"
            tdecks[tag] = deck_path(n2, SUBDIR)
            out, _ = run_deck(_deck_r_op(dev, R_LOW_BIAS, temp=t), n2, SUBDIR)
            _check(out, n2)
            iv = _need(parse_prints(out), "i(vp)", n2)
            if iv == 0:
                raise RuntimeError(f"zero current at T={t}")
            rt[t] = R_LOW_BIAS / (-iv)
        tc = tempco_ppm(rt[-40.0], rt[27.0], rt[150.0])
        note = ("linear tempco over the full -40..150 degC automotive span, "
                "not a local derivative -- the model also carries a tc2 term "
                "so a local slope would understate the endpoint error. ")
        if dev == "RPOLY_HI":
            note += F7_NOTE
        else:
            note += ("this card's tc1 sign is physically defensible: "
                     "heavily-doped poly and diffusion resistors trend "
                     "metallic (positive dR/dT).")
        col.measured(dev, "tc1", tc, "ppm/degC",
                     conditions=dict(cond_t,
                                     R_m40_ohm=rt[-40.0], R_27_ohm=rt[27.0],
                                     R_150_ohm=rt[150.0],
                                     R_150_over_R_27=rt[150.0] / rt[27.0],
                                     R_m40_over_R_27=rt[-40.0] / rt[27.0],
                                     decks=dict(tdecks)),
                     deck=tdecks.get("150"), note=note)
    except Exception as e:                                    # noqa: BLE001
        col.measured(dev, "tc1", None, "ppm/degC", conditions=cond_t,
                     deck=tdecks.get("150"), error=str(e))

    # ---------------- vcr1 (+ vcr2 in conditions) and golden_crosscheck
    nm_s = f"{dev}_rv"
    dp_s = deck_path(nm_s, SUBDIR)
    cond_v = dict(geom, sweep="dc Vp -5 5 0.25", temp_C=27, corner="TT",
                  PROC_ON=0, MM_ON=0,
                  model_form="R(V) = R0*(1 + VCR1*|V| + VCR2*V^2)",
                  fit="least squares of R(V) on [1, |V|, V^2]; "
                      "VCR1 = b/a, VCR2 = c/a",
                  card_vcr1_ppm_per_V=c["card_vcr1"] * 1e6,
                  card_vcr2_ppm_per_V2=c["card_vcr2"] * 1e6)
    r_at_golden: float | None = None
    try:
        out, _ = run_deck(_deck_r_sweep(dev), nm_s, SUBDIR)
        _check(out, nm_s)
        vs, cols = parse_dc_sweep(out, 1)
        if len(vs) < 20:
            raise RuntimeError(f"R(V) sweep returned {len(vs)} rows")
        vv, rr = [], []
        for v, i in zip(vs, cols[0]):
            if abs(v) < 1e-9 or abs(i) < 1e-30:
                continue
            vv.append(v)
            rr.append(v / i)
        if len(vv) < 10:
            raise RuntimeError("R(V) sweep produced too few usable points")
        a, b, cc = _polyfit_basis(vv, rr,
                                  [lambda x: 1.0, lambda x: abs(x),
                                   lambda x: x * x])
        if a == 0:
            raise RuntimeError("zero-bias intercept fitted to zero")
        vcr1 = b / a * 1e6
        vcr2 = cc / a * 1e6
        # residual of the 3-term fit, as a sanity check on the model form
        resid = max(abs(r - (a + b * abs(v) + cc * v * v)) / a
                    for v, r in zip(vv, rr))
        for v, r in zip(vv, rr):
            if abs(v - R_GOLDEN_V) < 1e-9:
                r_at_golden = r
        col.measured(dev, "vcr1", vcr1, "ppm/V",
                     conditions=dict(cond_v, fitted_R0_ohm=a,
                                     fitted_vcr2_ppm_per_V2=vcr2,
                                     n_fit_points=len(vv),
                                     max_fit_residual_relative=resid,
                                     R_at_plus5V_ohm=rr[-1],
                                     R_at_0V_fitted_ohm=a),
                     deck=dp_s,
                     note=("both terms of the wrapper's R(V) law are fitted "
                           "simultaneously over the full -5..+5 V sweep; "
                           "reporting VCR1 from a |V|-only fit would absorb "
                           "part of the quadratic term. The fitted VCR2 is in "
                           "conditions. V=0 is excluded (R = V/I is 0/0 "
                           "there); the zero-bias resistance is the fit "
                           "intercept. A max residual below ~1e-6 confirms the "
                           "two-term model form is exactly what the wrapper "
                           "implements."))
    except Exception as e:                                    # noqa: BLE001
        col.measured(dev, "vcr1", None, "ppm/V", conditions=cond_v,
                     deck=dp_s, error=str(e))

    _emit_crosscheck(col, dev, r_at_golden, R_GOLDEN_V, dp_s,
                     dict(geom, bias_V=R_GOLDEN_V, temp_C=27, corner="TT",
                          quantity="R(V) [Ohm]",
                          harness_method="dc Vp -5 5 0.25, R = V/(-i(Vp))"),
                     "Same method and geometry as the golden, so this should "
                     "be ~0% and any drift is a real model change.")

    # ---------------- rsh_corner_spread
    cond_c = dict(geom, bias_V=R_LOW_BIAS, temp_C=27,
                  corners=list(CORNER_CASE), PROC_ON=0, MM_ON=0,
                  metric="max over corners of 100*|R_corner - R_TT|/R_TT")
    cdecks: dict[str, str] = {}
    try:
        rc: dict[str, float] = {}
        for corner in CORNER_CASE:
            n2 = f"{dev}_corner_{corner}"
            cdecks[corner] = deck_path(n2, SUBDIR)
            out, _ = run_deck(_deck_r_op(dev, R_LOW_BIAS, corner=corner),
                              n2, SUBDIR)
            _check(out, n2)
            iv = _need(parse_prints(out), "i(vp)", n2)
            if iv == 0:
                raise RuntimeError(f"zero current at corner {corner}")
            rc[corner] = R_LOW_BIAS / (-iv)
        if "TT" not in rc:
            raise RuntimeError("TT corner missing")
        tt = rc["TT"]
        spread = max(abs(v - tt) for v in rc.values()) / tt * 100.0
        worst = max(rc, key=lambda k: abs(rc[k] - tt))
        col.derived(dev, "rsh_corner_spread", spread, "percent",
                    conditions=dict(cond_c, R_ohm=dict(rc),
                                    worst_corner=worst, decks=dict(cdecks)),
                    deck=cdecks.get("TT"),
                    note=("R is measured at each corner and normalized to TT. "
                          "Because the geometry is fixed, the R spread IS the "
                          "rsh spread. FS and SF leave the passive rsh "
                          "expressions untouched on every card, so the spread "
                          "is set entirely by FF/SS."))
    except Exception as e:                                    # noqa: BLE001
        col.derived(dev, "rsh_corner_spread", None, "percent",
                    conditions=cond_c, deck=cdecks.get("TT"), error=str(e))


# --------------------------------------------------------------------------
# capacitor driver
# --------------------------------------------------------------------------

def _run_capacitor(col: Collector, dev: str, anchors: dict) -> None:
    c = CAP[dev]
    area_um2 = C_L_UM * C_W_UM
    geom = dict(L_um=C_L_UM, W_um=C_W_UM, M=1, area_um2=area_um2)
    ac_cond = dict(geom, freq_Hz=CAP_FREQ, vac_V=1.0, temp_C=27, corner="TT",
                   PROC_ON=0, MM_ON=0,
                   method="AC probe: C = |imag(i(V))|/(2*pi*f), i.e. the "
                          "small-signal dQ/dV at the DC bias")

    # ---------------- C(V) ladder -> density, vcc1, crosscheck
    nm = f"{dev}_cv"
    dp = deck_path(nm, SUBDIR)
    c0: float | None = None
    try:
        out, _ = run_deck(_deck_c_cv(dev), nm, SUBDIR)
        _check(out, nm)
        p = parse_prints(out)
        cv: list[float] = []
        for k in range(len(C_BIASES)):
            cv.append(cap_from_ac(_need(p, f"imag(i(vb{k}))", nm), CAP_FREQ))
        c0 = cv[0]
    except Exception as e:                                    # noqa: BLE001
        cv = []
        col.measured(dev, "density", None, "fF/um^2", conditions=ac_cond,
                     deck=dp, error=str(e))
        col.derived(dev, "implied_dielectric_thickness", None, "nm",
                    conditions=ac_cond, deck=dp, error=str(e))
        col.measured(dev, "vcc1", None, "ppm/V", conditions=ac_cond, deck=dp,
                     error=str(e))

    if cv:
        # density
        dens = c0 / 1e-15 / area_um2
        col.measured(dev, "density", dens, "fF/um^2",
                     conditions=dict(ac_cond, bias_V=0.0, C_measured_F=c0,
                                     card_cj_F_per_m2=c["card_cj"]),
                     deck=dp,
                     note=("zero-bias small-signal capacitance divided by "
                           "L*W. The wrapper's cj is in F/m^2, and "
                           "1 F/m^2 = 1e3 fF/um^2, so a card cj of "
                           f"{c['card_cj']:g} predicts "
                           f"{c['card_cj']*1e3:g} fF/um^2."
                           + (" CFRINGE additionally carries a non-zero cjsw "
                              "perimeter term, so the measured density sits "
                              "slightly above cj*1e3."
                              if dev == "CFRINGE" else "")))
        # implied dielectric thickness
        eps_r = c["eps_r"]
        c_per_m2 = dens * 1e-3          # 1 fF/um^2 == 1e-3 F/m^2
        t_nm = eps_r * EPS0 / c_per_m2 * 1e9
        col.derived(dev, "implied_dielectric_thickness", t_nm, "nm",
                    conditions=dict(ac_cond, bias_V=0.0,
                                    eps_r=eps_r, dielectric=c["dielectric"],
                                    density_fF_per_um2=dens,
                                    C_per_area_F_per_m2=c_per_m2,
                                    eps0_F_per_m=EPS0,
                                    model_card_thick_m="see <DEV>_INT `thick`"),
                    deck=dp,
                    note=(f"parallel-plate inversion t = eps_r*eps0/(C/A) with "
                          f"eps_r={eps_r:g} ({c['dielectric']}). Numerically: "
                          f"t = {eps_r:g} * {EPS0:.6g} F/m / "
                          f"{c_per_m2:.6g} F/m^2 = {t_nm:.2f} nm. This is a "
                          "buildability check, not a process readout: it asks "
                          "whether the declared density corresponds to a "
                          "dielectric a fab could actually deposit and hold "
                          "off voltage across."))
        # vcc1 / vcc2
        try:
            a, b, cc = _polyfit_basis(C_BIASES, cv,
                                      [lambda x: 1.0, lambda x: abs(x),
                                       lambda x: x * x])
            if a == 0:
                raise RuntimeError("zero-bias intercept fitted to zero")
            vcc1 = b / a * 1e6
            vcc2 = cc / a * 1e6
            resid = max(abs(y - (a + b * abs(x) + cc * x * x)) / a
                        for x, y in zip(C_BIASES, cv))
            col.measured(dev, "vcc1", vcc1, "ppm/V",
                         conditions=dict(ac_cond, biases_V=list(C_BIASES),
                                         C_F=list(cv),
                                         fitted_C0_F=a,
                                         fitted_vcc2_ppm_per_V2=vcc2,
                                         max_fit_residual_relative=resid,
                                         card_vcc1_ppm_per_V=c["card_vcc1"]*1e6,
                                         card_vcc2_ppm_per_V2=c["card_vcc2"]*1e6,
                                         model_form="C(V) = C0*(1 + VCC1*|V| "
                                                    "+ VCC2*V^2)"),
                         deck=dp,
                         note=("METHOD CHOICE: AC probe at eight DC biases, "
                               "0..5 V, fitted on [1, |V|, V^2]; VCC1 = b/a. "
                               "The alternative -- the phase-C PWL-ramp-in-tran "
                               "method -- reads the bias term 10x LOW in this "
                               "ngspice build (its C(5)/C(0)-1 is 6.5e-5 where "
                               "the AC probe gives 6.494e-4, which is exactly "
                               "the wrapper's VCC1*5 + VCC2*25). The ramp "
                               "under-integrates the behavioral `Cextra` "
                               "branch, so only the AC probe recovers the "
                               "coefficient the wrapper declares. Zero-bias "
                               "capacitance is unaffected and agrees between "
                               "the two methods -- see golden_crosscheck."))
        except Exception as e:                                # noqa: BLE001
            col.measured(dev, "vcc1", None, "ppm/V", conditions=ac_cond,
                         deck=dp, error=str(e))

    _emit_crosscheck(col, dev, c0, C_GOLDEN_V, dp,
                     dict(geom, bias_V=C_GOLDEN_V, temp_C=27, corner="TT",
                          quantity="C(V) [F]",
                          harness_method="AC probe, 1 MHz, small-signal dQ/dV",
                          golden_method="PWL ramp 0->5 V over 1 ms in .tran, "
                                        "C = -i(Vp)/5000 V/s"),
                     "NOTE the two methods differ. At V=0 they must agree (and "
                     "do, to ~1e-6 %), which is what makes this a valid tie to "
                     "the golden; their bias-dependence does NOT agree -- see "
                     "the vcc1 note.")

    # ---------------- tcc_tc1
    cond_t = dict(geom, bias_V=0.0, freq_Hz=CAP_FREQ, corner="TT",
                  PROC_ON=0, MM_ON=0, temps_C=TEMPS,
                  method="char_lib.tempco_ppm: (C150 - C_m40)/190/C27",
                  card_tc1=c["card_tc1"], card_tc2=c["card_tc2"])
    tdecks: dict[str, str] = {}
    try:
        ct: dict[float, float] = {}
        for t in TEMPS:
            tag = "m40" if t < 0 else f"{int(t)}"
            n2 = f"{dev}_temp_{tag}"
            tdecks[tag] = deck_path(n2, SUBDIR)
            out, _ = run_deck(_deck_c_cv(dev, temp=t), n2, SUBDIR)
            _check(out, n2)
            ct[t] = cap_from_ac(_need(parse_prints(out), "imag(i(vb0))", n2),
                                CAP_FREQ)
        tcc = tempco_ppm(ct[-40.0], ct[27.0], ct[150.0])
        col.measured(dev, "tcc_tc1", tcc, "ppm/degC",
                     conditions=dict(cond_t, C_m40_F=ct[-40.0],
                                     C_27_F=ct[27.0], C_150_F=ct[150.0],
                                     C_150_over_C_27=ct[150.0] / ct[27.0],
                                     C_m40_over_C_27=ct[-40.0] / ct[27.0],
                                     decks=dict(tdecks)),
                     deck=tdecks.get("150"),
                     note=("zero-bias capacitance at each temperature. The "
                           "audit's phase-1 hypothesis that TCC is absent from "
                           "the capacitor cards is INCORRECT -- all four "
                           f"<DEV>_INT cards set tc1 (here {c['card_tc1']:g}) "
                           "and tc2 against tnom=27, and the measurement "
                           "recovers them. Expect this FoM in band."))
    except Exception as e:                                    # noqa: BLE001
        col.measured(dev, "tcc_tc1", None, "ppm/degC", conditions=cond_t,
                     deck=tdecks.get("150"), error=str(e))


# --------------------------------------------------------------------------
# Monte Carlo -- one run, all nine devices
# --------------------------------------------------------------------------

def _mc_conditions(dev: str, coeff: float) -> dict:
    per_dev_sigma = coeff / 3.0 / math.sqrt(MC_AREA_UM2)
    return dict(
        L_um=MC_L_UM, W_um=MC_W_UM, M=1, area_um2=MC_AREA_UM2,
        sqrt_area_um=math.sqrt(MC_AREA_UM2),
        N=MC_N, temp_C=27, corner="TT", PROC_ON=0, MM_ON=1,
        wrapper_3sigma_coeff=coeff,
        wrapper_implied_per_device_1sigma_fraction=per_dev_sigma,
        wrapper_implied_per_device_1sigma_percent=per_dev_sigma * 100.0,
        wrapper_implied_pair_1sigma_percent=(per_dev_sigma * math.sqrt(2.0)
                                             * 100.0),
        wrapper_implied_A_pair_percent_um=(per_dev_sigma * math.sqrt(2.0)
                                           * 100.0 * math.sqrt(MC_AREA_UM2)),
        pair_definition="stdev((X1-X2)/mean(X1,X2)) over N samples",
        freq_Hz=CAP_FREQ,
    )


def _run_mc(col: Collector, anchors: dict) -> None:
    fom = {d: ("matching_A_R_pair_1sigma" if d in RESISTORS
               else "matching_A_C_pair_1sigma") for d in DEVICES}
    coeffs = {d: (RES[d]["mm3s"] if d in RESISTORS else CAP[d]["mm3s"])
              for d in DEVICES}
    conds = {d: _mc_conditions(d, coeffs[d]) for d in DEVICES}

    def _fail(msg: str, deck: str | None = None, extra: dict | None = None):
        for d in DEVICES:
            col.measured(d, fom[d], None, "%.um",
                         conditions=dict(conds[d], **(extra or {})),
                         deck=deck, sigma="1-sigma", error=msg)

    try:
        res = mc_run(_deck_mc, "passives_mc", MC_N, _mc_extract,
                     subdir=f"{SUBDIR}_mc")
    except Exception as e:                                    # noqa: BLE001
        _fail(f"Monte Carlo driver failed: {e}")
        return

    extra = dict(n_samples_returned=res.n, seed_note=res.seed_note,
                 mc_deck_note="all nine matched pairs live in ONE deck; each "
                              ".subckt instance evaluates its own AGAUSS draw, "
                              "so the 18 draws per invocation are independent")
    if res.n < 3:
        _fail(f"only {res.n}/{MC_N} MC samples parsed", res.deck, extra)
        return
    if res.degenerate:
        # inventory 6.5 #22: `.param AGAUSS` is parsed before .control, so a
        # reset/op loop inside ONE invocation reuses a single draw. mc_run
        # spawns a process per sample specifically to avoid this; if it still
        # trips, the numbers are meaningless and must not be reported.
        _fail("MC DEGENERATE: all samples identical -- AGAUSS did not "
              "re-randomize across -b invocations (inventory 6.5 #22). "
              "Matching numbers suppressed rather than reported as zero.",
              res.deck, extra)
        return

    for d in DEVICES:
        cond = dict(conds[d], **extra)
        try:
            xa = res.series(f"{d}_a")
            xb = res.series(f"{d}_b")
            if len(xa) != len(xb) or len(xa) < 3:
                raise RuntimeError(f"only {min(len(xa), len(xb))} usable "
                                   f"samples for {d}")
            rel = [(a - b) / ((a + b) / 2.0) for a, b in zip(xa, xb)]
            sigma_pair_pct = statistics.stdev(rel) * 100.0
            a_pair = sigma_pair_pct * math.sqrt(MC_AREA_UM2)
            per_dev_pct = sigma_pair_pct / math.sqrt(2.0)
            mean_x = statistics.fmean(xa + xb)
            anc = anchors.get(d, {}).get(fom[d], {})
            tgt = anc.get("target")
            ratio = (tgt / a_pair) if (tgt and a_pair) else None
            col.measured(d, fom[d], a_pair, "%.um",
                         conditions=dict(
                             cond,
                             measured_pair_1sigma_percent=sigma_pair_pct,
                             measured_per_device_1sigma_percent=per_dev_pct,
                             mean_value=mean_x,
                             units_of_mean=("Ohm" if d in RESISTORS else "fF"),
                             anchor_target_percent_um=tgt,
                             anchor_over_measured_ratio=ratio,
                             quantity=("stdev((R1-R2)/mean(R)) * sqrt(W*L)"
                                       if d in RESISTORS else
                                       "stdev((C1-C2)/mean(C)) * sqrt(W*L)")),
                         deck=res.deck, sigma="1-sigma",
                         note=("A = sigma_pair[%] * sqrt(W*L um^2); at "
                               f"W=L={MC_W_UM:g}u the sqrt(W*L) factor is "
                               f"exactly {math.sqrt(MC_AREA_UM2):g} um, so A "
                               "is 10x the measured pair sigma in percent. "
                               + MATCH_NOTE_TAIL
                               + " The measured pair sigma should land on "
                                 "wrapper_implied_pair_1sigma_percent = "
                                 "sqrt(2)*coeff/3/sqrt(W*L); agreement "
                                 "confirms the AGAUSS 3-sigma reading of the "
                                 "wrapper is correct and that the optimism "
                                 "found in audit 5.2 is in the coefficient "
                                 "itself, not in a convention mix-up."))
        except Exception as e:                                # noqa: BLE001
            col.measured(d, fom[d], None, "%.um", conditions=cond,
                         deck=res.deck, sigma="1-sigma", error=str(e))


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def run(col: Collector) -> None:
    try:
        anchors = load_anchors()
    except Exception:                                         # noqa: BLE001
        anchors = {}
    for dev in DEVICES:
        try:
            if dev in RESISTORS:
                _run_resistor(col, dev, anchors)
            else:
                _run_capacitor(col, dev, anchors)
        except Exception as e:                                # noqa: BLE001
            col.measured(dev, "_module", None, "n/a",
                         error=f"passives device driver aborted: {e}")
    try:
        _run_mc(col, anchors)
    except Exception as e:                                    # noqa: BLE001
        for dev in DEVICES:
            col.measured(dev, "_module_mc", None, "n/a",
                         error=f"passives Monte Carlo aborted: {e}")
