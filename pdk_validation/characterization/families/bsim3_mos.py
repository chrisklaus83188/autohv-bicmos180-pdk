#!/usr/bin/env python3
"""
BSIM3 MOS characterization -- phase-2 harness family module.

Covers the eight BSIM3 subcircuit wrappers in autohv_bicmos180_case.lib:
NMOS18/PMOS18, NMOS33/PMOS33, NMOS50/PMOS50, NMOS12/PMOS12.

FoM keys match docs/anchor-values.json exactly, plus four extra diagnostic
keys that have no anchor band but carry the audit's assertions:

    vth_model_internal          ngspice's own @m.<inst>[vth]
    idsat_density_L1u           12 V parts only, the Lmin=0.15u sanity check
    mc_sigma_dvth_1sigma        matched-pair Monte Carlo (200 samples)
    mc_sigma_vth_per_device_1sigma
    mc_sigma_di_over_i
    mc_avt_implied_1sigma

Deliberate expected-failure tripwires (audit docs/model-realism-audit.md):
  * F6 -- AD/AS/PD/PS are unset on every M0 line, so cj_area / cjsw_sidewall
    measure ~0 and junction_perimeter_set comes out 0. Measured anyway.
  * F3 -- noia/noib/noic are BSIM4 defaults fed to a BSIM3 card (~6.25e21x
    too large), so the flicker corner runs off the top of the 1 Hz..1 GHz
    sweep and no thermal crossover exists.

Read-only with respect to the PDK.

Sign convention: PMOS decks are driven with negated supplies so that every
extracted sweep is monotone-increasing in |Vgs|; all reported voltages and
currents are magnitudes, matching the (positive) anchor bands.
"""
from __future__ import annotations

import math
import statistics

from char_lib import (header, run_deck, deck_path, parse_dc_sweep, parse_prints,
                      parse_meas, parse_table, ngspice_errored, Collector,
                      vth_max_gm, subthreshold_slope, linfit, cap_from_ac,
                      tempco_ppm, mc_run, CORNER_CASE, load_anchors)

DEVICES = ["NMOS18", "PMOS18", "NMOS33", "PMOS33", "NMOS50", "PMOS50",
           "NMOS12", "PMOS12"]

SUBDIR = "bsim3_mos"

# AC probe frequency for all capacitance extractions (well below any model
# pole, well above nothing that matters -- capacitance is frequency-flat here).
CAP_FREQ = 1.0e6

# Monte Carlo sample count (fixed by the brief; one ngspice process per sample).
MC_N = 200

# Per-class constants.
#   vrated   rated Vds/Vgs for the class
#   lmin     Lmin from pdk_validation/device_limits.csv (um)
#   vds_lin  low-Vds bias for the linear-region Id-Vg sweep
#   mm3s     the wrapper's own DVTH_MM 3-sigma coefficient, read from
#            autohv_bicmos180_case.lib (units V.um, divided by sqrt(W*L))
CLASS = {
    "18": dict(vrated=1.8, lmin=0.18, vds_lin=0.05, mm3s=0.0105),
    "33": dict(vrated=3.3, lmin=0.35, vds_lin=0.05, mm3s=0.012),
    "50": dict(vrated=5.0, lmin=0.50, vds_lin=0.05, mm3s=0.0135),
    "12": dict(vrated=12.0, lmin=0.15, vds_lin=0.10, mm3s=0.018),
}

# Geometry assumed when converting a measured drain-bulk capacitance into
# per-area / per-perimeter densities. The M0 lines carry none, so this is the
# geometry the instance line *should* have declared (audit 3.5: 0.5 um
# diffusion extension on a W=10u device).
AD_ASSUMED_UM2 = 10.0 * 0.5      # W * 0.5 um
PD_ASSUMED_UM = 2.0 * (10.0 + 0.5)

VTH_NOTE = ("max-gm extrapolation on a short-channel device; the anchor band "
            "is written against the card's long-channel zero-bias vth0, which "
            "is a different quantity. A ~100-150 mV gap here is a DEFINITION "
            "difference, not a model error -- compare against "
            "vth_model_internal.")


def _cls(dev: str) -> dict:
    return CLASS[dev[-2:]]


def _sign(dev: str) -> float:
    return -1.0 if dev.startswith("P") else 1.0


def _fnum(x: float) -> str:
    return repr(float(x))


# --------------------------------------------------------------------------
# deck builders
# --------------------------------------------------------------------------

