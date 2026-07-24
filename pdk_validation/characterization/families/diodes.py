#!/usr/bin/env python3
"""
Diode and zener characterization -- phase-2 harness family module.

Covers the six two-terminal junction wrappers in autohv_bicmos180_case.lib:
DIO_PN, DIO_FAST, DIO_SCH (signal/rectifier) and DZ_5V6, DZ_12, DZ_24
(zeners).  Ports are `a c` (anode, cathode), parameter AREA=1.  Zeners are
characterized in REVERSE breakdown, which is how they are used.

FoM keys match docs/anchor-values.json exactly:

    vf_at_1mA        signal diodes only
    n_ideality       signal diodes only
    bv               all six, reverse breakdown at a 1 uA criterion
    cjo_density      all six, AC at 1 MHz and zero bias
    tt_transit_time  all six, from the forward diffusion capacitance

plus two extra diagnostic keys with no anchor band:

    qrr_at_10mA      DIO_SCH only -- the stored charge a Schottky must not have
    bv_tempco        zeners only -- section 4.5 headline

Deliberate expected-failure tripwires (docs/model-realism-audit.md sec. 4):
  * 4.6 -- DIO_SCH carries tt=3e-10 s. A Schottky is a majority-carrier device:
    no injection, no stored charge, no reverse recovery. tt MUST be 0. The
    audit predicts 107 pF of spurious diffusion capacitance at 10 mA;
    tt_transit_time and qrr_at_10mA both measure it directly.
  * 4.5 -- no tbv1/tbv2/tcv exists on any zener card, so bv has no temperature
    coefficient at all. bv_tempco is an EXPECTED FAIL.
  * 4.4/4.3 -- cjo_density requires a declared physical area for AREA=1, which
    the PDK does not state. The reported density is conditional on the 1 um^2
    assumption; the absolute fF value is in conditions and is unconditional.

Read-only with respect to the PDK.
"""
from __future__ import annotations

import math

from char_lib import (header, run_deck, deck_path, parse_dc_sweep, parse_prints,
                      ngspice_errored, Collector, linfit, cap_from_ac,
                      load_anchors, T300, Q, K_B)

SIGNAL = ["DIO_PN", "DIO_FAST", "DIO_SCH"]
ZENERS = ["DZ_5V6", "DZ_12", "DZ_24"]
DEVICES = SIGNAL + ZENERS

SUBDIR = "diodes"

VT = K_B * T300 / Q
LN10 = math.log(10.0)

CAP_FREQ = 1.0e6            # AC probe frequency, both cjo and diffusion cap
TT_BIAS_A = 10e-3           # forward bias for the diffusion-capacitance probe
BV_CRIT_A = 1e-6            # primary reverse-breakdown criterion
BV_CRIT2_A = 1e-3           # secondary criterion, carried in conditions

# Forward sweep ballast. The anode is fed through this and the DEVICE node
# voltage is printed, so the ballast drop cancels out of vf_at_1mA while still
# keeping the solver away from the exponential wall.
FWD_BALLAST = 50.0
FWD_VMAX = 1.4

# Reverse sweep ballast, same construction.
REV_BALLAST = 1e3

# Reverse sweep ceiling per device. Generous headroom above the card's bv so
# both the 1 uA and the 1 mA crossings are inside the sweep.
REV_VMAX = {"DIO_PN": 130.0, "DIO_FAST": 110.0, "DIO_SCH": 70.0,
            "DZ_5V6": 12.0, "DZ_12": 22.0, "DZ_24": 38.0}

TEMPS_C = [-40.0, 27.0, 150.0]

AREA_NOTE = ("CONDITIONAL. The value is the density under the assumption that "
             "AREA=1 corresponds to 1 um^2. The PDK does not declare what "
             "physical area AREA=1 is -- there is no diode analogue of the MOS "
             "W_REF=10u convention, and device_limits.csv calls AREA a "
             "'relative area multiplier (unitless)'. Declaring the reference "
             "cell is an OPEN MAINTAINER DECISION (audit 4.3), so this density "
             "cannot be scored against the anchor band until it is made. The "
             "unconditional measurement is cjo_absolute_fF in conditions; "
             "rescale by the declared cell area once it exists.")


def _f(x: float) -> str:
    return repr(float(x))


def _check(out: str, what: str) -> None:
    err = ngspice_errored(out)
    if err:
        raise RuntimeError(f"{what}: ngspice error: {err}")


