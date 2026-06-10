"""
Async logic cell design framework for the AutoHV BiCMOS 180 PDK.
Generates ngspice decks, drives ngspice_con, parses results.

Three voltage domains: 1.8V (NMOS18/PMOS18), 3.3V (NMOS33/PMOS33), 5.0V (NMOS50/PMOS50).
Eight cells: INV, BUF, NAND2, NOR2, AND2, OR2, XOR2, XNOR2.
"""
import subprocess, re, os, math, json

NGSPICE = r"C:/Users/chris/SPICE/Qucs-S-25.2.0-win64/bin/ngspice_con.exe"
LIB     = r"C:/Users/chris/ngspice/Prompts/autohv_bicmos180_pdk/autohv_bicmos180_case.lib"
WORK    = r"C:/Users/chris/ngspice/Prompts/async_logic_design"
DECK    = os.path.join(WORK, "decks")
os.makedirs(DECK, exist_ok=True)

# ---------------------------------------------------------------- domains
DOMAINS = {
    "1v8": dict(n="NMOS18", p="PMOS18", L=0.18, vdd=1.8, vlist=[1.62, 1.80, 1.98],
                cpp=0.50, hov=1.5),
    "3v3": dict(n="NMOS33", p="PMOS33", L=0.35, vdd=3.3, vlist=[2.97, 3.30, 3.63],
                cpp=0.70, hov=2.0),
    "5v0": dict(n="NMOS50", p="PMOS50", L=0.50, vdd=5.0, vlist=[3.20, 5.00, 5.50],
                cpp=0.90, hov=2.5),
}
CORNERS = [0, 1, 2, 3, 4]          # TT FF SS FS SF
CNAME   = {0: "TT", 1: "FF", 2: "SS", 3: "FS", 4: "SF"}
TEMPS   = [-55, 27, 150]

CL_FF   = 5.0       # output load for rise/fall characterization (fF) = FO1
TIN_PS  = 20.0      # input edge (10-90) of the driving stimulus (ps)

# Poly-column count per cell for the layout-area estimate (see report notes)
NCOLS = {"INV":1, "BUF":2, "NAND2":2, "NOR2":2, "AND2":3, "OR2":3, "XOR2":6, "XNOR2":6}

# ---------------------------------------------------------------- ngspice runner
def run(deck_text, tag):
    path = os.path.join(DECK, tag + ".cir")
    with open(path, "w", newline="\n") as f:
        f.write(deck_text)
    r = subprocess.run([NGSPICE, "-b", path], capture_output=True, text=True, timeout=600)
    return r.stdout + "\n" + r.stderr

def parse_res(out):
    """Collect all 'RES key=val key=val ...' lines into list of dicts."""
    rows = []
    for ln in out.splitlines():
        if ln.startswith("RES "):
            d = {}
            for tok in ln.split()[1:]:
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    try: d[k] = float(v)
                    except ValueError: d[k] = v
            rows.append(d)
    return rows

# ---------------------------------------------------------------- cell netlists
# Each builder returns netlist lines (list[str]) for the cell core.
# Ports use nodes: vdd, 0(gnd), input pins, 'out'. W in microns, L in microns.
# Width dict keys are documented per cell.

