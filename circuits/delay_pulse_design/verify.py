"""End-to-end check of cells.lib: instantiate each SUBCKT (not the inline
netlist) and confirm the 20 ns metric + correct asymmetric/passthrough
behaviour at the nominal corner. Cross-checks against results.json."""
import json
import dp_lib as D

DOMV = {"1v8": 1.8, "3v3": 3.3, "5v0": 5.0}
DOMTAG = {"1v8": "1V8", "3v3": "3V3", "5v0": "5V0"}
LIBINC = '.include "../cells.lib"\n'


def deck(arch, dkey):
    v = DOMV[dkey]; h = v / 2
    name = f"{arch}_{DOMTAG[dkey]}"
    d = (f'.title verify {name}\n.include "{D.LIB}"\n' + LIBINC + ".param case=0\n"
         f"Vd v 0 {v}\nVi i 0 PULSE(0 {v} 20n 0.02n 0.02n 80n 400n)\n"
         f"X1 i o v 0 {name}\nCL o 0 5f\n"
         ".control\noption temp=27\ntran 0.02n 220n\n")
    if arch == "DLYR":
        d += (f"meas tran tmd trig v(i) val={h} rise=1 targ v(o) val={h} rise=1\n"
              f"meas tran tmp trig v(i) val={h} fall=1 targ v(o) val={h} fall=1\n"
              "meas tran lo find v(o) at=10n\nmeas tran hi find v(o) at=90n\n")
    elif arch == "DLYF":
        d += (f"meas tran tmd trig v(i) val={h} fall=1 targ v(o) val={h} fall=1\n"
              f"meas tran tmp trig v(i) val={h} rise=1 targ v(o) val={h} rise=1\n"
              "meas tran lo find v(o) at=10n\nmeas tran hi find v(o) at=90n\n")
    elif arch == "PHI":
        d += (f"meas tran tmd trig v(o) val={h} rise=1 td=19n targ v(o) val={h} fall=1 td=19n\n"
              "meas tran tmp find v(o) at=190n\n"        # rest after falling edge: ~0
              "meas tran lo find v(o) at=10n\nmeas tran hi find v(o) at=30n\n")  # idle / mid-pulse
    else:  # PLO
        d += (f"meas tran tmd trig v(o) val={h} fall=1 td=99n targ v(o) val={h} rise=1 td=99n\n"
              "meas tran tmp find v(o) at=80n\n"         # rest after rising edge: ~v
              "meas tran hi find v(o) at=10n\nmeas tran lo find v(o) at=110n\n")
    d += 'echo "RES tmd=$&tmd tmp=$&tmp lo=$&lo hi=$&hi"\n.endc\n.end\n'
    return d


def main():
    with open(D.WORK / "results.json") as f:
        res = json.load(f)
    print(f"{'cell':10s} {'metric':>9s} {'json':>9s} {'pass/rest':>11s} "
          f"{'lo(V)':>7s} {'hi(V)':>7s}  verdict")
    allok = True
    for dkey in ("1v8", "3v3", "5v0"):
        for arch in D.ARCHES:
            rows = D.parse_res(D.run(deck(arch, dkey), f"verify_{arch}_{dkey}"))
            r = rows[0] if rows else {}
            tmd = r.get("tmd"); tmp = r.get("tmp")
            lo = r.get("lo"); hi = r.get("hi")
            jm = res[dkey][arch]["metric_ns"]
            v = DOMV[dkey]
            ok = isinstance(tmd, float) and abs(tmd * 1e9 - jm) < 1.0
            # behavioural checks
            if arch in ("DLYR", "DLYF"):
                # passthrough edge fast (<25% of timed edge); idle rails clean
                ok &= isinstance(tmp, float) and tmp < 0.30 * tmd
                ok &= (lo < 0.1 * v) and (hi > 0.9 * v)
                passtxt = f"{tmp*1e9:.2f}ns" if isinstance(tmp, float) else "n/a"
            elif arch == "PHI":
                ok &= isinstance(tmp, float) and abs(tmp) < 0.1 * v   # rests low
                ok &= (lo < 0.1 * v) and (hi > 0.9 * v)               # idle low, pulse high
                passtxt = f"rest{tmp*1e3:.0f}mV"
            else:  # PLO
                ok &= isinstance(tmp, float) and tmp > 0.9 * v        # rests high
                ok &= (hi > 0.9 * v) and (lo < 0.1 * v)               # idle high, pulse low
                passtxt = f"rest{tmp:.2f}V"
            allok &= ok
            md = f"{tmd*1e9:.2f}ns" if isinstance(tmd, float) else "FAIL"
            print(f"{arch}_{DOMTAG[dkey]:6s} {md:>9s} {jm:8.2f}n {passtxt:>11s} "
                  f"{lo:7.3f} {hi:7.3f}  {'OK' if ok else 'XXX'}")
    print("\nALL CELLS OK" if allok else "\n*** SOME CELLS FAILED ***")


if __name__ == "__main__":
    main()
