* ISOLATION COPY -- discrimination experiment only.
* Source card : PDMOS80_INT (autohv_bicmos180_case_models.inc)
* Delta       : rd=1e-09, rs=1e-09; renamed PDMOS80_INT -> PDMOS80_D4 because ngspice-45 keeps the FIRST .model definition and would otherwise silently ignore this copy. Every other parameter byte-identical to the PDK card.
* NOT part of the PDK. Never .include this outside its experiment.
* The model name is DISTINCT from the source card: ngspice keeps the
* first definition of a name, so shadowing is impossible. This card
* must be instantiated directly, not via the PDK subckt wrapper.
.model PDMOS80_D4 VDMOS (pchan
+ vto={VTO_PDMOS80_STAT+TC_VTO_PDMOS80*(temper-27)}
+ kp={KP_PDMOS80_STAT*(1+TC_KP_PDMOS80*(temper-27))}
+ lambda=0.0027
+ theta=0.031
+ rd=1e-09
+ rs=1e-09
+ rg=5
+ rds=7e+09
+ cgdmax=7.5e-14
+ cgdmin=7e-15
+ a=0.245
+ cgs=9.5e-14
+ cjo=4.5e-14
+ is=1.3e-13
+ rb=0.28
+ bv={((90*_isTT + 86.4*_isFF + 93.6*_isSS + 93.6*_isFS + 86.4*_isSF))*(1+P_DBV_PDMOS80)}
+ ibv=1.5e-05
+ nbv=2.0
+ tt=6.5e-08
+ rq=0.46
+ vq=105
+ mtriode=0.52
+ ksubthres=0.082
+ )
