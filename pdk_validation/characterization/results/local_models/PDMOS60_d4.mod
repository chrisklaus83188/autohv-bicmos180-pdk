* ISOLATION COPY -- discrimination experiment only.
* Source card : PDMOS60_INT (autohv_bicmos180_case_models.inc)
* Delta       : rd=1e-09, rs=1e-09; renamed PDMOS60_INT -> PDMOS60_D4 because ngspice-45 keeps the FIRST .model definition and would otherwise silently ignore this copy. Every other parameter byte-identical to the PDK card.
* NOT part of the PDK. Never .include this outside its experiment.
* The model name is DISTINCT from the source card: ngspice keeps the
* first definition of a name, so shadowing is impossible. This card
* must be instantiated directly, not via the PDK subckt wrapper.
.model PDMOS60_D4 VDMOS (pchan
+ vto={VTO_PDMOS60_STAT+TC_VTO_PDMOS60*(temper-27)}
+ kp={KP_PDMOS60_STAT*(1+TC_KP_PDMOS60*(temper-27))}
+ lambda=0.0035
+ theta=0.035
+ rd=1e-09
+ rs=1e-09
+ rg=4
+ rds=5e+09
+ cgdmax=1.152e-13
+ cgdmin=1e-14
+ a=0.26
+ cgs=1.44e-13
+ cjo=6.5e-14
+ is=1.8e-13
+ rb=0.2
+ bv={((70*_isTT + 67.55*_isFF + 72.45*_isSS + 72.45*_isFS + 67.55*_isSF))*(1+P_DBV_PDMOS60)}
+ ibv=2e-05
+ nbv=1.9
+ tt=5e-08
+ rq=0.32
+ vq=85
+ mtriode=0.55
+ ksubthres=0.09
+ )
