v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {AutoHV transmission gates (circuits/transmission_gates/cells.lib) - every cell.  Power by text: VPWR=vdd, VGND=0.} -140 -120 0 0 0.4 0.4 {layer=4}
T {TG_*  ports: a b en vdd gnd   (bodies tied to the rails)        TGB_*  ports: a b en bn bp vdd gnd   (bodies on pins)} -140 -80 0 0 0.35 0.35 {layer=4}
T {bodies to the rails} -140 -20 0 0 0.35 0.35 {layer=8}
C {transmission_gates/TG_1K_1V8.sym} 140 80 0 0 {name=TG_1K_1V8}
C {transmission_gates/TG_100R_1V8.sym} 420 80 0 0 {name=TG_100R_1V8}
C {transmission_gates/TG_10R_1V8.sym} 700 80 0 0 {name=TG_10R_1V8}
C {transmission_gates/TG_1K_3V3.sym} 140 280 0 0 {name=TG_1K_3V3}
C {transmission_gates/TG_100R_3V3.sym} 420 280 0 0 {name=TG_100R_3V3}
C {transmission_gates/TG_10R_3V3.sym} 700 280 0 0 {name=TG_10R_3V3}
C {transmission_gates/TG_1K_5V0.sym} 140 480 0 0 {name=TG_1K_5V0}
C {transmission_gates/TG_100R_5V0.sym} 420 480 0 0 {name=TG_100R_5V0}
C {transmission_gates/TG_10R_5V0.sym} 700 480 0 0 {name=TG_10R_5V0}
T {bodies on pins bn / bp} 900 -20 0 0 0.35 0.35 {layer=8}
C {transmission_gates/TGB_1K_1V8.sym} 1180 80 0 0 {name=TGB_1K_1V8}
C {transmission_gates/TGB_100R_1V8.sym} 1460 80 0 0 {name=TGB_100R_1V8}
C {transmission_gates/TGB_10R_1V8.sym} 1740 80 0 0 {name=TGB_10R_1V8}
C {transmission_gates/TGB_1K_3V3.sym} 1180 280 0 0 {name=TGB_1K_3V3}
C {transmission_gates/TGB_100R_3V3.sym} 1460 280 0 0 {name=TGB_100R_3V3}
C {transmission_gates/TGB_10R_3V3.sym} 1740 280 0 0 {name=TGB_10R_3V3}
C {transmission_gates/TGB_1K_5V0.sym} 1180 480 0 0 {name=TGB_1K_5V0}
C {transmission_gates/TGB_100R_5V0.sym} 1460 480 0 0 {name=TGB_100R_5V0}
C {transmission_gates/TGB_10R_5V0.sym} 1740 480 0 0 {name=TGB_10R_5V0}
T {Include helpers (drive net 'vdd'; on a TGB cell also drive bn and bp):} -140 640 0 0 0.3 0.3 {layer=4}
C {autohv_lib.sym} -140 700 0 0 {name=AUTOHV CASE=0}
C {tg_lib.sym} 300 700 0 0 {name=TGLIB}
T {1.8 V rail-tied cells have a dead zone near mid-rail at SS / 1.62 V / cold.} -140 800 0 0 0.3 0.3 {layer=7}
T {See circuits/transmission_gates/REPORT.md section 6 before using TG_*_1V8.} -140 840 0 0 0.3 0.3 {layer=7}
