"""Driver: size all 4 delay/pulse archetypes in all 3 voltage domains to a
20 ns delay/pulse-width at the nominal corner (case=0/TT, Vnom, 27 C) with
near-minimum area, then characterize the timing metric and the passthrough
edge across the full 5-corner x 3-supply x 3-temperature PVT matrix.
Writes results.json."""
import dp_lib as D
import json, math, sys

# Cap geometry (um). Chosen so the MIM area ~ the resistor area at the 20 ns
# operating point -> total RC area sits at the analytic minimum.  Identical
# across domains (the RC delay to a mid-rail Schmitt trip is supply-independent).
CL = CW = 5.36          # -> 28.7 um^2 -> ~57 fF (CMIM_HI)


def mm(rows, key):
    vals = [(r[key], r) for r in rows
            if isinstance(r.get(key), float) and not math.isnan(r[key])]
    if not vals:
        return None
    lo = min(vals, key=lambda x: x[0]); hi = max(vals, key=lambda x: x[0])
    def cond(r):
        return f"{D.CNAME[int(r['cs'])]},{r['vd']}V,{int(r['tp'])}C"
    return dict(min=lo[0], min_at=cond(lo[1]), max=hi[0], max_at=cond(hi[1]),
                n=len(vals), n_total=len(rows))


def main(domains=("1v8", "3v3", "5v0"), arches=D.ARCHES):
    results = {}
    for dkey in domains:
        dom = D.DOMAINS[dkey]
        results[dkey] = {}
        for arch in arches:
            lr, nom, achieved = D.size_lr(arch, dom, CL, CW)
            pvt = D.char_pvt(arch, dom, lr, CL, CW)
            ar = D.area(arch, dom, lr, CL, CW)
            mstat = mm(pvt, "m")
            festat = mm(pvt, "fe")
            results[dkey][arch] = dict(
                lr_um=lr, cl_um=CL, cw_um=CW, wr_um=D.WR,
                nominal_ns={k: (v * 1e9 if isinstance(v, float) else v)
                            for k, v in nom.items()},
                metric_ns=achieved * 1e9,
                area=ar,
                pvt_metric=mstat, pvt_passthrough=festat,
            )
            mt = f"{mstat['min']*1e9:.1f}..{mstat['max']*1e9:.1f}" if mstat else "n/a"
            fe = f"{festat['max']*1e9:.2f}" if festat else "n/a"
            print(f"[{dkey}] {arch:4s} lr={lr:6.2f}u  nom={achieved*1e9:5.2f}ns  "
                  f"PVT={mt}ns  pass<={fe}ns  area={ar['active_um2']:.1f}um2",
                  flush=True)
    results["_provenance"] = D.provenance({"target_ns": 20.0, "cl_um": CL, "cw_um": CW})
    with open(D.WORK / "results.json", "w") as f:
        json.dump(results, f, indent=1, default=str)
    print(f"saved results.json  [model={D.MODEL_TAG} ngspice={D.ngspice_version()}]")
    return results


if __name__ == "__main__":
    doms = sys.argv[1].split(",") if len(sys.argv) > 1 else ("1v8", "3v3", "5v0")
    arc = sys.argv[2].split(",") if len(sys.argv) > 2 else D.ARCHES
    main(doms, arc)
