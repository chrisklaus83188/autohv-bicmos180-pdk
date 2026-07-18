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
INVROW = VSS_Y + 200                  # EN-buffer cells, below the vss rail
RAIL_L, RAIL_R = 150, 1700
NOTE_X = 620                          # title/notes anchor, mid-sheet
# raw pin offsets in the .sym; placement transforms are applied to these
RAW = {"d": (20, -40), "g": (-40, 0), "s": (20, 40), "b": (20, 0)}


def xform(x, y, rot, flip):
    """flip about the Y axis first, then rotate rot*90 (measured empirically)."""
    if flip:
        x = -x
    for _ in range(rot % 4):
        x, y = -y, x
    return x, y

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
        # Notes sit over the middle of the sheet, not off to the left, so the
        # drawing's overall extent stays roughly square.
        self.text(title, NOTE_X, VDD_Y - 280, 0.6)
        self.text(note, NOTE_X, VDD_Y - 220, 0.3)

    def text(self, t, x, y, sz=0.3):
        self._grid(x, y)
        self.L.append(f"T {{{esc(t)}}} {x} {y} 0 0 {sz} {sz} {{}}")

    @staticmethod
    def _grid(*vals):
        """Every emitted coordinate must be on the 10-grid, by construction.

        A device placed at a 5 (e.g. the exact midpoint between two columns)
        puts its PINS on 5-unit coordinates, which cannot be wired at the
        default snap. Fail loudly rather than emit an unwirable schematic.
        """
        for v in vals:
            assert int(v) % 10 == 0, f"off-grid coordinate {v}"

    def wire(self, x1, y1, x2, y2):
        if (x1, y1) != (x2, y2):
            assert x1 == x2 or y1 == y2, f"diagonal {(x1,y1,x2,y2)}"
            self._grid(x1, y1, x2, y2)
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
        self._grid(x, y)
        self.n += 1
        self.L.append(f"C {{lab_pin.sym}} {x} {y} 0 0 {{name=lz{self.n} lab={net}}}")

    def port(self, x, y, net, kind="ipin", rot=0):
        self._grid(x, y)
        self.n += 1
        self.L.append(f"C {{{kind}.sym}} {x} {y} {rot} 0 {{name=pz{self.n} lab={net}}}")

    def dev(self, dv, inst, x, y, mirror=False, vflip=False):
        """Place one MOS; return its pin coordinates. Adds the body-source tie.

        mirror flips about the vertical axis: gate to the right, drain/source
        column at x-20 instead of x+20.
        vflip flips about the horizontal axis, swapping which of drain/source
        points up. Needed when the terminal that must face a bus is the one the
        default orientation points away from -- routing to the far terminal
        would otherwise run straight through the device's own body.
        """
        self._grid(x, y)
        is_n = dv["model"].upper().startswith("N")
        rot, flip = (0, 0) if (is_n != vflip) else (2, 1)
        if mirror:
            flip = 1 - flip
        off = {k: xform(*v, rot, flip) for k, v in RAW.items()}
        at = f"name={inst} model={dv['model']}"
        if dv["params"]:
            at += " " + esc(dv["params"])
        # NOTE: symbol refs resolve against XSCHEM_LIBRARY_PATH (~/xschem_lib),
        # NOT against this file's directory -- "../autohv/..." does not resolve.
        self.L.append(f'C {{autohv/{dv["model"]}.sym}} {x} {y} {rot} {flip} {{{at}}}')
        self.text(inst, x - 60, y - 110, 0.28)   # keep annotations on-grid too
        P = {k: (x + o[0], y + o[1]) for k, o in off.items()}
        # rule 6: body-source stub where they share a net, else a label
        if dv["b"] == dv["s"]:
            self.wire(*P["b"], *P["s"])
        else:
            self.label(*P["b"], dv["b"])
        return P

    def cell(self, dv, inst, x, y):
        """Place a logic-library cell (INV_*): in/out pins, supplies by TEXT.

        The symbol's template defaults to VGND=0, but the comparators ground on
        'vss', so both rails are set explicitly from the library call's nodes
        (.subckt INV_xxx in out vdd gnd -> d g s b as parsed).
        """
        at = f"name={inst} VPWR={dv['s']} VGND={dv['b']}"
        self.L.append(f'C {{logic/{dv["model"]}.sym}} {x} {y} 0 0 {{{at}}}')
        self.text(f"{inst}  {dv['model']}", x - 40, y - 70, 0.28)
        return {"in": (x - 40, y), "out": (x + 40, y)}

    def write(self, path):
        path.write_text("\n".join(self.L) + "\n")


