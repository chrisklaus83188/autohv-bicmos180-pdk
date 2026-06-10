"""Driver: size all 8 cells in all 3 domains to VM=VDD/2 with Cin<=5fF,
then characterize VM, rise/fall across PVT. Writes results.json."""
import async_lib as A
import json, math, sys

CAP_MODEL_TGT = 4.5     # predicted-cap sizing target (fF); rail-avg comes ~10% under
CAP_HARD      = 5.0     # hard limit on measured rail-avg Cin (fF)
WMIN = {"1v8":0.22, "3v3":0.30, "5v0":0.40}
K_BUF = 3.0             # output-stage drive multiplier for BUF
K_AOI = 2.0             # output-inverter drive multiplier for AND2/OR2
RLIST = [0.3,0.5,0.8,1.2,1.8,2.6,3.6,5.0,7.0,10,14,19,25,32]
CELLS = ["INV","BUF","NAND2","NOR2","AND2","OR2","XOR2","XNOR2"]

def interp_ratio(rows, target):
    """rows: list of {'R':, 'vm':}. Find R where vm==target (vm increasing in R)."""
    pts = sorted((r["R"], r["vm"]) for r in rows if isinstance(r.get("vm"), float))
    for (r0,v0),(r1,v1) in zip(pts, pts[1:]):
        if (v0-target)*(v1-target) <= 0 and v1!=v0:
            return r0 + (target-v0)*(r1-r0)/(v1-v0)
    # no bracket: clamp to nearest endpoint
    if not pts: return None
    if abs(pts[0][1]-target) < abs(pts[-1][1]-target): return pts[0][0]
    return pts[-1][0]

def device_widths(cell, W):
    """Return (Nlist, Plist) of device widths (um) for area accounting."""
    if cell=="INV":  return [W["wn"]],[W["wp"]]
    if cell=="BUF":  return [W["wn1"],W["wn2"]],[W["wp1"],W["wp2"]]
    if cell in ("NAND2","NOR2"): return [W["wn"]]*2,[W["wp"]]*2
    if cell in ("AND2","OR2"):   return [W["wn"]]*2+[W["wni"]],[W["wp"]]*2+[W["wpi"]]
    if cell in ("XOR2","XNOR2"):
        return [W["wni"]]*2+[W["wn"]]*4, [W["wpi"]]*2+[W["wp"]]*4
    raise ValueError(cell)

def area(cell, dom, W):
    N,P = device_widths(cell, W)
    Lu = dom["L"]
    active = sum(w*Lu for w in N+P)                 # um^2 active gate area
    h = max(P) + max(N) + dom["hov"]                # cell height (um)
    w = A.NCOLS[cell]*dom["cpp"]                     # cell width (um)
    return dict(active_um2=active, layout_um2=h*w, cell_h=h, cell_w=w,
                ndev=len(N)+len(P))

def measure_caps(cell, dom, W):
    caps = {pin: A.deck_cap_pin(cell, dom, W, pin) for pin in A.CELL_INPUTS[cell]}
    return caps, max(caps.values())

def size_base(cell, dkey, dom, gn, gp, RINV):
    """Ratio-search + cap-budget sizing for a 'primitive' cell
    (INV/NAND2/NOR2/XOR2/XNOR2). Cap is a hard limit: if centering VM pushes
    Cin>5fF at min width, back off the P/N ratio (VM drifts off mid-supply)."""
    rows = A.deck_ratio(cell, dom, K=0, RINV=RINV, Rlist=RLIST)
    Rideal = interp_ratio(rows, dom["vdd"]/2)
    Rstar = Rideal
    for _ in range(8):
        if cell in ("XOR2","XNOR2"):
            Ccoef = 2*gn + gp*(RINV+Rstar)
        else:
            Ccoef = gn + gp*Rstar
        scale = max(CAP_MODEL_TGT/Ccoef, WMIN[dkey])
        W = A.widths_final(cell, scale, Rstar, 0, RINV)
        caps, cmax = measure_caps(cell, dom, W)
        if cmax <= CAP_HARD or Rstar < 1.0:
            break
        Rstar *= 0.90        # cap-limited: shrink PMOS, VM drifts below mid
    return dict(R=Rstar, Rideal=Rideal, scale=scale, W=W, caps=caps,
                cap_limited=(abs(Rstar-Rideal) > 1e-6), ratio_rows=rows)

