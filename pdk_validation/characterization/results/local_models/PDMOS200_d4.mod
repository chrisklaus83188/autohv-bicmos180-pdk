* ISOLATION COPY -- discrimination experiment only.
* Source card : PDMOS200_INT (autohv_bicmos180_case_models.inc)
* Delta       : rd=1e-09, rs=1e-09; renamed PDMOS200_INT -> PDMOS200_D4 because ngspice-45 keeps the FIRST .model definition and would otherwise silently ignore this copy. Every other parameter byte-identical to the PDK card.
* NOT part of the PDK. Never .include this outside its experiment.
* The model name is DISTINCT from the source card: ngspice keeps the
* first definition of a name, so shadowing is impossible. This card
* must be instantiated directly, not via the PDK subckt wrapper.
.model PDMOS200_D4 VDMOS (pchan
+ vto={VTO_PDMOS200_STAT+TC_VTO_PDMOS200*(temper-27)}
+ kp={KP_PDMOS200_STAT*(1+TC_KP_PDMOS200*(temper-27))}
+ lambda=0.0046
+ theta=0.12
+ rd=1e-09
+ rs=1e-09
+ rg=7.5
+ rds=2e+10
+ cgdmax=2.65626e-14
+ cgdmin=6.64064e-15
+ a=0.21
+ cgs=2.39063e-14
+ cjo=1.8e-14
+ is=1e-13
+ rb=0.82
+ bv={((230*_isTT + 216.2*_isFF + 243.8*_isSS + 243.8*_isFS + 216.2*_isSF))*(1+P_DBV_PDMOS200)}
+ ibv=4e-06
+ nbv=2.27
+ tt=1.55e-07
+ rq=4124.38
+ vq=248
+ mtriode=0.43
+ ksubthres=0.0811966
+ )
