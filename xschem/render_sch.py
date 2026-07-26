#!/usr/bin/env python3
"""Tiny headless renderer: xschem .sch -> SVG (no X / no xschem GUI needed).

Draws component symbol geometry (autohv/*.sym), wires (N), raw lines (L),
text (T), and net-name pins (lab_pin/ipin/opin/iopin -> the net label). Enough
to eyeball a cell schematic. Placement transform matches xschem (flip about Y,
then rot*90 as (x,y)->(-y,x)), per gen_cmp_sch_drawn.xform.
"""
import re
import sys
import pathlib

HERE = pathlib.Path(__file__).resolve().parent           # <repo>/xschem
CVAL = re.compile(r'^C \{([^}]*)\} (\S+) (\S+) (\S+) (\S+) \{(.*)\}\s*$')


def xform(x, y, rot, flip):
    x, y = float(x), float(y)
    if flip:
        x = -x
    for _ in range(rot % 4):
        x, y = -y, x
    return x, y


def prop(props, key, default=""):
    m = re.search(rf'\b{key}=([^\s]+)', props)
    return m.group(1) if m else default


def load_syms(path, ox, oy, rot, flip, props, out):
    """Emit drawable primitives for a symbol instance, transformed to sheet."""
    def place(px, py):
        tx, ty = xform(px, py, rot, flip)
        return ox + tx, oy + ty
    name = prop(props, "name")
    if name and not name.upper().startswith("X"):
        name = "X" + name            # show the netlist name (spiceprefix=X)
    model = prop(props, "model") or symname(path)
    for ln in path.read_text(errors="replace").splitlines():
        t = ln.split()
        if not t:
            continue
        if t[0] == "L":                      # L layer x1 y1 x2 y2 {}
            x1, y1 = place(t[2], t[3]); x2, y2 = place(t[4], t[5])
            out["lines"].append((x1, y1, x2, y2, t[1]))
        elif t[0] == "P":                    # P layer npts x1 y1 ... {}
            n = int(t[2]); pts = [place(t[3 + 2*i], t[4 + 2*i]) for i in range(n)]
            out["polys"].append((pts, t[1]))
        elif t[0] == "B":                    # pin box
            x1, y1 = place(t[2], t[3]); x2, y2 = place(t[4], t[5])
            out["pins"].append((x1, y1, x2, y2))
    # instance annotation
    lx, ly = place(26, -28)
    lbl = name if not model else f"{name} {model}"
    w = prop(props, "W"); l = prop(props, "L")
    if w or l:
        lbl += f" {w}/{l}".rstrip("/")
    out["texts"].append((lx, ly, lbl, 3.2, "#333"))


def symname(path):
    return path.stem


def render(schfile):
    sch = pathlib.Path(schfile)
    out = dict(lines=[], polys=[], pins=[], wires=[], texts=[], nets=[])
    for ln in sch.read_text(errors="replace").splitlines():
        m = CVAL.match(ln)
        if m:
            sym, x, y, rot, flip, props = m.groups()
            x, y, rot, flip = float(x), float(y), int(rot), int(flip)
            base = sym.split("/")[-1]
            if base in ("lab_pin.sym", "ipin.sym", "opin.sym", "iopin.sym"):
                net = prop(props, "lab")
                kind = base.split(".")[0]
                col = {"ipin": "#0a0", "opin": "#a00"}.get(kind, "#0077aa")
                out["nets"].append((x, y, net, col, kind))
            else:
                p = HERE / sym            # autohv/NMOS18.sym -> <xschem>/autohv/..
                if p.exists():
                    load_syms(p, x, y, rot, flip, props, out)
            continue
        t = ln.split()
        if not t:
            continue
        if t[0] == "N":                   # wire
            out["wires"].append((float(t[1]), float(t[2]), float(t[3]), float(t[4])))
        elif t[0] == "L":
            out["lines"].append((float(t[2]), float(t[3]), float(t[4]), float(t[5]), t[1]))
        elif t[0] == "T":                 # T {text} x y rot flip sx sy {}
            mm = re.match(r'^T \{(.*?)\} (\S+) (\S+) (\S+) (\S+) (\S+) (\S+)', ln)
            if mm:
                txt = mm.group(1)
                out["texts"].append((float(mm.group(2)), float(mm.group(3)),
                                     txt, float(mm.group(6)) * 14, "#555"))

    # bounds
    xs, ys = [], []
    for a in out["lines"] + [(*w, 0) for w in out["wires"]]:
        xs += [a[0], a[2]]; ys += [a[1], a[3]]
    for pts, _ in out["polys"]:
        xs += [p[0] for p in pts]; ys += [p[1] for p in pts]
    for n in out["nets"]:
        xs.append(n[0]); ys.append(n[1])
    minx, maxx, miny, maxy = min(xs)-60, max(xs)+120, min(ys)-40, max(ys)+60
    W, H = maxx - minx, maxy - miny
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{minx} {miny} {W} {H}" '
         f'font-family="monospace">',
         f'<rect x="{minx}" y="{miny}" width="{W}" height="{H}" fill="white"/>']
    for x1, y1, x2, y2 in out["wires"]:
        s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#0077aa" stroke-width="2"/>')
    for x1, y1, x2, y2, layer in out["lines"]:
        s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#111" stroke-width="2"/>')
    for pts, layer in out["polys"]:
        d = " ".join(f"{p[0]},{p[1]}" for p in pts)
        s.append(f'<polyline points="{d}" fill="none" stroke="#111" stroke-width="2"/>')
    for x1, y1, x2, y2 in out["pins"]:
        s.append(f'<rect x="{min(x1,x2)}" y="{min(y1,y2)}" width="{abs(x2-x1)}" '
                 f'height="{abs(y2-y1)}" fill="#c33"/>')
    for x, y, net, col, kind in out["nets"]:
        s.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{col}"/>')
        s.append(f'<text x="{x+6}" y="{y-4}" font-size="15" fill="{col}" '
                 f'font-weight="bold">{net}</text>')
    for x, y, txt, sz, col in out["texts"]:
        txt = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        s.append(f'<text x="{x}" y="{y}" font-size="{sz:.0f}" fill="{col}">{txt}</text>')
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    sch = sys.argv[1]
    outp = sys.argv[2] if len(sys.argv) > 2 else sch.replace(".sch", ".svg")
    pathlib.Path(outp).write_text(render(sch), encoding="utf-8")
    print(f"wrote {outp}")
