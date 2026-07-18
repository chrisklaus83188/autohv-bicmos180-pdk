#!/bin/bash
# Generate Xschem symbols for the AutoHV async-logic cells (cells.lib).
# Writes into <this-dir>/logic/. Power is connected BY TEXT: supply/ground are
# net names (VPWR/VGND, default vdd/0) injected by the symbol format and shown
# as text -- no power pins, no power wires.
#
# GRID RULE (hard): every pin connection point (center of its B rectangle) is an
# exact multiple of 10, and pin boxes are 6x6 with integer edges (center +/-3) so
# no fractional coordinate appears in a pin definition. Same-side pin pitch is a
# multiple of 20. Body geometry is sized to meet the pins, never the reverse.
set -e
SD="$(cd "$(dirname "$0")" && pwd -P)"
LIB="$SD/logic"
mkdir -p "$LIB"
VER='v {xschem version=3.4.8RC file_version=1.3}'

# ---- pins: in/out at (-40,0)/(40,0); a/b at (-40,-10)/(-40,10), pitch 20 ----
pins_1in() { cat <<'EOF'
B 5 -43 -3 -37 3 {name=in dir=in}
B 5 37 -3 43 3 {name=out dir=out}
EOF
}
pins_2in() { cat <<'EOF'
B 5 -43 -13 -37 -7 {name=a dir=in}
B 5 -43 7 -37 13 {name=b dir=in}
B 5 37 -3 43 3 {name=out dir=out}
EOF
}

# ---- glyph fragments (ANSI shapes), leads run out to the on-grid pins ----
glyph_inv() { cat <<'EOF'
L 4 -40 0 -20 0 {}
L 4 -20 -20 -20 20 {}
L 4 -20 -20 15 0 {}
L 4 -20 20 15 0 {}
A 4 20 0 5 0 360 {}
L 4 25 0 40 0 {}
EOF
}
glyph_buf() { cat <<'EOF'
L 4 -40 0 -20 0 {}
L 4 -20 -20 -20 20 {}
L 4 -20 -20 20 0 {}
L 4 -20 20 20 0 {}
L 4 20 0 40 0 {}
EOF
}
glyph_and() { cat <<'EOF'
L 4 -40 -10 -20 -10 {}
L 4 -40 10 -20 10 {}
P 4 10 -20 20 -20 -20 5 -20 13 -17 18 -10 20 0 18 10 13 17 5 20 -20 20 {}
L 4 20 0 40 0 {}
EOF
}
glyph_nand() { cat <<'EOF'
L 4 -40 -10 -20 -10 {}
L 4 -40 10 -20 10 {}
P 4 10 -20 20 -20 -20 5 -20 13 -17 18 -10 20 0 18 10 13 17 5 20 -20 20 {}
A 4 25 0 5 0 360 {}
L 4 30 0 40 0 {}
EOF
}
glyph_or() { cat <<'EOF'
L 4 -40 -10 -16 -10 {}
L 4 -40 10 -16 10 {}
P 4 14 -20 -20 -9 -18 3 -14 14 -8 22 -3 25 0 22 3 14 8 3 14 -9 18 -20 20 -13 10 -11 0 -13 -10 {}
L 4 25 0 40 0 {}
EOF
}
glyph_nor() { cat <<'EOF'
L 4 -40 -10 -16 -10 {}
L 4 -40 10 -16 10 {}
P 4 14 -20 -20 -9 -18 3 -14 14 -8 22 -3 25 0 22 3 14 8 3 14 -9 18 -20 20 -13 10 -11 0 -13 -10 {}
A 4 30 0 5 0 360 {}
L 4 35 0 40 0 {}
EOF
}
glyph_xor() { cat <<'EOF'
L 4 -40 -10 -19 -10 {}
L 4 -40 10 -19 10 {}
P 4 14 -17 -20 -6 -18 6 -14 17 -8 25 -3 28 0 25 3 17 8 6 14 -6 18 -17 20 -10 10 -8 0 -10 -10 {}
P 4 5 -25 -20 -18 -10 -16 0 -18 10 -25 20 {}
L 4 28 0 40 0 {}
EOF
}
glyph_xnor() { cat <<'EOF'
L 4 -40 -10 -19 -10 {}
L 4 -40 10 -19 10 {}
P 4 14 -17 -20 -6 -18 6 -14 17 -8 25 -3 28 0 25 3 17 8 6 14 -6 18 -17 20 -10 10 -8 0 -10 -10 {}
P 4 5 -25 -20 -18 -10 -16 0 -18 10 -25 20 {}
A 4 33 0 5 0 360 {}
L 4 38 0 40 0 {}
EOF
}

# emit_gate  TYPE(inv/buf/and/nand/or/nor/xor/xnor)  NIN(1/2)  CELLNAME
emit_gate() {
  local gtype="$1" nin="$2" f="$LIB/$3.sym"
  {
    echo "$VER"; echo 'G {}'
    echo 'K {type=logicgate'
    echo 'format="@spiceprefix@name @pinlist @VPWR @VGND @symname"'
    echo 'template="name=U1 VPWR=vdd VGND=0 spiceprefix=x"'
    echo '}'
    echo 'V {}'; echo 'S {}'; echo 'F {}'; echo 'E {}'
    glyph_$gtype
    if [ "$nin" = 1 ]; then pins_1in; else pins_2in; fi
    echo 'T {@spiceprefix@name} -12 -34 0 0 0.18 0.18 {}'
    echo 'T {@symname} -24 28 0 0 0.16 0.16 {layer=8}'
    echo 'T {@VPWR} 22 -26 0 0 0.18 0.18 {layer=4}'
    echo 'T {@VGND} 22 16 0 0 0.18 0.18 {layer=4}'
  } > "$f"
  echo "wrote $3.sym"
}

for D in 1V8 3V3 5V0; do
  emit_gate inv  1 "INV_$D"
  emit_gate buf  1 "BUF_$D"
  emit_gate nand 2 "NAND2_$D"
  emit_gate nor  2 "NOR2_$D"
  emit_gate and  2 "AND2_$D"
  emit_gate or   2 "OR2_$D"
  emit_gate xor  2 "XOR2_$D"
  emit_gate xnor 2 "XNOR2_$D"
done
echo "----"
echo "Total logic symbols: $(ls "$LIB"/*.sym | wc -l)"
