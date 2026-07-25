* ISOLATION COPY -- discrimination experiment only.
* Source card : NDMOS80_INT (autohv_bicmos180_case_models.inc)
* Delta       : rd=1e-09, rs=1e-09; renamed NDMOS80_INT -> NDMOS80_D4 because ngspice-45 keeps the FIRST .model definition and would otherwise silently ignore this copy. Every other parameter byte-identical to the PDK card.
* NOT part of the PDK. Never .include this outside its experiment.
* The model name is DISTINCT from the source card: ngspice keeps the
* first definition of a name, so shadowing is impossible. This card
* must be instantiated directly, not via the PDK subckt wrapper.
.model NDMOS80_D4 VDMOS (nchan
+ vto={VTO_NDMOS80_STAT+TC_VTO_NDMOS80*(temper-27)}
+ kp={KP_NDMOS80_STAT*(1+TC_KP_NDMOS80*(temper-27))}
+ lambda=0.003
+ theta=0.15
+ rd=1e-09
+ rs=1e-09
+ rg=4
+ rds=7e+09
+ cgdmax=2.65626e-14
+ cgdmin=6.64064e-15
+ a=0.26
+ cgs=2.39063e-14
+ cjo=5.5e-14
+ is=9e-14
+ rb=0.22
+ bv={((95*_isTT + 91.2*_isFF + 98.8*_isSS + 91.2*_isFS + 98.8*_isSF))*(1+P_DBV_NDMOS80)}
+ ibv=1.5e-05
+ nbv=1.95
+ tt=5.5e-08
+ rq=1955.89
+ vq=110
+ mtriode=0.55
+ ksubthres=0.0777778
+ )
