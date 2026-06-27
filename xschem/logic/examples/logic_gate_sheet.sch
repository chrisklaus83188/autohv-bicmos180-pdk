v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
E {}
T {AutoHV async-logic - every gate instantiated (8 types x 3 voltage domains).  Power is by text: VPWR=vdd (drive once), VGND=0 (auto).} -100 -95 0 0 0.4 0.4 {layer=4}
T {INV} -18 -55 0 0 0.3 0.3 {layer=7}
T {BUF} 142 -55 0 0 0.3 0.3 {layer=7}
T {NAND2} 302 -55 0 0 0.3 0.3 {layer=7}
T {NOR2} 462 -55 0 0 0.3 0.3 {layer=7}
T {AND2} 622 -55 0 0 0.3 0.3 {layer=7}
T {OR2} 782 -55 0 0 0.3 0.3 {layer=7}
T {XOR2} 942 -55 0 0 0.3 0.3 {layer=7}
T {XNOR2} 1102 -55 0 0 0.3 0.3 {layer=7}
T {1V8} -150 -8 0 0 0.35 0.35 {layer=8}
C {logic/INV_1V8.sym} 0 0 0 0 {name=INV_1V8}
C {logic/BUF_1V8.sym} 160 0 0 0 {name=BUF_1V8}
C {logic/NAND2_1V8.sym} 320 0 0 0 {name=NAND2_1V8}
C {logic/NOR2_1V8.sym} 480 0 0 0 {name=NOR2_1V8}
C {logic/AND2_1V8.sym} 640 0 0 0 {name=AND2_1V8}
C {logic/OR2_1V8.sym} 800 0 0 0 {name=OR2_1V8}
C {logic/XOR2_1V8.sym} 960 0 0 0 {name=XOR2_1V8}
C {logic/XNOR2_1V8.sym} 1120 0 0 0 {name=XNOR2_1V8}
T {3V3} -150 162 0 0 0.35 0.35 {layer=8}
C {logic/INV_3V3.sym} 0 170 0 0 {name=INV_3V3}
C {logic/BUF_3V3.sym} 160 170 0 0 {name=BUF_3V3}
C {logic/NAND2_3V3.sym} 320 170 0 0 {name=NAND2_3V3}
C {logic/NOR2_3V3.sym} 480 170 0 0 {name=NOR2_3V3}
C {logic/AND2_3V3.sym} 640 170 0 0 {name=AND2_3V3}
C {logic/OR2_3V3.sym} 800 170 0 0 {name=OR2_3V3}
C {logic/XOR2_3V3.sym} 960 170 0 0 {name=XOR2_3V3}
C {logic/XNOR2_3V3.sym} 1120 170 0 0 {name=XNOR2_3V3}
T {5V0} -150 332 0 0 0.35 0.35 {layer=8}
C {logic/INV_5V0.sym} 0 340 0 0 {name=INV_5V0}
C {logic/BUF_5V0.sym} 160 340 0 0 {name=BUF_5V0}
C {logic/NAND2_5V0.sym} 320 340 0 0 {name=NAND2_5V0}
C {logic/NOR2_5V0.sym} 480 340 0 0 {name=NOR2_5V0}
C {logic/AND2_5V0.sym} 640 340 0 0 {name=AND2_5V0}
C {logic/OR2_5V0.sym} 800 340 0 0 {name=OR2_5V0}
C {logic/XOR2_5V0.sym} 960 340 0 0 {name=XOR2_5V0}
C {logic/XNOR2_5V0.sym} 1120 340 0 0 {name=XNOR2_5V0}
T {Include helpers (drop one of each in a testbench, then drive net 'vdd'):} -150 500 0 0 0.28 0.28 {layer=4}
C {autohv_lib.sym} -150 530 0 0 {name=AUTOHV CASE=0}
C {logic_lib.sym} 200 530 0 0 {name=LOGICLIB}
