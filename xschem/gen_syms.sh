#!/bin/bash
# Generate Xschem symbols for the AutoHV_BiCMOS180 PDK (all .subckt devices).
# Writes into <this-dir>/autohv/. Re-run after editing glyphs/params.
#
# MOSFETs: traditional analog look. Drain=top, Source=bottom, Gate=left,
# Bulk=right (LV 4-term only). Polarity = SOURCE arrow (N outward, P inward).
# HV/LDMOS = baseline minus bulk pin, plus two drift ticks on the drain lead.
set -e
SD="$(cd "$(dirname "$0")" && pwd -P)"
LIB="$SD/autohv"
mkdir -p "$LIB"

VER='v {xschem version=3.4.8RC file_version=1.3}'

# ===========================================================================
# MOSFETs (subcircuit type, X prefix, @symname -> subckt name)
# ===========================================================================
# emit_mos NAME  POL(N|P)  HV(0|1)  LMODE(L|L8|NOL)
emit_mos() {
  local name="$1" pol="$2" hv="$3" lmode="$4"
  local f="$LIB/$name.sym" fmt tdef plabel xtype=nmos
  [ "$pol" = P ] && xtype=pmos
  case "$lmode" in
    L)   fmt='W=@W L=@L M=@M MM_SIGMA=@MM_SIGMA'; tdef='W=10u L=1u M=1 MM_SIGMA=0 spiceprefix=X'; plabel='W=@W L=@L M=@M';;
    L8)  fmt='W=@W L=@L M=@M MM_SIGMA=@MM_SIGMA'; tdef='W=10u L=8u M=1 MM_SIGMA=0 spiceprefix=X'; plabel='W=@W L=@L M=@M';;
    NOL) fmt='W=@W M=@M MM_SIGMA=@MM_SIGMA';      tdef='W=10u M=1 MM_SIGMA=0 spiceprefix=X';      plabel='W=@W M=@M';;
  esac
  # drain lead sticks out a touch further on HV (clears the drift box)
  local DTOP=-35 DLO=-37.5 DHI=-32.5
  [ "$hv" = 1 ] && { DTOP=-40; DLO=-42.5; DHI=-37.5; }
  # NOTE: type is a PRIMITIVE (nmos/pmos), NOT subcircuit. type=subcircuit makes
  # xschem emit a spurious empty ".subckt NMOSxx" that collides with the real
  # model in the .lib. A primitive type + @spiceprefix forces the X-prefixed
  # subckt call (robust even if the instance is renamed, e.g. MN4 -> XMN4).
  {
    echo "$VER"
    echo 'G {}'
    echo "K {type=$xtype"
    echo "format=\"@spiceprefix@name @pinlist @symname $fmt\""
    echo "template=\"name=M1 $tdef\""
    echo '}'
    echo 'V {}'; echo 'S {}'; echo 'F {}'; echo 'E {}'
    # --- common body: gate plate + channel bar (G left); D top / S bottom on a
    #     right rail reached by stretched horizontal drain/source lines; bulk a
    #     short stub tucked in on the right (LV only) ---
    if [ "$pol" = P ]; then
      echo 'L 4 -30 0 -15 0 {}'        # gate lead (stops at inversion bubble)
      echo 'A 4 -12.5 0 2.5 0 360 {}'  # PMOS gate inversion bubble
    else
      echo 'L 4 -30 0 -10 0 {}'        # gate lead
    fi
    echo 'L 4 -10 -15 -10 15 {}'   # gate plate (parallel bar, offset gap)
    echo 'L 4 -5 -15 -5 15 {}'     # channel/active bar
    echo 'L 4 -5 -15 15 -15 {}'    # drain horizontal (stretched)
    echo "L 4 15 -15 15 $DTOP {}"   # drain lead up to pin (extended; HV a touch more)
    echo 'L 4 -5 15 15 15 {}'      # source horizontal (stretched)
    echo 'L 4 15 15 15 30 {}'      # source lead down to pin
    if [ "$hv" = 0 ]; then
      echo 'L 4 -5 0 10 0 {}'      # bulk stub (short, LV 4-terminal only)
    else
      echo 'L 4 -5 -20 15 -20 {}'  # HV drift line (bisects the box)
      echo 'L 4 -5 -25 15 -25 {}'  # HV drift box top edge
      echo 'L 4 -5 -25 -5 -15 {}'  # HV drift box left edge (closes the box; right edge = drain lead)
    fi
    # --- source arrow encodes polarity; tip sits at the end of the source line ---
    if [ "$pol" = N ]; then
      echo 'P 4 4 15 15 10 12 10 18 15 15 {fill=true}'   # NMOS: tip at right edge (outward)
    else
      echo 'P 4 4 -5 15 0 12 0 18 -5 15 {fill=true}'     # PMOS: tip at left edge (inward)
    fi
    # --- pins: record order = subckt port order  d g s [b] ---
    echo "B 5 12.5 $DLO 17.5 $DHI {name=d dir=inout}"
    echo 'B 5 -32.5 -2.5 -27.5 2.5 {name=g dir=in}'
    echo 'B 5 12.5 27.5 17.5 32.5 {name=s dir=inout}'
    [ "$hv" = 0 ] && echo 'B 5 7.5 -2.5 12.5 2.5 {name=b dir=in}'
    # --- labels: instance, model/symbol, geometry ---
    echo 'T {@spiceprefix@name} 20 -22 0 0 0.2 0.2 {}'
    echo 'T {@symname} 20 -10 0 0 0.18 0.18 {layer=8}'
    echo "T {$plabel} 20 20 0 0 0.16 0.16 {}"
  } > "$f"
  echo "wrote $name.sym (MOS $pol hv=$hv $lmode)"
}

