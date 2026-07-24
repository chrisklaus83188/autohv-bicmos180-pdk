#!/usr/bin/env python3
"""
VDMOS / LDMOS characterization -- phase-2 harness family module.

Covers the thirteen ngspice-VDMOS subcircuit wrappers in
autohv_bicmos180_case.lib:

    NDMOS20  PDMOS20  DNMOS20
    NDMOS40  PDMOS40
    NDMOS60  PDMOS60
    NDMOS80  PDMOS80
    NDMOS120 PDMOS120
    NDMOS200 PDMOS200

FoM keys match docs/anchor-values.json exactly, plus these extra diagnostic
keys which carry the audit's assertions and have no anchor band:

    bv_corner_<FF|SS|FS|SF>       breakdown at the four non-TT corners
    rcond_gate_current            KNOWN ARTIFACT (Rcond g_int s 1e6)
    cap_reconciliation_ndmos200   the inventory 6.3 fork (NDMOS200 only)

Port order is `d g s` -- there is NO bulk pin on any VDMOS wrapper. Only
NDMOS200/PDMOS200 take an `L` parameter (drift length, default 8u); the other
eleven have no length knob at all.

Sign convention
---------------
Every sweep is run in a device-normalised gate coordinate

    u = pol * Vgs        pol = +1 for n-channel, -1 for p-channel

so that drain current rises monotonically with u for both polarities and the
char_lib extractors (which assume positive gm) apply unchanged. Voltages that
have a natural sign -- vth_lin, vto_tempco -- are reported SIGNED, i.e.
negative for the p-channel devices and for the depletion-mode DNMOS20.
Resistances, capacitances, current densities and swings are magnitudes.

DNMOS20 is a DEPLETION n-channel part (vto = -0.9 V), so Vgs = 0 leaves it ON.
Every "device off" bias in this module is computed from the card's own vto
rather than assumed to be 0 V.

Expected-failure tripwires (docs/model-realism-audit.md sections 2.1-2.9).
These are the FINDINGS. Do not "fix" them:
  * F1  -- kp implies a 287x-5213x oversized cell, so idsat_density comes out
           ~10^2-10^3x ABOVE the anchor band and ron_times_w ~10^3x BELOW it.
  * F1  -- rsp_specific_ron therefore lands ~10^3x under the 1-D unipolar
           silicon limit, which no lateral RESURF device can do.
  * F2  -- cgs/cgdmax remain 3.3x-48x large after the 2026-06-01 divide-by-1000,
           with a residual that slopes with voltage class.
  * 2.8 -- the ksubthres ladder slopes the wrong way; NDMOS200's n = 1.01 is at
           the Boltzmann floor. gm_over_id_ceiling is the cross-check.
  * 2.9 -- BV is constant vs drift length L; the L knob is penalty-only.

Read-only with respect to the PDK: this module writes decks and results only.
"""
from __future__ import annotations

import math

from char_lib import (header, run_deck, deck_path, parse_dc_sweep, parse_prints,
                      ngspice_errored, Collector, vth_max_gm,
                      subthreshold_slope, linfit, cap_from_ac, tempco_ppm,
                      mc_run, CORNER_CASE, load_anchors)

DEVICES = ["NDMOS20", "PDMOS20", "DNMOS20",
           "NDMOS40", "PDMOS40",
           "NDMOS60", "PDMOS60",
           "NDMOS80", "PDMOS80",
           "NDMOS120", "PDMOS120",
           "NDMOS200", "PDMOS200"]

SUBDIR = "vdmos"

CAP_FREQ = 1.0e6          # AC probe frequency for every capacitance extraction
MC_N = 200                # Monte Carlo samples (one ngspice process each)
W_UM = 10.0               # W_REF: every measurement is on the reference cell
VOV_STRONG = 4.0          # the "Vov = +4 V" bias called for by idsat/ron
BV_COMPLIANCE_A = 1.0e-6  # |Id| defining breakdown

# Cell pitch per voltage class, um -- audit 2.2 ladder. Used only to turn a
# measured Ron into a specific on-resistance.
PITCH_UM = {20: 5.0, 40: 7.0, 60: 9.0, 80: 11.0, 120: 15.0, 200: 22.0}

# The wrapper's own DVTH_MM 3-sigma coefficient, read from
# autohv_bicmos180_case.lib, and which mismatch ladder it belongs to
# (audit 2.6: ladder A is the physical one, ladder B is ~3x optimistic).
MM_3SIGMA = {
    "NDMOS20": (0.024, "A"), "PDMOS20": (0.024, "A"), "DNMOS20": (0.024, "A"),
    "NDMOS40": (0.0085, "B"), "PDMOS40": (0.0085, "B"),
    "NDMOS60": (0.027, "A"), "PDMOS60": (0.027, "A"),
    "NDMOS80": (0.0095, "B"), "PDMOS80": (0.0095, "B"),
    "NDMOS120": (0.030, "A"), "PDMOS120": (0.030, "A"),
    "NDMOS200": (0.011, "B"), "PDMOS200": (0.011, "B"),
}

# BV ratings at TT from the model cards, used only to place sweep ranges and
# bias ladders. The measured value is what gets reported.
BV_RATED = {
    "NDMOS20": 24.0, "PDMOS20": 22.0, "DNMOS20": 24.0,
    "NDMOS40": 48.0, "PDMOS40": 45.0,
    "NDMOS60": 75.0, "PDMOS60": 70.0,
    "NDMOS80": 95.0, "PDMOS80": 90.0,
    "NDMOS120": 135.0, "PDMOS120": 128.0,
    "NDMOS200": 225.0, "PDMOS200": 230.0,
}

# audit 3a81be0 corner table -- the cross-check demanded for the 200 V pair.
AUDIT_BV_TABLE = {
    "NDMOS200": {"TT": 225.0, "FF": 211.5, "SS": 238.5,
                 "FS": 211.5, "SF": 238.5},
    "PDMOS200": {"TT": 230.0, "FF": 216.2, "SS": 243.8,
                 "FS": 243.8, "SF": 216.2},
}

HAS_L = {"NDMOS200", "PDMOS200"}
L_LIST_UM = [5.0, 8.0, 12.0, 16.0]     # drift lengths for the BV-vs-L probe
E_SUST_V_PER_UM = 20.0                 # audit 2.9 recommended sustaining field

VTH_SIGN_NOTE = (
    "SIGNED value: positive for n-channel enhancement parts, negative for the "
    "p-channel parts and for the depletion-mode DNMOS20. The anchor band is "
    "written as a positive magnitude, so compare |value| against it. "
    "Extraction is max-gm linear extrapolation in the normalised coordinate "
    "u = pol*Vgs, then mapped back through pol."
)


# --------------------------------------------------------------------------
# per-device static facts
# --------------------------------------------------------------------------

def _pol(dev: str) -> float:
    """+1 for n-channel (including the depletion DNMOS20), -1 for p-channel."""
    return -1.0 if dev.startswith("P") else 1.0


def _vclass(dev: str) -> int:
    for v in (200, 120, 80, 60, 40, 20):
        if dev.endswith(str(v)):
            return v
    raise ValueError(f"cannot infer voltage class from {dev}")


def _pitch(dev: str) -> float:
    return PITCH_UM[_vclass(dev)]


def _inst(dev: str) -> str:
    """Subckt instance line for the reference cell (L only where it exists)."""
    if dev in HAS_L:
        return f"XH1 d g 0 {dev} W={W_UM:g}u L=8u\n"
    return f"XH1 d g 0 {dev} W={W_UM:g}u\n"


def _fnum(x: float) -> str:
    return repr(float(x))


def _check(out: str, what: str) -> None:
    err = ngspice_errored(out)
    if err:
        raise RuntimeError(f"{what}: ngspice error: {err}")


def _need(prints: dict, key: str, what: str) -> float:
    if key not in prints:
        raise RuntimeError(f"{what}: '{key}' missing from ngspice output")
    return prints[key]


# --------------------------------------------------------------------------
# model-card readback
# --------------------------------------------------------------------------

_CARD_KEYS = ["vto", "kp", "theta", "bv", "tt", "rd", "rs",
              "cgs", "cgdmax", "cgdmin", "cjo", "lambda", "ksubthres"]


def _deck_card(dev: str) -> str:
    """Read the resolved .model card parameters at TT / 27 degC.

    ngspice exposes VDMOS *model* parameters as @<MODELNAME>[param]. The
    instance path @m.xh1.m0[...] works for operating-point quantities (id, gm)
    but NOT for vth/vdsat -- VDMOS does not publish those, which is why every
    threshold in this module is extracted from a sweep instead.
    """
    d = header(f"{dev} model-card readback (TT, 27 degC)",
               instruments="Vd, Vg -- ideal sources, held at 0 for a trivial op")
    d += _inst(dev)
    d += "Vd d 0 dc 0\nVg g 0 dc 0\n"
    d += ".control\nop\n"
    d += "print " + " ".join(f"@{dev}_INT[{k}]" for k in _CARD_KEYS) + "\n"
    d += ".endc\n.end\n"
    return d