def _need(p: dict, key: str, what: str) -> float:
    if key not in p:
        raise RuntimeError(f"{what}: '{key}' missing from ngspice output")
    return p[key]


def _interp_x_at_y(xs, ys, ytarget, logy=True):
    """First crossing of ys through ytarget, interpolated in x."""
    for k in range(1, len(ys)):
        y0, y1 = ys[k - 1], ys[k]
        if y0 <= ytarget <= y1 and y1 > y0:
            if logy and y0 > 0:
                t = ((math.log(ytarget) - math.log(y0))
                     / (math.log(y1) - math.log(y0)))
            else:
                t = (ytarget - y0) / (y1 - y0)
            return xs[k - 1] + t * (xs[k] - xs[k - 1])
    return None


def _r2(x, y, slope, icept):
    ybar = sum(y) / len(y)
    ss_t = sum((v - ybar) ** 2 for v in y)
    ss_r = sum((v - (slope * u + icept)) ** 2 for u, v in zip(x, y))
    return 1.0 - ss_r / ss_t if ss_t > 0 else float("nan")


# --------------------------------------------------------------------------
# deck builders
# --------------------------------------------------------------------------

def _deck_fwd(dev: str) -> str:
    """Forward IV. Cathode grounded, anode fed through a ballast."""
    d = header(f"{dev} forward IV, AREA=1",
               instruments="Vs sweep through a 50 ohm ballast; v(a) is the "
                           "device terminal voltage so the ballast drop is "
                           "not counted")
    d += f"XD a 0 {dev} AREA=1\n"
    d += f"Rball s a {_f(FWD_BALLAST)}\n"
    d += "Vs s 0 dc 0\n"
    d += ".control\nset width=1000\n"
    d += f"dc Vs 0 {_f(FWD_VMAX)} 0.002\n"
    d += "echo TBL_BEGIN\nprint v(a) abs(i(Vs))\necho TBL_END\n"
    d += ".endc\n.end\n"
    return d


def _deck_rev(dev: str, temp: float | None = None) -> str:
    """Reverse IV. Anode grounded, cathode driven positive through a ballast."""
    ttl = f"{dev} reverse breakdown, AREA=1"
    if temp is not None:
        ttl += f", {temp} degC"
    d = header(ttl, instruments="Vs sweep through a 1 kohm ballast; v(k) is "
                                "the device terminal voltage",
               temp=temp)
    d += f"XD 0 k {dev} AREA=1\n"
    d += f"Rball s k {_f(REV_BALLAST)}\n"
    d += "Vs s 0 dc 0\n"
    vmax = REV_VMAX[dev]
    d += ".control\nset width=1000\n"
    d += f"dc Vs 0 {_f(vmax)} {_f(vmax / 2000.0)}\n"
    d += "echo TBL_BEGIN\nprint v(k) abs(i(Vs))\necho TBL_END\n"
    d += ".endc\n.end\n"
    return d


def _deck_cjo(dev: str) -> str:
    """Zero-bias junction capacitance, AC probe on the cathode."""
    d = header(f"{dev} zero-bias junction capacitance at {CAP_FREQ:g} Hz, AREA=1",
               instruments="Vk 1 V AC probe at 0 V DC")
    d += f"XD 0 k {dev} AREA=1\n"
    d += "Vk k 0 dc 0 ac 1\n"
    d += ".control\nset width=1000\n"
    d += f"ac lin 1 {CAP_FREQ:g} {CAP_FREQ:g}\n"
    d += "print imag(i(Vk))\n"
    d += ".endc\n.end\n"
    return d


def _deck_diffcap(dev: str) -> str:
    """Forward diffusion capacitance at 10 mA.

    The diode is biased AND probed by one ideal current source: DC 10 mA sets
    the operating point, the 1 A AC component makes v(a) numerically equal to
    the small-signal impedance Z. Extracting C from imag(Z) rather than from
    imag(Y) is what makes this immune to the model's series `rs`, which is
    purely real and therefore drops out of the imaginary part entirely.
    """
    d = header(f"{dev} forward diffusion capacitance at {TT_BIAS_A:g} A, "
               f"{CAP_FREQ:g} Hz, AREA=1",
               instruments="Ib ideal current source: DC bias plus a 1 A AC "
                           "probe, so v(a) reads out as the impedance directly")
    d += f"XD a 0 {dev} AREA=1\n"
    d += f"Ib 0 a dc {_f(TT_BIAS_A)} ac 1\n"
    d += ".control\nset width=1000\n"
    d += "op\nprint v(a)\n"
    d += f"ac lin 1 {CAP_FREQ:g} {CAP_FREQ:g}\n"
    d += "print real(v(a)) imag(v(a))\n"
    d += ".endc\n.end\n"
    return d


