v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {CMP_PIN_5V0} 620 -280 0 0 0.6 0.6 {}
T {body: circuits/comparators/comparators_all.lib (authority) | PMOS input pair, NMOS mirror load} 620 -220 0 0 0.3 0.3 {}
C {autohv/PMOS50.sym} 300 200 0 0 {name=ser model=PMOS50 W=4u L=0.5u M=1}
T {ser} 240 90 0 0 0.28 0.28 {}
C {lab_pin.sym} 320 200 0 0 {name=lz1 lab=vdd}
C {autohv/PMOS50.sym} 460 200 2 0 {name=mb model=PMOS50 W=\{20u*WSCALE\} L=\{LANA\} M=1}
T {mb} 400 90 0 0 0.28 0.28 {}
N 440 200 440 160 {}
C {autohv/PMOS50.sym} 600 200 2 1 {name=sh model=PMOS50 W=4u L=0.5u M=1}
T {sh} 540 90 0 0 0.28 0.28 {}
N 620 200 620 160 {}
C {autohv/PMOS50.sym} 910 200 2 1 {name=tail model=PMOS50 W=\{20u*WSCALE\} L=\{LANA\} M=2}
T {tail} 850 90 0 0 0.28 0.28 {}
N 930 200 930 160 {}
C {autohv/PMOS50.sym} 760 560 2 1 {name=m1 model=PMOS50 W=\{WIN*FIN\} L=\{LIN*FIN\} M=1}
T {m1} 700 450 0 0 0.28 0.28 {}
C {lab_pin.sym} 780 560 0 0 {name=lz2 lab=vdd}
C {autohv/PMOS50.sym} 1060 560 2 1 {name=m2 model=PMOS50 W=\{WIN*FIN\} L=\{LIN*FIN\} M=1}
T {m2} 1000 450 0 0 0.28 0.28 {}
C {lab_pin.sym} 1080 560 0 0 {name=lz3 lab=vdd}
C {autohv/NMOS50.sym} 800 880 0 1 {name=m3 model=NMOS50 W=\{10u*WSCALE*FIN\} L=\{LANA*FIN\} M=1}
T {m3} 740 770 0 0 0.28 0.28 {}
N 780 880 780 920 {}
C {autohv/NMOS50.sym} 1060 880 0 0 {name=m4 model=NMOS50 W=\{10u*WSCALE*FIN\} L=\{LANA*FIN\} M=1}
T {m4} 1000 770 0 0 0.28 0.28 {}
N 1080 880 1080 920 {}
C {autohv/NMOS50.sym} 1360 880 0 0 {name=m5 model=NMOS50 W=\{40u*WSCALE\} L=\{LANA\} M=1}
T {m5} 1300 770 0 0 0.28 0.28 {}
N 1380 880 1380 920 {}
C {autohv/PMOS50.sym} 1360 200 2 1 {name=m6 model=PMOS50 W=\{20u*WSCALE\} L=\{LANA\} M=4}
T {m6} 1300 90 0 0 0.28 0.28 {}
N 1380 200 1380 160 {}
C {autohv/PMOS50.sym} 1660 200 2 1 {name=m7 model=PMOS50 W=\{20u*WSCALE\} L=0.5u M=1}
T {m7} 1600 90 0 0 0.28 0.28 {}
N 1680 200 1680 160 {}
C {autohv/NMOS50.sym} 1660 880 0 0 {name=m8 model=NMOS50 W=\{10u*WSCALE\} L=0.5u M=1}
T {m8} 1600 770 0 0 0.28 0.28 {}
N 1680 880 1680 920 {}
C {autohv/NMOS50.sym} 1500 880 0 0 {name=sho2 model=NMOS50 W=4u L=0.5u M=1}
T {sho2} 1440 770 0 0 0.28 0.28 {}
N 1520 880 1520 920 {}
C {logic/INV_5V0.sym} 400 1240 0 0 {name=ei1 VPWR=vdd VGND=vss}
T {ei1  INV_5V0} 360 1170 0 0 0.28 0.28 {}
C {logic/INV_5V0.sym} 700 1240 0 0 {name=ei2 VPWR=vdd VGND=vss}
T {ei2  INV_5V0} 660 1170 0 0 0.28 0.28 {}
N 150 0 440 0 {}
N 440 0 620 0 {}
N 620 0 930 0 {}
N 930 0 1380 0 {}
N 1380 0 1680 0 {}
N 1680 0 1800 0 {}
N 150 1040 780 1040 {}
N 780 1040 1080 1040 {}
N 1080 1040 1380 1040 {}
N 1380 1040 1520 1040 {}
N 1520 1040 1680 1040 {}
N 1680 1040 1800 1040 {}
N 440 160 440 0 {}
N 930 160 930 0 {}
N 1380 160 1380 0 {}
N 1680 160 1680 0 {}
N 620 160 620 0 {}
N 780 920 780 1040 {}
N 1080 920 1080 1040 {}
N 1380 920 1380 1040 {}
N 1680 920 1680 1040 {}
N 1520 920 1520 1040 {}
C {lab_pin.sym} 150 0 0 0 {name=lz4 lab=vdd}
C {lab_pin.sym} 150 1040 0 0 {name=lz5 lab=vss}
N 320 300 440 300 {}
N 440 300 500 300 {}
N 500 300 620 300 {}
N 620 300 870 300 {}
N 870 300 1320 300 {}
N 440 240 440 300 {}
N 500 200 500 300 {}
N 870 200 870 300 {}
N 1320 200 1320 300 {}
N 620 240 620 300 {}
N 320 240 320 300 {}
C {lab_pin.sym} 440 300 0 0 {name=lz6 lab=ibg}
N 320 100 320 160 {}
N 150 100 320 100 {}
C {ipin.sym} 150 100 0 0 {name=pz7 lab=ibn_5uA}
N 780 520 780 440 {}
N 1080 520 1080 440 {}
N 780 440 930 440 {}
N 930 440 1080 440 {}
N 930 440 930 240 {}
C {lab_pin.sym} 930 440 0 0 {name=lz8 lab=tail}
N 780 600 780 720 {}
N 780 720 780 840 {}
N 780 720 840 720 {}
N 840 720 1020 720 {}
N 840 720 840 880 {}
N 1020 720 1020 880 {}
C {lab_pin.sym} 780 720 0 0 {name=lz9 lab=n1}
N 1080 600 1080 680 {}
N 1080 680 1080 840 {}
N 1080 680 1320 680 {}
N 1320 680 1320 880 {}
C {lab_pin.sym} 1080 680 0 0 {name=lz10 lab=n2}
N 1380 240 1380 560 {}
N 1380 560 1380 840 {}
N 1380 560 1520 560 {}
N 1520 560 1600 560 {}
N 1600 200 1600 560 {}
N 1600 560 1600 880 {}
N 1600 200 1620 200 {}
N 1600 880 1620 880 {}
N 1520 560 1520 840 {}
C {lab_pin.sym} 1380 560 0 0 {name=lz11 lab=o2}
N 1680 240 1680 540 {}
N 1680 540 1680 840 {}
N 1680 540 1860 540 {}
C {opin.sym} 1860 540 0 0 {name=pz12 lab=out}
N 500 560 720 560 {}
C {ipin.sym} 500 560 0 0 {name=pz13 lab=inp}
N 500 460 960 460 {}
N 960 460 960 560 {}
N 960 560 1020 560 {}
C {ipin.sym} 500 460 0 0 {name=pz14 lab=inn}
N 150 1240 360 1240 {}
C {ipin.sym} 150 1240 0 0 {name=pz15 lab=EN}
N 440 1240 660 1240 {}
C {lab_pin.sym} 440 1240 0 0 {name=lz16 lab=ENB}
N 740 1240 820 1240 {}
C {lab_pin.sym} 820 1240 0 0 {name=lz17 lab=ENbuf}
C {lab_pin.sym} 560 200 0 0 {name=lz18 lab=ENbuf}
C {lab_pin.sym} 260 200 0 0 {name=lz19 lab=ENB}
C {lab_pin.sym} 1460 880 0 0 {name=lz20 lab=ENB}
T {* EN buffer (PDK INV cells)} 340 1120 0 0 0.4 0.4 {}
T {* bias + shutdown switches} 240 -120 0 0 0.4 0.4 {}
T {* input pair + mirror load} 700 -120 0 0 0.4 0.4 {}
T {* gain stage} 1300 -120 0 0 0.4 0.4 {}
T {* output} 1600 -120 0 0 0.4 0.4 {}
T {* optional hysteresis - instantiated ONLY when HYSK>0 (default HYSK=0: these devices do not exist)} 240 1440 0 0 0.4 0.4 {}
C {autohv/PMOS50.sym} 300 1640 2 1 {name=htail model=PMOS50 W=\{20u*WSCALE*HYSK\} L=\{LANA\} M=1}
T {htail} 240 1530 0 0 0.28 0.28 {}
N 320 1640 320 1600 {}
C {lab_pin.sym} 320 1680 0 0 {name=lz21 lab=sh}
C {lab_pin.sym} 260 1640 0 0 {name=lz22 lab=ibg}
C {lab_pin.sym} 320 1600 0 0 {name=lz23 lab=vdd}
C {autohv/PMOS50.sym} 600 1640 2 1 {name=mha model=PMOS50 W=\{20u*WSCALE\} L=0.5u M=1}
T {mha} 540 1530 0 0 0.28 0.28 {}
C {lab_pin.sym} 620 1640 0 0 {name=lz24 lab=vdd}
C {lab_pin.sym} 620 1680 0 0 {name=lz25 lab=n1}
C {lab_pin.sym} 560 1640 0 0 {name=lz26 lab=out}
C {lab_pin.sym} 620 1600 0 0 {name=lz27 lab=sh}
C {autohv/PMOS50.sym} 900 1640 2 1 {name=mhb model=PMOS50 W=\{20u*WSCALE\} L=0.5u M=1}
T {mhb} 840 1530 0 0 0.28 0.28 {}
C {lab_pin.sym} 920 1640 0 0 {name=lz28 lab=vdd}
C {lab_pin.sym} 920 1680 0 0 {name=lz29 lab=n2}
C {lab_pin.sym} 860 1640 0 0 {name=lz30 lab=o2}
C {lab_pin.sym} 920 1600 0 0 {name=lz31 lab=sh}
