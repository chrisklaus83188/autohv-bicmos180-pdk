v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {PHI_3V3} 620 -280 0 0 0.6 0.6 {}
T {body: circuits/delay_pulse_design/cells.lib (authority) | delay core (out=dco) + inverter + 2-input gate + out inverter} 620 -220 0 0 0.3 0.3 {}
N 120 100 2760 100 {}
C {iopin.sym} 120 100 0 0 {name=pz1 lab=vdd sim_pinnumber=3}
N 120 860 2760 860 {}
C {iopin.sym} 120 860 0 0 {name=pz2 lab=gnd sim_pinnumber=4}
C {autohv/PMOS33.sym} 280 280 2 1 {name=I1 model=PMOS33 W=0.95u L=0.35u}
T {I1} 220 170 0 0 0.28 0.28 {}
N 300 280 300 240 {}
C {autohv/NMOS33.sym} 280 720 0 0 {name=I2 model=NMOS33 W=0.4u L=0.35u}
T {I2} 220 610 0 0 0.28 0.28 {}
N 300 720 300 760 {}
N 300 100 300 240 {}
N 300 760 300 860 {}
N 300 320 300 500 {}
N 300 500 300 680 {}
C {lab_pin.sym} 300 500 0 0 {name=lz3 lab=nIN}
N 240 280 240 500 {}
N 240 500 240 720 {}
N 120 500 240 500 {}
C {ipin.sym} 120 500 0 0 {name=pz4 lab=in sim_pinnumber=1}
C {autohv/RPOLY_HI.sym} 560 500 3 0 {name=R L=53.7500u W=0.5u}
T {R} 590 460 0 0 0.22 0.22 {}
N 300 500 530 500 {}
N 590 500 700 500 {}
N 700 500 780 500 {}
N 780 500 940 500 {}
N 940 500 1120 500 {}
C {lab_pin.sym} 700 500 0 0 {name=lz5 lab=nC}
N 1120 260 1120 420 {}
N 1120 420 1120 500 {}
N 1120 500 1120 580 {}
N 1120 580 1120 740 {}
C {autohv/PMOS33.sym} 760 200 2 1 {name=BP model=PMOS33 W=0.8u L=0.35u}
T {BP} 700 90 0 0 0.28 0.28 {}
N 780 200 780 160 {}
N 780 100 780 160 {}
N 780 240 780 500 {}
C {lab_pin.sym} 720 200 0 0 {name=lz6 lab=in}
C {autohv/CMIM_HI.sym} 940 640 0 0 {name=C L=5.3600u W=5.3600u}
T {C} 970 600 0 0 0.22 0.22 {}
N 940 500 940 610 {}
N 940 670 940 860 {}
C {autohv/PMOS33.sym} 1160 260 2 1 {name=S3 model=PMOS33 W=0.95u L=0.35u}
T {S3} 1100 150 0 0 0.28 0.28 {}
N 1180 260 1180 220 {}
C {autohv/PMOS33.sym} 1160 420 2 1 {name=S4 model=PMOS33 W=0.95u L=0.35u}
T {S4} 1100 310 0 0 0.28 0.28 {}
C {lab_pin.sym} 1180 420 0 0 {name=lz7 lab=vdd}
C {autohv/NMOS33.sym} 1160 580 0 0 {name=S2 model=NMOS33 W=0.4u L=0.35u}
T {S2} 1100 470 0 0 0.28 0.28 {}
C {lab_pin.sym} 1180 580 0 0 {name=lz8 lab=gnd}
C {autohv/NMOS33.sym} 1160 740 0 0 {name=S1 model=NMOS33 W=0.4u L=0.35u}
T {S1} 1100 630 0 0 0.28 0.28 {}
N 1180 740 1180 780 {}
N 1180 100 1180 220 {}
N 1180 300 1180 340 {}
N 1180 340 1180 380 {}
N 1180 460 1180 500 {}
N 1180 500 1180 540 {}
N 1180 620 1180 660 {}
N 1180 660 1180 700 {}
N 1180 780 1180 860 {}
C {lab_pin.sym} 1180 300 0 0 {name=lz9 lab=s2}
C {lab_pin.sym} 1180 620 0 0 {name=lz10 lab=s1}
C {autohv/PMOS33.sym} 1360 420 2 0 {name=S6 model=PMOS33 W=0.95u L=0.35u}
T {S6} 1300 310 0 0 0.28 0.28 {}
C {lab_pin.sym} 1340 420 0 0 {name=lz11 lab=vdd}
C {autohv/NMOS33.sym} 1520 580 0 1 {name=S5 model=NMOS33 W=0.4u L=0.35u}
T {S5} 1460 470 0 0 0.28 0.28 {}
C {lab_pin.sym} 1500 580 0 0 {name=lz12 lab=gnd}
N 1340 460 1340 860 {}
N 1500 100 1500 540 {}
N 1340 340 1340 380 {}
N 1180 340 1340 340 {}
N 1500 620 1500 660 {}
N 1180 660 1500 660 {}
N 1180 500 1400 500 {}
N 1400 500 1560 500 {}
N 1560 500 1660 500 {}
N 1400 420 1400 500 {}
N 1560 500 1560 580 {}
T {* input inverter} 200 -40 0 0 0.4 0.4 {}
T {* RC delay (R + MIM C) + bypass} 460 -40 0 0 0.4 0.4 {}
T {* Schmitt trigger + hysteresis} 1080 -40 0 0 0.4 0.4 {}
C {lab_pin.sym} 1660 500 0 0 {name=lz13 lab=dco}
C {autohv/PMOS33.sym} 1840 280 2 1 {name=PI1 model=PMOS33 W=0.95u L=0.35u}
T {PI1} 1780 170 0 0 0.28 0.28 {}
N 1860 280 1860 240 {}
C {autohv/NMOS33.sym} 1840 720 0 0 {name=PI2 model=NMOS33 W=0.4u L=0.35u}
T {PI2} 1780 610 0 0 0.28 0.28 {}
N 1860 720 1860 760 {}
N 1860 100 1860 240 {}
N 1860 760 1860 860 {}
N 1860 320 1860 500 {}
N 1860 500 1860 680 {}
N 1800 280 1800 500 {}
N 1800 500 1800 720 {}
C {lab_pin.sym} 1860 500 0 0 {name=lz14 lab=dbar}
N 1660 500 1800 500 {}
C {autohv/PMOS33.sym} 2160 280 2 1 {name=G1 model=PMOS33 W=0.95u L=0.35u}
T {G1} 2100 170 0 0 0.28 0.28 {}
N 2180 280 2180 240 {}
C {autohv/PMOS33.sym} 2360 280 2 1 {name=G2 model=PMOS33 W=0.95u L=0.35u}
T {G2} 2300 170 0 0 0.28 0.28 {}
N 2380 280 2380 240 {}
C {autohv/NMOS33.sym} 2160 560 0 0 {name=G3 model=NMOS33 W=0.4u L=0.35u}
T {G3} 2100 450 0 0 0.28 0.28 {}
C {lab_pin.sym} 2180 560 0 0 {name=lz15 lab=gnd}
C {autohv/NMOS33.sym} 2160 740 0 0 {name=G4 model=NMOS33 W=0.4u L=0.35u}
T {G4} 2100 630 0 0 0.28 0.28 {}
N 2180 740 2180 780 {}
N 2180 100 2180 240 {}
N 2380 100 2380 240 {}
N 2180 320 2380 320 {}
N 2180 320 2180 500 {}
N 2180 500 2180 520 {}
N 2180 600 2180 700 {}
C {lab_pin.sym} 2180 650 0 0 {name=lz16 lab=q}
N 2180 780 2180 860 {}
N 2120 280 2120 560 {}
C {lab_pin.sym} 2120 420 0 0 {name=lz17 lab=in}
N 1860 500 2000 500 {}
N 2000 180 2000 500 {}
N 2000 500 2000 740 {}
N 2000 180 2320 180 {}
N 2320 180 2320 280 {}
N 2000 740 2120 740 {}
C {lab_pin.sym} 2180 500 0 0 {name=lz18 lab=nnd}
C {autohv/PMOS33.sym} 2560 280 2 1 {name=O1 model=PMOS33 W=0.95u L=0.35u}
T {O1} 2500 170 0 0 0.28 0.28 {}
N 2580 280 2580 240 {}
C {autohv/NMOS33.sym} 2560 720 0 0 {name=O2 model=NMOS33 W=0.4u L=0.35u}
T {O2} 2500 610 0 0 0.28 0.28 {}
N 2580 720 2580 760 {}
N 2580 100 2580 240 {}
N 2580 760 2580 860 {}
N 2580 320 2580 500 {}
N 2580 500 2580 680 {}
N 2520 280 2520 500 {}
N 2520 500 2520 720 {}
C {lab_pin.sym} 2580 500 0 0 {name=lz19 lab=out}
N 2180 500 2520 500 {}
N 2580 500 2680 500 {}
C {opin.sym} 2680 500 0 0 {name=pz20 lab=out sim_pinnumber=2}
T {* inverter (dco->dbar)} 1780 -40 0 0 0.4 0.4 {}
T {* 2-input gate (in | dbar)} 2100 -40 0 0 0.4 0.4 {}
T {* output inverter} 2520 -40 0 0 0.4 0.4 {}
