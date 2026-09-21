"""Wall-clock cost of 200 Monte Carlo samples, three drive patterns.
(HANDOFF_monte_carlo.md section 4, runtime table)

Same NMOS5V0 mirror, same analysis (op), 200 samples each:

  inloop    one invocation, 200 x (reset + op), unseeded -- fast, not reproducible
  perrun    200 invocations with `.option seed=k`, 8 parallel workers --
            live and reproducible (the pattern 01_mc_mirror.py uses)
  external  one invocation, 200 x (alterparam S1/S2 + reset + op) with z values
            from Python -- the 04_mc_external_proto.py deck

Each pattern is timed REPEATS times and the fastest is reported, so the numbers
reflect the pattern rather than whatever else the machine was doing.  Timings
include deck writing and process start-up.  They are machine-dependent: the
host is recorded in the output.

This is the baseline for brief acceptance A11 (driver: 200 samples in < 2 s).

Output: results/03_runtime.json
"""
import importlib
import json
import os
import platform
import re
import time
from concurrent.futures import ThreadPoolExecutor

import mc_lib as M

NRUN = 200
REPEATS = 3
WORKERS = 8
ext = importlib.import_module("04_mc_external_proto")

IO_RE = re.compile(r"abs\(i\(vout\)\)\s*=\s*([-\d.eE+]+)")


def inloop():
    lines = [".title rt_inloop"] + M.mirror(mm=1, proc=0) + [
        ".control", "option temp=%d" % M.TEMP, "option numdgt=10",
        "let k = 0", "dowhile k < %d" % NRUN,
        "  reset", "  op", "  print abs(i(vout))", "  let k = k + 1", "end",
        ".endc", ".end", ""]
    return len(IO_RE.findall(M.run("\n".join(lines), "rt_inloop")))


def _single(seed):
    lines = [".title rt_perrun_%d" % seed] + M.mirror(mm=1, proc=0) + [
        ".option seed=%d" % seed, ".control", "option temp=%d" % M.TEMP,
        "option numdgt=10", "op", "print abs(i(vout))", ".endc", ".end", ""]
    return len(IO_RE.findall(M.run("\n".join(lines), "rt_perrun_%03d" % seed)))


def perrun():
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        return sum(ex.map(_single, range(1, NRUN + 1)))


def external():
    return len(ext.run_samples(ext.z_matrix(NRUN), "rt_external"))


PATTERNS = [
    ("inloop", "in-deck loop, one invocation", inloop),
    ("perrun", "`.option seed=k` per invocation, %d parallel workers" % WORKERS, perrun),
    ("external", "external driver (alterparam), one invocation", external),
]

results = {}
print("Runtime, %d samples, best of %d -- ngspice %s" % (NRUN, REPEATS, M.ngspice_version()))
print()
for key, title, fn in PATTERNS:
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        got = fn()
        times.append(time.perf_counter() - t0)
        if got != NRUN:
            raise SystemExit("%s returned %d samples, expected %d" % (key, got, NRUN))
    results[key] = {"title": title, "best_s": min(times), "all_s": times}
    print("  %-10s %-55s %6.2f s" % (key, title, min(times)))

out = {
    "provenance": M.provenance({"step": "03_mc_runtime", "nrun": NRUN, "repeats": REPEATS,
                                "host": {"platform": platform.platform(),
                                         "processor": platform.processor(),
                                         "cpu_count": os.cpu_count(),
                                         "python": platform.python_version()}}),
    "patterns": results,
    "handoff_section4_s": {"inloop": 0.7, "perrun": 3.1, "external": 0.7},
}
(M.RESULTS / "03_runtime.json").write_text(json.dumps(out, indent=1))
print()
print("wrote results/03_runtime.json")
