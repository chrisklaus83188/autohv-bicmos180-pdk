#!/usr/bin/env python3
"""Generate docs/sizing-guide.{md,json} from the sizing sweep results + analytical R/C/BJT.
Phase-3b: resistor rule defaults to RPOLY_HI (maintainer bug fix), DNMOS20 depletion row,
post-O5 sigma columns. Regenerated, not patched."""
import json, math, pathlib
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
res = HERE / "results"

vd = json.loads((res/"sizing_vdmos.json").read_text())
bs = json.loads((res/"sizing_bsim.json").read_text())
dep = {}
dp = res/"sizing_depletion.json"
if dp.exists(): dep = json.loads(dp.read_text())

g = {"_meta":{
    "purpose":"General-use sizing guide. MOS rows from the characterization harness (diode-connected "
              "mirror, gm/Id ~6); R/C/BJT analytical from the fixed sheet/density/mismatch values. "
              "TT / 27C at class-nominal supply.",
    "generated":"harness output + analytical, regenerated from the final model state (phase-3b)",
    "version":"2.0-phase3b"},
    "mos":{}, "resistors":{}, "capacitors":{}, "bjt":{}}

for src in (vd, bs):
    for dev,d in src.items():
        if dev.startswith("_"): continue
        g["mos"][dev]={"supply_V":d["supply"],
            "L_policy":("L=L_REF(8u)" if dev in ("NDMOS200","PDMOS200") else
                        ("process-min" if "DMOS" in dev else "Lmin; 2xLmin for tighter ro")),
            "mirror_points":d["points"]}
# DNMOS20 depletion row
if dep:
    g["mos"]["DNMOS20"]={"supply_V":dep.get("supply",10.0),"L_policy":"process-min (depletion)",
        "convention":"Vgs=0 self-biased current source (Idss), not a mirror-Vov device",
        "idss_per_um_uA":round(dep.get("idss_per_um_A",0)*1e6,3),
        "selfbias_points":dep.get("points",{})}

# --- resistors: RPOLY_HI default for ALL precision 1k-1M; RNWELL only as flagged alt ---
RES={"RPOLY_HI":(1200,1.5,-1400),"RPOLY_LO":(300,1.5,-100),"RNWELL":(1800,4.0,4000),
     "RNPLUS":(60,2.5,900),"RPPLUS":(110,2.5,1100)}
Wr=2.0
def rrow(lay,Rt):
    rsh,Ar,tc=RES[lay]; sq=Rt/rsh; area=sq*Wr*Wr; sig=Ar/math.sqrt(area) if area>0 else float('nan')
    return {"layer":lay,"squares":round(sq,1),"area_um2":round(area,0),"width_um":Wr,
            "sigma_dR_pct":round(sig,2),"tc1_ppm_C":tc,"drift_pct_-40_150C":round(tc*190/1e6*100,2)}
for Rt in (1e3,1e4,1e5,1e6):
    row=rrow("RPOLY_HI",Rt)              # DEFAULT: high-res poly, always
    row["note"]="RPOLY_HI is the precision default (stable, negative TC)."
    alt=rrow("RNWELL",Rt)               # flagged area-saving alternative
    alt["warning"]=("area-saving alternative ONLY: +76%% TC drift over -40..150C and a large "
                    "structural voltage coefficient -- keep off signal nodes.")
    row["rnwell_alt"]=alt
    g["resistors"][f"{Rt:g}"]=row

# --- capacitors ---
CAP={"CMIM_HI":(2.0,0.75),"CMIM_STD":(1.0,0.75),"CMOM":(0.35,1.5),"CFRINGE":(0.18,1.5)}
for Ct in (100e-15,1e-12,10e-12):
    best=None
    for lay,(dens,Ac) in CAP.items():
        area=Ct*1e15/dens; side=math.sqrt(area); sig=Ac/math.sqrt(area)
        bits=round(-math.log2(sig/100*3.46),1) if sig>0 else 0
        cand=(lay,round(area,1),round(side,1),round(sig,3),bits)
        if best is None or area<best[1]: best=cand
    g["capacitors"][f"{Ct*1e12:g}pF"]={"layer":best[0],"area_um2":best[1],"side_um":best[2],
        "sigma_dC_pct":best[3],"matching_bits":best[4]}

# --- BJT ---
VT=0.02585
BJTIS={"NPN_LV":(2e-16,140),"PNP_LAT":(8e-16,35),"NPN_HV":(4e-17,80),"PNP_HV":(1e-16,18)}
for dev,(iss,beta) in BJTIS.items():
    pts={}
    for Ic in (10e-6,100e-6,1e-3):
        vbe=VT*math.log(Ic/(iss*1)); sig=(0.012/3)*VT*1000*math.sqrt(2)
        pts[f"{Ic*1e6:g}uA"]={"AREA_mult":1,"Vbe_V":round(vbe,3),"beta":beta,
                              "pair_sigma_dVbe_mV":round(sig,2),"eff_fT_GHz_note":"D4: ~1 GHz-class"}
    g["bjt"][dev]=pts

(REPO/"docs"/"sizing-guide.json").write_text(json.dumps(g,indent=1),newline="\n")
print("sizing-guide.json:", len(g["mos"]),"MOS,",len(g["resistors"]),"R,",
      len(g["capacitors"]),"C,",len(g["bjt"]),"BJT")
