#!/bin/bash
# Generate Xschem symbols for the AutoHV delay/pulse cells in
# circuits/delay_pulse_design/cells.lib
# (15 cells: {DLYR,DLYF,DLY,PHI,PLO}x{1V8,3V3,5V0}; DLY = two-sided delay).
# Ports (all): in out vdd gnd.  Option-A "timing box": in/out pins, an inner
# two-row in->out waveform, power BY TEXT (VPWR=vdd, VGND=0).
set -e
SD="$(cd "$(dirname "$0")" && pwd -P)"
LIB="$SD/delay_pulse"; mkdir -p "$LIB"
VER='v {xschem version=3.4.8RC file_version=1.3}'

# emit  NAME  "IN_WAVE(P-args)"  "OUT_WAVE(P-args)"
emit() {
  local name="$1" inw="$2" outw="$3" f="$LIB/$1.sym"
  {
    echo "$VER"; echo 'G {}'
    echo 'K {type=delaycell'
    echo 'format="@spiceprefix@name @pinlist @VPWR @VGND @symname"'
    echo 'template="name=U1 VPWR=vdd VGND=0 spiceprefix=x"'
    echo '}'
    echo 'V {}'; echo 'S {}'; echo 'F {}'; echo 'E {}'
    # box + in/out leads + pins
    echo 'L 4 -32 -20 32 -20 {}'
    echo 'L 4 32 -20 32 20 {}'
    echo 'L 4 32 20 -32 20 {}'
    echo 'L 4 -32 20 -32 -20 {}'
    echo 'L 4 -50 0 -32 0 {}'
    echo 'L 4 32 0 50 0 {}'
    echo 'B 5 -53 -3 -47 3 {name=in dir=in}'
    echo 'B 5 47 -3 53 3 {name=out dir=out}'
    # inner two-row in->out waveform (in = layer 7, out = layer 8)
    echo "P 7 $inw {}"
    echo "P 8 $outw {}"
    echo 'T {in} -30 -8 0 0 0.1 0.1 {layer=7}'
    echo 'T {out} -31 5 0 0 0.1 0.1 {layer=8}'
    # power BY TEXT
    echo 'T {@VPWR} 17 -27 0 0 0.16 0.16 {layer=4}'
    echo 'T {@VGND} 20 24 0 0 0.16 0.16 {layer=4}'
    # names
    echo 'T {@symname} -32 -27 0 0 0.18 0.18 {layer=8}'
    echo 'T {@spiceprefix@name} -32 26 0 0 0.15 0.15 {}'
  } > "$f"
  echo "wrote $name.sym"
}

DLYR_IN='4 -22 -5 -8 -5 -8 -14 22 -14';   DLYR_OUT='4 -22 14 2 14 2 5 22 5'
DLYF_IN='4 -22 -14 -8 -14 -8 -5 22 -5';   DLYF_OUT='4 -22 5 2 5 2 14 22 14'
PHI_IN='4 -22 -5 -8 -5 -8 -14 22 -14';    PHI_OUT='6 -22 14 -8 14 -8 5 2 5 2 14 22 14'
PLO_IN='4 -22 -14 -8 -14 -8 -5 22 -5';    PLO_OUT='6 -22 5 -8 5 -8 14 2 14 2 5 22 5'
# DLY (two-sided): a pulse whose BOTH edges are delayed -- out is the same
# pulse shifted right (equal delay on the rising and the falling edge).
DLY_IN='6 -22 -5 -14 -5 -14 -14 2 -14 2 -5 22 -5'
DLY_OUT='6 -22 14 -6 14 -6 5 10 5 10 14 22 14'

for d in 1V8 3V3 5V0; do
  emit "DLYR_$d" "$DLYR_IN" "$DLYR_OUT"
  emit "DLYF_$d" "$DLYF_IN" "$DLYF_OUT"
  emit "DLY_$d"  "$DLY_IN"  "$DLY_OUT"
  emit "PHI_$d"  "$PHI_IN"  "$PHI_OUT"
  emit "PLO_$d"  "$PLO_IN"  "$PLO_OUT"
done
echo "----"
echo "Total delay/pulse symbols: $(ls "$LIB"/*.sym | wc -l)"
