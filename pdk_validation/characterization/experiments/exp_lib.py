#!/usr/bin/env python3
"""
Shared helpers for the phase-2 discrimination experiments D1-D4.

These four experiments settle assumptions the phase-1 static audit had to make.
Everything here is READ-ONLY with respect to the PDK: the only files written are
decks (under decks/), isolation model copies (under results/local_models/, via
char_lib.write_local_model) and each experiment's own payload.

Isolation-copy mechanism
------------------------
`card_text(name)` lifts the VERBATIM `.model <NAME> VDMOS ( ... )` block out of
autohv_bicmos180_case_models.inc. `override(body, rd=0, rs=0)` rewrites only the
named continuation lines, leaving every other parameter -- including the
corner/statistical `{...}` expressions -- byte-identical. The result is handed to
char_lib.write_local_model(), which stamps a provenance header and drops it in
results/local_models/.

MEASURED CORRECTION to char_lib's stated mechanism
--------------------------------------------------
char_lib.write_local_model()/lib_include() document the isolation copy as being
".include'd AFTER the PDK so this card shadows the original". **That does not
work in ngspice-45.** Verified directly: a deck that includes the PDK and then a
second `.model NDMOS200_INT VDMOS (... rd=0 rs=0 ...)` reads back
`@NDMOS200_INT[rd] = 1.2`, i.e. ngspice keeps the FIRST definition of a model
name and silently discards the later one. There is no warning. Any experiment
built on the documented shadowing assumption would have run entirely on stock
cards while believing it had zeroed rd/rs.

So `isolated()` gives the copy a DISTINCT model name (`<DEV>_<TAG>`) and the
decks instantiate that card DIRECTLY as a raw VDMOS device, bypassing the subckt
wrapper. At the reference cell this is exactly equivalent to the wrapper, and
`wrapper_equivalence_check()` proves it per experiment rather than asserting it:
with W = W_REF and L = L_REF the wrapper contributes only `mtot = 1`,
`RDRIFT = max(1.2*(L/L_REF-1)/mtot, 1e-6) = 1e-6 ohm` in series with the drain,
`DVTH_MM = 0` at MM_ON=0 (so `Vshift` is a 0 V short), and `Rgmin` 1e9 / `Rcond`
1e6 which sit gate-to-source and carry no drain current. The check runs the
stock card both ways and reports the Id ratio, which must be 1 to within 1e-6.

Sign handling
-------------
Mirrors families/vdmos.py: every sweep runs in the normalised gate coordinate

    u = pol * Vgs        pol = +1 n-channel (incl. depletion DNMOS20), -1 p-channel

so one code path serves n/p/depletion parts and drain current rises monotonically
with u everywhere. Vov = u - pol*vto is therefore always positive-going.

ngspice-45 gotchas honoured throughout
--------------------------------------
  * `set width=1000` before every `print` -- the default 80-column wrap silently
    truncates multi-vector output.
  * `.dc` rows are `index sweepvar vec1 ...`, so the sweep variable is NEVER
    printed (it is already column 1; printing it shifts every later column).
  * `;` is a COMMENT character in the ngspice control language. No `;` is emitted
    inside any `.control` block here.
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent            # .../characterization/experiments
CHAR_DIR = HERE.parent                            # .../characterization
if str(CHAR_DIR) not in sys.path:
    sys.path.insert(0, str(CHAR_DIR))

from char_lib import (                                             # noqa: E402
    REPO_ROOT, header, run_deck, deck_path, parse_dc_sweep, parse_prints,
    ngspice_errored, write_local_model, linfit, ngspice_version, find_ngspice,
    EPS_OX, K_B, Q, T300,
)

MODELS_INC = REPO_ROOT / "autohv_bicmos180_case_models.inc"

# The thirteen VDMOS wrappers, in voltage-class order.
DEVICES = ["NDMOS20", "PDMOS20", "DNMOS20",
           "NDMOS40", "PDMOS40",
           "NDMOS60", "PDMOS60",
           "NDMOS80", "PDMOS80",
           "NDMOS120", "PDMOS120",
           "NDMOS200", "PDMOS200"]

HAS_L = {"NDMOS200", "PDMOS200"}
W_UM = 10.0                     # W_REF: the reference cell every measurement uses

# Card BV ratings (TT), used only to place bias ladders.
BV_RATED = {
    "NDMOS20": 24.0, "PDMOS20": 22.0, "DNMOS20": 24.0,
    "NDMOS40": 48.0, "PDMOS40": 45.0,
    "NDMOS60": 75.0, "PDMOS60": 70.0,
    "NDMOS80": 95.0, "PDMOS80": 90.0,
    "NDMOS120": 135.0, "PDMOS120": 128.0,
    "NDMOS200": 225.0, "PDMOS200": 230.0,
}

# audit 2.1 inputs
L_CH_UM = 0.6
MU_N = 400.0                    # cm^2/Vs
MU_P = 130.0                    # cm^2/Vs
TOX_FLAT_NM = 30.0

# "Electrically zero" series resistance.
#
# An EXACT rd=0 / rs=0 makes ngspice-45's VDMOS fail to find an operating point
# at all -- gmin stepping, source stepping and the transient op all fail and the
# run dies with "Timestep too small; trouble with <model>-instance m0". Verified
# on NDMOS200: rd=rs=0 aborts, rd=rs=1e-9 converges and reads back 1e-9.
# 1e-9 ohm is negligible by any measure that matters here: at the ~1 A drain
# currents these cards produce it drops 1 nV, against the 0.070-4.38 ohm the
# stock cards carry, i.e. nine orders of magnitude down. Every "rd=rs=0" in D1,
# D3 and D4 therefore means R_ZERO.
R_ZERO = 1e-9

VT_300 = K_B * T300 / Q         # thermal voltage at 300.15 K
S_IDEAL_MV_DEC = 1000.0 * math.log(10.0) * VT_300   # ~59.6 mV/dec, the n=1 floor


# --------------------------------------------------------------------------
# model-card text surgery
# --------------------------------------------------------------------------

_INC_TEXT: str | None = None


def _inc() -> str:
    global _INC_TEXT
    if _INC_TEXT is None:
        _INC_TEXT = MODELS_INC.read_text(encoding="utf-8", errors="replace")
    return _INC_TEXT


def card_text(card: str) -> str:
    """Lift the verbatim `.model <card> VDMOS ( ... )` block from the PDK .inc.

    The block runs from the `.model` line to the first continuation line that is
    just `+ )`. Returned text is unmodified -- callers pass it through
    override() and then write_local_model().
    """
    lines = _inc().splitlines()
    start = None
    pat = re.compile(rf"^\s*\.model\s+{re.escape(card)}\s+VDMOS\b", re.I)
    for i, ln in enumerate(lines):
        if pat.match(ln):
            start = i
            break
    if start is None:
        raise RuntimeError(f"{card}: no VDMOS .model card found in {MODELS_INC}")
    for j in range(start + 1, len(lines)):
        if re.match(r"^\s*\+\s*\)\s*$", lines[j]):
            return "\n".join(lines[start:j + 1]) + "\n"
    raise RuntimeError(f"{card}: .model block never closed")


def override(body: str, **params: float) -> str:
    """Rewrite named `+ key=...` continuation lines; leave everything else alone.

    Every requested key must already exist on the card -- silently adding a
    parameter that was not there would change the model in a way the delta
    string does not describe. Missing keys raise.
    """
    out = body
    for key, val in params.items():
        pat = re.compile(rf"^(\s*\+\s*){re.escape(key)}\s*=\s*\S.*$",
                         re.I | re.M)
        new, n = pat.subn(lambda m: f"{m.group(1)}{key}={val:g}", out)
        if n != 1:
            raise RuntimeError(
                f"override: expected exactly one '{key}=' line, found {n}")
        out = new
    return out


def rename_card(body: str, old: str, new: str) -> str:
    """Rename the `.model` in a card body. Required: see the module docstring --
    ngspice-45 keeps the FIRST definition of a model name, so an isolation copy
    that reuses the PDK's name is silently ignored."""
    out, n = re.subn(rf"^(\s*\.model\s+){re.escape(old)}(\s+VDMOS\b)",
                     lambda m: f"{m.group(1)}{new}{m.group(2)}", body,
                     count=1, flags=re.I | re.M)
    if n != 1:
        raise RuntimeError(f"rename_card: could not rename {old}")
    return out


