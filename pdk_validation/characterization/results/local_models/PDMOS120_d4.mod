* ISOLATION COPY -- discrimination experiment only.
* Source card : PDMOS120_INT (autohv_bicmos180_case_models.inc)
* Delta       : rd=1e-09, rs=1e-09; renamed PDMOS120_INT -> PDMOS120_D4 because ngspice-45 keeps the FIRST .model definition and would otherwise silently ignore this copy. Every other parameter byte-identical to the PDK card.
* NOT part of the PDK. Never .include this outside its experiment.
* The model name is DISTINCT from the source card: ngspice keeps the
* first definition of a name, so shadowing is impossible. This card
* must be instantiated directly, not via the PDK subckt wrapper.
.model PDMOS120_D4 VDMOS (pchan
+ vto={VTO_PDMOS120_STAT+TC_VTO_PDMOS120*(temper-27)}
+ kp={KP_PDMOS120_STAT*(1+TC_KP_PDMOS120*(temper-27))}
+ lambda=0.003
+ theta=0.13
+ rd=1e-09
+ rs=1e-09
+ rg=6
+ rds=1e+10
+ cgdmax=2.65626e-14
+ cgdmin=6.64064e-15
+ a=0.225
+ cgs=2.39063e-14
+ cjo=2.9e-14
+ is=7e-14
+ rb=0.45
+ bv={((128*_isTT + 122.88*_isFF + 133.12*_isSS + 133.12*_isFS + 122.88*_isSF))*(1+P_DBV_PDMOS120)}
+ ibv=8e-06
+ nbv=2.15
+ tt=9.5e-08
+ rq=4145.31
+ vq=153
+ mtriode=0.47
+ ksubthres=0.0794872
+ )
