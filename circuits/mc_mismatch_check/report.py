"""Build REPORT.md from results/00_mechanism.json and results/01_mc_mirror.json,
plus results/02_m_sweep.json, 03_runtime.json and 04_external_proto.json when present."""
import json
from pathlib import Path

import mc_lib as M

HERE = Path(__file__).resolve().parent
mech = json.load(open(M.RESULTS / "00_mechanism.json"))
mc = json.load(open(M.RESULTS / "01_mc_mirror.json"))

P = []


def w(s=""):
    P.append(s)


io = [r["io"] for r in mc["runs"]]
d1 = [r["d1"] for r in mc["runs"]]
d2 = [r["d2"] for r in mc["runs"]]
n = len(io)
s = mc["iout"]
pred = mc["prediction"]
srt = sorted(io)


def pct(p):
    return srt[min(n - 1, int(round(p / 100 * (n - 1))))]


# how far out did the draws actually go, in units of the formula sigma?
sig = pred["sigma_vth_per_device_V"]
zmax = max(abs(v) / sig for v in d1 + d2)

w("# Monte Carlo check + NMOS50 current-mirror mismatch")
w()
w("Two questions, answered in order: does the PDK's Monte Carlo machinery actually")
w("randomize, and what does local mismatch do to a simple 10 uA mirror.")
w()
w("| | |")
w("|---|---|")
w("| simulator | ngspice `%s` |" % mech["provenance"]["ngspice_version"])
w("| model tag | `%s` |" % mech["provenance"]["model_tag"])
w("| corner / supply / temp | TT (`case=0`) / %g V / %g C |"
  % (M.VDD, M.TEMP))
w("| switches | `MM_ON=1`, `PROC_ON=0` (local mismatch only) |")
w("| runs | %d |" % n)
w()

w("## 1. Does Monte Carlo work?")
w()
w("Yes. `docs/characterization-inventory.md` item 22 suspects the in-deck")
w("`reset` + `op` loop of being statistically inert, and marks the suspicion **not")
w("confirmed by running**. Running it settles the question the other way: on")
w("ngspice-45 `reset` does re-draw every `.param AGAUSS` in the circuit, so the")
w("loop is live and item 22 can be closed as not reproduced -- with one exception")
w("noted below.")
w()
w("| check | what was driven | distinct samples | sigma/mu | reproducible |")
w("|---|---|---|---|---|")
for k in ("C1", "C2", "C3", "C4", "C5", "C5b"):
    c = mech["checks"][k]
    rep = c.get("reproducible")
    w("| %s | %s | %d / %d | %.3f %% | %s |"
      % (k, c["title"], c["distinct"], c["n"], c["sigma_over_mu_pct"],
         "-" if rep is None else ("yes" if rep else "no")))
c6 = mech["checks"]["C6"]
w()
w("Per-instance independence is direct, not inferred. In a single run the two")
w("mirror devices report different applied offsets:")
w()
w("```")
w("X1  delvto %+0.3f mV   W %.5f um" % (c6["delvto_x1"] * 1e3, c6["w_x1"] * 1e6))
w("X2  delvto %+0.3f mV   W %.5f um" % (c6["delvto_x2"] * 1e3, c6["w_x2"] * 1e6))
w("```")
w()
w("Both the threshold term and the geometry term are drawn per instance, which is")
w("what makes a mirror ratio move at all.")
w()

w("### Two traps in how you drive it")
w()
w("1. **`set rndseed` inside `.control` does not pin the draw.** It is applied")
w("   after `.param AGAUSS` has already been evaluated at parse time, so the same")
w("   seed gives a different answer every time (check C4). This matters:")
w("   `circuits/current_mirror_char/run_mc.py` documents itself as *\"Reproducible:")
w("   run k uses `set rndseed=k`\"*, and that claim does not hold on this build.")
w("   Its statistics are still valid, since the draws are live; only the")
w("   reproducibility claim fails.")
w("2. **A netlist `.option seed=N` plus an in-deck loop freezes the loop.** `reset`")
w("   re-seeds the generator to the same value, so all N iterations return one")
w("   identical result (check C5b). That is exactly the inert-loop failure item 22")
w("   predicted, reachable only by adding a fixed seed.")
w()
w("**Use one invocation per sample with `.option seed=k` in the netlist.** That is")
w("the only pattern measured to be both statistically live and bit-reproducible")
w("(check C5), and it is what the mirror run below uses.")
w()

