* ISOLATION COPY -- discrimination experiment only.
* Source card : NDMOS20_INT (autohv_bicmos180_case_models.inc)
* Delta       : rd=1e-09, rs=1e-09; renamed NDMOS20_INT -> NDMOS20_D4 because ngspice-45 keeps the FIRST .model definition and would otherwise silently ignore this copy. Every other parameter byte-identical to the PDK card.
* NOT part of the PDK. Never .include this outside its experiment.
* The model name is DISTINCT from the source card: ngspice keeps the
* first definition of a name, so shadowing is impossible. This card
* must be instantiated directly, not via the PDK subckt wrapper.
.model NDMOS20_D4 VDMOS (nchan
+ vto={VTO_NDMOS20_STAT+TC_VTO_NDMOS20*(temper-27)}
+ kp={KP_NDMOS20_STAT*(1+TC_KP_NDMOS20*(temper-27))}
+ lambda=0.008
+ theta=0.04
+ rd=1e-09
+ rs=1e-09
+ rg=2
+ rds=1e+09
+ cgdmax=4.032e-13
+ cgdmin=3.5e-14
+ a=0.32
+ cgs=4.992e-13
+ cjo=1.4e-13
+ is=5e-13
+ rb=0.06
+ bv={((24*_isTT + 23.4*_isFF + 24.6*_isSS + 23.4*_isFS + 24.6*_isSF))*(1+P_DBV_NDMOS20)}
+ ibv=5e-05
+ nbv=1.6
+ tt=1.8e-08
+ rq=0.12
+ vq=25
+ mtriode=0.65
+ ksubthres=0.095
+ )
