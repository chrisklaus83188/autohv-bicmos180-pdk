#!/usr/bin/env python3
"""Re-align a schematic to the 10-grid and re-attach wires to symbol pins.

Why this exists: when symbol pin coordinates move (e.g. an off-grid pin fix),
instances stay put but their pins shift, so wires drawn to the old pin locations
end up a few units away and silently disconnect.

ORTHOGONALITY IS PRESERVED. A wire endpoint is only ever moved along the wire's
own axis; if the pin is off that axis, a short perpendicular jog segment is
added to reach it. Naively snapping an endpoint straight onto the pin would
tilt the wire, which is how an earlier version produced diagonal wires.

Pass 1  snap every instance origin to the 10-grid
Pass 2  snap wire endpoints to the 10-grid, then re-attach to pins orthogonally
Pass 3  connector instances (labels/pins/noconn) snap onto a nearby device pin

Usage: repair_sch_grid.py <file.sch> [--radius N] [--dry-run]
Writes <file>.sch.bak once (if absent). Refuses to write if any diagonal results.
"""
import argparse
import pathlib
import re
import sys

GRID = 10
CONNECTORS = ("lab_pin", "lab_wire", "ipin", "opin", "iopin", "noconn", "gnd", "vdd")
PIN_RE = re.compile(r"^B\s+5\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*\{(.*)\}\s*$")
INST_RE = re.compile(r"^C\s+\{([^}]*)\}\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(\d+)\s+(\d+)\s*(\{.*\})?\s*$")
WIRE_RE = re.compile(r"^N\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s*(\{.*\})?\s*$")


def snap(v):
    return int(round(float(v) / GRID) * GRID)


def xform(x, y, rot, flip):
    """flip about the Y axis first, then rotate rot*90 (measured empirically)."""
    if flip:
        x = -x
    for _ in range(rot % 4):
        x, y = -y, x
    return x, y


def sym_pins(symref, libroot):
    name = symref if symref.endswith(".sym") else symref + ".sym"
    for cand in (libroot / name, libroot.parent / name):
        if cand.exists():
            out = []
            for line in cand.read_text(errors="replace").splitlines():
                m = PIN_RE.match(line.strip())
                if m:
                    x1, y1, x2, y2 = (float(v) for v in m.group(1, 2, 3, 4))
                    out.append(((x1 + x2) / 2, (y1 + y2) / 2))
            return out
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sch")
    ap.add_argument("--radius", type=int, default=25)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    sch = pathlib.Path(a.sch).resolve()
    libroot = sch.parent.parent
    orig = sch.read_text().splitlines()

    # ---- pass 1: instances to grid, collect device pins ----
    stage1, devpins, moved_inst = [], [], 0
    for ln in orig:
        m = INST_RE.match(ln)
        if not m:
            stage1.append(ln)
            continue
        symref, x, y = m.group(1), m.group(2), m.group(3)
        rot, flip, attrs = int(m.group(4)), int(m.group(5)), m.group(6) or "{}"
        nx, ny = snap(x), snap(y)
        if (nx, ny) != (float(x), float(y)):
            moved_inst += 1
        stage1.append(f"C {{{symref}}} {nx} {ny} {rot} {flip} {attrs}")
        if symref.rsplit("/", 1)[-1].replace(".sym", "") not in CONNECTORS:
            for px, py in sym_pins(symref, libroot):
                tx, ty = xform(px, py, rot, flip)
                devpins.append((nx + tx, ny + ty))

    def nearest(px, py):
        best, bd, tie = None, a.radius + 1, False
        for qx, qy in devpins:
            d = abs(qx - px) + abs(qy - py)
            if d < bd:
                best, bd, tie = (qx, qy), d, False
            elif d == bd and (qx, qy) != best:
                tie = True
        return None if (best is None or tie) else best

    # ---- pass 2: wires ----
    final, jogs, moved_wire, dropped = [], [], 0, 0
    for ln in stage1:
        mw = WIRE_RE.match(ln)
        if not mw:
            final.append(ln)
            continue
        x1, y1, x2, y2 = (snap(v) for v in mw.group(1, 2, 3, 4))
        attrs = mw.group(5) or "{}"
        horiz, vert = (y1 == y2), (x1 == x2)

        def attach(px, py):
            """Return the new endpoint, moving only along the wire's axis."""
            nonlocal moved_wire
            p = nearest(px, py)
            if p is None or (int(p[0]), int(p[1])) == (px, py):
                return px, py
            qx, qy = int(p[0]), int(p[1])
            if horiz and not vert:
                if qx != px:
                    moved_wire += 1
                if qy != py:                      # perpendicular jog to the pin
                    jogs.append((qx, py, qx, qy))
                return qx, py
            if vert and not horiz:
                if qy != py:
                    moved_wire += 1
                if qx != px:
                    jogs.append((px, qy, qx, qy))
                return px, qy
            # degenerate (point) wire: safe to move outright
            moved_wire += 1
            return qx, qy

        x1, y1 = attach(x1, y1)
        x2, y2 = attach(x2, y2)
        if (x1, y1) == (x2, y2):
            dropped += 1
            continue
        final.append(f"N {x1} {y1} {x2} {y2} {attrs}")

    # ---- pass 3: connectors onto pins ----
    out, moved_conn = [], 0
    for ln in final:
        mi = INST_RE.match(ln)
        if mi and mi.group(1).rsplit("/", 1)[-1].replace(".sym", "") in CONNECTORS:
            symref, x, y = mi.group(1), int(mi.group(2)), int(mi.group(3))
            rot, flip, attrs = mi.group(4), mi.group(5), mi.group(6) or "{}"
            p = nearest(x, y)
            if p and (int(p[0]), int(p[1])) != (x, y):
                x, y = int(p[0]), int(p[1])
                moved_conn += 1
            out.append(f"C {{{symref}}} {x} {y} {rot} {flip} {attrs}")
        else:
            out.append(ln)

    for jx1, jy1, jx2, jy2 in sorted(set(jogs)):
        if (jx1, jy1) != (jx2, jy2):
            out.append(f"N {jx1} {jy1} {jx2} {jy2} {{}}")

    diag = [l for l in out if (m := WIRE_RE.match(l))
            and m.group(1) != m.group(3) and m.group(2) != m.group(4)]

    print(f"instances snapped to grid : {moved_inst}")
    print(f"wire endpoints re-attached: {moved_wire}")
    print(f"orthogonal jogs added     : {len(set(jogs))}")
    print(f"zero-length wires dropped : {dropped}")
    print(f"connectors re-attached    : {moved_conn}")
    print(f"DIAGONAL wires in result  : {len(diag)}  (must be 0)")
    if diag:
        for d in diag[:5]:
            print("   ", d)
        print("refusing to write")
        return 1
    if a.dry_run:
        print("(dry run - nothing written)")
        return 0
    bak = pathlib.Path(str(sch) + ".bak")
    if not bak.exists():
        bak.write_text("\n".join(orig) + "\n")
        print(f"backup written: {bak.name}")
    sch.write_text("\n".join(out) + "\n")
    print(f"rewrote {sch.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
