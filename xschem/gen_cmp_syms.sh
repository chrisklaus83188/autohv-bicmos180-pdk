#!/bin/bash
# Generate Xschem symbols for the AutoHV comparator cells in
# circuits/comparators/comparators_all.lib (9 single-output cells:
# CMP_{NIN,PIN,RR}_{1V8,3V3,5V0}).  Ports for ALL: inp inn out vdd vss nb.
# Power connected BY TEXT (VPWR=vdd, VGND=0) -- no power pins/wires.
set -e
SD="$(cd "$(dirname "$0")" && pwd -P)"
LIB="$SD/comparators"; mkdir -p "$LIB"
VER='v {xschem version=3.4.8RC file_version=1.3}'

# emit  NAME  "PARAMS_FORMAT"  "PARAMS_TEMPLATE"  TYPETAG  BIASPIN(ibp_5uA/ibn_5uA)
emit() {
  local name="$1" pf="$2" pt="$3" tag="$4" bias="$5" f="$LIB/$1.sym"
  local biaslbl="${bias%_5uA}"
  {
    echo "$VER"; echo 'G {}'
    echo 'K {type=comparator'
    echo "format=\"@spiceprefix@name @@inp @@inn @@out @VPWR @VGND @@$bias @@EN @symname $pf\""
    echo "template=\"name=U1 VPWR=vdd VGND=0 spiceprefix=x $pt\""
    echo '}'
    echo 'V {}'; echo 'S {}'; echo 'F {}'; echo 'E {}'
    # box (-30..30 square) + inner comparator triangle
    echo 'L 4 -30 -30 30 -30 {}'
    echo 'L 4 30 -30 30 30 {}'
    echo 'L 4 30 30 -30 30 {}'
    echo 'L 4 -30 30 -30 -30 {}'
    echo 'L 4 -12 -12 -12 12 {}'
    echo 'L 4 -12 -12 10 0 {}'
    echo 'L 4 -12 12 10 0 {}'
    # inputs (+ top, - bottom), single output; bias + EN on the bottom
    echo 'L 4 -50 -20 -30 -20 {}'
    echo 'L 4 -50 20 -30 20 {}'
    echo 'L 4 30 0 50 0 {}'
    echo 'L 4 -20 30 -20 50 {}'
    echo 'L 4 20 30 20 50 {}'
    # pins: centers on the 10-grid, 6x6 boxes with integer edges
    echo 'B 5 -53 -23 -47 -17 {name=inp dir=in}'
    echo 'B 5 -53 17 -47 23 {name=inn dir=in}'
    echo 'B 5 47 -3 53 3 {name=out dir=out}'
    echo "B 5 -23 47 -17 53 {name=$bias dir=in}"
    echo 'B 5 17 47 23 53 {name=EN dir=in}'
    echo 'T {+} -27 -24 0 0 0.3 0.3 {}'
    echo 'T {-} -27 16 0 0 0.4 0.4 {}'
    echo "T {$biaslbl} -34 45 0 0 0.11 0.11 {}"
    echo 'T {EN} 24 45 0 0 0.11 0.11 {}'
    echo "T {$tag} -8 -4 0 0 0.16 0.16 {layer=7}"
    # power BY TEXT
    echo 'T {@VPWR} 12 -26 0 0 0.16 0.16 {layer=4}'
    echo 'T {@VGND} 12 20 0 0 0.16 0.16 {layer=4}'
    # names
    echo 'T {@symname} -30 -40 0 0 0.18 0.18 {layer=8}'
    echo 'T {@spiceprefix@name} 16 -40 0 0 0.15 0.15 {}'
  } > "$f"
  echo "wrote $name.sym"
}

NIN_PF='IREF=@IREF WSCALE=@WSCALE WIN=@WIN LIN=@LIN LANA=@LANA FIN=@FIN HYSK=@HYSK'
NIN_PT='IREF=5u WSCALE=1 WIN=40u LIN=2u LANA=2u FIN=1 HYSK=0'
PIN_PT='IREF=5u WSCALE=1 WIN=80u LIN=2u LANA=2u FIN=1 HYSK=0'
RR_PF='IREF=@IREF FIN=@FIN'
RR_PT='IREF=5u FIN=1'

for r in 1V8 3V3 5V0; do
  emit "CMP_NIN_$r" "$NIN_PF" "$NIN_PT" "N"  ibp_5uA
  emit "CMP_PIN_$r" "$NIN_PF" "$PIN_PT" "P"  ibn_5uA
  emit "CMP_RR_$r"  "$RR_PF"  "$RR_PT"  "RR" ibp_5uA
done
echo "----"
echo "Total comparator symbols: $(ls "$LIB"/*.sym | wc -l)"
