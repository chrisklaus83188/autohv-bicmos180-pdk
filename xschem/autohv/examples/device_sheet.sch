v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {AutoHV_BiCMOS180 - device sheet (all 40 devices + PWL sources, nothing wired)} -10 -110 0 0 0.5 0.5 {layer=4}
T {Reference palette: copy any instance into a testbench. Params are editable per instance (press q).} -10 -86 0 0 0.28 0.28 {}
T {LV NMOS   (d g s b)  -  W L M MM_SIGMA} -10 -60 0 0 0.3 0.3 {layer=8}
C {autohv/NMOS12.sym} 0 0 0 0 {name=NMOS12 W=10u L=1u M=1 MM_SIGMA=0}
C {autohv/NMOS18.sym} 150 0 0 0 {name=NMOS18 W=10u L=1u M=1 MM_SIGMA=0}
C {autohv/NMOS33.sym} 300 0 0 0 {name=NMOS33 W=10u L=1u M=1 MM_SIGMA=0}
C {autohv/NMOS50.sym} 450 0 0 0 {name=NMOS50 W=10u L=1u M=1 MM_SIGMA=0}
T {LV PMOS   (d g s b)} -10 120 0 0 0.3 0.3 {layer=8}
C {autohv/PMOS12.sym} 0 180 0 0 {name=PMOS12 W=10u L=1u M=1 MM_SIGMA=0}
C {autohv/PMOS18.sym} 150 180 0 0 {name=PMOS18 W=10u L=1u M=1 MM_SIGMA=0}
C {autohv/PMOS33.sym} 300 180 0 0 {name=PMOS33 W=10u L=1u M=1 MM_SIGMA=0}
C {autohv/PMOS50.sym} 450 180 0 0 {name=PMOS50 W=10u L=1u M=1 MM_SIGMA=0}
T {N-LDMOS   (d g s)  -  W M MM_SIGMA} -10 300 0 0 0.3 0.3 {layer=8}
C {autohv/NDMOS20.sym} 0 360 0 0 {name=NDMOS20 W=10u M=1 MM_SIGMA=0}
C {autohv/NDMOS40.sym} 150 360 0 0 {name=NDMOS40 W=10u M=1 MM_SIGMA=0}
C {autohv/NDMOS60.sym} 300 360 0 0 {name=NDMOS60 W=10u M=1 MM_SIGMA=0}
C {autohv/NDMOS80.sym} 450 360 0 0 {name=NDMOS80 W=10u M=1 MM_SIGMA=0}
C {autohv/NDMOS120.sym} 600 360 0 0 {name=NDMOS120 W=10u M=1 MM_SIGMA=0}
C {autohv/DNMOS20.sym} 750 360 0 0 {name=DNMOS20 W=10u M=1 MM_SIGMA=0}
T {P-LDMOS   (d g s)} -10 480 0 0 0.3 0.3 {layer=8}
C {autohv/PDMOS20.sym} 0 540 0 0 {name=PDMOS20 W=10u M=1 MM_SIGMA=0}
C {autohv/PDMOS40.sym} 150 540 0 0 {name=PDMOS40 W=10u M=1 MM_SIGMA=0}
C {autohv/PDMOS60.sym} 300 540 0 0 {name=PDMOS60 W=10u M=1 MM_SIGMA=0}
C {autohv/PDMOS80.sym} 450 540 0 0 {name=PDMOS80 W=10u M=1 MM_SIGMA=0}
C {autohv/PDMOS120.sym} 600 540 0 0 {name=PDMOS120 W=10u M=1 MM_SIGMA=0}
T {LDMOS 200V  (d g s)  -  W L M MM_SIGMA} -10 660 0 0 0.3 0.3 {layer=8}
C {autohv/NDMOS200.sym} 0 720 0 0 {name=NDMOS200 W=10u L=8u M=1 MM_SIGMA=0}
C {autohv/PDMOS200.sym} 150 720 0 0 {name=PDMOS200 W=10u L=8u M=1 MM_SIGMA=0}
T {BJT   (c b e)  -  AREA MM_SIGMA} -10 840 0 0 0.3 0.3 {layer=8}
C {autohv/NPN_LV.sym} 0 900 0 0 {name=NPN_LV AREA=1 MM_SIGMA=0}
C {autohv/NPN_HV.sym} 150 900 0 0 {name=NPN_HV AREA=1 MM_SIGMA=0}
C {autohv/PNP_LAT.sym} 300 900 0 0 {name=PNP_LAT AREA=1 MM_SIGMA=0}
C {autohv/PNP_HV.sym} 450 900 0 0 {name=PNP_HV AREA=1 MM_SIGMA=0}
T {Diodes / Zeners   (a c)  -  AREA MM_SIGMA} -10 1020 0 0 0.3 0.3 {layer=8}
C {autohv/DIO_PN.sym} 0 1080 0 0 {name=DIO_PN AREA=1 MM_SIGMA=0}
C {autohv/DIO_FAST.sym} 150 1080 0 0 {name=DIO_FAST AREA=1 MM_SIGMA=0}
C {autohv/DIO_SCH.sym} 300 1080 0 0 {name=DIO_SCH AREA=1 MM_SIGMA=0}
C {autohv/DZ_5V6.sym} 450 1080 0 0 {name=DZ_5V6 AREA=1 MM_SIGMA=0}
C {autohv/DZ_12.sym} 600 1080 0 0 {name=DZ_12 AREA=1 MM_SIGMA=0}
C {autohv/DZ_24.sym} 750 1080 0 0 {name=DZ_24 AREA=1 MM_SIGMA=0}
T {Resistors   (p n)  -  L W MM_SIGMA} -10 1200 0 0 0.3 0.3 {layer=8}
C {autohv/RPOLY_HI.sym} 0 1260 0 0 {name=RPOLY_HI L=100u W=10u MM_SIGMA=0}
C {autohv/RPOLY_LO.sym} 150 1260 0 0 {name=RPOLY_LO L=100u W=10u MM_SIGMA=0}
C {autohv/RNWELL.sym} 300 1260 0 0 {name=RNWELL L=100u W=10u MM_SIGMA=0}
C {autohv/RNPLUS.sym} 450 1260 0 0 {name=RNPLUS L=100u W=10u MM_SIGMA=0}
C {autohv/RPPLUS.sym} 600 1260 0 0 {name=RPPLUS L=100u W=10u MM_SIGMA=0}
T {Capacitors   (p n)  -  L W MM_SIGMA} -10 1380 0 0 0.3 0.3 {layer=8}
C {autohv/CMIM_STD.sym} 0 1440 0 0 {name=CMIM_STD L=100u W=100u MM_SIGMA=0}
C {autohv/CMIM_HI.sym} 150 1440 0 0 {name=CMIM_HI L=100u W=100u MM_SIGMA=0}
C {autohv/CMOM.sym} 300 1440 0 0 {name=CMOM L=100u W=100u MM_SIGMA=0}
C {autohv/CFRINGE.sym} 450 1440 0 0 {name=CFRINGE L=100u W=100u MM_SIGMA=0}
T {PIECEWISE-LINEAR SOURCES} -10 1570 0 0 0.4 0.4 {layer=4}
T {Build a testbench stimulus with a plain vsource/isource whose value is a pwl(...) list, or use the dedicated controlled-PWL symbols.} -10 1594 0 0 0.26 0.26 {}
C {vsource.sym} 0 1640 0 0 {name=VPWL1 value="pwl(0 0 10n 0 11n 1.8 100n 1.8 101n 0)"}
T {time-PWL voltage} 18 1606 0 0 0.26 0.26 {layer=8}
T {vsource, value=} 18 1628 0 0 0.22 0.22 {}
T {pwl(t0 v0 t1 v1 ...)} 18 1646 0 0 0.22 0.22 {}
C {isource.sym} 220 1640 0 0 {name=IPWL1 value="pwl(0 0 1u 0 1.001u 100u 5u 100u)"}
T {time-PWL current} 238 1606 0 0 0.26 0.26 {layer=8}
T {isource, value=} 238 1628 0 0 0.22 0.22 {}
T {pwl(t0 i0 t1 i1 ...)} 238 1646 0 0 0.22 0.22 {}
C {vsource_pwl.sym} 470 1640 0 0 {name=EPWL1 TABLE="0 0 1 1.8 2 1.8"}
T {vsource_pwl.sym} 490 1596 0 0 0.26 0.26 {layer=8}
T {controlled pwl(1):} 490 1616 0 0 0.22 0.22 {}
T {out = pwl of V(cp,cm)} 490 1634 0 0 0.22 0.22 {}
T {TABLE = in0 out0 in1 out1 ...} 490 1652 0 0 0.22 0.22 {}
C {isource_pwl.sym} 740 1640 0 0 {name=GPWL1 TABLE="0 0 1 1m 2 1m"}
T {isource_pwl.sym} 760 1596 0 0 0.26 0.26 {layer=8}
T {controlled pwl(1) current} 760 1616 0 0 0.22 0.22 {}
