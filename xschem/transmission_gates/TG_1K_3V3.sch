v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {TG_1K_3V3} 560 170 0 0 0.6 0.6 {}
T {~1 kohm at TT / 3.3 V / 27 C, worst case over the input level.} 560 220 0 0 0.3 0.3 {}
T {Wp/Wn = 2.5, L = 0.35 um. PVT envelope and input window: ../REPORT.md.} 560 255 0 0 0.3 0.3 {}
T {body: circuits/transmission_gates/cells.lib is the netlist authority. Do not hand-edit;} 560 300 0 0 0.28 0.28 {}
T {regenerate with circuits/transmission_gates/gen_cells.py.} 560 330 0 0 0.28 0.28 {}
N 120 100 1400 100 {}
C {lab_pin.sym} 120 100 0 0 {name=lvdd lab=vdd}
N 120 900 1400 900 {}
C {lab_pin.sym} 120 900 0 0 {name=lgnd lab=gnd}
C {iopin.sym} 120 500 0 0 {name=pa lab=a sim_pinnumber=1}
C {iopin.sym} 1400 500 0 0 {name=pb lab=b sim_pinnumber=2}
C {ipin.sym} 120 300 0 0 {name=pen lab=en sim_pinnumber=3}
C {autohv/PMOS33.sym} 400 240 2 1 {name=XINVP W=1.15u L=0.35u M=1}
C {lab_pin.sym} 420 280 0 0 {name=lXINVPd lab=enb}
C {lab_pin.sym} 360 240 0 0 {name=lXINVPg lab=en}
C {lab_pin.sym} 420 200 0 0 {name=lXINVPs lab=vdd}
C {lab_pin.sym} 420 240 0 0 {name=lXINVPb lab=vdd}
C {autohv/NMOS33.sym} 400 700 0 0 {name=XINVN W=0.46u L=0.35u M=1}
C {lab_pin.sym} 420 660 0 0 {name=lXINVNd lab=enb}
C {lab_pin.sym} 360 700 0 0 {name=lXINVNg lab=en}
C {lab_pin.sym} 420 740 0 0 {name=lXINVNs lab=gnd}
C {lab_pin.sym} 420 700 0 0 {name=lXINVNb lab=gnd}
C {autohv/NMOS33.sym} 1000 340 0 0 {name=XN W=4.6u L=0.35u M=1}
C {lab_pin.sym} 1020 300 0 0 {name=lXNd lab=b}
C {lab_pin.sym} 960 340 0 0 {name=lXNg lab=en}
C {lab_pin.sym} 1020 380 0 0 {name=lXNs lab=a}
C {lab_pin.sym} 1020 340 0 0 {name=lXNb lab=gnd}
C {autohv/PMOS33.sym} 1000 640 0 0 {name=XP W=11.5u L=0.35u M=1}
C {lab_pin.sym} 1020 600 0 0 {name=lXPd lab=b}
C {lab_pin.sym} 960 640 0 0 {name=lXPg lab=enb}
C {lab_pin.sym} 1020 680 0 0 {name=lXPs lab=a}
C {lab_pin.sym} 1020 640 0 0 {name=lXPb lab=vdd}
T {* control inverter: enb = !en} 200 470 0 0 0.4 0.4 {}
T {* pass pair: a <-> b} 790 470 0 0 0.4 0.4 {}
