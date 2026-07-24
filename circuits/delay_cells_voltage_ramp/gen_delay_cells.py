#!/usr/bin/env python3
"""
gen_delay_cells.py -- emit the voltage-ramp delay-cell library and testbenches.

A delay cell here is: a PMOS current mirror (from circuits/current_mirror_char)
sources a controlled current into a PDK MIM capacitor, producing a linear voltage
ramp on node RAMP.  An NMOS switch across the cap resets the ramp; its gate is
driven by a BUF_5V0 buffer whose input is the RST pin.

  ports:  RST  RAMP  VDD  GND      (active-high reset: RST=1 -> ramp held at 0)

Signal-path devices are all PDK (PMOS50 mirror, CMIM_STD cap, NMOS50 switch,
BUF_5V0 = PMOS50/NMOS50).  The mirror reference current and the MIR_CW wide-swing
cascode bias are ideal sources -- bias *instruments*, exactly as in the
current-mirror characterization study (see MIRROR_CHAR.md).

Twelve cells = 3 mirror topologies x 4 bias currents.  Geometry (L=2 um, W per
current for Vov~200 mV, Strategy B) and the wide-swing bias come straight from
circuits/current_mirror_char/designs.json.

Four testbenches (one per current) each instantiate all three topologies on a
common RST and Vdd, and run a transient long enough to cover the full ramp.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CELLS = os.path.join(HERE, "cells")
TB = os.path.join(HERE, "tb")

# ---- design data of record (Strategy B, L=2um) from designs.json -------------
#   label,  Iref,     W_mirror,      vbias_CW  (V below Vdd)
CURRENTS = [
    ("100n", "100n", "0.8768254u", "1.9"),
    ("1u",   "1u",   "8.292503u",  "1.7"),
    ("10u",  "10u",  "81.22778u",  "1.6"),
    ("100u", "100u", "795.6526u",  "1.65"),
]

L_MIR = "2u"          # locked mirror channel length
CAP_LW = "31.623u"    # CMIM_STD ~1.0 pF (CJ0=1 fF/um^2 * 1000 um^2)
# NMOS50 reset switch: sized to firmly sink the largest bias (100 uA) and hold the
# ramp node stably low (Ron ~50 ohm -> ~5 mV at 100 uA).  A weaker switch lets the
# node drift, which dithers CMIM_STD's behavioral branch and stalls the transient.
SW_W, SW_L = "100u", "0.5u"

# common tail: ramp capacitor + reset switch + reset buffer
def _tail():
    return (
        f"* --- ramp capacitor: PDK MIM, ~1 pF ---\n"
        f"Xcap RAMP GND CMIM_STD L={CAP_LW} W={CAP_LW}\n"
        f"* --- reset switch across the cap; gate = buffered RST (active-high) ---\n"
        f"Xrst RAMP nrstb GND GND NMOS50 W={SW_W} L={SW_L} M=1\n"
        f"Xbuf RST nrstb VDD GND BUF_5V0\n"
    )

def cell_S(lbl, iref, w, _vb):
    return (
        f".subckt DLYRAMP_S_{lbl.upper()} RST RAMP VDD GND\n"
        f"* Simple PMOS current mirror -> RAMP.  Iref: ideal reference (instrument).\n"
        f"Iref nin GND {iref}\n"
        f"Xin  nin  nin VDD VDD PMOS50 W={w} L={L_MIR} M=1\n"
        f"Xout RAMP nin VDD VDD PMOS50 W={w} L={L_MIR} M=1\n"
        f"{_tail()}"
        f".ends DLYRAMP_S_{lbl.upper()}\n"
    )

def cell_CS(lbl, iref, w, _vb):
    return (
        f".subckt DLYRAMP_CS_{lbl.upper()} RST RAMP VDD GND\n"
        f"* Standard diode-stack cascode mirror -> RAMP (recommended: flat I over PVT).\n"
        f"Iref n2 GND {iref}\n"
        f"Xin    n1   n1 VDD VDD PMOS50 W={w} L={L_MIR} M=1\n"
        f"Xincs  n2   n2 n1  VDD PMOS50 W={w} L={L_MIR} M=1\n"
        f"Xout   n3   n1 VDD VDD PMOS50 W={w} L={L_MIR} M=1\n"
        f"Xoutcs RAMP n2 n3  VDD PMOS50 W={w} L={L_MIR} M=1\n"
        f"{_tail()}"
        f".ends DLYRAMP_CS_{lbl.upper()}\n"
    )

def cell_CW(lbl, iref, w, vb):
    return (
        f".subckt DLYRAMP_CW_{lbl.upper()} RST RAMP VDD GND\n"
        f"* Wide-swing cascode mirror -> RAMP.  Vbcw: ideal Vdd-referenced bias (instrument).\n"
        f"Iref ng GND {iref}\n"
        f"Vbcw VDD ncw {vb}\n"
        f"Xin    nA ng  VDD VDD PMOS50 W={w} L={L_MIR} M=1\n"
        f"Xincw  ng ncw nA  VDD PMOS50 W={w} L={L_MIR} M=1\n"
        f"Xout   nB ng  VDD VDD PMOS50 W={w} L={L_MIR} M=1\n"
        f"Xoutcw RAMP ncw nB VDD PMOS50 W={w} L={L_MIR} M=1\n"
        f"{_tail()}"
        f".ends DLYRAMP_CW_{lbl.upper()}\n"
    )

TOPO = [("s", cell_S), ("cs", cell_CS), ("cw", cell_CW)]

# ---- transient timing per current: t_ramp = C*Vspan/I, C=1pF, Vspan~4V --------
#   label -> (TD, PW, PER, TSTEP, TSTOP)  -- reset released at TD, ramp runs PW.
# TD (reset hold) is kept >= ~100 ns so the cascode bias fully settles under UIC
# before the ramp is released; the cascode devices are large (W up to ~800 um) and
# UIC skips the DC operating point, so they need a settling window at every current.
TIMING = {
    "100n": ("200n", "48u",  "100u", "20n",   "48.5u"),
    "1u":   ("200n", "4.8u", "10u",  "2n",    "5.2u"),
    "10u":  ("100n", "500n", "2u",   "0.2n",  "620n"),
    "100u": ("100n", "80n",  "400n", "0.05n", "200n"),
}

def testbench(lbl, iref):
    td, pw, per, tstep, tstop = TIMING[lbl]
    L = lbl.upper()
    meas = ""
    for tag, node in (("s", "ramp_s"), ("cs", "ramp_cs"), ("cw", "ramp_cw")):
        meas += (
            f"meas tran t1_{tag} when v({node})=1 rise=1\n"
            f"meas tran t3_{tag} when v({node})=3 rise=1\n"
            f"let slope_{tag} = 2/(t3_{tag}-t1_{tag})\n"
            f"print slope_{tag}\n"
        )
    return (
        f".title delay-cell voltage ramp -- {iref} bias, MIR_S / MIR_CS / MIR_CW\n"
        f"* Three mirror topologies charging ~1 pF at {iref}; RST resets the ramp.\n"
        f'.include "../../../autohv_bicmos180_case.lib"\n'
        f'.include "../../../circuits/async_logic_design/cells.lib"\n'
        f'.include "../cells/dlyramp_s_{lbl}.lib"\n'
        f'.include "../cells/dlyramp_cs_{lbl}.lib"\n'
        f'.include "../cells/dlyramp_cw_{lbl}.lib"\n'
        f"\n"
        f"Vdd vdd 0 5\n"
        f"* RST: reset held (5V), released to 0V at {td} for the ramp, re-asserted at end\n"
        f"Vrst rst 0 PULSE(5 0 {td} 1n 1n {pw} {per})\n"
        f"\n"
        f"Xs  rst ramp_s  vdd 0 DLYRAMP_S_{L}\n"
        f"Xcs rst ramp_cs vdd 0 DLYRAMP_CS_{L}\n"
        f"Xcw rst ramp_cw vdd 0 DLYRAMP_CW_{L}\n"
        f"\n"
        f"* UIC: start from t=0 with the ramp held at 0 by reset.  This avoids a DC\n"
        f"* operating-point interaction between the simple mirror and CMIM_STD's\n"
        f"* behavioral voltage-coefficient branch that otherwise stalls the transient\n"
        f"* when all three topologies share one deck.  The reset hold (TD above) gives\n"
        f"* the cascode bias time to settle before the ramp is released.\n"
        f".tran {tstep} {tstop} uic\n"
        f".control\n"
        f"run\n"
        f"{meas}"
        f".endc\n"
        f".end\n"
    )

def main():
    os.makedirs(CELLS, exist_ok=True)
    os.makedirs(TB, exist_ok=True)
    n = 0
    for lbl, iref, w, vb in CURRENTS:
        for tag, fn in TOPO:
            path = os.path.join(CELLS, f"dlyramp_{tag}_{lbl}.lib")
            with open(path, "w") as f:
                f.write(fn(lbl, iref, w, vb))
            n += 1
    for lbl, iref, _w, _vb in CURRENTS:
        path = os.path.join(TB, f"tb_{lbl}.cir")
        with open(path, "w") as f:
            f.write(testbench(lbl, iref))
    print(f"wrote {n} cell netlists to cells/ and {len(CURRENTS)} testbenches to tb/")

if __name__ == "__main__":
    main()
