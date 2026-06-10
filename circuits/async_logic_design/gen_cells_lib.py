#!/usr/bin/env python3
"""
gen_cells_lib.py -- (re)generate circuits/async_logic_design/cells.lib

Produces 24 .subckt definitions (8 cells x 3 voltage domains) with the
characterized widths from results.json baked in, so the cells can be used
as black-box building blocks in higher-level schematics.

This is the single source of truth for the cells library: every time the
characterization sweep updates results.json, re-run this script to refresh
cells.lib. The topology comes from async_lib.cell_netlist() so there is
no risk of subckt and characterization decks drifting apart.

Subckt naming: <CELL>_<DOMAIN> where DOMAIN is 1V8 / 3V3 / 5V0. The
underscored form (not INV18 / INV33 / INV50) avoids confusion with the
PDK's high-voltage device names where the trailing number is the
breakdown voltage (e.g. NDMOS200 = 200 V).

Port order:
    INV    in  out  vdd  gnd
    BUF    in  out  vdd  gnd
    NAND2  a   b    out  vdd  gnd
    NOR2   a   b    out  vdd  gnd
    AND2   a   b    out  vdd  gnd
    OR2    a   b    out  vdd  gnd
    XOR2   a   b    out  vdd  gnd
    XNOR2  a   b    out  vdd  gnd

Usage example (in a downstream deck):
    .include "../../autohv_bicmos180_case.lib"     ; the PDK
    .include "../cells.lib"                          ; this library
    X1 a b o vdd 0 NAND2_3V3                         ; instantiate
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import async_lib  # reuse the cell_netlist topology generator

HERE     = Path(__file__).resolve().parent
RESULTS  = HERE / "results.json"
OUT_LIB  = HERE / "cells.lib"

CELLS = ["INV", "BUF", "NAND2", "NOR2", "AND2", "OR2", "XOR2", "XNOR2"]
DOMAIN_TAG = {"1v8": "1V8", "3v3": "3V3", "5v0": "5V0"}

PORTS = {
    "INV":   ["in", "out"],
    "BUF":   ["in", "out"],
    "NAND2": ["a", "b", "out"],
    "NOR2":  ["a", "b", "out"],
    "AND2":  ["a", "b", "out"],
    "OR2":   ["a", "b", "out"],
    "XOR2":  ["a", "b", "out"],
    "XNOR2": ["a", "b", "out"],
}


def generate_subckt(cell: str, dom_key: str, W: dict[str, float]) -> str:
    """Return a complete `.subckt ... .ends` block for one (cell, domain)."""
    dom = async_lib.DOMAINS[dom_key]
    tag = DOMAIN_TAG[dom_key]
    name = f"{cell}_{tag}"
    ports = " ".join(PORTS[cell] + ["vdd", "gnd"])

    # cell_netlist emits X-instance lines with hardcoded '0' for gnd. Inside
    # a subckt we need 'gnd' (the port name) instead. Replace whitespace-
    # delimited '0' tokens only; the regex won't touch the '0' inside width
    # expressions like {(0.8402)*1e-6} because they're not space-bounded.
    body = async_lib.cell_netlist(cell, dom, async_lib.wf_numeric(W))
    body = re.sub(r"(?<=\s)0(?=\s)", "gnd", body)

    return (
        f".subckt {name} {ports}\n"
        f"{body}"
        f".ends {name}\n"
    )


def main(argv: list[str] | None = None) -> int:
    if not RESULTS.exists():
        print(
            f"ERROR: {RESULTS.name} not found. Run python async_run.py first.",
            file=sys.stderr,
        )
        return 2

    data = json.loads(RESULTS.read_text())
    lines: list[str] = []

    lines.append("* AutoHV BiCMOS 180 PDK -- asynchronous-logic cell library\n")
    lines.append("*\n")
    lines.append(
        "* 24 static-CMOS cells: INV, BUF, NAND2, NOR2, AND2, OR2, XOR2, XNOR2\n"
    )
    lines.append(
        "* in three voltage domains (1.8 V / 3.3 V / 5 V), each sized for\n"
    )
    lines.append(
        "* V_M = Vdd/2 at the nominal corner with input-pin load <= 5 fF.\n"
    )
    lines.append("*\n")
    lines.append("* GENERATED -- do not hand-edit. To refresh widths:\n")
    lines.append("*   python async_run.py        # re-characterize, updates results.json\n")
    lines.append("*   python gen_cells_lib.py    # regenerate this file from results.json\n")
    lines.append("*\n")
    lines.append("* Naming: <CELL>_<DOMAIN> where DOMAIN is 1V8 / 3V3 / 5V0\n")
    lines.append("*\n")
    lines.append("* Port order:\n")
    lines.append("*   INV    in  out  vdd  gnd\n")
    lines.append("*   BUF    in  out  vdd  gnd\n")
    lines.append("*   gate2  a   b    out  vdd  gnd\n")
    lines.append("*\n")
    lines.append("* Usage example (from a deck two levels deep -- e.g. in decks/):\n")
    lines.append("*   .include \"../../../autohv_bicmos180_case.lib\"\n")
    lines.append("*   .include \"../cells.lib\"\n")
    lines.append("*   X1 a b o vdd 0 NAND2_3V3\n")
    lines.append("*\n")

    n_subckts = 0
    for dom_key in ("1v8", "3v3", "5v0"):
        tag = DOMAIN_TAG[dom_key]
        dom = async_lib.DOMAINS[dom_key]
        lines.append(
            f"\n* ============================================================\n"
            f"* {tag} domain  --  NMOS{tag.replace('V','').lstrip('0') or '50'}/"
            f"PMOS{tag.replace('V','').lstrip('0') or '50'}  L = {dom['L']:.2f} um\n"
            f"* ============================================================\n\n"
        )
        for cell in CELLS:
            W = data[dom_key][cell]["W"]
            lines.append(generate_subckt(cell, dom_key, W))
            lines.append("\n")
            n_subckts += 1

    OUT_LIB.write_text("".join(lines))
    n_total_lines = OUT_LIB.read_text().count("\n")
    print(f"Wrote {OUT_LIB.relative_to(HERE.parents[1])}")
    print(f"  {n_subckts} subckts ({n_subckts // 8} domains x 8 cells)")
    print(f"  {n_total_lines} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
