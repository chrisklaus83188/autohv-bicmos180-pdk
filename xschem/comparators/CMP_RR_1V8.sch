v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {CMP_RR_1V8} 620 -280 0 0 0.6 0.6 {}
T {body: circuits/comparators/comparators_all.lib (authority) | rail-to-rail input, folded cascode} 620 -220 0 0 0.3 0.3 {}
C {autohv/NMOS18.sym} 250 1200 0 0 {name=rbn model=NMOS18 W=10u L=1u M=1}
T {rbn} 190 1090 0 0 0.28 0.28 {}
N 270 1200 270 1240 {}
C {autohv/NMOS18.sym} 250 700 0 0 {name=ser model=NMOS18 W=4u L=0.5u M=1}
T {ser} 190 590 0 0 0.28 0.28 {}
C {lab_pin.sym} 270 700 0 0 {name=lz1 lab=vss}
C {autohv/NMOS18.sym} 400 1200 0 0 {name=mir model=NMOS18 W=10u L=1u M=1}
T {mir} 340 1090 0 0 0.28 0.28 {}
N 420 1200 420 1240 {}
C {autohv/PMOS18.sym} 550 200 2 1 {name=rbp model=PMOS18 W=20u L=1u M=1}
T {rbp} 490 90 0 0 0.28 0.28 {}
N 570 200 570 160 {}
C {autohv/PMOS18.sym} 700 200 2 1 {name=vc1 model=PMOS18 W=20u L=1u M=1}
T {vc1} 640 90 0 0 0.28 0.28 {}
N 720 200 720 160 {}
C {autohv/PMOS18.sym} 700 460 2 1 {name=vc2 model=PMOS18 W=20u L=1u M=1}
T {vc2} 640 350 0 0 0.28 0.28 {}
C {lab_pin.sym} 720 460 0 0 {name=lz2 lab=vdd}
C {autohv/NMOS18.sym} 850 1200 0 0 {name=isk model=NMOS18 W=10u L=1u M=1}
T {isk} 790 1090 0 0 0.28 0.28 {}
N 870 1200 870 1240 {}
C {autohv/NMOS18.sym} 1000 1200 0 0 {name=shn model=NMOS18 W=4u L=0.5u M=1}
T {shn} 940 1090 0 0 0.28 0.28 {}
N 1020 1200 1020 1240 {}
C {autohv/PMOS18.sym} 1150 200 2 1 {name=shp model=PMOS18 W=4u L=0.5u M=1}
T {shp} 1090 90 0 0 0.28 0.28 {}
N 1170 200 1170 160 {}
C {autohv/PMOS18.sym} 1300 200 2 1 {name=mtp model=PMOS18 W=40u L=1u M=1}
T {mtp} 1240 90 0 0 0.28 0.28 {}
N 1320 200 1320 160 {}
C {autohv/PMOS18.sym} 1450 700 2 1 {name=p1 model=PMOS18 W=\{80u*FIN\} L=\{1u*FIN\} M=1}
T {p1} 1390 590 0 0 0.28 0.28 {}
C {lab_pin.sym} 1470 700 0 0 {name=lz3 lab=vdd}
C {autohv/PMOS18.sym} 1600 700 2 1 {name=p2 model=PMOS18 W=\{80u*FIN\} L=\{1u*FIN\} M=1}
T {p2} 1540 590 0 0 0.28 0.28 {}
C {lab_pin.sym} 1620 700 0 0 {name=lz4 lab=vdd}
C {autohv/NMOS18.sym} 1450 940 0 0 {name=n1 model=NMOS18 W=\{40u*FIN\} L=\{1u*FIN\} M=1}
T {n1} 1390 830 0 0 0.28 0.28 {}
C {lab_pin.sym} 1470 940 0 0 {name=lz5 lab=vss}
C {autohv/NMOS18.sym} 1600 940 0 0 {name=n2 model=NMOS18 W=\{40u*FIN\} L=\{1u*FIN\} M=1}
T {n2} 1540 830 0 0 0.28 0.28 {}
C {lab_pin.sym} 1620 940 0 0 {name=lz6 lab=vss}
C {autohv/NMOS18.sym} 1520 1200 0 0 {name=mtn model=NMOS18 W=20u L=1u M=1}
T {mtn} 1460 1090 0 0 0.28 0.28 {}
N 1540 1200 1540 1240 {}
C {autohv/PMOS18.sym} 1750 200 2 1 {name=f1 model=PMOS18 W=60u L=1u M=1}
T {f1} 1690 90 0 0 0.28 0.28 {}
N 1770 200 1770 160 {}
C {autohv/PMOS18.sym} 1750 460 2 1 {name=cp1 model=PMOS18 W=40u L=1u M=1}
T {cp1} 1690 350 0 0 0.28 0.28 {}
C {lab_pin.sym} 1770 460 0 0 {name=lz7 lab=vdd}
C {autohv/NMOS18.sym} 1750 1200 0 0 {name=mm1 model=NMOS18 W=\{20u*FIN\} L=\{1u*FIN\} M=1}
T {mm1} 1690 1090 0 0 0.28 0.28 {}
N 1770 1200 1770 1240 {}
C {autohv/PMOS18.sym} 1900 200 2 1 {name=f2 model=PMOS18 W=60u L=1u M=1}
T {f2} 1840 90 0 0 0.28 0.28 {}
N 1920 200 1920 160 {}
C {autohv/PMOS18.sym} 1900 460 2 1 {name=cp2 model=PMOS18 W=40u L=1u M=1}
T {cp2} 1840 350 0 0 0.28 0.28 {}
C {lab_pin.sym} 1920 460 0 0 {name=lz8 lab=vdd}
C {autohv/NMOS18.sym} 1900 1200 0 0 {name=mm2 model=NMOS18 W=\{20u*FIN\} L=\{1u*FIN\} M=1}
T {mm2} 1840 1090 0 0 0.28 0.28 {}
N 1920 1200 1920 1240 {}
C {autohv/PMOS18.sym} 2100 200 2 1 {name=s2p model=PMOS18 W=40u L=1u M=1}
T {s2p} 2040 90 0 0 0.28 0.28 {}
N 2120 200 2120 160 {}
C {autohv/NMOS18.sym} 2100 1200 0 0 {name=s2n model=NMOS18 W=40u L=1u M=1}
T {s2n} 2040 1090 0 0 0.28 0.28 {}
N 2120 1200 2120 1240 {}
C {autohv/NMOS18.sym} 2250 1200 0 0 {name=sho2 model=NMOS18 W=4u L=0.5u M=1}
T {sho2} 2190 1090 0 0 0.28 0.28 {}
N 2270 1200 2270 1240 {}
C {autohv/PMOS18.sym} 2400 200 2 1 {name=bp model=PMOS18 W=20u L=0.5u M=1}
T {bp} 2340 90 0 0 0.28 0.28 {}
N 2420 200 2420 160 {}
C {autohv/NMOS18.sym} 2400 1200 0 0 {name=bn model=NMOS18 W=10u L=0.5u M=1}
T {bn} 2340 1090 0 0 0.28 0.28 {}
N 2420 1200 2420 1240 {}
C {logic/INV_1V8.sym} 400 1560 0 0 {name=ei1 VPWR=vdd VGND=vss}
T {ei1  INV_1V8} 360 1490 0 0 0.28 0.28 {}
C {logic/INV_1V8.sym} 700 1560 0 0 {name=ei2 VPWR=vdd VGND=vss}
T {ei2  INV_1V8} 660 1490 0 0 0.28 0.28 {}
N 150 0 570 0 {}
N 570 0 720 0 {}
N 720 0 1170 0 {}
N 1170 0 1320 0 {}
N 1320 0 1770 0 {}
N 1770 0 1920 0 {}
N 1920 0 2120 0 {}
N 2120 0 2420 0 {}
N 2420 0 2560 0 {}
N 150 1360 270 1360 {}
N 270 1360 420 1360 {}
N 420 1360 870 1360 {}
N 870 1360 1020 1360 {}
N 1020 1360 1540 1360 {}
N 1540 1360 1770 1360 {}
N 1770 1360 1920 1360 {}
N 1920 1360 2120 1360 {}
N 2120 1360 2270 1360 {}
N 2270 1360 2420 1360 {}
N 2420 1360 2560 1360 {}
N 570 160 570 0 {}
N 720 160 720 0 {}
N 1170 160 1170 0 {}
N 1320 160 1320 0 {}
N 1770 160 1770 0 {}
N 1920 160 1920 0 {}
N 2120 160 2120 0 {}
N 2420 160 2420 0 {}
N 270 1240 270 1360 {}
N 420 1240 420 1360 {}
N 870 1240 870 1360 {}
N 1020 1240 1020 1360 {}
N 1540 1240 1540 1360 {}
N 1770 1240 1770 1360 {}
N 1920 1240 1920 1360 {}
N 2120 1240 2120 1360 {}
N 2270 1240 2270 1360 {}
N 2420 1240 2420 1360 {}
C {lab_pin.sym} 150 0 0 0 {name=lz9 lab=vdd}
C {lab_pin.sym} 150 1360 0 0 {name=lz10 lab=vss}
N 210 1100 270 1100 {}
N 270 1100 360 1100 {}
N 360 1100 810 1100 {}
N 810 1100 1020 1100 {}
N 1020 1100 1480 1100 {}
N 270 1160 270 1100 {}
N 210 1200 210 1100 {}
N 360 1200 360 1100 {}
N 810 1200 810 1100 {}
N 1480 1200 1480 1100 {}
N 1020 1160 1020 1100 {}
N 270 740 270 1100 {}
C {lab_pin.sym} 210 1100 0 0 {name=lz11 lab=ibg_n}
N 420 300 510 300 {}
N 510 300 570 300 {}
N 570 300 1170 300 {}
N 1170 300 1260 300 {}
N 1260 300 1710 300 {}
N 1710 300 1860 300 {}
N 1860 300 2060 300 {}
N 420 1160 420 300 {}
N 570 240 570 300 {}
N 510 200 510 300 {}
N 1260 200 1260 300 {}
N 1710 200 1710 300 {}
N 1860 200 1860 300 {}
N 2060 200 2060 300 {}
N 1170 240 1170 300 {}
C {lab_pin.sym} 420 300 0 0 {name=lz12 lab=pmd}
N 150 660 270 660 {}
C {ipin.sym} 150 660 0 0 {name=pz13 lab=ibp_5uA}
N 720 240 720 320 {}
N 720 320 720 420 {}
N 660 200 660 320 {}
N 660 320 720 320 {}
C {lab_pin.sym} 720 320 0 0 {name=lz14 lab=k}
N 660 560 720 560 {}
N 720 560 870 560 {}
N 870 560 1710 560 {}
N 1710 560 1860 560 {}
N 720 500 720 560 {}
N 660 460 660 560 {}
N 1710 460 1710 560 {}
N 1860 460 1860 560 {}
N 870 1160 870 560 {}
C {lab_pin.sym} 660 560 0 0 {name=lz15 lab=vcp}
N 1320 240 1320 580 {}
N 1320 580 1470 580 {}
N 1470 580 1620 580 {}
N 1470 580 1470 660 {}
N 1620 580 1620 660 {}
C {lab_pin.sym} 1320 580 0 0 {name=lz16 lab=sp}
N 1470 1060 1540 1060 {}
N 1540 1060 1620 1060 {}
N 1470 980 1470 1060 {}
N 1620 980 1620 1060 {}
N 1540 1060 1540 1160 {}
C {lab_pin.sym} 1540 1060 0 0 {name=lz17 lab=sn}
N 1770 240 1770 340 {}
N 1770 340 1770 420 {}
N 1470 900 1500 900 {}
N 1500 340 1500 900 {}
N 1500 340 1770 340 {}
C {lab_pin.sym} 1770 340 0 0 {name=lz18 lab=x}
N 1920 240 1920 380 {}
N 1920 380 1920 420 {}
N 1620 900 1660 900 {}
N 1660 380 1660 900 {}
N 1660 380 1920 380 {}
C {lab_pin.sym} 1920 380 0 0 {name=lz19 lab=y}
N 1770 500 1770 800 {}
N 1770 800 1770 1160 {}
N 1470 740 1470 800 {}
N 1470 800 1770 800 {}
C {lab_pin.sym} 1770 800 0 0 {name=lz20 lab=a}
N 1920 500 1920 860 {}
N 1920 860 1920 1160 {}
N 1620 740 1620 860 {}
N 1620 860 1920 860 {}
C {lab_pin.sym} 1920 860 0 0 {name=lz21 lab=b}
N 1710 1100 1770 1100 {}
N 1770 1100 1860 1100 {}
N 1710 1200 1710 1100 {}
N 1860 1200 1860 1100 {}
N 1770 1100 1770 1160 {}
N 1920 1020 1920 1160 {}
N 1920 1020 2060 1020 {}
N 2060 1020 2060 1200 {}
N 2120 240 2120 620 {}
N 2120 620 2120 1160 {}
N 2120 620 2270 620 {}
N 2270 620 2340 620 {}
N 2340 200 2340 620 {}
N 2340 620 2340 1200 {}
N 2340 200 2360 200 {}
N 2340 1200 2360 1200 {}
N 2270 620 2270 1160 {}
C {lab_pin.sym} 2120 620 0 0 {name=lz22 lab=o2}
N 2420 240 2420 640 {}
N 2420 640 2420 1160 {}
N 2420 640 2620 640 {}
C {opin.sym} 2620 640 0 0 {name=pz23 lab=out}
N 1410 700 1410 820 {}
N 1410 820 1410 940 {}
N 150 820 1410 820 {}
C {ipin.sym} 150 820 0 0 {name=pz24 lab=inp}
N 1560 620 1560 700 {}
N 1560 700 1560 940 {}
N 150 620 1560 620 {}
C {ipin.sym} 150 620 0 0 {name=pz25 lab=inn}
N 150 1560 360 1560 {}
C {ipin.sym} 150 1560 0 0 {name=pz26 lab=EN}
N 440 1560 660 1560 {}
C {lab_pin.sym} 440 1560 0 0 {name=lz27 lab=ENB}
N 740 1560 820 1560 {}
C {lab_pin.sym} 820 1560 0 0 {name=lz28 lab=ENbuf}
C {lab_pin.sym} 960 1200 0 0 {name=lz29 lab=ENB}
C {lab_pin.sym} 1110 200 0 0 {name=lz30 lab=ENbuf}
C {lab_pin.sym} 2210 1200 0 0 {name=lz31 lab=ENB}
C {lab_pin.sym} 210 700 0 0 {name=lz32 lab=ENbuf}
T {* bias generation} 190 -120 0 0 0.4 0.4 {}
T {* rail-to-rail input pairs} 1240 -120 0 0 0.4 0.4 {}
T {* fold + cascode + mirror} 1690 -120 0 0 0.4 0.4 {}
T {* gain stage} 2040 -120 0 0 0.4 0.4 {}
T {* output} 2340 -120 0 0 0.4 0.4 {}
T {* EN buffer (PDK INV cells)} 340 1440 0 0 0.4 0.4 {}
