"""
Delay-cell / pulse-generator design framework for the AutoHV BiCMOS 180 PDK.
Generates ngspice decks, drives ngspice_con, parses results.

Four cell archetypes, each in three voltage domains (1.8 / 3.3 / 5.0 V):

  DLYR  - rising-edge delay,  falling-edge passthrough  (non-inverting)
  DLYF  - falling-edge delay, rising-edge  passthrough  (non-inverting)
  PHI   - logic-HIGH pulse on rising edge, falling-edge passthrough
  PLO   - logic-LOW  pulse on falling edge, rising-edge  passthrough

Timing target: 20 ns delay / pulse width at the NOMINAL corner
(case=0 / TT, nominal supply, 27 C).  Area is minimised by realising the
time constant with a high-sheet poly resistor (RPOLY_HI) charging a
high-density MIM cap (CMIM_HI), with the resistor/cap areas balanced near
the analytic minimum.  A 6T Schmitt trigger restores a clean fast output
edge; the asymmetric edge is set by a single bypass transistor across the
RC node.
"""
import subprocess, os, shutil, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE
DECK = WORK / "decks"
DECK.mkdir(exist_ok=True)

# decks/ -> delay_pulse_design/ -> circuits/ -> repo root (where the PDK lives)
LIB = "../../../autohv_bicmos180_case.lib"


def _find_ngspice() -> str:
    cand = os.environ.get("NGSPICE_BIN")
    if cand and Path(cand).exists():
        return cand
    for name in ("ngspice_con", "ngspice_con.exe", "ngspice"):
        p = shutil.which(name)
        if p:
            return p
    for p in (
        r"C:\Program Files\Qucs-S-25.2.0-win64\bin\ngspice_con.exe",
        r"C:\Spice64\bin\ngspice_con.exe",
        r"C:\Program Files\ngspice\bin\ngspice_con.exe",
    ):
        if Path(p).exists():
            return p
    raise RuntimeError("ngspice not found; set NGSPICE_BIN.")


NGSPICE = _find_ngspice()

# ---------------------------------------------------------------- domains
# wn/wp     : NMOS/PMOS width for inverters, Schmitt, logic gates (um)
# wbp       : bypass transistor width (um) -- must be << R, easily met
# Lg        : channel length for the logic devices (um)
DOMAINS = {
    "1v8": dict(n="NMOS18", p="PMOS18", Lg=0.18, vdd=1.8,
                vlist=[1.62, 1.80, 1.98], wn=0.30, wp=0.70, wbp=0.60,
                cpp=0.50, hov=1.5),
    "3v3": dict(n="NMOS33", p="PMOS33", Lg=0.35, vdd=3.3,
                vlist=[2.97, 3.30, 3.63], wn=0.40, wp=0.95, wbp=0.80,
                cpp=0.70, hov=2.0),
    "5v0": dict(n="NMOS50", p="PMOS50", Lg=0.50, vdd=5.0,
                vlist=[3.20, 5.00, 5.50], wn=0.50, wp=1.15, wbp=1.00,
                cpp=0.90, hov=2.5),
}
CNAME = {0: "TT", 1: "FF", 2: "SS", 3: "FS", 4: "SF"}
TEMPS = [-55, 27, 150]

WR = 0.5             # poly-resistor width (um) -- assumed precision-poly minimum
RSH_HI = 1200.0      # RPOLY_HI sheet (ohm/sq, TT) -- for L starting guess
CJ_HI = 2e-3         # CMIM_HI areal cap (F/m^2, TT) = 2 fF/um^2
CL_FF = 5.0          # output load (fF) = fanout-of-1

# transistor count by archetype, for the layout-area estimate
#   delay core = INV1(2) + bypass(1) + Schmitt(6) = 9
#   PHI/PLO    = core(9) + inv(2) + 2-input gate(4) + out inv(2) = 17
NDEV = {"DLYR": 9, "DLYF": 9, "PHI": 17, "PLO": 17}
# poly columns (device-width pitch count) for the layout box estimate
NCOLS = {"DLYR": 5, "DLYF": 5, "PHI": 9, "PLO": 9}