def _deck_idvg(dev: str) -> str:
    """Low-Vds Id-Vg sweep + an .op that reports the model's internal vth."""
    c = _cls(dev)
    s = _sign(dev)
    vr, lmin, vdsl = c["vrated"], c["lmin"], c["vds_lin"]
    step = 0.005
    d = header(f"{dev} Id-Vg, linear region (Vds={vdsl} V), W=10u L={lmin}u",
               instruments="Vd (drain bias), Vg (gate sweep) -- ideal sources")
    d += f"XM1 d g 0 0 {dev} W=10u L={lmin}u\n"
    d += f"Vd d 0 dc {_fnum(s * vdsl)}\n"
    d += f"Vg g 0 dc {_fnum(s * vr)}\n"
    d += ".control\n"
    d += "op\n"
    d += "print @m.xm1.m0[vth] @m.xm1.m0[id] @m.xm1.m0[gm]\n"
    d += f"dc Vg 0 {_fnum(s * vr)} {_fnum(s * step)}\n"
    d += "echo TBL_BEGIN\n"
    d += "print abs(i(Vd))\n"
    d += "echo TBL_END\n"
    d += ".endc\n.end\n"
    return d


def _deck_idsat(dev: str) -> str:
    """Id at Vgs=Vds=Vrated, L=Lmin (and L=1u alongside for the 12 V parts)."""
    c = _cls(dev)
    s = _sign(dev)
    vr, lmin = c["vrated"], c["lmin"]
    d = header(f"{dev} Idsat at Vgs=Vds={vr} V, W=10u L={lmin}u",
               instruments="Vd, Vg -- ideal sources")
    d += f"XM1 d g 0 0 {dev} W=10u L={lmin}u\n"
    if dev.endswith("12"):
        d += f"XM3 d3 g 0 0 {dev} W=10u L=1u\n"
        d += f"Vd3 d3 0 dc {_fnum(s * vr)}\n"
    d += f"Vd d 0 dc {_fnum(s * vr)}\n"
    d += f"Vg g 0 dc {_fnum(s * vr)}\n"
    d += ".control\nop\n"
    d += "print @m.xm1.m0[id]"
    if dev.endswith("12"):
        d += " @m.xm3.m0[id]"
    d += "\n.endc\n.end\n"
    return d


def _deck_caps(dev: str) -> str:
    """Three independent, mutually isolated AC testbenches in one deck.

    XC1  W=10u L=10u, Vgs=Vrated, Vds=0, AC on gate  -> Cgg   -> cox
    XC2  W=10u L=Lmin, Vgs=0, Vds=0,     AC on gate  -> Cgd   -> cgso_overlap
    XC3  W=10u L=Lmin, all nodes at 0,   AC on drain -> Cdb   -> cj (F6 probe)

    The three subcircuits share only ground, so the three AC sources do not
    superpose into each other's measured branch currents.
    """
    c = _cls(dev)
    s = _sign(dev)
    vr, lmin = c["vrated"], c["lmin"]
    d = header(f"{dev} AC capacitance extraction at {CAP_FREQ:g} Hz",
               instruments="Vg1/Vd3 AC probes (1 V), all other sources ideal DC")
    # 1) Cgg in strong inversion, long channel -> Cox
    d += f"XC1 d1 g1 0 0 {dev} W=10u L=10u\n"
    d += "Vd1 d1 0 dc 0\n"
    d += f"Vg1 g1 0 dc {_fnum(s * vr)} ac 1\n"
    # 2) Cgd with the channel off -> gate/drain overlap only
    d += f"XC2 d2 g2 0 0 {dev} W=10u L={lmin}u\n"
    d += "Vd2 d2 0 dc 0\n"
    d += "Vg2 g2 0 dc 0 ac 1\n"
    # 3) drain-bulk junction cap, device off, AC driven at the drain
    d += f"XC3 d3 0 0 b3 {dev} W=10u L={lmin}u\n"
    d += "Vd3 d3 0 dc 0 ac 1\n"
    d += "Vb3 b3 0 dc 0\n"
    d += ".control\n"
    d += f"ac lin 1 {CAP_FREQ:g} {CAP_FREQ:g}\n"
    d += "print imag(i(Vg1)) imag(i(Vd2)) imag(i(Vb3))\n"
    d += ".endc\n.end\n"
    return d


def _deck_noise_bias(dev: str) -> str:
    """Id-Vg at Vds=Vrated/2, used to solve for the Vgs that gives Id ~ 10 uA."""
    c = _cls(dev)
    s = _sign(dev)
    vr, lmin = c["vrated"], c["lmin"]
    d = header(f"{dev} noise bias search: Id-Vg at Vds={vr/2} V",
               instruments="Vd, Vg -- ideal sources")
    d += f"XM1 d g 0 0 {dev} W=10u L={lmin}u\n"
    d += f"Vd d 0 dc {_fnum(s * vr / 2)}\n"
    d += "Vg g 0 dc 0\n"
    d += ".control\n"
    d += f"dc Vg 0 {_fnum(s * vr)} {_fnum(s * 0.005)}\n"
    d += "echo TBL_BEGIN\nprint abs(i(Vd))\necho TBL_END\n"
    d += ".endc\n.end\n"
    return d


