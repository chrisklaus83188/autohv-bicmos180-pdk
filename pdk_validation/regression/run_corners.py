#!/usr/bin/env python3
"""
P2.2: corner-sanity check across all device families.

For each device family, measure one canonical I-V (or R, or C) at all
five corners (TT, FF, SS, FS, SF) and verify the *sign* of the change
versus TT matches what the .inc's corner factors predict.

Catches:
  * the `case` parameter failing to propagate to a family
    (e.g. a missing _isFF term on a model card),
  * a corner factor flipped in sign or magnitude,
  * VDMOS-family corners failing to flow through the P0 fix's
    parse-time *_STAT params.

Statistics (PROC_ON, MM_ON) are kept OFF so the measurement is
deterministic and depends only on the corner selector.

Probes (one per device family/polarity):

  BSIM3 NMOS (NMOS18)    -> ID @ VGS=VDS=1.2 V
  BSIM3 PMOS (PMOS18)    -> |ID| @ |VGS|=|VDS|=1.2 V
  VDMOS NMOS (NDMOS20)   -> ID @ Vgs=2.5 V, Vds=3 V
  VDMOS PMOS (PDMOS20)   -> |ID| @ Vgs=-2.5 V, Vds=-3 V
  BJT NPN  (NPN_LV)      -> Ic @ Ib=10 uA, Vcc=2 V
  BJT PNP  (PNP_LAT)     -> |Ic| @ Ib=10 uA, Vec=2 V
  Diode    (DIO_PN)      -> Vf @ Ifwd = 1 mA
  R        (RPOLY_HI)    -> R = V / I  @ V=1 V
  C        (CMIM_STD)    -> C from a small dV/dt tran

Expected sign-of-change vs TT (+1 = should increase, -1 = should
decrease, 0 = should stay at TT). NMOS-like devices follow the
N-channel column at mixed corners (FF/FS fast, SS/SF slow); PMOS-like
follow the P-channel column (FF/SF fast, SS/FS slow). Diodes / R / C
in this lib don't distinguish N vs P, so FS and SF stay at TT.

  family            FF  SS  FS  SF
  BSIM3 NMOS, VDMOS NMOS, NPN  +1  -1  +1  -1
  BSIM3 PMOS, VDMOS PMOS, PNP  +1  -1  -1  +1
  Diode (Vf)                   -1  +1   0   0
  R                            -1  +1   0   0
  C                            +1  -1   0   0

Usage:
  python run_corners.py
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
LIB_PATH = REPO_ROOT / "autohv_bicmos180_case.lib"

CORNERS = [
    ("TT", 0),
    ("FF", 1),
    ("SS", 2),
    ("FS", 3),
    ("SF", 4),
]

# Relative tolerance for the "should equal TT" probes (sign 0).
EQ_TOL = 1e-4


def find_ngspice() -> str | None:
    cand = os.environ.get("NGSPICE_BIN")
    if cand and Path(cand).exists():
        return cand
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


def run_deck(ngspice: str, deck: str) -> str:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cir", delete=False, encoding="utf-8"
    ) as f:
        f.write(deck)
        deck_path = f.name
    try:
        res = subprocess.run(
            [ngspice, "-b", deck_path],
            capture_output=True, text=True, timeout=30,
        )
        out = (res.stdout or "") + (res.stderr or "")
    finally:
        try:
            os.unlink(deck_path)
        except OSError:
            pass
    if "no such function" in out:
        raise RuntimeError(f"ngspice errored: {out[-300:]!r}")
    return out


def lib_uri() -> str:
    return str(LIB_PATH).replace("\\", "/")


def re_extract(pattern: str) -> Callable[[str], float]:
    """Return a metric_fn that extracts the (first) regex group as float."""
    compiled = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
    def extract(out: str) -> float:
        m = compiled.search(out)
        if not m:
            raise RuntimeError(f"could not match {pattern!r} in:\n{out[-500:]}")
        return float(m.group(1))
    return extract


# --- Probe deck templates (each uses {lib} and {case} placeholders) ---

DECK_BSIM_N = """\
.include "{lib}"
.param case={case}
.param PROC_ON=0
.param MM_ON=0
Vd d 0 1.2
Vg g 0 1.2
X1 d g 0 0 NMOS18 W=10u L=1u M=1
.control
op
print i(Vd)
quit
.endc
.end
"""

DECK_BSIM_P = """\
.include "{lib}"
.param case={case}
.param PROC_ON=0
.param MM_ON=0
Vd d 0 -1.2
Vg g 0 -1.2
X1 d g 0 0 PMOS18 W=10u L=1u M=1
.control
op
print i(Vd)
quit
.endc
.end
"""

DECK_VDMOS_N = """\
.include "{lib}"
.param case={case}
.param PROC_ON=0
.param MM_ON=0
Vd d 0 3
Vg g 0 2.5
X1 d g 0 NDMOS20 W=20u M=1
.control
op
print i(Vd)
quit
.endc
.end
"""

DECK_VDMOS_P = """\
.include "{lib}"
.param case={case}
.param PROC_ON=0
.param MM_ON=0
Vd d 0 -3
Vg g 0 -2.5
X1 d g 0 PDMOS20 W=20u M=1
.control
op
print i(Vd)
quit
.endc
.end
"""

DECK_NPN = """\
.include "{lib}"
.param case={case}
.param PROC_ON=0
.param MM_ON=0
Vc c 0 2
Ib 0 b 10u
Ve e 0 0
X1 c b e NPN_LV AREA=1
.control
op
print i(Vc)
quit
.endc
.end
"""

DECK_PNP = """\
.include "{lib}"
.param case={case}
.param PROC_ON=0
.param MM_ON=0
Vc c 0 -2
Ib b 0 10u
Ve e 0 0
X1 c b e PNP_LAT AREA=1
.control
op
print i(Vc)
quit
.endc
.end
"""

DECK_DIODE = """\
.include "{lib}"
.param case={case}
.param PROC_ON=0
.param MM_ON=0
* Force Ifwd = 1 mA through DIO_PN; measure forward voltage.
Ifwd 0 a 1m
X1 a 0 DIO_PN AREA=1
.control
op
print v(a)
quit
.endc
.end
"""

DECK_R = """\
.include "{lib}"
.param case={case}
.param PROC_ON=0
.param MM_ON=0
Vp p 0 1
X1 p 0 RPOLY_HI L=100u W=10u
.control
op
print i(Vp)
quit
.endc
.end
"""

DECK_C = """\
.include "{lib}"
.param case={case}
.param PROC_ON=0
.param MM_ON=0
* PWL ramp 0 -> 1 V over 1 ms gives dV/dt = 1000 V/s; sample 1 V.
Vp p 0 PWL(0 0 1m 1 100m 1)
X1 p 0 CMIM_STD L=100u W=100u
.control
tran 50u 1m 0 50u UIC
* At t = 1 ms, V = 1 V. ngspice prints multiple samples; we pick the
* last one (closest to t=1ms).
print i(Vp)
quit
.endc
.end
"""


def metric_load_i_into_vd(out: str) -> float:
    """Drain current = -i(Vd); return positive magnitude."""
    m = re.search(r"i\(vd\)\s*=\s*(-?\d+\.\d+e[+-]?\d+)", out, re.I)
    if not m:
        raise RuntimeError(f"missing i(Vd) in:\n{out[-400:]}")
    return abs(float(m.group(1)))


def metric_load_i_into_vc(out: str) -> float:
    m = re.search(r"i\(vc\)\s*=\s*(-?\d+\.\d+e[+-]?\d+)", out, re.I)
    if not m:
        raise RuntimeError(f"missing i(Vc) in:\n{out[-400:]}")
    return abs(float(m.group(1)))


def metric_vf(out: str) -> float:
    """Forward voltage at the diode anode."""
    m = re.search(r"v\(a\)\s*=\s*(-?\d+\.\d+e[+-]?\d+)", out, re.I)
    if not m:
        raise RuntimeError(f"missing v(a) in:\n{out[-400:]}")
    return float(m.group(1))


def metric_resistor(out: str) -> float:
    """R = 1 V / I (Vp drives 1 V; load current = -i(Vp))."""
    m = re.search(r"i\(vp\)\s*=\s*(-?\d+\.\d+e[+-]?\d+)", out, re.I)
    if not m:
        raise RuntimeError(f"missing i(Vp) in:\n{out[-400:]}")
    load_i = -float(m.group(1))
    return 1.0 / load_i


def metric_cap(out: str) -> float:
    """C(V) extracted from the last tran sample: C = -i(Vp) / dV/dt where
    dV/dt = 1000 V/s. We take the LAST i(Vp) value printed, which is at
    the latest sampled time (closest to the V = 1 V mark).
    """
    # ngspice's print after .tran emits one column-formatted block; the
    # last row has the final time/value. Match the last occurrence.
    matches = list(re.finditer(
        r"^\s*\d+\s+\S+\s+(-?\d+\.\d+e[+-]?\d+)\s*$", out, re.MULTILINE,
    ))
    if not matches:
        # Fallback: search for "i(vp)" lines explicitly.
        matches = list(re.finditer(
            r"i\(vp\)[^\n]*?(-?\d+\.\d+e[+-]?\d+)", out, re.I,
        ))
        if not matches:
            raise RuntimeError(f"missing i(Vp) tran samples in:\n{out[-500:]}")
    last_i = float(matches[-1].group(1))
    return -last_i / 1000.0  # dV/dt = 1000 V/s


@dataclass
class Probe:
    name: str
    deck_template: str
    metric: Callable[[str], float]
    units: str
    # corner-name -> expected sign of (value - value_TT) / value_TT
    #   +1  = should increase (relative to TT)
    #   -1  = should decrease
    #    0  = should equal TT (within EQ_TOL)
    expected_signs: dict[str, int]


PROBES = [
    Probe("BSIM3 NMOS  (NMOS18)  ID @ VGS=VDS=1.2 V",
          DECK_BSIM_N, metric_load_i_into_vd, "A",
          {"FF": +1, "SS": -1, "FS": +1, "SF": -1}),
    Probe("BSIM3 PMOS  (PMOS18)  |ID| @ |VGS|=|VDS|=1.2 V",
          DECK_BSIM_P, metric_load_i_into_vd, "A",
          {"FF": +1, "SS": -1, "FS": -1, "SF": +1}),
    Probe("VDMOS NMOS  (NDMOS20) ID @ Vgs=2.5 Vds=3 V",
          DECK_VDMOS_N, metric_load_i_into_vd, "A",
          {"FF": +1, "SS": -1, "FS": +1, "SF": -1}),
    Probe("VDMOS PMOS  (PDMOS20) |ID| @ Vgs=-2.5 Vds=-3 V",
          DECK_VDMOS_P, metric_load_i_into_vd, "A",
          {"FF": +1, "SS": -1, "FS": -1, "SF": +1}),
    Probe("BJT NPN     (NPN_LV)  Ic @ Ib=10uA Vc=2 V",
          DECK_NPN, metric_load_i_into_vc, "A",
          {"FF": +1, "SS": -1, "FS": +1, "SF": -1}),
    Probe("BJT PNP     (PNP_LAT) |Ic| @ Ib=10uA Vec=2 V",
          DECK_PNP, metric_load_i_into_vc, "A",
          {"FF": +1, "SS": -1, "FS": -1, "SF": +1}),
    Probe("Diode       (DIO_PN)  Vf @ Ifwd=1 mA",
          DECK_DIODE, metric_vf, "V",
          {"FF": -1, "SS": +1, "FS": 0, "SF": 0}),
    Probe("Resistor    (RPOLY_HI) R = V/I @ V=1 V",
          DECK_R, metric_resistor, "ohm",
          {"FF": -1, "SS": +1, "FS": 0, "SF": 0}),
    Probe("Cap         (CMIM_STD) C from dV/dt = 1 kV/s ramp",
          DECK_C, metric_cap, "F",
          {"FF": +1, "SS": -1, "FS": 0, "SF": 0}),
]


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--probe",
        nargs="+",
        default=None,
        help="restrict to listed probes (substring match on probe name)",
    )
    return p.parse_args(argv)


def fmt_value(v: float, units: str) -> str:
    if units == "A":
        if abs(v) < 1e-6:
            return f"{v*1e9:+8.3f} nA"
        elif abs(v) < 1e-3:
            return f"{v*1e6:+8.3f} uA"
        else:
            return f"{v*1e3:+8.3f} mA"
    if units == "V":
        return f"{v:+7.4f} V"
    if units == "ohm":
        if abs(v) >= 1e3:
            return f"{v/1e3:+8.3f} kohm"
        return f"{v:+8.3f} ohm"
    if units == "F":
        if abs(v) < 1e-9:
            return f"{v*1e12:+8.3f} pF"
        return f"{v*1e9:+8.3f} nF"
    return f"{v:+e} {units}"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    ngspice = find_ngspice()
    if ngspice is None:
        print("ERROR: ngspice_con not found", file=sys.stderr)
        return 2
    if not LIB_PATH.exists():
        print(f"ERROR: lib not found at {LIB_PATH}", file=sys.stderr)
        return 2

    probes = PROBES
    if args.probe:
        probes = [p for p in PROBES
                  if any(needle.lower() in p.name.lower() for needle in args.probe)]

    print(f"ngspice : {ngspice}")
    print(f"lib     : {LIB_PATH}")
    print(f"probes  : {len(probes)}")
    print(f"corners : {[c[0] for c in CORNERS]}")
    print()

    fails: list[tuple[str, str]] = []
    lib = lib_uri()

    for probe in probes:
        values: dict[str, float] = {}
        for corner_name, case in CORNERS:
            deck = probe.deck_template.format(lib=lib, case=case)
            out = run_deck(ngspice, deck)
            values[corner_name] = probe.metric(out)

        tt = values["TT"]
        line = f"  {probe.name}\n    TT = {fmt_value(tt, probe.units)}"
        per_corner_ok = True
        for corner_name, expected in probe.expected_signs.items():
            v = values[corner_name]
            if tt == 0:
                delta = 0.0
            else:
                delta = (v - tt) / abs(tt)
            actual_sign = 0
            if abs(delta) > EQ_TOL:
                actual_sign = 1 if delta > 0 else -1
            tag = "OK"
            if actual_sign != expected:
                tag = "FAIL"
                per_corner_ok = False
                fails.append((
                    probe.name,
                    f"corner {corner_name}: expected sign {expected:+d}, "
                    f"got delta={delta*100:+.3f}% (sign {actual_sign:+d})"
                ))
            line += (f"\n    {corner_name} = {fmt_value(v, probe.units)}  "
                     f"delta={delta*100:+7.3f}%  expected sign {expected:+d}   {tag}")
        if per_corner_ok:
            line += "\n    [PROBE OK]"
        print(line)
        print()

    n_corners_total = sum(len(p.expected_signs) for p in probes)
    if fails:
        print(f"Failed: {len(fails)} of {n_corners_total} corner checks")
        return 1
    print(f"ALL PASS: {n_corners_total}/{n_corners_total} corner checks across {len(probes)} probes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