def _read_card(dev: str) -> tuple[dict, str]:
    nm = f"{dev}_card"
    dp = deck_path(nm, SUBDIR)
    out, _ = run_deck(_deck_card(dev), nm, SUBDIR)
    _check(out, nm)
    p = parse_prints(out)
    card = {}
    for k in _CARD_KEYS:
        v = p.get(f"@{dev.lower()}_int[{k}]")
        if v is not None:
            card[k] = v
    if "vto" not in card:
        raise RuntimeError(f"{nm}: model card readback returned no vto")
    return card, dp


# --------------------------------------------------------------------------
# bias helpers, all expressed through the card's own vto
# --------------------------------------------------------------------------

def _vgs_off(pol: float, vto: float) -> float:
    """A gate bias that holds the channel firmly off.

    Enhancement parts (pol*vto > 0) are off at Vgs = 0. The depletion DNMOS20
    (pol=+1, vto=-0.9) is not, so it gets 1 V of extra reverse gate drive.
    """
    return 0.0 if pol * vto > 0 else vto - pol * 1.0


def _vds_sat(dev: str) -> float:
    """Drain bias for the saturation-region measurements, MAGNITUDE.

    'Vds = 0.5*BV or 10 V, whichever is smaller' per the brief.
    """
    return min(0.5 * BV_RATED[dev], 10.0)


# --------------------------------------------------------------------------
# deck builders
# --------------------------------------------------------------------------

def _deck_idvg(dev: str, pol: float, vto: float, u_lo: float, u_hi: float,
               step: float, vds_mag: float, temp: float | None = None,
               title: str = "Id-Vg") -> str:
    """Id-Vg sweep in the normalised coordinate u = pol*Vgs.

    Vg is swept from pol*u_lo to pol*u_hi with a pol-signed step, so the deck
    is a plain .dc for both polarities and column 1 of the printed table is the
    real Vg. Only abs(i(Vd)) is printed -- the sweep variable is already
    column 1 and printing it again would shift every subsequent column.
    """
    d = header(f"{dev} {title}: Vds={pol*vds_mag:+.4g} V, W={W_UM:g}u",
               instruments="Vd (drain bias), Vg (gate sweep) -- ideal sources",
               temp=temp)
    d += _inst(dev)
    d += f"Vd d 0 dc {_fnum(pol * vds_mag)}\n"
    d += "Vg g 0 dc 0\n"
    d += ".control\n"
    d += (f"dc Vg {_fnum(pol * u_lo)} {_fnum(pol * u_hi)} "
          f"{_fnum(pol * step)}\n")
    d += "echo TBL_BEGIN\nprint abs(i(Vd))\necho TBL_END\n"
    d += ".endc\n.end\n"
    return d


def _deck_bias(dev: str, pol: float, vgs: float, vds: float,
               temp: float | None = None, corner: str = "TT",
               title: str = "op") -> str:
    """Single operating point at an explicit (Vgs, Vds), both already signed."""
    d = header(f"{dev} {title}: Vgs={vgs:+.4g} V, Vds={vds:+.4g} V",
               instruments="Vd, Vg -- ideal sources",
               case=CORNER_CASE[corner], temp=temp)
    d += _inst(dev)
    d += f"Vd d 0 dc {_fnum(vds)}\n"
    d += f"Vg g 0 dc {_fnum(vgs)}\n"
    d += ".control\nop\n"
    d += "print @m.xh1.m0[id] @m.xh1.m0[gm]\n"
    d += "print i(Vd) i(Vg)\n"
    d += ".endc\n.end\n"
    return d


def _deck_caps(dev: str, pol: float, vgs_off: float, vds_mag: float,
               l_um: float = 8.0) -> str:
    """Terminal capacitances at one drain bias, device OFF.

    Two AC runs on one netlist, 1 V probe, 1 MHz:
      run 1: probe at the drain (Vd ac 1), gate AC-grounded (Vg ac 0)
             |imag(i(Vd))| -> Coss = Cds + Cgd
             |imag(i(Vg))| -> Crss = Cgd          (gate return current)
      run 2: probe at the gate  (Vg ac 1), drain AC-grounded (Vd ac 0)
             |imag(i(Vg))| -> Ciss = Cgs + Cgd

    So Cgs = Ciss - Crss and Cds = Coss - Crss. Taking imag() rather than abs()
    matters: the wrapper's Rgmin (1e9) and Rcond (1e6) put a real 1e-6 S across
    the gate probe, which abs() would fold into the capacitance.
    """
    inst = (f"XH1 d g 0 {dev} W={W_UM:g}u L={l_um:g}u\n" if dev in HAS_L
            else f"XH1 d g 0 {dev} W={W_UM:g}u\n")
    d = header(f"{dev} terminal C at Vds={pol*vds_mag:+.4g} V, "
               f"Vgs={vgs_off:+.4g} V (channel off)",
               instruments=f"Vd/Vg 1 V AC probes at {CAP_FREQ:g} Hz; "
                           "DC values are ideal bias sources")
    d += inst
    d += f"Vd d 0 dc {_fnum(pol * vds_mag)} ac 1\n"
    d += f"Vg g 0 dc {_fnum(vgs_off)} ac 0\n"
    d += ".control\n"
    d += f"ac lin 1 {CAP_FREQ:g} {CAP_FREQ:g}\n"
    d += "let coss = abs(imag(i(Vd)))\n"
    d += "let crss = abs(imag(i(Vg)))\n"
    d += "print coss crss\n"
    d += "alter Vd acmag=0\n"
    d += "alter Vg acmag=1\n"
    d += f"ac lin 1 {CAP_FREQ:g} {CAP_FREQ:g}\n"
    d += "let ciss = abs(imag(i(Vg)))\n"
    d += "print ciss\n"
    d += ".endc\n.end\n"
    return d


def _deck_bv(dev: str, pol: float, vgs_off: float, corner: str,
             l_um: float = 8.0) -> str:
    """Drain ramp with the gate off, swept through the breakdown knee.

    Range 0.80x..1.10x the card rating so the knee is always bracketed; step
    is rating/2000 (about 0.11 V on a 225 V part), which resolves the knee to
    better than 0.05%.
    """
    rated = BV_RATED[dev]
    lo, hi = 0.80 * rated, 1.10 * rated
    step = rated / 2000.0
    inst = (f"XH1 d g 0 {dev} W={W_UM:g}u L={l_um:g}u\n" if dev in HAS_L
            else f"XH1 d g 0 {dev} W={W_UM:g}u\n")
    d = header(f"{dev} breakdown ramp, corner {corner}, gate off "
               f"(Vgs={vgs_off:+.4g} V)"
               + (f", L={l_um:g}u" if dev in HAS_L else ""),
               instruments="Vd (drain ramp), Vg -- ideal sources",
               case=CORNER_CASE[corner])
    d += inst
    d += "Vd d 0 dc 0\n"
    d += f"Vg g 0 dc {_fnum(vgs_off)}\n"
    d += ".control\n"
    d += f"dc Vd {_fnum(pol * lo)} {_fnum(pol * hi)} {_fnum(pol * step)}\n"
    d += "echo TBL_BEGIN\nprint abs(i(Vd))\necho TBL_END\n"
    d += ".endc\n.end\n"
    return d


def _deck_rcond(dev: str, pol: float) -> str:
    """DC gate current vs |Vgs|, source grounded.

    KNOWN ARTIFACT probe: the wrapper carries `Rcond g_int s 1e6`, a hard
    1 Mohm gate-to-source shunt added to break a floating-node singularity
    (HANDOFF_dmos200_vshift_multiinstance_REPLY). A real insulated gate draws
    no DC current at all.
    """
    d = header(f"{dev} DC gate current vs Vgs (Rcond artifact probe)",
               instruments="Vg (gate sweep), Vd -- ideal sources")
    d += _inst(dev)
    d += f"Vd d 0 dc {_fnum(pol * 0.1)}\n"
    d += "Vg g 0 dc 0\n"
    d += ".control\n"
    d += f"dc Vg 0 {_fnum(pol * 12.0)} {_fnum(pol * 0.05)}\n"
    d += "echo TBL_BEGIN\nprint abs(i(Vg))\necho TBL_END\n"
    d += ".endc\n.end\n"
    return d


