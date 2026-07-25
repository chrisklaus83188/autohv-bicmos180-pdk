* ISOLATION COPY -- discrimination experiment only.
* Source card : PDMOS40_INT (autohv_bicmos180_case_models.inc)
* Delta       : rd=1e-09, rs=1e-09; renamed PDMOS40_INT -> PDMOS40_D4 because ngspice-45 keeps the FIRST .model definition and would otherwise silently ignore this copy. Every other parameter byte-identical to the PDK card.
* NOT part of the PDK. Never .include this outside its experiment.
* The model name is DISTINCT from the source card: ngspice keeps the
* first definition of a name, so shadowing is impossible. This card
* must be instantiated directly, not via the PDK subckt wrapper.
.model PDMOS40_D4 VDMOS (pchan
+ vto={VTO_PDMOS40_STAT+TC_VTO_PDMOS40*(temper-27)}
+ kp={KP_PDMOS40_STAT*(1+TC_KP_PDMOS40*(temper-27))}
+ lambda=0.0048
+ theta=0.18
+ rd=1e-09
+ rs=1e-09
+ rg=3
+ rds=2e+09
+ cgdmax=2.65626e-14
+ cgdmin=6.64064e-15
+ a=0.285
+ cgs=2.39063e-14
+ cjo=1.05e-13
+ is=3.3e-13
+ rb=0.13
+ bv={((45*_isTT + 43.65*_isFF + 46.35*_isSS + 46.35*_isFS + 43.65*_isSF))*(1+P_DBV_PDMOS40)}
+ ibv=3.5e-05
+ nbv=1.8
+ tt=3.5e-08
+ rq=458.44
+ vq=52
+ mtriode=0.59
+ ksubthres=0.074359
+ )
