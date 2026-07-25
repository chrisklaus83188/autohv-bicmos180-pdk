"""Full characterization driver: for every cell (sized L_R taken from
results.json) run the enriched PVT sweep + a 200-run Monte Carlo at the
typical corner (PROC_ON=1, MM_ON=1). Writes char.json with PVT min/max
envelopes, MC statistics, and the raw MC delay/width samples (for histograms).
Pure ngspice; full BSIM3 / VDMOS / behavioral-R-C models, no simplifications."""
import dp_lib as D
import json, math, statistics, sys

NMC = 200
CL = CW = 5.36
METRICS = ("m", "fe", "tr", "tf")     # primary, passthrough, out-rise, out-fall


def fin(rows, key):
    return [r[key] for r in rows
            if isinstance(r.get(key), float) and not math.isnan(r[key])]


def pvt_stat(rows, key):
    vals = [(r[key], r) for r in rows
            if isinstance(r.get(key), float) and not math.isnan(r[key])]
    if not vals:
        return None
    lo = min(vals, key=lambda x: x[0]); hi = max(vals, key=lambda x: x[0])
    def cond(r):
        return f"{D.CNAME[int(r['cs'])]},{r['vd']}V,{int(r['tp'])}C"
    return dict(min=lo[0], max=hi[0], min_at=cond(lo[1]), max_at=cond(hi[1]),
                n=len(vals))


def mc_stat(rows, key, keep_samples=False):
    v = fin(rows, key)
    if len(v) < 2:
        return None
    mean = statistics.mean(v); sd = statistics.fmean  # placeholder
    sd = statistics.stdev(v)
    v_sorted = sorted(v)
    def pct(p):
        k = (len(v_sorted) - 1) * p
        f = math.floor(k); c = math.ceil(k)
        if f == c:
            return v_sorted[int(k)]
        return v_sorted[f] * (c - k) + v_sorted[c] * (k - f)
    d = dict(n=len(v), mean=mean, std=sd, rel=sd / mean if mean else None,
             min=min(v), max=max(v), p1=pct(0.01), p50=pct(0.50), p99=pct(0.99))
    if keep_samples:
        d["samples"] = v
    return d


def nominal_from_pvt(rows, vdd):
    for r in rows:
        if int(r.get("cs", -1)) == 0 and abs(r.get("vd", -9) - vdd) < 1e-6 \
           and int(r.get("tp", -999)) == 27:
            return {k: (r[k] if isinstance(r.get(k), float) else None) for k in METRICS}
    return {}


def main(domains=("1v8", "3v3", "5v0"), arches=D.ARCHES, workers=8, threads=2):
    """Run every (cell, kind) ngspice job concurrently. Each ngspice uses
    `threads` OpenMP threads (.option num_threads); with `workers` processes,
    threads*workers ~ slightly above the core count was fastest in a sweep
    (num_threads=2 x 8 workers ~ 5 solves/s on a 12-core box). MC jobs (200
    iters) are the long pole, so they are submitted first."""
    import concurrent.futures as cf
    D.NUM_THREADS = threads
    src = json.load(open(D.WORK / "results.json"))
    jobs = []   # (dkey, arch, kind, lr)
    for dkey in domains:
        for arch in arches:
            lr = float(src[dkey][arch]["lr_um"])
            jobs.append((dkey, arch, "mc", lr))   # long jobs first
    for dkey in domains:
        for arch in arches:
            lr = float(src[dkey][arch]["lr_um"])
            jobs.append((dkey, arch, "pvt", lr))

    def runjob(job):
        dkey, arch, kind, lr = job
        dom = D.DOMAINS[dkey]
        if kind == "mc":
            return job, D.char_mc(arch, dom, lr, CL, CW, n=NMC)
        return job, D.char_pvt(arch, dom, lr, CL, CW)

    raw = {(d, a): {} for d in domains for a in arches}
    done = 0
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for fut in cf.as_completed([ex.submit(runjob, j) for j in jobs]):
            (dkey, arch, kind, lr), rows = fut.result()
            raw[(dkey, arch)][kind] = rows
            done += 1
            tag = f"{arch}_{dkey.upper()}"
            if kind == "mc":
                ms = mc_stat(rows, "m")
                print(f"[{done:2d}/{len(jobs)}] MC  {tag:9s} "
                      f"mean={ms['mean']*1e9:.2f}ns sd={ms['std']*1e9:.3f}ns "
                      f"({ms['rel']*100:.1f}%) range {ms['min']*1e9:.1f}..{ms['max']*1e9:.1f}ns",
                      flush=True)
            else:
                pm = pvt_stat(rows, "m")
                print(f"[{done:2d}/{len(jobs)}] PVT {tag:9s} "
                      f"m={pm['min']*1e9:.1f}..{pm['max']*1e9:.1f}ns "
                      f"(slow {pm['max_at']})", flush=True)

    out = {}
    for dkey in domains:
        dom = D.DOMAINS[dkey]; out[dkey] = {}
        for arch in arches:
            lr = float(src[dkey][arch]["lr_um"])
            pvt = raw[(dkey, arch)]["pvt"]; mc = raw[(dkey, arch)]["mc"]
            out[dkey][arch] = dict(
                lr_um=lr, cl_um=CL, cw_um=CW, area=D.area(arch, dom, lr, CL, CW),
                supplies=dom["vlist"], temps=D.TEMPS,
                nominal=nominal_from_pvt(pvt, dom["vdd"]),
                pvt={k: pvt_stat(pvt, k) for k in METRICS},
                mc={k: mc_stat(mc, k, keep_samples=(k == "m")) for k in METRICS})
    out["_provenance"] = D.provenance({"n_mc": NMC, "cl_um": CL, "cw_um": CW})
    with open(D.WORK / "char.json", "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"saved char.json  [model={D.MODEL_TAG} ngspice={D.ngspice_version()} n_mc={NMC}]")
    return out


if __name__ == "__main__":
    doms = sys.argv[1].split(",") if len(sys.argv) > 1 else ("1v8", "3v3", "5v0")
    arc = sys.argv[2].split(",") if len(sys.argv) > 2 else D.ARCHES
    main(doms, arc)