def draw_nin(cell, name):
    """Two-stage: NMOS pair + PMOS mirror load -> PMOS CS stage -> inverter."""
    D = cell["devs"]
    bias = cell["ports"][5]
    S = Sheet(name, "body: circuits/comparators/comparators_all.lib (authority) | "
                    "vdd/vss rails drawn; ibg/o2/ENB/ENbuf are long-haul labels")

    # Column plan.  Xser sits directly ABOVE Xmb so the bias branch reads as a
    # vertical stack, and Xsh sits just right of Xmb.  Xmb is MIRRORED so its
    # gate faces right toward the ibg bus; that moves its drain column to x-20,
    # so it is placed 40 to the right of Xser to keep the stack aligned.
    XSER, XL, XT, XR, XS2, XSHO2, XO = 300, 660, 810, 960, 1260, 1400, 1560
    XMB = XSER + 40
    XM3 = XL + 40                     # mirrored: +40 keeps its drain over m1's
    XSH = 520
    XE1, XE2 = 400, 700               # EN-buffer cells, below the vss rail

    # ---- core devices -------------------------------------------------
    mb = S.dev(D["Xmb"], "mb", XMB, NROW, mirror=True)
    tail = S.dev(D["Xtail"], "tail", XT, NROW)
    m1 = S.dev(D["Xm1"], "m1", XL, DROW)
    m2 = S.dev(D["Xm2"], "m2", XR, DROW)
    m3 = S.dev(D["Xm3"], "m3", XM3, PROW, mirror=True)
    m4 = S.dev(D["Xm4"], "m4", XR, PROW)
    m5 = S.dev(D["Xm5"], "m5", XS2, PROW)
    m6 = S.dev(D["Xm6"], "m6", XS2, NROW)
    m7 = S.dev(D["Xm7"], "m7", XO, PROW)
    m8 = S.dev(D["Xm8"], "m8", XO, NROW)
    # EN buffer is two PDK logic cells, not discrete devices
    ei1 = S.cell(D["Xei1"], "ei1", XE1, INVROW)
    ei2 = S.cell(D["Xei2"], "ei2", XE2, INVROW)
    sh = S.dev(D["Xsh"], "sh", XSH, NROW)
    sho2 = S.dev(D["Xsho2"], "sho2", XSHO2, PROW)
    ser = S.dev(D["Xser"], "ser", XSER, DROW)      # stacked above mb

    # ---- rails ---------------------------------------------------------
    # the INV cells take their supplies by text, so they are not on the rails
    ptop = [m3, m4, m5, m7, sho2]
    nbot = [mb, tail, m6, m8, sh]
    S.hline(VDD_Y, RAIL_L, RAIL_R, taps=[p["s"][0] for p in ptop])
    S.hline(VSS_Y, RAIL_L, RAIL_R, taps=[p["s"][0] for p in nbot])
    for p in ptop:
        S.wire(p["s"][0], p["s"][1], p["s"][0], VDD_Y)
    for p in nbot:
        S.wire(p["s"][0], p["s"][1], p["s"][0], VSS_Y)
    S.label(RAIL_L, VDD_Y, "vdd")
    S.label(RAIL_L, VSS_Y, "vss")

    # ---- ibg bias bus (crosses the tail drop harmlessly) ---------------
    BUS = 780
    taps = [mb["d"][0], mb["g"][0], sh["d"][0], tail["g"][0], m6["g"][0]]
    S.hline(BUS, mb["d"][0], m6["g"][0], taps=taps)
    for p, term in ((mb, "g"), (sh, "d"), (tail, "g"), (m6, "g")):
        S.wire(p[term][0], p[term][1], p[term][0], BUS)
    # ser source -> mb drain: one vertical through the bus, so the whole bias
    # branch (ser.s, mb.d, mb.g, tail.g, m6.g, sh.d) is a single visible stack
    S.vline(mb["d"][0], ser["s"][1], mb["d"][1], taps=[BUS])
    # ser drain carries the ibp_5uA pin up to its port
    S.vline(ser["d"][0], ser["d"][1], 420)
    S.hline(420, RAIL_L, ser["d"][0])
    S.port(RAIL_L, 420, bias)
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
    # span from whichever is leftmost -- m3's gate sits RIGHT of its drain when
    # mirrored, so the run must still reach back to the n1 column to tap it
    S.hline(MG, min(m3["d"][0], m3["g"][0]), m4["g"][0],
            taps=[m3["d"][0], m3["g"][0]])
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

    # ---- EN buffer: two PDK INV cells in a row ----------------------------
    enb_net = D["Xei1"]["g"]                 # .subckt INV in out vdd gnd
    buf_net = D["Xei2"]["g"]
    S.hline(INVROW, RAIL_L, ei1["in"][0])
    S.port(RAIL_L, INVROW, D["Xei1"]["d"])   # EN
    S.hline(INVROW, ei1["out"][0], ei2["in"][0])
    S.label(ei1["out"][0], INVROW, enb_net)  # name the wired net (see ibg note)
    S.label(*sh["g"], enb_net)
    S.hline(INVROW, ei2["out"][0], ei2["out"][0] + 80)
    S.label(ei2["out"][0] + 80, INVROW, buf_net)
    S.label(*ser["g"], buf_net)
    S.label(*sho2["g"], buf_net)

    S.text("* EN buffer (PDK INV cells)", XE1 - 60, INVROW - 120, 0.4)
    S.text("* bias + shutdown switches", XSER - 60, VDD_Y - 120, 0.4)
    S.text("* input pair + mirror load", XL - 60, VDD_Y - 120, 0.4)
    S.text("* gain stage", XS2 - 60, VDD_Y - 120, 0.4)
    S.text("* output", XO - 60, VDD_Y - 120, 0.4)

    # ---- optional hysteresis (.if HYSK>0) -- labels only, off to the side --
    hy = [k for k in ("Xhtail", "Xmha", "Xmhb") if k in D]
    if hy:
        HX, HY = XSER, INVROW + 400
        S.text("* optional hysteresis - instantiated ONLY when HYSK>0 "
               "(default HYSK=0: these devices do not exist)", HX - 60, HY - 200, 0.4)
        for i, k in enumerate(hy):
            dv = D[k]
            x = HX + i * 300
            P = S.dev(dv, k[1:], x, HY)
            for t in ("d", "g", "s"):
                S.label(*P[t], dv[t])
    return S