def isolated(dev: str, tag: str, **params: float) -> tuple[Path, str]:
    """Write results/local_models/<dev>_<tag>.mod. Returns (path, model_name).

    The copy is RENAMED to <DEV>_<TAG> rather than shadowing <DEV>_INT, because
    ngspice-45 does not honour redefinition (module docstring). Decks include the
    file and instantiate `model_name` as a raw VDMOS device.
    """
    src = f"{dev}_INT"
    new = f"{dev}_{tag}".upper()
    delta = (", ".join(f"{k}={v:g}" for k, v in params.items())
             + f"; renamed {src} -> {new} because ngspice-45 keeps the FIRST "
               f".model definition and would otherwise silently ignore this "
               f"copy. Every other parameter byte-identical to the PDK card.")
    body = rename_card(override(card_text(src), **params), src, new)
    return write_local_model(f"{dev}_{tag}", src, body, delta), new


def inst_raw(model: str, ref: str = "M0") -> str:
    """Raw VDMOS instance at the reference cell: `M0 d g 0 <model> m=1`.

    m=1 is the wrapper's mtot at W = W_REF, M = 1. VDMOS has no W/L and no bulk
    pin -- size enters only through m, which is the whole reason audit 2.1 has to
    back an implied width out of kp.
    """
    return f"{ref} d g 0 {model} m=1\n"


