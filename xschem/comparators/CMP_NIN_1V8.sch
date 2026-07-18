v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {CMP_NIN_1V8} 620 -280 0 0 0.6 0.6 {}
T {body: circuits/comparators/comparators_all.lib (authority) | vdd/vss rails drawn; ibg/o2/ENB/ENbuf are long-haul labels} 620 -220 0 0 0.3 0.3 {}
C {autohv/NMOS18.sym} 340 880 0 1 {name=mb model=NMOS18 W=\{10u*WSCALE\} L=\{LANA\} M=1}
T {mb} 280 770 0 0 0.28 0.28 {}
N 320 880 320 920 {}
C {autohv/NMOS18.sym} 810 880 0 0 {name=tail model=NMOS18 W=\{10u*WSCALE\} L=\{LANA\} M=2}
T {tail} 750 770 0 0 0.28 0.28 {}
N 830 880 830 920 {}
C {autohv/NMOS18.sym} 660 560 0 0 {name=m1 model=NMOS18 W=\{WIN*FIN\} L=\{LIN*FIN\} M=1}
T {m1} 600 450 0 0 0.28 0.28 {}
C {lab_pin.sym} 680 560 0 0 {name=lz1 lab=vss}
C {autohv/NMOS18.sym} 960 560 0 0 {name=m2 model=NMOS18 W=\{WIN*FIN\} L=\{LIN*FIN\} M=1}
T {m2} 900 450 0 0 0.28 0.28 {}
C {lab_pin.sym} 980 560 0 0 {name=lz2 lab=vss}
C {autohv/PMOS18.sym} 700 200 2 0 {name=m3 model=PMOS18 W=\{20u*WSCALE*FIN\} L=\{LANA*FIN\} M=1}
T {m3} 640 90 0 0 0.28 0.28 {}
N 680 200 680 160 {}
C {autohv/PMOS18.sym} 960 200 2 1 {name=m4 model=PMOS18 W=\{20u*WSCALE*FIN\} L=\{LANA*FIN\} M=1}
T {m4} 900 90 0 0 0.28 0.28 {}
N 980 200 980 160 {}
C {autohv/PMOS18.sym} 1260 200 2 1 {name=m5 model=PMOS18 W=\{80u*WSCALE\} L=\{LANA\} M=1}
T {m5} 1200 90 0 0 0.28 0.28 {}
N 1280 200 1280 160 {}
C {autohv/NMOS18.sym} 1260 880 0 0 {name=m6 model=NMOS18 W=\{10u*WSCALE\} L=\{LANA\} M=4}
T {m6} 1200 770 0 0 0.28 0.28 {}
N 1280 880 1280 920 {}
C {autohv/PMOS18.sym} 1560 200 2 1 {name=m7 model=PMOS18 W=\{20u*WSCALE\} L=0.5u M=1}
T {m7} 1500 90 0 0 0.28 0.28 {}
N 1580 200 1580 160 {}
C {autohv/NMOS18.sym} 1560 880 0 0 {name=m8 model=NMOS18 W=\{10u*WSCALE\} L=0.5u M=1}
T {m8} 1500 770 0 0 0.28 0.28 {}
N 1580 880 1580 920 {}
C {logic/INV_1V8.sym} 400 1240 0 0 {name=ei1 VPWR=vdd VGND=vss}
T {ei1  INV_1V8} 360 1170 0 0 0.28 0.28 {}
C {logic/INV_1V8.sym} 700 1240 0 0 {name=ei2 VPWR=vdd VGND=vss}
T {ei2  INV_1V8} 660 1170 0 0 0.28 0.28 {}
C {autohv/NMOS18.sym} 520 880 0 0 {name=sh model=NMOS18 W=4u L=0.5u M=1}
T {sh} 460 770 0 0 0.28 0.28 {}
N 540 880 540 920 {}
C {autohv/PMOS18.sym} 1400 200 2 1 {name=sho2 model=PMOS18 W=4u L=0.5u M=1}
T {sho2} 1340 90 0 0 0.28 0.28 {}
N 1420 200 1420 160 {}
C {autohv/NMOS18.sym} 300 560 0 0 {name=ser model=NMOS18 W=4u L=0.5u M=1}
T {ser} 240 450 0 0 0.28 0.28 {}
C {lab_pin.sym} 320 560 0 0 {name=lz3 lab=vss}
N 150 0 680 0 {}
N 680 0 980 0 {}
N 980 0 1280 0 {}
N 1280 0 1420 0 {}
N 1420 0 1580 0 {}
N 1580 0 1700 0 {}
N 150 1040 320 1040 {}
N 320 1040 540 1040 {}
N 540 1040 830 1040 {}
N 830 1040 1280 1040 {}
N 1280 1040 1580 1040 {}
N 1580 1040 1700 1040 {}
N 680 160 680 0 {}
N 980 160 980 0 {}
N 1280 160 1280 0 {}
N 1580 160 1580 0 {}
N 1420 160 1420 0 {}
N 320 920 320 1040 {}
N 830 920 830 1040 {}
N 1280 920 1280 1040 {}
N 1580 920 1580 1040 {}
N 540 920 540 1040 {}
C {lab_pin.sym} 150 0 0 0 {name=lz4 lab=vdd}
C {lab_pin.sym} 150 1040 0 0 {name=lz5 lab=vss}
N 320 780 380 780 {}
N 380 780 540 780 {}
N 540 780 770 780 {}
N 770 780 1220 780 {}
N 380 880 380 780 {}
N 540 840 540 780 {}
N 770 880 770 780 {}
N 1220 880 1220 780 {}
N 320 600 320 780 {}
N 320 780 320 840 {}
N 320 420 320 520 {}
N 150 420 320 420 {}
C {ipin.sym} 150 420 0 0 {name=pz6 lab=ibp_5uA}
C {lab_pin.sym} 320 780 0 0 {name=lz7 lab=ibg}
N 680 600 680 700 {}
N 980 600 980 700 {}
N 680 700 830 700 {}
N 830 700 980 700 {}
N 830 700 830 840 {}
C {lab_pin.sym} 830 700 0 0 {name=lz8 lab=tail}
N 680 240 680 320 {}
N 680 320 680 520 {}
N 680 320 740 320 {}
N 740 320 920 320 {}
N 740 320 740 200 {}
N 920 320 920 200 {}
C {lab_pin.sym} 680 320 0 0 {name=lz9 lab=n1}
N 980 240 980 440 {}
N 980 440 980 520 {}
N 980 440 1220 440 {}
N 1220 440 1220 200 {}
C {lab_pin.sym} 980 440 0 0 {name=lz10 lab=n2}
N 1280 240 1280 620 {}
N 1280 620 1280 840 {}
N 1280 620 1420 620 {}
N 1420 620 1500 620 {}
N 1500 200 1500 620 {}
N 1500 620 1500 880 {}
N 1500 200 1520 200 {}
N 1500 880 1520 880 {}
C {lab_pin.sym} 1280 620 0 0 {name=lz11 lab=o2}
N 1420 240 1420 620 {}
N 1580 240 1580 540 {}
N 1580 540 1580 840 {}
N 1580 540 1760 540 {}
C {opin.sym} 1760 540 0 0 {name=pz12 lab=out}
N 440 560 620 560 {}
C {ipin.sym} 440 560 0 0 {name=pz13 lab=inp}
N 440 460 860 460 {}
N 860 460 860 560 {}
N 860 560 920 560 {}
C {ipin.sym} 440 460 0 0 {name=pz14 lab=inn}
N 150 1240 360 1240 {}
C {ipin.sym} 150 1240 0 0 {name=pz15 lab=EN}
N 440 1240 660 1240 {}
C {lab_pin.sym} 440 1240 0 0 {name=lz16 lab=ENB}
C {lab_pin.sym} 480 880 0 0 {name=lz17 lab=ENB}
N 740 1240 820 1240 {}
C {lab_pin.sym} 820 1240 0 0 {name=lz18 lab=ENbuf}
C {lab_pin.sym} 260 560 0 0 {name=lz19 lab=ENbuf}
C {lab_pin.sym} 1360 200 0 0 {name=lz20 lab=ENbuf}
T {* EN buffer (PDK INV cells)} 340 1120 0 0 0.4 0.4 {}
T {* bias + shutdown switches} 240 -120 0 0 0.4 0.4 {}
T {* input pair + mirror load} 600 -120 0 0 0.4 0.4 {}
T {* gain stage} 1200 -120 0 0 0.4 0.4 {}
T {* output} 1500 -120 0 0 0.4 0.4 {}
T {* optional hysteresis - instantiated ONLY when HYSK>0 (default HYSK=0: these devices do not exist)} 240 1440 0 0 0.4 0.4 {}
C {autohv/NMOS18.sym} 300 1640 0 0 {name=htail model=NMOS18 W=\{10u*WSCALE*HYSK\} L=\{LANA\} M=1}
T {htail} 240 1530 0 0 0.28 0.28 {}
N 320 1640 320 1680 {}
C {lab_pin.sym} 320 1600 0 0 {name=lz21 lab=sh}
C {lab_pin.sym} 260 1640 0 0 {name=lz22 lab=ibg}
C {lab_pin.sym} 320 1680 0 0 {name=lz23 lab=vss}
C {autohv/NMOS18.sym} 600 1640 0 0 {name=mha model=NMOS18 W=\{10u*WSCALE\} L=0.5u M=1}
T {mha} 540 1530 0 0 0.28 0.28 {}
C {lab_pin.sym} 620 1640 0 0 {name=lz24 lab=vss}
C {lab_pin.sym} 620 1600 0 0 {name=lz25 lab=n1}
C {lab_pin.sym} 560 1640 0 0 {name=lz26 lab=out}
C {lab_pin.sym} 620 1680 0 0 {name=lz27 lab=sh}
C {autohv/NMOS18.sym} 900 1640 0 0 {name=mhb model=NMOS18 W=\{10u*WSCALE\} L=0.5u M=1}
T {mhb} 840 1530 0 0 0.28 0.28 {}
C {lab_pin.sym} 920 1640 0 0 {name=lz28 lab=vss}
C {lab_pin.sym} 920 1600 0 0 {name=lz29 lab=n2}
C {lab_pin.sym} 860 1640 0 0 {name=lz30 lab=o2}
C {lab_pin.sym} 920 1680 0 0 {name=lz31 lab=sh}