ARCHES = ["DLYR", "DLYF", "PHI", "PLO"]
ARCH_LONG = {
    "DLYR": "rising-edge delay / falling passthrough",
    "DLYF": "falling-edge delay / rising passthrough",
    "PHI":  "HIGH pulse on rising edge / falling passthrough",
    "PLO":  "LOW pulse on falling edge / rising passthrough",
}


# ---------------------------------------------------------------- ngspice runner
# Force single-threaded ngspice so many cells can run as independent processes
# without OpenMP threads from each one oversubscribing (and spin-waiting on) the
# cores. Belt-and-suspenders: the env vars + the per-deck `.option num_threads=1`.
_ENV = dict(os.environ, OMP_WAIT_POLICY="passive", OMP_DYNAMIC="false")

# ngspice threads per process (set via .option num_threads). With many cells run
# as concurrent processes, threads_per_proc * n_workers should ~ core count.
NUM_THREADS = 1


def run(deck_text, tag, timeout=900):
    path = DECK / (tag + ".cir")
    with open(path, "w", newline="\n") as f:
        f.write(deck_text)
    r = subprocess.run([NGSPICE, "-b", path.name], cwd=str(DECK),
                       capture_output=True, text=True, timeout=timeout, env=_ENV)
    return r.stdout + "\n" + r.stderr


def parse_res(out):
    rows = []
    for ln in out.splitlines():
        if ln.startswith("RES "):
            d = {}
            for tok in ln.split()[1:]:
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    try:
                        d[k] = float(v)
                    except ValueError:
                        d[k] = v
            rows.append(d)
    return rows


# ---------------------------------------------------------------- cell netlist
def core_netlist(arch, dom, lr, cl, cw, outnode):
    """Delay core: 'in' -> outnode (delayed copy of in).
    arch 'DLYR'/'PHI' use a pull-UP bypass (fast falling out);
    arch 'DLYF'/'PLO' use a pull-DOWN bypass (fast rising out)."""
    n, p, Lg = dom["n"], dom["p"], dom["Lg"]
    wn, wp, wbp = dom["wn"], dom["wp"], dom["wbp"]
    up = arch in ("DLYR", "PHI")
    L = f"{Lg}u"
    s = []
    # input inverter: nIN = !in
    s.append(f"XI1 nIN in vdd vdd {p} W={wp}u L={L}")
    s.append(f"XI2 nIN in 0   0   {n} W={wn}u L={L}")
    # RC node
    s.append(f"XR nIN nC RPOLY_HI L={lr:.4f}u W={WR}u")
    s.append(f"XC nC 0 CMIM_HI L={cl:.4f}u W={cw:.4f}u")
    # bypass for the fast edge
    if up:
        s.append(f"XBP nC in vdd vdd {p} W={wbp}u L={L}")   # pull up when in low
    else:
        s.append(f"XBP nC in 0 0 {n} W={wbp}u L={L}")       # pull down when in high
    # 6T Schmitt trigger (inverting): outnode = !nC
    s.append(f"XS1 s1 nC 0   0   {n} W={wn}u L={L}")
    s.append(f"XS2 {outnode} nC s1 0 {n} W={wn}u L={L}")
    s.append(f"XS3 s2 nC vdd vdd {p} W={wp}u L={L}")
    s.append(f"XS4 {outnode} nC s2 vdd {p} W={wp}u L={L}")
    s.append(f"XS5 vdd {outnode} s1 0   {n} W={wn}u L={L}")
    s.append(f"XS6 0   {outnode} s2 vdd {p} W={wp}u L={L}")
    return "\n".join(s) + "\n"


