#!/usr/bin/env python3
"""
Shared infrastructure for the AutoHV BiCMOS180 characterization harness (phase 2).

Responsibilities
  * locate and invoke ngspice, recording the exact version string
  * template decks, write them to decks/ (committed for auditability), run them
  * parse ngspice batch output: `print` lines, `.meas` results, wrdata tables
  * Monte Carlo driver that spawns ONE PROCESS PER SAMPLE
  * a Measurement record type carrying provenance

Methodological conventions follow circuits/current_mirror_char/ (the repo's
high-water mark per characterization-inventory.md):
  - ideal sources are labelled as instruments in the deck header
  - every number carries provenance: which deck, which conditions
  - [measured] = read from a simulator output
    [derived]  = computed from one or more [measured] values

MONTE CARLO WARNING (characterization-inventory.md 6.5 #22):
ngspice re-randomizes `.param AGAUSS` draws only ACROSS `-b` invocations.
`.param` is parsed before the `.control` block, so `set rndseed` cannot reach
it and `-D rndseed=N` is silently ignored. A loop of `reset`/`op` inside ONE
invocation yields IDENTICAL samples. mc_run() therefore spawns a subprocess per
sample and asserts non-degeneracy before returning.

Read-only with respect to the PDK: nothing here writes to
autohv_bicmos180_case.lib or autohv_bicmos180_case_models.inc.
"""
from __future__ import annotations

import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

HERE = Path(__file__).resolve().parent          # pdk_validation/characterization
REPO_ROOT = HERE.parents[1]                     # repo root
LIB_PATH = REPO_ROOT / "autohv_bicmos180_case.lib"
DECKS_DIR = HERE / "decks"
RESULTS_DIR = HERE / "results"
LOCAL_MODELS_DIR = RESULTS_DIR / "local_models"
ANCHOR_PATH = REPO_ROOT / "docs" / "anchor-values.json"

# ngspice batch timeout per invocation (seconds). Generous: some VDMOS
# transients are slow, but nothing here should approach it.
DEFAULT_TIMEOUT = 120

_NG_BIN: str | None = None
_NG_VERSION: str | None = None

# Physical constants (SI unless noted)
Q = 1.602176634e-19
K_B = 1.380649e-23
EPS0 = 8.854187817e-12
EPS_OX = 3.9 * EPS0
EPS_SI = 11.7 * EPS0
T300 = 300.15


# --------------------------------------------------------------------------
# ngspice discovery and invocation
# --------------------------------------------------------------------------

def find_ngspice() -> str:
    """Locate the ngspice batch binary.

    Order: $NGSPICE_BIN, PATH, then known Windows install locations. On
    Windows use ngspice_con.exe -- plain ngspice.exe is the GUI/console
    variant which does not stream stdout back to the caller (the harness
    would see no output and time out as if the run hung).
    """
    global _NG_BIN
    if _NG_BIN:
        return _NG_BIN
    cand = os.environ.get("NGSPICE_BIN")
    if cand and Path(cand).exists():
        _NG_BIN = cand
        return _NG_BIN
    for name in ("ngspice_con", "ngspice_con.exe", "ngspice"):
        p = shutil.which(name)
        if p:
            _NG_BIN = p
            return _NG_BIN
    for p in (
        r"C:\Program Files\Qucs-S-25.2.0-win64\bin\ngspice_con.exe",
        r"C:\Spice64\bin\ngspice_con.exe",
        r"C:\Program Files\ngspice\bin\ngspice_con.exe",
    ):
        if Path(p).exists():
            _NG_BIN = p
            return _NG_BIN
    raise RuntimeError(
        "ngspice not found. Set NGSPICE_BIN to the ngspice_con(.exe) path."
    )


def ngspice_version() -> str:
    """Exact version banner line, recorded in the results file."""
    global _NG_VERSION
    if _NG_VERSION:
        return _NG_VERSION
    out = subprocess.run(
        [find_ngspice(), "--version"], capture_output=True, text=True, timeout=30
    ).stdout
    for line in out.splitlines():
        if "ngspice" in line.lower() and "circuit level" in line.lower():
            _NG_VERSION = line.strip().lstrip("*").strip()
            return _NG_VERSION
    _NG_VERSION = out.strip().splitlines()[0] if out.strip() else "unknown"
    return _NG_VERSION


