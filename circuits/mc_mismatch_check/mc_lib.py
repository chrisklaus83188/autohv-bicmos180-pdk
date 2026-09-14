"""Monte Carlo mechanism check + mismatch characterization of a simple NMOS50
current mirror.  AutoHV BiCMOS 180 PDK.

Device under test
-----------------
Simple two-transistor NMOS mirror, both devices NMOS50, W = 4.7 um, L = 1.0 um.
That geometry is the sizing guide's own gm/Id ~ 6 entry for NMOS50 at 10 uA
(docs/sizing-guide.md), which also pre-registers a matched-pair sigma(dI/I) of
4.08 % -- so the guide gives an independent number to check the MC against.

  Iref  ---> node `in`, diode-connected X1
  X2 mirrors into node `out`, held at Vdd/2 by an ideal source.

Nominal PVT throughout: case=0 (TT), Vdd = 5.0 V, 27 C.
Mismatch only: MM_ON=1, PROC_ON=0.

Why two drive patterns are tested
---------------------------------
`docs/characterization-inventory.md` item 22 flags that an in-deck
`reset`+`op` loop may be statistically inert, because `.param AGAUSS` is
evaluated at parse time and would not be re-drawn by `reset`.  Both patterns are
therefore measured before any result is trusted:

  inloop  -- one ngspice invocation, N iterations of `reset` + `op`
  perrun  -- N ngspice invocations, `set rndseed=k` in each
"""
import os
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECK = HERE / "decks"
RESULTS = HERE / "results"
DECK.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

# decks/ -> mc_mismatch_check/ -> circuits/ -> repo root
LIB = "../../../autohv_bicmos180_case.lib"
MODEL_TAG = "v2-grounded"

# device under test
DEV = "NMOS50"
W = 4.7        # um   -- sizing guide gm/Id~6 entry for NMOS50 at 10 uA
L = 1.0        # um   -- sizing guide BSIM3 analog default
IREF = 10e-6   # A
VDD = 5.0      # V
VOUT = 2.5     # V    -- mirror output held at Vdd/2 (MIRROR_CHAR anchor)
TEMP = 27      # degC
CASE = 0       # TT
GUIDE_SIGMA_PCT = 4.08   # docs/sizing-guide.md pre-registered matched-pair sigma


def _find_ngspice() -> str:
    cand = os.environ.get("NGSPICE_BIN")
    if cand and Path(cand).exists():
        return cand
    for name in ("ngspice_con", "ngspice_con.exe", "ngspice"):
        p = shutil.which(name)
        if p:
            return p
    for p in (r"C:\Program Files\Qucs-S-25.2.0-win64\bin\ngspice_con.exe",
              r"C:\Spice64\bin\ngspice_con.exe",
              r"C:\Program Files\ngspice\bin\ngspice_con.exe"):
        if Path(p).exists():
            return p
    raise RuntimeError("ngspice not found; set NGSPICE_BIN.")


NGSPICE = _find_ngspice()
_ENV = dict(os.environ, OMP_WAIT_POLICY="passive", OMP_DYNAMIC="false")
_NGVER = None


def ngspice_version() -> str:
    global _NGVER
    if _NGVER:
        return _NGVER
    _NGVER = "unknown"
    try:
        out = subprocess.run([NGSPICE, "--version"], capture_output=True,
                             text=True, timeout=30).stdout
        m = re.search(r"ngspice-?\s*[\d.]+", out, re.IGNORECASE)
        if m:
            _NGVER = m.group(0).replace(" ", "")
    except Exception:
        pass
    return _NGVER


def provenance(extra=None):
    d = {"model_tag": MODEL_TAG, "ngspice_version": ngspice_version(),
         "device": DEV, "W_um": W, "L_um": L, "iref_A": IREF,
         "vdd_V": VDD, "vout_V": VOUT, "temp_C": TEMP, "corner": "TT"}
    if extra:
        d.update(extra)
    return d


def mirror(mm=1, proc=0, case=CASE, vdd=VDD, iref=IREF):
    """The circuit itself -- identical in every deck built here."""
    return [
        '.include "%s"' % LIB,
        ".param case=%d" % case,
        ".param PROC_ON=%d" % proc,
        ".param MM_ON=%d" % mm,
        ".option num_threads=1",
        "Vdd  dd 0 %.6g" % vdd,
        "Iref dd in %.6g" % iref,
        "X1 in  in 0 0 %s W=%gu L=%gu" % (DEV, W, L),   # diode-connected ref
        "X2 out in 0 0 %s W=%gu L=%gu" % (DEV, W, L),   # mirror output
        "Vout out 0 %.6g" % VOUT,
    ]


def deck_inloop(n, mm=1, proc=0, seed=None):
    """Pattern A: one invocation, n iterations of `reset` + `op`."""
    lines = [".title mc_inloop"] + mirror(mm, proc) + [".control"]
    if seed is not None:
        lines.append("set rndseed=%d" % seed)
    lines += [
        "option temp=%d" % TEMP,
        "let k = 0",
        "dowhile k < %d" % n,
        "  reset",
        "  op",
        "  let io = abs(i(vout))",
        "  let ii = abs(i(vdd)) - io",
        '  echo "RES k=$&k iout=$&io"',
        "  let k = k + 1",
        "end",
        ".endc", ".end", ""]
    return "\n".join(lines)


def deck_single(seed=None, mm=1, proc=0):
    """Pattern B: one invocation = one Monte Carlo sample."""
    lines = [".title mc_single"] + mirror(mm, proc) + [".control"]
    if seed is not None:
        lines.append("set rndseed=%d" % seed)
    lines += [
        "option temp=%d" % TEMP,
        "op",
        "let io = abs(i(vout))",
        "let vg = v(in)",
        'echo "RES iout=$&io vgs=$&vg"',
        ".endc", ".end", ""]
    return "\n".join(lines)


def run(text, tag, timeout=600):
    path = DECK / (tag + ".cir")
    path.write_text(text, newline="\n")
    r = subprocess.run([NGSPICE, "-b", path.name], cwd=str(DECK),
                       capture_output=True, text=True, timeout=timeout, env=_ENV)
    return r.stdout + "\n" + r.stderr


def parse_res(out):
    """Collect every `RES key=value ...` line an ngspice deck echoed."""
    rows = []
    for ln in out.splitlines():
        if ln.strip().startswith("RES "):
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


def stats(xs):
    n = len(xs)
    if n == 0:
        return {"n": 0}
    mu = sum(xs) / n
    if n > 1:
        var = sum((x - mu) ** 2 for x in xs) / (n - 1)
    else:
        var = 0.0
    sd = var ** 0.5
    s = sorted(xs)
    return {"n": n, "mean": mu, "std": sd,
            "sigma_over_mu_pct": 100 * sd / mu if mu else float("nan"),
            "min": s[0], "max": s[-1],
            "p50": s[n // 2],
            "distinct": len(set(xs))}