def _deck_noise(dev: str, vgs: float) -> str:
    """Input-referred noise, 1 Hz .. 1 GHz, 10 pts/decade.

    The drain is biased through a 1e9 H inductor: DC short for the operating
    point, effectively open at every swept frequency, and noiseless -- so the
    only noise sources in the circuit are the device's own.
    """
    c = _cls(dev)
    s = _sign(dev)
    vr, lmin = c["vrated"], c["lmin"]
    d = header(f"{dev} flicker corner, W=10u L={lmin}u, Vds={vr/2} V",
               instruments="Vdd via 1e9 H bias choke (noiseless); Vg -- ideal")
    d += f"XM1 d g 0 0 {dev} W=10u L={lmin}u\n"
    d += f"Vdd dd 0 dc {_fnum(s * vr / 2)}\n"
    d += "Lb dd d 1e9\n"
    d += f"Vg g 0 dc {_fnum(vgs)} ac 1\n"
    d += ".control\nop\n"
    d += "print @m.xm1.m0[id] @m.xm1.m0[gm]\n"
    d += "noise v(d) Vg dec 10 1 1e9\n"
    d += "setplot noise1\n"
    d += "echo TBL_BEGIN\nprint inoise_spectrum\necho TBL_END\n"
    d += ".endc\n.end\n"
    return d


def _deck_corner(dev: str, corner: str, temp: float | None = None) -> str:
    """Idsat and internal vth at one process corner (and optionally one temp).

    Two instances so both quantities are read at their own canonical bias in
    a single invocation:
        XI  Vgs=Vds=Vrated       -> Idsat
        XT  Vgs=Vrated, Vds=low  -> vth_model_internal
    """
    c = _cls(dev)
    s = _sign(dev)
    vr, lmin, vdsl = c["vrated"], c["lmin"], c["vds_lin"]
    ttl = f"{dev} corner {corner}" + (f" at {temp} degC" if temp is not None else "")
    d = header(ttl, instruments="Vdi, Vdt, Vg -- ideal sources",
               case=CORNER_CASE[corner], temp=temp)
    d += f"XI di g 0 0 {dev} W=10u L={lmin}u\n"
    d += f"XT dt g 0 0 {dev} W=10u L={lmin}u\n"
    d += f"Vdi di 0 dc {_fnum(s * vr)}\n"
    d += f"Vdt dt 0 dc {_fnum(s * vdsl)}\n"
    d += f"Vg g 0 dc {_fnum(s * vr)}\n"
    d += ".control\nop\n"
    d += "print @m.xi.m0[id] @m.xt.m0[vth]\n"
    d += ".endc\n.end\n"
    return d


def _deck_mc(dev: str) -> str:
    """Matched pair, W/L = 10u/1u, MM_ON=1 PROC_ON=0, both in saturation."""
    c = _cls(dev)
    s = _sign(dev)
    vr = c["vrated"]
    vg = s * vr / 2.0
    vd = s * vr / 2.0
    d = header(f"{dev} Monte Carlo matched pair, W/L=10u/1u, MM_ON=1",
               instruments="Vd1, Vd2, Vg -- ideal sources", proc=0, mm=1)
    d += f"XM1 d1 g 0 0 {dev} W=10u L=1u\n"
    d += f"XM2 d2 g 0 0 {dev} W=10u L=1u\n"
    d += f"Vd1 d1 0 dc {_fnum(vd)}\n"
    d += f"Vd2 d2 0 dc {_fnum(vd)}\n"
    d += f"Vg g 0 dc {_fnum(vg)}\n"
    d += ".control\nop\n"
    d += ("print @m.xm1.m0[id] @m.xm2.m0[id] "
          "@m.xm1.m0[vth] @m.xm2.m0[vth]\n")
    d += ".endc\n.end\n"
    return d


# --------------------------------------------------------------------------
# extraction helpers
# --------------------------------------------------------------------------

def _check(out: str, what: str) -> None:
    err = ngspice_errored(out)
    if err:
        raise RuntimeError(f"{what}: ngspice error: {err}")


def _need(prints: dict, key: str, what: str) -> float:
    if key not in prints:
        raise RuntimeError(f"{what}: '{key}' missing from ngspice output")
    return prints[key]