def lib_include(local_model: Path | None = None) -> str:
    """The .include block every deck starts with.

    If local_model is given (a discrimination-experiment isolation copy),
    it is included AFTER the PDK so its .model card shadows the original.
    """
    s = f'.include "{LIB_PATH.as_posix()}"\n'
    if local_model is not None:
        s += f'.include "{Path(local_model).as_posix()}"\n'
    return s


def run_deck(
    deck: str,
    name: str,
    subdir: str = "",
    timeout: int = DEFAULT_TIMEOUT,
    keep: bool = True,
) -> tuple[str, float]:
    """Write a deck to decks/<subdir>/<name>.cir, run it, return (stdout, wall_s).

    Decks are committed for auditability, so every number in the results
    file can be traced to a standalone re-runnable deck:
        ngspice -b pdk_validation/characterization/decks/<subdir>/<name>.cir
    """
    d = DECKS_DIR / subdir if subdir else DECKS_DIR
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{name}.cir"
    path.write_text(deck, encoding="utf-8", newline="\n")
    t0 = time.time()
    try:
        proc = subprocess.run(
            [find_ngspice(), "-b", str(path)],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(d),
        )
        out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    except subprocess.TimeoutExpired:
        out = f"__HARNESS_TIMEOUT__ after {timeout}s"
    return out, time.time() - t0


def deck_path(name: str, subdir: str = "") -> str:
    """Repo-relative deck path, for the provenance field."""
    d = DECKS_DIR / subdir if subdir else DECKS_DIR
    return (d / f"{name}.cir").relative_to(REPO_ROOT).as_posix()


# --------------------------------------------------------------------------
# output parsing
# --------------------------------------------------------------------------

_NUM = r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?"


def parse_prints(out: str) -> dict[str, float]:
    """Parse `print a b c` output lines of the form `name = value`.

    ngspice prints one `name = value` per line for scalars. Vector prints
    are handled by parse_table().
    """
    res: dict[str, float] = {}
    for m in re.finditer(rf"^\s*([\w.#@\[\]$:()]+)\s*=\s*({_NUM})\s*$", out, re.M):
        try:
            res[m.group(1).lower()] = float(m.group(2))
        except ValueError:
            pass
    return res


def parse_meas(out: str) -> dict[str, float]:
    """Parse `.meas`/`meas` result lines: `name = value` possibly with trailing text."""
    res: dict[str, float] = {}
    for m in re.finditer(rf"^\s*([\w.#$]+)\s*=\s*({_NUM})", out, re.M):
        res.setdefault(m.group(1).lower(), float(m.group(2)))
    return res


def parse_table(out: str, begin: str, end: str) -> list[list[float]]:
    """Parse a whitespace-numeric table echoed between two markers.

    Decks emit sweeps via
        echo <BEGIN>
        print vec1 vec2 ...
        echo <END>
    ngspice's multi-vector `print` emits an index column then the vectors.
    Rows that do not parse as all-floats (headers, blanks) are skipped.
    """
    seg = out.split(begin, 1)
    if len(seg) < 2:
        return []
    seg = seg[1].split(end, 1)[0]
    rows: list[list[float]] = []
    for line in seg.splitlines():
        parts = line.split()
        if not parts:
            continue
        try:
            vals = [float(p) for p in parts]
        except ValueError:
            continue
        if len(vals) >= 2:
            rows.append(vals)
    return rows


def parse_dc_sweep(out: str, nvec: int = 1, begin: str = "TBL_BEGIN",
                   end: str = "TBL_END") -> tuple[list[float], list[list[float]]]:
    """Parse a `.dc` sweep printed between markers.

    ngspice emits one row per point as:  index  sweepvar  vec1 [vec2 ...]
    So DO NOT `print` the sweep variable itself -- it is already column 1 and
    printing it again shifts every subsequent column. Decks should emit only
    the dependent vectors:

        dc Vg 0 1.8 0.02
        echo TBL_BEGIN
        print abs(i(Vd))          <-- one vector -> nvec=1
        echo TBL_END

    Returns (sweep_values, [vec1_values, vec2_values, ...]).
    """
    rows = parse_table(out, begin, end)
    xs: list[float] = []
    cols: list[list[float]] = [[] for _ in range(nvec)]
    for r in rows:
        if len(r) < 2 + nvec:
            continue
        xs.append(r[1])
        for k in range(nvec):
            cols[k].append(r[2 + k])
    return xs, cols


