"""
Transmission-gate (CMOS switch) characterization framework, AutoHV BiCMOS 180 PDK.

Builds ngspice decks, drives ngspice, parses wrdata output.

Measurement principle
---------------------
The switch sits between node `a` (swept common-mode level) and node `b`.  A
floating source `Vb b a DV` pins b exactly DV above a, so the current it carries
IS the switch current and

    Ron(level) = DV / |I(Vb)|

with DV small enough (1 mV) that this is the incremental on-resistance at that
level.  Every switch variant in a deck shares node `a`, so one `.dc` sweep of Va
characterizes the whole width ladder at once -- the variants do not interact
because each `b_k` is held by its own ideal source.

Body configurations
-------------------
  srcbody : NMOS body -> a, PMOS body -> a   (Vsb = 0, best case)
  rail    : NMOS body -> gnd, PMOS body -> vdd (as shipped; body effect present)
"""
import os
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECK = HERE / "decks"
RESULTS = HERE / "results"
DECK.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

# decks/ -> transmission_gates/ -> circuits/ -> repo root
LIB = "../../../autohv_bicmos180_case.lib"

MODEL_TAG = "v2-grounded"


def _find_ngspice() -> str:
    cand = os.environ.get("NGSPICE_BIN")
    if cand and Path(cand).exists():
        return cand
    for name in ("ngspice_con", "ngspice_con.exe", "ngspice"):
        p = shutil.which(name)
        if p:
            return p
    for p in (
        r"C:\Program Files\Qucs-S-25.2.0-win64\bin\ngspice_con.exe",
        r"C:\Spice64\bin\ngspice_con.exe",
        r"C:\Program Files\ngspice\bin\ngspice_con.exe",
    ):
        if Path(p).exists():
            return p
    raise RuntimeError("ngspice not found; set NGSPICE_BIN.")


NGSPICE = _find_ngspice()
_NGVER = None


def ngspice_version() -> str:
    global _NGVER
    if _NGVER:
        return _NGVER
    _NGVER = "unknown"
    try:
        out = subprocess.run([NGSPICE, "--version"], capture_output=True,
                             text=True, timeout=30).stdout
        m = re.search(r"ngspice-?\s*[\d.]+", out, re.IGNORECASE)
        if m:
            _NGVER = m.group(0).replace(" ", "")
    except Exception:
        pass
    return _NGVER


def provenance(extra=None):
    d = {"model_tag": MODEL_TAG, "ngspice_version": ngspice_version()}
    if extra:
        d.update(extra)
    return d


# ---------------------------------------------------------------- domains
# Wmin/Lmin are the PDK fabrication minima (docs/geometry-minima.md) and are
# also the wrapper defaults.  Wmax/Mmax from pdk_validation/device_limits.csv.
# idc_dens is the DC current density rating (mA per um of drawn width).
DOMAINS = {
    "1v8": dict(n="NMOS1V8", p="PMOS1V8", vdd=1.80, Wmin=0.22, Lmin=0.18,
                Wmax=100.0, Mmax=1000, idc_dens=2.0, vgs_dcmax=2.0),
    "3v3": dict(n="NMOS3V3", p="PMOS3V3", vdd=3.30, Wmin=0.30, Lmin=0.35,
                Wmax=100.0, Mmax=1000, idc_dens=1.6, vgs_dcmax=3.6),
    "5v0": dict(n="NMOS5V0", p="PMOS5V0", vdd=5.00, Wmin=0.40, Lmin=0.50,
                Wmax=100.0, Mmax=1000, idc_dens=1.2, vgs_dcmax=5.5),
}

CNAME = {0: "TT", 1: "FF", 2: "SS", 3: "FS", 4: "SF"}
CORNERS = [0, 1, 2, 3, 4]
TEMPS = [-55, 27, 150]          # -55 C is below the model Tj_min of -40 C
VTOL = 0.10                     # supply tolerance, +/-10 %

DV = 1e-3                       # differential probe voltage across the switch (V)
NPTS = 101                      # points in the input-level sweep

_ENV = dict(os.environ, OMP_WAIT_POLICY="passive", OMP_DYNAMIC="false")