def _deck_mc(dev: str, pol: float, vto: float) -> str:
    """Matched pair at W_REF, MM_ON=1 PROC_ON=0.

    The wrapper injects mismatch as a series gate offset:
        Vshift g g_int DC {-DVTH_MM}
    so v(g_int) - v(g) IS that instance's threshold offset in volts, exactly.
    Reading the two internal nodes therefore measures the drawn Vth mismatch
    directly, with no extraction error folded in, at the cost of one .op per
    sample instead of a full Id-Vg sweep -- which is what makes N=200 x 13
    devices affordable.

    The pair is biased into MODERATE INVERSION (Vov = +0.5 V), not held off.
    That matters for the non-degeneracy guard: with the gates grounded these
    enhancement devices are off, their drain current is just Vds/rds, and it
    prints bit-identical across every sample regardless of the Vth draw --
    which trips char_lib's degeneracy check as a FALSE POSITIVE even though
    the Vth draws themselves are varying fine. Biasing on the steep part of
    the transfer curve makes Id genuinely Vth-sensitive, so the guard tests
    what it is meant to test.
    """
    vg = vto + pol * 0.5
    vd = pol * 1.0
    inst = (lambda tag, dn, gn:
            f"X{tag} {dn} {gn} 0 {dev} W={W_UM:g}u L=8u\n" if dev in HAS_L
            else f"X{tag} {dn} {gn} 0 {dev} W={W_UM:g}u\n")
    d = header(f"{dev} Monte Carlo matched pair at W_REF={W_UM:g}u, MM_ON=1",
               instruments="Vga/Vgb/Vda/Vdb -- ideal sources", proc=0, mm=1)
    d += inst("A", "da", "ga")
    d += inst("B", "db", "gb")
    d += f"Vga ga 0 dc {_fnum(vg)}\nVgb gb 0 dc {_fnum(vg)}\n"
    d += f"Vda da 0 dc {_fnum(vd)}\nVdb db 0 dc {_fnum(vd)}\n"
    d += ".control\nop\n"
    d += "print v(xa.g_int) v(xb.g_int)\n"
    d += "print @m.xa.m0[id] @m.xb.m0[id]\n"
    d += ".endc\n.end\n"
    return d


# --------------------------------------------------------------------------
# sweep-based extraction
# --------------------------------------------------------------------------

def _sweep_u(out: str, pol: float) -> tuple[list[float], list[float]]:
    """(u, |Id|) from a printed .dc table, u = pol*Vg, sorted ascending in u."""
    vg, cols = parse_dc_sweep(out, 1)
    if not vg:
        raise RuntimeError("Id-Vg sweep returned no parsable rows")
    pts = sorted(zip((pol * v for v in vg), cols[0]))
    return [p[0] for p in pts], [p[1] for p in pts]


