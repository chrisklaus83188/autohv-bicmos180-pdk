* ISOLATION COPY -- discrimination experiment only.
* Source card : NDMOS200_INT (autohv_bicmos180_case_models.inc)
* Delta       : rd=1e-09, rs=1e-09; renamed NDMOS200_INT -> NDMOS200_D3 because ngspice-45 keeps the FIRST .model definition and would otherwise silently ignore this copy. Every other parameter byte-identical to the PDK card.
* NOT part of the PDK. Never .include this outside its experiment.
* The model name is DISTINCT from the source card: ngspice keeps the
* first definition of a name, so shadowing is impossible. This card
* must be instantiated directly, not via the PDK subckt wrapper.
.model NDMOS200_D3 VDMOS (nchan
+ vto={VTO_NDMOS200_STAT+TC_VTO_NDMOS200*(temper-27)}
+ kp={KP_NDMOS200_STAT*(1+TC_KP_NDMOS200*(temper-27))}
+ lambda=0.0012
+ theta=0.018
+ rd=1e-09
+ rs=1e-09
+ rg=6
+ rds=2e+10
+ cgdmax=3.5e-14
+ cgdmin=3e-15
+ a=0.22
+ cgs=4.8e-14
+ cjo=2.2e-14
+ is=2.5e-14
+ rb=0.65
+ bv={((225*_isTT + 211.5*_isFF + 238.5*_isSS + 211.5*_isFS + 238.5*_isSF))*(1+P_DBV_NDMOS200)}
+ ibv=4e-06
+ nbv=2.2
+ tt=1.3e-07
+ rq=1.10
+ vq=260
+ mtriode=0.45
+ ksubthres=0.060
+ )