# --------------------------------------------------------------------------
# extraction
# --------------------------------------------------------------------------

def _cap_from_impedance(imag_z: float, g: float, w: float) -> float:
    """C from the imaginary part of the small-signal impedance.

    For a junction conductance g in parallel with C, then any purely real
    series rs:
        Z  = rs + 1/(g + jwC)
        Im(Z) = -wC / (g^2 + w^2 C^2)          <- rs has cancelled
    Solving the resulting quadratic for C and keeping the physical (small)
    root, written in the numerically stable form so the near-unity square root
    does not lose precision:
        C = 2*X*g^2 / (w * (1 + sqrt(1 - 4 X^2 g^2))),   X = -Im(Z)
    """
    X = -imag_z
    if X <= 0:
        raise RuntimeError(f"imag(Z) = {imag_z:.4g} is not capacitive")
    disc = 1.0 - 4.0 * X * X * g * g
    if disc < 0:
        raise RuntimeError(f"no real solution for C (discriminant {disc:.4g}); "
                           f"the assumed junction conductance {g:.4g} S is "
                           f"inconsistent with the measured impedance")
    return 2.0 * X * g * g / (w * (1.0 + math.sqrt(disc)))


def _fwd_and_n(col, dev, cond_base, emit=True):
    """Forward sweep -> (vf_at_1mA, n_ideality). Emits both when emit."""
    nm = f"{dev}_fwd"
    dp = deck_path(nm, SUBDIR)
    cond = dict(cond_base, ballast_ohm=FWD_BALLAST, vsweep_max_V=FWD_VMAX,
                vstep_V=0.002)
    vf = n = None
    try:
        out, _ = run_deck(_deck_fwd(dev), nm, SUBDIR)
        _check(out, nm)
        xs, cols = parse_dc_sweep(out, 2)
        if len(xs) < 50:
            raise RuntimeError(f"forward sweep returned {len(xs)} rows")
        vd, idd = cols
        vf = _interp_x_at_y(vd, idd, 1e-3)
        if vf is None:
            raise RuntimeError(f"I=1 mA not bracketed (max {max(idd):.3g} A)")
        if emit:
            col.measured(dev, "vf_at_1mA", vf, "V",
                         conditions=dict(cond, i_A=1e-3,
                                         method="log-linear interpolation of "
                                                "the device terminal voltage "
                                                "v(a) vs log(I)"),
                         deck=dp)
    except Exception as e:                                        # noqa: BLE001
        if emit:
            col.measured(dev, "vf_at_1mA", None, "V", conditions=cond, deck=dp,
                         error=str(e))
        return None, None, dp

    cond_n = dict(cond, fit_i_window_A=[1e-6, 1e-4], vt_V=VT, t_K=T300,
                  method="least squares log10(I) vs V over 1 uA..100 uA; "
                         "n = 1/(slope*Vt*ln10)")
    try:
        w = [(vd[k], math.log10(idd[k])) for k in range(len(vd))
             if 1e-6 <= idd[k] <= 1e-4]
        if len(w) < 6:
            raise RuntimeError(f"only {len(w)} points in the 1 uA..100 uA "
                               f"fit window")
        slope, icept = linfit([p[0] for p in w], [p[1] for p in w])
        if math.isnan(slope) or slope <= 0:
            raise RuntimeError("non-positive log10(I) vs V slope")
        n = 1.0 / (slope * VT * LN10)
        if emit:
            col.derived(dev, "n_ideality", n, "",
                        conditions=dict(cond_n, slope_dec_per_V=slope,
                                        fit_points=len(w),
                                        fit_r2=_r2([p[0] for p in w],
                                                   [p[1] for p in w],
                                                   slope, icept),
                                        is_extracted_A=10.0 ** icept),
                        deck=dp,
                        note="the 1 uA..100 uA window is chosen to sit above "
                             "any leakage floor and below the onset of series-"
                             "resistance droop, so this returns the card's `n` "
                             "rather than a resistance-corrupted slope.")
    except Exception as e:                                        # noqa: BLE001
        if emit:
            col.derived(dev, "n_ideality", None, "", conditions=cond_n,
                        deck=dp, error=str(e))
        n = None
    return vf, n, dp