def ngspice_errored(out: str) -> str | None:
    """Return a short reason string if the run failed, else None."""
    if "__HARNESS_TIMEOUT__" in out:
        return "timeout"
    for pat in (
        r"^\s*Error[: ]", r"no such function", r"singular matrix",
        r"iteration limit reached", r"unknown subckt", r"unknown parameter",
        r"Timestep too small", r"doAnalyses: TRAN:  Timestep too small",
    ):
        m = re.search(pat, out, re.M | re.I)
        if m:
            return m.group(0).strip()[:80]
    return None


# --------------------------------------------------------------------------
# measurement record
# --------------------------------------------------------------------------

@dataclass
class Measurement:
    device: str
    fom: str
    value: float | None
    units: str
    tag: str                      # "measured" | "derived"
    conditions: dict[str, Any] = field(default_factory=dict)
    deck: str | None = None
    note: str = ""
    error: str | None = None
    sigma_convention: str = "n/a"

    def as_dict(self) -> dict:
        return asdict(self)


class Collector:
    """Accumulates Measurements and experiment payloads for one run."""

    def __init__(self) -> None:
        self.items: list[Measurement] = []
        self.experiments: dict[str, Any] = {}
        self.errors: list[dict] = []

    def add(self, m: Measurement) -> None:
        self.items.append(m)
        if m.error:
            self.errors.append({"device": m.device, "fom": m.fom, "error": m.error})

    def measured(self, device, fom, value, units, conditions=None, deck=None,
                 note="", error=None, sigma="n/a") -> None:
        self.add(Measurement(device, fom, value, units, "measured",
                             conditions or {}, deck, note, error, sigma))

    def derived(self, device, fom, value, units, conditions=None, deck=None,
                note="", error=None, sigma="n/a") -> None:
        self.add(Measurement(device, fom, value, units, "derived",
                             conditions or {}, deck, note, error, sigma))

    def to_json(self) -> dict:
        by_dev: dict[str, dict] = {}
        for m in self.items:
            by_dev.setdefault(m.device, {})[m.fom] = m.as_dict()
        return {"devices": by_dev, "_experiments": self.experiments,
                "_errors": self.errors}


# --------------------------------------------------------------------------
# extraction helpers
# --------------------------------------------------------------------------

def vth_max_gm(vg: Sequence[float], idr: Sequence[float]) -> tuple[float, float]:
    """Threshold by max-gm linear extrapolation (the standard MOS method).

    Find the point of maximum dId/dVg, fit the tangent there, and take its
    Vg-axis intercept. Returns (vth, gm_max). Caller supplies a LOW-Vds
    sweep so the linear-region assumption holds.
    """
    if len(vg) < 5:
        return float("nan"), float("nan")
    best_i, best_g = 1, -1.0
    for i in range(1, len(vg) - 1):
        g = (idr[i + 1] - idr[i - 1]) / (vg[i + 1] - vg[i - 1])
        if g > best_g:
            best_g, best_i = g, i
    # tangent at best_i: Id = g*(Vg - Vth)  ->  Vth = Vg - Id/g
    if best_g <= 0:
        return float("nan"), float("nan")
    return vg[best_i] - idr[best_i] / best_g, best_g


def subthreshold_slope(vg: Sequence[float], idr: Sequence[float],
                       decades_min: float = 2.0
                       ) -> tuple[float, tuple[float, float], float]:
    """Fit S in mV/decade over the widest clean subthreshold window.

    Returns (S_mV_per_dec, (vg_lo, vg_hi), decades_fitted). Selects the
    window by scanning for the longest run of monotonically rising log10(Id)
    below the max-gm threshold, then least-squares fits log10(Id) vs Vg.
    Returns nan if fewer than `decades_min` decades are available.
    """
    pts = [(v, i) for v, i in zip(vg, idr) if i > 0]
    if len(pts) < 5:
        return float("nan"), (float("nan"), float("nan")), 0.0
    lv = [(v, math.log10(i)) for v, i in pts]
    # Use the lower half of the log-current span: that is subthreshold.
    lo_l, hi_l = lv[0][1], lv[-1][1]
    span = hi_l - lo_l
    if span < decades_min:
        return float("nan"), (float("nan"), float("nan")), span
    target_hi = lo_l + 0.75 * span
    win = [p for p in lv if p[1] <= target_hi]
    # trim the very bottom (numerical floor / leakage plateau)
    if len(win) > 6:
        win = win[1:]
    if len(win) < 4:
        return float("nan"), (float("nan"), float("nan")), span
    dec = win[-1][1] - win[0][1]
    if dec < decades_min:
        return float("nan"), (win[0][0], win[-1][0]), dec
    n = len(win)
    sx = sum(p[0] for p in win); sy = sum(p[1] for p in win)
    sxx = sum(p[0] * p[0] for p in win); sxy = sum(p[0] * p[1] for p in win)
    den = n * sxx - sx * sx
    if abs(den) < 1e-30:
        return float("nan"), (win[0][0], win[-1][0]), dec
    slope = (n * sxy - sx * sy) / den          # decades per volt
    if slope <= 0:
        return float("nan"), (win[0][0], win[-1][0]), dec
    return 1000.0 / slope, (win[0][0], win[-1][0]), dec


