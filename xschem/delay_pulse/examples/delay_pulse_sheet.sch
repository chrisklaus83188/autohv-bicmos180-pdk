v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {AutoHV delay/pulse cells - every cell.  Power by text: VPWR=vdd, VGND=0.  Ports: in out vdd gnd.} -100 -60 0 0 0.4 0.4 {layer=4}
C {delay_pulse/DLYR_1V8.sym} 0 10 0 0 {name=DLYR_1V8}
C {delay_pulse/DLYR_3V3.sym} 190 10 0 0 {name=DLYR_3V3}
C {delay_pulse/DLYR_5V0.sym} 380 10 0 0 {name=DLYR_5V0}
C {delay_pulse/DLYF_1V8.sym} 0 150 0 0 {name=DLYF_1V8}
C {delay_pulse/DLYF_3V3.sym} 190 150 0 0 {name=DLYF_3V3}
C {delay_pulse/DLYF_5V0.sym} 380 150 0 0 {name=DLYF_5V0}
C {delay_pulse/PHI_1V8.sym} 0 290 0 0 {name=PHI_1V8}
C {delay_pulse/PHI_3V3.sym} 190 290 0 0 {name=PHI_3V3}
C {delay_pulse/PHI_5V0.sym} 380 290 0 0 {name=PHI_5V0}
C {delay_pulse/PLO_1V8.sym} 0 430 0 0 {name=PLO_1V8}
C {delay_pulse/PLO_3V3.sym} 190 430 0 0 {name=PLO_3V3}
C {delay_pulse/PLO_5V0.sym} 380 430 0 0 {name=PLO_5V0}
T {Include helpers (then drive net 'vdd'):} -100 560 0 0 0.3 0.3 {layer=4}
C {autohv_lib.sym} -100 590 0 0 {name=AUTOHV CASE=0}
C {dly_lib.sym} 150 590 0 0 {name=DLYLIB}