def _reverse(dev: str, temp: float | None = None):
    """Reverse sweep -> (bv_at_1uA, bv_at_1mA, deck_path, imax)."""
    tag = "" if temp is None else f"_{_tempslug(temp)}"
    nm = f"{dev}_rev{tag}"
    dp = deck_path(nm, SUBDIR)
    out, _ = run_deck(_deck_rev(dev, temp), nm, SUBDIR)
    _check(out, nm)
    xs, cols = parse_dc_sweep(out, 2)
    if len(xs) < 50:
        raise RuntimeError(f"reverse sweep returned {len(xs)} rows")
    vd, idd = cols
    bv1 = _interp_x_at_y(vd, idd, BV_CRIT_A)
    bv2 = _interp_x_at_y(vd, idd, BV_CRIT2_A)
    if bv1 is None:
        raise RuntimeError(f"|I| never reached {BV_CRIT_A:g} A up to "
                           f"{REV_VMAX[dev]} V (max {max(idd):.3g} A)")
    return bv1, bv2, dp, max(idd)


def _tempslug(t: float) -> str:
    return ("m" if t < 0 else "") + f"{abs(t):g}C"


def _diffcap(col, dev, n, cond_base):
    """AC diffusion-capacitance extraction -> tt, plus qrr for DIO_SCH."""
    nm = f"{dev}_diffcap"
    dp = deck_path(nm, SUBDIR)
    w = 2.0 * math.pi * CAP_FREQ
    nn = n if (n and n > 0) else 1.0
    g = TT_BIAS_A / (nn * VT)
    cond = dict(cond_base, i_forward_A=TT_BIAS_A, freq_Hz=CAP_FREQ,
                n_used=nn, vt_V=VT,
                junction_conductance_S=g,
                method="AC small-signal. tt = C_d / g with C_d from imag(Z) "
                       "at 1 MHz and g = I/(n*Vt) using the MEASURED n. "
                       "Extraction is via imag(Z), not imag(Y), so the "
                       "model's series rs -- purely real -- cancels exactly "
                       "instead of biasing the answer low.")
    try:
        if not n:
            raise RuntimeError("needs a measured n_ideality to set the "
                               "junction conductance")
        out, _ = run_deck(_deck_diffcap(dev), nm, SUBDIR)
        _check(out, nm)
        p = parse_prints(out)
        vop = p.get("v(a)")
        imz = _need(p, "imag(v(a))", nm)
        rez = p.get("real(v(a))")
        cd = _cap_from_impedance(imz, g, w)
        tt = cd / g
        cond = dict(cond, vf_at_bias_V=vop, imag_z_ohm=imz, real_z_ohm=rez,
                    c_diffusion_F=cd, c_diffusion_pF=cd * 1e12)
        note = ("AC METHOD (stated per the brief): diffusion capacitance at "
                "10 mA forward, C_d = tt*I/(n*Vt), inverted for tt. No "
                "transient reverse-recovery integration was needed.")
        if dev == "DIO_SCH":
            note = ("EXPECTED FAIL. " + note + " A Schottky is a majority-"
                    "carrier device: no minority injection, no stored charge, "
                    "no reverse recovery -- that is the entire reason it gets "
                    "chosen as a rectifier or clamp, and tt MUST be 0. The "
                    "measured C_d is in conditions; audit 4.6 predicts ~107 pF "
                    "of spurious diffusion capacitance at this bias, growing "
                    "linearly with current, i.e. worst exactly where a "
                    "Schottky would be used. Everything else on this card "
                    "(is 6.18 decades above PN, vj=0.45, m=0.22, eg=0.69, "
                    "xti=2) is thermionic emission done correctly, which makes "
                    "the non-zero tt look like a copy-paste from the PN card.")
        col.measured(dev, "tt_transit_time", tt, "s", conditions=cond,
                     deck=dp, note=note)
        if dev == "DIO_SCH":
            # Qrr from the same small-signal charge: Q = tt * I is the stored
            # charge the junction is carrying at the operating point, which is
            # what a reverse-recovery integration would return.
            col.measured(dev, "qrr_at_10mA", tt * TT_BIAS_A, "C",
                         conditions=dict(cond,
                                         derivation="Qrr = tt * I_forward, "
                                                    "with tt from the AC "
                                                    "diffusion-capacitance "
                                                    "extraction above"),
                         deck=dp,
                         note="the stored charge a true Schottky cannot have. "
                              "Measured by the AC diffusion-capacitance route "
                              "rather than by integrating a switching "
                              "transient: the two are the same quantity "
                              "(Q = tt*I) and the AC route is not exposed to "
                              "timestep-control fragility. A true Schottky "
                              "must give 0 C.")
        return tt
    except Exception as e:                                        # noqa: BLE001
        col.measured(dev, "tt_transit_time", None, "s", conditions=cond,
                     deck=dp, error=str(e))
        if dev == "DIO_SCH":
            col.measured(dev, "qrr_at_10mA", None, "C", conditions=cond,
                         deck=dp, error=str(e))
        return None