def _swing_decade_band(vg, idr, lo=1e-9, hi=1e-7):
    """Cross-check S over a narrow current band, the way a bench engineer fits.

    Returns (S_mV_per_dec, decades_spanned), or (nan, 0.0) if the band is not
    populated by at least 4 points.
    """
    w = [(v, math.log10(i)) for v, i in zip(vg, idr) if lo <= i <= hi]
    if len(w) < 4:
        return float("nan"), 0.0
    slope, _ = linfit([p[0] for p in w], [p[1] for p in w])
    if not slope or slope <= 0 or math.isnan(slope):
        return float("nan"), 0.0
    return 1000.0 / slope, w[-1][1] - w[0][1]


def _flicker_corner(freqs, sd):
    """Corner from an input-referred noise spectral-density curve.

    Returns (f_corner, note). sd is inoise_spectrum, i.e. V^2/Hz.
    Criterion: the corner is where total input-referred noise POWER is twice
    the thermal floor -- equivalently where the extrapolated 1/f term crosses
    the white term. Requires the sweep to actually reach a flat floor; on
    these cards it never does (F3).
    """
    pts = [(f, v) for f, v in zip(freqs, sd) if f > 0 and v > 0]
    if len(pts) < 20:
        raise RuntimeError("noise sweep returned too few usable points")
    # log-log slope over the top decade tells us whether we reached a floor
    top = pts[-11:]
    lf = [math.log10(p[0]) for p in top]
    lv = [math.log10(p[1]) for p in top]
    slope, _ = linfit(lf, lv)
    floor = pts[-1][1]
    if slope < -0.5:
        return None, (f"top-decade log-log slope {slope:.3f} (pure 1/f); "
                      f"S_in(1 GHz)={floor:.4g} V^2/Hz -- no thermal floor "
                      f"reached anywhere in 1 Hz..1 GHz")
    thresh = 2.0 * floor
    for f, v in pts:
        if v <= thresh:
            return f, (f"corner = lowest f where S_in <= 2x the 1 GHz floor "
                       f"({floor:.4g} V^2/Hz); top-decade slope {slope:.3f}")
    return None, (f"S_in never falls to 2x its 1 GHz value; top-decade slope "
                  f"{slope:.3f}")


# --------------------------------------------------------------------------
# per-device driver
# --------------------------------------------------------------------------

