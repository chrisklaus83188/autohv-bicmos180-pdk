#!/usr/bin/env python3
"""
run_phase0.py -- Phase 0 (brief 4): pick L.

At Iin=10uA, TT/5.0V/27C, for MIR_S and MIR_CS, sweep L in {0.5,1,2,4} um; for
each size W for Vov~=200mV; report lambda_eff, r_out, area, Vov.  Recommend a
locked L.  Emits phase0.json.

lambda_eff / r_out are measured from a real .dc sweep of the built mirror
(fine 10 mV grid, 0->2.0 V in-saturation window).  Geometry lives in the decks.
"""
import json, os
import numpy as np
import mirror_lib as ML
import analysis as AN

HERE = os.path.dirname(os.path.abspath(__file__))
Iin = 10e-6
Vdd = 5.0
L_LIST = [0.5e-6, 1e-6, 2e-6, 4e-6]

def area_of(geom, topo):
    a = geom["Win"]*geom["Lin"]*geom["Min"] + geom["Wout"]*geom["Lout"]*geom["Mout"]
    if topo in ("MIR_CS",):
        a += 2*geom["Wc"]*geom["Lc"]*geom["Mc"]   # 2 cascode devices
    return a

def main():
    rows = []
    for L in L_LIST:
        # size W for Vov=0.2 at 10uA using a diode device of this L
        W, op, clamped = ML.size_W_for_vov(L, Iin, 0.20, Vdd=Vdd)
        geom = dict(Win=W, Lin=L, Min=1, Wout=W, Lout=L, Mout=1,
                    Wc=W, Lc=L, Mc=1)
        for topo in ("MIR_S", "MIR_CS"):
            deck, out = ML.deck_dc(f"p0_{topo}_L{L*1e9:.0f}n", topo, geom,
                                   Iin, Vdd, 0, 3.0, 0.01)
            # persist the netlist as data of record
            with open(os.path.join(ML.NETLISTS,
                      f"phase0_{topo}_L{L*1e9:.0f}n.cir"), "w") as f:
                f.write(deck)
            ML.run(deck, "p0")
            v, i = ML.read_wrdata(out)
            mtr = AN.band_metrics(v, i, Vdd, Iin)
            rows.append(dict(
                topo=topo, L_um=L*1e6, W_um=W*1e6, clamped=clamped,
                Vov=op["vov"], vdsat=op["vdsat"], gm_id=op["gm_id"], IC=op["IC"],
                lambda_eff=mtr["lambda_eff"], rout_MΩ=mtr["rout_inband"]/1e6,
                area_um2=area_of(geom, topo)*1e12,
                gain_vddhalf=mtr["gain_vddhalf"], nonlin_pct=mtr["ramp_nonlin_pct"]))
    with open(os.path.join(HERE, "phase0.json"), "w") as f:
        json.dump(rows, f, indent=2)

    # report
    print(f"\nPhase 0 -- L selection @ Iin=10uA, TT/5.0V/27C, Vov target 200mV\n")
    hdr = ("topo","L(um)","W(um)","Vov(mV)","gm/Id","IC","lam_eff(/V)",
           "rout(MΩ)","area(um2)","gain@Vd/2","nonlin%")
    print("{:7} {:6} {:8} {:8} {:6} {:6} {:11} {:9} {:10} {:9} {:8}".format(*hdr))
    for r in rows:
        print("{:7} {:6.2f} {:8.2f} {:8.1f} {:6.2f} {:6.2f} {:11.5f} {:9.3f} {:10.2f} {:9.4f} {:8.3f}".format(
            r["topo"], r["L_um"], r["W_um"], r["Vov"]*1e3, r["gm_id"], r["IC"],
            r["lambda_eff"], r["rout_MΩ"], r["area_um2"], r["gain_vddhalf"],
            r["nonlin_pct"]))
    print()
    # lambda*L invariance and area scaling summary (MIR_S)
    print("MIR_S lambda*L and area(L^2) check:")
    for r in rows:
        if r["topo"]=="MIR_S":
            print("  L=%.1fum: lambda*L=%.4f (um-normalized %.4f)  area=%.2f um2"%(
                r["L_um"], r["lambda_eff"]*r["L_um"], r["lambda_eff"]*r["L_um"], r["area_um2"]))

if __name__ == "__main__":
    main()
