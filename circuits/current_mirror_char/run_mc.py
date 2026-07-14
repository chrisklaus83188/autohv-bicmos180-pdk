#!/usr/bin/env python3
"""
run_mc.py -- Monte Carlo (brief 5), nominal PVT (TT/5.0V/27C), two SEPARATE modes:
  * mismatch : MM_ON=1 PROC_ON=0  (local device-to-device Vth/W/L mismatch --
               the delvto series-shift mechanism inside each PMOS50 subckt)
  * procmm   : MM_ON=1 PROC_ON=1  (global process + local mismatch)

>=500 runs each, on the full V_out grid.  Per run we extract I_out(1.2V) and the
in-band lambda_eff (brief 6.9).  A mirror is a ratio, so global process should
largely cancel -> mismatch dominates.  We test that by comparing the two modes.

Reproducible: run k uses `set rndseed=k`.
"""
import json, os, itertools, subprocess
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import mirror_lib as ML
import analysis as AN

HERE = os.path.dirname(os.path.abspath(__file__))
NRUN = 500
TOPOS = ["MIR_S", "MIR_CS", "MIR_CW"]
DESIGNS = ["B_10u", "B_100n", "A_100n"]
MODES = {"mismatch": (1, 0), "procmm": (1, 1)}
Vdd = 5.0

with open(os.path.join(HERE, "_geoms.json")) as f:
    GEOMS = json.load(f)


def job(args):
    name, topo, mode, k = args
    g = dict(GEOMS[name]); Iin = g["Iin"]
    mm, proc = MODES[mode]
    tag = f"mc_{name}_{topo}_{mode}_{k}"
    outf = os.path.join(ML.RAW, f"{tag}.dat")
    # build a dc deck but inject the rndseed into its .control block
    deck, outf = ML.deck_dc(tag, topo, g, Iin, Vdd, 0.0, Vdd, 0.1,
                            case=0, proc=proc, mm=mm, temp=27, outfile=outf)
    deck = deck.replace(".control\n", f".control\nset rndseed={k}\n", 1)
    dpath = os.path.join(ML.RAW, f"_{tag}.cir")
    with open(dpath, "w") as f:
        f.write(deck)
    subprocess.run(["ngspice", "-b", dpath], capture_output=True, text=True,
                   timeout=600)
    v, i = ML.read_wrdata(outf)
    m = AN.band_metrics(v, i, Vdd, Iin)
    os.remove(outf); os.remove(dpath)
    return (name, topo, mode, m["I_at_vddhalf"], m["lambda_eff"])


def main():
    jobs = [(n, t, mode, k)
            for n in DESIGNS for t in TOPOS for mode in MODES
            for k in range(1, NRUN+1)]
    print(f"MC: {len(jobs)} runs "
          f"({len(DESIGNS)} designs x {len(TOPOS)} topo x {len(MODES)} modes x {NRUN})")
    acc = {}
    with ProcessPoolExecutor(max_workers=8) as ex:
        for n, res in enumerate(ex.map(job, jobs, chunksize=25), 1):
            name, topo, mode, imid, lam = res
            acc.setdefault((name, topo, mode), {"I": [], "lam": []})
            acc[(name, topo, mode)]["I"].append(imid)
            acc[(name, topo, mode)]["lam"].append(lam)
            if n % 2000 == 0:
                print(f"  {n}/{len(jobs)}")
    out = {}
    for (name, topo, mode), v in acc.items():
        I = np.array(v["I"]); lam = np.array(v["lam"])
        Iin = GEOMS[name]["Iin"]
        rec = dict(
            name=name, topo=topo, mode=mode, nrun=len(I),
            anchor="Vout=Vdd/2",
            I_mid_mean=float(I.mean()), I_mid_std=float(I.std(ddof=1)),
            I_mid_sigma_mu=float(I.std(ddof=1)/I.mean()),
            gain_mean=float(I.mean()/Iin),
            lam_mean=float(lam.mean()), lam_std=float(lam.std(ddof=1)),
            I_runs=I.tolist(), lam_runs=lam.tolist())   # every run (data of record)
        out.setdefault(name, {}).setdefault(topo, {})[mode] = rec
    with open(os.path.join(HERE, "mc_results.json"), "w") as f:
        json.dump(dict(nrun=NRUN, designs=DESIGNS, topos=TOPOS,
                       modes=list(MODES), vdd=Vdd, anchor="Vout=Vdd/2",
                       results=out), f)
    # report
    print("\n=== MC summary (sigma/mu of Iout@Vdd/2, and lambda spread) ===")
    print("%-14s %-7s %-9s %10s %10s %12s"%("design","topo","mode","gain","sig/mu(%)","lam sig"))
    for name in DESIGNS:
        for topo in TOPOS:
            for mode in MODES:
                r = out[name][topo][mode]
                print("%-14s %-7s %-9s %10.4f %10.3f %12.2e"%(
                    name, topo, mode, r["gain_mean"], r["I_mid_sigma_mu"]*100,
                    r["lam_std"]))

if __name__ == "__main__":
    main()
