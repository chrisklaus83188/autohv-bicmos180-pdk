#!/usr/bin/env python3
"""Generate docs/sizing-guide.{md,json} from the sizing sweep results + analytical R/C/BJT.
Phase-3b: resistor rule defaults to RPOLY_HI (maintainer bug fix), DNMOS20 depletion row,
post-O5 sigma columns. Regenerated, not patched."""
import json, math, pathlib
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[1]
res = HERE / "results"

# --- v2.2-defaults: fabrication floor + analog (matched-use) floor ------------
VDMOS_WMIN = 3.0            # um, fabrication min gate finger (device_limits [grounded])
BSIM_WMIN = {"NMOS18":0.22,"PMOS18":0.22,"NMOS33":0.30,"PMOS33":0.30,
             "NMOS50":0.40,"PMOS50":0.40,"NMOS12":0.22,"PMOS12":0.22}
MOS_ANALOG_THRESH = 20.0   # % sigma(dI/I) matched-pair floor for MOS
PASSIVE_ANALOG_THRESH = 1.0  # % sigma(dR/R, dC/C) matched floor for passives
# 3-sigma Vth mismatch coefficients (same source as sizing_guide.py)
MM_VDMOS={"NDMOS20":0.024,"PDMOS20":0.024,"DNMOS20":0.024,"NDMOS40":0.0255,"PDMOS40":0.0255,
 "NDMOS60":0.027,"PDMOS60":0.027,"NDMOS80":0.0285,"PDMOS80":0.0285,"NDMOS120":0.030,
 "PDMOS120":0.030,"NDMOS200":0.033,"PDMOS200":0.033}
MM_BSIM={"NMOS18":0.0105,"PMOS18":0.0105,"NMOS33":0.012,"PMOS33":0.012,
 "NMOS50":0.033,"PMOS50":0.033,"NMOS12":0.093,"PMOS12":0.093}

def analog_W_mos(dev, gmid, L_um, vdmos):
    """Min matched-pair W where sigma(dI/I) crosses MOS_ANALOG_THRESH (20%), at this
    device's operating gm/Id. sigma_pair = gmid*sqrt(2)*(X/3)/sqrt(area)*100. Returns W (um)."""
    X = MM_VDMOS.get(dev) if vdmos else MM_BSIM.get(dev)
    if not X or not gmid or gmid != gmid:
        return None
    area = (gmid*math.sqrt(2)*(X/3.0)*100.0/MOS_ANALOG_THRESH)**2   # um^2 (BSIM) or mtot (VDMOS)
    W = 10.0*area if vdmos else area/max(L_um, 1e-9)                # VDMOS area=W/10 -> W=10*area
    return round(W, 2)

def clamp_W(W, wmin):
    """Fab-floor clamp; returns (W_listed, clamped_bool)."""
    if W is None or W != W:
        return W, False
    return (round(wmin, 2), True) if W < wmin else (W, False)

def sigma_di_at(dev, W, gmid, vdmos, L_um):
    """Matched-pair sigma(dI/I) % at width W (same analytic form as sizing_guide.py).
    Used to recompute sigma when a mirror width is Wmin-clamped (larger area = better match)."""
    X = MM_VDMOS.get(dev) if vdmos else MM_BSIM.get(dev)
    if not X or not gmid or gmid != gmid or not W:
        return None
    area = (W/10.0) if vdmos else (W*L_um)
    return round(gmid*math.sqrt(2)*(X/3.0)/math.sqrt(max(area,1e-9))*100.0, 2)

vd = json.loads((res/"sizing_vdmos.json").read_text())
bs = json.loads((res/"sizing_bsim.json").read_text())
dep = {}
dp = res/"sizing_depletion.json"
if dp.exists(): dep = json.loads(dp.read_text())

g = {"_meta":{
    "purpose":"General-use sizing guide. MOS rows from the characterization harness (diode-connected "
              "mirror, gm/Id ~6); R/C/BJT analytical from the fixed sheet/density/mismatch values. "
              "TT / 27C at class-nominal supply.",
    "generated":"harness output + analytical; v2.2-defaults added fab-Wmin clamp + analog(matched) floor column",
    "version":"5.0-v2.2-defaults"},
    "mos":{}, "resistors":{}, "capacitors":{}, "bjt":{}}

