#!/usr/bin/env python3
"""
Phase C: passive R(V) and C(V) golden-curve regression.

For each behavioral resistor and capacitor in the PDK:

  * Resistors (5): RPOLY_HI, RPOLY_LO, RNWELL, RNPLUS, RPPLUS
        - drive Vp 0 with a DC source,
        - sweep Vp from -5 V to +5 V in 0.25 V steps,
        - extract R(V) = V / -i(Vp) (skipping V=0).

  * Capacitors (4): CMIM_STD, CMIM_HI, CMOM, CFRINGE
        - drive Vp 0 with a PWL ramp 0 -> 5 V over 1 ms (dV/dt = 5000 V/s),
        - run .tran,
        - extract C(V) = -i(Vp) / dV/dt at each transient sample.

Each (V, value) curve is interpolated onto a fixed comparison grid and
diffed against a stored golden in goldens/. Failure if the max relative
error exceeds --tol (default 1e-3).

Catches:
  * VCR/VCC coefficient drift (R/C bias dependence changes),
  * re-introduced abs() kinks (R(V) or C(V) would re-acquire a cusp at V=0),
  * unit-typo regressions on rsh/cj,
  * tempco-on-passives drift (run at T=27 only; tempco regressions show
    later when Phase D adds a temp sweep).

Usage:
  python run_passives.py                       # check goldens, exit non-zero on diff
  python run_passives.py --regenerate          # overwrite goldens from current lib
  python run_passives.py --device CMIM_STD     # restrict to listed devices
  python run_passives.py --tol 1e-4            # tighter relative tolerance

Env:
  NGSPICE_BIN     path to ngspice_con(.exe); auto-detected if unset
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
LIB_PATH = REPO_ROOT / "autohv_bicmos180_case.lib"
GOLDEN_DIR = HERE / "goldens"

# --- Devices -------------------------------------------------------------
# (name, type, params-string, comparison V-grid)
R_GRID = [round(-5.0 + 0.25 * i, 4) for i in range(41)]  # -5 to +5 step 0.25
C_GRID = [round(0.0 + 0.25 * i, 4) for i in range(21)]   #  0 to +5 step 0.25

PASSIVE_DEVICES = [
    ("RPOLY_HI", "r", "L=100u W=10u",  R_GRID),
    ("RPOLY_LO", "r", "L=100u W=10u",  R_GRID),
    ("RNWELL",   "r", "L=100u W=10u",  R_GRID),
    ("RNPLUS",   "r", "L=100u W=10u",  R_GRID),
    ("RPPLUS",   "r", "L=100u W=10u",  R_GRID),
    ("CMIM_STD", "c", "L=100u W=100u", C_GRID),
    ("CMIM_HI",  "c", "L=100u W=100u", C_GRID),
    ("CMOM",     "c", "L=100u W=100u", C_GRID),
    ("CFRINGE",  "c", "L=100u W=100u", C_GRID),
]

# --- Cap ramp parameters -------------------------------------------------
C_RAMP_VMIN = 0.0
C_RAMP_VMAX = 5.0
C_RAMP_TIME = 1e-3          # 1 ms
C_RAMP_DVDT = (C_RAMP_VMAX - C_RAMP_VMIN) / C_RAMP_TIME   # 5000 V/s
C_RAMP_TSTEP = 25e-6        # 25 us samples = 41 nominal points along ramp

# --- ngspice plumbing ----------------------------------------------------

def find_ngspice() -> str | None:
    cand = os.environ.get("NGSPICE_BIN")
    if cand and Path(cand).exists():
        return cand
    # On Windows the preferred batch binary is ngspice_con(.exe) (the
    # plain ngspice.exe opens a GUI/console window and doesn't stream
    # stdout). On Linux/macOS the binary is just `ngspice` and runs in
    # batch mode under -b.
    for name in ("ngspice_con", "ngspice_con.exe", "ngspice"):
        p = shutil.which(name)
        if p:
            return p
    for p in (
        r"C:\Spice64\bin\ngspice_con.exe",
        r"C:\Program Files\ngspice\bin\ngspice_con.exe",
    ):
        if Path(p).exists():
            return p
    return None


def lib_uri(lib_path: Path) -> str:
    return str(lib_path).replace("\\", "/")


def run_ngspice(ngspice: str, deck: str, out_path: Path) -> str:
    """Write the deck to a temp file, run ngspice -b, return stdout."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cir", delete=False, encoding="utf-8"
    ) as f:
        f.write(deck.replace("{OUT}", lib_uri(out_path)))
        deck_path = f.name
    try:
        res = subprocess.run(
            [ngspice, "-b", deck_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return (res.stdout or "") + "\n" + (res.stderr or "")
    finally:
        try:
            os.unlink(deck_path)
        except OSError:
            pass


def parse_wrdata(path: Path) -> list[list[float]]:
    """Parse ngspice wrdata ASCII output. Returns one list per row.

    wrdata format: for each requested vector v_i, columns are
    (scale, value) repeated. So with N vectors, each row has 2N cols.
    """
    rows: list[list[float]] = []
    with open(path, "r") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            try:
                rows.append([float(p) for p in parts])
            except ValueError:
                continue
    return rows


def interp_at(xs: list[float], ys: list[float], target_xs: list[float]) -> list[float]:
    """Linear interpolation. Inputs xs must be monotonic (asc or desc)."""
    if len(xs) < 2:
        raise ValueError("need >=2 points to interpolate")
    if xs[0] > xs[-1]:
        xs = xs[::-1]
        ys = ys[::-1]
    out: list[float] = []
    for tx in target_xs:
        if tx <= xs[0]:
            # extrapolate flat
            out.append(ys[0])
            continue
        if tx >= xs[-1]:
            out.append(ys[-1])
            continue
        # binary search
        lo, hi = 0, len(xs) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if xs[mid] <= tx:
                lo = mid
            else:
                hi = mid
        # linear between xs[lo], xs[hi]
        if xs[hi] == xs[lo]:
            out.append(ys[lo])
        else:
            f = (tx - xs[lo]) / (xs[hi] - xs[lo])
            out.append(ys[lo] + f * (ys[hi] - ys[lo]))
    return out


# --- Deck builders -------------------------------------------------------

R_DECK = """\
* Phase C: R(V) sweep for {name}
.include "{lib}"
.param case=0
.param PROC_ON=0
.param MM_ON=0
Vp p 0 1
X1 p 0 {name} {params}
.control
dc Vp -5 5 0.25
wrdata {{OUT}} v(p) i(Vp)
quit
.endc
.end
"""

C_DECK = """\
* Phase C: C(V) ramp for {name}
.include "{lib}"
.param case=0
.param PROC_ON=0
.param MM_ON=0
Vp p 0 PWL(0 0 {tramp:g} {vmax:g} 100m {vmax:g})
X1 p 0 {name} {params}
.control
tran {tstep:g} {tramp:g} 0 {tstep:g} UIC
wrdata {{OUT}} v(p) i(Vp)
quit
.endc
.end
"""


def measure_r(ngspice: str, name: str, params: str, lib: Path,
              out: Path) -> tuple[list[float], list[float]]:
    deck = R_DECK.format(name=name, params=params, lib=lib_uri(lib))
    stdout = run_ngspice(ngspice, deck, out)
    if "Error" in stdout or "no such function" in stdout:
        raise RuntimeError(
            f"ngspice errored for {name}: {stdout[-400:]!r}"
        )
    rows = parse_wrdata(out)
    if not rows:
        raise RuntimeError(f"no data rows produced for {name}")
    v_vals = [r[1] for r in rows]    # column index 1 = v(p)
    i_vals = [r[3] for r in rows]    # column index 3 = i(Vp)
    # Load current = -i(Vp); R(V) = V / load_current. Skip V=0.
    R: list[float] = []
    V_out: list[float] = []
    for v, i_vp in zip(v_vals, i_vals):
        if abs(v) < 1e-9:
            continue
        load_i = -i_vp
        if abs(load_i) < 1e-30:
            continue
        R.append(v / load_i)
        V_out.append(v)
    return V_out, R


def measure_c(ngspice: str, name: str, params: str, lib: Path,
              out: Path) -> tuple[list[float], list[float]]:
    deck = C_DECK.format(
        name=name, params=params, lib=lib_uri(lib),
        tramp=C_RAMP_TIME, vmax=C_RAMP_VMAX, tstep=C_RAMP_TSTEP,
    )
    stdout = run_ngspice(ngspice, deck, out)
    if "Error" in stdout or "no such function" in stdout:
        raise RuntimeError(
            f"ngspice errored for {name}: {stdout[-400:]!r}"
        )
    rows = parse_wrdata(out)
    if not rows:
        raise RuntimeError(f"no data rows produced for {name}")
    # Use only the ramp phase (t <= tramp). column 0 = time, 1 = v(p),
    # 2 = time (repeat), 3 = i(Vp).
    V_out: list[float] = []
    C_out: list[float] = []
    for r in rows:
        t = r[0]
        v = r[1]
        i_vp = r[3]
        if t > C_RAMP_TIME * 1.001:
            continue
        if v < C_RAMP_VMIN - 1e-6 or v > C_RAMP_VMAX + 1e-6:
            continue
        c_val = -i_vp / C_RAMP_DVDT
        V_out.append(v)
        C_out.append(c_val)
    return V_out, C_out


# --- Golden I/O ----------------------------------------------------------

def golden_path(name: str) -> Path:
    return GOLDEN_DIR / f"{name}.json"


def write_golden(name: str, kind: str, grid: list[float],
                 ys: list[float]) -> None:
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "device": name,
        "type": kind,
        "ngspice_version": "45.2",
        "v_grid": grid,
        "values": ys,
    }
    with open(golden_path(name), "w") as f:
        json.dump(data, f, indent=2)


def read_golden(name: str) -> dict | None:
    p = golden_path(name)
    if not p.exists():
        return None
    with open(p, "r") as f:
        return json.load(f)


# --- Comparison ----------------------------------------------------------

def max_rel_err(new_ys: list[float], gold_ys: list[float]) -> tuple[float, int]:
    """Returns (max_rel_err, index)."""
    worst = 0.0
    worst_i = -1
    for i, (n, g) in enumerate(zip(new_ys, gold_ys)):
        if g == 0:
            denom = max(abs(n), 1e-30)
        else:
            denom = abs(g)
        err = abs(n - g) / denom
        if err > worst:
            worst = err
            worst_i = i
    return worst, worst_i


# --- Main ----------------------------------------------------------------

def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--regenerate",
        action="store_true",
        help="overwrite goldens from current lib (use only when you trust the lib)",
    )
    p.add_argument(
        "--device",
        nargs="+",
        default=None,
        help="restrict to listed devices",
    )
    p.add_argument(
        "--tol",
        type=float,
        default=1e-3,
        help="max allowed relative error vs golden (default 1e-3 = 0.1%%)",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    ngspice = find_ngspice()
    if ngspice is None:
        print("ERROR: ngspice_con not found", file=sys.stderr)
        return 2
    if not LIB_PATH.exists():
        print(f"ERROR: lib not found at {LIB_PATH}", file=sys.stderr)
        return 2

    devices = PASSIVE_DEVICES
    if args.device:
        wanted = set(args.device)
        devices = [d for d in PASSIVE_DEVICES if d[0] in wanted]
        missing = wanted - {d[0] for d in devices}
        if missing:
            print(f"ERROR: unknown device(s): {sorted(missing)}", file=sys.stderr)
            return 2

    print(f"ngspice : {ngspice}")
    print(f"lib     : {LIB_PATH}")
    print(f"mode    : {'REGENERATE' if args.regenerate else 'check'}")
    print(f"tol     : {args.tol:.1e}  (relative)")
    print()

    fails: list[tuple[str, str]] = []
    n_regen = 0
    n_pass = 0
    # ngspice on Windows can't reliably wrdata to a UNC share path
    # (e.g. \\Mac\Home\...); use the local Windows temp dir.
    tmp_dir = Path(tempfile.gettempdir())
    out_data = tmp_dir / "autohv_passives_scratch.data"
    try:
        for name, kind, params, grid in devices:
            try:
                if out_data.exists():
                    out_data.unlink()
                if kind == "r":
                    raw_v, raw_y = measure_r(ngspice, name, params, LIB_PATH, out_data)
                else:
                    raw_v, raw_y = measure_c(ngspice, name, params, LIB_PATH, out_data)
            except Exception as e:
                fails.append((name, f"measurement error: {e}"))
                print(f"  {name:10s} ERR  {e}")
                continue

            if len(raw_v) < 4:
                fails.append((name, f"too few samples ({len(raw_v)})"))
                print(f"  {name:10s} ERR  too few samples")
                continue

            new_on_grid = interp_at(raw_v, raw_y, grid)

            if args.regenerate:
                write_golden(name, kind, grid, new_on_grid)
                n_regen += 1
                # quick stats so the user sees something sensible was written
                lo, hi = min(new_on_grid), max(new_on_grid)
                unit = "ohm" if kind == "r" else "F"
                print(f"  {name:10s} GOLD  {lo:.3e} .. {hi:.3e} {unit}  "
                      f"({len(grid)} pts)")
                continue

            gold = read_golden(name)
            if gold is None:
                fails.append((name, "no golden -- run with --regenerate first"))
                print(f"  {name:10s} MISS  no golden")
                continue
            if gold.get("v_grid") != grid:
                fails.append((name, "golden V-grid changed -- regenerate"))
                print(f"  {name:10s} GRID  golden V-grid stale")
                continue

            err, idx = max_rel_err(new_on_grid, gold["values"])
            if err <= args.tol:
                n_pass += 1
                print(f"  {name:10s} OK    max rel err {err:.2e} @ V={grid[idx]:+.2f}")
            else:
                fails.append((
                    name,
                    f"rel err {err:.3e} > tol {args.tol:.0e} "
                    f"@ V={grid[idx]:+.2f}: new={new_on_grid[idx]:.4e}, "
                    f"gold={gold['values'][idx]:.4e}"
                ))
                print(f"  {name:10s} FAIL  max rel err {err:.3e} "
                      f"@ V={grid[idx]:+.2f}  "
                      f"(new={new_on_grid[idx]:.4e}, gold={gold['values'][idx]:.4e})")
    finally:
        try:
            out_data.unlink()
        except OSError:
            pass

    print()
    if args.regenerate:
        print(f"Wrote {n_regen} goldens into {GOLDEN_DIR.relative_to(REPO_ROOT)}")
        return 0 if not fails else 1
    print(f"Passed: {n_pass}/{len(devices)}")
    if fails:
        print(f"Failed: {len(fails)}")
        for name, reason in fails:
            print(f"  {name}: {reason}")
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