def vlist(dom):
    """Supply corners at +/-VTOL."""
    v = DOMAINS[dom]["vdd"]
    return [round(v * (1 - VTOL), 4), v, round(v * (1 + VTOL), 4)]


def split_wm(wtot, dom):
    """Split a total drawn width into (W per finger, M) inside the fab window."""
    d = DOMAINS[dom]
    if wtot <= d["Wmax"]:
        return wtot, 1
    m = int(-(-wtot // d["Wmax"]))          # ceil
    if m > d["Mmax"]:
        raise ValueError(f"{wtot} um exceeds Wmax*Mmax for {dom}")
    return wtot / m, m


# ---------------------------------------------------------------- deck build
def switch_inst(tag, dom, wn, wp, body, extra_l=None):
    """One transmission gate from `a` to `b_<tag>`, gates ideally driven.

    body: 'srcbody' -> both wells on node a;  'rail' -> NMOS to 0, PMOS to vdd.
    """
    d = DOMAINS[dom]
    L = extra_l if extra_l is not None else d["Lmin"]
    wn_f, mn = split_wm(wn, dom)
    wp_f, mp = split_wm(wp, dom)
    bn, bp = ("a", "a") if body == "srcbody" else ("0", "vdd")
    b = f"b_{tag}"
    s = [
        f"Vb_{tag} {b} a {DV}",
        f"XN_{tag} {b} en  a {bn} {d['n']} W={wn_f:.6g}u L={L:.6g}u M={mn}",
        f"XP_{tag} {b} enb a {bp} {d['p']} W={wp_f:.6g}u L={L:.6g}u M={mp}",
    ]
    return "\n".join(s)


def level_sweep_deck(title, dom, variants, body, case=0, temp=27, vdd=None,
                     outfile="out.txt", proc_on=0, mm_on=0):
    """Deck: sweep the switch common-mode level 0..vdd, report Ron per variant.

    variants: list of (tag, wn_um, wp_um) or (tag, wn_um, wp_um, L_um).
    """
    d = DOMAINS[dom]
    v = d["vdd"] if vdd is None else vdd
    step = v / (NPTS - 1)
    lines = [
        f".title {title}",
        f'.include "{LIB}"',
        f".param case={case}",
        f".param PROC_ON={proc_on}",
        f".param MM_ON={mm_on}",
        ".option num_threads=1",
        f"Vdd  vdd 0 {v:.6g}",
        f"Ven  en  0 {v:.6g}",
        "Venb enb 0 0",
        "Va   a   0 0",
    ]
    tags = []
    for spec in variants:
        tag, wn, wp = spec[0], spec[1], spec[2]
        L = spec[3] if len(spec) > 3 else None
        lines.append(switch_inst(tag, dom, wn, wp, body, extra_l=L))
        tags.append(tag)
    lines += [
        ".control",
        f"option temp={temp}",
        f"dc Va 0 {v:.6g} {step:.8g}",
    ]
    for t in tags:
        lines.append(f"let ron_{t} = {DV}/abs(i(vb_{t}))")
    lines.append("wrdata " + outfile + " " + " ".join(f"ron_{t}" for t in tags))
    lines += [".endc", ".end", ""]
    return "\n".join(lines)


def run_deck(text, tag, timeout=1800):
    path = DECK / (tag + ".cir")
    path.write_text(text, newline="\n")
    r = subprocess.run([NGSPICE, "-b", path.name], cwd=str(DECK),
                       capture_output=True, text=True, timeout=timeout, env=_ENV)
    return r.stdout + "\n" + r.stderr


def read_wrdata(path, ncols):
    """wrdata writes x,y pairs per vector: x1 y1 x2 y2 ...  Returns (xs, [ys...])."""
    xs, cols = [], [[] for _ in range(ncols)]
    for ln in Path(path).read_text().splitlines():
        t = ln.split()
        if len(t) < 2 * ncols:
            continue
        try:
            vals = [float(x) for x in t]
        except ValueError:
            continue
        xs.append(vals[0])
        for k in range(ncols):
            cols[k].append(vals[2 * k + 1])
    return xs, cols