for src in (vd, bs):
    for dev,d in src.items():
        if dev.startswith("_"): continue
        vdmos = "DMOS" in dev
        wmin = VDMOS_WMIN if vdmos else BSIM_WMIN.get(dev, 0.22)
        L_um = 8.0 if dev in ("NDMOS200","PDMOS200") else 1.0
        pts = {}
        for k, p in d["points"].items():
            q = dict(p)
            Wc, clamped = clamp_W(p.get("W_um"), wmin)
            q["W_um"] = Wc
            if clamped:
                q["wmin_clamped"] = True
                # recompute sigma at the (larger) clamped area; gm/Id runs richer at
                # fixed I but the area gain dominates matching -- listed sigma is a mild
                # upper bound (holds the gm/Id-6 value).
                rs = sigma_di_at(dev, Wc, p.get("gm_id"), vdmos, L_um)
                if rs is not None:
                    q["sigma_dI_pct"] = rs
                q["note"] = (f"Wmin-clamped to fab floor {wmin:g}um (gm/Id-6 width was "
                             f"{p['W_um']}um < floor); at {wmin:g}um the mirror runs richer than "
                             f"gm/Id~6 -- add source degeneration to trim.")
            pts[k] = q
        lo_k = min(d["points"], key=lambda x: float(x))
        aW = analog_W_mos(dev, d["points"][lo_k].get("gm_id"), L_um, vdmos)
        g["mos"][dev]={"supply_V":d["supply"],
            "L_policy":("L=L_REF(8u)" if dev in ("NDMOS200","PDMOS200") else
                        ("process-min" if vdmos else "L=1.0um (2xLmin-class, analog default)")),
            "fab_Wmin_um": wmin,
            "analog_min_W_um": aW,   # min matched W where sigma(dI/I) crosses 20% at lowest-I gm/Id
            "mirror_points":pts}
# DNMOS20 depletion row (clamp self-bias W to the 3um VDMOS fab floor)
if dep:
    dpts = {}
    for k, p in dep.get("points", {}).items():
        q = dict(p)
        Wc, clamped = clamp_W(p.get("W_um"), VDMOS_WMIN)
        q["W_um"] = Wc
        if clamped:
            q["note"] = (f"W<{VDMOS_WMIN:g}um: clamp to fab floor {VDMOS_WMIN:g}um + source-degen R "
                         f"to trim Idss to target")
        dpts[k] = q
    g["mos"]["DNMOS20"]={"supply_V":dep.get("supply",10.0),"L_policy":"process-min (depletion)",
        "convention":"Vgs=0 self-biased current source (Idss), not a mirror-Vov device",
        "idss_per_um_uA":round(dep.get("idss_per_um_A",0)*1e6,3),
        "fab_Wmin_um": VDMOS_WMIN,
        "selfbias_points":dpts}

# --- resistors: RPOLY_HI default for ALL precision 1k-1M; RNWELL only as flagged alt ---
RES={"RPOLY_HI":(1200,1.5,-1400),"RPOLY_LO":(300,1.5,-100),"RNWELL":(1800,4.0,4000),
     "RNPLUS":(60,2.5,900),"RPPLUS":(110,2.5,1100)}
Wr=2.0
def rrow(lay,Rt):
    rsh,Ar,tc=RES[lay]; sq=Rt/rsh; area=sq*Wr*Wr; sig=Ar/math.sqrt(area) if area>0 else float('nan')
    amin=round(Ar**2/(PASSIVE_ANALOG_THRESH**2),2)   # area (um2) where sigma(dR/R) = 1%
    return {"layer":lay,"squares":round(sq,1),"area_um2":round(area,0),"width_um":Wr,
            "sigma_dR_pct":round(sig,2),"tc1_ppm_C":tc,"drift_pct_-40_150C":round(tc*190/1e6*100,2),
            "analog_min_area_um2":amin}
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
        amin=round(Ac**2/(PASSIVE_ANALOG_THRESH**2),2)   # area where sigma(dC/C)=1%
        cand=(lay,round(area,1),round(side,1),round(sig,3),bits,amin)
        if best is None or area<best[1]: best=cand
    g["capacitors"][f"{Ct*1e12:g}pF"]={"layer":best[0],"area_um2":best[1],"side_um":best[2],
        "sigma_dC_pct":best[3],"matching_bits":best[4],"analog_min_area_um2":best[5]}

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

