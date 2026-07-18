v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {CMP_PIN_1V8} -200 -320 0 0 0.6 0.6 {}
T {body: circuits/comparators/comparators_all.lib (authority)} -200 -260 0 0 0.3 0.3 {}
T {supplies vdd/vss connect by net name, not by wire} -200 -220 0 0 0.3 0.3 {}
C {ipin.sym} -200 -160 0 0 {name=p1 lab=inp}
C {ipin.sym} -200 -120 0 0 {name=p2 lab=inn}
C {opin.sym} -200 -80 0 0 {name=p3 lab=out}
C {ipin.sym} -200 -40 0 0 {name=p4 lab=ibn_5uA}
C {ipin.sym} -200 0 0 0 {name=p5 lab=EN}
T {* bias mirror (PMOS diode; ref current pulled from ibn_5uA down toward vss)} -60 -120 0 0 0.4 0.4 {}
C {autohv/PMOS18.sym} 0 0 2 1 {name=mb model=PMOS18 W=\{20u*WSCALE\} L=\{LANA\} M=1}
T {Xmb} -60 -110 0 0 0.3 0.3 {}
T {W=\{20u*WSCALE\} L=\{LANA\} M=1} -60 90 0 0 0.25 0.25 {}
C {lab_pin.sym} 20 40 0 0 {name=lmbd lab=ibg}
C {lab_pin.sym} -40 0 0 0 {name=lmbg lab=ibg}
N 20 -40 20 -80 {}
C {lab_pin.sym} 20 -80 0 0 {name=lmbs lab=vdd}
C {lab_pin.sym} 20 0 0 0 {name=lmbb lab=vdd}
T {* stage 1: PMOS pair, NMOS mirror load (both scaled by FIN for offset)} -60 240 0 0 0.4 0.4 {}
C {autohv/PMOS18.sym} 0 360 2 1 {name=tail model=PMOS18 W=\{20u*WSCALE\} L=\{LANA\} M=2}
T {Xtail} -60 250 0 0 0.3 0.3 {}
T {W=\{20u*WSCALE\} L=\{LANA\} M=2} -60 450 0 0 0.25 0.25 {}
C {lab_pin.sym} 20 400 0 0 {name=ltaild lab=tail}
C {lab_pin.sym} -40 360 0 0 {name=ltailg lab=ibg}
N 20 320 20 280 {}
C {lab_pin.sym} 20 280 0 0 {name=ltails lab=vdd}
C {lab_pin.sym} 20 360 0 0 {name=ltailb lab=vdd}
C {autohv/PMOS18.sym} 280 360 2 1 {name=m1 model=PMOS18 W=\{WIN*FIN\} L=\{LIN*FIN\} M=1}
T {Xm1} 220 250 0 0 0.3 0.3 {}
T {W=\{WIN*FIN\} L=\{LIN*FIN\} M=1} 220 450 0 0 0.25 0.25 {}
C {lab_pin.sym} 300 400 0 0 {name=lm1d lab=n1}
C {lab_pin.sym} 240 360 0 0 {name=lm1g lab=inp}
C {lab_pin.sym} 300 320 0 0 {name=lm1s lab=tail}
C {lab_pin.sym} 300 360 0 0 {name=lm1b lab=vdd}
C {autohv/PMOS18.sym} 560 360 2 1 {name=m2 model=PMOS18 W=\{WIN*FIN\} L=\{LIN*FIN\} M=1}
T {Xm2} 500 250 0 0 0.3 0.3 {}
T {W=\{WIN*FIN\} L=\{LIN*FIN\} M=1} 500 450 0 0 0.25 0.25 {}
C {lab_pin.sym} 580 400 0 0 {name=lm2d lab=n2}
C {lab_pin.sym} 520 360 0 0 {name=lm2g lab=inn}
C {lab_pin.sym} 580 320 0 0 {name=lm2s lab=tail}
C {lab_pin.sym} 580 360 0 0 {name=lm2b lab=vdd}
C {autohv/NMOS18.sym} 840 360 0 0 {name=m3 model=NMOS18 W=\{10u*WSCALE*FIN\} L=\{LANA*FIN\} M=1}
T {Xm3} 780 250 0 0 0.3 0.3 {}
T {W=\{10u*WSCALE*FIN\} L=\{LANA*FIN\} M=1} 780 450 0 0 0.25 0.25 {}
C {lab_pin.sym} 860 320 0 0 {name=lm3d lab=n1}
C {lab_pin.sym} 800 360 0 0 {name=lm3g lab=n1}
N 860 400 860 440 {}
C {lab_pin.sym} 860 440 0 0 {name=lm3s lab=vss}
C {lab_pin.sym} 860 360 0 0 {name=lm3b lab=vss}
C {autohv/NMOS18.sym} 1120 360 0 0 {name=m4 model=NMOS18 W=\{10u*WSCALE*FIN\} L=\{LANA*FIN\} M=1}
T {Xm4} 1060 250 0 0 0.3 0.3 {}
T {W=\{10u*WSCALE*FIN\} L=\{LANA*FIN\} M=1} 1060 450 0 0 0.25 0.25 {}
C {lab_pin.sym} 1140 320 0 0 {name=lm4d lab=n2}
C {lab_pin.sym} 1080 360 0 0 {name=lm4g lab=n1}
N 1140 400 1140 440 {}
C {lab_pin.sym} 1140 440 0 0 {name=lm4s lab=vss}
C {lab_pin.sym} 1140 360 0 0 {name=lm4b lab=vss}
T {* optional steered-current hysteresis} -60 600 0 0 0.4 0.4 {}
C {autohv/PMOS18.sym} 0 720 2 1 {name=htail model=PMOS18 W=\{20u*WSCALE*HYSK\} L=\{LANA\} M=1}
T {Xhtail  [HYSK>0 only]} -60 610 0 0 0.3 0.3 {}
T {W=\{20u*WSCALE*HYSK\} L=\{LANA\} M=1} -60 810 0 0 0.25 0.25 {}
C {lab_pin.sym} 20 760 0 0 {name=lhtaild lab=sh}
C {lab_pin.sym} -40 720 0 0 {name=lhtailg lab=ibg}
N 20 680 20 640 {}
C {lab_pin.sym} 20 640 0 0 {name=lhtails lab=vdd}
C {lab_pin.sym} 20 720 0 0 {name=lhtailb lab=vdd}
C {autohv/PMOS18.sym} 280 720 2 1 {name=mha model=PMOS18 W=\{20u*WSCALE\} L=0.5u M=1}
T {Xmha  [HYSK>0 only]} 220 610 0 0 0.3 0.3 {}
T {W=\{20u*WSCALE\} L=0.5u M=1} 220 810 0 0 0.25 0.25 {}
C {lab_pin.sym} 300 760 0 0 {name=lmhad lab=n1}
C {lab_pin.sym} 240 720 0 0 {name=lmhag lab=out}
C {lab_pin.sym} 300 680 0 0 {name=lmhas lab=sh}
C {lab_pin.sym} 300 720 0 0 {name=lmhab lab=vdd}
C {autohv/PMOS18.sym} 560 720 2 1 {name=mhb model=PMOS18 W=\{20u*WSCALE\} L=0.5u M=1}
T {Xmhb  [HYSK>0 only]} 500 610 0 0 0.3 0.3 {}
T {W=\{20u*WSCALE\} L=0.5u M=1} 500 810 0 0 0.25 0.25 {}
C {lab_pin.sym} 580 760 0 0 {name=lmhbd lab=n2}
C {lab_pin.sym} 520 720 0 0 {name=lmhbg lab=o2}
C {lab_pin.sym} 580 680 0 0 {name=lmhbs lab=sh}
C {lab_pin.sym} 580 720 0 0 {name=lmhbb lab=vdd}
T {* stage 2: NMOS common-source + PMOS current-source load} -60 960 0 0 0.4 0.4 {}
C {autohv/NMOS18.sym} 0 1080 0 0 {name=m5 model=NMOS18 W=\{40u*WSCALE\} L=\{LANA\} M=1}
T {Xm5} -60 970 0 0 0.3 0.3 {}
T {W=\{40u*WSCALE\} L=\{LANA\} M=1} -60 1170 0 0 0.25 0.25 {}
C {lab_pin.sym} 20 1040 0 0 {name=lm5d lab=o2}
C {lab_pin.sym} -40 1080 0 0 {name=lm5g lab=n2}
N 20 1120 20 1160 {}
C {lab_pin.sym} 20 1160 0 0 {name=lm5s lab=vss}
C {lab_pin.sym} 20 1080 0 0 {name=lm5b lab=vss}
C {autohv/PMOS18.sym} 280 1080 2 1 {name=m6 model=PMOS18 W=\{20u*WSCALE\} L=\{LANA\} M=4}
T {Xm6} 220 970 0 0 0.3 0.3 {}
T {W=\{20u*WSCALE\} L=\{LANA\} M=4} 220 1170 0 0 0.25 0.25 {}
C {lab_pin.sym} 300 1120 0 0 {name=lm6d lab=o2}
C {lab_pin.sym} 240 1080 0 0 {name=lm6g lab=ibg}
N 300 1040 300 1000 {}
C {lab_pin.sym} 300 1000 0 0 {name=lm6s lab=vdd}
C {lab_pin.sym} 300 1080 0 0 {name=lm6b lab=vdd}
T {* stage 3: CMOS output inverter (rail-to-rail)} -60 1320 0 0 0.4 0.4 {}
C {autohv/PMOS18.sym} 0 1440 2 1 {name=m7 model=PMOS18 W=\{20u*WSCALE\} L=0.5u M=1}
T {Xm7} -60 1330 0 0 0.3 0.3 {}
T {W=\{20u*WSCALE\} L=0.5u M=1} -60 1530 0 0 0.25 0.25 {}
C {lab_pin.sym} 20 1480 0 0 {name=lm7d lab=out}
C {lab_pin.sym} -40 1440 0 0 {name=lm7g lab=o2}
N 20 1400 20 1360 {}
C {lab_pin.sym} 20 1360 0 0 {name=lm7s lab=vdd}
C {lab_pin.sym} 20 1440 0 0 {name=lm7b lab=vdd}
C {autohv/NMOS18.sym} 280 1440 0 0 {name=m8 model=NMOS18 W=\{10u*WSCALE\} L=0.5u M=1}
T {Xm8} 220 1330 0 0 0.3 0.3 {}
T {W=\{10u*WSCALE\} L=0.5u M=1} 220 1530 0 0 0.25 0.25 {}
C {lab_pin.sym} 300 1400 0 0 {name=lm8d lab=out}
C {lab_pin.sym} 240 1440 0 0 {name=lm8g lab=o2}
N 300 1480 300 1520 {}
C {lab_pin.sym} 300 1520 0 0 {name=lm8s lab=vss}
C {lab_pin.sym} 300 1440 0 0 {name=lm8b lab=vss}
T {* enable / bias-shutdown disable (small switches; core on true rails)} -60 1680 0 0 0.4 0.4 {}
C {autohv/PMOS18.sym} 0 1800 2 1 {name=ei1p model=PMOS18 W=4u L=0.5u M=1}
T {Xei1p} -60 1690 0 0 0.3 0.3 {}
T {W=4u L=0.5u M=1} -60 1890 0 0 0.25 0.25 {}
C {lab_pin.sym} 20 1840 0 0 {name=lei1pd lab=ENB}
C {lab_pin.sym} -40 1800 0 0 {name=lei1pg lab=EN}
N 20 1760 20 1720 {}
C {lab_pin.sym} 20 1720 0 0 {name=lei1ps lab=vdd}
C {lab_pin.sym} 20 1800 0 0 {name=lei1pb lab=vdd}
C {autohv/NMOS18.sym} 280 1800 0 0 {name=ei1n model=NMOS18 W=2u L=0.5u M=1}
T {Xei1n} 220 1690 0 0 0.3 0.3 {}
T {W=2u L=0.5u M=1} 220 1890 0 0 0.25 0.25 {}
C {lab_pin.sym} 300 1760 0 0 {name=lei1nd lab=ENB}
C {lab_pin.sym} 240 1800 0 0 {name=lei1ng lab=EN}
N 300 1840 300 1880 {}
C {lab_pin.sym} 300 1880 0 0 {name=lei1ns lab=vss}
C {lab_pin.sym} 300 1800 0 0 {name=lei1nb lab=vss}
C {autohv/PMOS18.sym} 560 1800 2 1 {name=ei2p model=PMOS18 W=4u L=0.5u M=1}
T {Xei2p} 500 1690 0 0 0.3 0.3 {}
T {W=4u L=0.5u M=1} 500 1890 0 0 0.25 0.25 {}
C {lab_pin.sym} 580 1840 0 0 {name=lei2pd lab=ENbuf}
C {lab_pin.sym} 520 1800 0 0 {name=lei2pg lab=ENB}
N 580 1760 580 1720 {}
C {lab_pin.sym} 580 1720 0 0 {name=lei2ps lab=vdd}
C {lab_pin.sym} 580 1800 0 0 {name=lei2pb lab=vdd}
C {autohv/NMOS18.sym} 840 1800 0 0 {name=ei2n model=NMOS18 W=2u L=0.5u M=1}
T {Xei2n} 780 1690 0 0 0.3 0.3 {}
T {W=2u L=0.5u M=1} 780 1890 0 0 0.25 0.25 {}
C {lab_pin.sym} 860 1760 0 0 {name=lei2nd lab=ENbuf}
C {lab_pin.sym} 800 1800 0 0 {name=lei2ng lab=ENB}
N 860 1840 860 1880 {}
C {lab_pin.sym} 860 1880 0 0 {name=lei2ns lab=vss}
C {lab_pin.sym} 860 1800 0 0 {name=lei2nb lab=vss}
C {autohv/PMOS18.sym} 1120 1800 2 1 {name=ser model=PMOS18 W=4u L=0.5u M=1}
T {Xser} 1060 1690 0 0 0.3 0.3 {}
T {W=4u L=0.5u M=1} 1060 1890 0 0 0.25 0.25 {}
C {lab_pin.sym} 1140 1840 0 0 {name=lserd lab=ibg}
C {lab_pin.sym} 1080 1800 0 0 {name=lserg lab=ENB}
C {lab_pin.sym} 1140 1760 0 0 {name=lsers lab=ibn_5uA}
C {lab_pin.sym} 1140 1800 0 0 {name=lserb lab=vdd}
C {autohv/PMOS18.sym} 1400 1800 2 1 {name=sh model=PMOS18 W=4u L=0.5u M=1}
T {Xsh} 1340 1690 0 0 0.3 0.3 {}
T {W=4u L=0.5u M=1} 1340 1890 0 0 0.25 0.25 {}
C {lab_pin.sym} 1420 1840 0 0 {name=lshd lab=ibg}
C {lab_pin.sym} 1360 1800 0 0 {name=lshg lab=ENbuf}
N 1420 1760 1420 1720 {}
C {lab_pin.sym} 1420 1720 0 0 {name=lshs lab=vdd}
C {lab_pin.sym} 1420 1800 0 0 {name=lshb lab=vdd}
T {* enable / bias-shutdown disable (small switches; core on true rails) (cont.)} -60 2040 0 0 0.4 0.4 {}
C {autohv/NMOS18.sym} 0 2160 0 0 {name=sho2 model=NMOS18 W=4u L=0.5u M=1}
T {Xsho2} -60 2050 0 0 0.3 0.3 {}
T {W=4u L=0.5u M=1} -60 2250 0 0 0.25 0.25 {}
C {lab_pin.sym} 20 2120 0 0 {name=lsho2d lab=o2}
C {lab_pin.sym} -40 2160 0 0 {name=lsho2g lab=ENB}
N 20 2200 20 2240 {}
C {lab_pin.sym} 20 2240 0 0 {name=lsho2s lab=vss}
C {lab_pin.sym} 20 2160 0 0 {name=lsho2b lab=vss}
