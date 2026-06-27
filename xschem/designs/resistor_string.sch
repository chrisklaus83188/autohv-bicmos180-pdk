v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {resistor_string : 25x RPOLY_HI in series.  Taps: OV = after R5 (~80% of RP-RN), REG = after R13 (~48%), UV = after R20 (~20%).} -130 -135 0 0 0.3 0.3 {layer=4}
C {autohv/RPOLY_HI.sym} 0 0 0 0 {name=R1 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 80 0 0 {name=R2 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 160 0 0 {name=R3 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 240 0 0 {name=R4 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 320 0 0 {name=R5 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 400 0 0 {name=R6 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 480 0 0 {name=R7 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 560 0 0 {name=R8 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 640 0 0 {name=R9 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 720 0 0 {name=R10 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 800 0 0 {name=R11 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 880 0 0 {name=R12 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 960 0 0 {name=R13 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 1040 0 0 {name=R14 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 1120 0 0 {name=R15 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 1200 0 0 {name=R16 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 1280 0 0 {name=R17 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 1360 0 0 {name=R18 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 1440 0 0 {name=R19 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 1520 0 0 {name=R20 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 1600 0 0 {name=R21 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 1680 0 0 {name=R22 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 1760 0 0 {name=R23 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 1840 0 0 {name=R24 W=2u L=10u MM_SIGMA=0}
C {autohv/RPOLY_HI.sym} 0 1920 0 0 {name=R25 W=2u L=10u MM_SIGMA=0}
N 0 30 0 50 {}
N 0 110 0 130 {}
N 0 190 0 210 {}
N 0 270 0 290 {}
N 0 350 0 370 {}
N 0 430 0 450 {}
N 0 510 0 530 {}
N 0 590 0 610 {}
N 0 670 0 690 {}
N 0 750 0 770 {}
N 0 830 0 850 {}
N 0 910 0 930 {}
N 0 990 0 1010 {}
N 0 1070 0 1090 {}
N 0 1150 0 1170 {}
N 0 1230 0 1250 {}
N 0 1310 0 1330 {}
N 0 1390 0 1410 {}
N 0 1470 0 1490 {}
N 0 1550 0 1570 {}
N 0 1630 0 1650 {}
N 0 1710 0 1730 {}
N 0 1790 0 1810 {}
N 0 1870 0 1890 {}
N 0 -30 0 -90 {}
C {iopin.sym} 0 -90 0 0 {name=pRP lab=RP}
N 0 1950 0 2010 {}
C {iopin.sym} 0 2010 0 0 {name=pRN lab=RN}
N 0 350 200 350 {}
C {iopin.sym} 200 350 0 0 {name=pOV lab=OV}
N 0 990 200 990 {}
C {iopin.sym} 200 990 0 0 {name=pREG lab=REG}
N 0 1550 200 1550 {}
C {iopin.sym} 200 1550 0 0 {name=pUV lab=UV}
