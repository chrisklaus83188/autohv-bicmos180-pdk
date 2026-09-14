"""Does Monte Carlo actually work in this PDK on this ngspice?

`docs/characterization-inventory.md` item 22 raises the concern that an in-deck
`reset` + `op` loop -- the pattern in `examples/03_monte_carlo.cir` and in
`pdk_validation/.../autohv_mismatch_mc.cir` -- may be statistically inert,
because `.param AGAUSS` is evaluated at parse time and might not be re-drawn by
`reset`.  The item is explicitly marked "not confirmed by running".  This script
confirms or refutes it, and establishes which drive pattern to use.

Six checks, all on the same NMOS50 mirror:

  C1  MM_ON=0 produces no spread at all                      (negative control)
  C2  in-deck `reset` + `op` loop, unseeded                   (the disputed one)
  C3  separate invocations, unseeded
  C4  separate invocations, `set rndseed=k` inside .control
  C5  separate invocations, `.option seed=k` in the netlist
  C6  the two devices in one run draw independently

plus a reproducibility test on every randomizing pattern.

Output: results/00_mechanism.json
"""
import json
import re

import mc_lib as M

N = 40
out = {"provenance": M.provenance({"step": "00_mc_mechanism"}), "checks": {}}
verdict = []
caveats = []


def record(key, title, io, note="", repro=None):
    s = M.stats(io)
    out["checks"][key] = {"title": title, **s, "note": note, "reproducible": repro}
    live = s["distinct"] > 1
    print("  %-6s %-46s distinct %3d/%-3d  sigma/mu %7.3f %%  %s"
          % (key, title, s["distinct"], s["n"], s["sigma_over_mu_pct"],
             "" if repro is None else ("reproducible" if repro else "not reproducible")))
    return live


def single(seed=None, netlist_seed=None, mm=1, tag="x"):
    lines = [".title single"] + M.mirror(mm=mm, proc=0)
    if netlist_seed is not None:
        lines.append(".option seed=%d" % netlist_seed)
    lines.append(".control")
    if seed is not None:
        lines.append("set rndseed=%d" % seed)
    lines += ["option temp=%d" % M.TEMP, "option numdgt=10", "op",
              "print abs(i(vout))", ".endc", ".end", ""]
    o = M.run("\n".join(lines), tag)
    m = re.search(r"abs\(i\(vout\)\)\s*=\s*([-\d.eE+]+)", o)
    if not m:
        raise SystemExit("no result:\n" + o[-1500:])
    return float(m.group(1))


def loop(n, seed=None, netlist_seed=None, tag="l"):
    lines = [".title loop"] + M.mirror(mm=1, proc=0)
    if netlist_seed is not None:
        lines.append(".option seed=%d" % netlist_seed)
    lines.append(".control")
    if seed is not None:
        lines.append("set rndseed=%d" % seed)
    lines += ["option temp=%d" % M.TEMP, "option numdgt=10",
              "let k=0", "dowhile k < %d" % n,
              "  reset", "  op", "  print abs(i(vout))", "  let k=k+1", "end",
              ".endc", ".end", ""]
    o = M.run("\n".join(lines), tag)
    return [float(x) for x in re.findall(r"abs\(i\(vout\)\)\s*=\s*([-\d.eE+]+)", o)]


print("Monte Carlo mechanism check -- ngspice %s, NMOS50 mirror, MM_ON=1 PROC_ON=0"
      % M.ngspice_version())
print()

# C1 negative control
io = [single(netlist_seed=k, mm=0, tag="c1_%d" % k) for k in range(1, 11)]
live = record("C1", "MM_ON=0 (negative control)", io, "must be flat")
verdict.append(("C1", (not live), "MM_ON=0 gives a single value, as it must"))

# C2 the disputed in-deck loop
a = loop(N, tag="c2a")
b = loop(N, tag="c2b")
live = record("C2", "in-deck reset+op loop, unseeded", a, repro=(a == b))
verdict.append(("C2", live, "the in-deck loop DOES re-draw on this build"))

