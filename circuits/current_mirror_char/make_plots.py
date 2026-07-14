#!/usr/bin/env python3
"""make_plots.py -- brief-10 plots: I_out vs V_out families, V_SD collapse,
MC clouds.  All from results.json / mc_results.json (real sweeps)."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
PL = os.path.join(HERE, "plots"); os.makedirs(PL, exist_ok=True)
res = json.load(open(os.path.join(HERE, "results.json")))["sweeps"]
mc = json.load(open(os.path.join(HERE, "mc_results.json")))["results"]

def sel(name=None, topo=None, Vdd=5.0, case=0, temp=27):
    for s in res:
        if (s["name"]==name and s["topo"]==topo and s["Vdd"]==Vdd
                and s["case"]==case and s["temp"]==temp):
            return s
    return None

COL = {"MIR_S":"#d1495b","MIR_CS":"#2e75b6","MIR_CW":"#33a02c"}

# 1. topology family: Iout vs Vout, 3 topologies, locked 10uA design, nominal
def plot_topo_family():
    fig, ax = plt.subplots(1, 2, figsize=(11,4.2))
    for topo in ("MIR_S","MIR_CS","MIR_CW"):
        s = sel("B_10u", topo)
        Iin = s["Iin"]
        v=np.array(s["fine_Vout"]); i=np.array(s["fine_Iout"])*1e6
        ax[0].plot(v,i,color=COL[topo],label=topo,lw=1.8)
        ax[1].plot(v,i*1e-6/Iin,color=COL[topo],label=topo,lw=1.8)
    for a in ax:
        a.axvline(2.5,ls=":",c="k",alpha=.4)
        a.set_xlabel("V_out (V)"); a.grid(alpha=.3); a.legend()
    ax[0].set_ylabel("I_out (µA)"); ax[0].set_title("Locked 10µA mirror (L=2µ) @ TT/5V/27°C")
    ax[1].set_ylabel("I_out / I_in"); ax[1].set_title("mirror gain — cascodes flatten to 1.000")
    ax[1].set_ylim(0.95,1.10); ax[1].axhline(1.0,ls="--",c="gray",alpha=.6)
    ax[1].annotate("Vdd/2",(2.5,1.005),fontsize=8)
    fig.tight_layout(); fig.savefig(f"{PL}/01_topology_family.png",dpi=130); plt.close(fig)

# 2. V_SD collapse: 4 Vdd sweeps of B_10u MIR_S overlaid vs Vout, then vs VSD
def plot_vsd_collapse():
    fig, ax = plt.subplots(1,2,figsize=(11,4.2))
    for Vdd in (3.2,4.5,5.0,5.5):
        s=sel("B_10u","MIR_S",Vdd=Vdd)
        v=np.array(s["grid_Vout"]); i=np.array(s["grid_Iout"])*1e6
        ax[0].plot(v,i,label=f"Vdd={Vdd}",lw=1.5)
        ax[1].plot(Vdd-v,i,label=f"Vdd={Vdd}",lw=1.5,alpha=.8)
    ax[0].set_xlabel("V_out (V)"); ax[0].set_title("B_10u MIR_S: 4 supplies vs V_out")
    ax[1].set_xlabel("V_SD = Vdd − V_out (V)")
    ax[1].set_title("… collapse onto one I_out(V_SD) curve (residual = 0)")
    for a in ax:
        a.set_ylabel("I_out (µA)"); a.grid(alpha=.3); a.legend()
    fig.tight_layout(); fig.savefig(f"{PL}/02_vsd_collapse.png",dpi=130); plt.close(fig)

# 3. Strategy A vs B: gain(Vout) at each current
def plot_stratAB():
    fig, ax = plt.subplots(1,2,figsize=(11,4.2),sharey=True)
    curr = ["100n","1u","10u","100u"]
    cmap = plt.cm.viridis(np.linspace(0,.85,4))
    for j,(strat,axx) in enumerate(zip(("B","A"),ax)):
        for c,col in zip(curr,cmap):
            s=sel(f"{strat}_{c}","MIR_S")
            v=np.array(s["fine_Vout"]); i=np.array(s["fine_Iout"])
            axx.plot(v,i/s["Iin"],color=col,label=f"{c}",lw=1.6)
        axx.axvline(1.2,ls=":",c="k",alpha=.4); axx.axhline(1,ls="--",c="gray",alpha=.5)
        axx.set_xlabel("V_out (V)"); axx.grid(alpha=.3); axx.legend(title="I_in")
        axx.set_title(f"Strategy {strat} — "+("sized per current" if strat=="B" else "10µA cell, programmed"))
    ax[0].set_ylabel("I_out / I_in"); ax[0].set_ylim(0.9,1.12)
    fig.suptitle("Simple-mirror gain vs V_out — Strategy A (fixed geom) diverges at 100nA & 100µA",y=1.02)
    fig.tight_layout(); fig.savefig(f"{PL}/03_strategy_A_vs_B.png",dpi=130,bbox_inches="tight"); plt.close(fig)

# 4. lambda_eff vs L (Phase 0)
def plot_phase0():
    p0=json.load(open(os.path.join(HERE,"phase0.json")))
    fig,ax=plt.subplots(figsize=(6,4.3))
    for topo,c in (("MIR_S","#d1495b"),("MIR_CS","#2e75b6")):
        L=[r["L_um"] for r in p0 if r["topo"]==topo]
        lam=[r["lambda_eff"] for r in p0 if r["topo"]==topo]
        ax.loglog(L,lam,"o-",color=c,label=topo)
    ax.set_xlabel("L (µm)"); ax.set_ylabel("λ_eff (/V)")
    ax.set_title("Phase 0: λ_eff vs L @ Vov=200mV, 10µA  (locked L=2µm)")
    ax.axvline(2.0,ls=":",c="k",alpha=.5); ax.grid(alpha=.3,which="both"); ax.legend()
    fig.tight_layout(); fig.savefig(f"{PL}/04_phase0_lambda_vs_L.png",dpi=130); plt.close(fig)

# 5. MC clouds: histograms of Iout@1.2 for 3 topologies, B_10u, both modes
def plot_mc():
    fig, ax = plt.subplots(1,2,figsize=(11,4.2),sharey=True)
    for axx,mode,ttl in zip(ax,("mismatch","procmm"),
                            ("mismatch-only","process + mismatch")):
        for topo in ("MIR_S","MIR_CS","MIR_CW"):
            I=np.array(mc["B_10u"][topo][mode]["I_runs"])*1e6
            axx.hist(I,bins=40,alpha=.55,color=COL[topo],label=topo)
        axx.set_xlabel("I_out @ V_out=1.2V (µA)"); axx.set_title(f"B_10u — {ttl}")
        axx.grid(alpha=.3); axx.legend()
    ax[0].set_ylabel("count")
    fig.suptitle("MC clouds: process shift barely widens the ratio (mismatch dominates)",y=1.02)
    fig.tight_layout(); fig.savefig(f"{PL}/05_mc_clouds.png",dpi=130,bbox_inches="tight"); plt.close(fig)

# 6. MC area effect: B_10u vs B_100n sigma/mu
def plot_mc_area():
    fig,ax=plt.subplots(figsize=(6.5,4.3))
    for name,ls in (("B_10u","-"),("B_100n","--")):
        I=np.array(mc[name]["MIR_S"]["mismatch"]["I_runs"])
        I=I/I.mean()
        ax.hist(I,bins=45,alpha=.5,label=f"{name} (σ/µ={I.std()*100:.2f}%)")
    ax.set_xlabel("I_out @1.2V, normalized to mean"); ax.set_ylabel("count")
    ax.set_title("Mismatch: small 100nA device (W=0.88µ) matches ~10× worse")
    ax.legend(); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(f"{PL}/06_mc_area_effect.png",dpi=130); plt.close(fig)

if __name__=="__main__":
    plot_topo_family(); plot_vsd_collapse(); plot_stratAB()
    plot_phase0(); plot_mc(); plot_mc_area()
    print("wrote plots:", sorted(os.listdir(PL)))