def card_params(card: str) -> dict[str, float]:
    """Numeric-literal parameters on a card. `{...}` expressions are skipped.

    kp/vto/rd/rs are corner expressions, so they are NOT available here -- read
    those back from ngspice with read_card() instead.
    """
    vals: dict[str, float] = {}
    for m in re.finditer(r"^\s*\+\s*(\w+)\s*=\s*([-+0-9.eE]+)\s*$",
                         card_text(card), re.M):
        try:
            vals[m.group(1).lower()] = float(m.group(2))
        except ValueError:
            pass
    return vals


# --------------------------------------------------------------------------
# device facts
# --------------------------------------------------------------------------

def pol(dev: str) -> float:
    """+1 n-channel (including the depletion DNMOS20), -1 p-channel."""
    return -1.0 if dev.startswith("P") else 1.0


def mu(dev: str) -> float:
    return MU_P if dev.startswith("P") else MU_N


def vclass(dev: str) -> int:
    for v in (200, 120, 80, 60, 40, 20):
        if dev.endswith(str(v)):
            return v
    raise ValueError(dev)


def inst(dev: str, ref: str = "XH1") -> str:
    return (f"{ref} d g 0 {dev} W={W_UM:g}u L=8u\n" if dev in HAS_L
            else f"{ref} d g 0 {dev} W={W_UM:g}u\n")


def fnum(x: float) -> str:
    return repr(float(x))


def check(out: str, what: str) -> None:
    err = ngspice_errored(out)
    if err:
        raise RuntimeError(f"{what}: ngspice error: {err}")


# --------------------------------------------------------------------------
# model-card readback (resolved values, corner TT, 27 degC)
# --------------------------------------------------------------------------

_CARD_KEYS = ["vto", "kp", "theta", "lambda", "rd", "rs", "ksubthres",
              "mtriode", "bv"]


class DUT:
    """Which card a deck exercises: the stock PDK wrapper, or an isolation copy.

    stock(dev)              -> the subckt wrapper, PDK card, nothing changed
    iso(dev, tag, **params) -> a renamed local copy with params forced, wired as
                               a raw VDMOS at the reference cell
    """

    def __init__(self, dev: str, tag: str | None = None, **params: float):
        self.dev = dev
        self.tag = tag
        self.params = params
        if tag is None:
            self.path: Path | None = None
            self.model = f"{dev}_INT"
            self.label = "stock"
        else:
            self.path, self.model = isolated(dev, tag, **params)
            self.label = tag

    @property
    def netlist(self) -> str:
        return inst(self.dev) if self.tag is None else inst_raw(self.model)

    @property
    def idprobe(self) -> str:
        """The operating-point accessor for THIS instance's drain current."""
        # Subckt instances are reached as @m.<inst>.<dev>[..]; a TOP-LEVEL
        # device is just @<dev>[..] with no "m." prefix (ngspice-45 answers
        # "no such device or model name m.m0" if the prefix is used).
        return "@m.xh1.m0[id]" if self.tag is None else "@m0[id]"

    def as_dict(self) -> dict:
        return {"device": self.dev, "variant": self.label,
                "model_card": self.model,
                "forced": {k: v for k, v in self.params.items()},
                "local_model_file": (
                    self.path.relative_to(REPO_ROOT).as_posix()
                    if self.path else None),
                "wiring": ("PDK subckt wrapper at W=W_REF=10u"
                           if self.tag is None else
                           "raw VDMOS instance m=1 (wrapper bypassed -- see "
                           "exp_lib docstring: ngspice-45 ignores a redefined "
                           ".model, so the copy must be renamed)")}


