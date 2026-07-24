* ISOLATION COPY -- discrimination experiment only.
* Source card : NDMOS120_INT (autohv_bicmos180_case_models.inc)
* Delta       : rd=1e-09, rs=1e-09; renamed NDMOS120_INT -> NDMOS120_D4 because ngspice-45 keeps the FIRST .model definition and would otherwise silently ignore this copy. Every other parameter byte-identical to the PDK card.
* NOT part of the PDK. Never .include this outside its experiment.
* The model name is DISTINCT from the source card: ngspice keeps the
* first definition of a name, so shadowing is impossible. This card
* must be instantiated directly, not via the PDK subckt wrapper.
.model NDMOS120_D4 VDMOS (nchan
+ vto={VTO_NDMOS120_STAT+TC_VTO_NDMOS120*(temper-27)}
+ kp={KP_NDMOS120_STAT*(1+TC_KP_NDMOS120*(temper-27))}
+ lambda=0.002
+ theta=0.022
+ rd=1e-09
+ rs=1e-09
+ rg=5
+ rds=1e+10
+ cgdmax=6.24e-14
+ cgdmin=5e-15
+ a=0.24
+ cgs=8.64e-14
+ cjo=3.5e-14
+ is=5e-14
+ rb=0.35
+ bv={((135*_isTT + 128.25*_isFF + 141.75*_isSS + 128.25*_isFS + 141.75*_isSF))*(1+P_DBV_NDMOS120)}
+ ibv=8e-06
+ nbv=2.1
+ tt=8e-08
+ rq=0.65
+ vq=160
+ mtriode=0.5
+ ksubthres=0.07
+ )
