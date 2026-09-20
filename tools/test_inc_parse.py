#!/usr/bin/env python3
"""Unit test for tools/inc_parse.py (ruling AE1 §1.2).

One line of each form, plus deliberately malformed input asserting the raise. The
raise is the point: a parser that returned None on an unrecognised line is what
silently degraded five direction records, so "cannot read it" must be loud.

    python tools/test_inc_parse.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from inc_parse import IncParseError, parse, sigma_of, tt_of, z_of, is_statistical  # noqa: E402

FAILED = []


def check(label, got, want):
    if got != want:
        FAILED.append(f"{label}: got {got!r}, want {want!r}")


def check_raises(label, fn, *a):
    try:
        fn(*a)
    except IncParseError:
        return
    except Exception as exc:                      # noqa: BLE001
        FAILED.append(f"{label}: raised {type(exc).__name__}, want IncParseError")
        return
    FAILED.append(f"{label}: did not raise")


# --- marker form, two parens with a draw (the authoring notation) ------------
M2 = "{((4.25e-09*_isTT + 4.2075e-09*_isFF + 4.2925e-09*_isSS + 4.25e-09*_isFS + 4.25e-09*_isSF))*(1+P_TOX_18)}"
p = parse(M2)
check("marker2.kind", p.kind, "marker")
check("marker2.tt", p.tt, 4.25e-09)
check("marker2.draw", p.draw, "P_TOX_18")
check("marker2.corners.FF", p.corners["FF"], 4.2075e-09)
check("marker2.tt_of", tt_of(M2), 4.25e-09)
check("marker2.is_statistical", is_statistical(M2), True)

# --- marker form, ONE paren and no draw (pclm) ------------------------------
M1 = "{(1.2*_isTT + 1.21728*_isFF + 1.18464*_isSS + 1.2*_isFS + 1.2*_isSF)}"
p = parse(M1)
check("marker1.kind", p.kind, "marker")
check("marker1.tt", p.tt, 1.2)
check("marker1.draw", p.draw, None)
check("marker1.is_statistical", is_statistical(M1), False)   # no draw: corner-only

# --- generated additive ------------------------------------------------------
A = "{0.88 + 0.016492*Z_VTH_NMOS50}"
p = parse(A)
check("additive.kind", p.kind, "additive")
check("additive.tt", p.tt, 0.88)
check("additive.sigma", p.sigma, 0.016492)
check("additive.z", p.z, "Z_VTH_NMOS50")
check("additive.sigma_of", sigma_of(A), 0.016492)
check("additive.z_of", z_of(A), "Z_VTH_NMOS50")

# --- generated multiplicative ------------------------------------------------
X = "{190*exp(0.026667*Z_U0_NMOS50)}"
p = parse(X)
check("mult.kind", p.kind, "multiplicative")
check("mult.tt", p.tt, 190.0)
check("mult.sigma", p.sigma, 0.026667)
check("mult.z", p.z, "Z_U0_NMOS50")

# --- reference: a tempco wrapper around a _STAT param ------------------------
R = "{KP_NDMOS20_STAT*(1+TC_KP_NDMOS20*(temper-27))}"
p = parse(R)
check("ref.kind", p.kind, "reference")
check("ref.tt", p.tt, None)
check("ref.z", p.z, "KP_NDMOS20_STAT")
check_raises("ref.tt_of raises", tt_of, R)       # no TT to give

# --- a trailing $ comment must not defeat the brace strip --------------------
# The comment has to come off BEFORE the braces: such a line does not end in "}",
# so stripping braces first leaves them attached and every form misses.
check("comment.additive", tt_of("{0.88 + 0.016492*Z_VTH_NMOS50} $ measured"), 0.88)
check("comment.plain", tt_of("{1.4e-07}  $ Leff"), 1.4e-07)
check("comment.unbraced", tt_of("1  $ NOTE: single global fit"), 1.0)

# --- plain deterministic value ----------------------------------------------
check("plain.kind", parse("1.4e-07").kind, "plain")
check("plain.tt", parse("1.4e-07").tt, 1.4e-07)
check("plain.paren", parse("(0.68)").tt, 0.68)
check("plain.is_statistical", is_statistical("1.4e-07"), False)

# --- non-numeric literal: recognised, not an error ---------------------------
check("text.kind", parse("3.3.0").kind, "text")
check("text.tt", parse("3.3.0").tt, None)
check("text.is_statistical", is_statistical("3.3.0"), False)
check_raises("text.tt_of raises", tt_of, "3.3.0")

# --- the failure modes must RAISE, never return None ------------------------
check_raises("malformed raises", parse, "{this is not an expression}")
check_raises("empty raises", parse, "")
check_raises("none raises", parse, None)
check_raises("marker without TT raises", parse, "{(1.2*_isFF + 1.1*_isSS)}")
check_raises("sigma_of on plain raises", sigma_of, "1.4e-07")
check_raises("z_of on marker raises", z_of, M2)

if FAILED:
    print("FAILED (%d):" % len(FAILED))
    for f in FAILED:
        print("   ", f)
    sys.exit(1)
print("inc_parse: all checks passed")
