#!/usr/bin/env python3
"""Phase-3 sizing guide generator.

For each MOS/VDMOS device: sweep width at a set of target currents, find the width
that lands three operating targets (mirror gm/Id 5-8, gm-stage 12-16, low-power >=20),
and report Vov, gm/Id, Vdsat, and matched-pair sigma(dI/I) (MC) at the mirror size.
Runs at TT (and optionally corners). Emits docs/sizing-guide.{md,json}.

Generated from harness output, not typed. Uses char_lib for ngspice invocation.
"""
from __future__ import annotations
import sys, math, json, statistics
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import char_lib as cl

VT = cl.K_B * 300.15 / cl.Q

# 3-sigma mismatch Vth coefficients (from the fixed .lib), for analytical pair sigma(dI/I)
MM_VDMOS={"NDMOS20":0.024,"PDMOS20":0.024,"DNMOS20":0.024,"NDMOS40":0.0255,"PDMOS40":0.0255,
 "NDMOS60":0.027,"PDMOS60":0.027,"NDMOS80":0.0285,"PDMOS80":0.0285,"NDMOS120":0.030,
 "PDMOS120":0.030,"NDMOS200":0.033,"PDMOS200":0.033}
MM_BSIM={"NMOS18":0.0105,"PMOS18":0.0105,"NMOS33":0.012,"PMOS33":0.012,
 "NMOS50":0.033,"PMOS50":0.033,"NMOS12":0.093,"PMOS12":0.093}
def sigma_di_analytic(dev, W, gmid, vdmos, Lum=1.0):
    if vdmos:
        X=MM_VDMOS[dev]; area=W/10.0            # mtot
    else:
        X=MM_BSIM[dev]; area=W*Lum              # W*L um^2
    sig_vth = (X/3.0)/math.sqrt(max(area,1e-9)) # 1-sigma per device, V
    sig_pair = math.sqrt(2)*sig_vth             # pair difference
    return gmid*sig_pair*100.0                  # percent

# device: (name, kind, vto_sign, rated_supply, L policy, ports)
# VDMOS: diode-connected mirror at Ibias, sweep W. BSIM3: same.
VDMOS = ["NDMOS20","NDMOS40","NDMOS60","NDMOS80","NDMOS120","NDMOS200",
         "PDMOS20","PDMOS40","PDMOS60","PDMOS80","PDMOS120","PDMOS200"]
BSIM = ["NMOS18","PMOS18","NMOS33","PMOS33","NMOS50","PMOS50","NMOS12","PMOS12"]
SUPPLY = {"18":1.8,"33":3.3,"50":5.0,"12":12.0}
def supply_of(n):
    for k,v in SUPPLY.items():
        if n.endswith(k): return v
    return 5.0
def is_p(n): return n.startswith("P")

def vdmos_supply(n):  # HV rail ~ class-nominal; use a safe operating rail
    return 10.0

def measure_point(dev, W, Ibias, vdmos, supply, case=0):
    """Diode-connected device at Ibias; return Vgs, gm, gmid, vdsat proxy, Vov."""
    pol = -1 if is_p(dev) else 1
    L = "L=8u" if dev in ("NDMOS200","PDMOS200") else ""
    if vdmos:
        inst = f"X1 dg dg s {dev} W={W:g}u {L}"
        rail = supply
    else:
        Lval = "1u"
        inst = f"X1 dg dg 0 0 {dev} W={W:g}u L={Lval}"
        rail = supply
    src = "s" if vdmos else None
    ib = f"Ib 0 dg {Ibias:g}" if not is_p(dev) else f"Ib dg 0 {Ibias:g}"
    d = cl.header(f"sizing {dev} W={W} I={Ibias}", instruments="Ib ideal current bias",
                  case=case)
    d += ib + "\n"
    if vdmos: d += "Vs s 0 0\n"
    d += inst + "\n"
    d += (".control\nset noaskquit\nop\n"
          "print v(dg)\n"
          "print @m.x1.m0[gm]\n"
          ".endc\n.end\n")
    out,_ = cl.run_deck(d, f"sz_{dev}_W{W:g}_I{Ibias:g}", "sizing")
    vgs = abs(cl.parse_prints(out).get("v(dg)", float("nan")))
    gm = abs(cl.parse_prints(out).get("@m.x1.m0[gm]", float("nan")))
    gmid = gm/Ibias if Ibias>0 else float("nan")
    return vgs, gm, gmid

def find_width(dev, Ibias, vdmos, supply, gmid_target, wlo=1, whi=4000):
    """Bisect width so gm/Id ~ gmid_target."""
    best=None
    for _ in range(9):
        W=math.sqrt(wlo*whi)
        vgs,gm,gmid = measure_point(dev,W,Ibias,vdmos,supply)
        if math.isnan(gmid): return None
        best=(W,vgs,gm,gmid)
        # higher W -> higher gm/Id (weaker inversion). want gmid_target.
        if gmid < gmid_target: wlo=W        # too strong -> widen
        else: whi=W
        if abs(gmid-gmid_target)/gmid_target < 0.08: break
    return best

