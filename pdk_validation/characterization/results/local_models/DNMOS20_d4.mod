* ISOLATION COPY -- discrimination experiment only.
* Source card : DNMOS20_INT (autohv_bicmos180_case_models.inc)
* Delta       : rd=1e-09, rs=1e-09; renamed DNMOS20_INT -> DNMOS20_D4 because ngspice-45 keeps the FIRST .model definition and would otherwise silently ignore this copy. Every other parameter byte-identical to the PDK card.
* NOT part of the PDK. Never .include this outside its experiment.
* The model name is DISTINCT from the source card: ngspice keeps the
* first definition of a name, so shadowing is impossible. This card
* must be instantiated directly, not via the PDK subckt wrapper.
.model DNMOS20_D4 VDMOS (nchan
+ vto={VTO_DNMOS20_STAT+TC_VTO_DNMOS20*(temper-27)}
+ kp={KP_DNMOS20_STAT*(1+TC_KP_DNMOS20*(temper-27))}
+ lambda=0.005
+ theta=0.038
+ rd=1e-09
+ rs=1e-09
+ rg=2
+ rds=1e+09
+ cgdmax=1.44e-13
+ cgdmin=1.2e-14
+ a=0.3
+ cgs=2.016e-13
+ cjo=7e-14
+ is=2e-13
+ rb=0.1
+ bv={((24*_isTT + 23.4*_isFF + 24.6*_isSS + 23.4*_isFS + 24.6*_isSF))*(1+P_DBV_DNMOS20)}
+ ibv=4e-05
+ nbv=1.7
+ tt=2e-08
+ rq=0.2
+ vq=28
+ mtriode=0.6
+ ksubthres=0.085
+ )