def cell_netlist(cell, dom, wf, remap=None):
    """wf(name)->str gives a width expression (number or ngspice param expr) for
    each logical width 'name'. remap maps pin node names (a,b,in) to other nodes."""
    n, p, L = dom["n"], dom["p"], dom["L"]
    remap = remap or {}
    lines = []
    cnt = [0]
    def nd(x): return remap.get(x, x)
    def dev(model, d, g, s, b, wname):
        cnt[0]+=1
        # NOTE: the 'u' suffix is dropped after a brace expression (W={x}u -> metres),
        # so scale to metres explicitly inside the braces.
        lines.append(f"X{cnt[0]} {nd(d)} {nd(g)} {nd(s)} {nd(b)} {model} "
                     f"W={{({wf(wname)})*1e-6}} L={L}u\n")

    if cell == "INV":
        dev(p,"out","in","vdd","vdd","wp"); dev(n,"out","in","0","0","wn")
    elif cell == "BUF":
        dev(p,"mid","in","vdd","vdd","wp1"); dev(n,"mid","in","0","0","wn1")
        dev(p,"out","mid","vdd","vdd","wp2"); dev(n,"out","mid","0","0","wn2")
    elif cell == "NAND2":
        dev(p,"out","a","vdd","vdd","wp"); dev(p,"out","b","vdd","vdd","wp")
        dev(n,"out","a","n1","0","wn");    dev(n,"n1","b","0","0","wn")
    elif cell == "NOR2":
        dev(p,"p1","a","vdd","vdd","wp");  dev(p,"out","b","p1","vdd","wp")
        dev(n,"out","a","0","0","wn");     dev(n,"out","b","0","0","wn")
    elif cell == "AND2":   # NAND2 -> INV
        dev(p,"nd","a","vdd","vdd","wp"); dev(p,"nd","b","vdd","vdd","wp")
        dev(n,"nd","a","n1","0","wn");    dev(n,"n1","b","0","0","wn")
        dev(p,"out","nd","vdd","vdd","wpi"); dev(n,"out","nd","0","0","wni")
    elif cell == "OR2":    # NOR2 -> INV
        dev(p,"p1","a","vdd","vdd","wp");  dev(p,"nr","b","p1","vdd","wp")
        dev(n,"nr","a","0","0","wn");      dev(n,"nr","b","0","0","wn")
        dev(p,"out","nr","vdd","vdd","wpi"); dev(n,"out","nr","0","0","wni")
    elif cell in ("XOR2","XNOR2"):
        dev(p,"abar","a","vdd","vdd","wpi"); dev(n,"abar","a","0","0","wni")
        dev(p,"bbar","b","vdd","vdd","wpi"); dev(n,"bbar","b","0","0","wni")
        if cell == "XNOR2":
            # PDN out low when A!=B : (a.bbar) || (abar.b)
            dev(n,"out","a","m1","0","wn");    dev(n,"m1","bbar","0","0","wn")
            dev(n,"out","abar","m2","0","wn"); dev(n,"m2","b","0","0","wn")
            # PUN out high when A==B : gates(abar,bbar) || gates(a,b)
            dev(p,"out","abar","k1","vdd","wp"); dev(p,"k1","bbar","vdd","vdd","wp")
            dev(p,"out","a","k2","vdd","wp");    dev(p,"k2","b","vdd","vdd","wp")
        else: # XOR2
            # PDN out low when A==B : (a.b) || (abar.bbar)
            dev(n,"out","a","m1","0","wn");    dev(n,"m1","b","0","0","wn")
            dev(n,"out","abar","m2","0","wn"); dev(n,"m2","bbar","0","0","wn")
            # PUN out high when A!=B : gates(abar,b) || gates(a,bbar)
            dev(p,"out","abar","k1","vdd","wp"); dev(p,"k1","b","vdd","vdd","wp")
            dev(p,"out","a","k2","vdd","wp");    dev(p,"k2","bbar","vdd","vdd","wp")
    else:
        raise ValueError(cell)
    return "".join(lines)

# ---- width expression builders (symbolic for ratio search; numeric for final)
def wf_symbolic(cell, K, RINV):
    """Return wf using ngspice params S (scale) and R (P/N ratio knob).
    K=drive multiplier, RINV=fixed internal-inverter P/N ratio (numbers)."""
    m = {
        "wn":"S", "wp":"S*R",
        "wn1":"S", "wp1":"S*R", "wn2":f"S*{K}", "wp2":f"S*R*{K}",
        "wni": ("S" if cell in ("XOR2","XNOR2") else f"S*{K}"),
        "wpi": (f"S*{RINV}" if cell in ("XOR2","XNOR2") else f"S*{K}*{RINV}"),
    }
    return lambda name: m[name]

def wf_numeric(W):
    return lambda name: f"{W[name]:.4f}"

def widths_final(cell, scale, R, K, RINV):
    """Concrete width dict from scale & ratio (mirrors wf_symbolic)."""
    W = {"wn":scale, "wp":scale*R}
    if cell=="BUF":
        W.update(wn1=scale, wp1=scale*R, wn2=scale*K, wp2=scale*R*K)
    if cell in ("AND2","OR2"):
        W.update(wni=scale*K, wpi=scale*K*RINV)
    if cell in ("XOR2","XNOR2"):
        W.update(wni=scale, wpi=scale*RINV)
    return W

# inputs that exist per cell
CELL_INPUTS = {"INV":["in"], "BUF":["in"], "NAND2":["a","b"], "NOR2":["a","b"],
               "AND2":["a","b"], "OR2":["a","b"], "XOR2":["a","b"], "XNOR2":["a","b"]}