# LV 4-terminal MOS (d g s b)
for d in NMOS12 NMOS18 NMOS33 NMOS50; do emit_mos "$d" N 0 L; done
for d in PMOS12 PMOS18 PMOS33 PMOS50; do emit_mos "$d" P 0 L; done
# HV DMOS, 3-terminal (d g s), no L
for d in NDMOS20 NDMOS40 NDMOS60 NDMOS80 NDMOS120 DNMOS20; do emit_mos "$d" N 1 NOL; done
for d in PDMOS20 PDMOS40 PDMOS60 PDMOS80 PDMOS120;          do emit_mos "$d" P 1 NOL; done
# HV DMOS 200 V, 3-terminal (d g s), L = drift length (8u)
emit_mos NDMOS200 N 1 L8
emit_mos PDMOS200 P 1 L8

# ===========================================================================
# BJT / diode / resistor / capacitor  (unchanged; validated)
# ===========================================================================
glyph_npn() { cat <<'EOF'
L 4 0 -30 0 30 {}
L 4 -20 0 -12.5 0 {}
L 4 -20 0 0 0 {}
L 4 -0 10 8.75 18.75 {}
L 4 0 -10 20 -30 {}
P 4 4 20 30 13.75 13.75 3.75 23.75 20 30 {fill=true}
EOF
}
glyph_pnp() { cat <<'EOF'
L 4 0 -30 0 30 {}
L 4 -20 0 0 0 {}
L 4 10 -20 20 -30 {}
L 4 0 10 20 30 {}
P 4 4 0 -10 15 -15 5 -25 0 -10 {fill=true}
EOF
}
glyph_diode() { cat <<'EOF'
L 4 0 5 0 30 {}
L 4 0 -30 0 -5 {}
L 4 -10 5 10 5 {}
P 4 4 -0 5 -10 -5 10 -5 0 5 {fill=true}
EOF
}
glyph_zener() { cat <<'EOF'
L 4 0 5 0 30 {}
L 4 0 -30 0 -5 {}
L 4 -20 5 20 5 {}
L 4 20 -5 20 5 {}
L 4 -20 5 -20 15 {}
P 4 4 -0 5 -10 -5 10 -5 -0 5 {fill=true}
EOF
}
glyph_res() { cat <<'EOF'
L 4 0 20 0 30 {}
L 4 0 20 7.5 17.5 {}
L 4 -7.5 12.5 7.5 17.5 {}
L 4 -7.5 12.5 7.5 7.5 {}
L 4 -7.5 2.5 7.5 7.5 {}
L 4 -7.5 2.5 7.5 -2.5 {}
L 4 -7.5 -7.5 7.5 -2.5 {}
L 4 -7.5 -7.5 7.5 -12.5 {}
L 4 -7.5 -17.5 7.5 -12.5 {}
L 4 -7.5 -17.5 0 -20 {}
L 4 0 -30 0 -20 {}
EOF
}
glyph_cap() { cat <<'EOF'
L 4 0 5 0 30 {}
L 4 0 -30 0 -5 {}
L 4 -10 -5 10 -5 {}
L 4 -10 5 10 5 {}
EOF
}
# Schottky: diode triangle + S-bent cathode bar (DIO_SCH distinguishing mark)
glyph_schottky() { cat <<'EOF'
L 4 0 5 0 30 {}
L 4 0 -30 0 -5 {}
L 4 -10 5 10 5 {}
L 4 -10 5 -10 9 {}
L 4 -10 9 -6 9 {}
L 4 10 5 10 1 {}
L 4 10 1 6 1 {}
P 4 4 -0 5 -10 -5 10 -5 0 5 {fill=true}
EOF
}
# Resistor per-material marks (all share the base zigzag glyph_res):
#   poly  -> tick(s) across the top lead  (RPOLY_LO 1 tick, RPOLY_HI 2 ticks)
#   silicon/well -> a "tub" bracket framing the body (RNWELL/RNPLUS/RPPLUS)
glyph_res_poly1() { glyph_res; printf 'L 4 -3 -24 3 -24 {}\n'; }
glyph_res_poly2() { glyph_res; printf 'L 4 -3 -23 3 -23 {}\nL 4 -3 -26 3 -26 {}\n'; }
glyph_res_tub() { glyph_res; printf 'L 4 -11 -10 -11 10 {}\nL 4 -11 -10 -9 -10 {}\nL 4 -11 10 -9 10 {}\nL 4 11 -10 11 10 {}\nL 4 11 -10 9 -10 {}\nL 4 11 10 9 10 {}\n'; }
pins_npn() { cat <<'EOF'
B 5 17.5 -32.5 22.5 -27.5 {name=c dir=inout}
B 5 -22.5 -2.5 -17.5 2.5 {name=b dir=in}
B 5 17.5 27.5 22.5 32.5 {name=e dir=inout}
EOF
}
pins_pnp() { cat <<'EOF'
B 5 17.5 27.5 22.5 32.5 {name=c dir=inout}
B 5 -22.5 -2.5 -17.5 2.5 {name=b dir=in}
B 5 17.5 -32.5 22.5 -27.5 {name=e dir=inout}
EOF
}
pins_ac() { cat <<'EOF'
B 5 -2.5 -32.5 2.5 -27.5 {name=a dir=inout}
B 5 -2.5 27.5 2.5 32.5 {name=c dir=inout}
EOF
}
pins_pn() { cat <<'EOF'
B 5 -2.5 -32.5 2.5 -27.5 {name=p dir=inout}
B 5 -2.5 27.5 2.5 32.5 {name=n dir=inout}
EOF
}
# Same idiom as the MOS symbols: primitive type (NOT subcircuit), @spiceprefix
# forces the X subckt-call prefix, @symname = subckt name (= filename).
# emit_dev NAME TYPE GLYPHFN PINSFN FMT TDEF PREFIX PLABEL
emit_dev() {
  local name="$1" type="$2" gfn="$3" pfn="$4" fmt="$5" tdef="$6" pfx="$7" plabel="$8"
  {
    echo "$VER"; echo 'G {}'
    echo "K {type=$type"
    echo "format=\"@spiceprefix@name @pinlist @symname $fmt\""
    echo "template=\"name=${pfx}1 $tdef spiceprefix=X\""
    echo '}'
    echo 'V {}'; echo 'S {}'; echo 'F {}'; echo 'E {}'
    $gfn; $pfn
    echo 'T {@spiceprefix@name} 26 -6 0 0 0.2 0.2 {}'
    echo 'T {@symname} 26 6 0 0 0.18 0.18 {layer=8}'
    echo "T {$plabel} 26 18 0 0 0.16 0.16 {}"
  } > "$LIB/$name.sym"
  echo "wrote $name.sym"
}
BJT_FMT='AREA=@AREA MM_SIGMA=@MM_SIGMA';  BJT_TDEF='AREA=1 MM_SIGMA=0'
RES_FMT='L=@L W=@W MM_SIGMA=@MM_SIGMA';    RES_TDEF='L=100u W=10u MM_SIGMA=0'
CAP_FMT='L=@L W=@W MM_SIGMA=@MM_SIGMA';    CAP_TDEF='L=100u W=100u MM_SIGMA=0'
# BJT (c b e), AREA
emit_dev NPN_LV  npn glyph_npn pins_npn "$BJT_FMT" "$BJT_TDEF" Q 'AREA=@AREA'
emit_dev NPN_HV  npn glyph_npn pins_npn "$BJT_FMT" "$BJT_TDEF" Q 'AREA=@AREA'
emit_dev PNP_LAT pnp glyph_pnp pins_pnp "$BJT_FMT" "$BJT_TDEF" Q 'AREA=@AREA'
emit_dev PNP_HV  pnp glyph_pnp pins_pnp "$BJT_FMT" "$BJT_TDEF" Q 'AREA=@AREA'
# Diodes / zeners (a c), AREA
emit_dev DIO_PN   diode glyph_diode    pins_ac "$BJT_FMT" "$BJT_TDEF" D 'AREA=@AREA'
emit_dev DIO_FAST diode glyph_diode    pins_ac "$BJT_FMT" "$BJT_TDEF" D 'AREA=@AREA'
emit_dev DIO_SCH  diode glyph_schottky pins_ac "$BJT_FMT" "$BJT_TDEF" D 'AREA=@AREA'
emit_dev DZ_5V6   diode glyph_zener    pins_ac "$BJT_FMT" "$BJT_TDEF" D 'AREA=@AREA'
emit_dev DZ_12    diode glyph_zener    pins_ac "$BJT_FMT" "$BJT_TDEF" D 'AREA=@AREA'
emit_dev DZ_24    diode glyph_zener    pins_ac "$BJT_FMT" "$BJT_TDEF" D 'AREA=@AREA'
# Resistors (p n), L W -- per-material distinguishing mark
emit_dev RPOLY_HI resistor glyph_res_poly2 pins_pn "$RES_FMT" "$RES_TDEF" R 'L=@L W=@W'
emit_dev RPOLY_LO resistor glyph_res_poly1 pins_pn "$RES_FMT" "$RES_TDEF" R 'L=@L W=@W'
emit_dev RNWELL   resistor glyph_res_tub   pins_pn "$RES_FMT" "$RES_TDEF" R 'L=@L W=@W'
emit_dev RNPLUS   resistor glyph_res_tub   pins_pn "$RES_FMT" "$RES_TDEF" R 'L=@L W=@W'
emit_dev RPPLUS   resistor glyph_res_tub   pins_pn "$RES_FMT" "$RES_TDEF" R 'L=@L W=@W'
# Caps (p n), L W
emit_dev CMIM_STD capacitor glyph_cap pins_pn "$CAP_FMT" "$CAP_TDEF" C 'L=@L W=@W'
emit_dev CMIM_HI  capacitor glyph_cap pins_pn "$CAP_FMT" "$CAP_TDEF" C 'L=@L W=@W'
emit_dev CMOM     capacitor glyph_cap pins_pn "$CAP_FMT" "$CAP_TDEF" C 'L=@L W=@W'
emit_dev CFRINGE  capacitor glyph_cap pins_pn "$CAP_FMT" "$CAP_TDEF" C 'L=@L W=@W'

echo "----"
echo "Total symbols: $(ls "$LIB"/*.sym | wc -l)"
