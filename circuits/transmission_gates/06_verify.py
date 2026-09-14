"""Step 5 -- verify the generated cells.

(a) Every one of the 18 cells is instantiated from cells.lib and swept over the
    input level.  The measured Ron must reproduce the step-04 numbers, which
    were taken on hand-built device pairs -- that is the cross-check that the
    generator wrote what was characterized.  TGB cells are checked twice: with
    the bodies strapped to the rails (must equal the TG cell) and with them
    strapped to the switch terminal (must equal the step-04 srcbody numbers).

(b) Switching behaviour: the internal inverter delay en -> enb (the skew
    between the two pass devices) and the charge injected onto a held node when
    the switch opens.

Output: results/06_verify.json
"""
import json
import re

import tg_lib as T

DOMTAG = {"1v8": "1V8", "3v3": "3V3", "5v0": "5V0"}
CLASSES = ["1K", "100R", "10R"]
TOL = 0.02          # allowed relative difference against step 04

pvt = json.load(open(T.RESULTS / "04_pvt.json"))
out = {"provenance": T.provenance({"step": "06_verify"}), "ron": {}, "timing": {}}
fails = []


def head(dom, extra=""):
    d = T.DOMAINS[dom]
    return [".title verify", '.include "' + T.LIB + '"',
            '.include "../cells.lib"',
            ".param case=0", ".param PROC_ON=0", ".param MM_ON=0",
            ".option num_threads=1",
            "Vdd vdd 0 %.6g" % d["vdd"]] + ([extra] if extra else [])


# ---------------------------------------------------------------- (a) Ron
for dom in ("1v8", "3v3", "5v0"):
    d = T.DOMAINS[dom]
    out["ron"][dom] = {}
    for cls in CLASSES:
        cases = [("TG_%s_%s" % (cls, DOMTAG[dom]), "rail",
                  "X1 a b en vdd 0 TG_%s_%s" % (cls, DOMTAG[dom])),
                 ("TGB_%s_%s" % (cls, DOMTAG[dom]), "rail",
                  "X1 a b en 0 vdd vdd 0 TGB_%s_%s" % (cls, DOMTAG[dom])),
                 ("TGB_%s_%s" % (cls, DOMTAG[dom]), "srcbody",
                  "X1 a b en a a vdd 0 TGB_%s_%s" % (cls, DOMTAG[dom]))]
        for (name, body, inst) in cases:
            step = d["vdd"] / (T.NPTS - 1)
            tag = "06r_%s_%s_%s" % (name, body, cls)
            lines = head(dom) + [
                "Ven en 0 %.6g" % d["vdd"],
                "Va a 0 0",
                "Vb b a %g" % T.DV,
                inst,
                ".control", "option temp=27",
                "dc Va 0 %.6g %.8g" % (d["vdd"], step),
                "let ron = %g/abs(i(vb))" % T.DV,
                "wrdata %s.txt ron" % tag, ".endc", ".end", ""]
            log = T.run_deck("\n".join(lines), tag)
            if "No. of Data Rows" not in log:
                print(log[-2500:])
                raise SystemExit("ngspice failed " + tag)
            xs, cols = T.read_wrdata(T.DECK / (tag + ".txt"), 1)
            peak = max(cols[0])
            ref = pvt["summary"][dom][body][cls]["ron_typ_ohm"]
            err = abs(peak - ref) / ref
            key = "%s/%s" % (name, body)
            out["ron"][dom].setdefault(cls, {})[key] = {
                "ron_typ_ohm": peak, "ref_step04_ohm": ref, "rel_err": err}
            flag = "ok " if err <= TOL else "FAIL"
            if err > TOL:
                fails.append("%s %s: %.4g vs %.4g" % (key, dom, peak, ref))
            print("%s %-4s %-18s %-8s Ron_typ %9.4g ohm  (step04 %9.4g, %+.2f %%)"
                  % (flag, dom, name, body, peak, ref, 100 * (peak / ref - 1)))

