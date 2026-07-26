v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 975 -585 1020 -585 {lab=off}
N 1020 -585 1035 -585 {lab=off}
N 860 -585 895 -585 {lab=on}
N 1115 -585 1170 -585 {lab=xxx}
C {autohv/NMOS50.sym} 2120 -715 0 0 {name=M1 W=10u L=1u M=1 MM_SIGMA=0 spiceprefix=X}
C {autohv/NMOS50.sym} 2300 -715 0 0 {name=M2 W=10u L=1u M=1 MM_SIGMA=0 spiceprefix=X}
C {autohv/NMOS50.sym} 2300 -580 0 0 {name=M3 W=10u L=1u M=1 MM_SIGMA=0 spiceprefix=X}
C {autohv/NMOS50.sym} 1635 -715 0 1 {name=M4 W=10u L=1u M=1 MM_SIGMA=0 spiceprefix=X}
C {autohv/NMOS50.sym} 1455 -715 0 1 {name=M5 W=10u L=1u M=1 MM_SIGMA=0 spiceprefix=X}
C {autohv/NMOS50.sym} 1455 -580 0 1 {name=M6 W=10u L=1u M=1 MM_SIGMA=0 spiceprefix=X}
C {logic/INV_5V0.sym} 935 -585 0 0 {name=U1 VPWR=VDD VGND=GND spiceprefix=x}
C {logic/INV_5V0.sym} 1075 -585 0 0 {name=U2 VPWR=VDD VGND=GND spiceprefix=x}
C {lab_wire.sym} 1020 -585 0 0 {name=p1 sig_type=std_logic lab=off}
C {ipin.sym} 860 -585 0 0 {name=p2 lab=on}
C {lab_wire.sym} 1160 -585 0 0 {name=p3 sig_type=std_logic lab=onb}