def compose_cell(cell, dom, base, RINV, scale_inv):
    """Build BUF/AND2/OR2 by composing already-sized primitives."""
    si, Ri = scale_inv, RINV
    if cell=="BUF":   # INV -> K*INV
        W = dict(wn1=si, wp1=si*Ri, wn2=K_BUF*si, wp2=K_BUF*si*Ri)
        src="INV"
    elif cell=="AND2":  # NAND2 -> INV
        nb=base["NAND2"]["W"]; W=dict(wn=nb["wn"], wp=nb["wp"], wni=si, wpi=si*Ri)
        src="NAND2"
    elif cell=="OR2":   # NOR2 -> INV
        nb=base["NOR2"]["W"]; W=dict(wn=nb["wn"], wp=nb["wp"], wni=si, wpi=si*Ri)
        src="NOR2"
    caps, cmax = measure_caps(cell, dom, W)
    return dict(R=base.get(src,{}).get("R"), W=W, caps=caps, cap_limited=False)

def characterize(cell, dom, W):
    vm = A.deck_vm_pvt(cell, dom, W)
    tr = A.deck_tran_pvt(cell, dom, W)
    def mm(rows, key):
        vals=[(r[key], r) for r in rows if isinstance(r.get(key),float) and not math.isnan(r[key])]
        if not vals: return None
        lo=min(vals,key=lambda x:x[0]); hi=max(vals,key=lambda x:x[0])
        return dict(min=lo[0], min_at=cond(lo[1]), max=hi[0], max_at=cond(hi[1]))
    out=dict()
    # VM per config: absolute volts and as fraction of supply
    for r in vm:
        if isinstance(r.get("vm"),float): r["vmfrac"]=r["vm"]/r["vd"]
    cfgs=set(r.get("cfg") for r in vm)
    out["vm"]={}
    for c in cfgs:
        sub=[r for r in vm if r.get("cfg")==c]
        m=mm(sub,"vm")
        if m:
            mf=mm(sub,"vmfrac"); m["fracmin"]=mf["min"]; m["fracmax"]=mf["max"]
        out["vm"][c]=m
    out["trise"]=mm(tr,"trise")
    out["tfall"]=mm(tr,"tfall")
    out["vm_rows"]=vm; out["tr_rows"]=tr
    return out

def cond(r):
    return f"{A.CNAME[int(r['cs'])]},{r['vd']}V,{int(r['tp'])}C"

def main(domains=("1v8","3v3","5v0"), cells=CELLS):
    results={}
    for dkey in domains:
        dom=A.DOMAINS[dkey]
        gn,gp=A.measure_gnp(dom)
        base={}
        # 1) primitives needing independent sizing
        inv = size_base("INV", dkey, dom, gn, gp, RINV=2.0)
        RINV, scale_inv = inv["R"], inv["scale"]
        base["INV"]=inv
        for cell in ("NAND2","NOR2","XOR2","XNOR2"):
            base[cell]=size_base(cell, dkey, dom, gn, gp, RINV)
        # 2) composed cells
        for cell in ("BUF","AND2","OR2"):
            base[cell]=compose_cell(cell, dom, base, RINV, scale_inv)
        # 3) characterize + record
        results.setdefault(dkey,{})["_meta"]=dict(gn=gn,gp=gp,RINV=RINV,scale_inv=scale_inv)
        for cell in cells:
            s=base[cell]
            ch=characterize(cell, dom, s["W"])
            ar=area(cell, dom, s["W"])
            results[dkey][cell]=dict(R=s.get("R"), Rideal=s.get("Rideal"),
                cap_limited=s.get("cap_limited",False), W=s["W"], caps=s["caps"],
                area=ar, vm=ch["vm"], trise=ch["trise"], tfall=ch["tfall"])
            cmax=max(s["caps"].values())
            trmax=ch["trise"]["max"]*1e12 if ch["trise"] else float('nan')
            tfmax=ch["tfall"]["max"]*1e12 if ch["tfall"] else float('nan')
            vmn=ch["vm"]
            anyc=next(iter(vmn)); vmrep=vmn[anyc]
            vmtxt=f"{vmrep['min']/dom['vdd']:.2f}-{vmrep['max']/dom['vdd']:.2f}Vdd" if vmrep else "n/a"
            print(f"[{dkey}] {cell:6s} R={s.get('R') and round(s['R'],2)} "
                  f"Cin<={cmax:.2f}fF VM/Vdd={vmtxt} area={ar['layout_um2']:.2f}um2 "
                  f"tr<={trmax:.0f}ps tf<={tfmax:.0f}ps", flush=True)
    with open(A.os.path.join(A.WORK,"results.json"),"w") as f:
        json.dump(results, f, indent=1, default=str)
    print("saved results.json")
    return results

if __name__=="__main__":
    doms = sys.argv[1].split(",") if len(sys.argv)>1 else ("1v8","3v3","5v0")
    cls  = sys.argv[2].split(",") if len(sys.argv)>2 else CELLS
    main(doms, cls)