def cell_netlist(arch, dom, lr, cl, cw):
    """Full cell: 'in' -> 'out'."""
    n, p, Lg = dom["n"], dom["p"], dom["Lg"]
    wn, wp = dom["wn"], dom["wp"]
    L = f"{Lg}u"
    if arch in ("DLYR", "DLYF"):
        return core_netlist(arch, dom, lr, cl, cw, "out")
    # pulse cells: core -> dco, invert -> dbar, combine with 'in'
    s = [core_netlist(arch, dom, lr, cl, cw, "dco")]
    s.append(f"XPI1 dbar dco vdd vdd {p} W={wp}u L={L}")   # dbar = !dco
    s.append(f"XPI2 dbar dco 0   0   {n} W={wn}u L={L}")
    if arch == "PHI":   # out = in AND dbar  = NAND2(in,dbar) -> INV
        s.append(f"XG1 nnd in   vdd vdd {p} W={wp}u L={L}")
        s.append(f"XG2 nnd dbar vdd vdd {p} W={wp}u L={L}")
        s.append(f"XG3 nnd in   q   0   {n} W={wn}u L={L}")
        s.append(f"XG4 q   dbar 0   0   {n} W={wn}u L={L}")
        s.append(f"XO1 out nnd vdd vdd {p} W={wp}u L={L}")
        s.append(f"XO2 out nnd 0   0   {n} W={wn}u L={L}")
    else:               # PLO: out = in OR dbar = NOR2(in,dbar) -> INV
        s.append(f"XG1 p1  in   vdd vdd {p} W={wp}u L={L}")
        s.append(f"XG2 nnr dbar p1  vdd {p} W={wp}u L={L}")
        s.append(f"XG3 nnr in   0   0   {n} W={wn}u L={L}")
        s.append(f"XG4 nnr dbar 0   0   {n} W={wn}u L={L}")
        s.append(f"XO1 out nnr vdd vdd {p} W={wp}u L={L}")
        s.append(f"XO2 out nnr 0   0   {n} W={wn}u L={L}")
    return "".join(x if x.endswith("\n") else x + "\n" for x in s)


# ---------------------------------------------------------------- decks
HEADER = (".title {tag}\n"
          '.include "%s"\n' % LIB)

# Input: rises at 20 ns, high 80 ns, falls at 100 ns, period 200 ns.
def _stim(vdd):
    return f"Vin in 0 PULSE(0 {vdd} 20n 0.02n 0.02n 80n 200n)\n"


def meas_nominal(arch, dom, lr, cl, cw):
    """Single nominal-corner run (case=0, Vnom, 27 C). Returns dict of metrics
    in seconds: rising/falling output delay, and pulse width where applicable."""
    vdd = dom["vdd"]
    half = vdd / 2
    body = cell_netlist(arch, dom, lr, cl, cw)
    ctl = [".control", "option temp=27", "tran 0.02n 200n"]
    # output edge delays referenced to input edges
    ctl.append(f"meas tran tdr trig v(in) val={half} rise=1 targ v(out) val={half} rise=1")
    ctl.append(f"meas tran tdf trig v(in) val={half} fall=1 targ v(out) val={half} fall=1")
    if arch == "PHI":
        # high pulse after the input rising edge
        ctl.append(f"meas tran pw trig v(out) val={half} rise=1 td=19n targ v(out) val={half} fall=1 td=19n")
        ctl.append("meas tran vrest find v(out) at=190n")   # should be ~0 (no pulse on fall)
    if arch == "PLO":
        ctl.append(f"meas tran pw trig v(out) val={half} fall=1 td=99n targ v(out) val={half} rise=1 td=99n")
        ctl.append("meas tran vrest find v(out) at=80n")    # should be ~vdd (no pulse on rise)
    keys = "tdr=$&tdr tdf=$&tdf"
    if arch in ("PHI", "PLO"):
        keys += " pw=$&pw vrest=$&vrest"
    ctl.append(f'echo "RES {keys}"')
    ctl.append(".endc"); ctl.append(".end")
    deck = (HEADER.format(tag=f"size_{arch}_{dom['n']}") +
            ".param case=0\n" + f"Vdd vdd 0 {vdd}\n" + _stim(vdd) +
            body + f"CL out 0 {CL_FF}f\n" + "\n".join(ctl) + "\n")
    rows = parse_res(run(deck, f"size_{arch}_{dom['n']}"))
    return rows[0] if rows else {}