def _cjo(col, dev, cond_base):
    nm = f"{dev}_cjo"
    dp = deck_path(nm, SUBDIR)
    cond = dict(cond_base, v_bias_V=0.0, freq_Hz=CAP_FREQ, vac_V=1.0,
                assumed_cell_um2=1.0,
                method="C = |imag(i(Vk))| / (2*pi*f*Vac) at zero DC bias, "
                       "where the SPICE junction expression reduces to cjo "
                       "exactly")
    try:
        out, _ = run_deck(_deck_cjo(dev), nm, SUBDIR)
        _check(out, nm)
        p = parse_prints(out)
        cj = cap_from_ac(_need(p, "imag(i(vk))", nm), CAP_FREQ)
        col.measured(dev, "cjo_density", cj / 1e-15, "fF/um^2",
                     conditions=dict(cond, cjo_absolute_fF=cj / 1e-15,
                                     cjo_absolute_pF=cj / 1e-12),
                     deck=dp, note=AREA_NOTE)
    except Exception as e:                                        # noqa: BLE001
        col.measured(dev, "cjo_density", None, "fF/um^2", conditions=cond,
                     deck=dp, error=str(e))


# --------------------------------------------------------------------------
# per-device drivers
# --------------------------------------------------------------------------

def _run_signal(col: Collector, dev: str) -> None:
    base = dict(AREA=1, temp_C=27, corner="TT", PROC_ON=0, MM_ON=0,
                reference_cell="AREA=1 is an UNDECLARED physical area "
                               "(audit 4.3)")
    _vf, n, _dp = _fwd_and_n(col, dev, base, emit=True)

    # ---- bv
    nm = f"{dev}_rev"
    dp = deck_path(nm, SUBDIR)
    cond_b = dict(base, criterion_A=BV_CRIT_A, ballast_ohm=REV_BALLAST,
                  sweep_max_V=REV_VMAX[dev],
                  method="reverse terminal voltage v(k) at |I| = 1 uA; the "
                         "cathode is fed through a ballast so the sweep can "
                         "run past the knee")
    try:
        bv1, bv2, dp, imax = _reverse(dev)
        col.measured(dev, "bv", bv1, "V",
                     conditions=dict(cond_b, bv_at_1mA_V=bv2,
                                     i_max_in_sweep_A=imax),
                     deck=dp,
                     note="the 1 mA value is in conditions. The gap between "
                          "the two is set by nbv: the SPICE breakdown branch "
                          "moves e-fold per nbv*Vt, so a soft knee (large nbv) "
                          "spreads them apart and a hard one collapses them. "
                          "The card's `bv` parameter is the voltage at `ibv`, "
                          "which is neither of these two criteria.")
    except Exception as e:                                        # noqa: BLE001
        col.measured(dev, "bv", None, "V", conditions=cond_b, deck=dp,
                     error=str(e))

    _cjo(col, dev, base)
    _diffcap(col, dev, n, base)


