v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 700 -505 700 -435 {lab=OUT}
N 700 -585 700 -545 {lab=SRC}
N 700 -635 700 -585 {lab=SRC}
N 700 -395 700 -355 {lab=SNK}
N 700 -355 700 -305 {lab=SNK}
N 550 -395 640 -395 {lab=NG}
N 550 -545 640 -545 {lab=PG}
N 545 -635 700 -635 {lab=SRC}
N 545 -305 700 -305 {lab=SNK}
N 700 -470 765 -470 {lab=OUT}
C {autohv/NMOS50.sym} 680 -395 0 0 {name=M1 W=10u L=1u M=1 MM_SIGMA=0 spiceprefix=X}
C {autohv/PMOS50.sym} 680 -545 2 1 {name=M2 W=10u L=1u M=1 MM_SIGMA=0 spiceprefix=X}
C {ipin.sym} 550 -395 0 0 {name=p1 lab=NG}
C {ipin.sym} 550 -545 0 0 {name=p2 lab=PG}
C {iopin.sym} 545 -635 2 0 {name=p3 lab=SRC}
C {iopin.sym} 545 -305 2 0 {name=p5 lab=SNK}
C {iopin.sym} 765 -470 0 0 {name=p4 lab=OUT}
