#!/usr/bin/env python3
"""
run_dc.py -- primary + fine DC sweeps across the full PVT matrix (brief 5).

For every (design, topology) x Vdd{3.2,4.5,5.0,5.5} x corner{0..4} x temp{-55,27,150}
run a .dc sweep of V_out from 0 to Vdd at 10 mV, then:
  * record the 100 mV grid (data of record) verbatim,
  * keep the fine 10 mV arrays for nominal-PVT configs (for downstream quadrature
    and the V_SD collapse check),
  * compute the brief-6 band metrics.

Emits one representative netlist per (design, topology) into netlists/ and the
full record into results.json.  Parallelized across cores; each job uses a unique
wrdata file so runs don't collide.
"""
import json, os, itertools, tempfile
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import mirror_lib as ML
import analysis as AN

HERE = os.path.dirname(os.path.abspath(__file__))
TOPOS = ["MIR_S", "MIR_CS", "MIR_CW"]
VDDS = [3.2, 4.5, 5.0, 5.5]
CASES = [0, 1, 2, 3, 4]
TEMPS = [-55, 27, 150]
CASE_NAME = {0:"TT",1:"FF",2:"SS",3:"FS",4:"SF"}
FINE_STEP = 0.010
GRID_STEP = 0.100

with open(os.path.join(HERE, "_geoms.json")) as f:
    GEOMS = json.load(f)   # name -> {Win.., vbias, Iin, ...} (geometry dict flat)


def _geom(name):
    g = GEOMS[name]           # already a flat SI geometry dict (Win.., vbias, Iin)
    return dict(g), g["Iin"]


def job(args):
    name, topo, Vdd, case, temp = args
    geom, Iin = _geom(name)
    tag = f"{name}_{topo}_{Vdd}_{case}_{temp}".replace(".", "p")
    outf = os.path.join(ML.RAW, f"dc_{tag}.dat")
    deck, outf = ML.deck_dc(tag, topo, geom, Iin, Vdd, 0.0, Vdd, FINE_STEP,
                            case=case, temp=temp, outfile=outf)
    # write unique deck to avoid parallel collision on the shared _p0.cir path
    dpath = os.path.join(ML.RAW, f"_dc_{tag}.cir")
    with open(dpath, "w") as f:
        f.write(deck)
    import subprocess
    subprocess.run([ML.NGSPICE, "-b", dpath], cwd=ML.RAW, capture_output=True,
                   text=True, timeout=600)
    v, i = ML.read_wrdata(outf)
    # subsample the 100 mV grid (data of record)
    grid_v = np.round(np.arange(0.0, Vdd+1e-9, GRID_STEP), 3)
    grid_i = np.interp(grid_v, v, i)
    mtr = AN.band_metrics(v, i, Vdd, Iin)
    nominal = (Vdd == 5.0 and case == 0 and temp == 27)
    rec = dict(name=name, topo=topo, Vdd=Vdd, case=case, corner=CASE_NAME[case],
               temp=temp, Iin=Iin,
               grid_Vout=grid_v.tolist(), grid_Iout=grid_i.tolist(),
               metrics=mtr)
    if nominal:
        rec["fine_Vout"] = np.round(v, 4).tolist()
        rec["fine_Iout"] = i.tolist()
    os.remove(outf); os.remove(dpath)
    return rec


def main():
    names = list(GEOMS.keys())
    # emit one representative netlist per (design, topology) at nominal PVT
    for name in names:
        geom, Iin = _geom(name)
        for topo in TOPOS:
            deck, _ = ML.deck_dc(f"{name}_{topo}", topo, geom, Iin, 5.0, 0.0, 5.0,
                                 FINE_STEP, case=0, temp=27,
                                 outfile=os.path.join(ML.RAW, "ignore.dat"))
            with open(os.path.join(ML.NETLISTS, f"{name}_{topo}.cir"), "w") as f:
                f.write(deck)

    jobs = list(itertools.product(names, TOPOS, VDDS, CASES, TEMPS))
    print(f"DC sweep matrix: {len(jobs)} configs "
          f"({len(names)} designs x {len(TOPOS)} topo x {len(VDDS)} Vdd x "
          f"{len(CASES)} corner x {len(TEMPS)} temp)")
    results = []
    with ProcessPoolExecutor(max_workers=8) as ex:
        for n, rec in enumerate(ex.map(job, jobs, chunksize=4), 1):
            results.append(rec)
            if n % 100 == 0:
                print(f"  {n}/{len(jobs)} done")
    out = dict(meta=dict(topos=TOPOS, vdds=VDDS, cases=CASE_NAME, temps=TEMPS,
                         fine_step=FINE_STEP, grid_step=GRID_STEP,
                         band=f"0..{AN.VBAND}V in-saturation (supply-agnostic)",
                         gain_anchor="Vdd/2"),
               sweeps=results)
    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(out, f)
    print(f"wrote results.json  ({len(results)} sweeps)")

if __name__ == "__main__":
    main()