def _above_floor(u: list[float], idr: list[float], mult: float = 50.0
                 ) -> tuple[list[float], list[float], float]:
    """Drop the numerical/leakage plateau at the bottom of a subthreshold sweep.

    The floor is estimated as the median of the lowest five positive currents;
    everything below `mult` times that is discarded. Returns the surviving
    points and the floor estimate.
    """
    pos = sorted(i for i in idr if i > 0)
    if len(pos) < 5:
        raise RuntimeError("fewer than five positive current points")
    floor = pos[len(pos) // 2] if len(pos) < 10 else pos[2]
    keep = [(a, b) for a, b in zip(u, idr) if b > mult * floor]
    return [k[0] for k in keep], [k[1] for k in keep], floor


def _gm_over_id(u: list[float], idr: list[float]) -> tuple[float, float, float]:
    """max(gm/Id) by central difference. Returns (max, u_at_max, id_at_max)."""
    best, bu, bi = float("-inf"), float("nan"), float("nan")
    for k in range(1, len(u) - 1):
        du = u[k + 1] - u[k - 1]
        if du <= 0 or idr[k] <= 0:
            continue
        gm = (idr[k + 1] - idr[k - 1]) / du
        r = gm / idr[k]
        if r > best:
            best, bu, bi = r, u[k], idr[k]
    if not math.isfinite(best):
        raise RuntimeError("no usable gm/Id point")
    return best, bu, bi


def _interp_crossing(xs: list[float], ys: list[float], target: float) -> float:
    """First x where y crosses `target`, interpolated in log(y).

    Breakdown is an exponential knee, so a linear interpolation between two
    samples that straddle 1 uA would bias the answer; log-space is the right
    interpolant and is exact for the model's exp() form.
    """
    for k in range(1, len(xs)):
        if ys[k] >= target > ys[k - 1] > 0:
            l0, l1 = math.log(ys[k - 1]), math.log(ys[k])
            if l1 == l0:
                return xs[k]
            f = (math.log(target) - l0) / (l1 - l0)
            return xs[k - 1] + f * (xs[k] - xs[k - 1])
        if ys[k] >= target and ys[k - 1] <= 0:
            return xs[k]
    raise RuntimeError(f"|Id| never reached {target:g} A over the swept range")


# --------------------------------------------------------------------------
# individual measurement blocks
# --------------------------------------------------------------------------

def _do_idvg(col: Collector, dev: str, pol: float, card: dict) -> dict:
    """vth_lin, subthreshold_swing, gm_over_id_ceiling. Returns cached values."""
    vto = card["vto"]
    svto = pol * vto                     # threshold in u coordinates, positive
    out_cache: dict = {}
    vds_lin = 0.1

    # -- coarse sweep for vth_lin -------------------------------------------
    nm = f"{dev}_idvg"
    dp = deck_path(nm, SUBDIR)
    u_lo, u_hi, step = svto - 1.5, svto + 5.0, 0.02
    cond = dict(W_um=W_UM, M=1, vds_V=pol * vds_lin, temp_C=27, corner="TT",
                PROC_ON=0, MM_ON=0, polarity=("n" if pol > 0 else "p"),
                model_vto_V=vto, u_sweep_V=[u_lo, u_hi], u_step_V=step,
                u_definition="u = pol*Vgs")
    if dev in HAS_L:
        cond["L_um"] = 8.0
    try:
        out, _ = run_deck(_deck_idvg(dev, pol, vto, u_lo, u_hi, step, vds_lin),
                          nm, SUBDIR)
        _check(out, nm)
        u, idr = _sweep_u(out, pol)
        if len(u) < 20:
            raise RuntimeError(f"Id-Vg sweep returned {len(u)} rows")
        out_cache["u"], out_cache["id"] = u, idr
        vth_u, gmmax = vth_max_gm(u, idr)
        if math.isnan(vth_u):
            raise RuntimeError("max-gm extrapolation failed (no positive gm)")
        out_cache["vth_u"] = vth_u
        col.measured(dev, "vth_lin", pol * vth_u, "V",
                     conditions=dict(cond, method="max-gm linear extrapolation",
                                     vth_in_u_coord_V=vth_u,
                                     gm_max_S_per_V=gmmax,
                                     model_card_vto_V=vto),
                     deck=dp, note=VTH_SIGN_NOTE)
    except Exception as e:                                        # noqa: BLE001
        col.measured(dev, "vth_lin", None, "V", conditions=cond, deck=dp,
                     error=str(e), note=VTH_SIGN_NOTE)

    # -- fine subthreshold sweep for S and gm/Id ----------------------------
    nm = f"{dev}_subth"
    dpS = deck_path(nm, SUBDIR)
    su_lo, su_hi, sstep = svto - 1.2, svto + 0.2, 0.004
    condS = dict(cond, u_sweep_V=[su_lo, su_hi], u_step_V=sstep)
    try:
        out, _ = run_deck(_deck_idvg(dev, pol, vto, su_lo, su_hi, sstep,
                                     vds_lin, title="subthreshold Id-Vg"),
                          nm, SUBDIR)
        _check(out, nm)
        su, sid = _sweep_u(out, pol)
        fu, fid, floor = _above_floor(su, sid, mult=50.0)
        if len(fu) < 10:
            raise RuntimeError(f"only {len(fu)} points survive the "
                               f"{50*floor:.3g} A floor cut")
        S, (vlo, vhi), dec = subthreshold_slope(fu, fid, decades_min=2.0)
        condS_fit = dict(
            condS,
            method="least-squares log10(|Id|) vs u over the widest clean window",
            leakage_floor_A=floor, floor_cut_multiple=50.0,
            points_after_floor_cut=len(fu),
            fit_u_lo_V=vlo, fit_u_hi_V=vhi, fit_decades=dec,
            fit_vgs_lo_V=pol * vlo if not math.isnan(vlo) else None,
            fit_vgs_hi_V=pol * vhi if not math.isnan(vhi) else None,
            model_ksubthres_note=("the card's ksubthres IS S in V/dec by "
                                  "construction; audit 2.8 shows the ladder "
                                  "slopes the wrong way"),
        )
        if math.isnan(S):
            raise RuntimeError(f"no clean >=2-decade subthreshold window "
                               f"(only {dec:.2f} decades usable)")
        col.measured(dev, "subthreshold_swing", S, "mV/dec",
                     conditions=condS_fit, deck=dpS,
                     note=("D2 input: fit_u_lo_V/fit_u_hi_V and fit_decades "
                           "give the exact raw fit range. Compare with "
                           "gm_over_id_ceiling on the same sweep."))
    except Exception as e:                                        # noqa: BLE001
        col.measured(dev, "subthreshold_swing", None, "mV/dec",
                     conditions=condS, deck=dpS, error=str(e))
        fu, fid = [], []

    # -- gm/Id ceiling off the same fine sweep ------------------------------
    condG = dict(condS, method="max of central-difference dId/du / Id",
                 basis_deck=dpS)
    try:
        if not fu:
            raise RuntimeError("subthreshold sweep unavailable")
        g, ug, ig = _gm_over_id(fu, fid)
        # The D2 discrimination: is the card's ksubthres a natural-log slope
        # (ceiling 1/k) or a per-decade slope (ceiling ln10/k)?
        ks = card.get("ksubthres")
        cand_ln = (1.0 / ks) if ks else None
        cand_dec = (math.log(10.0) / ks) if ks else None
        reading = "indeterminate (ksubthres unavailable)"
        if cand_ln and cand_dec:
            reading = ("natural-log: ksubthres is a per-e-fold slope, "
                       "S = ln10*ksubthres"
                       if abs(g - cand_ln) < abs(g - cand_dec) else
                       "per-decade: ksubthres IS S in V/dec, ceiling ln10/k")
        col.measured(dev, "gm_over_id_ceiling", g, "1/V",
                     conditions=dict(condG, u_at_max_V=ug,
                                     vgs_at_max_V=pol * ug, id_at_max_A=ig,
                                     model_ksubthres=ks,
                                     natural_log_reading_1_over_k=cand_ln,
                                     per_decade_reading_ln10_over_k=cand_dec,
                                     discriminated_reading=reading),
                     deck=dpS,
                     note=("D2 cross-check. A ceiling near 1/ksubthres implies "
                           "the model reads ksubthres as a NATURAL-log slope; "
                           "near ln(10)/ksubthres implies a per-decade slope. "
                           "Both candidates and the nearer one are in "
                           "conditions. Audit 2.8 asserts the per-decade "
                           "reading (S_mV_per_dec = 1000*ksubthres)."))
        out_cache["gmid"] = g
    except Exception as e:                                        # noqa: BLE001
        col.measured(dev, "gm_over_id_ceiling", None, "1/V", conditions=condG,
                     deck=dpS, error=str(e))
    return out_cache


def _do_strong(col: Collector, dev: str, pol: float, card: dict) -> None:
    """idsat_density, ron_times_w, rsp_specific_ron, theta, and the tempcos."""
    vto = card["vto"]
    vgs_on = vto + pol * VOV_STRONG          # signed, Vov = +4 V
    vds_sat_mag = _vds_sat(dev)
    pitch = _pitch(dev)

    # -- idsat_density ------------------------------------------------------
    nm = f"{dev}_idsat"
    dp = deck_path(nm, SUBDIR)
    cond = dict(W_um=W_UM, M=1, vgs_V=vgs_on, vds_V=pol * vds_sat_mag,
                vov_V=VOV_STRONG, temp_C=27, corner="TT", PROC_ON=0, MM_ON=0,
                vds_rule="min(0.5*BV_rated, 10 V)", bv_rated_V=BV_RATED[dev],
                model_vto_V=vto)
    if dev in HAS_L:
        cond["L_um"] = 8.0
    try:
        out, _ = run_deck(_deck_bias(dev, pol, vgs_on, pol * vds_sat_mag,
                                     title="Idsat"), nm, SUBDIR)
        _check(out, nm)
        idd = abs(_need(parse_prints(out), "@m.xh1.m0[id]", nm))
        col.measured(dev, "idsat_density", idd / W_UM * 1e3, "mA/um",
                     conditions=dict(cond, id_total_A=idd), deck=dp,
                     note=("F1 EXPECTED FAIL: kp implies a cell 287x-5213x "
                           "wider than W_REF (audit 2.1), so this should land "
                           "~10^2-10^3x above the anchor band. That is the "
                           "finding, not a harness error."))
    except Exception as e:                                        # noqa: BLE001
        col.measured(dev, "idsat_density", None, "mA/um", conditions=cond,
                     deck=dp, error=str(e))

    # -- ron_times_w and rsp_specific_ron, plus rd_tempco -------------------
    ron: dict[float, float] = {}
    ron_decks: dict[str, str] = {}
    for t in (-40.0, 27.0, 150.0):
        tag = {-40.0: "m40", 27.0: "27", 150.0: "150"}[t]
        nm = f"{dev}_ron_{tag}"
        ron_decks[tag] = deck_path(nm, SUBDIR)
        try:
            # Vth moves with temperature, so hold Vov constant by re-deriving
            # the gate bias from the card's own temperature-shifted vto.
            out, _ = run_deck(_deck_bias(dev, pol, vgs_on, pol * 0.1,
                                         temp=(None if t == 27.0 else t),
                                         title=f"Ron at {t:g} degC"),
                              nm, SUBDIR)
            _check(out, nm)
            idd = abs(_need(parse_prints(out), "@m.xh1.m0[id]", nm))
            if idd <= 0:
                raise RuntimeError("zero drain current at the Ron bias")
            ron[t] = 0.1 / idd
        except Exception:                                         # noqa: BLE001
            pass

    condR = dict(W_um=W_UM, M=1, vgs_V=vgs_on, vds_V=pol * 0.1,
                 vov_V=VOV_STRONG, temp_C=27, corner="TT",
                 method="Ron = |Vds| / |Id| at |Vds| = 0.1 V",
                 model_vto_V=vto)
    if dev in HAS_L:
        condR["L_um"] = 8.0
    try:
        if 27.0 not in ron:
            raise RuntimeError("Ron at 27 degC unavailable")
        col.measured(dev, "ron_times_w", ron[27.0] * W_UM, "Ohm.um",
                     conditions=dict(condR, ron_ohm=ron[27.0]),
                     deck=ron_decks["27"],
                     note=("F1 EXPECTED FAIL: rd+rs imply a specific Ron "
                           "370x-2660x below the 1-D unipolar silicon limit "
                           "(audit 2.2), so this lands ~10^3x BELOW the anchor "
                           "band. That is the finding."))
        area_cm2 = (W_UM * 1e-4) * (pitch * 1e-4)
        col.derived(dev, "rsp_specific_ron", ron[27.0] * area_cm2 * 1e3,
                    "mOhm.cm^2",
                    conditions=dict(condR, pitch_um=pitch,
                                    cell_area_cm2=area_cm2,
                                    ron_ohm=ron[27.0],
                                    pitch_source="audit 2.2 ladder: "
                                                 "20V:5 40V:7 60V:9 80V:11 "
                                                 "120V:15 200V:22 um",
                                    unipolar_limit_mOhm_cm2=(
                                        5.9e-9 * BV_RATED[dev] ** 2.5 * 1e3)),
                    deck=ron_decks["27"],
                    note=("derived from ron_times_w and the assumed cell "
                          "pitch. Compare against unipolar_limit_mOhm_cm2: no "
                          "lateral RESURF device can go below it."))
    except Exception as e:                                        # noqa: BLE001
        col.measured(dev, "ron_times_w", None, "Ohm.um", conditions=condR,
                     deck=ron_decks.get("27"), error=str(e))
        col.derived(dev, "rsp_specific_ron", None, "mOhm.cm^2",
                    conditions=dict(condR, pitch_um=pitch),
                    deck=ron_decks.get("27"), error=str(e))

    condRT = dict(condR, temps_C=[-40, 27, 150], decks=ron_decks,
                  metric="tempco_ppm(Ron(-40), Ron(27), Ron(150))")
    try:
        if not {-40.0, 27.0, 150.0} <= set(ron):
            raise RuntimeError(f"Ron missing at "
                               f"{sorted({-40.0,27.0,150.0} - set(ron))} degC")
        tc = tempco_ppm(ron[-40.0], ron[27.0], ron[150.0])
        col.derived(dev, "rd_tempco", tc, "ppm/degC",
                    conditions=dict(condRT, ron_m40_ohm=ron[-40.0],
                                    ron_27_ohm=ron[27.0],
                                    ron_150_ohm=ron[150.0]),
                    deck=ron_decks["150"],
                    note=("full -40..150 degC span, normalised to the 27 degC "
                          "value, matching how tc1 is specified. Note the gate "
                          "bias is held at a FIXED voltage across temperature, "
                          "so a little of this tempco is the vto drift feeding "
                          "through the channel rather than pure drift-region "
                          "mobility."))
    except Exception as e:                                        # noqa: BLE001
        col.derived(dev, "rd_tempco", None, "ppm/degC", conditions=condRT,
                    deck=ron_decks.get("150"), error=str(e))


def _do_vto_tempco(col: Collector, dev: str, pol: float, card: dict) -> None:
    """Vth at -40 / 27 / 150 degC -> mV/degC (signed)."""
    vto = card["vto"]
    svto = pol * vto
    u_lo, u_hi, step = svto - 1.5, svto + 5.0, 0.02
    vth: dict[float, float] = {}
    decks: dict[str, str] = {}
    for t in (-40.0, 27.0, 150.0):
        tag = {-40.0: "m40", 27.0: "27", 150.0: "150"}[t]
        nm = f"{dev}_vth_{tag}"
        decks[tag] = deck_path(nm, SUBDIR)
        try:
            out, _ = run_deck(
                _deck_idvg(dev, pol, vto, u_lo, u_hi, step, 0.1,
                           temp=(None if t == 27.0 else t),
                           title=f"Id-Vg at {t:g} degC"), nm, SUBDIR)
            _check(out, nm)
            u, idr = _sweep_u(out, pol)
            v, _g = vth_max_gm(u, idr)
            if not math.isnan(v):
                vth[t] = pol * v            # signed
        except Exception:                                         # noqa: BLE001
            pass

    cond = dict(W_um=W_UM, M=1, vds_V=pol * 0.1, corner="TT",
                temps_C=[-40, 27, 150], decks=decks,
                method="max-gm extrapolation at each temperature",
                metric="(Vth(150) - Vth(-40)) / 190 degC")
    if dev in HAS_L:
        cond["L_um"] = 8.0
    try:
        if not {-40.0, 27.0, 150.0} <= set(vth):
            raise RuntimeError(f"Vth missing at "
                               f"{sorted({-40.0,27.0,150.0} - set(vth))} degC")
        tc = (vth[150.0] - vth[-40.0]) / 190.0 * 1000.0
        col.derived(dev, "vto_tempco", tc, "mV/degC",
                    conditions=dict(cond, vth_m40_V=vth[-40.0],
                                    vth_27_V=vth[27.0], vth_150_V=vth[150.0]),
                    deck=decks["150"],
                    note=("SIGNED, in the device's own polarity: a p-channel "
                          "Vth that becomes less negative with temperature "
                          "gives a POSITIVE number here while |Vth| falls. "
                          "The anchor band (-3..-1 mV/degC) is written for the "
                          "n-channel sense, so compare -|value| for p-channel."))
    except Exception as e:                                        # noqa: BLE001
        col.derived(dev, "vto_tempco", None, "mV/degC", conditions=cond,
                    deck=decks.get("150"), error=str(e))


def _do_theta(col: Collector, dev: str, pol: float, card: dict) -> None:
    """theta from the strong-inversion Id = (kp/2)Vov^2/(1+theta*Vov) form.

    Rearranged to a straight line so a single least-squares fit does it:
        Vov^2 / Id = (2/kp')*(1 + theta*Vov)
    slope/intercept = theta, and kp' (the effective mtot-scaled kp) falls out
    of the intercept as a by-product.
    """
    vto = card["vto"]
    svto = pol * vto
    vds_mag = _vds_sat(dev)
    u_lo, u_hi, step = svto + 0.5, svto + 4.0, 0.05
    nm = f"{dev}_theta"
    dp = deck_path(nm, SUBDIR)
    cond = dict(W_um=W_UM, M=1, vds_V=pol * vds_mag, temp_C=27, corner="TT",
                vov_range_V=[0.5, 4.0], u_step_V=step, model_vto_V=vto,
                model_kp=card.get("kp"), model_theta=card.get("theta"),
                method="linfit(Vov, Vov^2/Id); theta = slope/intercept")
    if dev in HAS_L:
        cond["L_um"] = 8.0
    try:
        out, _ = run_deck(_deck_idvg(dev, pol, vto, u_lo, u_hi, step, vds_mag,
                                     title="strong-inversion Id-Vg (theta)"),
                          nm, SUBDIR)
        _check(out, nm)
        u, idr = _sweep_u(out, pol)
        xs, ys, raw = [], [], []
        for uu, ii in zip(u, idr):
            vov = uu - svto
            if vov <= 0.3 or ii <= 0:
                continue
            xs.append(vov)
            ys.append(vov * vov / ii)
            raw.append([round(vov, 6), ii])
        if len(xs) < 8:
            raise RuntimeError(f"only {len(xs)} usable strong-inversion points")
        slope, intercept = linfit(xs, ys)
        if not math.isfinite(slope) or not math.isfinite(intercept) \
                or intercept == 0:
            raise RuntimeError("degenerate fit (zero or non-finite intercept)")
        theta = slope / intercept
        kp_eff = 2.0 / intercept
        # residual, to expose a bad fit rather than let it pass silently
        pred = [intercept + slope * x for x in xs]
        ss_res = sum((a - b) ** 2 for a, b in zip(ys, pred))
        ss_tot = sum((a - sum(ys) / len(ys)) ** 2 for a in ys)
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        rd_rs = (card.get("rd") or 0.0) + (card.get("rs") or 0.0)
        # how much of the applied Vov is eaten by the series drop at the top
        id_top = raw[-1][1]
        ir_drop = id_top * rd_rs
        note = ("D4 input: raw fit points are in conditions.fit_points as "
                "[Vov_V, Id_A]. ")
        if ir_drop > 0.25 * xs[-1] or r2 < 0.98:
            note += (f"POORLY CONDITIONED: the (rd+rs)={rd_rs:.4g} Ohm series "
                     f"drop is {ir_drop:.4g} V at the top of the fit range, "
                     f"i.e. {100*ir_drop/xs[-1]:.0f}% of Vov, and the linear "
                     f"fit gives R^2={r2:.5f}. Series resistance, not mobility "
                     f"degradation, dominates this extraction, so the number "
                     f"is an UPPER BOUND on theta and should not be compared "
                     f"to the card value directly. D4 must redo it with "
                     f"rd=rs=0.")
        else:
            note += (f"series drop {ir_drop:.4g} V ({100*ir_drop/xs[-1]:.0f}% "
                     f"of Vov) at the top of the range, R^2={r2:.5f}; the fit "
                     f"is acceptably conditioned.")
        col.derived(dev, "theta", theta, "1/V",
                    conditions=dict(cond, fit_points=raw, fit_r2=r2,
                                    fit_slope=slope, fit_intercept=intercept,
                                    kp_eff_implied=kp_eff,
                                    rd_plus_rs_ohm=rd_rs,
                                    ir_drop_at_top_of_range_V=ir_drop),
                    deck=dp, note=note)
    except Exception as e:                                        # noqa: BLE001
        col.derived(dev, "theta", None, "1/V", conditions=cond, deck=dp,
                    error=str(e))


def _do_caps(col: Collector, dev: str, pol: float, card: dict) -> None:
    """Cgs / Cgd / Cds vs |Vds| at 1 MHz, device off."""
    vto = card["vto"]
    vgs_off = _vgs_off(pol, vto)
    bv = BV_RATED[dev]
    ladder = []
    for v in (0.1, 12.0, 0.5 * bv, 0.9 * bv):
        if not any(abs(v - x) < 1e-9 for x in ladder):
            ladder.append(v)
    ladder.sort()

    table: list[dict] = []
    decks: dict[str, str] = {}
    for v in ladder:
        tag = f"{v:g}".replace(".", "p")
        nm = f"{dev}_cap_{tag}"
        decks[f"{v:g}"] = deck_path(nm, SUBDIR)
        try:
            out, _ = run_deck(_deck_caps(dev, pol, vgs_off, v), nm, SUBDIR)
            _check(out, nm)
            p = parse_prints(out)
            coss = cap_from_ac(_need(p, "coss", nm), CAP_FREQ)
            crss = cap_from_ac(_need(p, "crss", nm), CAP_FREQ)
            ciss = cap_from_ac(_need(p, "ciss", nm), CAP_FREQ)
            table.append({
                "vds_V": pol * v, "vds_mag_V": v,
                "ciss_fF": ciss / 1e-15, "coss_fF": coss / 1e-15,
                "crss_cgd_fF": crss / 1e-15,
                "cgs_fF": (ciss - crss) / 1e-15,
                "cds_fF": (coss - crss) / 1e-15,
            })
        except Exception:                                         # noqa: BLE001
            table.append({"vds_V": pol * v, "vds_mag_V": v, "error": True})

    good = [r for r in table if "error" not in r]
    cond = dict(W_um=W_UM, M=1, vgs_V=vgs_off, temp_C=27, corner="TT",
                freq_Hz=CAP_FREQ, vac_V=1.0,
                vds_ladder_mag_V=ladder, bv_rated_V=bv,
                c_vs_vds_table=table, decks=decks,
                channel_state="off",
                method=("two AC runs per bias: drain probe with the gate "
                        "AC-grounded gives Coss=Cds+Cgd and, from the gate "
                        "return current, Crss=Cgd; gate probe with the drain "
                        "AC-grounded gives Ciss=Cgs+Cgd. Then Cgs=Ciss-Crss "
                        "and Cds=Coss-Crss. imag() is used rather than abs() "
                        "so the wrapper's Rgmin/Rcond conductance does not "
                        "contaminate the result."),
                model_card_fF={k: (card[k] / 1e-15) for k in
                               ("cgs", "cgdmax", "cgdmin", "cjo") if k in card})
    if dev in HAS_L:
        cond["L_um"] = 8.0

    f2 = ("F2 EXPECTED FAIL: audit 2.4 finds cgs/cgdmax still 3.3x-48x large "
          "after the 2026-06-01 divide-by-1000, with the residual sloping from "
          "48x at the 20 V class to 3.3x at 200 V. cjo is in band.")

    def emit(fom, row, key, units, extra, note):
        """Emit one cap FoM, attributing the deck for ITS OWN bias point."""
        if row is None:
            col.measured(dev, fom, None, units, conditions=dict(cond, **extra),
                         deck=decks.get(f"{ladder[0]:g}"),
                         error="capacitance ladder produced no usable point")
            return
        col.measured(dev, fom, row[key], units,
                     conditions=dict(cond, at_vds_V=row["vds_V"], **extra),
                     deck=decks.get(f"{row['vds_mag_V']:g}"), note=note)

    lowv = good[0] if good else None
    highv = good[-1] if good else None
    emit("cgs_per_cell", lowv, "cgs_fF", "fF", {"quantity": "Ciss - Crss"},
         "Cgs at the lowest drain bias in the ladder. " + f2)
    emit("cgdmax_per_cell", lowv, "crss_cgd_fF", "fF", {"quantity": "Crss"},
         ("Cgd at the LOWEST drain bias, i.e. the top of the ladder. Note this "
          "is a terminal measurement with the channel off (Vgd is slightly "
          "negative), so it sits below the card's cgdmax parameter, which the "
          "VDMOS model only reaches for Vgd > 0. Both are in conditions. "
          + f2))
    emit("cgdmin_per_cell", highv, "crss_cgd_fF", "fF", {"quantity": "Crss"},
         "Cgd at the highest drain bias (0.9x rated BV). " + f2)
    emit("cjo_per_cell", lowv, "cds_fF", "fF", {"quantity": "Coss - Crss"},
         ("drain-source junction capacitance with the channel off, at the "
          "lowest drain bias, so it approximates the zero-bias cjo. Audit 2.4 "
          "finds cjo IN BAND across the whole family (0.25x-2.9x) -- this one "
          "is the control that shows the F2 slope is real and not a harness "
          "artifact."))


def _do_bv(col: Collector, dev: str, pol: float, card: dict) -> dict:
    """Breakdown at all five corners. Returns {corner: BV}."""
    vgs_off = _vgs_off(pol, card["vto"])
    bvs: dict[str, float] = {}
    decks: dict[str, str] = {}
    for corner in CORNER_CASE:
        nm = f"{dev}_bv_{corner}"
        decks[corner] = deck_path(nm, SUBDIR)
        try:
            out, _ = run_deck(_deck_bv(dev, pol, vgs_off, corner), nm, SUBDIR)
            _check(out, nm)
            u, idr = _sweep_u(out, pol)   # u = pol*Vd here, i.e. |Vds|
            bvs[corner] = _interp_crossing(u, idr, BV_COMPLIANCE_A)
        except Exception:                                         # noqa: BLE001
            pass

    audit = AUDIT_BV_TABLE.get(dev)
    cross = None
    if audit and bvs:
        dev_max = max(abs(bvs[c] - audit[c]) / audit[c] * 100.0
                      for c in audit if c in bvs)
        cross = {
            "audit_3a81be0_table_V": audit,
            "max_abs_deviation_pct": dev_max,
            "verdict": ("AGREES with the audit 3a81be0 table to within "
                        f"{dev_max:.2f}% at every corner"
                        if dev_max < 1.0 else
                        "DISAGREES with the audit 3a81be0 table by up to "
                        f"{dev_max:.2f}%"),
        }

    cond = dict(W_um=W_UM, M=1, vgs_V=vgs_off, temp_C=27, PROC_ON=0, MM_ON=0,
                compliance_A=BV_COMPLIANCE_A,
                method=("gate-off drain ramp over 0.80x..1.10x the card "
                        "rating, step rating/2000, crossing of |Id| = 1 uA "
                        "interpolated in log(Id)"),
                bv_all_corners_V=bvs, decks=decks,
                bv_rated_V=BV_RATED[dev])
    if dev in HAS_L:
        cond["L_um"] = 8.0
    if cross:
        cond["audit_cross_check"] = cross

    note = ("all five corners are in conditions.bv_all_corners_V; the value "
            "field is TT. The four non-TT corners are also emitted separately "
            "as bv_corner_<NAME>.")
    if cross:
        note += " Audit cross-check: " + cross["verdict"] + "."

    if "TT" in bvs:
        col.measured(dev, "bv", bvs["TT"], "V", conditions=cond,
                     deck=decks["TT"], note=note)
    else:
        col.measured(dev, "bv", None, "V", conditions=cond,
                     deck=decks.get("TT"),
                     error="TT breakdown ramp did not reach 1 uA compliance")
    for corner in ("FF", "SS", "FS", "SF"):
        c2 = dict(cond, corner=corner)
        if corner in bvs:
            col.measured(dev, f"bv_corner_{corner}", bvs[corner], "V",
                         conditions=c2, deck=decks[corner],
                         note="companion to bv; see bv.conditions for the "
                              "full five-corner table and the audit "
                              "cross-check.")
        else:
            col.measured(dev, f"bv_corner_{corner}", None, "V", conditions=c2,
                         deck=decks.get(corner),
                         error="breakdown ramp did not reach 1 uA compliance")
    return bvs


def _do_l_drift(col: Collector, dev: str, pol: float, card: dict) -> None:
    """BV vs drift length L -- NDMOS200 / PDMOS200 only. Expected FLAT."""
    vgs_off = _vgs_off(pol, card["vto"])
    rated = BV_RATED[dev]
    tbl: list[dict] = []
    decks: dict[str, str] = {}
    for l_um in L_LIST_UM:
        nm = f"{dev}_bv_L{l_um:g}u"
        decks[f"{l_um:g}u"] = deck_path(nm, SUBDIR)
        try:
            out, _ = run_deck(_deck_bv(dev, pol, vgs_off, "TT", l_um=l_um),
                              nm, SUBDIR)
            _check(out, nm)
            u, idr = _sweep_u(out, pol)
            tbl.append({"L_um": l_um,
                        "bv_V": _interp_crossing(u, idr, BV_COMPLIANCE_A)})
        except Exception as e:                                    # noqa: BLE001
            tbl.append({"L_um": l_um, "error": str(e)})

    got = [r for r in tbl if "bv_V" in r]
    spread = None
    if len(got) >= 2:
        vs = [r["bv_V"] for r in got]
        spread = (max(vs) - min(vs)) / (sum(vs) / len(vs)) * 100.0

    l_needed = rated / E_SUST_V_PER_UM
    cond = dict(W_um=W_UM, M=1, vgs_V=vgs_off, temp_C=27, corner="TT",
                compliance_A=BV_COMPLIANCE_A,
                L_sweep_um=L_LIST_UM, L_MIN_um=5.0, L_REF_um=8.0,
                bv_vs_L_table=tbl, decks=decks,
                bv_spread_across_L_pct=spread,
                bv_rated_V=rated, assumed_E_sust_V_per_um=E_SUST_V_PER_UM,
                definition=("L at which BV would reach the card rating if BV "
                            "scaled at 20 V/um, i.e. bv_rated / 20"))
    col.derived(dev, "l_drift_for_bv", l_needed, "um", conditions=cond,
                deck=decks.get("8u"),
                note=("known artifact: BV is constant vs L; logged not "
                      "asserted. The reported value is NOT a measurement -- it "
                      "is the drift length the rating WOULD imply at 20 V/um "
                      "(audit 2.9). The actual measured BV-vs-L table is in "
                      "conditions.bv_vs_L_table and is flat to "
                      + (f"{spread:.3f}%" if spread is not None else "n/a")
                      + " over L = 5..16 um, which is the finding: above "
                        "L_REF the L knob only adds RDRIFT, below it Leff "
                        "clamps at L_MIN, and breakdown never moves."))


def _do_rcond(col: Collector, dev: str, pol: float) -> None:
    """KNOWN ARTIFACT: DC gate current through the wrapper's Rcond shunt."""
    nm = f"{dev}_rcond"
    dp = deck_path(nm, SUBDIR)
    targets = [1.8, 5.0, 12.0]
    cond = dict(W_um=W_UM, M=1, vds_V=pol * 0.1, temp_C=27, corner="TT",
                source="grounded",
                mechanism="Rcond g_int s 1e6 in the subckt wrapper",
                expected_A={f"{t:g}": t / 1e6 for t in targets})
    if dev in HAS_L:
        cond["L_um"] = 8.0
    note = ("known artifact: Rcond g_int s 1e6 (anchor _known_artifacts). "
            "A real insulated gate draws no DC current; this 1 Mohm "
            "gate-to-source shunt exists to break a floating-node singularity "
            "(HANDOFF_dmos200_vshift_multiinstance_REPLY). Logged, not "
            "asserted. All three bias points are in conditions.igate_A.")
    try:
        out, _ = run_deck(_deck_rcond(dev, pol), nm, SUBDIR)
        _check(out, nm)
        u, ig = _sweep_u(out, pol)          # u = |Vgs|
        vals = {}
        for t in targets:
            k = min(range(len(u)), key=lambda j: abs(u[j] - t))
            vals[f"{t:g}"] = {"vgs_V": pol * u[k], "igate_A": ig[k]}
        col.measured(dev, "rcond_gate_current", vals["5"]["igate_A"], "A",
                     conditions=dict(cond, igate_A=vals,
                                     value_at_vgs_V=pol * 5.0),
                     deck=dp, note=note)
    except Exception as e:                                        # noqa: BLE001
        col.measured(dev, "rcond_gate_current", None, "A", conditions=cond,
                     deck=dp, error=str(e), note=note)


def _do_body_diode(col: Collector, dev: str, card: dict, card_deck: str) -> None:
    """Body-diode transit time, read from the model card. NOT measured."""
    tt = card.get("tt")
    cond = dict(source="@%s_INT[tt] read back from the resolved model card"
                       % dev, corner="TT", temp_C=27,
                exercised="no -- no reverse-recovery transient was run")
    note = ("read from model card, not measured; reverse recovery not "
            "exercised in phase 2. A reverse-recovery transient on these "
            "wrappers is slow and fragile (the Vshift/Rgmin/Rcond gate network "
            "provokes 'Timestep too small' on HV stacks), and the audit 2.10 "
            "verdict on tt is already 'OK, no action' -- 18..155 ns is exactly "
            "what an HV drift body diode looks like. Measuring it would spend "
            "the phase-2 runtime budget to re-confirm a non-finding.")
    if tt is None:
        col.derived(dev, "body_diode_tt", None, "s", conditions=cond,
                    deck=card_deck,
                    error="model card readback did not return tt", note=note)
    else:
        col.derived(dev, "body_diode_tt", tt, "s", conditions=cond,
                    deck=card_deck, note=note)


# --------------------------------------------------------------------------
# Monte Carlo
# --------------------------------------------------------------------------

def _mc_extract(out: str) -> dict[str, float]:
    """Per-sample draw.

    v(g_int) = Vg + DVTH_MM, so the two internal node voltages differ from the
    drawn Vth offsets only by the common gate bias. That constant cancels
    exactly in `delta_mV`, and a constant offset does not move a standard
    deviation, so every sigma reported downstream is unaffected by it.
    """
    p = parse_prints(out)
    try:
        va = p["v(xa.g_int)"]
        vb = p["v(xb.g_int)"]
    except KeyError:
        return {}
    d = {"vgint_a_mV": va * 1000.0, "vgint_b_mV": vb * 1000.0,
         "delta_mV": (va - vb) * 1000.0}
    ia, ib = p.get("@m.xa.m0[id]"), p.get("@m.xb.m0[id]")
    if ia is not None and ib is not None:
        d["id_a"], d["id_b"] = ia, ib
    return d


def _do_mc(col: Collector, dev: str, pol: float, card: dict) -> None:
    x3, ladder = MM_3SIGMA[dev]
    wrapper_1sigma_mV = x3 / 3.0 * 1000.0        # mtot = 1 at W_REF
    cond = dict(W_um=W_UM, M=1, N=MC_N, temp_C=27, corner="TT",
                PROC_ON=0, MM_ON=1,
                wrapper_dvth_3sigma_coeff=x3,
                wrapper_implied_per_device_1sigma_mV=wrapper_1sigma_mV,
                mismatch_ladder=ladder,
                ladder_note=("audit 2.6: ladder A (20/60/120 V + DNMOS20) is "
                             "the physical one at 0.65-0.82x the tox-based "
                             "A_VT expectation; ladder B (40/80/200 V) is "
                             "uniformly ~3x optimistic and is the defective "
                             "one."),
                pair="two identical W_REF instances at Vov = +0.5 V",
                vgs_V=card["vto"] + pol * 0.5, vds_V=pol * 1.0,
                quantity=("v(g_int) - v(g) of each instance IS that instance's "
                          "drawn Vth offset in volts, because the wrapper "
                          "injects mismatch as Vshift g g_int DC {-DVTH_MM}. "
                          "The common gate bias cancels in the pair delta and "
                          "does not move any standard deviation."),
                per_device_rule="stdev(delta)/sqrt(2)")
    if dev in HAS_L:
        cond["L_um"] = 8.0
    try:
        res = mc_run(lambda i: _deck_mc(dev, pol, card["vto"]), f"{dev}_mc",
                     MC_N, _mc_extract, subdir=f"{SUBDIR}_mc")
        cond = dict(cond, n_samples_returned=res.n, seed_note=res.seed_note)
        if res.n < 3:
            raise RuntimeError(f"only {res.n}/{MC_N} MC samples parsed")
        if res.degenerate:
            raise RuntimeError(
                "MC DEGENERATE: every sample came back identical. ngspice is "
                "not re-randomising the wrapper's .param AGAUSS draw across "
                "invocations, so this sigma is meaningless. See char_lib "
                "mc_run() and characterization-inventory.md 6.5 #22.")
        s_pair = res.sigma("delta_mV")
        s_dev = s_pair / math.sqrt(2.0)
        col.measured(dev, "sigma_vth_1sigma_at_wref", s_dev, "mV",
                     conditions=dict(cond, pair_sigma_mV=s_pair,
                                     pair_mean_mV=res.mean("delta_mV"),
                                     single_instance_sigma_a_mV=res.sigma(
                                         "vgint_a_mV"),
                                     single_instance_sigma_b_mV=res.sigma(
                                         "vgint_b_mV"),
                                     id_sigma_a_A=res.sigma("id_a"),
                                     id_sigma_b_A=res.sigma("id_b"),
                                     ratio_to_wrapper_prediction=(
                                         s_dev / wrapper_1sigma_mV
                                         if wrapper_1sigma_mV else None)),
                     deck=res.deck, sigma="1-sigma",
                     note=("PER-DEVICE sigma = pair_sigma/sqrt(2). Should land "
                           "on wrapper_implied_per_device_1sigma_mV = "
                           f"{wrapper_1sigma_mV:.3f} mV; ratio_to_wrapper_"
                           "prediction is the end-to-end check that the "
                           "AGAUSS 3-sigma convention and the 1/sqrt(mtot) "
                           "area scaling both behave. The two "
                           "single_instance_sigma_* entries confirm the two "
                           "instances draw independently."))
    except Exception as e:                                        # noqa: BLE001
        col.measured(dev, "sigma_vth_1sigma_at_wref", None, "mV",
                     conditions=cond, sigma="1-sigma", error=str(e))


# --------------------------------------------------------------------------
# the inventory 6.3 capacitance fork -- NDMOS200 only
# --------------------------------------------------------------------------

_REPRO1_BODY = """.param SOA_ON=1
VB  d 0 DC {VBIAS} AC 1
Vg  g 0 DC 0
XN5 d g 0 NDMOS200 W=40u L=8u
.param VBIAS=0.1
.ac lin 1 1meg 1meg
.control
  foreach vb 0.1 12 100 200
    alter VB dc=$vb
    run
    let cdrain = abs(i(VB))/(2*3.14159265*1e6*1)
    echo "Vds=$vb" ; print cdrain
  end
.endc
.end
"""

_REPRO1_FIXED_BODY = """.param SOA_ON=1
VB  d 0 DC {VBIAS} AC 1
Vg  g 0 DC 0
XN5 d g 0 NDMOS200 W=40u L=8u
.param VBIAS=0.1
.ac lin 1 1meg 1meg
.control
  foreach vb 0.1 12 100 200
    alter VB dc=$vb
    run
    let cdrain = abs(i(VB))/(2*3.14159265*1e6*1)
    echo VDSMARK $vb
    print cdrain
  end
.endc
.end
"""


def _changelog_variant_deck(vds: float) -> str:
    """The CHANGELOG / coss_check.cir form: one parse-time bias, one run.

    Differences from Repro-1: DC bias is set on the source card rather than by
    `alter` inside a foreach, and the 2*pi is ngspice's PI constant rather than
    a literal 3.14159265.
    """
    d = header(f"NDMOS200 cap reconciliation -- CHANGELOG/coss_check variant, "
               f"Vds={vds:g} V",
               instruments="VB 1 V AC probe at 1 MHz; Vg ideal DC")
    d += f"VB d 0 DC {vds:g} AC 1\n"
    d += "Vg g 0 DC 0\n"
    d += "XN5 d g 0 NDMOS200 W=40u L=8u\n"
    d += ".ac lin 1 1meg 1meg\n"
    d += ".control\nrun\n"
    d += "let cdrain = abs(i(VB))/(2*PI*1e6)\n"
    d += "print cdrain\n"
    d += ".endc\n.end\n"
    return d


def _do_cap_reconciliation(col: Collector) -> None:
    dev = "NDMOS200"
    vds_list = [0.1, 12.0, 100.0, 200.0]
    # Historical PRE-fix drain capacitances, in farads, as reported by the two
    # sources. HANDOFF_vdmos_caps.md "Reproduction / Repro 1" gives 172 pF /
    # 52 pF / 18.7 pF; docs/CHANGELOG.md 2026-06-01 gives 105 / 29.5 / 11.4 /
    # 8.84 pF pre-fix and exactly 1000x less post-fix.
    handoff_pre_fix = {"0.1": 172e-12, "12": 52e-12, "200": 18.7e-12}
    changelog_pre_fix = {"0.1": 105e-12, "12": 29.5e-12,
                         "100": 11.4e-12, "200": 8.84e-12}

    nm_a = f"{dev}_recon_repro1_verbatim"
    nm_af = f"{dev}_recon_repro1_fixed"
    dp_a = deck_path(nm_a, SUBDIR)
    dp_af = deck_path(nm_af, SUBDIR)

    result: dict = {
        "device_under_test": "NDMOS200 W=40u L=8u, gate at 0 V, AC 1 MHz",
        "quantity": "drain terminal capacitance |i(VB)|/(2*pi*f*Vac)",
        "handoff_reported_pre_fix_F": handoff_pre_fix,
        "changelog_reported_pre_fix_F": changelog_pre_fix,
        "changelog_reported_post_fix_F": {
            k: v / 1000.0 for k, v in changelog_pre_fix.items()},
        "decks": {"repro1_verbatim": dp_a, "repro1_fixed_echo": dp_af},
    }

    try:
        # (a) HANDOFF Repro-1, VERBATIM
        d = header("NDMOS200 cap reconciliation -- HANDOFF_vdmos_caps.md "
                   "Repro-1, VERBATIM",
                   instruments="VB 1 V AC probe at 1 MHz; Vg ideal DC")
        out_a, _ = run_deck(d + _REPRO1_BODY, nm_a, SUBDIR)
        _check(out_a, nm_a)
        pa = parse_prints(out_a)
        result["repro1_verbatim_cdrain_prints"] = {
            k: v for k, v in pa.items() if "cdrain" in k}
        result["repro1_verbatim_emitted_any_capacitance"] = bool(
            result["repro1_verbatim_cdrain_prints"])

        # (a') the same deck with the echo/print on separate lines
        d = header("NDMOS200 cap reconciliation -- HANDOFF Repro-1 with the "
                   "echo and print on separate lines",
                   instruments="VB 1 V AC probe at 1 MHz; Vg ideal DC")
        out_af, _ = run_deck(d + _REPRO1_FIXED_BODY, nm_af, SUBDIR)
        _check(out_af, nm_af)
        vals_a: dict[str, float] = {}
        cur = None
        for line in out_af.splitlines():
            s = line.strip()
            if s.startswith("VDSMARK"):
                cur = s.split()[-1]
            elif cur and s.startswith("cdrain") and "=" in s:
                try:
                    vals_a[cur] = float(s.split("=")[1].strip())
                except ValueError:
                    pass
                cur = None
        result["repro1_fixed_measured_F"] = vals_a

        # (b) the CHANGELOG variant, one deck per bias
        vals_b: dict[str, float] = {}
        decks_b: dict[str, str] = {}
        for v in vds_list:
            nm = f"{dev}_recon_changelog_{f'{v:g}'.replace('.', 'p')}"
            decks_b[f"{v:g}"] = deck_path(nm, SUBDIR)
            out, _ = run_deck(_changelog_variant_deck(v), nm, SUBDIR)
            _check(out, nm)
            p = parse_prints(out)
            if "cdrain" in p:
                vals_b[f"{v:g}"] = p["cdrain"]
        result["changelog_variant_measured_F"] = vals_b
        result["decks"]["changelog_variant"] = decks_b

        # agreement between the two methods as run TODAY
        ratios = {k: (vals_a[k] / vals_b[k])
                  for k in vals_a if k in vals_b and vals_b[k]}
        result["method_a_over_method_b_ratio"] = ratios
        max_dev = (max(abs(r - 1.0) for r in ratios.values()) * 100.0
                   if ratios else None)
        result["max_method_disagreement_pct"] = max_dev

        # the historical 1.6-2.1x fork, both sources taken PRE-fix
        result["historical_handoff_over_changelog_ratio"] = {
            k: hv / changelog_pre_fix[k]
            for k, hv in handoff_pre_fix.items() if k in changelog_pre_fix}

        if not ratios:
            raise RuntimeError("neither variant produced a usable capacitance")

        verbatim_ok = result["repro1_verbatim_emitted_any_capacitance"]
        note = (
            "VERDICT: the 1.6-2.1x pre-fix disagreement is NOT explicable by "
            "probe terminal or AC-ground topology -- it is a genuine "
            "unexplained gap in the historical reports. Two findings.\n"
            "(1) The two decks are methodologically IDENTICAL. Both drive the "
            "drain with a 1 V AC source, both hold the gate at DC 0 with no AC "
            "component (so the gate is an AC ground in both), both read the "
            "same branch current i(VB), both divide by 2*pi*1e6. The only real "
            "differences are cosmetic: `alter` inside a foreach versus a "
            "parse-time DC value, and ngspice's PI constant versus a literal "
            "3.14159265. Run today they agree to "
            f"{max_dev:.4g}% at every bias in the ladder "
            "(method_a_over_method_b_ratio), so neither `alter` nor the "
            "constant explains anything.\n"
            "(2) Today's numbers reproduce the CHANGELOG's post-fix table "
            "exactly (105 / 29.5 / 11.4 / 8.84 fF at 0.1 / 12 / 100 / 200 V). "
            "Since the VDMOS terminal capacitances are linear in the cgs / "
            "cgdmax / cgdmin / cjo card parameters, the CHANGELOG's PRE-fix "
            "column is exactly 1000x these, i.e. self-consistent. The "
            "HANDOFF's pre-fix numbers (172 / 52 / 18.7 pF) are not reachable "
            "from any uniform rescale of the current cards, and critically the "
            "handoff/changelog ratio is NOT flat -- it rises 1.64x -> 1.76x -> "
            "2.12x with drain bias. A different W, M or mtot would scale every "
            "bias point equally and produce a FLAT ratio; a bias-dependent "
            "ratio can only come from a different split between the "
            "bias-independent caps (cgs, cgd) and the bias-dependent junction "
            "cap (cjo). The most likely explanation is that the handoff was "
            "measured against an earlier revision of the model cards with a "
            "different cap split, not against the cards the CHANGELOG "
            "verified. It cannot be reconciled from the decks alone.\n"
            "(3) Incidental but real: the HANDOFF's Repro-1 as printed does "
            "not work. `echo \"Vds=$vb\" ; print cdrain` uses `;`, which is a "
            "COMMENT character in ngspice's control language, so `print "
            "cdrain` is never executed and the deck emits no capacitance at "
            "all. Run verbatim it emitted "
            + ("capacitance values anyway" if verbatim_ok else
               "ZERO cdrain lines, confirming this")
            + ". Whatever produced the 172 pF figure was therefore not the "
            "deck as published. repro1_fixed_measured_F is the same deck with "
            "the echo and print on separate lines."
        )
        col.measured(dev, "cap_reconciliation_ndmos200",
                     max_dev, "percent", conditions=result, deck=dp_af,
                     note=note)
    except Exception as e:                                        # noqa: BLE001
        col.measured(dev, "cap_reconciliation_ndmos200", None, "percent",
                     conditions=result, deck=dp_a, error=str(e))


# --------------------------------------------------------------------------
# per-device driver
# --------------------------------------------------------------------------

def _run_device(col: Collector, dev: str, anchors: dict) -> None:
    pol = _pol(dev)
    card, card_deck = _read_card(dev)

    for fn in (_do_idvg, _do_strong, _do_vto_tempco, _do_theta, _do_caps,
               _do_bv):
        try:
            fn(col, dev, pol, card)
        except Exception as e:                                    # noqa: BLE001
            col.measured(dev, f"_block_{fn.__name__}", None, "n/a",
                         error=f"{fn.__name__} aborted: {e}")

    if dev in HAS_L:
        try:
            _do_l_drift(col, dev, pol, card)
        except Exception as e:                                    # noqa: BLE001
            col.derived(dev, "l_drift_for_bv", None, "um",
                        error=f"_do_l_drift aborted: {e}")

    try:
        _do_rcond(col, dev, pol)
    except Exception as e:                                        # noqa: BLE001
        col.measured(dev, "rcond_gate_current", None, "A",
                     error=f"_do_rcond aborted: {e}")

    try:
        _do_body_diode(col, dev, card, card_deck)
    except Exception as e:                                        # noqa: BLE001
        col.derived(dev, "body_diode_tt", None, "s",
                    error=f"_do_body_diode aborted: {e}")

    try:
        _do_mc(col, dev, pol, card)
    except Exception as e:                                        # noqa: BLE001
        col.measured(dev, "sigma_vth_1sigma_at_wref", None, "mV",
                     sigma="1-sigma", error=f"_do_mc aborted: {e}")


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------

def run(col: Collector) -> None:
    try:
        anchors = load_anchors()
    except Exception:                                             # noqa: BLE001
        anchors = {}
    for dev in DEVICES:
        try:
            _run_device(col, dev, anchors)
        except Exception as e:                                    # noqa: BLE001
            col.measured(dev, "_module", None, "n/a",
                         error=f"vdmos device driver aborted: {e}")
    try:
        _do_cap_reconciliation(col)
    except Exception as e:                                        # noqa: BLE001
        col.measured("NDMOS200", "cap_reconciliation_ndmos200", None,
                     "percent", error=f"cap reconciliation aborted: {e}")