def draw_pin(cell, name):
    """Two-stage, complement of NIN: PMOS pair + NMOS mirror load.

    Same three-row frame, but the roles of the rails swap -- bias/tail/stage-2
    source sit on vdd at the TOP row, the mirror load on vss at the BOTTOM.
    The output inverter (m7 PMOS / m8 NMOS) is identical in both topologies.
    """
    D = cell["devs"]
    bias = cell["ports"][5]                      # ibn_5uA
    S = Sheet(name, "body: circuits/comparators/comparators_all.lib (authority) | "
                    "PMOS input pair, NMOS mirror load")

    TOPROW, PAIRROW, BOTROW = PROW, DROW, NROW
    XSER, XMB, XSH = 300, 460, 600
    XL, XT, XR = 760, 910, 1060
    XS2, XSHO2, XO = 1360, 1500, 1660
    XM3 = XL + 40                                # mirrored: keeps drain over m1
    RAIL_R2 = 1800
    XE1, XE2 = 400, 700

    # Xser must present its ibg terminal DOWNWARD to the bias bus and its pin
    # terminal upward. Which of d/s carries ibg is read from the library rather
    # than assumed, and the device is flipped to suit.
    ibg_net = D["Xmb"]["d"]
    ser_bus = "s" if D["Xser"]["s"] == ibg_net else "d"
    ser_pin = "d" if ser_bus == "s" else "s"
    ser = S.dev(D["Xser"], "ser", XSER, TOPROW, vflip=(ser_bus == "s"))
    mb = S.dev(D["Xmb"], "mb", XMB, TOPROW, mirror=True)
    sh = S.dev(D["Xsh"], "sh", XSH, TOPROW)
    tail = S.dev(D["Xtail"], "tail", XT, TOPROW)
    m1 = S.dev(D["Xm1"], "m1", XL, PAIRROW)
    m2 = S.dev(D["Xm2"], "m2", XR, PAIRROW)
    m3 = S.dev(D["Xm3"], "m3", XM3, BOTROW, mirror=True)
    m4 = S.dev(D["Xm4"], "m4", XR, BOTROW)
    m5 = S.dev(D["Xm5"], "m5", XS2, BOTROW)
    m6 = S.dev(D["Xm6"], "m6", XS2, TOPROW)
    m7 = S.dev(D["Xm7"], "m7", XO, TOPROW)
    m8 = S.dev(D["Xm8"], "m8", XO, BOTROW)
    sho2 = S.dev(D["Xsho2"], "sho2", XSHO2, BOTROW)
    ei1 = S.cell(D["Xei1"], "ei1", XE1, INVROW)
    ei2 = S.cell(D["Xei2"], "ei2", XE2, INVROW)

    # ---- rails ----
    ptop = [mb, tail, m6, m7, sh]                # sources on vdd
    nbot = [m3, m4, m5, m8, sho2]                # sources on vss
    S.hline(VDD_Y, RAIL_L, RAIL_R2, taps=[p["s"][0] for p in ptop])
    S.hline(VSS_Y, RAIL_L, RAIL_R2, taps=[p["s"][0] for p in nbot])
    for p in ptop:
        S.wire(p["s"][0], p["s"][1], p["s"][0], VDD_Y)
    for p in nbot:
        S.wire(p["s"][0], p["s"][1], p["s"][0], VSS_Y)
    S.label(RAIL_L, VDD_Y, "vdd")
    S.label(RAIL_L, VSS_Y, "vss")

    # ---- ibg bus, just under the top row ----
    BUS = 300
    pins = [mb["d"], mb["g"], tail["g"], m6["g"], sh["d"], ser[ser_bus]]
    xs = [p[0] for p in pins]
    S.hline(BUS, min(xs), max(xs), taps=xs)
    for px, py in pins:
        S.wire(px, py, px, BUS)
    S.label(mb["d"][0], BUS, D["Xmb"]["d"])      # ibg

    # ---- bias pin up to its port (ser is leftmost, so nothing to cross) ----
    S.vline(ser[ser_pin][0], ser[ser_pin][1], 100)
    S.hline(100, RAIL_L, ser[ser_pin][0])
    S.port(RAIL_L, 100, bias)

    # ---- pair sources -> tie bar -> tail drain ----
    TIE = 440
    S.wire(*m1["s"], m1["s"][0], TIE)
    S.wire(*m2["s"], m2["s"][0], TIE)
    S.hline(TIE, m1["s"][0], m2["s"][0], taps=[tail["d"][0]])
    S.wire(tail["d"][0], TIE, *tail["d"])
    S.label(tail["d"][0], TIE, D["Xtail"]["d"])  # tail

    # ---- n1: pair drain down to the mirror diode, plus both mirror gates ----
    MG = 720
    S.vline(m1["d"][0], m1["d"][1], m3["d"][1], taps=[MG])
    S.hline(MG, min(m3["d"][0], m3["g"][0]), m4["g"][0],
            taps=[m3["d"][0], m3["g"][0]])
    S.wire(m3["g"][0], MG, *m3["g"])
    S.wire(m4["g"][0], MG, *m4["g"])
    S.label(m3["d"][0], MG, D["Xm3"]["d"])       # n1

    # ---- n2 -> stage-2 gate ----
    N2 = 680
    S.vline(m4["d"][0], m2["d"][1], m4["d"][1], taps=[N2])
    S.hline(N2, m4["d"][0], m5["g"][0])
    S.wire(m5["g"][0], N2, *m5["g"])
    S.label(m4["d"][0], N2, D["Xm4"]["d"])       # n2

    # ---- o2 -> output inverter gates ----
    O2, SPINE = 560, m7["g"][0] - 20
    S.vline(m6["d"][0], m6["d"][1], m5["d"][1], taps=[O2])
    S.hline(O2, m6["d"][0], SPINE, taps=[sho2["d"][0]])
    S.vline(SPINE, m7["g"][1], m8["g"][1], taps=[O2])
    S.wire(SPINE, m7["g"][1], *m7["g"])
    S.wire(SPINE, m8["g"][1], *m8["g"])
    S.vline(sho2["d"][0], sho2["d"][1], O2)
    S.label(m6["d"][0], O2, D["Xm6"]["d"])       # o2

    # ---- out ----
    OY = 540
    S.vline(m7["d"][0], m7["d"][1], m8["d"][1], taps=[OY])
    S.hline(OY, m7["d"][0], RAIL_R2 + 60)
    S.port(RAIL_R2 + 60, OY, D["Xm7"]["d"], "opin")

    # ---- inputs ----
    S.hline(m1["g"][1], 500, m1["g"][0])
    S.port(500, m1["g"][1], D["Xm1"]["g"])
    gx, gy = m2["g"]
    S.hline(460, 500, gx - 60)
    S.vline(gx - 60, 460, gy)
    S.hline(gy, gx - 60, gx)
    S.port(500, 460, D["Xm2"]["g"])

    # ---- EN buffer, below the vss rail ----
    S.hline(INVROW, RAIL_L, ei1["in"][0])
    S.port(RAIL_L, INVROW, D["Xei1"]["d"])
    S.hline(INVROW, ei1["out"][0], ei2["in"][0])
    S.label(ei1["out"][0], INVROW, D["Xei1"]["g"])
    S.hline(INVROW, ei2["out"][0], ei2["out"][0] + 80)
    S.label(ei2["out"][0] + 80, INVROW, D["Xei2"]["g"])
    # which switch takes ENB vs ENbuf is read from the library, not assumed
    for d, inst in ((sh, "Xsh"), (ser, "Xser"), (sho2, "Xsho2")):
        S.label(*d["g"], D[inst]["g"])

    S.text("* EN buffer (PDK INV cells)", XE1 - 60, INVROW - 120, 0.4)
    S.text("* bias + shutdown switches", XSER - 60, VDD_Y - 120, 0.4)
    S.text("* input pair + mirror load", XL - 60, VDD_Y - 120, 0.4)
    S.text("* gain stage", XS2 - 60, VDD_Y - 120, 0.4)
    S.text("* output", XO - 60, VDD_Y - 120, 0.4)

    hy = [k for k in ("Xhtail", "Xmha", "Xmhb") if k in D]
    if hy:
        HX, HY = XSER, INVROW + 400
        S.text("* optional hysteresis - instantiated ONLY when HYSK>0 "
               "(default HYSK=0: these devices do not exist)", HX - 60, HY - 200, 0.4)
        for i, k in enumerate(hy):
            dv = D[k]
            P = S.dev(dv, k[1:], HX + i * 300, HY)
            for t in ("d", "g", "s"):
                S.label(*P[t], dv[t])
    return S


