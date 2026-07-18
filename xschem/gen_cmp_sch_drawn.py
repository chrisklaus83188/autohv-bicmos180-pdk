#!/usr/bin/env python3
"""Draw the comparator schematics as real circuits (routed, not label-soup).

There are only THREE topologies -- NIN, PIN, RR -- the 1V8/3V3/5V0 variants
differ solely in model suffix and device sizing, so each topology is placed by
hand once and instantiated three times with sizes read from
circuits/comparators/comparators_all.lib (still the netlist authority).

Routing rules (see xschem crossing test): a wire merely PASSING OVER another
connects to nothing; only a shared endpoint (T-junction) connects. So every
intended junction must fall on a segment END -- that is what vline()/hline()
'taps' do. Crossings are therefore free and are used deliberately.

Layout: vdd rail on top, vss on the bottom, three device rows between, signal
flowing left to right.
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
LIB = HERE.parent / "circuits" / "comparators" / "comparators_all.lib"
OUT = HERE / "comparators"

# ---- row geometry -------------------------------------------------------
VDD_Y, VSS_Y = 0, 1040
PROW, DROW, NROW = 200, 560, 880      # PMOS-on-vdd / diff pair / NMOS-on-vss
NOFF = {"d": (20, -40), "g": (-40, 0), "s": (20, 40), "b": (20, 0)}
POFF = {"d": (20, 40), "g": (-40, 0), "s": (20, -40), "b": (20, 0)}

SUB = re.compile(r"^\.subckt\s+(\S+)\s+(.*?)(?:\s+params:\s*(.*))?$", re.I)
DEVRE = re.compile(r"^(X\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*(.*)$")


def parse(path):
    cells, cur = {}, None
    for raw in path.read_text(errors="replace").splitlines():
        s = raw.split(";", 1)[0].strip()
        m = SUB.match(s)
        if m:
            cur = m.group(1)
            cells[cur] = {"ports": m.group(2).split(), "devs": {}}
            continue
        if s.lower().startswith(".ends"):
            cur = None
            continue
        if cur:
            m = DEVRE.match(s)
            if m:
                cells[cur]["devs"][m.group(1)] = {
                    "d": m.group(2), "g": m.group(3), "s": m.group(4),
                    "b": m.group(5), "model": m.group(6),
                    "params": m.group(7).strip()}
    return cells


def esc(t):
    return t.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


class Sheet:
    def __init__(self, title, note):
        self.L = ["v {xschem version=3.4.8RC file_version=1.3}", "G {}", "K {}",
                  "V {}", "S {}", "E {}"]
        self.n = 0
        self.text(title, -1150, VDD_Y - 260, 0.6)
        self.text(note, -1150, VDD_Y - 200, 0.3)

    def text(self, t, x, y, sz=0.3):
        self.L.append(f"T {{{esc(t)}}} {x} {y} 0 0 {sz} {sz} {{}}")

    def wire(self, x1, y1, x2, y2):
        if (x1, y1) != (x2, y2):
            assert x1 == x2 or y1 == y2, f"diagonal {(x1,y1,x2,y2)}"
            self.L.append(f"N {x1} {y1} {x2} {y2} {{}}")

    def vline(self, x, y1, y2, taps=()):
        """Vertical run split at every tap so junctions land on segment ends."""
        pts = sorted({y1, y2} | {t for t in taps if min(y1, y2) < t < max(y1, y2)})
        for a, b in zip(pts, pts[1:]):
            self.wire(x, a, x, b)

    def hline(self, y, x1, x2, taps=()):
        pts = sorted({x1, x2} | {t for t in taps if min(x1, x2) < t < max(x1, x2)})
        for a, b in zip(pts, pts[1:]):
            self.wire(a, y, b, y)

    def label(self, x, y, net):
        self.n += 1
        self.L.append(f"C {{lab_pin.sym}} {x} {y} 0 0 {{name=lz{self.n} lab={net}}}")

    def port(self, x, y, net, kind="ipin", rot=0):
        self.n += 1
        self.L.append(f"C {{{kind}.sym}} {x} {y} {rot} 0 {{name=pz{self.n} lab={net}}}")

    def dev(self, dv, inst, x, y):
        """Place one MOS; return its pin coordinates. Adds the body-source tie."""
        is_n = dv["model"].upper().startswith("N")
        off = NOFF if is_n else POFF
        rot, flip = (0, 0) if is_n else (2, 1)
        at = f"name={inst} model={dv['model']}"
        if dv["params"]:
            at += " " + esc(dv["params"])
        # NOTE: symbol refs resolve against XSCHEM_LIBRARY_PATH (~/xschem_lib),
        # NOT against this file's directory -- "../autohv/..." does not resolve.
        self.L.append(f'C {{autohv/{dv["model"]}.sym}} {x} {y} {rot} {flip} {{{at}}}')
        self.text(inst, x - 55, y - 105, 0.28)
        P = {k: (x + o[0], y + o[1]) for k, o in off.items()}
        # rule 6: body-source stub where they share a net, else a label
        if dv["b"] == dv["s"]:
            self.wire(*P["b"], *P["s"])
        else:
            self.label(*P["b"], dv["b"])
        return P

    def write(self, path):
        path.write_text("\n".join(self.L) + "\n")


def draw_nin(cell, name):
    """Two-stage: NMOS pair + PMOS mirror load -> PMOS CS stage -> inverter."""
    D = cell["devs"]
    bias = cell["ports"][5]
    S = Sheet(name, "body: circuits/comparators/comparators_all.lib (authority) | "
                    "vdd/vss rails drawn; ibg/o2/ENB/ENbuf are long-haul labels")

    # column plan.  Xser sits directly ABOVE Xmb so the bias branch reads as a
    # vertical stack; Xsho2 sits next to the o2 node it clamps.
    XE1, XE2, XSH = -900, -600, -300
    XMB, XL, XT, XR, XS2, XSHO2, XO = 300, 660, 810, 960, 1260, 1400, 1560
    XSER = XMB

    # ---- core devices -------------------------------------------------
    mb = S.dev(D["Xmb"], "mb", XMB, NROW)
    tail = S.dev(D["Xtail"], "tail", XT, NROW)
    m1 = S.dev(D["Xm1"], "m1", XL, DROW)
    m2 = S.dev(D["Xm2"], "m2", XR, DROW)
    m3 = S.dev(D["Xm3"], "m3", XL, PROW)
    m4 = S.dev(D["Xm4"], "m4", XR, PROW)
    m5 = S.dev(D["Xm5"], "m5", XS2, PROW)
    m6 = S.dev(D["Xm6"], "m6", XS2, NROW)
    m7 = S.dev(D["Xm7"], "m7", XO, PROW)
    m8 = S.dev(D["Xm8"], "m8", XO, NROW)
    e1p = S.dev(D["Xei1p"], "ei1p", XE1, PROW)
    e1n = S.dev(D["Xei1n"], "ei1n", XE1, NROW)
    e2p = S.dev(D["Xei2p"], "ei2p", XE2, PROW)
    e2n = S.dev(D["Xei2n"], "ei2n", XE2, NROW)
    sh = S.dev(D["Xsh"], "sh", XSH, NROW)
    sho2 = S.dev(D["Xsho2"], "sho2", XSHO2, PROW)
    ser = S.dev(D["Xser"], "ser", XSER, DROW)      # stacked above mb

    # ---- rails ---------------------------------------------------------
    ptop = [m3, m4, m5, m7, e1p, e2p, sho2]
    nbot = [mb, tail, m6, m8, e1n, e2n, sh]
    S.hline(VDD_Y, -1000, 1700, taps=[p["s"][0] for p in ptop])
    S.hline(VSS_Y, -1000, 1700, taps=[p["s"][0] for p in nbot])
    for p in ptop:
        S.wire(p["s"][0], p["s"][1], p["s"][0], VDD_Y)
    for p in nbot:
        S.wire(p["s"][0], p["s"][1], p["s"][0], VSS_Y)
    S.label(-1000, VDD_Y, "vdd")
    S.label(-1000, VSS_Y, "vss")

    # ---- ibg bias bus (crosses the tail drop harmlessly) ---------------
    BUS = 780
    taps = [sh["d"][0], mb["g"][0], mb["d"][0], tail["g"][0], m6["g"][0]]
    S.hline(BUS, sh["d"][0], m6["g"][0], taps=taps)
    for p, term in ((sh, "d"), (mb, "g"), (tail, "g"), (m6, "g")):
        S.wire(p[term][0], p[term][1], p[term][0], BUS)
    # ser source -> mb drain: one vertical through the bus, so the whole bias
    # branch (ser.s, mb.d, mb.g, tail.g, m6.g, sh.d) is a single visible stack
    S.vline(mb["d"][0], ser["s"][1], mb["d"][1], taps=[BUS])
    # ser drain carries the ibp_5uA pin up to its port
    S.vline(ser["d"][0], ser["d"][1], 420)
    S.hline(420, 150, ser["d"][0])
    S.port(150, 420, bias)
    # A wire-only net gets an auto name, so a lab_pin named "ibg" elsewhere would
    # form a SEPARATE net. Naming the wired net here is what merges the two.
    S.label(mb["d"][0], BUS, "ibg")

    # ---- differential pair: sources -> tie bar -> tail ------------------
    TIE = 700
    S.wire(*m1["s"], m1["s"][0], TIE)
    S.wire(*m2["s"], m2["s"][0], TIE)
    S.hline(TIE, m1["s"][0], m2["s"][0], taps=[tail["d"][0]])
    S.wire(tail["d"][0], TIE, *tail["d"])
    S.label(tail["d"][0], TIE, "tail")       # else it netlists as an auto name

    # ---- n1: mirror diode + both mirror gates ---------------------------
    MG = 320
    S.vline(m3["d"][0], m3["d"][1], m1["d"][1], taps=[MG])
    S.hline(MG, m3["g"][0], m4["g"][0], taps=[m3["d"][0]])
    S.wire(m3["g"][0], MG, *m3["g"])
    S.wire(m4["g"][0], MG, *m4["g"])
    S.label(m3["d"][0], MG, "n1")            # name the wired net (see ibg note)

    # ---- n2 -> stage-2 gate ---------------------------------------------
    N2 = 440
    S.vline(m4["d"][0], m4["d"][1], m2["d"][1], taps=[N2])
    S.hline(N2, m4["d"][0], m5["g"][0])
    S.wire(m5["g"][0], N2, *m5["g"])
    S.label(m4["d"][0], N2, "n2")            # name the wired net (see ibg note)

    # ---- o2 -> output inverter gates -------------------------------------
    O2, SPINE = 620, m7["g"][0] - 20
    S.vline(m5["d"][0], m5["d"][1], m6["d"][1], taps=[O2])
    S.hline(O2, m5["d"][0], SPINE, taps=[sho2["d"][0]])   # tap for the sho2 drop
    S.vline(SPINE, m7["g"][1], m8["g"][1], taps=[O2])
    S.wire(SPINE, m7["g"][1], *m7["g"])
    S.wire(SPINE, m8["g"][1], *m8["g"])
    S.label(m5["d"][0], O2, "o2")            # name the wired net (see ibg note)
    # sho2 clamps o2: wire its drain down to the o2 run rather than labelling it
    S.vline(sho2["d"][0], sho2["d"][1], O2)

    # ---- out -------------------------------------------------------------
    OY = 540
    S.vline(m7["d"][0], m7["d"][1], m8["d"][1], taps=[OY])
    S.hline(OY, m7["d"][0], 1760)
    S.port(1760, OY, "out", "opin")

    # ---- inputs ----------------------------------------------------------
    # Own lanes, ABOVE the pair row. They must not share the DROW lane, which
    # the EN/ENB routing uses -- doing so shorted inp/inn to EN/ENB. They cross
    # the enable spines, which is harmless: crossings do not connect.
    # inp goes straight into m1's gate. inn cannot share that lane (it would run
    # through m1's body), so it drops in one lane above, just left of m2.
    S.hline(m1["g"][1], 440, m1["g"][0])
    S.port(440, m1["g"][1], "inp")
    gx, gy = m2["g"]
    S.hline(460, 440, gx - 60)
    S.vline(gx - 60, 460, gy)
    S.hline(gy, gx - 60, gx)
    S.port(440, 460, "inn")

    # ---- EN inverter chain ------------------------------------------------
    ENS = e1p["g"][0] - 20
    S.vline(ENS, e1p["g"][1], e1n["g"][1], taps=[DROW])
    S.wire(ENS, e1p["g"][1], *e1p["g"])
    S.wire(ENS, e1n["g"][1], *e1n["g"])
    S.hline(DROW, -1200, ENS)
    S.port(-1200, DROW, "EN")

    ENB = e2p["g"][0] - 20
    S.vline(e1p["d"][0], e1p["d"][1], e1n["d"][1], taps=[DROW])
    S.hline(DROW, e1p["d"][0], ENB)
    S.vline(ENB, e2p["g"][1], e2n["g"][1], taps=[DROW])
    S.wire(ENB, e2p["g"][1], *e2p["g"])
    S.wire(ENB, e2n["g"][1], *e2n["g"])
    S.label(e1p["d"][0], DROW, "ENB")        # name the wired net (see ibg note)
    S.label(*sh["g"], "ENB")

    S.vline(e2p["d"][0], e2p["d"][1], e2n["d"][1], taps=[DROW + 60])
    S.label(e2p["d"][0], DROW + 60, "ENbuf")
    S.label(*ser["g"], "ENbuf")
    S.label(*sho2["g"], "ENbuf")

    S.text("* enable / bias shutdown", XE1 - 60, VDD_Y - 120, 0.4)
    S.text("* bias", XMB - 60, VDD_Y - 120, 0.4)
    S.text("* input pair + mirror load", XL - 60, VDD_Y - 120, 0.4)
    S.text("* gain stage", XS2 - 60, VDD_Y - 120, 0.4)
    S.text("* output", XO - 60, VDD_Y - 120, 0.4)

    # ---- optional hysteresis (.if HYSK>0) -- labels only, off to the side --
    hy = [k for k in ("Xhtail", "Xmha", "Xmhb") if k in D]
    if hy:
        HX, HY = XE1, VSS_Y + 420
        S.text("* optional hysteresis - instantiated ONLY when HYSK>0 "
               "(default HYSK=0: these devices do not exist)", HX - 60, HY - 200, 0.4)
        for i, k in enumerate(hy):
            dv = D[k]
            x = HX + i * 300
            P = S.dev(dv, k[1:], x, HY)
            for t in ("d", "g", "s"):
                S.label(*P[t], dv[t])
    return S


def main():
    cells = parse(LIB)
    made = 0
    for name in ("CMP_NIN_5V0", "CMP_NIN_3V3", "CMP_NIN_1V8"):
        if name not in cells:
            print(f"  skip {name} (not in lib)")
            continue
        draw_nin(cells[name], name).write(OUT / f"{name}.sch")
        print(f"  drew {name}.sch")
        made += 1
    print(f"{made} schematic(s) written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
