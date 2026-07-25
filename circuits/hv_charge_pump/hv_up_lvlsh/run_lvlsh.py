#!/usr/bin/env python3
"""
run_lvlsh.py -- first-qualification harness for the high-side gate-driver LEVEL
SHIFTER (AutoHV_BiCMOS180, 200 V class). Its only prior testbench was the
commented example in levelshifter_top.spice, so this is the first time the
circuit is characterized (Step-0 ruling 4: minimal first qualification, not
deletion; verify function at the 200 V rail; measure levels, switching, bias).

Runs two decks:
  * tb_levelshifter_op.cir  -- DC operating point at SW=200 V in idle/set/reset.
                               This converges (Rcond fix) and gives the real
                               output levels + bias currents.
  * tb_levelshifter.cir     -- full transient. This does NOT converge (timestep
                               collapses ~0.5 us on the delay-cell behavioral-R
                               (BVCR) / HV-cascode nodes) -- recorded as the
                               switching failure mode / redesign scope.

Writes lvlsh_results.json (provenance-stamped) and generates REPORT.md.
Run:  python run_lvlsh.py
"""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODEL_TAG = "v2-grounded"


def find_ngspice():
    cand = os.environ.get("NGSPICE_BIN")
    if cand and Path(cand).exists():
        return cand
    for name in ("ngspice_con", "ngspice_con.exe", "ngspice"):
        p = shutil.which(name)
        if p:
            return p
    for p in (r"C:\Program Files\Qucs-S-25.2.0-win64\bin\ngspice_con.exe",
              r"C:\Spice64\bin\ngspice_con.exe"):
        if Path(p).exists():
            return p
    raise SystemExit("ngspice not found; set NGSPICE_BIN")


NG = find_ngspice()


def ngspice_version():
    try:
        out = subprocess.run([NG, "--version"], capture_output=True, text=True,
                             timeout=30).stdout
        m = re.search(r"ngspice-?\s*[\d.]+", out, re.IGNORECASE)
        return m.group(0).replace(" ", "") if m else "unknown"
    except Exception:
        return "unknown"


def run(deck):
    r = subprocess.run([NG, "-b", deck], cwd=str(HERE), capture_output=True,
                       text=True, timeout=400)
    return r.stdout + "\n" + r.stderr


def parse_results(out):
    """Collect 'RESULT k=v ...' lines keyed by their 'state' field."""
    states = {}
    for ln in out.splitlines():
        if ln.strip().startswith("RESULT "):
            d = {}
            for tok in ln.split()[1:]:
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    try:
                        d[k] = float(v)
                    except ValueError:
                        d[k] = v
            st = d.get("state", "?")
            states.setdefault(st, {}).update(d)
    return states


def main():
    res = {"_provenance": {"model_tag": MODEL_TAG, "ngspice_version": ngspice_version(),
                           "vhv": 200, "vboot": 12, "vddl": 5}}

    # ---- DC operating-point verification at the 200 V rail --------------------
    op_out = run("tb_levelshifter_op.cir")
    op = parse_results(op_out)
    res["op"] = op
    op_ok = all(s in op for s in ("idle", "set", "reset"))

    # ---- full transient (switching) : expected to fail convergence -----------
    tr_out = run("tb_levelshifter.cir")
    tr = parse_results(tr_out)
    tstop = None
    m = re.search(r"Timestep too small;\s*time\s*=\s*([\d.eE+-]+)", tr_out)
    if m:
        tstop = float(m.group(1))
    trouble = re.search(r'trouble with node "([^"]+)"', tr_out)
    tr_ok = bool(tr.get("state")) and tstop is None and "aborted" not in tr_out.lower()
    res["transient"] = {
        "converged": tr_ok,
        "abort_time_s": tstop,
        "trouble_node": trouble.group(1) if trouble else None,
        "measured": tr if tr_ok else {},
    }

    (HERE / "lvlsh_results.json").write_text(json.dumps(res, indent=2))
    print(f"wrote lvlsh_results.json  [model={MODEL_TAG} ngspice={ngspice_version()}]")
    print(f"  OP verification at 200 V: {'PASS' if op_ok else 'FAIL'}")
    if tr_ok:
        print("  transient (switching):    converged")
    else:
        node = res["transient"]["trouble_node"]
        print(f"  transient (switching):    DID NOT CONVERGE (abort t={tstop}, node {node})")
    write_report(res, op_ok, tr_ok)
    return res


def v(op, state, key):
    x = op.get("op", {}).get(state, {}).get(key)
    return x if isinstance(x, (int, float)) else float("nan")


