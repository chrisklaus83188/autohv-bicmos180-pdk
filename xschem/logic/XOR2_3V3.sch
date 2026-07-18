v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {XOR2_3V3 - implementation generated from circuits/async_logic_design/cells.lib. Do not hand-edit; regenerate with xschem/gen_logic_schematics.py} -120 -330 0 0 0.3 0.3 {layer=4}
N -120 -240 1120 -240 {}
N -120 240 1120 240 {}
C {lab_pin.sym} -120 -240 0 0 {name=lvdd lab=vdd}
C {lab_pin.sym} -120 240 0 0 {name=lgnd lab=gnd}
C {autohv/PMOS33.sym} 0 -140 2 1 {name=MP1 W=0.9811u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 20 -100 0 0 {name=lP1d lab=abar}
C {lab_pin.sym} -40 -140 0 0 {name=lP1g lab=a}
N 20 -180 20 -240 {}
C {lab_pin.sym} 20 -140 0 0 {name=lP1b lab=vdd}
C {autohv/PMOS33.sym} 200 -140 2 1 {name=MP2 W=0.9811u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 220 -100 0 0 {name=lP2d lab=bbar}
C {lab_pin.sym} 160 -140 0 0 {name=lP2g lab=b}
N 220 -180 220 -240 {}
C {lab_pin.sym} 220 -140 0 0 {name=lP2b lab=vdd}
C {autohv/PMOS33.sym} 400 -140 2 1 {name=MP3 W=1.2367u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 420 -100 0 0 {name=lP3d lab=out}
C {lab_pin.sym} 360 -140 0 0 {name=lP3g lab=abar}
C {lab_pin.sym} 420 -180 0 0 {name=lP3s lab=k1}
C {lab_pin.sym} 420 -140 0 0 {name=lP3b lab=vdd}
C {autohv/PMOS33.sym} 600 -140 2 1 {name=MP4 W=1.2367u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 620 -100 0 0 {name=lP4d lab=k1}
C {lab_pin.sym} 560 -140 0 0 {name=lP4g lab=b}
N 620 -180 620 -240 {}
C {lab_pin.sym} 620 -140 0 0 {name=lP4b lab=vdd}
C {autohv/PMOS33.sym} 800 -140 2 1 {name=MP5 W=1.2367u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 820 -100 0 0 {name=lP5d lab=out}
C {lab_pin.sym} 760 -140 0 0 {name=lP5g lab=a}
C {lab_pin.sym} 820 -180 0 0 {name=lP5s lab=k2}
C {lab_pin.sym} 820 -140 0 0 {name=lP5b lab=vdd}
C {autohv/PMOS33.sym} 1000 -140 2 1 {name=MP6 W=1.2367u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 1020 -100 0 0 {name=lP6d lab=k2}
C {lab_pin.sym} 960 -140 0 0 {name=lP6g lab=bbar}
N 1020 -180 1020 -240 {}
C {lab_pin.sym} 1020 -140 0 0 {name=lP6b lab=vdd}
C {autohv/NMOS33.sym} 0 140 0 0 {name=MN1 W=0.3u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 20 100 0 0 {name=lN1d lab=abar}
C {lab_pin.sym} -40 140 0 0 {name=lN1g lab=a}
N 20 180 20 240 {}
C {lab_pin.sym} 20 140 0 0 {name=lN1b lab=gnd}
C {autohv/NMOS33.sym} 200 140 0 0 {name=MN2 W=0.3u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 220 100 0 0 {name=lN2d lab=bbar}
C {lab_pin.sym} 160 140 0 0 {name=lN2g lab=b}
N 220 180 220 240 {}
C {lab_pin.sym} 220 140 0 0 {name=lN2b lab=gnd}
C {autohv/NMOS33.sym} 400 140 0 0 {name=MN3 W=0.3u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 420 100 0 0 {name=lN3d lab=out}
C {lab_pin.sym} 360 140 0 0 {name=lN3g lab=a}
C {lab_pin.sym} 420 180 0 0 {name=lN3s lab=m1}
C {lab_pin.sym} 420 140 0 0 {name=lN3b lab=gnd}
C {autohv/NMOS33.sym} 600 140 0 0 {name=MN4 W=0.3u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 620 100 0 0 {name=lN4d lab=m1}
C {lab_pin.sym} 560 140 0 0 {name=lN4g lab=b}
N 620 180 620 240 {}
C {lab_pin.sym} 620 140 0 0 {name=lN4b lab=gnd}
C {autohv/NMOS33.sym} 800 140 0 0 {name=MN5 W=0.3u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 820 100 0 0 {name=lN5d lab=out}
C {lab_pin.sym} 760 140 0 0 {name=lN5g lab=abar}
C {lab_pin.sym} 820 180 0 0 {name=lN5s lab=m2}
C {lab_pin.sym} 820 140 0 0 {name=lN5b lab=gnd}
C {autohv/NMOS33.sym} 1000 140 0 0 {name=MN6 W=0.3u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 1020 100 0 0 {name=lN6d lab=m2}
C {lab_pin.sym} 960 140 0 0 {name=lN6g lab=bbar}
N 1020 180 1020 240 {}
C {lab_pin.sym} 1020 140 0 0 {name=lN6b lab=gnd}
C {ipin.sym} -220 -40 0 0 {name=pi0 lab=a}
C {ipin.sym} -220 40 0 0 {name=pi1 lab=b}
C {opin.sym} 1220 0 0 0 {name=po lab=out}
