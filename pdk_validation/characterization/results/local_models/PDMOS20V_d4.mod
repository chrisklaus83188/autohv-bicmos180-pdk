* ISOLATION COPY -- discrimination experiment only.
* Source card : PDMOS20V_INT (autohv_bicmos180_case_models.inc)
* Delta       : rd=1e-09, rs=1e-09; renamed PDMOS20V_INT -> PDMOS20V_D4 because ngspice-45 keeps the FIRST .model definition and would otherwise silently ignore this copy. Every other parameter byte-identical to the PDK card.
* NOT part of the PDK. Never .include this outside its experiment.
* The model name is DISTINCT from the source card: ngspice keeps the
* first definition of a name, so shadowing is impossible. This card
* must be instantiated directly, not via the PDK subckt wrapper.
.model PDMOS20V_D4 VDMOS (pchan
+ vto={VTO_PDMOS20V_STAT+TC_VTO_PDMOS20V*(temper-27)}
+ kp={KP_PDMOS20V_STAT*(1+TC_KP_PDMOS20V*(temper-27))}
+ lambda=0.007
+ theta=0.2
+ rd=1e-09
+ rs=1e-09
+ rg=3
+ rds=1e+09
+ cgdmax=2.65626e-14
+ cgdmin=6.64064e-15
+ a=0.3
+ cgs=2.39063e-14
+ cjo=1.5e-13
+ is=8e-13
+ rb=0.08
+ bv={((22*_isTT + 21.45*_isFF + 22.55*_isSS + 22.55*_isFS + 21.45*_isSF))*(1+P_DBV_PDMOS20V)}
+ ibv=6e-05
+ nbv=1.7
+ tt=2.2e-08
+ rq=178.727
+ vq=24
+ mtriode=0.62
+ ksubthres=0.0726496
+ )