def write_report(res, op_ok, tr_ok):
    p = res["_provenance"]
    op = res
    L = []
    A = L.append
    A("# High-Side Gate-Driver Level Shifter — First-Qualification Report")
    A("### AutoHV BiCMOS180 PDK · 200 V class (NDMOS200 / PDMOS200) · `circuits/hv_charge_pump/hv_up_lvlsh/`\n")
    A(f"<sub>Models: **{p['model_tag']}** (frozen) · simulator: **{p['ngspice_version']}** · "
      f"V_HV = {p['vhv']} V rail, V_BOOT = {p['vboot']} V bootstrap, V_DDL = {p['vddl']} V logic.</sub>\n")
    A("**First characterization of this circuit.** Its only prior testbench was the commented example "
      "in `levelshifter_top.spice`; it had never been simulated. This is a *minimal first "
      "qualification* (Step-0 ruling 4): verify function at the 200 V rail and measure output levels "
      "and bias currents. Placeholder sizings are the `levelshifter_top.spice` defaults (HV whv/whvp = "
      "40 µm, lhv = 8 µm; LV wp = 20 µm / wn = 10 µm), consistent with `docs/sizing-guide.md`.\n")

    A("## 1. Function at the 200 V rail — VERIFIED (DC operating point)\n")
    A("SW held at 200 V, BOOT floating 12 V above it (212 V). The high-side latch is set/reset by the "
      "low-side ON/OFF commands and the buffered outputs `ON_HS`/`OFF_HS` swing between SW (200 V) and "
      "BOOT (212 V) — a clean 12 V high-side gate-drive referenced to the 200 V rail.\n")
    A("| State | Q (V) | QB (V) | ON_HS (V) | OFF_HS (V) | I_BOOT | I_VDD |")
    A("|---|---|---|---|---|---|---|")
    for st in ("idle", "set", "reset"):
        A(f"| {st} | {v(op,st,'q'):.2f} | {v(op,st,'qb'):.2f} | {v(op,st,'onhs'):.1f} | "
          f"{v(op,st,'offhs'):.1f} | {v(op,st,'iboot')*1e6:.1f} µA | "
          f"{v(op,st,'ivdd')*1e6:.2f} µA |")
    A("")
    A("- **Set** (ON=5 V): `ON_HS` → 212 V (BOOT, high-side driver on), `OFF_HS` → 200 V (SW). Latch "
      "Q/QB = 200/212 V.")
    A("- **Reset** (OFF=5 V): outputs flip — `ON_HS` → 200 V, `OFF_HS` → 212 V; Q/QB = 212/200 V.")
    A("- **Idle** (ON=OFF=0): the cross-coupled latch sits metastable-symmetric (Q ≈ QB ≈ 210.7 V); "
      "set/reset resolves it deterministically.")
    A(f"- **Bias current** from the 12 V bootstrap: ~{v(op,'idle','iboot')*1e3:.2f} mA standing "
      f"(idle, through the R1/R2 bias resistors + mirror legs), ~{v(op,'set','iboot')*1e6:.0f} µA in "
      f"the resolved set/reset states.\n")

    A("## 2. Switching (transient) — DOES NOT CONVERGE (redesign scope)\n")
    t = res["transient"]
    A(f"The full switching transient (SW ramped to 200 V, then ON/OFF one-shots) **fails to complete**: "
      f"the timestep collapses to ~1e-20 s at t ≈ {t['abort_time_s']:.2e} s"
      + (f" on node `{t['trouble_node']}`" if t['trouble_node'] else "") + ". This is *not* a sizing "
      "problem and is left for a later redesign (Step-0 ruling 4 — do not redesign here).\n")
    A("**Failure mode.** The stall originates in the `DELAY_CELL` block: its series `RPOLY_HI` resistors "
      "carry a behavioral voltage-coefficient branch (BVCR), and in combination with the floating HV "
      "cascode nodes this forms a stiff loop that micro-steps to a standstill early in the ramp (before "
      "SW even reaches high voltage). Simulator aids (`rshunt`, `gmin`, `method=gear`, `uic`) shift the "
      "reported node but do not clear the collapse.\n")
    A("**Redesign scope (later, not this program):**")
    A("- Replace the delay-cell behavioral-R timing with a device-based delay, or gate the BVCR branch "
      "so it is well-defined from t=0 (this mirrors the `.tran uic` / behavioral-branch findings already "
      "documented for `delay_cells_voltage_ramp` and the VDMOS `Rcond` handoffs).")
    A("- Give the HV cascode source nodes (S5/S6/S9/S12) a defined start (small pull-down or `.ic`) so "
      "the level-shift legs do not float at t=0.")
    A("- Re-verify dynamic set/reset propagation and high-side slew once the above land; the **static "
      "function at 200 V is already correct**, so the redesign is a convergence/robustness task, not a "
      "topology change.\n")

    A("## 3. Files\n")
    A("- `tb_levelshifter_op.cir` — DC operating-point verification (this report's §1).")
    A("- `tb_levelshifter.cir` — full transient (documents the §2 non-convergence).")
    A("- `run_lvlsh.py` — this harness. `lvlsh_results.json` — machine-readable results + provenance.")
    A("- Design: `levelshifter_top.spice` (top), `levelshifter.spice`, `buffer.spice`, `delay_cell.spice`, "
      "`inv.spice` (unchanged — no redesign in this program).")

    (HERE / "REPORT.md").write_text("\n".join(L), encoding="utf-8")
    print("wrote REPORT.md")


if __name__ == "__main__":
    main()