def stock(dev: str) -> DUT:
    return DUT(dev)


def read_card(dut: DUT, subdir: str) -> tuple[dict[str, float], str]:
    """Resolved .model parameters via ngspice's @<MODEL>[param] accessors.

    Every experiment calls this on its ISOLATION COPY as well as on the stock
    card, so the rd=rs=0 edit is PROVEN to have landed rather than assumed --
    which is exactly the failure mode the renaming works around.
    """
    nm = f"{dut.dev}_card_{dut.label}"
    d = header(f"{dut.dev} model-card readback (TT, 27 degC) -- {dut.label}",
               instruments="Vd, Vg -- ideal sources at 0 V for a trivial op",
               local_model=dut.path)
    d += dut.netlist
    d += "Vd d 0 dc 0\nVg g 0 dc 0\n"
    d += ".control\nset width=1000\nop\n"
    d += "print " + " ".join(f"@{dut.model}[{k}]" for k in _CARD_KEYS) + "\n"
    d += ".endc\n.end\n"
    out, _ = run_deck(d, nm, subdir)
    check(out, nm)
    p = parse_prints(out)
    lo = dut.model.lower()
    card = {k: p[f"@{lo}[{k}]"] for k in _CARD_KEYS if f"@{lo}[{k}]" in p}
    if "vto" not in card or "kp" not in card:
        raise RuntimeError(f"{nm}: card readback returned no vto/kp")
    return card, deck_path(nm, subdir)


# --------------------------------------------------------------------------
# sweeps
# --------------------------------------------------------------------------

def deck_idvg(dut: DUT, u_lo: float, u_hi: float, step: float,
              vds_mag: float, title: str) -> str:
    """Id-Vg in the normalised coordinate u = pol*Vgs.

    Vg is swept pol*u_lo -> pol*u_hi with a pol-signed step, so one plain `.dc`
    serves both polarities and column 1 of the table is the real Vg. Only
    abs(i(Vd)) is printed: the sweep variable is already column 1, and printing
    it again would shift every later column.
    """
    p = pol(dut.dev)
    d = header(f"{dut.dev} [{dut.label}] {title}: Vds={p*vds_mag:+.4g} V",
               instruments="Vd (drain bias), Vg (gate sweep) -- ideal sources",
               local_model=dut.path)
    d += dut.netlist
    d += f"Vd d 0 dc {fnum(p * vds_mag)}\nVg g 0 dc 0\n"
    d += ".control\nset width=1000\n"
    d += f"dc Vg {fnum(p * u_lo)} {fnum(p * u_hi)} {fnum(p * step)}\n"
    d += "echo TBL_BEGIN\nprint abs(i(Vd))\necho TBL_END\n"
    d += ".endc\n.end\n"
    return d


def deck_bias(dut: DUT, vgs: float, vds: float, title: str) -> str:
    """One operating point at an explicit already-signed (Vgs, Vds)."""
    d = header(f"{dut.dev} [{dut.label}] {title}: "
               f"Vgs={vgs:+.4g} V, Vds={vds:+.4g} V",
               instruments="Vd, Vg -- ideal sources", local_model=dut.path)
    d += dut.netlist
    d += f"Vd d 0 dc {fnum(vds)}\nVg g 0 dc {fnum(vgs)}\n"
    d += ".control\nset width=1000\nop\n"
    d += f"print {dut.idprobe}\nprint i(Vd)\n"
    d += ".endc\n.end\n"
    return d


def sweep_u(out: str, p: float) -> tuple[list[float], list[float]]:
    """(u, |Id|) from a printed .dc table, sorted ascending in u = pol*Vg."""
    vg, cols = parse_dc_sweep(out, 1)
    if not vg:
        raise RuntimeError("Id-Vg sweep returned no parsable rows")
    pts = sorted(zip((p * v for v in vg), cols[0]))
    return [q[0] for q in pts], [q[1] for q in pts]


def run_idvg(dut: DUT, u_lo: float, u_hi: float, step: float, vds_mag: float,
             subdir: str, nm: str, title: str
             ) -> tuple[list[float], list[float], str]:
    out, _ = run_deck(deck_idvg(dut, u_lo, u_hi, step, vds_mag, title),
                      nm, subdir)
    check(out, nm)
    u, idr = sweep_u(out, pol(dut.dev))
    return u, idr, deck_path(nm, subdir)


