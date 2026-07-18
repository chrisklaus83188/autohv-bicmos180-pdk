v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {AND2_3V3 - implementation generated from circuits/async_logic_design/cells.lib. Do not hand-edit; regenerate with xschem/gen_logic_schematics.py} -120 -330 0 0 0.3 0.3 {layer=4}
N -120 -240 520 -240 {}
N -120 240 520 240 {}
C {lab_pin.sym} -120 -240 0 0 {name=lvdd lab=vdd}
C {lab_pin.sym} -120 240 0 0 {name=lgnd lab=gnd}
C {autohv/PMOS33.sym} 0 -140 2 1 {name=MP1 W=1.3719u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 20 -100 0 0 {name=lP1d lab=nd}
C {lab_pin.sym} -40 -140 0 0 {name=lP1g lab=a}
N 20 -180 20 -240 {}
C {lab_pin.sym} 20 -140 0 0 {name=lP1b lab=vdd}
C {autohv/PMOS33.sym} 200 -140 2 1 {name=MP2 W=1.3719u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 220 -100 0 0 {name=lP2d lab=nd}
C {lab_pin.sym} 160 -140 0 0 {name=lP2g lab=b}
N 220 -180 220 -240 {}
C {lab_pin.sym} 220 -140 0 0 {name=lP2b lab=vdd}
C {autohv/PMOS33.sym} 400 -140 2 1 {name=MP3 W=2.1378u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 420 -100 0 0 {name=lP3d lab=out}
C {lab_pin.sym} 360 -140 0 0 {name=lP3g lab=nd}
N 420 -180 420 -240 {}
C {lab_pin.sym} 420 -140 0 0 {name=lP3b lab=vdd}
C {autohv/NMOS33.sym} 0 140 0 0 {name=MN1 W=1.4316u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 20 100 0 0 {name=lN1d lab=nd}
C {lab_pin.sym} -40 140 0 0 {name=lN1g lab=a}
C {lab_pin.sym} 20 180 0 0 {name=lN1s lab=n1}
C {lab_pin.sym} 20 140 0 0 {name=lN1b lab=gnd}
C {autohv/NMOS33.sym} 200 140 0 0 {name=MN2 W=1.4316u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 220 100 0 0 {name=lN2d lab=n1}
C {lab_pin.sym} 160 140 0 0 {name=lN2g lab=b}
N 220 180 220 240 {}
C {lab_pin.sym} 220 140 0 0 {name=lN2b lab=gnd}
C {autohv/NMOS33.sym} 400 140 0 0 {name=MN3 W=0.6537u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 420 100 0 0 {name=lN3d lab=out}
C {lab_pin.sym} 360 140 0 0 {name=lN3g lab=nd}
N 420 180 420 240 {}
C {lab_pin.sym} 420 140 0 0 {name=lN3b lab=gnd}
C {ipin.sym} -220 -40 0 0 {name=pi0 lab=a}
C {ipin.sym} -220 40 0 0 {name=pi1 lab=b}
C {opin.sym} 620 0 0 0 {name=po lab=out}
