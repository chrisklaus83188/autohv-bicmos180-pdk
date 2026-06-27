v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 840 -160 840 -110 {lab=#net1}
N 90 -40 90 -10 {lab=#net2}
N 170 -80 170 -10 {lab=#net2}
N 140 -80 170 -80 {lab=#net2}
N 500 -80 800 -80 {lab=#net2}
N 90 -180 90 -110 {lab=VIN}
N -200 -180 90 -180 {lab=VIN}
N 135 -80 140 -80 {lab=#net2}
N 90 -10 170 -10 {lab=#net2}
N 840 -410 840 -320 {lab=CP}
N 130 -410 840 -410 {lab=CP}
N 840 150 840 175 {lab=#net3}
N 765 150 840 150 {lab=#net3}
N 765 150 765 215 {lab=#net3}
N 765 215 795 215 {lab=#net3}
N 840 -40 840 150 {lab=#net3}
N 170 -80 500 -80 {lab=#net2}
N -200 -410 130 -410 {lab=CP}
N 580 -180 580 170 {lab=VIN}
N 210 -180 580 -180 {lab=VIN}
N 90 -180 210 -180 {lab=VIN}
N 630 215 765 215 {lab=#net3}
N 625 215 630 215 {lab=#net3}
N 580 170 580 175 {lab=VIN}
N 580 475 580 495 {lab=#net4}
N 515 475 580 475 {lab=#net4}
N 515 475 515 530 {lab=#net4}
N 515 530 535 530 {lab=#net4}
N 580 440 580 475 {lab=#net4}
N 580 245 580 280 {lab=#net5}
N 840 250 840 285 {lab=#net6}
N 840 245 840 250 {lab=#net6}
N 580 600 840 600 {lab=#net7}
N 580 560 580 600 {lab=#net7}
N 580 530 580 560 {lab=#net7}
N 575 530 580 530 {lab=#net7}
N 840 300 840 320 {lab=#net6}
N 775 300 840 300 {lab=#net6}
N 775 300 775 355 {lab=#net6}
N 775 355 795 355 {lab=#net6}
N 840 285 840 320 {lab=#net6}
N 835 355 840 355 {lab=#net8}
N 840 355 840 385 {lab=#net8}
N 840 385 840 410 {lab=#net8}
N 840 570 840 600 {lab=#net7}
N 195 475 195 495 {lab=#net9}
N 240 530 260 530 {lab=#net4}
N 195 440 195 475 {lab=#net9}
N 195 530 195 560 {lab=#net7}
N 195 530 200 530 {lab=#net7}
N 25 530 45 530 {lab=xxx}
N 90 530 90 560 {lab=#net7}
N 85 530 90 530 {lab=#net7}
N 270 600 580 600 {lab=#net7}
N 195 560 195 600 {lab=#net7}
N 90 560 90 600 {lab=#net7}
N 90 600 270 600 {lab=#net7}
N 90 -10 90 175 {lab=#net2}
N 90 245 90 495 {lab=#net9}
N -190 560 -190 600 {lab=#net7}
N -190 530 -185 530 {lab=#net7}
N -190 530 -190 560 {lab=#net7}
N -190 475 -190 495 {lab=xxx}
N -190 475 -135 475 {lab=xxx}
N -135 475 -130 475 {lab=xxx}
N -130 475 -130 530 {lab=xxx}
N 260 530 515 530 {lab=#net4}
N 195 600 270 600 {lab=#net7}
N 90 440 195 440 {lab=#net9}
N -145 530 25 530 {lab=xxx}
N -190 600 90 600 {lab=#net7}
N -190 400 -190 475 {lab=xxx}
C {designs/resistor_string.sym} 840 -240 0 0 {name=x1}
C {autohv/PDMOS200.sym} 105 -80 2 0 {name=M1 W=10u L=8u M=1 MM_SIGMA=0 spiceprefix=X}
C {autohv/PDMOS200.sym} 825 -80 2 1 {name=M2 W=10u L=8u M=1 MM_SIGMA=0 spiceprefix=X}
C {noconn.sym} 890 -210 2 0 {name=l1}
C {noconn.sym} 890 -240 2 0 {name=l2}
C {noconn.sym} 890 -270 2 0 {name=l3}
C {iopin.sym} -200 -410 0 1 {name=p1 lab=CP}
C {iopin.sym} -200 -180 0 1 {name=p2 lab=VIN}
C {autohv/NDMOS200.sym} 825 215 0 0 {name=M3 W=10u L=8u M=1 MM_SIGMA=0 spiceprefix=X}
C {designs/resistor_string.sym} 840 490 0 0 {name=LS_SNS[2:0]}
C {autohv/NDMOS200.sym} 75 215 0 0 {name=M4 W=10u L=8u M=1 MM_SIGMA=0 spiceprefix=X}
C {autohv/NDMOS200.sym} 595 215 0 1 {name=M5 W=10u L=8u M=1 MM_SIGMA=0 spiceprefix=X}
C {designs/resistor_string.sym} 580 360 0 0 {name=LS_SNS1[2:0]}
C {noconn.sym} 630 330 2 0 {name=l4}
C {noconn.sym} 630 360 2 0 {name=l5}
C {noconn.sym} 630 390 2 0 {name=l6}
C {autohv/NMOS50.sym} 565 530 0 0 {name=M6 W=10u L=1u M=1 MM_SIGMA=0 spiceprefix=X}
C {autohv/NMOS50.sym} 825 355 0 0 {name=M8 W=10u L=1u M=1 MM_SIGMA=0 spiceprefix=X}
C {autohv/NMOS50.sym} 210 530 0 1 {name=M7 W=10u L=1u M=1 MM_SIGMA=0 spiceprefix=X}
C {autohv/NMOS50.sym} 75 530 0 0 {name=M9 W=10u L=1u M=1 MM_SIGMA=0 spiceprefix=X}
C {autohv/NMOS50.sym} -175 530 0 1 {name=M10 W=10u L=1u M=1 MM_SIGMA=0 spiceprefix=X}
C {ipin.sym} -190 400 1 0 {name=p3 lab=IBIAS}
