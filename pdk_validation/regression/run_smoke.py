#!/usr/bin/env python3
"""
Phase A smoke regression for the AutoHV BiCMOS 180 PDK.

For each of the 38 .subckt devices defined in autohv_bicmos180_case.lib,
generate a minimal deck biasing it, run ngspice in batch, and require:
  * the deck reaches the SMOKE_OK marker (op converged), and
  * ngspice prints no fatal-error patterns.

Sweeps the full corner * statistics matrix by default:
  case        in {0,1,2,3,4}        (TT, FF, SS, FS, SF)
  PROC_ON     in {0,1}              (die-to-die process variation)
  MM_ON       in {0,1}              (local mismatch)
Total:  38 * 5 * 4 = 760 ops.

Pinned to ngspice-45.2 (the version P0 was developed against).

Usage:
  python run_smoke.py                 # full matrix (760 ops)
  python run_smoke.py --quick         # case=0 + (PROC,MM)=(1,1) only (38 ops)
  python run_smoke.py --device NDMOS20 PDMOS40   # only listed devices
  python run_smoke.py --jobs 4        # parallel workers (default 1)

Env:
  NGSPICE_BIN     path to ngspice_con(.exe); auto-detected if unset
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB_PATH = REPO_ROOT / "autohv_bicmos180_case.lib"
TARGET_NGSPICE = "45.2"

CORNERS = [0, 1, 2, 3, 4]
STAT_COMBOS = [(0, 0), (0, 1), (1, 0), (1, 1)]  # (PROC_ON, MM_ON)

DEVICES = [
    ("NMOS18",   "bsim_n",    ""),
    ("PMOS18",   "bsim_p",    ""),
    ("NMOS33",   "bsim_n",    ""),
    ("PMOS33",   "bsim_p",    ""),
    ("NMOS50",   "bsim_n",    ""),
    ("PMOS50",   "bsim_p",    ""),
    ("NMOS12",   "bsim_n",    ""),
    ("PMOS12",   "bsim_p",    ""),
    ("NDMOS20",  "vdmos_n",   ""),
    ("PDMOS20",  "vdmos_p",   ""),
    ("NDMOS40",  "vdmos_n",   ""),
    ("PDMOS40",  "vdmos_p",   ""),
    ("NDMOS60",  "vdmos_n",   ""),
    ("PDMOS60",  "vdmos_p",   ""),
    ("NDMOS80",  "vdmos_n",   ""),
    ("PDMOS80",  "vdmos_p",   ""),
    ("NDMOS120", "vdmos_n",   ""),
    ("PDMOS120", "vdmos_p",   ""),
    ("NDMOS200", "vdmos_n",   "L=8u"),
    ("PDMOS200", "vdmos_p",   "L=8u"),
    ("DNMOS20",  "vdmos_dep", ""),
    ("NPN_LV",   "npn",       ""),
    ("PNP_LAT",  "pnp",       ""),
    ("NPN_HV",   "npn",       ""),
    ("PNP_HV",   "pnp",       ""),
    ("DIO_PN",   "dio",       ""),
    ("DIO_FAST", "dio",       ""),
    ("DIO_SCH",  "dio",       ""),
    ("DZ_5V6",   "dio",       ""),
    ("DZ_12",    "dio",       ""),
    ("DZ_24",    "dio",       ""),
    ("RPOLY_HI", "r",         ""),
    ("RPOLY_LO", "r",         ""),
    ("RNWELL",   "r",         ""),
    ("RNPLUS",   "r",         ""),
    ("RPPLUS",   "r",         ""),
    ("CMIM_STD", "c",         ""),
    ("CMIM_HI",  "c",         ""),
    ("CMOM",     "c",         ""),
    ("CFRINGE",  "c",         ""),
]
assert len(DEVICES) == 40, "device count drifted from the .lib"


def make_instance(name: str, klass: str, extra: str) -> list[str]:
    """SPICE lines for a minimal one-device test circuit (sources + X line)."""
    extra = f" {extra}" if extra else ""
    if klass == "bsim_n":
        return [
            "Vd d 0 3",
            "Vg g 0 2.5",
            f"X1 d g 0 0 {name} W=10u L=1u M=1{extra}",
        ]
    if klass == "bsim_p":
        return [
            "Vd d 0 -3",
            "Vg g 0 -2.5",
            f"X1 d g 0 0 {name} W=10u L=1u M=1{extra}",
        ]
    if klass == "vdmos_n":
        return [
            "Vd d 0 3",
            "Vg g 0 2.5",
            f"X1 d g 0 {name} W=10u M=1{extra}",
        ]
    if klass == "vdmos_p":
        return [
            "Vd d 0 -3",
            "Vg g 0 -2.5",
            f"X1 d g 0 {name} W=10u M=1{extra}",
        ]
    if klass == "vdmos_dep":
        # depletion device: on at Vgs=0
        return [
            "Vd d 0 3",
            "Vg g 0 0",
            f"X1 d g 0 {name} W=10u M=1{extra}",
        ]
    if klass == "npn":
        return [
            "Vc c 0 1",
            "Vb b 0 0.7",
            "Ve e 0 0",
            f"X1 c b e {name} AREA=1{extra}",
        ]
    if klass == "pnp":
        return [
            "Vc c 0 -1",
            "Vb b 0 -0.7",
            "Ve e 0 0",
            f"X1 c b e {name} AREA=1{extra}",
        ]
    if klass == "dio":
        return [
            "Va a 0 0.7",
            f"X1 a 0 {name} AREA=1{extra}",
        ]
    if klass == "r":
        return [
            "Vp p 0 1",
            f"X1 p 0 {name} L=100u W=10u{extra}",
        ]
    if klass == "c":
        # DC op only: cap is open; just ensure parse + op convergence.
        return [
            "Vp p 0 1",
            f"X1 p 0 {name} L=100u W=100u{extra}",
        ]
    raise ValueError(f"unknown device class {klass!r}")


DECK_TEMPLATE = """\
* P1 Phase-A smoke: {name} case={case} PROC_ON={proc} MM_ON={mm}
.include "{lib}"
.param case={case}
.param PROC_ON={proc}
.param MM_ON={mm}
{instance}
.control
op
echo SMOKE_OK
quit
.endc
.end
"""

ERROR_PATTERNS = [
    re.compile(r"^\s*Error[: ]", re.MULTILINE | re.IGNORECASE),
    re.compile(r"no such function", re.IGNORECASE),
    re.compile(r"singular matrix", re.IGNORECASE),
    re.compile(r"iteration limit reached", re.IGNORECASE),
    re.compile(r"too many subckts", re.IGNORECASE),
    re.compile(r"unknown subckt", re.IGNORECASE),
    re.compile(r"unknown parameter", re.IGNORECASE),
]


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


def run_one(
    ngspice: str,
    lib_path: Path,
    name: str,
    klass: str,
    extra: str,
    case: int,
    proc: int,
    mm: int,
) -> tuple[bool, str, float]:
    """Returns (ok, reason, elapsed_seconds)."""
    instance = "\n".join(make_instance(name, klass, extra))
    deck = DECK_TEMPLATE.format(
        name=name,
        case=case,
        proc=proc,
        mm=mm,
        lib=str(lib_path).replace("\\", "/"),
        instance=instance,
    )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cir", delete=False, encoding="utf-8"
    ) as f:
        f.write(deck)
        deck_path = f.name
    t0 = time.monotonic()
    try:
        res = subprocess.run(
            [ngspice, "-b", deck_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        out = (res.stdout or "") + "\n" + (res.stderr or "")
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT (>60s)", time.monotonic() - t0
    finally:
        try:
            os.unlink(deck_path)
        except OSError:
            pass

    elapsed = time.monotonic() - t0

    for pat in ERROR_PATTERNS:
        m = pat.search(out)
        if m:
            # grab the matched line + a little context
            line_start = out.rfind("\n", 0, m.start()) + 1
            line_end = out.find("\n", m.end())
            if line_end < 0:
                line_end = len(out)
            line = out[line_start:line_end].strip()
            return False, f"{line[:160]}", elapsed

    if "SMOKE_OK" not in out:
        return False, "no SMOKE_OK marker (op did not complete)", elapsed
    return True, "", elapsed


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "--quick",
        action="store_true",
        help="case=0, (PROC,MM)=(1,1) only (38 ops, ~1 min)",
    )
    p.add_argument(
        "--device",
        nargs="+",
        default=None,
        help="restrict to a subset of devices (by name)",
    )
    p.add_argument(
        "--jobs",
        "-j",
        type=int,
        default=1,
        help="parallel worker count (default 1; raise to 4-8 on idle laptop)",
    )
    p.add_argument(
        "--max-op-secs",
        type=float,
        default=4.0,
        help=(
            "per-op wall-time budget in seconds (default 4.0; bumped from "
            "2.0 in 2026-05-29 to absorb the ~200 ms parse overhead from "
            "the 13 VDMOS .if (SH_ON==1) self-heating blocks). An op that "
            "converges but exceeds the budget is reported as a failure -- "
            "catches convergence/stiffness regressions like the pre-fix "
            "abs() kink (>120 s on a passive transient). Disable "
            "with --max-op-secs 0."
        ),
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    ngspice = find_ngspice()
    if ngspice is None:
        print(
            "ERROR: ngspice_con not found. Set NGSPICE_BIN or add it to PATH.",
            file=sys.stderr,
        )
        return 2
    if not LIB_PATH.exists():
        print(f"ERROR: lib not found at {LIB_PATH}", file=sys.stderr)
        return 2

    devices = DEVICES
    if args.device:
        wanted = set(args.device)
        devices = [d for d in DEVICES if d[0] in wanted]
        missing = wanted - {d[0] for d in devices}
        if missing:
            print(f"ERROR: unknown device(s): {sorted(missing)}", file=sys.stderr)
            return 2

    if args.quick:
        corners = [0]
        stat_combos = [(1, 1)]
    else:
        corners = CORNERS
        stat_combos = STAT_COMBOS

    total = len(devices) * len(corners) * len(stat_combos)
    print(f"ngspice : {ngspice}")
    print(f"lib     : {LIB_PATH}")
    print(f"devices : {len(devices)}")
    print(f"corners : {corners}")
    print(f"stat    : {stat_combos}    (PROC_ON, MM_ON)")
    print(f"jobs    : {args.jobs}")
    budget_str = (
        "disabled" if args.max_op_secs <= 0 else f"{args.max_op_secs:.2f}s"
    )
    print(f"budget  : {budget_str} per op")
    print(f"total   : {total} ops")
    print()

    fails: list[tuple[str, int, int, int, str]] = []
    pass_count = 0
    op_times: list[float] = []
    started = time.monotonic()

    def check_budget(ok: bool, reason: str, elapsed: float) -> tuple[bool, str]:
        if ok and args.max_op_secs > 0 and elapsed > args.max_op_secs:
            return False, (
                f"exceeded budget: {elapsed:.2f}s > {args.max_op_secs:.2f}s"
            )
        return ok, reason

    def submit_all(executor):
        for dev_name, klass, extra in devices:
            for case in corners:
                for proc, mm in stat_combos:
                    fut = executor.submit(
                        run_one,
                        ngspice,
                        LIB_PATH,
                        dev_name,
                        klass,
                        extra,
                        case,
                        proc,
                        mm,
                    )
                    yield fut, (dev_name, case, proc, mm)

    completed = 0
    progress_every = max(1, total // 20)

    if args.jobs <= 1:
        for dev_name, klass, extra in devices:
            per_dev_fails = 0
            for case in corners:
                for proc, mm in stat_combos:
                    ok, reason, op_elapsed = run_one(
                        ngspice, LIB_PATH, dev_name, klass, extra, case, proc, mm
                    )
                    op_times.append(op_elapsed)
                    ok, reason = check_budget(ok, reason, op_elapsed)
                    completed += 1
                    if ok:
                        pass_count += 1
                    else:
                        fails.append((dev_name, case, proc, mm, reason))
                        per_dev_fails += 1
                    if completed % progress_every == 0:
                        elapsed = time.monotonic() - started
                        print(
                            f"  ... {completed}/{total} done in {elapsed:.0f}s",
                            flush=True,
                        )
            mark = "OK" if per_dev_fails == 0 else f"FAIL ({per_dev_fails})"
            print(f"  {dev_name:10s} {mark}")
    else:
        with ThreadPoolExecutor(max_workers=args.jobs) as ex:
            future_keys = dict(submit_all(ex))
            for fut in as_completed(future_keys):
                key = future_keys[fut]
                dev_name, case, proc, mm = key
                ok, reason, op_elapsed = fut.result()
                op_times.append(op_elapsed)
                ok, reason = check_budget(ok, reason, op_elapsed)
                completed += 1
                if ok:
                    pass_count += 1
                else:
                    fails.append((dev_name, case, proc, mm, reason))
                if completed % progress_every == 0:
                    elapsed = time.monotonic() - started
                    print(
                        f"  ... {completed}/{total} done in {elapsed:.0f}s",
                        flush=True,
                    )

    elapsed = time.monotonic() - started
    print()
    if op_times:
        sorted_times = sorted(op_times)
        n = len(sorted_times)
        median = sorted_times[n // 2]
        p95 = sorted_times[min(n - 1, int(n * 0.95))]
        max_t = sorted_times[-1]
        max_idx = op_times.index(max_t)
        print(
            f"Op time: median={median*1000:.0f}ms  "
            f"p95={p95*1000:.0f}ms  max={max_t*1000:.0f}ms"
        )
        if args.max_op_secs > 0 and max_t > args.max_op_secs * 0.5:
            print(
                f"  (max op was #{max_idx+1}/{n}, using "
                f"{max_t / args.max_op_secs * 100:.0f}% of {args.max_op_secs:.2f}s budget)"
            )
    print(f"Passed: {pass_count}/{total}   ({elapsed:.1f}s wall)")
    if fails:
        print(f"Failed: {len(fails)}")
        # Group by device for readability.
        by_dev: dict[str, list[tuple[int, int, int, str]]] = {}
        for dev, case, proc, mm, reason in fails:
            by_dev.setdefault(dev, []).append((case, proc, mm, reason))
        for dev in sorted(by_dev):
            entries = by_dev[dev]
            print(f"  {dev} ({len(entries)} fail(s)):")
            for case, proc, mm, reason in entries:
                print(f"    case={case} PROC={proc} MM={mm} -> {reason}")
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