# ---------------------------------------------------------------- (b) timing
# The switch current during a gate edge is dominated by charge injected through
# the gate overlap capacitance, so it cannot time the channel.  Two separate
# measurements instead:
#   t_pd  -- internal inverter delay en -> enb, the skew between the two pass
#            devices, which is what sets how fast the gate closes.
#   Qinj  -- charge dumped onto a held node when the switch opens: a hold cap on
#            `b`, source on `a`, switch turned off, step in v(b) x C.
CHOLD = 50e-12
print()
for dom in ("1v8", "3v3", "5v0"):
    d = T.DOMAINS[dom]
    out["timing"][dom] = {}
    for cls in CLASSES:
        name = "TG_%s_%s" % (cls, DOMTAG[dom])
        vm = d["vdd"] / 2
        v = d["vdd"]
        lines = head(dom) + [
            "Ven en 0 PULSE(0 %.6g 20n 0.2n 0.2n 40n 100n)" % v,
            "Va a 0 %.6g" % vm,
            "Rb b 0 1e12",
            "X1 a b en vdd 0 " + name,
            ".control", "option temp=27", "tran 0.01n 80n",
            "meas tran tpd_hl trig v(en) val=%.6g rise=1 targ v(x1.enb) val=%.6g fall=1"
            % (vm, vm),
            "meas tran tpd_lh trig v(en) val=%.6g fall=1 targ v(x1.enb) val=%.6g rise=1"
            % (vm, vm),
            ".endc", ".end", ""]
        log = T.run_deck(chr(10).join(lines), "06t_%s" % name)
        vals = {}
        for k in ("tpd_hl", "tpd_lh"):
            m = re.search(k + r"\s*=\s*([-\d.eE+]+)", log)
            vals[k + "_ns"] = float(m.group(1)) * 1e9 if m else None
        # Charge injection on turn-off, swept over the signal level: an NMOS
        # dumps negative charge and a PMOS positive, and the two only cancel
        # near one level, so the worst case has to be searched for.
        qrows = []
        for frac in (0.1, 0.25, 0.5, 0.75, 0.9):
            vlev = v * frac
            lines = head(dom) + [
                "Ven en 0 PULSE(%.6g 0 20n 0.2n 0.2n 40n 200n)" % v,
                "Va a 0 %.6g" % vlev,
                "Chold b 0 %g" % CHOLD,
                "X1 a b en vdd 0 " + name,
                ".control", "option temp=27", "tran 0.005n 58n",
                "meas tran vb_on  FIND v(b) AT=19n",
                "meas tran vb_off FIND v(b) AT=55n",
                ".endc", ".end", ""]
            log = T.run_deck(chr(10).join(lines), "06q_%s_%d" % (name, int(frac * 100)))
            von = voff = None
            m = re.search(r"vb_on\s*=\s*([-\d.eE+]+)", log)
            if m:
                von = float(m.group(1))
            m = re.search(r"vb_off\s*=\s*([-\d.eE+]+)", log)
            if m:
                voff = float(m.group(1))
            if von is not None and voff is not None:
                qrows.append({"level_V": round(vlev, 4),
                              "dv_mV": (voff - von) * 1e3,
                              "qinj_pC": (voff - von) * CHOLD * 1e12})
        worst = max(qrows, key=lambda r: abs(r["qinj_pC"])) if qrows else None
        vals["qinj_pC_worst"] = worst["qinj_pC"] if worst else None
        vals["qinj_worst_level_V"] = worst["level_V"] if worst else None
        vals["qinj_by_level"] = qrows
        vals["chold_pF"] = CHOLD * 1e12
        out["timing"][dom][cls] = vals
        print("%-4s %-16s inverter tpd %6.3f / %6.3f ns (hl/lh)   "
              "Qinj worst %+7.3f pC at %.2f V"
              % (dom, name, vals["tpd_hl_ns"] or float("nan"),
                 vals["tpd_lh_ns"] or float("nan"),
                 vals["qinj_pC_worst"] if vals["qinj_pC_worst"] is not None else float("nan"),
                 vals["qinj_worst_level_V"] or float("nan")))

(T.RESULTS / "06_verify.json").write_text(json.dumps(out, indent=1))
print("\n%d mismatch(es)" % len(fails))
for f in fails:
    print("  " + f)
print("wrote results/06_verify.json")
