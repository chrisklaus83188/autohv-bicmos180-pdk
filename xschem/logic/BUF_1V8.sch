v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {BUF_1V8 - implementation generated from circuits/async_logic_design/cells.lib. Do not hand-edit; regenerate with xschem/gen_logic_schematics.py} -120 -330 0 0 0.3 0.3 {layer=4}
N -120 -240 320 -240 {}
N -120 240 320 240 {}
C {lab_pin.sym} -120 -240 0 0 {name=lvdd lab=vdd}
C {lab_pin.sym} -120 240 0 0 {name=lgnd lab=gnd}
C {autohv/PMOS18.sym} 0 -140 2 1 {name=MP1 W=2.656u L=0.18u M=1 MM_SIGMA=0}
C {lab_pin.sym} 20 -100 0 0 {name=lP1d lab=mid}
C {lab_pin.sym} -40 -140 0 0 {name=lP1g lab=in}
N 20 -180 20 -240 {}
C {lab_pin.sym} 20 -140 0 0 {name=lP1b lab=vdd}
C {autohv/PMOS18.sym} 200 -140 2 1 {name=MP2 W=7.968u L=0.18u M=1 MM_SIGMA=0}
C {lab_pin.sym} 220 -100 0 0 {name=lP2d lab=out}
C {lab_pin.sym} 160 -140 0 0 {name=lP2g lab=mid}
N 220 -180 220 -240 {}
C {lab_pin.sym} 220 -140 0 0 {name=lP2b lab=vdd}
C {autohv/NMOS18.sym} 0 140 0 0 {name=MN1 W=0.5717u L=0.18u M=1 MM_SIGMA=0}
C {lab_pin.sym} 20 100 0 0 {name=lN1d lab=mid}
C {lab_pin.sym} -40 140 0 0 {name=lN1g lab=in}
N 20 180 20 240 {}
C {lab_pin.sym} 20 140 0 0 {name=lN1b lab=gnd}
C {autohv/NMOS18.sym} 200 140 0 0 {name=MN2 W=1.7151u L=0.18u M=1 MM_SIGMA=0}
C {lab_pin.sym} 220 100 0 0 {name=lN2d lab=out}
C {lab_pin.sym} 160 140 0 0 {name=lN2g lab=mid}
N 220 180 220 240 {}
C {lab_pin.sym} 220 140 0 0 {name=lN2b lab=gnd}
C {ipin.sym} -220 0 0 0 {name=pi0 lab=in}
C {opin.sym} 420 0 0 0 {name=po lab=out}