# --- markdown assembly (phase-4 Step 3: ONE correct writer; JSON is the source of truth) ---
# Sections are emitted strictly in order: MOS mirror table -> DNMOS20 depletion ->
# resistors -> capacitors -> BJT. No interleave, no duplicated rows.
def _mirror_cells(pts):
    cells=[]
    for k in sorted(pts,key=lambda x:float(x)):
        p=pts[k]; I=float(k)*1e6; sig=p.get("sigma_dI_pct")
        sig_s=f"{sig}%" if sig is not None else "n/a"
        star=" \\*" if p.get("wmin_clamped") else ""
        cells.append(f"{I:g}uA: {p['W_um']}um{star} / {p.get('Vgs','')} / {p.get('gm_id','')} / {sig_s}")
    while len(cells)<3: cells.append("")
    return cells

md=[]
md.append("# Sizing Guide -- AutoHV BiCMOS180 PDK\n")
md.append("**What sizes make sense at uA-level currents and nominal supplies.** MOS rows from the")
md.append("characterization harness (diode-connected mirror, gm/Id ~ 6); R/C/BJT analytical from the")
md.append("grounded sheet/density/mismatch values. TT / 27 C at class-nominal supply. Regenerated from the")
md.append("final phase-4 model state -- **no known-optimistic columns**. BSIM3 rows are drawn at")
md.append("**L = 1.0 um (2xLmin-class, analog default)**; VDMOS at the process cell (200 V at L_REF = 8 um).\n")
md.append("**How to choose:** MOS -- your device + bias current gives the **mirror** width W (gm/Id ~ 6);")
md.append("for a gm stage size ~2x narrower (gm/Id 12-16), low-power ~4x wider (>= 20). sigma(dI/I) is the")
md.append("matched-pair 1-sigma; halve it by 4x-ing area. Resistors default to **RPOLY_HI** (precision poly).")
md.append("Capacitors: MIM for precision. BJT: AREA sets Vbe.\n")
md.append("**Two floors (v2.2-defaults).** Each MOS/passive row carries two size floors: the **fab min**")
md.append(f"(smallest buildable -- the [grounded]/[derived] `device_limits.csv` minimum; VDMOS = {VDMOS_WMIN:g} um")
md.append("min gate finger, so mirror widths below it are Wmin-clamped and flagged) and the **min sensible")
md.append(f"(matched)** floor -- the size at which matched-pair **sigma(dI/I) crosses {MOS_ANALOG_THRESH:g}% for MOS**")
md.append(f"pairs (at the device's lowest guide current) / **sigma(dR/R), sigma(dC/C) crosses {PASSIVE_ANALOG_THRESH:g}% for")
md.append("passives**. The analog floor is *guidance* (matching), not a hard rule; where it exceeds the fab min")
md.append("you must size up for matched use, where it is below the fab min the fab floor governs. Full basis:")
md.append("`docs/geometry-minima.md`.\n")
md.append("---\n")
mos_mirror=[d for d in g["mos"] if "mirror_points" in g["mos"][d]]
n_dev=len(mos_mirror)+(1 if "DNMOS20" in g["mos"] else 0)
md.append(f"## MOS -- mirror sizing (gm/Id ~ 6)  [{n_dev} devices]\n")
md.append("W is Wmin-clamped to the fab floor where the gm/Id-6 width falls below it (\\*).\n")
md.append("| device | supply | fab Wmin (um) | min matched W (sig<20%) | I(lo) W/Vgs/gmId/sig | I(mid) W/Vgs/gmId/sig | I(hi) W/Vgs/gmId/sig |")
md.append("|---|---|---|---|---|---|---|")
for dev in mos_mirror:
    m=g["mos"][dev]; c=_mirror_cells(m["mirror_points"])
    fab=m.get("fab_Wmin_um"); aW=m.get("analog_min_W_um")
    md.append(f"| {dev} | {m['supply_V']}V | {fab:g} | {aW if aW is not None else 'n/a'} | {c[0]} | {c[1]} | {c[2]} |")