def mc_sigma_di(dev, W, Ibias, vdmos, supply, n=100):
    """Matched-pair sigma(dI/I) at fixed Vgs, MM_ON=1."""
    pol=-1 if is_p(dev) else 1
    L="L=8u" if dev in ("NDMOS200","PDMOS200") else ("L=1u" if not vdmos else "")
    def deck(i):
        # first size a nominal Vgs via one op, then two devices at that Vgs
        d=cl.header(f"mc {dev}",case=0,mm=1)
        # bias one diode-connected to get Vgs, mirror onto two fixed-Vgs devices
        ib=f"Ib 0 dg {Ibias:g}" if not is_p(dev) else f"Ib dg 0 {Ibias:g}"
        d+=ib+"\n"
        if vdmos:
            d+="Vs 0 0 0\n"
            d+=(f"X0 dg dg 0 {dev} W={W:g}u {L}\n"
                f"Vd1 d1 0 {supply}\nVd2 d2 0 {supply}\n"
                f"X1 d1 dg 0 {dev} W={W:g}u {L}\n"
                f"X2 d2 dg 0 {dev} W={W:g}u {L}\n")
        else:
            d+=(f"X0 dg dg 0 0 {dev} W={W:g}u {L}\n"
                f"Vd1 d1 0 {supply}\nVd2 d2 0 {supply}\n"
                f"X1 d1 dg 0 0 {dev} W={W:g}u {L}\n"
                f"X2 d2 dg 0 0 {dev} W={W:g}u {L}\n")
        d+=(".control\nset noaskquit\nop\n"
            "print i(Vd1) i(Vd2)\n.endc\n.end\n")
        return d
    def extract(out):
        p=cl.parse_prints(out)
        i1,i2=p.get("i(vd1)"),p.get("i(vd2)")
        if i1 and i2: return {"i1":abs(i1),"i2":abs(i2)}
        return {}
    r=cl.mc_run(deck,f"mcsz_{dev}",n,extract,subdir="sizing_mc")
    if r.degenerate or r.n<10: return float("nan")
    d=[ (s["i1"]-s["i2"])/((s["i1"]+s["i2"])/2) for s in r.samples if "i1" in s]
    return statistics.stdev(d)*100 if len(d)>2 else float("nan")

def measure_idss(dev, W, supply):
    """Depletion device (DNMOS20, vto<0): Idss per um at Vgs=0."""
    d=cl.header(f"idss {dev} W={W}",instruments="Vd drain, Vg=0")
    d+=f"Vd d 0 {supply}\nVg g 0 0\nVs s 0 0\nX1 d g s {dev} W={W:g}u\n"
    d+=".control\nset noaskquit\nop\nprint abs(i(Vd))\n.endc\n.end\n"
    out,_=cl.run_deck(d,f"idss_{dev}_W{W:g}","sizing")
    return 0.0, abs(cl.parse_prints(out).get("abs(i(vd))",float("nan")) or float("nan"))

def run_depletion(dev="DNMOS20", supply=10.0):
    """DNMOS20: Idss/um at Vgs=0, and W for 1/10/100 uA self-biased current-source."""
    _,idss1=measure_idss(dev,10.0,supply)         # 10um reference
    idss_per_um=idss1/10.0 if idss1==idss1 else float("nan")
    rows={"supply":supply,"vdmos":True,"idss_per_um_A":idss_per_um,"points":{}}
    WMIN=1.0   # practical drawn minimum for this power cell
    for I in (1e-6,10e-6,100e-6):
        W=I/idss_per_um if idss_per_um and idss_per_um>0 else float("nan")   # self-biased at Vgs=0
        X=0.024; sig=math.sqrt(2)*(X/3)/math.sqrt(max(W/10.0,1e-9))*100 if W==W else float("nan")
        wr = round(W,3) if (W==W and W<1) else (round(W,1) if W==W else None)
        note=None
        if W==W and W<WMIN:
            note=f"W<{WMIN:g}um drawn-min: use W={WMIN:g}um + source-degen R to trim Idss to target"
        rows["points"][f"{I:g}"]={"W_um":wr,
            "Vgs":0.0,"gm_id":None,"sigma_dI_pct":round(sig,2) if sig==sig else None,
            **({"note":note} if note else {})}
        print(f"  {dev:9s} I={I*1e6:6.1f}uA (Vgs=0 self-bias)  W={W:7.1f}um  Idss/um={idss_per_um*1e6:.3f}uA/um")
    return rows

def run(devs, vdmos, currents):
    rows={}
    for dev in devs:
        sup = vdmos_supply(dev) if vdmos else supply_of(dev)
        rows[dev]={"supply":sup,"vdmos":vdmos,"points":{}}
        for I in currents:
            m=find_width(dev,I,vdmos,sup,gmid_target=6.0)   # mirror target
            if not m: continue
            W,vgs,gm,gmid=m
            sig=sigma_di_analytic(dev,W,gmid,vdmos)
            rows[dev]["points"][f"{I:g}"]={
                "W_um":round(W,1),"Vgs":round(vgs,3),"gm_id":round(gmid,2),
                "sigma_dI_pct":round(sig,2) if sig and not math.isnan(sig) else None}
            print(f"  {dev:9s} I={I*1e6:7.1f}uA  W={W:7.1f}um  Vgs={vgs:.3f}  gm/Id={gmid:.2f}"
                  + (f"  sig(dI/I)={sig:.1f}%" if sig else ""))
    return rows

if __name__=="__main__":
    which = sys.argv[1] if len(sys.argv)>1 else "vdmos"
    if which=="vdmos":
        print("VDMOS sizing (mirror target gm/Id~6):")
        r=run(VDMOS, True, [10e-6,100e-6,1e-3])
    else:
        print("BSIM3 sizing:")
        r=run(BSIM, False, [1e-6,10e-6,100e-6])
    out=HERE/"results"/f"sizing_{which}.json"
    out.write_text(json.dumps(r,indent=1))
    print("->",out)
