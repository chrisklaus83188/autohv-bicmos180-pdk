#!/usr/bin/env python3
"""
build_designs.py -- construct the locked designs (brief 4) after Phase 0 fixed
L = 2.0 um.  Writes designs.json (the geometry data of record).

Controlled-comparison rule (brief 2): within a design the input diode device and
the output device are IDENTICAL; the cascode adds a series device sized the same.
So all three devices share one geometry (W,L,M).  Only topology differs.

  Strategy B ("sized per current"): for each Iin in {100n,1u,10u,100u}, L=2um,
      W sized for Vov~=200mV, clamped at Wmin=0.5um (report actual Vov if clamped).
  Strategy A ("one cell programmed"): take the 10uA-B geometry, drive unchanged
      at all four currents.

vbias for MIR_CW is calibrated (max compliance, gain within 0.5%) at nominal
TT/5V/27C and held (it is referenced to Vdd, so it tracks supply).
"""
import json, os
import numpy as np
import mirror_lib as ML

HERE = os.path.dirname(os.path.abspath(__file__))
LOCK_L = 2.0e-6
Wmin = 0.5e-6
CURRENTS = {"100n": 100e-9, "1u": 1e-6, "10u": 10e-6, "100u": 100e-6}
Vdd_nom = 5.0


def geom_for(W, L):
    return dict(Win=W, Lin=L, Min=1, Wout=W, Lout=L, Mout=1, Wc=W, Lc=L, Mc=1)


def area_of(geom, topo):
    a = geom["Win"]*geom["Lin"]*geom["Min"] + geom["Wout"]*geom["Lout"]*geom["Mout"]
    if topo == "MIR_CS":
        a += 2*geom["Wc"]*geom["Lc"]*geom["Mc"]
    elif topo in ("MIR_CW",):
        a += 2*geom["Wc"]*geom["Lc"]*geom["Mc"]
    return a


def record_design(name, W, L, Iin, strategy, note=""):
    """Build one design: geometry + per-current device OP + per-topology area +
    calibrated vbias.  Device OP is measured on a diode device at the DRIVE
    current (so Strategy-A under-drive shows up in Vov/gm-Id/IC)."""
    geom = geom_for(W, L)
    op = ML.diode_op(W, L, Iin, Vdd_nom)           # op at the actual drive current
    clamped = (abs(W-Wmin) < 1e-12)
    vbias = ML.calibrate_vbias(geom, Iin, Vdd_nom)
    rec = dict(
        name=name, strategy=strategy, note=note, Iin=Iin,
        geometry=dict(W_um=W*1e6, L_um=L*1e6, M=1,
                      note="input diode, output, and cascode devices all identical"),
        device_op=dict(Vov_mV=op["vov"]*1e3, VDSAT_mV=op["vdsat"]*1e3,
                       gm_ID=op["gm_id"], IC=op["IC"], VSG_mV=op["vsg"]*1e3,
                       Vth_mV=op["vth"]*1e3, clamped_Wmin=clamped),
        vbias_CW=vbias,
        area_um2=dict(MIR_S=area_of(geom, "MIR_S")*1e12,
                      MIR_CS=area_of(geom, "MIR_CS")*1e12,
                      MIR_CW=area_of(geom, "MIR_CW")*1e12),
    )
    return rec, geom


def main():
    designs = {}
    geoms = {}

    # Strategy B: size W per current
    W_by_curr = {}
    for tag, Iin in CURRENTS.items():
        W, op, clamped = ML.size_W_for_vov(LOCK_L, Iin, 0.20, Wmin=Wmin)
        W_by_curr[tag] = W
        rec, g = record_design(f"B_{tag}", W, LOCK_L, Iin, "B",
                               "sized for Vov=200mV at this current")
        designs[f"B_{tag}"] = rec; geoms[f"B_{tag}"] = g

    # Strategy A: 10uA-B geometry, driven at all four currents
    W10 = W_by_curr["10u"]
    for tag, Iin in CURRENTS.items():
        rec, g = record_design(f"A_{tag}", W10, LOCK_L, Iin, "A",
                               "10uA-B geometry driven unchanged at this current")
        designs[f"A_{tag}"] = rec; geoms[f"A_{tag}"] = g

    out = dict(locked_L_um=LOCK_L*1e6, Wmin_um=Wmin*1e6, Vov_target_mV=200,
               Vdd_nominal=Vdd_nom, designs=designs)
    with open(os.path.join(HERE, "designs.json"), "w") as f:
        json.dump(out, f, indent=2)
    # also persist the geometry map for downstream drivers
    with open(os.path.join(HERE, "_geoms.json"), "w") as f:
        json.dump({k: {**v, "vbias": designs[k]["vbias_CW"],
                       "Iin": designs[k]["Iin"]} for k, v in geoms.items()},
                  f, indent=2)

    # report
    print(f"\nLocked designs (L={LOCK_L*1e6:.1f}um).  vbias=CW cascode drop below Vdd.\n")
    print("{:14} {:4} {:8} {:9} {:8} {:7} {:6} {:7} {:8}".format(
        "design","strat","Iin","W(um)","Vov(mV)","gm/Id","IC","vbias","clamp"))
    for k, r in designs.items():
        d = r["device_op"]
        print("{:14} {:4} {:8} {:9.2f} {:8.1f} {:7.2f} {:6.2f} {:7.3f} {:8}".format(
            k, r["strategy"], _fmtI(r["Iin"]), r["geometry"]["W_um"],
            d["Vov_mV"], d["gm_ID"], d["IC"], r["vbias_CW"],
            "yes" if d["clamped_Wmin"] else ""))

def _fmtI(I):
    if I >= 1e-6: return f"{I*1e6:g}u"
    return f"{I*1e9:g}n"

if __name__ == "__main__":
    main()
