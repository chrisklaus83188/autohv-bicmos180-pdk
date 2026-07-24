* ISOLATION COPY -- discrimination experiment only.
* Source card : DNMOS20_INT (autohv_bicmos180_case_models.inc)
* Delta       : ; renamed DNMOS20_INT -> DNMOS20_ASIS because ngspice-45 keeps the FIRST .model definition and would otherwise silently ignore this copy. Every other parameter byte-identical to the PDK card.
* NOT part of the PDK. Never .include this outside its experiment.
* Included AFTER the PDK so this card shadows the original.
.model DNMOS20_ASIS VDMOS (nchan
+ vto={VTO_DNMOS20_STAT+TC_VTO_DNMOS20*(temper-27)}
+ kp={KP_DNMOS20_STAT*(1+TC_KP_DNMOS20*(temper-27))}
+ lambda=0.005
+ theta=0.038
+ rd={RD_DNMOS20_STAT*(1+TC_RD_DNMOS20*(temper-27))}
+ rs={RS_DNMOS20_STAT*(1+TC_RS_DNMOS20*(temper-27))}
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