w("## 2. The mirror")
w()
w("Simple two-transistor NMOS mirror, nothing cascoded. Both devices `NMOS50`,")
w("W = %g um, L = %g um, which is the sizing guide's own gm/Id ~ 6 entry for" % (M.W, M.L))
w("NMOS50 at 10 uA. Reference is an ideal 10 uA source into the diode-connected")
w("device; the output sits at Vdd/2.")
w()
w("```spice")
w("Vdd  dd 0 %g" % M.VDD)
w("Iref dd in %gu" % (M.IREF * 1e6))
w("X1 in  in 0 0 NMOS50 W=%gu L=%gu    ; diode-connected reference" % (M.W, M.L))
w("X2 out in 0 0 NMOS50 W=%gu L=%gu    ; mirror output" % (M.W, M.L))
w("Vout out 0 %g" % M.VOUT)
w("```")
w()
w("## 3. Result")
w()
w("| quantity | value |")
w("|---|---|")
w("| mean output current | %.4f uA |" % (s["mean"] * 1e6))
w("| standard deviation | %.4f uA |" % (s["std"] * 1e6))
w("| **sigma / mu** | **%.2f %%** |" % s["sigma_over_mu_pct"])
w("| min / max over %d runs | %.3f / %.3f uA |" % (n, s["min"] * 1e6, s["max"] * 1e6))
w("| 1st / 50th / 99th percentile | %.3f / %.3f / %.3f uA |"
  % (pct(1) * 1e6, pct(50) * 1e6, pct(99) * 1e6))
w("| mean gain, Iout / Iref | %.4f |" % mc["gain_mean"])
w("| gain with mismatch off | %.4f |" % mc["gain_zero_mismatch"])
w("| gm/Id at the operating point | %.2f /V |" % mc["gm_over_id_mean"])
w()
w("The %.1f %% by which the mean sits above 10 uA is **not** mismatch. It is the"
  % (100 * (mc["gain_zero_mismatch"] - 1)))
w("systematic gain error of a simple mirror: the reference device runs at")
w("Vds = Vgs = %.3f V" % mc["runs"][0]["vg"])
w("while the output device sits at %g V, and channel-length modulation makes up the" % M.VOUT)
w("difference. Turning mismatch off leaves it unchanged at %.4f. Mismatch is the"
  % mc["gain_zero_mismatch"])
w("spread around that mean, not the offset of it.")
w()

# histogram
lo, hi = min(io), max(io)
NB = 24
bins = [0] * NB
for v in io:
    k = min(NB - 1, int((v - lo) / (hi - lo) * NB))
    bins[k] += 1
peak = max(bins)
w("Distribution of the output current over the %d runs:" % n)
w()
w("```")
for k in range(NB):
    c = lo + (k + 0.5) * (hi - lo) / NB
    w("%6.3f uA | %-40s %3d" % (c * 1e6, "#" * int(round(40 * bins[k] / peak)), bins[k]))
w("```")
w()

w("## 4. Cross-check against the model's own numbers")
w()
w("The spread is not only self-consistent, it matches what the wrapper's mismatch")
w("formula says it should be before any simulation is run. `NMOS50` in")
w("`autohv_bicmos180_case.lib` draws its threshold offset as")
w()
w("```")
w("AGAUSS(0, 0.033/sqrt(W*L), 3)")
w("```")
w()
w("and ngspice's `AGAUSS(nom, avar, n)` has standard deviation `avar/n`, so the")
w("0.033 V.um figure is a 3-sigma coefficient and the per-device sigma at")
w("W*L = %g um^2 is %.3f mV." % (M.W * M.L, pred["sigma_vth_per_device_V"] * 1e3))
w()
w("| quantity | formula | measured over %d runs | error |" % n)
w("|---|---|---|---|")
w("| sigma(delvto), one device | %.3f mV | %.3f mV | %+.1f %% |"
  % (pred["sigma_vth_per_device_V"] * 1e3, mc["delvto_dev1"]["std"] * 1e3,
     100 * (mc["delvto_dev1"]["std"] / pred["sigma_vth_per_device_V"] - 1)))
