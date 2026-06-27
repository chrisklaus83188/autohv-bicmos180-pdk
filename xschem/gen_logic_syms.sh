#!/bin/bash
# Generate Xschem symbols for the AutoHV async-logic cells (cells.lib).
# Writes into <this-dir>/logic/. Power is connected BY TEXT: supply/ground are
# net names (VPWR/VGND, default vdd/0) injected by the symbol format and shown
# as text -- no power pins, no power wires.
set -e
SD="$(cd "$(dirname "$0")" && pwd -P)"
LIB="$SD/logic"
mkdir -p "$LIB"
VER='v {xschem version=3.4.8RC file_version=1.3}'

pins_1in() { cat <<'EOF'
B 5 -37.5 -2.5 -32.5 2.5 {name=in dir=in}
B 5 32.5 -2.5 37.5 2.5 {name=out dir=out}
EOF
}
pins_2in() { cat <<'EOF'
B 5 -37.5 -12.5 -32.5 -7.5 {name=a dir=in}
B 5 -37.5 7.5 -32.5 12.5 {name=b dir=in}
B 5 32.5 -2.5 37.5 2.5 {name=out dir=out}
EOF
}
glyph_inv() { cat <<'EOF'
L 4 -35 0 -18 0 {}
L 4 -18 -14 -18 14 {}
L 4 -18 -14 12 0 {}
L 4 -18 14 12 0 {}
A 4 15 0 3 0 360 {}
L 4 18 0 35 0 {}
EOF
}
glyph_buf() { cat <<'EOF'
L 4 -35 0 -18 0 {}
L 4 -18 -14 -18 14 {}
L 4 -18 -14 15 0 {}
L 4 -18 14 15 0 {}
L 4 15 0 35 0 {}
EOF
}
glyph_and() { cat <<'EOF'
L 4 -35 -10 -18 -10 {}
L 4 -35 10 -18 10 {}
P 4 10 -18 14 -18 -14 2 -14 9 -12 14 -7 16 0 14 7 9 12 2 14 -18 14 {}
L 4 16 0 35 0 {}
EOF
}
glyph_nand() { cat <<'EOF'
L 4 -35 -10 -18 -10 {}
L 4 -35 10 -18 10 {}
P 4 10 -18 14 -18 -14 2 -14 9 -12 14 -7 16 0 14 7 9 12 2 14 -18 14 {}
A 4 19 0 3 0 360 {}
L 4 22 0 35 0 {}
EOF
}
glyph_or() { cat <<'EOF'
L 4 -35 -10 -14 -10 {}
L 4 -35 10 -14 10 {}
P 4 15 -18 -14 -8 -13 3 -10 12 -6 19 -2 22 0 19 2 12 6 3 10 -8 13 -18 14 -12 7 -10 0 -12 -7 -18 -14 {}
L 4 22 0 35 0 {}
EOF
}
glyph_nor() { cat <<'EOF'
L 4 -35 -10 -14 -10 {}
L 4 -35 10 -14 10 {}
P 4 15 -18 -14 -8 -13 3 -10 12 -6 19 -2 22 0 19 2 12 6 3 10 -8 13 -18 14 -12 7 -10 0 -12 -7 -18 -14 {}
A 4 25 0 3 0 360 {}
L 4 28 0 35 0 {}
EOF
}
glyph_xor() { cat <<'EOF'
L 4 -35 -10 -17 -10 {}
L 4 -35 10 -17 10 {}
P 4 15 -16 -14 -6 -13 5 -10 14 -6 21 -2 24 0 21 2 14 6 5 10 -6 13 -16 14 -10 7 -8 0 -10 -7 -16 -14 {}
P 4 5 -22 -14 -16 -7 -14 0 -16 7 -22 14 {}
L 4 24 0 35 0 {}
EOF
}
glyph_xnor() { cat <<'EOF'
L 4 -35 -10 -17 -10 {}
L 4 -35 10 -17 10 {}
P 4 15 -16 -14 -6 -13 5 -10 14 -6 21 -2 24 0 21 2 14 6 5 10 -6 13 -16 14 -10 7 -8 0 -10 -7 -16 -14 {}
P 4 5 -22 -14 -16 -7 -14 0 -16 7 -22 14 {}
A 4 27 0 3 0 360 {}
L 4 30 0 35 0 {}
EOF
}

# emit_gate  TYPE  NIN(1/2)  CELLNAME
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
    echo 'T {@spiceprefix@name} -10 -30 0 0 0.18 0.18 {}'
    echo 'T {@symname} -20 22 0 0 0.16 0.16 {layer=8}'
    echo 'T {@VPWR} 18 -22 0 0 0.18 0.18 {layer=4}'
    echo 'T {@VGND} 18 12 0 0 0.18 0.18 {layer=4}'
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