def linfit(x: Sequence[float], y: Sequence[float]) -> tuple[float, float]:
    """Least-squares slope, intercept."""
    n = len(x)
    if n < 2:
        return float("nan"), float("nan")
    sx = sum(x); sy = sum(y); sxx = sum(a * a for a in x)
    sxy = sum(a * b for a, b in zip(x, y))
    den = n * sxx - sx * sx
    if abs(den) < 1e-30:
        return float("nan"), float("nan")
    slope = (n * sxy - sx * sy) / den
    return slope, (sy - slope * sx) / n


def cap_from_ac(i_mag: float, freq: float, vac: float = 1.0) -> float:
    """C = |I| / (2*pi*f*Vac) from a 1 V AC probe. [derived]"""
    return abs(i_mag) / (2.0 * math.pi * freq * vac)


def tempco_ppm(v_lo: float, v_27: float, v_hi: float,
               t_lo: float = -40.0, t_hi: float = 150.0) -> float:
    """Linear tempco in ppm/degC from three temperature points. [derived]

    Uses the full -40..150 span (the proposed automotive qualification range)
    rather than a local derivative, matching how tc1 is specified.
    """
    if v_27 == 0 or any(math.isnan(v) for v in (v_lo, v_27, v_hi)):
        return float("nan")
    return (v_hi - v_lo) / (t_hi - t_lo) / v_27 * 1e6


# --------------------------------------------------------------------------
# Monte Carlo
# --------------------------------------------------------------------------

@dataclass
class MCResult:
    n: int
    seed_note: str
    samples: list[dict[str, float]]
    degenerate: bool
    deck: str

    def series(self, key: str) -> list[float]:
        return [s[key] for s in self.samples if key in s and
                not math.isnan(s.get(key, float("nan")))]

    def sigma(self, key: str) -> float:
        v = self.series(key)
        return statistics.stdev(v) if len(v) > 2 else float("nan")

    def mean(self, key: str) -> float:
        v = self.series(key)
        return statistics.fmean(v) if v else float("nan")


def mc_run(deck_fn: Callable[[int], str], name: str, n: int,
           extract: Callable[[str], dict[str, float]],
           subdir: str = "mc", timeout: int = DEFAULT_TIMEOUT) -> MCResult:
    """Monte Carlo: ONE ngspice PROCESS PER SAMPLE.

    This is mandatory, not an optimization. `.param AGAUSS` is evaluated at
    parse time, so a loop inside one invocation re-uses a single draw and
    every sample comes out identical (inventory 6.5 #22). We verify
    non-degeneracy on the way out and flag it loudly if it trips.

    Seeding: ngspice time-seeds its RNG per invocation and offers no way to
    set the seed for `.param AGAUSS` (-D rndseed is silently ignored). So
    runs are NOT bit-reproducible; we record that fact rather than pretend.
    """
    samples: list[dict[str, float]] = []
    dpath = deck_path(f"{name}_s0", subdir)
    for i in range(n):
        deck = deck_fn(i)
        out, _ = run_deck(deck, f"{name}_s{i}", subdir, timeout=timeout,
                          keep=(i == 0))
        if i > 0:
            # keep only sample 0 on disk; the rest are identical modulo the
            # RNG draw and would be 200 near-duplicate files per device
            p = (DECKS_DIR / subdir / f"{name}_s{i}.cir")
            try:
                p.unlink()
            except OSError:
                pass
        vals = extract(out)
        if vals:
            samples.append(vals)
    # Degeneracy check, RELATIVE not absolute.
    # An earlier version compared round(v, 15), an absolute 1e-15 quantum.
    # Farad-scale values (~1e-13) all collapse to the same rounded number, so a
    # perfectly healthy MC run was flagged degenerate. Compare spread against
    # magnitude instead, so the check is unit-free.
    degenerate = False
    if len(samples) > 2:
        for key in samples[0]:
            vals = [s[key] for s in samples
                    if key in s and s[key] is not None
                    and not math.isnan(s[key])]
            if len(vals) < 3:
                continue
            scale = max(abs(v) for v in vals)
            spread = max(vals) - min(vals)
            if scale == 0.0 or spread <= 1e-12 * scale:
                degenerate = True
                break
    return MCResult(n=len(samples),
                    seed_note=("ngspice time-seeds .param AGAUSS per -b "
                               "invocation; no settable seed exists "
                               "(-D rndseed does not reach .param). "
                               "Runs are not bit-reproducible."),
                    samples=samples, degenerate=degenerate, deck=dpath)