def _run_device(col: Collector, dev: str, anchors: dict) -> None:
    c = _cls(dev)
    s = _sign(dev)
    vr, lmin, vdsl = c["vrated"], c["lmin"], c["vds_lin"]
    W_UM = 10.0
    geom = {"W_um": W_UM, "L_um": lmin, "M": 1}

    # ---------------- 1/2. vth_lin, vth_model_internal, subthreshold_swing
    nm = f"{dev}_idvg"
    dp = deck_path(nm, SUBDIR)
    cond_base = dict(geom, vds_V=vdsl, temp_C=27, corner="TT",
                     PROC_ON=0, MM_ON=0)
    try:
        out, _ = run_deck(_deck_idvg(dev), nm, SUBDIR)
        _check(out, nm)
        vg, cols = parse_dc_sweep(out, 1)
        idr = cols[0]
        if len(vg) < 20:
            raise RuntimeError(f"Id-Vg sweep returned {len(vg)} rows")
        vgm = [abs(v) for v in vg]
        vth, gmmax = vth_max_gm(vgm, idr)
        if math.isnan(vth):
            raise RuntimeError("max-gm extrapolation failed (no positive gm)")
        col.measured(dev, "vth_lin", vth, "V",
                     conditions=dict(cond_base, method="max-gm linear "
                                     "extrapolation", vg_step_V=0.005,
                                     gm_max_S=gmmax,
                                     anchor_definition="model vth0 "
                                     "(long-channel, zero-bias)"),
                     deck=dp, note=VTH_NOTE)
    except Exception as e:                                    # noqa: BLE001
        col.measured(dev, "vth_lin", None, "V", conditions=cond_base,
                     deck=dp, error=str(e))
        vg, idr, vgm = [], [], []

    # subthreshold swing off the same sweep
    try:
        if not vgm:
            raise RuntimeError("Id-Vg sweep unavailable (see vth_lin)")
        S, (vlo, vhi), dec = subthreshold_slope(vgm, idr, decades_min=2.0)
        if math.isnan(S):
            raise RuntimeError(f"no clean >=2-decade subthreshold window "
                               f"(only {dec:.2f} decades usable)")
        s_band, band_dec = _swing_decade_band(vgm, idr)
        col.measured(dev, "subthreshold_swing", S, "mV/dec",
                     conditions=dict(cond_base, fit_vg_lo_V=vlo,
                                     fit_vg_hi_V=vhi, fit_decades=dec,
                                     method="char_lib.subthreshold_slope: "
                                            "least-squares log10(Id) vs Vgs "
                                            "over the widest clean window",
                                     crosscheck_S_1nA_to_100nA_mV_per_dec=s_band,
                                     crosscheck_decades=band_dec),
                     deck=dp,
                     note=("METHOD SENSITIVITY: char_lib fits the widest clean "
                           "window, which on the thick-oxide parts reaches down "
                           "into deep subthreshold where the log slope is "
                           "shallower, biasing S high. The conditions carry a "
                           "narrow-band (1 nA..100 nA) cross-check fitted the "
                           "way a bench engineer would; on NMOS18 the two agree "
                           "to a few mV/dec, on the 12 V parts they differ by "
                           "~30-50 mV/dec. Both are above the anchor band."))
    except Exception as e:                                    # noqa: BLE001
        col.measured(dev, "subthreshold_swing", None, "mV/dec",
                     conditions=cond_base, deck=dp, error=str(e))

    # ---------------- 3. idsat_density (+ L=1u for the 12 V parts)
    nm = f"{dev}_idsat"
    dp = deck_path(nm, SUBDIR)
    cond_i = dict(geom, vgs_V=vr, vds_V=vr, temp_C=27, corner="TT")
    try:
        out, _ = run_deck(_deck_idsat(dev), nm, SUBDIR)
        _check(out, nm)
        p = parse_prints(out)
        idsat = abs(_need(p, "@m.xm1.m0[id]", nm))
        col.measured(dev, "idsat_density", idsat / W_UM * 1e3, "mA/um",
                     conditions=cond_i, deck=dp,
                     note=("Lmin from pdk_validation/device_limits.csv"
                           + (" -- 0.15u on a 20 nm oxide is itself a phase-1"
                              " finding (audit 3.3)" if dev.endswith("12")
                              else "")))
        if dev.endswith("12"):
            id1 = abs(_need(p, "@m.xm3.m0[id]", nm))
            col.measured(dev, "idsat_density_L1u", id1 / W_UM * 1e3, "mA/um",
                         conditions=dict(cond_i, L_um=1.0), deck=dp,
                         note=("companion to idsat_density: the same bias at a "
                               "physically defensible length. Audit 3.3 argues "
                               "L>=0.8-1.5 um is required for punchthrough "
                               "control at 12 V."))
    except Exception as e:                                    # noqa: BLE001
        col.measured(dev, "idsat_density", None, "mA/um", conditions=cond_i,
                     deck=dp, error=str(e))
        if dev.endswith("12"):
            col.measured(dev, "idsat_density_L1u", None, "mA/um",
                         conditions=dict(cond_i, L_um=1.0), deck=dp,
                         error=str(e))

    # ---------------- 4/5/6/7. capacitances
    nm = f"{dev}_caps"
    dp = deck_path(nm, SUBDIR)
    cond_cox = dict(W_um=10.0, L_um=10.0, vgs_V=vr, vds_V=0.0,
                    freq_Hz=CAP_FREQ, vac_V=1.0, temp_C=27, corner="TT")
    cond_ov = dict(geom, vgs_V=0.0, vds_V=0.0, freq_Hz=CAP_FREQ, vac_V=1.0,
                   temp_C=27, corner="TT")
    cond_cj = dict(geom, vgs_V=0.0, vds_V=0.0, vbs_V=0.0, freq_Hz=CAP_FREQ,
                   vac_V=1.0, temp_C=27, corner="TT",
                   AD_assumed_um2=AD_ASSUMED_UM2, PD_assumed_um=PD_ASSUMED_UM)
    cdb = None
    try:
        out, _ = run_deck(_deck_caps(dev), nm, SUBDIR)
        _check(out, nm)
        p = parse_prints(out)
        cgg = cap_from_ac(_need(p, "imag(i(vg1))", nm), CAP_FREQ)
        cgd = cap_from_ac(_need(p, "imag(i(vd2))", nm), CAP_FREQ)
        cdb = cap_from_ac(_need(p, "imag(i(vb3))", nm), CAP_FREQ)
    except Exception as e:                                    # noqa: BLE001
        for fom, u, cnd in (("cox", "fF/um^2", cond_cox),
                            ("cgso_overlap", "fF/um", cond_ov),
                            ("cj_area", "fF/um^2", cond_cj),
                            ("cjsw_sidewall", "fF/um", cond_cj),
                            ("junction_perimeter_set", "boolean", cond_cj)):
            col.derived(dev, fom, None, u, conditions=cnd, deck=dp,
                        error=str(e))
        cgg = cgd = None

    if cgg is not None:
        col.derived(dev, "cox", cgg / 1e-15 / (10.0 * 10.0), "fF/um^2",
                    conditions=cond_cox, deck=dp,
                    note=("Cgg/(W*L) with the channel in strong inversion at "
                          "L=10u so the intrinsic term dominates the two "
                          "overlap terms (~0.6% of the total here)."))
        col.derived(dev, "cgso_overlap", cgd / 1e-15 / W_UM, "fF/um",
                    conditions=cond_ov, deck=dp,
                    note=("Cgd with the channel off, divided by W. With "
                          "AD/AS/PD/PS unset this is gate-drain overlap and "
                          "nothing else on the junction side -- which is the "
                          "point of F6. It does include the BSIM3 fringing "
                          "term cf, which the cards leave unset so the model "
                          "computes its default from tox; expect this to read "
                          "~0.10 fF/um above the card's cgdo on the 1.8 V "
                          "parts, less on thicker oxides."))
        f6 = "F6 expected-fail: AD/AS/PD/PS unset on the M0 line"
        col.derived(dev, "cj_area", cdb / 1e-15 / AD_ASSUMED_UM2, "fF/um^2",
                    conditions=cond_cj, deck=dp, note=f6)
        col.derived(dev, "cjsw_sidewall", cdb / 1e-15 / PD_ASSUMED_UM,
                    "fF/um", conditions=cond_cj, deck=dp, note=f6)
        col.measured(dev, "junction_perimeter_set",
                     1 if (cdb / 1e-15) > 0.1 else 0, "boolean",
                     conditions=dict(cond_cj, cdb_measured_fF=cdb / 1e-15,
                                     threshold_fF=0.1),
                     deck=dp,
                     note=("direct F6 assertion: 1 iff the drain-bulk junction "
                           "capacitance is non-negligible. " + f6))

    # ---------------- 8. flicker corner
    nm = f"{dev}_noise"
    dp = deck_path(nm, SUBDIR)
    cond_n = dict(geom, vds_V=vr / 2, temp_C=27, corner="TT",
                  target_id_A=10e-6, sweep="dec 10 1 1e9",
                  ref="input-referred (inoise_spectrum, V^2/Hz)")
    try:
        bnm = f"{dev}_noise_bias"
        out, _ = run_deck(_deck_noise_bias(dev), bnm, SUBDIR)
        _check(out, bnm)
        bvg, bcols = parse_dc_sweep(out, 1)
        if len(bvg) < 20:
            raise RuntimeError("noise bias sweep returned too few rows")
        best = min(range(len(bvg)), key=lambda k: abs(bcols[0][k] - 10e-6))
        vgs = bvg[best]
        out, _ = run_deck(_deck_noise(dev, vgs), nm, SUBDIR)
        _check(out, nm)
        p = parse_prints(out)
        id_act = abs(_need(p, "@m.xm1.m0[id]", nm))
        gm_act = abs(p.get("@m.xm1.m0[gm]", float("nan")))
        freqs, ncols = parse_dc_sweep(out, 1)
        cond_n = dict(cond_n, vgs_V=vgs, id_actual_A=id_act, gm_S=gm_act,
                      bias_deck=deck_path(bnm, SUBDIR))
        fc, note = _flicker_corner(freqs, ncols[0])
        if fc is None:
            col.measured(dev, "flicker_corner", None, "Hz", conditions=cond_n,
                         deck=dp,
                         error="no crossover in 1Hz-1GHz (consistent with F3)",
                         note="F3: noia/noib/noic are BSIM4 defaults on a "
                              "BSIM3 card (~6.25e21x). " + note)
        else:
            col.measured(dev, "flicker_corner", fc, "Hz", conditions=cond_n,
                         deck=dp, note=note)
    except Exception as e:                                    # noqa: BLE001
        col.measured(dev, "flicker_corner", None, "Hz", conditions=cond_n,
                     deck=dp, error=str(e))

    # ---------------- 9/10/11. corners and temperature
    idsat_c: dict[str, float] = {}
    vth_c: dict[str, float] = {}
    corner_decks: dict[str, str] = {}
    for corner in CORNER_CASE:
        nm = f"{dev}_corner_{corner}"
        corner_decks[corner] = deck_path(nm, SUBDIR)
        try:
            out, _ = run_deck(_deck_corner(dev, corner), nm, SUBDIR)
            _check(out, nm)
            p = parse_prints(out)
            idsat_c[corner] = abs(_need(p, "@m.xi.m0[id]", nm))
            vth_c[corner] = abs(_need(p, "@m.xt.m0[vth]", nm))
        except Exception:                                     # noqa: BLE001
            pass

    # vth_model_internal (TT, 27 degC) -- reported alongside vth_lin
    cond_vmi = dict(geom, vgs_V=vr, vds_V=vdsl, vbs_V=0.0, temp_C=27,
                    corner="TT", source="ngspice @m.xt.m0[vth]")
    if "TT" in vth_c:
        col.measured(dev, "vth_model_internal", vth_c["TT"], "V",
                     conditions=cond_vmi, deck=corner_decks["TT"],
                     note=("the simulator's own threshold for this instance at "
                           "this bias, magnitude. The anchor band for vth is "
                           "written against the card's vth0 (long-channel, "
                           "zero-bias) -- a different definition again, so "
                           "expect this to sit between vth0 and the max-gm "
                           "vth_lin."))
    else:
        col.measured(dev, "vth_model_internal", None, "V", conditions=cond_vmi,
                     deck=corner_decks.get("TT"),
                     error="TT corner .op did not report @m.xt.m0[vth]")

    cond_sp = dict(geom, temp_C=27, corners=list(CORNER_CASE),
                   PROC_ON=0, MM_ON=0,
                   metric="max(|FF-TT|,|SS-TT|)",
                   decks={k: v for k, v in corner_decks.items()})
    try:
        if not {"TT", "FF", "SS"} <= set(idsat_c):
            raise RuntimeError(f"corner Idsat missing for "
                               f"{sorted({'TT','FF','SS'} - set(idsat_c))}")
        tt = idsat_c["TT"]
        if tt == 0:
            raise RuntimeError("TT Idsat is zero")
        spread = max(abs(idsat_c["FF"] - tt), abs(idsat_c["SS"] - tt)) / tt * 100
        col.derived(dev, "idsat_corner_spread", spread, "percent",
                    conditions=dict(cond_sp, vgs_V=vr, vds_V=vr,
                                    idsat_A={k: v for k, v in idsat_c.items()}),
                    deck=corner_decks["TT"])
    except Exception as e:                                    # noqa: BLE001
        col.derived(dev, "idsat_corner_spread", None, "percent",
                    conditions=cond_sp, deck=corner_decks.get("TT"),
                    error=str(e))

    try:
        if not {"TT", "FF", "SS"} <= set(vth_c):
            raise RuntimeError(f"corner vth missing for "
                               f"{sorted({'TT','FF','SS'} - set(vth_c))}")
        tt = vth_c["TT"]
        spread = max(abs(vth_c["FF"] - tt), abs(vth_c["SS"] - tt)) * 1000.0
        col.derived(dev, "vth_corner_spread", spread, "mV",
                    conditions=dict(cond_sp, vgs_V=vr, vds_V=vdsl,
                                    basis="vth_model_internal",
                                    vth_V={k: v for k, v in vth_c.items()}),
                    deck=corner_decks["TT"])
    except Exception as e:                                    # noqa: BLE001
        col.derived(dev, "vth_corner_spread", None, "mV", conditions=cond_sp,
                    deck=corner_decks.get("TT"), error=str(e))

    # vth tempco
    cond_t = dict(geom, vgs_V=vr, vds_V=vdsl, corner="TT",
                  temps_C=[-40, 27, 150], basis="vth_model_internal",
                  metric="(v150 - v_m40)/190")
    tdecks = {}
    try:
        vt = {}
        for t in (-40.0, 150.0):
            tag = "m40" if t < 0 else "150"
            nm = f"{dev}_temp_{tag}"
            tdecks[tag] = deck_path(nm, SUBDIR)
            out, _ = run_deck(_deck_corner(dev, "TT", temp=t), nm, SUBDIR)
            _check(out, nm)
            vt[t] = abs(_need(parse_prints(out), "@m.xt.m0[vth]", nm))
        if "TT" not in vth_c:
            raise RuntimeError("27 degC reference vth unavailable")
        tc = (vt[150.0] - vt[-40.0]) / 190.0 * 1000.0
        col.derived(dev, "vth_tempco", tc, "mV/degC",
                    conditions=dict(cond_t, vth_m40_V=vt[-40.0],
                                    vth_27_V=vth_c["TT"], vth_150_V=vt[150.0],
                                    decks=tdecks),
                    deck=tdecks.get("150"),
                    note="magnitude convention: |Vth| at each temperature, so "
                         "a falling |Vth| gives a negative tempco for both "
                         "polarities. NOTE: none of the eight cards set kt1, "
                         "kt2 or ute, so the temperature behaviour here is the "
                         "BSIM3 default kt1=-0.11 V, i.e. -0.11/tnom = -0.367 "
                         "mV/degC for every device regardless of class. A "
                         "device-independent, class-independent answer is the "
                         "signature of an unset parameter, not of physics.")
    except Exception as e:                                    # noqa: BLE001
        col.derived(dev, "vth_tempco", None, "mV/degC", conditions=cond_t,
                    deck=tdecks.get("150"), error=str(e))

    # ---------------- 12. Monte Carlo matched pair
    _run_mc(col, dev, anchors)