md.append("")
if "DNMOS20" in g["mos"]:
    dn=g["mos"]["DNMOS20"]
    md.append("### DNMOS20 (depletion) -- Vgs=0 self-biased current source")
    md.append(f"Idss = **{dn.get('idss_per_um_uA')} uA/um** at Vgs=0. Not a mirror-Vov device; size for self-biased duty:\n")
    md.append("| target I | W (Vgs=0) | sigma(dI/I) | note |")
    md.append("|---|---|---|---|")
    for k in sorted(dn.get("selfbias_points",{}),key=lambda x:float(x)):
        p=dn["selfbias_points"][k]; I=float(k)*1e6
        md.append(f"| {I:g} uA | {p['W_um']} um | {p.get('sigma_dI_pct')}% | {p.get('note','direct')} |")
    md.append("")
md.append("## Resistors -- default RPOLY_HI (precision poly)\n")
md.append("| target | layer | squares | area (um2) | min area (sig<1%) | sigma(dR/R) | tc1 (ppm/C) | drift -40..150C | area-saving alt |")
md.append("|---|---|---|---|---|---|---|---|---|")
for Rt in sorted(g["resistors"],key=lambda x:float(x)):
    r=g["resistors"][Rt]; alt=r.get("rnwell_alt",{})
    altstr=(f"RNWELL {alt.get('squares')}sq (WARN: {alt.get('drift_pct_-40_150C')}% drift, "
            f"structural VCR -- off signal only)") if alt else ""
    md.append(f"| {float(Rt):g} Ohm | **{r['layer']}** | {r['squares']} | {r['area_um2']} | "
              f"{r.get('analog_min_area_um2')} | {r['sigma_dR_pct']}% | {r['tc1_ppm_C']} | "
              f"{r['drift_pct_-40_150C']}% | {altstr} |")
md.append("")
md.append("## Capacitors\n")
md.append("| target | layer | area (um2) | side (um) | min area (sig<1%) | sigma(dC/C) | matching bits |")
md.append("|---|---|---|---|---|---|---|")
for Ct in g["capacitors"]:
    c=g["capacitors"][Ct]
    md.append(f"| {Ct} | {c['layer']} | {c['area_um2']} | {c['side_um']} | {c.get('analog_min_area_um2')} | {c['sigma_dC_pct']}% | {c['matching_bits']} |")
md.append("")
md.append("## BJT -- AREA per decade of Ic\n")
md.append("| device | 10uA Vbe/beta | 100uA Vbe/beta | 1mA Vbe/beta | pair sig(dVbe) | eff fT |")
md.append("|---|---|---|---|---|---|")
for dev in g["bjt"]:
    pts=g["bjt"][dev]
    def _c(uak): p=pts.get(uak,{}); return f"{p.get('Vbe_V','')}/{p.get('beta','')}"
    sig=next(iter(pts.values())).get("pair_sigma_dVbe_mV","")
    md.append(f"| {dev} | {_c('10uA')} | {_c('100uA')} | {_c('1000uA')} | {sig} mV | ~1 GHz-class |")
md.append("")
md.append("---\n")
md.append(f"*Machine-readable: `docs/sizing-guide.json` (v{g['_meta']['version']}). "
          "Regenerate: `sizing_guide.py {vdmos,bsim}` then `gen_sizing_docs.py`.*")
(REPO/"docs"/"sizing-guide.md").write_text("\n".join(md)+"\n",newline="\n",encoding="utf-8")
print("sizing-guide.md:", len(mos_mirror),"MOS +", (1 if "DNMOS20" in g["mos"] else 0),"depletion, R/C/BJT")
