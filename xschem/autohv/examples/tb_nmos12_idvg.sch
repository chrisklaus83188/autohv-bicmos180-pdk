v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
C {autohv/NMOS12.sym} 0 0 0 0 {name=M1 W=10u L=1u M=1 MM_SIGMA=0}
C {lab_pin.sym} 15 -35 0 0 {name=ld lab=D}
C {lab_pin.sym} -30 0 0 1 {name=lg lab=G}
C {gnd.sym} 15 30 0 0 {name=gs lab=0}
C {gnd.sym} 10 0 0 0 {name=gb lab=0}
C {autohv_lib.sym} 200 -120 0 0 {name=AUTOHV only_toplevel=true CASE=0}
C {code_shown.sym} 200 0 0 0 {name=STIM value="
vds D 0 dc 6
vgs G 0 dc 12
.dc vgs 0 12 1
.control
run
print -i(vds)
.endc
"}