def target_metric(arch):
    """Which measured quantity must equal 20 ns for this archetype."""
    return {"DLYR": "tdr", "DLYF": "tdf", "PHI": "pw", "PLO": "pw"}[arch]


def size_lr(arch, dom, cl, cw, target_ns=20.0, lr_lo=10.0, lr_hi=150.0, tol=0.02):
    """Bisection on resistor length L_R to hit the 20 ns target at nominal.
    The metric is monotonic increasing in L_R; a NaN means the delayed edge ran
    past the transient window, i.e. L_R is too large."""
    key = target_metric(arch)
    tgt = target_ns * 1e-9
    def m(lr):
        r = meas_nominal(arch, dom, lr, cl, cw)
        v = r.get(key)
        return (v if isinstance(v, float) else float("nan")), r
    lo, hi = lr_lo, lr_hi
    best = None
    for _ in range(10):
        mid = 0.5 * (lo + hi)
        vmid, rmid = m(mid)
        if vmid == vmid:        # finite -> keep as best candidate
            best = (mid, rmid, vmid)
        if vmid != vmid:        # NaN -> edge past window -> L_R too large
            hi = mid; continue
        if abs(vmid - tgt) / tgt <= tol:
            break
        if vmid < tgt:
            lo = mid
        else:
            hi = mid
    return best   # (lr, metrics_dict, achieved_metric_s)


# ---------------------------------------------------------------- area
def area(arch, dom, lr, cl, cw):
    a_r = lr * WR                 # resistor active area (um^2)
    a_c = cl * cw                 # MIM cap area (um^2)
    # rough transistor active area
    wn, wp, Lg = dom["wn"], dom["wp"], dom["Lg"]
    a_dev = NDEV[arch] * 0.5 * (wn + wp) * Lg
    active = a_r + a_c + a_dev
    return dict(a_res=a_r, a_cap=a_c, a_dev=a_dev, active_um2=active,
                r_LxW=f"{lr:.1f}x{WR}", c_LxW=f"{cw:.2f}x{cw:.2f}")


# ---------------------------------------------------------------- measurement
# Output-edge search windows (td) per archetype: (rise_td, fall_td).
_EDGE_TD = {"DLYR": ("19n", "99n"), "DLYF": ("19n", "99n"),
            "PHI": ("19n", "19n"), "PLO": ("99n", "99n")}


def _loop_meas(arch):
    """Measurement block for the in-loop decks (PVT/MC). Assumes ngspice vars
    h (=Vdd/2), v10 (=0.1 Vdd), v90 (=0.9 Vdd) are defined. Returns
    (list_of_meas_lines, echo_key_string). Measures:
      m  = primary metric  (delay for DLY*, pulse width for P*)
      fe = passthrough/fast edge (delay cells only; spurious for pulse cells)
      tr = output rise time 10->90%   tf = output fall time 90->10%"""
    rtd, ftd = _EDGE_TD[arch]
    L = []
    if arch == "PHI":
        L.append("meas tran m trig v(out) val=$&h rise=1 td=19n targ v(out) val=$&h fall=1 td=19n")
        L.append("meas tran fe trig v(in) val=$&h fall=1 targ v(out) val=$&h fall=1")
    elif arch == "PLO":
        L.append("meas tran m trig v(out) val=$&h fall=1 td=99n targ v(out) val=$&h rise=1 td=99n")
        L.append("meas tran fe trig v(in) val=$&h rise=1 targ v(out) val=$&h rise=1")
    elif arch == "DLYR":
        L.append("meas tran m  trig v(in) val=$&h rise=1 targ v(out) val=$&h rise=1")
        L.append("meas tran fe trig v(in) val=$&h fall=1 targ v(out) val=$&h fall=1")
    else:  # DLYF
        L.append("meas tran m  trig v(in) val=$&h fall=1 targ v(out) val=$&h fall=1")
        L.append("meas tran fe trig v(in) val=$&h rise=1 targ v(out) val=$&h rise=1")
    L.append(f"meas tran tr trig v(out) val=$&v10 rise=1 td={rtd} targ v(out) val=$&v90 rise=1 td={rtd}")
    L.append(f"meas tran tf trig v(out) val=$&v90 fall=1 td={ftd} targ v(out) val=$&v10 fall=1 td={ftd}")
    return L, "m=$&m fe=$&fe tr=$&tr tf=$&tf"