# --------------------------------------------------------------------------
# local model copies for discrimination experiments
# --------------------------------------------------------------------------

def write_local_model(name: str, source_card: str, body: str, delta: str) -> Path:
    """Write a testbench-local .model copy with a documented single change.

    Per the phase-2 brief these are tightly scoped: they live under
    results/local_models/, name their source card and the delta in a header,
    and are never .include'd by anything outside their own experiment.

    *** SHADOWING DOES NOT WORK -- READ THIS BEFORE USING. ***
    An earlier version of this docstring claimed that including the copy AFTER
    the PDK makes it shadow the original card. It does not. ngspice-45 keeps
    the FIRST definition of a given model name and silently discards any later
    one, with no warning. A deck that includes the PDK and then a second
    `.model NDMOS200_INT ...` still reads back the PDK's parameters.

    Anything relying on shadowing would silently run on stock cards while
    reporting that it had changed them. The working pattern, implemented in
    experiments/exp_lib.py, is:

        1. give the copy a DISTINCT model name (e.g. NDMOS200_INT_D3)
        2. instantiate that model raw, bypassing the PDK subckt wrapper
        3. prove the bypass is equivalent (wrapper_equivalence_check) rather
           than assuming it
        4. read the changed parameter back through ngspice (@MODEL[param]) to
           prove the edit actually landed

    Also note: exactly rd=0/rs=0 will not converge on a VDMOS card (gmin and
    source stepping both fail, then "Timestep too small"). Use 1e-9 -- nine
    orders below the carded values and electrically irrelevant.
    """
    LOCAL_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    p = LOCAL_MODELS_DIR / f"{name}.mod"
    hdr = (
        f"* ISOLATION COPY -- discrimination experiment only.\n"
        f"* Source card : {source_card} "
        f"(autohv_bicmos180_case_models.inc)\n"
        f"* Delta       : {delta}\n"
        f"* NOT part of the PDK. Never .include this outside its experiment.\n"
        f"* The model name is DISTINCT from the source card: ngspice keeps the\n"
        f"* first definition of a name, so shadowing is impossible. This card\n"
        f"* must be instantiated directly, not via the PDK subckt wrapper.\n"
    )
    p.write_text(hdr + body, encoding="utf-8", newline="\n")
    return p


# --------------------------------------------------------------------------
# anchors
# --------------------------------------------------------------------------

def load_anchors() -> dict:
    with open(ANCHOR_PATH, encoding="utf-8") as f:
        return json.load(f)


def corner_names() -> list[str]:
    return ["TT", "FF", "SS", "FS", "SF"]


CORNER_CASE = {"TT": 0, "FF": 1, "SS": 2, "FS": 3, "SF": 4}


def header(title: str, instruments: str = "", case: int = 0,
           proc: int = 0, mm: int = 0, temp: float | None = None,
           local_model: Path | None = None) -> str:
    """Standard deck preamble.

    `instruments` documents which sources are ideal measurement instruments
    rather than part of a circuit under test -- the convention borrowed from
    circuits/current_mirror_char/MIRROR_CHAR.md.
    """
    s = f"* {title}\n"
    s += "* Generated by pdk_validation/characterization -- phase 2 harness.\n"
    if instruments:
        s += f"* Instruments (ideal, not DUT): {instruments}\n"
    s += "* Re-run standalone:  ngspice -b <this file>\n"
    s += lib_include(local_model)
    s += f".param case={case}\n.param PROC_ON={proc}\n.param MM_ON={mm}\n"
    if temp is not None:
        s += f".options temp={temp}\n"
    return s