w("| sigma(delvto2 - delvto1) | %.3f mV | %.3f mV | %+.1f %% |"
  % (pred["sigma_vth_pair_V"] * 1e3, mc["delvto_pair_diff"]["std"] * 1e3,
     100 * (mc["delvto_pair_diff"]["std"] / pred["sigma_vth_pair_V"] - 1)))
w("| sigma/mu of Iout | %.3f %% | %.3f %% | %+.1f %% |"
  % (pred["total_pct"], s["sigma_over_mu_pct"],
     100 * (s["sigma_over_mu_pct"] / pred["total_pct"] - 1)))
w()
w("The predicted current spread is `(gm/Id) x sigma(delta Vth)` = %.2f x %.3f mV ="
  % (mc["gm_over_id_mean"], pred["sigma_vth_pair_V"] * 1e3))
w("%.2f %%, with the W and L mismatch terms adding %.2f %% in quadrature -- they are"
  % (pred["from_vth_pct"], pred["from_geometry_pct"]))
w("negligible here, so this mirror's matching is a threshold-voltage problem and")
w("nothing else.")
w()
w("Independently, `docs/sizing-guide.md` pre-registers **%.2f %%** as the matched-pair"
  % pred["sizing_guide_pct"])
w("sigma(dI/I) for exactly this device, current and geometry. Three numbers derived")
w("three different ways agree:")
w()
w("| source | sigma(dI/I) |")
w("|---|---|")
w("| sizing guide, pre-registered | %.2f %% |" % pred["sizing_guide_pct"])
w("| wrapper formula, hand-computed | %.2f %% |" % pred["total_pct"])
w("| this Monte Carlo, %d runs | %.2f %% |" % (n, s["sigma_over_mu_pct"]))
w()
w("At %d samples the standard error on a standard deviation is about %.1f %%, so the"
  % (n, 100 / (2 * (n - 1)) ** 0.5))
w("%.1f %% gap between measurement and formula is roughly %.1f standard errors --"
  % (100 * (s["sigma_over_mu_pct"] / pred["total_pct"] - 1),
     (s["sigma_over_mu_pct"] / pred["total_pct"] - 1) / (1 / (2 * (n - 1)) ** 0.5)))
w("ordinary sampling noise, not a discrepancy.")
w()
w("One thing this run does *not* settle: the largest threshold draw seen was %.2f"
  % zmax)
w("sigma. The `AGAUSS(..., 3)` third argument is a scale factor in ngspice, not a")
w("truncation, and %d samples cannot distinguish a truncated tail from a Gaussian one."
  % n)
w("If the tails matter for a design, that needs its own experiment.")
w()


def _load(name):
    p = M.RESULTS / name
    return json.load(open(p)) if p.exists() else None


msw = _load("02_m_sweep.json")
if msw:
    w("## 5. Does `M` reduce mismatch?")
    w()
    w("No. Every mismatch term in the v2.2 MOS wrapper scales as `1/sqrt(AUM2)` with")
    w("`AUM2 = W*L`, and `M` is not in it. Same mirror, %d fixed-seed runs per row,"
      % msw["provenance"]["nrun_per_geometry"])
    w("four times the baseline area reached three ways:")
    w()
    w("| geometry | total area | sigma(delvto), pooled | formula, v2.2 wrapper "
      "| formula, `M` in `AUM2` | sigma/mu(Iout) |")
    w("|---|---|---|---|---|---|")
    for g in msw["geometries"]:
        w("| W=%g L=%g M=%d | %.1f um^2 | %.3f mV | %.3f mV | %.3f mV | %.3f %% |"
          % (g["W_um"], g["L_um"], g["M"], g["total_area_um2"],
             g["sigma_delvto_pooled_mV"], g["formula_v2_2_mV"], g["formula_R1_mV"],
             g["sigma_over_mu_pct"]))
    w()
    w("Quadrupling the area through `M` leaves sigma(delvto) where the v2.2 formula")
    w("puts it; through W or L it halves. The sigma/mu column also moves with gm/Id --")
    w("a wider device at fixed current sits closer to weak inversion, a longer one")
    w("further from it -- which is legitimate; the delvto column is the clean evidence.")
    w("This table is the \"before\" for acceptance A1 of the MC realism program: after")
    w("the `AUM2` fix the M=4 row must follow the right-hand formula column.")
    w()