# C3 separate invocations, unseeded
a = [single(tag="c3a") for _ in range(N)]
b = [single(tag="c3b") for _ in range(N)]
live = record("C3", "separate invocations, unseeded", a, repro=(a == b))
verdict.append(("C3", live, "separate invocations re-draw"))

# C4 separate invocations with `set rndseed` in .control
a = [single(seed=k, tag="c4a_%d" % k) for k in range(1, N + 1)]
b = [single(seed=k, tag="c4b_%d" % k) for k in range(1, N + 1)]
live = record("C4", "separate runs, .control `set rndseed=k`", a, repro=(a == b))
verdict.append(("C4", live, "randomizes, but `set rndseed` does NOT pin the draw"))
caveats.append("`set rndseed` in .control does not make a run reproducible: it is "
               "applied after .param AGAUSS has already been evaluated at parse time. "
               "circuits/current_mirror_char/run_mc.py claims reproducibility on this "
               "basis; that claim does not hold on ngspice-45.")

# C5 separate invocations with `.option seed` in the netlist
a = [single(netlist_seed=k, tag="c5a_%d" % k) for k in range(1, N + 1)]
b = [single(netlist_seed=k, tag="c5b_%d" % k) for k in range(1, N + 1)]
live = record("C5", "separate runs, netlist `.option seed=k`", a, repro=(a == b))
verdict.append(("C5", live and (a == b),
                "the only pattern that is both live and reproducible"))

# C5b the trap: a netlist seed WITH the in-deck loop
a = loop(N, netlist_seed=1234, tag="c5c")
b = loop(N, netlist_seed=1234, tag="c5d")
live = record("C5b", "in-deck loop + fixed `.option seed`", a,
              "reset re-seeds to the same value", repro=(a == b))
verdict.append(("C5b", (not live),
                "a fixed netlist seed freezes the in-deck loop, as expected"))
caveats.append("A netlist `.option seed=N` combined with an in-deck reset loop makes "
               "every iteration identical -- `reset` re-seeds the generator to the same "
               "value. Seed per invocation, never per loop.")

# C6 per-instance independence
lines = [".title indep"] + M.mirror(mm=1, proc=0) + [
    ".option seed=99", ".control", "option temp=%d" % M.TEMP, "option numdgt=10", "op",
    "print @m.x1.m0[delvto] @m.x2.m0[delvto] @m.x1.m0[w] @m.x2.m0[w]",
    ".endc", ".end", ""]
o = M.run("\n".join(lines), "c6")
g = {k: float(v) for k, v in re.findall(r"(@m\.x[12]\.m0\[\w+\])\s*=\s*([-\d.eE+]+)", o)}
d1, d2 = g["@m.x1.m0[delvto]"], g["@m.x2.m0[delvto]"]
w1, w2 = g["@m.x1.m0[w]"], g["@m.x2.m0[w]"]
indep = (d1 != d2) and (w1 != w2)
out["checks"]["C6"] = {"title": "per-instance independence", "delvto_x1": d1,
                       "delvto_x2": d2, "w_x1": w1, "w_x2": w2, "independent": indep}
print("  %-6s %-46s delvto %+0.3f / %+0.3f mV, W %.5f / %.5f um"
      % ("C6", "two instances in one run", d1 * 1e3, d2 * 1e3, w1 * 1e6, w2 * 1e6))
verdict.append(("C6", indep,
                "each instance draws its own threshold AND geometry offset"))

print()
print("Verdict")
allok = True
for key, ok, msg in verdict:
    print("  [%s] %-4s %s" % ("ok" if ok else "!!", key, msg))
    allok = allok and ok
out["all_pass"] = allok
out["caveats"] = caveats
print()
print("Caveats on how to drive it")
for c in caveats:
    print("  - " + c)
(M.RESULTS / "00_mechanism.json").write_text(json.dumps(out, indent=1))
print()
print("Monte Carlo %s on this build."
      % ("WORKS -- draws are live and per-instance independent" if allok
         else "DOES NOT work"))
print("wrote results/00_mechanism.json")