# ---------------------------------------------------------------- PVT sweep
def char_pvt(arch, dom, lr, cl, cw):
    """Full 5-corner x 3-supply x 3-temp transient sweep. Returns list of dicts.
    Supplies = dom['vlist'] (1.8/3.3 V: +-10%; 5 V: 3.2/5.0/5.5 V).
    Temperatures = -55 / 27 / 150 C. Process = TT,FF,SS,FS,SF."""
    vdd = dom["vdd"]
    body = cell_netlist(arch, dom, lr, cl, cw)
    vl = " ".join(f"{v:.3f}" for v in dom["vlist"])
    tl = " ".join(str(t) for t in TEMPS)
    ml, keys = _loop_meas(arch)
    mlines = "".join("   " + x + "\n" for x in ml)
    deck = (HEADER.format(tag=f"pvt_{arch}") + f".param case=0\n.option num_threads={NUM_THREADS}\n" +
            f"Vdd vdd 0 {vdd}\n" +
            f"Vin in 0 PULSE(0 {vdd} 20n 0.02n 0.02n 80n 400n)\n" +
            body + f"CL out 0 {CL_FF}f\n" +
            ".control\n"
            "foreach cs 0 1 2 3 4\n"
            f" foreach vd {vl}\n"
            f"  foreach tp {tl}\n"
            "   alterparam case=$cs\n   reset\n"
            "   alter Vdd dc=$vd\n"
            f"   alter Vin pulse=[ 0 $vd 20n 0.02n 0.02n 80n 400n ]\n"
            "   option temp=$tp\n"
            "   let h=$vd/2\n   let v10=0.1*$vd\n   let v90=0.9*$vd\n"
            "   tran 0.05n 200n\n" + mlines +
            f'   echo "RES cs=$cs vd=$vd tp=$tp {keys}"\n'
            "  end\n end\nend\n.endc\n.end\n")
    return parse_res(run(deck, f"pvt_{arch}_{dom['n']}"))


# ---------------------------------------------------------------- Monte Carlo
def char_mc(arch, dom, lr, cl, cw, n=200):
    """Monte Carlo at the typical corner (case=0/TT, nominal Vdd, 27 C) with
    BOTH die-to-die process (PROC_ON=1) and local mismatch (MM_ON=1) enabled.
    Each iteration does reset (re-randomizes all AGAUSS draws) + tran + meas.
    Returns list of per-iteration dicts."""
    vdd = dom["vdd"]
    body = cell_netlist(arch, dom, lr, cl, cw)
    ml, keys = _loop_meas(arch)
    mlines = "".join("  " + x + "\n" for x in ml)
    deck = (HEADER.format(tag=f"mc_{arch}") +
            f".param case=0\n.param PROC_ON=1\n.param MM_ON=1\n.option num_threads={NUM_THREADS}\n" +
            f"Vdd vdd 0 {vdd}\n" +
            f"Vin in 0 PULSE(0 {vdd} 20n 0.02n 0.02n 80n 400n)\n" +
            body + f"CL out 0 {CL_FF}f\n" +
            ".control\n"
            f"let nmc = {n}\nlet i = 0\n"
            "dowhile i < nmc\n"
            "  reset\n"
            "  option temp=27\n"
            f"  let h={vdd/2}\n  let v10={0.1*vdd}\n  let v90={0.9*vdd}\n"
            "  tran 0.05n 180n\n" + mlines +
            f'  echo "RES it=$&i {keys}"\n'
            "  let i = i + 1\n"
            "end\n.endc\n.end\n")
    return parse_res(run(deck, f"mc_{arch}_{dom['n']}"))
