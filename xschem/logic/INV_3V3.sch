v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {INV_3V3 - implementation generated from circuits/async_logic_design/cells.lib. Do not hand-edit; regenerate with xschem/gen_logic_schematics.py} -120 -330 0 0 0.3 0.3 {layer=4}
N -120 -240 120 -240 {}
N -120 240 120 240 {}
C {lab_pin.sym} -120 -240 0 0 {name=lvdd lab=vdd}
C {lab_pin.sym} -120 240 0 0 {name=lgnd lab=gnd}
C {autohv/PMOS33.sym} 0 -140 2 1 {name=MP1 W=2.1378u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 20 -100 0 0 {name=lP1d lab=out}
C {lab_pin.sym} -40 -140 0 0 {name=lP1g lab=in}
N 20 -180 20 -240 {}
C {lab_pin.sym} 20 -140 0 0 {name=lP1b lab=vdd}
C {autohv/NMOS33.sym} 0 140 0 0 {name=MN1 W=0.6537u L=0.35u M=1 MM_SIGMA=0}
C {lab_pin.sym} 20 100 0 0 {name=lN1d lab=out}
C {lab_pin.sym} -40 140 0 0 {name=lN1g lab=in}
N 20 180 20 240 {}
C {lab_pin.sym} 20 140 0 0 {name=lN1b lab=gnd}
C {ipin.sym} -220 0 0 0 {name=pi0 lab=in}
C {opin.sym} 220 0 0 0 {name=po lab=out}
