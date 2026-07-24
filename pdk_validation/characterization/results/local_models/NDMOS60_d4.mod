* ISOLATION COPY -- discrimination experiment only.
* Source card : NDMOS60_INT (autohv_bicmos180_case_models.inc)
* Delta       : rd=1e-09, rs=1e-09; renamed NDMOS60_INT -> NDMOS60_D4 because ngspice-45 keeps the FIRST .model definition and would otherwise silently ignore this copy. Every other parameter byte-identical to the PDK card.
* NOT part of the PDK. Never .include this outside its experiment.
* The model name is DISTINCT from the source card: ngspice keeps the
* first definition of a name, so shadowing is impossible. This card
* must be instantiated directly, not via the PDK subckt wrapper.
.model NDMOS60_D4 VDMOS (nchan
+ vto={VTO_NDMOS60_STAT+TC_VTO_NDMOS60*(temper-27)}
+ kp={KP_NDMOS60_STAT*(1+TC_KP_NDMOS60*(temper-27))}
+ lambda=0.004
+ theta=0.03
+ rd=1e-09
+ rs=1e-09
+ rg=3
+ rds=5e+09
+ cgdmax=1.536e-13
+ cgdmin=1.4e-14
+ a=0.28
+ cgs=2.112e-13
+ cjo=7.5e-14
+ is=1.2e-13
+ rb=0.15
+ bv={((75*_isTT + 72.375*_isFF + 77.625*_isSS + 72.375*_isFS + 77.625*_isSF))*(1+P_DBV_NDMOS60)}
+ ibv=2e-05
+ nbv=1.8
+ tt=4e-08
+ rq=0.25
+ vq=90
+ mtriode=0.58
+ ksubthres=0.08
+ )
