#!/bin/bash
# Generate Xschem symbols for the AutoHV transmission-gate cells in
# circuits/transmission_gates/cells.lib
# (18 cells: {TG,TGB}_{1K,100R,10R}_{1V8,3V3,5V0}).
# Classic transmission-gate glyph: a bow-tie body between switch terminals a
# (left) and b (right); en drives the upper gate bar, and the lower gate bar
# carries an inversion bubble because the complement is made inside the cell.
# TGB adds the body pins bn / bp below.  Power BY TEXT (VPWR=vdd, VGND=0).
#   TG   ports: a b en vdd gnd
#   TGB  ports: a b en bn bp vdd gnd
set -e
SD="$(cd "$(dirname "$0")" && pwd -P)"
LIB="$SD/transmission_gates"; mkdir -p "$LIB"
VER='v {xschem version=3.4.8RC file_version=1.3}'

# emit  NAME  PREFIX  "NOMINAL @ SUPPLY"   (PREFIX = TG or TGB)
emit() {
  local name="$1" pre="$2" note="$3" f="$LIB/$1.sym"
  {
    echo "$VER"; echo 'G {}'
    echo 'K {type=switch'
    echo 'format="@spiceprefix@name @pinlist @VPWR @VGND @symname"'
    echo 'template="name=U1 VPWR=vdd VGND=0 spiceprefix=x"'
    echo '}'
    echo 'V {}'; echo 'S {}'; echo 'F {}'; echo 'E {}'
    # switch leads
    echo 'L 4 -70 0 -40 0 {}'
    echo 'L 4 40 0 70 0 {}'
    # bow-tie body
    echo 'P 4 4 -40 -20 -40 20 0 0 -40 -20 {}'
    echo 'P 4 4 40 -20 40 20 0 0 40 -20 {}'
    # NMOS gate bar, driven from en
    echo 'L 4 -26 -30 26 -30 {}'
    echo 'L 4 0 -30 0 -50 {}'
    # PMOS gate bar with the inversion bubble (the inverter is inside the cell)
    echo 'L 4 -26 30 26 30 {}'
    echo 'A 4 0 36 6 0 360 {}'
    # pins -- order here is the netlist pinlist order
    echo 'B 5 -73 -3 -67 3 {name=a dir=inout}'
    echo 'B 5 67 -3 73 3 {name=b dir=inout}'
    echo 'B 5 -3 -53 3 -47 {name=en dir=in}'
    if [ "$pre" = TGB ]; then
      echo 'L 4 -40 20 -40 50 {}'
      echo 'L 4 40 20 40 50 {}'
      echo 'B 5 -43 47 -37 53 {name=bn dir=in}'
      echo 'B 5 37 47 43 53 {name=bp dir=in}'
      echo 'T {bn} -62 38 0 0 0.14 0.14 {layer=4}'
      echo 'T {bp} 46 38 0 0 0.14 0.14 {layer=4}'
    fi
    echo 'T {a} -66 -14 0 0 0.14 0.14 {layer=8}'
    echo 'T {b} 56 -14 0 0 0.14 0.14 {layer=8}'
    echo 'T {en} 6 -48 0 0 0.14 0.14 {layer=7}'
    echo 'T {inv} 10 30 0 0 0.12 0.12 {layer=7}'
    echo 'T {@VPWR} -18 -68 0 0 0.16 0.16 {layer=4}'
    echo 'T {@VGND} -18 56 0 0 0.16 0.16 {layer=4}'
    echo "T {$note} -40 -82 0 0 0.15 0.15 {layer=8}"
    echo 'T {@symname} -40 -98 0 0 0.18 0.18 {layer=8}'
    echo 'T {@spiceprefix@name} 24 -82 0 0 0.15 0.15 {}'
  } > "$f"
  echo "wrote $name.sym"
}

for dv in "1V8:1.8" "3V3:3.3" "5V0:5"; do
  d="${dv%%:*}"; v="${dv##*:}"
  for cn in "1K:1 kohm" "100R:100 ohm" "10R:10 ohm"; do
    c="${cn%%:*}"; nom="${cn#*:}"
    emit "TG_${c}_$d"  TG  "$nom @ ${v}V"
    emit "TGB_${c}_$d" TGB "$nom @ ${v}V"
  done
done
echo "----"
echo "Total transmission-gate symbols: $(ls "$LIB"/*.sym | wc -l)"