CELL_INVERTING = {"INV":True,"BUF":False,"NAND2":True,"NOR2":True,
                  "AND2":False,"OR2":False,"XOR2":None,"XNOR2":None}

# ============================================================ deck builders
HEADER = (".title {tag}\n"
          '.include "%s"\n' % LIB +
          ".param case=0\n.param VDD={vnom}\n")

def measure_gnp(dom):
    """Per-micron gate input capacitance (fF/um) for N and P at L, bias VDD/2."""
    vnom, L = dom["vdd"], dom["L"]
    out = {}
    for kind, model in (("gn", dom["n"]), ("gp", dom["p"])):
        if kind == "gn":
            dev = f"X1 dd g 0 0 {model} W=10u L={L}u\n"
        else:
            dev = f"X1 dd g vdd vdd {model} W=10u L={L}u\n"
        deck = (HEADER.format(tag=kind, vnom=vnom) +
                f"Vdd vdd 0 {vnom}\n" +
                f"Vd dd 0 {vnom/2}\n" +
                f"Vg g 0 {vnom/2} AC 1\n" + dev +
                ".control\nac lin 1 1e6 1e6\n"
                "let gpm = abs(imag(Vg#branch))/(2*PI*1e6)/10*1e15\n"
                f'echo "RES {kind}=$&gpm"\n.endc\n.end\n')
        rows = parse_res(run(deck, "gnp_"+kind+"_"+ [k for k,v in DOMAINS.items() if v is dom][0]))
        out[kind] = rows[0][kind]
    return out["gn"], out["gp"]

def deck_cap_pin(cell, dom, W, pin):
    """Average switching input capacitance (fF) at one pin: small-signal AC cap
    evaluated at the two input rails (pin=0 and pin=VDD) and averaged. At the
    rails the stage gain ~0, so Cgd is not Miller-inflated -> true digital load.
    Other inputs held at VDD/2."""
    vnom = dom["vdd"]
    pins = CELL_INPUTS[cell]
    src = f"Vdd vdd 0 {vnom}\n"
    for pn in pins:
        ac = " AC 1" if pn == pin else ""
        bias = 0.0 if pn == pin else vnom/2
        src += f"V_{pn} {pn} 0 {bias}{ac}\n"
    deck = (HEADER.format(tag=f"cap_{cell}_{pin}", vnom=vnom) + src +
            cell_netlist(cell, dom, wf_numeric(W)) +
            ".control\n"
            f"foreach vb 0 {vnom}\n"
            f"  alter V_{pin} dc=$vb\n  ac lin 1 1e6 1e6\n"
            f"  let cpf = abs(imag(V_{pin}#branch))/6283185.307*1e15\n"
            '  echo "RES cap=$&cpf"\n'
            "end\n.endc\n.end\n")
    rows = parse_res(run(deck, f"cap_{cell}_{dom['n']}_{pin}"))
    vals = [r["cap"] for r in rows if isinstance(r.get("cap"), float)]
    return sum(vals)/len(vals) if vals else float("nan")

# input configurations: (remap, swept_node) for VM ; (remap) for TRAN
def vm_configs(cell):
    if cell in ("INV","BUF"): return [("nom", {})]
    if cell in ("NAND2","NOR2","AND2","OR2"): return [("tied", {"a":"in","b":"in"})]
    if cell == "XOR2":  return [("b0", {"a":"in","b":"0"}), ("b1", {"a":"in","b":"vdd"})]
    if cell == "XNOR2": return [("b1", {"a":"in","b":"vdd"}), ("b0", {"a":"in","b":"0"})]

def tran_remap(cell):
    if cell in ("INV","BUF"): return {}
    if cell in ("NAND2","AND2"): return {"a":"in","b":"vdd"}
    if cell in ("NOR2","OR2"):  return {"a":"in","b":"0"}
    if cell == "XOR2":  return {"a":"in","b":"0"}
    if cell == "XNOR2": return {"a":"in","b":"vdd"}

# With the chosen tran hold states the output is inverting for these cells,
# non-inverting for the rest (BUF, AND2, OR2, XOR2, XNOR2 -> out follows 'in').
TRAN_INVERTING = {"INV","NAND2","NOR2"}

