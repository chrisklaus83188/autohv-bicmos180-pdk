"""Characterize the two-sided DLY cells (DLY_1V8/3V3/5V0) and MERGE the results
into the existing char.json + results.json without touching the 12 edge-
asymmetric cells.

DLY has no bypass FET, so BOTH edges are real RC delays: metric 'm' is the
rising-edge delay and 'fe' is the falling-edge delay (not a fast passthrough).
Same ngspice flow as dp_char.py -- full BSIM3 / behavioral-R-C models, full
PVT matrix (5 corners x 3 supplies x 3 temps) + 200-run Monte Carlo at TT.

Resistor length L_R is taken from the shipped cells/DLY_<D>.lib (centered
between the DLYR rise-tuned and DLYF fall-tuned values), not re-sized.
"""
import concurrent.futures as cf
import json
import re
import sys

import dp_lib as D
import dp_char as C          # reuse pvt_stat / mc_stat / nominal_from_pvt

ARCH = "DLY"
CL = CW = C.CL               # 5.36 um (same MIM cap as every other cell)
DOMS = ("1v8", "3v3", "5v0")


def lr_from_lib(dkey):
    """Read L_R (um) straight from the shipped per-cell lib -- the netlist
    authority -- so characterization uses exactly what the cell ships with."""
    name = f"DLY_{dkey.upper()}"
    for ln in (D.WORK / "cells" / f"{name}.lib").read_text().splitlines():
        if ln.strip().startswith("XR"):
            return float(re.search(r"L=([0-9.]+)u", ln).group(1))
    raise RuntimeError(f"no XR in {name}.lib")


def char_json_entry(dom, lr, pvt, mc):
    return dict(
        lr_um=lr, cl_um=CL, cw_um=CW, area=D.area(ARCH, dom, lr, CL, CW),
        supplies=dom["vlist"], temps=D.TEMPS,
        nominal=C.nominal_from_pvt(pvt, dom["vdd"]),
        pvt={k: C.pvt_stat(pvt, k) for k in C.METRICS},
        mc={k: C.mc_stat(mc, k, keep_samples=(k == "m")) for k in C.METRICS})


def results_json_entry(dom, lr, pvt):
    """Compact design-doc record (mirrors results.json), with BOTH edges kept
    explicit: pvt_rise = metric 'm', pvt_fall = metric 'fe' (also a real delay)."""
    nom = C.nominal_from_pvt(pvt, dom["vdd"])
    rise, fall = C.pvt_stat(pvt, "m"), C.pvt_stat(pvt, "fe")
    keep = ("min", "max", "min_at", "max_at", "n")
    return dict(
        lr_um=lr, cl_um=CL, cw_um=CW, wr_um=D.WR,
        area=D.area(ARCH, dom, lr, CL, CW),
        nominal_ns={"tdr": (nom.get("m") or 0) * 1e9,
                    "tdf": (nom.get("fe") or 0) * 1e9},
        metric_ns=(nom.get("m") or 0) * 1e9,
        pvt_rise={k: rise[k] for k in keep} if rise else None,
        pvt_fall={k: fall[k] for k in keep} if fall else None)


def main(threads=2, workers=3, mc_timeout=2400):
    """num_threads=2 is the per-process sweet spot; only 3 concurrent workers
    keeps contention low so each 200-iter MC finishes fast (the earlier 6-way
    run throttled and one MC hit the 900 s cap). mc_timeout adds headroom."""
    D.NUM_THREADS = threads
    jobs = ([(dk, "mc") for dk in DOMS] +      # long jobs first (run alone-ish)
            [(dk, "pvt") for dk in DOMS])

    def runjob(job):
        dk, kind = job
        dom = D.DOMAINS[dk]; lr = lr_from_lib(dk)
        if kind == "mc":
            return job, D.char_mc(ARCH, dom, lr, CL, CW, n=C.NMC, timeout=mc_timeout)
        return job, D.char_pvt(ARCH, dom, lr, CL, CW, timeout=mc_timeout)

    raw = {dk: {} for dk in DOMS}
    done = 0
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for fut in cf.as_completed([ex.submit(runjob, j) for j in jobs]):
            (dk, kind), rows = fut.result()
            raw[dk][kind] = rows; done += 1
            tag = f"DLY_{dk.upper()}"
            if kind == "mc":
                ms = C.mc_stat(rows, "m")
                print(f"[{done}/{len(jobs)}] MC  {tag:9s} rise mean={ms['mean']*1e9:.2f}ns "
                      f"sd={ms['std']*1e9:.3f}ns ({ms['rel']*100:.1f}%)", flush=True)
            else:
                pm = C.pvt_stat(rows, "m"); pf = C.pvt_stat(rows, "fe")
                print(f"[{done}/{len(jobs)}] PVT {tag:9s} rise {pm['min']*1e9:.1f}..{pm['max']*1e9:.1f}ns "
                      f"fall {pf['min']*1e9:.1f}..{pf['max']*1e9:.1f}ns", flush=True)

    # ---- merge into char.json ----
    cj = json.load(open(D.WORK / "char.json"))
    for dk in DOMS:
        dom = D.DOMAINS[dk]; lr = lr_from_lib(dk)
        cj[dk][ARCH] = char_json_entry(dom, lr, raw[dk]["pvt"], raw[dk]["mc"])
    with open(D.WORK / "char.json", "w") as f:
        json.dump(cj, f, indent=1, default=str)
    print("merged DLY into char.json")

    # ---- merge into results.json ----
    rj = json.load(open(D.WORK / "results.json"))
    for dk in DOMS:
        dom = D.DOMAINS[dk]; lr = lr_from_lib(dk)
        rj[dk][ARCH] = results_json_entry(dom, lr, raw[dk]["pvt"])
    with open(D.WORK / "results.json", "w") as f:
        json.dump(rj, f, indent=1, default=str)
    print("merged DLY into results.json")


if __name__ == "__main__":
    main(*(int(x) for x in sys.argv[1:3])) if len(sys.argv) > 1 else main()