def id_at(dut: DUT, vto: float, vov: float, vds_mag: float,
          subdir: str, nm: str) -> tuple[float, str]:
    """|Id| at a given overdrive. Vov is in u coordinates, so always positive."""
    p = pol(dut.dev)
    out, _ = run_deck(deck_bias(dut, vto + p * vov, p * vds_mag,
                                f"Vov={vov:g} V"), nm, subdir)
    check(out, nm)
    pr = parse_prints(out)
    key = dut.idprobe
    if key not in pr:
        raise RuntimeError(f"{nm}: no {key} in output")
    return abs(pr[key]), deck_path(nm, subdir)


def wrapper_equivalence_check(dev: str, subdir: str) -> dict:
    """Prove the raw-instance wiring reproduces the wrapper on the STOCK card.

    Every isolation copy is instantiated raw rather than through the subckt (the
    ngspice model-redefinition problem in the module docstring). This control
    runs the UNMODIFIED card both ways at a strong-inversion bias and reports the
    Id ratio, so the bypass is demonstrated equivalent instead of argued to be.
    """
    dut_w = stock(dev)
    card, _ = read_card(dut_w, subdir)
    p, vto = pol(dev), card["vto"]
    vds = min(0.5 * BV_RATED[dev], 10.0)
    dut_r = DUT(dev, "asis")                      # rename only, no parameter change
    i_w, dw = id_at(dut_w, vto, 4.0, vds, subdir, f"{dev}_equiv_wrapper")
    i_r, dr = id_at(dut_r, vto, 4.0, vds, subdir, f"{dev}_equiv_raw")
    ratio = i_r / i_w if i_w else float("nan")
    return {
        "device": dev, "bias": {"vov_V": 4.0, "vds_V": p * vds},
        "id_via_wrapper_A": i_w, "id_via_raw_instance_A": i_r,
        "ratio_raw_over_wrapper": ratio,
        "agrees": bool(abs(ratio - 1.0) < 1e-6),
        "decks": {"wrapper": dw, "raw": dr},
        "note": ("At W = W_REF and L = L_REF the wrapper adds only mtot=1, a "
                 "1e-6 ohm RDRIFT, a 0 V Vshift (MM_ON=0) and the gate-side "
                 "Rgmin/Rcond shunts, which carry no drain current. A ratio of "
                 "1 confirms the raw-instance bypass changes nothing, so any "
                 "difference seen later is the forced parameter and not the "
                 "wiring."),
    }


# --------------------------------------------------------------------------
# small numeric helpers
# --------------------------------------------------------------------------

def r2_of(xs, ys, slope, intercept) -> float:
    if len(ys) < 3:
        return float("nan")
    pred = [intercept + slope * x for x in xs]
    ss_res = sum((a - b) ** 2 for a, b in zip(ys, pred))
    mean = sum(ys) / len(ys)
    ss_tot = sum((a - mean) ** 2 for a in ys)
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")


def cox_from_tox_nm(tox_nm: float) -> float:
    """Cox in F/m^2."""
    return EPS_OX / (tox_nm * 1e-9)


def w_implied_um(kp: float, dev: str, tox_nm: float) -> float:
    """audit 2.1: W_implied = kp * L_ch / (mu * Cox), all SI, returned in um.

    mu is in cm^2/Vs on the card-facing side, so it is converted to m^2/Vs.
    """
    mu_si = mu(dev) * 1e-4
    return kp * (L_CH_UM * 1e-6) / (mu_si * cox_from_tox_nm(tox_nm)) * 1e6


def tox_band_from_theta_nm(theta: float) -> tuple[float, float]:
    """audit 2.7: theta ~ (1..3)e-7 / tox[cm]  ->  tox[cm] = (1..3)e-7 / theta.

    Returned as (tox_lo_nm, tox_hi_nm) -- a BAND, never a point, because the
    empirical constant spans 3x.
    """
    if theta <= 0:
        return float("nan"), float("nan")
    return (1e-7 / theta) * 1e7, (3e-7 / theta) * 1e7   # cm -> nm


def spread(vals) -> float:
    """max/min of a positive series: the flatness metric D4 turns on."""
    v = [x for x in vals if x and math.isfinite(x) and x > 0]
    return max(v) / min(v) if len(v) >= 2 else float("nan")


def provenance() -> dict:
    return {"ngspice": ngspice_version(), "ngspice_bin": find_ngspice(),
            "models_inc": MODELS_INC.relative_to(REPO_ROOT).as_posix(),
            "kT_over_q_at_300p15K_V": VT_300,
            "boltzmann_floor_mV_per_dec": S_IDEAL_MV_DEC}