def draw_rr(cell, name):
    """Rail-to-rail folded cascode: complementary input pairs summed in a fold.

    Five device rows instead of three.  Reading down a fold column: f1 sources
    from vdd into node x, cascode cp1 passes x down to a, and mirror mm1 sinks a
    to vss -- so x and a are two separate verticals in the SAME column,
    separated by cp1's body.  The input pairs sit to the left and reach the fold
    through their own lanes; the PMOS pair's drain must route BELOW the pair row
    to reach node a, since a straight run would collide with p2's drain pin.
    """
    D = cell["devs"]
    bias = cell["ports"][5]
    S = Sheet(name, "body: circuits/comparators/comparators_all.lib (authority) | "
                    "rail-to-rail input, folded cascode")

    TOP, CASC, PP, NP, BOT = 200, 460, 700, 940, 1200
    VSSR = 1360
    IROW = VSSR + 200
    XSER = XRBN = 250
    XMIR, XRBP, XVC, XISK, XSHN, XSHP, XMTP = 400, 550, 700, 850, 1000, 1150, 1300
    XP1 = XN1 = 1450
    XP2 = XN2 = 1600
    # NOT the exact midpoint of the pair columns (1525) -- that is off the
    # 10-grid and would put this device's PINS on 5-unit coordinates, which
    # cannot be wired at the default snap.
    XMTN = 1520
    XA, XB, XS2, XSHO2, XO = 1750, 1900, 2100, 2250, 2400
    RR = 2560
    # routing lanes, all distinct where their x-spans could overlap
    PMD, VCP, SP, XL_, YL_, AL, BL, SN, IBG, MG, BS2, O2L, OUTL, INPL, INNL = (
        300, 560, 580, 340, 380, 800, 860, 1060, 1100, 1100, 1020, 620, 640, 820, 620)

    ibg_net = D["Xrbn"]["d"]
    ser_bus = "s" if D["Xser"]["s"] == ibg_net else "d"
    ser_pin = "d" if ser_bus == "s" else "s"

    rbn = S.dev(D["Xrbn"], "rbn", XRBN, BOT)
    ser = S.dev(D["Xser"], "ser", XSER, PP, vflip=(ser_bus == "d"))
    mir = S.dev(D["Xmir"], "mir", XMIR, BOT)
    rbp = S.dev(D["Xrbp"], "rbp", XRBP, TOP)
    vc1 = S.dev(D["Xvc1"], "vc1", XVC, TOP)
    vc2 = S.dev(D["Xvc2"], "vc2", XVC, CASC)
    isk = S.dev(D["Xisk"], "isk", XISK, BOT)
    shn = S.dev(D["Xshn"], "shn", XSHN, BOT)
    shp = S.dev(D["Xshp"], "shp", XSHP, TOP)
    mtp = S.dev(D["Xmtp"], "mtp", XMTP, TOP)
    p1 = S.dev(D["Xp1"], "p1", XP1, PP)
    p2 = S.dev(D["Xp2"], "p2", XP2, PP)
    n1 = S.dev(D["Xn1"], "n1", XN1, NP)
    n2 = S.dev(D["Xn2"], "n2", XN2, NP)
    mtn = S.dev(D["Xmtn"], "mtn", XMTN, BOT)
    f1 = S.dev(D["Xf1"], "f1", XA, TOP)
    cp1 = S.dev(D["Xcp1"], "cp1", XA, CASC)
    mm1 = S.dev(D["Xmm1"], "mm1", XA, BOT)
    f2 = S.dev(D["Xf2"], "f2", XB, TOP)
    cp2 = S.dev(D["Xcp2"], "cp2", XB, CASC)
    mm2 = S.dev(D["Xmm2"], "mm2", XB, BOT)
    s2p = S.dev(D["Xs2p"], "s2p", XS2, TOP)
    s2n = S.dev(D["Xs2n"], "s2n", XS2, BOT)
    sho2 = S.dev(D["Xsho2"], "sho2", XSHO2, BOT)
    bp = S.dev(D["Xbp"], "bp", XO, TOP)
    bn = S.dev(D["Xbn"], "bn", XO, BOT)
    ei1 = S.cell(D["Xei1"], "ei1", 400, IROW)
    ei2 = S.cell(D["Xei2"], "ei2", 700, IROW)

    # ---- rails ----
    ptop = [rbp, vc1, shp, mtp, f1, f2, s2p, bp]
    nbot = [rbn, mir, isk, shn, mtn, mm1, mm2, s2n, sho2, bn]
    S.hline(VDD_Y, RAIL_L, RR, taps=[p["s"][0] for p in ptop])
    S.hline(VSSR, RAIL_L, RR, taps=[p["s"][0] for p in nbot])
    for p in ptop:
        S.wire(p["s"][0], p["s"][1], p["s"][0], VDD_Y)
    for p in nbot:
        S.wire(p["s"][0], p["s"][1], p["s"][0], VSSR)
    S.label(RAIL_L, VDD_Y, "vdd")
    S.label(RAIL_L, VSSR, "vss")

    def bus(lane, pins, label=None):
        xs = [p[0] for p in pins]
        S.hline(lane, min(xs), max(xs), taps=xs)
        for px, py in pins:
            S.wire(px, py, px, lane)
        if label:
            S.label(min(xs), lane, label)

    # ---- ibg_n (NMOS mirror gate) and pmd (PMOS mirror gate) buses ----
    bus(IBG, [rbn["d"], rbn["g"], mir["g"], isk["g"], mtn["g"], shn["d"],
              ser[ser_bus]], ibg_net)
    # mir's drain must be a BUS MEMBER, not a separate riser -- its column sits
    # left of the other pmd pins, so the bus has to extend to reach it
    bus(PMD, [mir["d"], rbp["d"], rbp["g"], mtp["g"], f1["g"], f2["g"],
              s2p["g"], shp["d"]], D["Xrbp"]["d"])

    # ---- bias pin ----
    S.vline(ser[ser_pin][0], ser[ser_pin][1], 660)
    S.hline(660, RAIL_L, ser[ser_pin][0])
    S.port(RAIL_L, 660, bias)

    # ---- cascode bias: vc1 diode -> k -> vc2 -> vcp ----
    KG = 320
    S.vline(vc1["d"][0], vc1["d"][1], vc2["s"][1], taps=[KG])
    S.vline(vc1["g"][0], vc1["g"][1], KG)        # vc1 is DIODE-connected
    S.hline(KG, vc1["g"][0], vc1["d"][0])
    S.label(vc1["d"][0], KG, D["Xvc1"]["d"])                        # k
    bus(VCP, [vc2["d"], vc2["g"], cp1["g"], cp2["g"], isk["d"]], D["Xvc2"]["d"])

    # ---- input pair tails ----
    S.vline(mtp["d"][0], mtp["d"][1], SP)
    S.hline(SP, mtp["d"][0], p2["s"][0], taps=[p1["s"][0]])
    S.wire(p1["s"][0], SP, *p1["s"])
    S.wire(p2["s"][0], SP, *p2["s"])
    S.label(mtp["d"][0], SP, D["Xmtp"]["d"])                        # sp
    S.hline(SN, n1["s"][0], n2["s"][0], taps=[mtn["d"][0]])
    S.wire(*n1["s"], n1["s"][0], SN)
    S.wire(*n2["s"], n2["s"][0], SN)
    S.wire(mtn["d"][0], SN, *mtn["d"])
    S.label(mtn["d"][0], SN, D["Xmtn"]["d"])                        # sn

    # ---- fold nodes x,y: NMOS pair drain out to the right, then up ----
    # Doglegs must sit in the gap BETWEEN the pair columns, and the two hops off
    # the drains must not overlap -- at 1700/1850 the x and y runs shared the
    # y=900 lane between 1620 and 1700, shorting the two fold nodes together,
    # and the x run also cut straight through n2's body.
    for nd, fd, cd, lane, dogleg, net in (
            (n1, f1, cp1, XL_, 1500, D["Xn1"]["d"]),
            (n2, f2, cp2, YL_, 1660, D["Xn2"]["d"])):
        S.vline(fd["d"][0], fd["d"][1], cd["s"][1], taps=[lane])
        S.hline(nd["d"][1], nd["d"][0], dogleg)
        S.vline(dogleg, nd["d"][1], lane)
        S.hline(lane, dogleg, fd["d"][0])
        S.label(fd["d"][0], lane, net)

    # ---- summing nodes a,b: PMOS pair drain drops BELOW the pair row first ----
    for pd, cd, md, lane, net in ((p1, cp1, mm1, AL, D["Xp1"]["d"]),
                                  (p2, cp2, mm2, BL, D["Xp2"]["d"])):
        S.vline(cd["d"][0], cd["d"][1], md["d"][1], taps=[lane])
        S.vline(pd["d"][0], pd["d"][1], lane)
        S.hline(lane, pd["d"][0], cd["d"][0])
        S.label(cd["d"][0], lane, net)
    # mirror gates (both take node a)
    S.hline(MG, mm1["g"][0], mm2["g"][0], taps=[mm1["d"][0]])
    S.wire(*mm1["g"], mm1["g"][0], MG)
    S.wire(*mm2["g"], mm2["g"][0], MG)
    S.vline(mm1["d"][0], MG, mm1["d"][1])

    # ---- stage 2 ----
    S.vline(mm2["d"][0], BS2, mm2["d"][1])
    S.hline(BS2, mm2["d"][0], s2n["g"][0])
    S.wire(s2n["g"][0], BS2, *s2n["g"])

    # ---- o2 -> output inverter ----
    SPINE = bp["g"][0] - 20
    S.vline(s2p["d"][0], s2p["d"][1], s2n["d"][1], taps=[O2L])
    S.hline(O2L, s2p["d"][0], SPINE, taps=[sho2["d"][0]])
    S.vline(SPINE, bp["g"][1], bn["g"][1], taps=[O2L])
    S.wire(SPINE, bp["g"][1], *bp["g"])
    S.wire(SPINE, bn["g"][1], *bn["g"])
    S.vline(sho2["d"][0], sho2["d"][1], O2L)
    S.label(s2p["d"][0], O2L, D["Xs2p"]["d"])                       # o2

    # ---- out ----
    S.vline(bp["d"][0], bp["d"][1], bn["d"][1], taps=[OUTL])
    S.hline(OUTL, bp["d"][0], RR + 60)
    S.port(RR + 60, OUTL, D["Xbp"]["d"], "opin")

    # ---- inputs: each drives BOTH pairs, so one vertical per input ----
    S.vline(p1["g"][0], p1["g"][1], n1["g"][1], taps=[INPL])
    S.hline(INPL, RAIL_L, p1["g"][0])
    S.port(RAIL_L, INPL, D["Xp1"]["g"])
    # tap at p2's gate so the pin lands on a segment END rather than mid-wire
    S.vline(p2["g"][0], INNL, n2["g"][1], taps=[p2["g"][1]])
    S.hline(INNL, RAIL_L, p2["g"][0])
    S.port(RAIL_L, INNL, D["Xp2"]["g"])

    # ---- EN buffer ----
    S.hline(IROW, RAIL_L, ei1["in"][0])
    S.port(RAIL_L, IROW, D["Xei1"]["d"])
    S.hline(IROW, ei1["out"][0], ei2["in"][0])
    S.label(ei1["out"][0], IROW, D["Xei1"]["g"])
    S.hline(IROW, ei2["out"][0], ei2["out"][0] + 80)
    S.label(ei2["out"][0] + 80, IROW, D["Xei2"]["g"])
    for d, inst in ((shn, "Xshn"), (shp, "Xshp"), (sho2, "Xsho2"), (ser, "Xser")):
        S.label(*d["g"], D[inst]["g"])

    S.text("* bias generation", XRBN - 60, VDD_Y - 120, 0.4)
    S.text("* rail-to-rail input pairs", XMTP - 60, VDD_Y - 120, 0.4)
    S.text("* fold + cascode + mirror", XA - 60, VDD_Y - 120, 0.4)
    S.text("* gain stage", XS2 - 60, VDD_Y - 120, 0.4)
    S.text("* output", XO - 60, VDD_Y - 120, 0.4)
    S.text("* EN buffer (PDK INV cells)", 340, IROW - 120, 0.4)
    return S


def main():
    cells = parse(LIB)
    made = 0
    for name in ("CMP_RR_5V0", "CMP_RR_3V3", "CMP_RR_1V8"):
        if name in cells:
            draw_rr(cells[name], name).write(OUT / f"{name}.sch")
            print(f"  drew {name}.sch")
            made += 1
    for name in ("CMP_PIN_5V0", "CMP_PIN_3V3", "CMP_PIN_1V8"):
        if name in cells:
            draw_pin(cells[name], name).write(OUT / f"{name}.sch")
            print(f"  drew {name}.sch")
            made += 1
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
