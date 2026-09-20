#!/usr/bin/env python3
"""One parser for every form a card expression takes in this PDK (ruling AE1 §1.2).

There are two files and three expression forms, and before this module every tool
carried its own regex for them. That is how five direction records were silently
degraded: `measure_stat_directions.tt_of` returned None on the generated form, the
caller built no perturbation, and the variable vanished from the direction with no
record at all.

**Parsers raise; they do not return None.** A tool that cannot read a line stops and
says so. That is the whole point of this module -- the silent None was the bug, not
the missing regex.

FORMS
-----
`marker`          the authoring notation in autohv_bicmos180_case_models.inc.in:
                  ((1.2*_isTT + 1.21*_isFF + ...))*(1+P_X)   two parens, with a draw
                  (1.2*_isTT + 1.21*_isFF + ...)             one paren, no draw (pclm)
                  The _isXX terms mark "this parameter is statistical" and carry the
                  per-corner values; P_X marks which draw applied.

`additive`        generated:  {0.88 + 0.016492*Z_VTH_NMOS50}
`multiplicative`  generated:  {190*exp(0.026667*Z_U0_NMOS50)}
`reference`       a tempco wrapper around a _STAT param, which the generator does not
                  own:        {KP_NDMOS20_STAT*(1+TC_KP_NDMOS20*(temper-27))}
`plain`           a deterministic value: 1.4e-07
`text`            a non-numeric literal: version=3.3.0

USAGE
    from inc_parse import parse, tt_of, sigma_of, z_of, IncParseError
    p = parse("{0.88 + 0.016492*Z_VTH_NMOS50}")
    p.kind, p.tt, p.sigma, p.z   -> "additive", 0.88, 0.016492, "Z_VTH_NMOS50"
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

NUM = r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?"


class IncParseError(ValueError):
    """Raised when an expression matches none of the known forms."""


@dataclass
class Parsed:
    kind: str                       # marker | additive | multiplicative | reference | plain | text
    raw: str
    tt: float | None = None         # the typical value, where the form carries one
    sigma: float | None = None      # generated forms only
    z: str | None = None            # generated forms only, e.g. "Z_VTH_NMOS50"
    draw: str | None = None         # marker form only, e.g. "P_DVTH_NMOS18"
    corners: dict = field(default_factory=dict)   # marker form: {"TT": .., "FF": .., ...}


def _strip(expr: str) -> str:
    # Order matters: the comment goes first. A braced expression with a trailing
    # note -- `{0.88 + 0.016492*Z_VTH_NMOS50} $ measured` -- does not *end* in "}",
    # so stripping braces first leaves them attached and every form below misses.
    e = re.sub(r"\s*\$.*$", "", expr).strip()      # drop an inline $ comment
    if e.startswith("{") and e.endswith("}"):
        e = e[1:-1].strip()
    return e.strip()


def parse(expr: str) -> Parsed:
    """Parse one card-parameter expression. Raises IncParseError if unrecognised."""
    if expr is None:
        raise IncParseError("expression is None")
    e = _strip(expr)
    if not e:
        raise IncParseError("empty expression")

    # --- marker form: carries _isXX corner terms -----------------------------
    if "_isTT" in e:
        corners = {}
        for sfx in ("TT", "FF", "SS", "FS", "SF"):
            m = re.search(rf"({NUM})\s*\*\s*_is{sfx}\b", e)
            if m:
                corners[sfx] = float(m.group(1))
        if "TT" not in corners:
            raise IncParseError(f"marker form without a _isTT term: {expr!r}")
        d = re.search(r"\b(P_[A-Z][A-Z0-9_]*)", e)
        return Parsed("marker", expr, tt=corners["TT"],
                      draw=d.group(1) if d else None, corners=corners)

    # --- generated multiplicative: TT*exp(sigma*Z_X) -------------------------
    m = re.fullmatch(rf"({NUM})\s*\*\s*exp\(\s*({NUM})\s*\*\s*(Z_\w+)\s*\)", e)
    if m:
        return Parsed("multiplicative", expr, tt=float(m.group(1)),
                      sigma=float(m.group(2)), z=m.group(3))

    # --- generated additive: TT + sigma*Z_X ----------------------------------
    m = re.fullmatch(rf"({NUM})\s*\+\s*({NUM})\s*\*\s*(Z_\w+)", e)
    if m:
        return Parsed("additive", expr, tt=float(m.group(1)),
                      sigma=float(m.group(2)), z=m.group(3))

    # --- reference: a _STAT param, optionally wrapped in a tempco ------------
    m = re.search(r"\b(\w+_STAT)\b", e)
    if m:
        return Parsed("reference", expr, tt=None, z=m.group(1))

    # --- plain deterministic value -------------------------------------------
    m = re.fullmatch(rf"\(*\s*({NUM})\s*\)*", e)
    if m:
        return Parsed("plain", expr, tt=float(m.group(1)))

    # --- non-numeric literal (e.g. version=3.3.0) ----------------------------
    # A legitimate card value that is simply not a number. Recognising it keeps
    # consumers from special-casing it, without weakening the rule that genuinely
    # unreadable input raises.
    if re.fullmatch(r"[\w.+-]+", e):
        return Parsed("text", expr)

    raise IncParseError(f"unrecognised card expression: {expr!r}")


def tt_of(expr: str) -> float:
    """The typical value. Raises if the form carries none (e.g. a _STAT reference)."""
    p = parse(expr)
    if p.tt is None:
        raise IncParseError(f"no TT value in a {p.kind} expression: {expr!r}")
    return p.tt


def sigma_of(expr: str) -> float:
    """The sigma of a generated expression. Raises on any other form."""
    p = parse(expr)
    if p.sigma is None:
        raise IncParseError(f"no sigma in a {p.kind} expression: {expr!r}")
    return p.sigma


def z_of(expr: str) -> str:
    """The Z_ variable of a generated expression. Raises on any other form."""
    p = parse(expr)
    if p.z is None or not p.z.startswith("Z_"):
        raise IncParseError(f"no Z_ variable in a {p.kind} expression: {expr!r}")
    return p.z


def is_statistical(expr: str) -> bool:
    """True if this parameter is driven by a statistical variable in either notation."""
    try:
        p = parse(expr)
    except IncParseError:
        return False
    return p.kind in ("additive", "multiplicative") or (
        p.kind == "marker" and p.draw is not None)