rt = _load("03_runtime.json")
if rt:
    host = rt["provenance"]["host"]
    w("## 6. Runtime, %d samples" % rt["provenance"]["nrun"])
    w()
    w("Best of %d, including deck writing and process start-up. Host: %s, %d logical CPUs."
      % (rt["provenance"]["repeats"], host["platform"], host["cpu_count"]))
    w()
    w("| pattern | wall clock | HANDOFF section 4 |")
    w("|---|---|---|")
    for k, p in rt["patterns"].items():
        w("| %s | %.2f s | %.1f s |" % (p["title"], p["best_s"], rt["handoff_section4_s"][k]))
    w()
    w("The in-deck loop is fast but not reproducible (check C2). Per-invocation seeding")
    w("is reproducible but pays a process start per sample. The external driver keeps")
    w("both properties in one invocation, which is the pattern the program's Phase 3")
    w("driver builds on (acceptance A11: under 2 s).")
    w()

ext = _load("04_external_proto.json")
if ext:
    pr = ext["prediction"]
    w("## 7. External random-number driver prototype")
    w()
    w("Each device carries its own knob (`MM_SIGMA={S1}` on X1, `{S2}` on X2) with")
    w("`MM_ON=0`; Python draws the unit-normal values (numpy `default_rng(%d)`) and"
      % ext["provenance"]["z_seed"])
    w("one ngspice invocation steps `alterparam` + `reset` + `op` through all %d samples."
      % ext["provenance"]["nrun"])
    w()
    w("| quantity | value |")
    w("|---|---|")
    w("| sigma/mu of Iout | %.3f %% |" % ext["sigma_over_mu_pct"])
    w("| distinct samples | %d / %d |" % (ext["iout"]["distinct"], ext["iout"]["n"]))
    w("| bit-identical on repeat | %s |" % ("yes" if ext["bit_identical_on_repeat"] else "**no**"))
    w("| first-order prediction, one knob per device | %.3f %% |"
      % pr["correlated_single_knob_pct"])
    w("| wrapper formula, independent terms (section 4) | %.3f %% |"
      % pr["independent_terms_pct_from_01"])
    w("| native `MM_ON=1` measurement (section 3) | %.3f %% |"
      % ext["native_mm_on_sigma_over_mu_pct_from_01"])
    w("| HANDOFF section 4 prototype | %.2f %% |" % ext["handoff_section4_sigma_over_mu_pct"])
    w()
    w("One `MM_SIGMA` scales a device's Vth, W and L terms by the same z, so the three")
    w("are perfectly correlated; the W term then partly cancels the Vth term, which is")
    w("why the one-knob prediction sits slightly below the independent-terms one. The")
    w("program replaces `MM_SIGMA` with independent `Z_VT`, `Z_W`, `Z_L` (R5 as ruled).")
    w()

w("## 8. Reproduce")
w()
w("```bash")
w("cd circuits/mc_mismatch_check")
w("python 00_mc_mechanism.py       # does MC randomize, and how must it be driven")
w("python 01_mc_mirror.py          # the 200-run mirror measurement")
w("python 02_mc_m_sweep.py         # does M reduce mismatch (not in the v2.2 wrappers)")
w("python 04_mc_external_proto.py  # external random-number driver prototype")
w("python 03_mc_runtime.py         # wall clock of the three patterns; run last, alone")
w("python report.py")
w("```")
w()
w("Seeds 1..%d, one ngspice invocation each, so the numbers above are" % n)
w("bit-reproducible on this build.")
w()

(HERE / "REPORT.md").write_text("\n".join(P) + "\n", newline="\n", encoding="utf-8")
print("wrote REPORT.md (%d lines)" % len(P))
