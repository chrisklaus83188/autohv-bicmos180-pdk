v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {AutoHV comparators (comparators_all.lib) - every cell.  Power by text: VPWR=vdd, VGND=0.  Ports: inp inn out vdd vss nb.} -120 -70 0 0 0.4 0.4 {layer=4}
C {comparators/CMP_NIN_1V8.sym} 0 20 0 0 {name=CMP_NIN_1V8}
C {comparators/CMP_NIN_3V3.sym} 230 20 0 0 {name=CMP_NIN_3V3}
C {comparators/CMP_NIN_5V0.sym} 460 20 0 0 {name=CMP_NIN_5V0}
C {comparators/CMP_PIN_1V8.sym} 0 170 0 0 {name=CMP_PIN_1V8}
C {comparators/CMP_PIN_3V3.sym} 230 170 0 0 {name=CMP_PIN_3V3}
C {comparators/CMP_PIN_5V0.sym} 460 170 0 0 {name=CMP_PIN_5V0}
C {comparators/CMP_RR_1V8.sym} 0 320 0 0 {name=CMP_RR_1V8}
C {comparators/CMP_RR_3V3.sym} 230 320 0 0 {name=CMP_RR_3V3}
C {comparators/CMP_RR_5V0.sym} 460 320 0 0 {name=CMP_RR_5V0}
T {Include helpers (drive net 'vdd', bias nb e.g. Ib vdd nb 5u):} -120 450 0 0 0.3 0.3 {layer=4}
C {autohv_lib.sym} -120 480 0 0 {name=AUTOHV CASE=0}
C {cmp_lib.sym} 200 480 0 0 {name=CMPLIB}