def deck_ratio(cell, dom, K, RINV, Rlist, Sval=1.0):
    """Symbolic deck: sweep R, measure nominal VM (TT,27,Vnom). Uses first vm cfg.
    Returns list of (R, VM)."""
    vnom = dom["vdd"]
    cfgname, remap = vm_configs(cell)[0]
    wf = wf_symbolic(cell, K, RINV)
    body = cell_netlist(cell, dom, wf, remap)
    rl = " ".join(f"{r:.4f}" for r in Rlist)
    deck = (HEADER.format(tag=f"ratio_{cell}", vnom=vnom) +
            f".param S={Sval}\n.param R={Rlist[0]}\n" +
            f"Vdd vdd 0 {vnom}\nVin in 0 {vnom/2}\n" + body +
            ".control\nlet half = " + f"{vnom/2}\n" +
            f"foreach rr {rl}\n"
            "  alterparam R=$rr\n  reset\n"
            f"  dc Vin 0 {vnom} {vnom/400}\n"
            "  meas dc vm find v(in) when v(out)=$&half cross=1\n"
            '  echo "RES R=$rr vm=$&vm"\n'
            "end\n.endc\n.end\n")
    return parse_res(run(deck, f"ratio_{cell}_{dom['n']}"))

def deck_vm_pvt(cell, dom, W):
    """Full PVT VM sweep for all vm configs. Returns list of dicts."""
    vnom = dom["vdd"]
    rows_all = []
    for cfgname, remap in vm_configs(cell):
        body = cell_netlist(cell, dom, wf_numeric(W), remap)
        vl = " ".join(f"{v:.3f}" for v in dom["vlist"])
        tl = " ".join(str(t) for t in TEMPS)
        deck = (HEADER.format(tag=f"vm_{cell}_{cfgname}", vnom=vnom) +
                f"Vdd vdd 0 {{VDD}}\nVin in 0 {{VDD/2}}\n" + body +
                ".control\n"
                "foreach cs 0 1 2 3 4\n"
                f" foreach vd {vl}\n"
                f"  foreach tp {tl}\n"
                "   alterparam case=$cs\n   alterparam VDD=$vd\n   reset\n"
                "   option temp=$tp\n   let half=$vd/2\n"
                f"   dc Vin 0 $vd {vnom/500:.5f}\n"
                "   meas dc vm find v(in) when v(out)=$&half cross=1\n"
                f'   echo "RES cfg={cfgname} cs=$cs vd=$vd tp=$tp vm=$&vm"\n'
                "  end\n end\nend\n.endc\n.end\n")
        rows_all += parse_res(run(deck, f"vm_{cell}_{dom['n']}_{cfgname}"))
    return rows_all

def deck_tran_pvt(cell, dom, W):
    """Full PVT rise/fall sweep. Returns list of dicts with trise,tfall (ps)."""
    vnom = dom["vdd"]
    remap = tran_remap(cell)
    body = cell_netlist(cell, dom, wf_numeric(W), remap)
    vl = " ".join(f"{v:.3f}" for v in dom["vlist"])
    tl = " ".join(str(t) for t in TEMPS)
    tin = TIN_PS*1e-3   # ns
    # Window each edge to the correct transition (input rises @2n, falls @11n) so a
    # static hazard on the opposite edge cannot corrupt the 10-90 measurement.
    inv = cell in TRAN_INVERTING
    tdr = "10.5n" if inv else "1.5n"   # output rising edge search start
    tdf = "1.5n"  if inv else "10.5n"  # output falling edge search start
    deck = (HEADER.format(tag=f"tr_{cell}", vnom=vnom) +
            f"Vdd vdd 0 {{VDD}}\n"
            f"Vin in 0 PULSE(0 {{VDD}} 2n {tin}n {tin}n 9n 20n)\n" + body +
            f"CL out 0 {CL_FF}f\n"
            ".control\n"
            "foreach cs 0 1 2 3 4\n"
            f" foreach vd {vl}\n"
            f"  foreach tp {tl}\n"
            "   alterparam case=$cs\n   alterparam VDD=$vd\n   reset\n"
            "   option temp=$tp\n"
            "   let v10=0.1*$vd\n   let v90=0.9*$vd\n"
            "   tran 0.004n 20n\n"
            f"   meas tran trise trig v(out) val=$&v10 rise=1 td={tdr} targ v(out) val=$&v90 rise=1 td={tdr}\n"
            f"   meas tran tfall trig v(out) val=$&v90 fall=1 td={tdf} targ v(out) val=$&v10 fall=1 td={tdf}\n"
            f'   echo "RES cs=$cs vd=$vd tp=$tp trise=$&trise tfall=$&tfall"\n'
            "  end\n end\nend\n.endc\n.end\n")
    return parse_res(run(deck, f"tr_{cell}_{dom['n']}"))