def _run_zener(col: Collector, dev: str) -> None:
    base = dict(AREA=1, temp_C=27, corner="TT", PROC_ON=0, MM_ON=0,
                usage="REVERSE breakdown -- how a zener is actually used",
                reference_cell="AREA=1 is an UNDECLARED physical area "
                               "(audit 4.3)")
    # forward sweep is run only to obtain n for the diffusion-cap extraction;
    # vf_at_1mA / n_ideality are not anchor keys for the zeners.
    _vf, n, _dp = _fwd_and_n(col, dev, base, emit=False)

    # ---- bv at three temperatures
    nm = f"{dev}_rev"
    dp = deck_path(nm, SUBDIR)
    cond_b = dict(base, criterion_A=BV_CRIT_A, ballast_ohm=REV_BALLAST,
                  sweep_max_V=REV_VMAX[dev])
    bv1 = {}
    bv2 = {}
    decks = {}
    errs = {}
    for t in TEMPS_C:
        try:
            a, b, d, _imax = _reverse(dev, t)
            bv1[t], bv2[t], decks[t] = a, b, d
        except Exception as e:                                    # noqa: BLE001
            errs[t] = str(e)

    if 27.0 in bv1:
        col.measured(dev, "bv", bv1[27.0], "V",
                     conditions=dict(cond_b, bv_at_1mA_V=bv2[27.0],
                                     method="reverse terminal voltage v(k) at "
                                            "|I| = 1 uA"),
                     deck=decks[27.0],
                     note="the 1 uA criterion sits below the card's `ibv`, so "
                          "this reads a little under the nameplate bv; the "
                          "1 mA value in conditions brackets it from above. "
                          "The distance between them is nbv*Vt*ln(I2/I1) and "
                          "is a direct read of how soft the modelled knee is.")
    else:
        col.measured(dev, "bv", None, "V", conditions=cond_b,
                     error=errs.get(27.0, "27 degC sweep failed"))

    cond_t = dict(base, temps_C=TEMPS_C, criterion_A=BV_CRIT_A,
                  metric="(bv(150 degC) - bv(-40 degC)) / 190",
                  bv_1uA_by_temp_V={f"{k:g}": v for k, v in bv1.items()},
                  bv_1mA_by_temp_V={f"{k:g}": v for k, v in bv2.items()},
                  decks={f"{k:g}": v for k, v in decks.items()})
    try:
        missing = [t for t in TEMPS_C if t not in bv1]
        if missing:
            raise RuntimeError(f"bv missing at {missing}: "
                               f"{[errs.get(t) for t in missing]}")
        tc = (bv1[150.0] - bv1[-40.0]) / 190.0 * 1000.0
        tc2 = ((bv2[150.0] - bv2[-40.0]) / 190.0 * 1000.0
               if all(t in bv2 and bv2[t] is not None for t in TEMPS_C)
               else None)
        col.measured(dev, "bv_tempco", tc, "mV/degC",
                     conditions=dict(cond_t, tempco_at_1mA_mV_per_degC=tc2),
                     deck=decks[150.0],
                     note="expected-fail: no tbv1/tbv2 on the zener cards; a "
                          "real zener moves +6..+25 mV/degC above 6 V. "
                          "The three bv values are in conditions so the "
                          "flatness is visible directly. IMPORTANT READING "
                          "NOTE: any residual non-zero number here is NOT a "
                          "modelled bv tempco. `bv` itself is a temperature-"
                          "invariant constant on these cards; what moves is "
                          "the offset between `bv` and the measurement "
                          "criterion, because the SPICE breakdown branch "
                          "carries nbv*Vt in its exponent and Vt is "
                          "proportional to T. That artifact has the WRONG SIGN "
                          "below ibv and flips sign above it -- compare "
                          "tempco_at_1mA_mV_per_degC in conditions with the "
                          "1 uA headline. A physical zener tempco cannot "
                          "change sign with the measurement current; this one "
                          "does, which is the proof there is no bv tempco in "
                          "the model at all. Audit 4.5: over -40..150 degC "
                          "DZ_24 should move +2.9 to +4.8 V, and it is flat -- "
                          "wrong in the unsafe direction, since a real clamp "
                          "passes more voltage hot than simulated. The model "
                          "also gives no way to tell the good near-zero-tempco "
                          "5.6 V reference part from the bad ones, since all "
                          "three are equally flat.")
    except Exception as e:                                        # noqa: BLE001
        col.measured(dev, "bv_tempco", None, "mV/degC", conditions=cond_t,
                     deck=decks.get(150.0), error=str(e))

    _cjo(col, dev, base)
    _diffcap(col, dev, n, dict(base, n_source="measured on the forward branch "
                                              "of the same zener"))


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def run(col: Collector) -> None:
    try:
        _anchors = load_anchors()
    except Exception:                                             # noqa: BLE001
        _anchors = {}
    for dev in SIGNAL:
        try:
            _run_signal(col, dev)
        except Exception as e:                                    # noqa: BLE001
            col.measured(dev, "_module", None, "n/a",
                         error=f"diodes device driver aborted: {e}")
    for dev in ZENERS:
        try:
            _run_zener(col, dev)
        except Exception as e:                                    # noqa: BLE001
            col.measured(dev, "_module", None, "n/a",
                         error=f"diodes device driver aborted: {e}")
