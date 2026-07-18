v {xschem version=3.4.5 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {CMP_RR_5V0} -200 -320 0 0 0.6 0.6 {}
T {body: circuits/comparators/comparators_all.lib (authority)} -200 -260 0 0 0.3 0.3 {}
T {supplies vdd/vss connect by net name, not by wire} -200 -220 0 0 0.3 0.3 {}
C {ipin.sym} -200 -160 0 0 {name=p1 lab=inp}
C {ipin.sym} -200 -120 0 0 {name=p2 lab=inn}
C {opin.sym} -200 -80 0 0 {name=p3 lab=out}
C {ipin.sym} -200 -40 0 0 {name=p4 lab=ibp_5uA}
C {ipin.sym} -200 0 0 0 {name=p5 lab=EN}
T {* bias generation} -60 -120 0 0 0.4 0.4 {}
C {autohv/NMOS50.sym} 0 0 0 0 {name=rbn model=NMOS50 W=10u L=1u M=1}
T {Xrbn} -60 -110 0 0 0.3 0.3 {}
T {W=10u L=1u M=1} -60 90 0 0 0.25 0.25 {}
C {lab_pin.sym} 20 -40 0 0 {name=lrbnd lab=ibg_n}
C {lab_pin.sym} -40 0 0 0 {name=lrbng lab=ibg_n}
N 20 40 20 80 {}
C {lab_pin.sym} 20 80 0 0 {name=lrbns lab=vss}
C {lab_pin.sym} 20 0 0 0 {name=lrbnb lab=vss}
C {autohv/NMOS50.sym} 280 0 0 0 {name=mir model=NMOS50 W=10u L=1u M=1}
T {Xmir} 220 -110 0 0 0.3 0.3 {}
T {W=10u L=1u M=1} 220 90 0 0 0.25 0.25 {}
C {lab_pin.sym} 300 -40 0 0 {name=lmird lab=pmd}
C {lab_pin.sym} 240 0 0 0 {name=lmirg lab=ibg_n}
N 300 40 300 80 {}
C {lab_pin.sym} 300 80 0 0 {name=lmirs lab=vss}
C {lab_pin.sym} 300 0 0 0 {name=lmirb lab=vss}
C {autohv/PMOS50.sym} 560 0 2 1 {name=rbp model=PMOS50 W=20u L=1u M=1}
T {Xrbp} 500 -110 0 0 0.3 0.3 {}
T {W=20u L=1u M=1} 500 90 0 0 0.25 0.25 {}
C {lab_pin.sym} 580 40 0 0 {name=lrbpd lab=pmd}
C {lab_pin.sym} 520 0 0 0 {name=lrbpg lab=pmd}
N 580 -40 580 -80 {}
C {lab_pin.sym} 580 -80 0 0 {name=lrbps lab=vdd}
C {lab_pin.sym} 580 0 0 0 {name=lrbpb lab=vdd}
C {autohv/PMOS50.sym} 840 0 2 1 {name=vc1 model=PMOS50 W=20u L=1u M=1}
T {Xvc1} 780 -110 0 0 0.3 0.3 {}
T {W=20u L=1u M=1} 780 90 0 0 0.25 0.25 {}
C {lab_pin.sym} 860 40 0 0 {name=lvc1d lab=k}
C {lab_pin.sym} 800 0 0 0 {name=lvc1g lab=k}
N 860 -40 860 -80 {}
C {lab_pin.sym} 860 -80 0 0 {name=lvc1s lab=vdd}
C {lab_pin.sym} 860 0 0 0 {name=lvc1b lab=vdd}
C {autohv/PMOS50.sym} 1120 0 2 1 {name=vc2 model=PMOS50 W=20u L=1u M=1}
T {Xvc2} 1060 -110 0 0 0.3 0.3 {}
T {W=20u L=1u M=1} 1060 90 0 0 0.25 0.25 {}
C {lab_pin.sym} 1140 40 0 0 {name=lvc2d lab=vcp}
C {lab_pin.sym} 1080 0 0 0 {name=lvc2g lab=vcp}
C {lab_pin.sym} 1140 -40 0 0 {name=lvc2s lab=k}
C {lab_pin.sym} 1140 0 0 0 {name=lvc2b lab=vdd}
C {autohv/NMOS50.sym} 1400 0 0 0 {name=isk model=NMOS50 W=10u L=1u M=1}
T {Xisk} 1340 -110 0 0 0.3 0.3 {}
T {W=10u L=1u M=1} 1340 90 0 0 0.25 0.25 {}
C {lab_pin.sym} 1420 -40 0 0 {name=liskd lab=vcp}
C {lab_pin.sym} 1360 0 0 0 {name=liskg lab=ibg_n}
N 1420 40 1420 80 {}
C {lab_pin.sym} 1420 80 0 0 {name=lisks lab=vss}
C {lab_pin.sym} 1420 0 0 0 {name=liskb lab=vss}
T {* rail-to-rail folded-cascode input stage} -60 240 0 0 0.4 0.4 {}
C {autohv/NMOS50.sym} 0 360 0 0 {name=mtn model=NMOS50 W=20u L=1u M=1}
T {Xmtn} -60 250 0 0 0.3 0.3 {}
T {W=20u L=1u M=1} -60 450 0 0 0.25 0.25 {}
C {lab_pin.sym} 20 320 0 0 {name=lmtnd lab=sn}
C {lab_pin.sym} -40 360 0 0 {name=lmtng lab=ibg_n}
N 20 400 20 440 {}
C {lab_pin.sym} 20 440 0 0 {name=lmtns lab=vss}
C {lab_pin.sym} 20 360 0 0 {name=lmtnb lab=vss}
C {autohv/NMOS50.sym} 280 360 0 0 {name=n1 model=NMOS50 W=\{40u*FIN\} L=\{1u*FIN\} M=1}
T {Xn1} 220 250 0 0 0.3 0.3 {}
T {W=\{40u*FIN\} L=\{1u*FIN\} M=1} 220 450 0 0 0.25 0.25 {}
C {lab_pin.sym} 300 320 0 0 {name=ln1d lab=x}
C {lab_pin.sym} 240 360 0 0 {name=ln1g lab=inp}
C {lab_pin.sym} 300 400 0 0 {name=ln1s lab=sn}
C {lab_pin.sym} 300 360 0 0 {name=ln1b lab=vss}
C {autohv/NMOS50.sym} 560 360 0 0 {name=n2 model=NMOS50 W=\{40u*FIN\} L=\{1u*FIN\} M=1}
T {Xn2} 500 250 0 0 0.3 0.3 {}
T {W=\{40u*FIN\} L=\{1u*FIN\} M=1} 500 450 0 0 0.25 0.25 {}
C {lab_pin.sym} 580 320 0 0 {name=ln2d lab=y}
C {lab_pin.sym} 520 360 0 0 {name=ln2g lab=inn}
C {lab_pin.sym} 580 400 0 0 {name=ln2s lab=sn}
C {lab_pin.sym} 580 360 0 0 {name=ln2b lab=vss}
C {autohv/PMOS50.sym} 840 360 2 1 {name=mtp model=PMOS50 W=40u L=1u M=1}
T {Xmtp} 780 250 0 0 0.3 0.3 {}
T {W=40u L=1u M=1} 780 450 0 0 0.25 0.25 {}
C {lab_pin.sym} 860 400 0 0 {name=lmtpd lab=sp}
C {lab_pin.sym} 800 360 0 0 {name=lmtpg lab=pmd}
N 860 320 860 280 {}
C {lab_pin.sym} 860 280 0 0 {name=lmtps lab=vdd}
C {lab_pin.sym} 860 360 0 0 {name=lmtpb lab=vdd}
C {autohv/PMOS50.sym} 1120 360 2 1 {name=p1 model=PMOS50 W=\{80u*FIN\} L=\{1u*FIN\} M=1}
T {Xp1} 1060 250 0 0 0.3 0.3 {}
T {W=\{80u*FIN\} L=\{1u*FIN\} M=1} 1060 450 0 0 0.25 0.25 {}
C {lab_pin.sym} 1140 400 0 0 {name=lp1d lab=a}
C {lab_pin.sym} 1080 360 0 0 {name=lp1g lab=inp}
C {lab_pin.sym} 1140 320 0 0 {name=lp1s lab=sp}
C {lab_pin.sym} 1140 360 0 0 {name=lp1b lab=vdd}
C {autohv/PMOS50.sym} 1400 360 2 1 {name=p2 model=PMOS50 W=\{80u*FIN\} L=\{1u*FIN\} M=1}
T {Xp2} 1340 250 0 0 0.3 0.3 {}
T {W=\{80u*FIN\} L=\{1u*FIN\} M=1} 1340 450 0 0 0.25 0.25 {}
C {lab_pin.sym} 1420 400 0 0 {name=lp2d lab=b}
C {lab_pin.sym} 1360 360 0 0 {name=lp2g lab=inn}
C {lab_pin.sym} 1420 320 0 0 {name=lp2s lab=sp}
C {lab_pin.sym} 1420 360 0 0 {name=lp2b lab=vdd}
T {* rail-to-rail folded-cascode input stage (cont.)} -60 600 0 0 0.4 0.4 {}
C {autohv/PMOS50.sym} 0 720 2 1 {name=f1 model=PMOS50 W=60u L=1u M=1}
T {Xf1} -60 610 0 0 0.3 0.3 {}
T {W=60u L=1u M=1} -60 810 0 0 0.25 0.25 {}
C {lab_pin.sym} 20 760 0 0 {name=lf1d lab=x}
C {lab_pin.sym} -40 720 0 0 {name=lf1g lab=pmd}
N 20 680 20 640 {}
C {lab_pin.sym} 20 640 0 0 {name=lf1s lab=vdd}
C {lab_pin.sym} 20 720 0 0 {name=lf1b lab=vdd}
C {autohv/PMOS50.sym} 280 720 2 1 {name=f2 model=PMOS50 W=60u L=1u M=1}
T {Xf2} 220 610 0 0 0.3 0.3 {}
T {W=60u L=1u M=1} 220 810 0 0 0.25 0.25 {}
C {lab_pin.sym} 300 760 0 0 {name=lf2d lab=y}
C {lab_pin.sym} 240 720 0 0 {name=lf2g lab=pmd}
N 300 680 300 640 {}
C {lab_pin.sym} 300 640 0 0 {name=lf2s lab=vdd}
C {lab_pin.sym} 300 720 0 0 {name=lf2b lab=vdd}
C {autohv/PMOS50.sym} 560 720 2 1 {name=cp1 model=PMOS50 W=40u L=1u M=1}
T {Xcp1} 500 610 0 0 0.3 0.3 {}
T {W=40u L=1u M=1} 500 810 0 0 0.25 0.25 {}
C {lab_pin.sym} 580 760 0 0 {name=lcp1d lab=a}
C {lab_pin.sym} 520 720 0 0 {name=lcp1g lab=vcp}
C {lab_pin.sym} 580 680 0 0 {name=lcp1s lab=x}
C {lab_pin.sym} 580 720 0 0 {name=lcp1b lab=vdd}
C {autohv/PMOS50.sym} 840 720 2 1 {name=cp2 model=PMOS50 W=40u L=1u M=1}
T {Xcp2} 780 610 0 0 0.3 0.3 {}
T {W=40u L=1u M=1} 780 810 0 0 0.25 0.25 {}
C {lab_pin.sym} 860 760 0 0 {name=lcp2d lab=b}
C {lab_pin.sym} 800 720 0 0 {name=lcp2g lab=vcp}
C {lab_pin.sym} 860 680 0 0 {name=lcp2s lab=y}
C {lab_pin.sym} 860 720 0 0 {name=lcp2b lab=vdd}
C {autohv/NMOS50.sym} 1120 720 0 0 {name=mm1 model=NMOS50 W=\{20u*FIN\} L=\{1u*FIN\} M=1}
T {Xmm1} 1060 610 0 0 0.3 0.3 {}
T {W=\{20u*FIN\} L=\{1u*FIN\} M=1} 1060 810 0 0 0.25 0.25 {}
C {lab_pin.sym} 1140 680 0 0 {name=lmm1d lab=a}
C {lab_pin.sym} 1080 720 0 0 {name=lmm1g lab=a}
N 1140 760 1140 800 {}
C {lab_pin.sym} 1140 800 0 0 {name=lmm1s lab=vss}
C {lab_pin.sym} 1140 720 0 0 {name=lmm1b lab=vss}
C {autohv/NMOS50.sym} 1400 720 0 0 {name=mm2 model=NMOS50 W=\{20u*FIN\} L=\{1u*FIN\} M=1}
T {Xmm2} 1340 610 0 0 0.3 0.3 {}
T {W=\{20u*FIN\} L=\{1u*FIN\} M=1} 1340 810 0 0 0.25 0.25 {}
C {lab_pin.sym} 1420 680 0 0 {name=lmm2d lab=b}
C {lab_pin.sym} 1360 720 0 0 {name=lmm2g lab=a}
N 1420 760 1420 800 {}
C {lab_pin.sym} 1420 800 0 0 {name=lmm2s lab=vss}
C {lab_pin.sym} 1420 720 0 0 {name=lmm2b lab=vss}
T {* stage 2: common-source gain + current-source load} -60 960 0 0 0.4 0.4 {}
C {autohv/NMOS50.sym} 0 1080 0 0 {name=s2n model=NMOS50 W=40u L=1u M=1}
T {Xs2n} -60 970 0 0 0.3 0.3 {}
T {W=40u L=1u M=1} -60 1170 0 0 0.25 0.25 {}
C {lab_pin.sym} 20 1040 0 0 {name=ls2nd lab=o2}
C {lab_pin.sym} -40 1080 0 0 {name=ls2ng lab=b}
N 20 1120 20 1160 {}
C {lab_pin.sym} 20 1160 0 0 {name=ls2ns lab=vss}
C {lab_pin.sym} 20 1080 0 0 {name=ls2nb lab=vss}
C {autohv/PMOS50.sym} 280 1080 2 1 {name=s2p model=PMOS50 W=40u L=1u M=1}
T {Xs2p} 220 970 0 0 0.3 0.3 {}
T {W=40u L=1u M=1} 220 1170 0 0 0.25 0.25 {}
C {lab_pin.sym} 300 1120 0 0 {name=ls2pd lab=o2}
C {lab_pin.sym} 240 1080 0 0 {name=ls2pg lab=pmd}
N 300 1040 300 1000 {}
C {lab_pin.sym} 300 1000 0 0 {name=ls2ps lab=vdd}
C {lab_pin.sym} 300 1080 0 0 {name=ls2pb lab=vdd}
T {* stage 3: CMOS inverter (rail-to-rail digital out)} -60 1320 0 0 0.4 0.4 {}
C {autohv/PMOS50.sym} 0 1440 2 1 {name=bp model=PMOS50 W=20u L=0.5u M=1}
T {Xbp} -60 1330 0 0 0.3 0.3 {}
T {W=20u L=0.5u M=1} -60 1530 0 0 0.25 0.25 {}
C {lab_pin.sym} 20 1480 0 0 {name=lbpd lab=out}
C {lab_pin.sym} -40 1440 0 0 {name=lbpg lab=o2}
N 20 1400 20 1360 {}
C {lab_pin.sym} 20 1360 0 0 {name=lbps lab=vdd}
C {lab_pin.sym} 20 1440 0 0 {name=lbpb lab=vdd}
C {autohv/NMOS50.sym} 280 1440 0 0 {name=bn model=NMOS50 W=10u L=0.5u M=1}
T {Xbn} 220 1330 0 0 0.3 0.3 {}
T {W=10u L=0.5u M=1} 220 1530 0 0 0.25 0.25 {}
C {lab_pin.sym} 300 1400 0 0 {name=lbnd lab=out}
C {lab_pin.sym} 240 1440 0 0 {name=lbng lab=o2}
N 300 1480 300 1520 {}
C {lab_pin.sym} 300 1520 0 0 {name=lbns lab=vss}
C {lab_pin.sym} 300 1440 0 0 {name=lbnb lab=vss}
T {* enable / bias-shutdown disable (small switches; core on true rails)} -60 1680 0 0 0.4 0.4 {}
C {autohv/PMOS50.sym} 0 1800 2 1 {name=ei1p model=PMOS50 W=4u L=0.5u M=1}
T {Xei1p} -60 1690 0 0 0.3 0.3 {}
T {W=4u L=0.5u M=1} -60 1890 0 0 0.25 0.25 {}
C {lab_pin.sym} 20 1840 0 0 {name=lei1pd lab=ENB}
C {lab_pin.sym} -40 1800 0 0 {name=lei1pg lab=EN}
N 20 1760 20 1720 {}
C {lab_pin.sym} 20 1720 0 0 {name=lei1ps lab=vdd}
C {lab_pin.sym} 20 1800 0 0 {name=lei1pb lab=vdd}
C {autohv/NMOS50.sym} 280 1800 0 0 {name=ei1n model=NMOS50 W=2u L=0.5u M=1}
T {Xei1n} 220 1690 0 0 0.3 0.3 {}
T {W=2u L=0.5u M=1} 220 1890 0 0 0.25 0.25 {}
C {lab_pin.sym} 300 1760 0 0 {name=lei1nd lab=ENB}
C {lab_pin.sym} 240 1800 0 0 {name=lei1ng lab=EN}
N 300 1840 300 1880 {}
C {lab_pin.sym} 300 1880 0 0 {name=lei1ns lab=vss}
C {lab_pin.sym} 300 1800 0 0 {name=lei1nb lab=vss}
C {autohv/PMOS50.sym} 560 1800 2 1 {name=ei2p model=PMOS50 W=4u L=0.5u M=1}
T {Xei2p} 500 1690 0 0 0.3 0.3 {}
T {W=4u L=0.5u M=1} 500 1890 0 0 0.25 0.25 {}
C {lab_pin.sym} 580 1840 0 0 {name=lei2pd lab=ENbuf}
C {lab_pin.sym} 520 1800 0 0 {name=lei2pg lab=ENB}
N 580 1760 580 1720 {}
C {lab_pin.sym} 580 1720 0 0 {name=lei2ps lab=vdd}
C {lab_pin.sym} 580 1800 0 0 {name=lei2pb lab=vdd}
C {autohv/NMOS50.sym} 840 1800 0 0 {name=ei2n model=NMOS50 W=2u L=0.5u M=1}
T {Xei2n} 780 1690 0 0 0.3 0.3 {}
T {W=2u L=0.5u M=1} 780 1890 0 0 0.25 0.25 {}
C {lab_pin.sym} 860 1760 0 0 {name=lei2nd lab=ENbuf}
C {lab_pin.sym} 800 1800 0 0 {name=lei2ng lab=ENB}
N 860 1840 860 1880 {}
C {lab_pin.sym} 860 1880 0 0 {name=lei2ns lab=vss}
C {lab_pin.sym} 860 1800 0 0 {name=lei2nb lab=vss}
C {autohv/NMOS50.sym} 1120 1800 0 0 {name=ser model=NMOS50 W=4u L=0.5u M=1}
T {Xser} 1060 1690 0 0 0.3 0.3 {}
T {W=4u L=0.5u M=1} 1060 1890 0 0 0.25 0.25 {}
C {lab_pin.sym} 1140 1760 0 0 {name=lserd lab=ibg_n}
C {lab_pin.sym} 1080 1800 0 0 {name=lserg lab=ENbuf}
C {lab_pin.sym} 1140 1840 0 0 {name=lsers lab=ibp_5uA}
C {lab_pin.sym} 1140 1800 0 0 {name=lserb lab=vss}
C {autohv/NMOS50.sym} 1400 1800 0 0 {name=shn model=NMOS50 W=4u L=0.5u M=1}
T {Xshn} 1340 1690 0 0 0.3 0.3 {}
T {W=4u L=0.5u M=1} 1340 1890 0 0 0.25 0.25 {}
C {lab_pin.sym} 1420 1760 0 0 {name=lshnd lab=ibg_n}
C {lab_pin.sym} 1360 1800 0 0 {name=lshng lab=ENB}
N 1420 1840 1420 1880 {}
C {lab_pin.sym} 1420 1880 0 0 {name=lshns lab=vss}
C {lab_pin.sym} 1420 1800 0 0 {name=lshnb lab=vss}
T {* enable / bias-shutdown disable (small switches; core on true rails) (cont.)} -60 2040 0 0 0.4 0.4 {}
C {autohv/PMOS50.sym} 0 2160 2 1 {name=shp model=PMOS50 W=4u L=0.5u M=1}
T {Xshp} -60 2050 0 0 0.3 0.3 {}
T {W=4u L=0.5u M=1} -60 2250 0 0 0.25 0.25 {}
C {lab_pin.sym} 20 2200 0 0 {name=lshpd lab=pmd}
C {lab_pin.sym} -40 2160 0 0 {name=lshpg lab=ENbuf}
N 20 2120 20 2080 {}
C {lab_pin.sym} 20 2080 0 0 {name=lshps lab=vdd}
C {lab_pin.sym} 20 2160 0 0 {name=lshpb lab=vdd}
C {autohv/NMOS50.sym} 280 2160 0 0 {name=sho2 model=NMOS50 W=4u L=0.5u M=1}
T {Xsho2} 220 2050 0 0 0.3 0.3 {}
T {W=4u L=0.5u M=1} 220 2250 0 0 0.25 0.25 {}
C {lab_pin.sym} 300 2120 0 0 {name=lsho2d lab=o2}
C {lab_pin.sym} 240 2160 0 0 {name=lsho2g lab=ENB}
N 300 2200 300 2240 {}
C {lab_pin.sym} 300 2240 0 0 {name=lsho2s lab=vss}
C {lab_pin.sym} 300 2160 0 0 {name=lsho2b lab=vss}
