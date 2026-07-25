* ISOLATION COPY -- discrimination experiment only.
* Source card : NDMOS40_INT (autohv_bicmos180_case_models.inc)
* Delta       : rd=1e-09, rs=1e-09; renamed NDMOS40_INT -> NDMOS40_D4 because ngspice-45 keeps the FIRST .model definition and would otherwise silently ignore this copy. Every other parameter byte-identical to the PDK card.
* NOT part of the PDK. Never .include this outside its experiment.
* The model name is DISTINCT from the source card: ngspice keeps the
* first definition of a name, so shadowing is impossible. This card
* must be instantiated directly, not via the PDK subckt wrapper.
.model NDMOS40_D4 VDMOS (nchan
+ vto={VTO_NDMOS40_STAT+TC_VTO_NDMOS40*(temper-27)}
+ kp={KP_NDMOS40_STAT*(1+TC_KP_NDMOS40*(temper-27))}
+ lambda=0.0055
+ theta=0.18
+ rd=1e-09
+ rs=1e-09
+ rg=3
+ rds=2e+09
+ cgdmax=2.65626e-14
+ cgdmin=6.64064e-15
+ a=0.30
+ cgs=2.39063e-14
+ cjo=1e-13
+ is=2.5e-13
+ rb=0.10
+ bv={((48*_isTT + 46.56*_isFF + 49.44*_isSS + 46.56*_isFS + 49.44*_isSF))*(1+P_DBV_NDMOS40)}
+ ibv=3e-05
+ nbv=1.7
+ tt=2.8e-08
+ rq=1195.68
+ vq=55
+ mtriode=0.61
+ ksubthres=0.074359
+ )