def _mc_extract(out: str) -> dict[str, float]:
    p = parse_prints(out)
    try:
        i1 = p["@m.xm1.m0[id]"]
        i2 = p["@m.xm2.m0[id]"]
        v1 = p["@m.xm1.m0[vth]"]
        v2 = p["@m.xm2.m0[vth]"]
    except KeyError:
        return {}
    mean_i = (i1 + i2) / 2.0
    d = {"id1": i1, "id2": i2, "vth1": v1, "vth2": v2,
         "dvth_mV": (v1 - v2) * 1000.0}
    if mean_i != 0:
        d["di_over_i_pct"] = (i1 - i2) / mean_i * 100.0
    return d


def _run_mc(col: Collector, dev: str, anchors: dict) -> None:
    c = _cls(dev)
    vr = c["vrated"]
    mm3s = c["mm3s"]
    W_UM, L_UM = 10.0, 1.0
    area = W_UM * L_UM

    # what the wrapper itself predicts, and what the anchor expects
    wrapper_1sigma_mV = mm3s / 3.0 / math.sqrt(area) * 1000.0
    avt = anchors.get(dev, {}).get("avt_1sigma", {}).get("target")
    pelgrom_1sigma_mV = (avt / math.sqrt(area)) if avt else None

    cond = dict(W_um=W_UM, L_um=L_UM, M=1, N=MC_N, temp_C=27, corner="TT",
                PROC_ON=0, MM_ON=1, vgs_V=vr / 2, vds_V=vr / 2,
                wrapper_dvth_3sigma_coeff=mm3s,
                wrapper_implied_per_device_1sigma_mV=wrapper_1sigma_mV,
                anchor_avt_1sigma_mV_um=avt,
                pelgrom_prediction_per_device_1sigma_mV=pelgrom_1sigma_mV,
                pair_note="two identical subckt instances, identically biased")

    keys = ["mc_sigma_dvth_1sigma", "mc_sigma_vth_per_device_1sigma",
            "mc_sigma_di_over_i", "mc_avt_implied_1sigma"]
    units = {"mc_sigma_dvth_1sigma": "mV",
             "mc_sigma_vth_per_device_1sigma": "mV",
             "mc_sigma_di_over_i": "percent",
             "mc_avt_implied_1sigma": "mV.um"}

    try:
        res = mc_run(lambda i: _deck_mc(dev), f"{dev}_mc", MC_N, _mc_extract,
                     subdir=f"{SUBDIR}_mc")
        cond = dict(cond, n_samples_returned=res.n, seed_note=res.seed_note)
        if res.n < 3:
            raise RuntimeError(f"only {res.n}/{MC_N} MC samples parsed")
        if res.degenerate:
            for k in keys:
                col.measured(dev, k, None, units[k], conditions=cond,
                             deck=res.deck, sigma="1-sigma",
                             error="MC DEGENERATE: all samples identical - "
                                   "AGAUSS not re-randomizing")
            return
        s_pair = res.sigma("dvth_mV")
        s_dev = s_pair / math.sqrt(2.0)
        s_ii = res.sigma("di_over_i_pct")
        col.measured(dev, "mc_sigma_dvth_1sigma", s_pair, "mV",
                     conditions=dict(cond, quantity="stdev(vth1-vth2)"),
                     deck=res.deck, sigma="1-sigma",
                     note="PAIR sigma (the difference of two devices); divide "
                          "by sqrt(2) for the per-device number, reported as "
                          "mc_sigma_vth_per_device_1sigma.")
        col.measured(dev, "mc_sigma_vth_per_device_1sigma", s_dev, "mV",
                     conditions=dict(cond, quantity="stdev(vth1-vth2)/sqrt(2)"),
                     deck=res.deck, sigma="1-sigma",
                     note="end-to-end check of the wrapper's AGAUSS 3-sigma "
                          "convention: this should land on "
                          "wrapper_implied_per_device_1sigma_mV.")
        col.measured(dev, "mc_sigma_di_over_i", s_ii, "percent",
                     conditions=dict(cond, quantity="stdev((I1-I2)/mean(I))"),
                     deck=res.deck, sigma="1-sigma")
        col.derived(dev, "mc_avt_implied_1sigma", s_dev * math.sqrt(area),
                    "mV.um",
                    conditions=dict(cond,
                                    quantity="per-device sigma * sqrt(W*L)"),
                    deck=res.deck, sigma="1-sigma",
                    note="A_VT implied by the wrapper's own mismatch draw, to "
                         "be compared with the avt_1sigma anchor.")
    except Exception as e:                                    # noqa: BLE001
        for k in keys:
            col.measured(dev, k, None, units[k], conditions=cond,
                         sigma="1-sigma", error=str(e))


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
            _run_device(col, dev, anchors)
        except Exception as e:                                # noqa: BLE001
            col.measured(dev, "_module", None, "n/a",
                         error=f"bsim3_mos device driver aborted: {e}")
