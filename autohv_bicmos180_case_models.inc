* ============================================================================
* AutoHV_BiCMOS180 - case-parameterized models + params (include file).
* Pulled in by autohv_bicmos180_case.lib. Keep these two files together.
* Kept separate so the Qucs-S library palette lists only the 76 devices,
* not the 38 internal *_INT models.
* ============================================================================

.param case=0
.param PROC_ON=0
.param MM_ON=0
* --- one-hot corner selectors (exactly one is 1; TT is the default) ---
.param _isFF={(case==1)}
.param _isSS={(case==2)}
.param _isFS={(case==3)}
.param _isSF={(case==4)}
.param _isTT={1 - _isFF - _isSS - _isFS - _isSF}

* --- statistical parameters (corner-independent; gated by PROC_ON/MM_ON) ---
.param P_TOX_18={PROC_ON*AGAUSS(0,0.01,3)}
.param P_CJ_18={PROC_ON*AGAUSS(0,0.05,3)}
.param P_CJSW_18={PROC_ON*AGAUSS(0,0.05,3)}
.param P_TOX_33={PROC_ON*AGAUSS(0,0.01,3)}
.param P_CJ_33={PROC_ON*AGAUSS(0,0.05,3)}
.param P_CJSW_33={PROC_ON*AGAUSS(0,0.05,3)}
.param P_TOX_50={PROC_ON*AGAUSS(0,0.01,3)}
.param P_CJ_50={PROC_ON*AGAUSS(0,0.05,3)}
.param P_CJSW_50={PROC_ON*AGAUSS(0,0.05,3)}
.param P_DVTH_NMOS18={PROC_ON*AGAUSS(0,0.025,3)}
.param P_DU0_NMOS18={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DVSAT_NMOS18={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DRDSW_NMOS18={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DJS_NMOS18={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DVTH_PMOS18={PROC_ON*AGAUSS(0,0.025,3)}
.param P_DU0_PMOS18={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DVSAT_PMOS18={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DRDSW_PMOS18={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DJS_PMOS18={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DVTH_NMOS33={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DU0_NMOS33={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DVSAT_NMOS33={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DRDSW_NMOS33={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DJS_NMOS33={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DVTH_PMOS33={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DU0_PMOS33={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DVSAT_PMOS33={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DRDSW_PMOS33={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DJS_PMOS33={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DVTH_NMOS50={PROC_ON*AGAUSS(0,0.035,3)}
.param P_DU0_NMOS50={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DVSAT_NMOS50={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DRDSW_NMOS50={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DJS_NMOS50={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DVTH_PMOS50={PROC_ON*AGAUSS(0,0.035,3)}
.param P_DU0_PMOS50={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DVSAT_PMOS50={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DRDSW_PMOS50={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DJS_PMOS50={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DVTO_NMOS12={PROC_ON*AGAUSS(0,0.035,3)}
.param P_DUO_NMOS12={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DKP_NMOS12={PROC_ON*AGAUSS(0,0.12,3)}
.param P_DVMAX_NMOS12={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DRSH_NMOS12={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DVTO_PMOS12={PROC_ON*AGAUSS(0,0.035,3)}
.param P_DUO_PMOS12={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DKP_PMOS12={PROC_ON*AGAUSS(0,0.12,3)}
.param P_DVMAX_PMOS12={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DRSH_PMOS12={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DVTO_NDMOS20={PROC_ON*AGAUSS(0,0.04,3)}
.param P_DKP_NDMOS20={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRD_NDMOS20={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRS_NDMOS20={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_NDMOS20={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DVTO_PDMOS20={PROC_ON*AGAUSS(0,0.04,3)}
.param P_DKP_PDMOS20={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRD_PDMOS20={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRS_PDMOS20={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_PDMOS20={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DVTO_NDMOS60={PROC_ON*AGAUSS(0,0.045,3)}
.param P_DKP_NDMOS60={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRD_NDMOS60={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRS_NDMOS60={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_NDMOS60={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DVTO_PDMOS60={PROC_ON*AGAUSS(0,0.045,3)}
.param P_DKP_PDMOS60={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRD_PDMOS60={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRS_PDMOS60={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_PDMOS60={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DVTO_NDMOS120={PROC_ON*AGAUSS(0,0.05,3)}
.param P_DKP_NDMOS120={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRD_NDMOS120={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRS_NDMOS120={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_NDMOS120={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DVTO_PDMOS120={PROC_ON*AGAUSS(0,0.05,3)}
.param P_DKP_PDMOS120={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRD_PDMOS120={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRS_PDMOS120={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_PDMOS120={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DVTO_DNMOS20={PROC_ON*AGAUSS(0,0.04,3)}
.param P_DKP_DNMOS20={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRD_DNMOS20={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRS_DNMOS20={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_DNMOS20={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DVTO_NDMOS40={PROC_ON*AGAUSS(0,0.0425,3)}
.param P_DKP_NDMOS40={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRD_NDMOS40={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRS_NDMOS40={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_NDMOS40={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DVTO_PDMOS40={PROC_ON*AGAUSS(0,0.0425,3)}
.param P_DKP_PDMOS40={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRD_PDMOS40={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRS_PDMOS40={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_PDMOS40={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DVTO_NDMOS80={PROC_ON*AGAUSS(0,0.0475,3)}
.param P_DKP_NDMOS80={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRD_NDMOS80={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRS_NDMOS80={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_NDMOS80={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DVTO_PDMOS80={PROC_ON*AGAUSS(0,0.0475,3)}
.param P_DKP_PDMOS80={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRD_PDMOS80={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRS_PDMOS80={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_PDMOS80={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DVTO_NDMOS200={PROC_ON*AGAUSS(0,0.055,3)}
.param P_DKP_NDMOS200={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRD_NDMOS200={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRS_NDMOS200={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_NDMOS200={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DVTO_PDMOS200={PROC_ON*AGAUSS(0,0.055,3)}
.param P_DKP_PDMOS200={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRD_PDMOS200={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRS_PDMOS200={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_PDMOS200={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DIS_NPN_LV={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DBF_NPN_LV={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DRB_NPN_LV={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRC_NPN_LV={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRE_NPN_LV={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DTF_NPN_LV={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DTR_NPN_LV={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_NPN_LV={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DIS_PNP_LAT={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DBF_PNP_LAT={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DRB_PNP_LAT={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRC_PNP_LAT={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRE_PNP_LAT={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DTF_PNP_LAT={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DTR_PNP_LAT={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_PNP_LAT={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DIS_NPN_HV={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DBF_NPN_HV={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DRB_NPN_HV={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRC_NPN_HV={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRE_NPN_HV={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DTF_NPN_HV={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DTR_NPN_HV={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_NPN_HV={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DIS_PNP_HV={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DBF_PNP_HV={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DRB_PNP_HV={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRC_PNP_HV={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DRE_PNP_HV={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DTF_PNP_HV={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DTR_PNP_HV={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_PNP_HV={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DIS_DIO_PN={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DRS_DIO_PN={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_DIO_PN={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DCJO_DIO_PN={PROC_ON*AGAUSS(0,0.05,3)}
.param P_DTT_DIO_PN={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DIS_DIO_FAST={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DRS_DIO_FAST={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_DIO_FAST={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DCJO_DIO_FAST={PROC_ON*AGAUSS(0,0.05,3)}
.param P_DTT_DIO_FAST={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DIS_DIO_SCH={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DRS_DIO_SCH={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_DIO_SCH={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DCJO_DIO_SCH={PROC_ON*AGAUSS(0,0.05,3)}
.param P_DTT_DIO_SCH={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DIS_DZ_5V6={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DRS_DZ_5V6={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_DZ_5V6={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DCJO_DZ_5V6={PROC_ON*AGAUSS(0,0.05,3)}
.param P_DTT_DZ_5V6={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DIS_DZ_12={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DRS_DZ_12={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_DZ_12={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DCJO_DZ_12={PROC_ON*AGAUSS(0,0.05,3)}
.param P_DTT_DZ_12={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DIS_DZ_24={PROC_ON*AGAUSS(0,0.2,3)}
.param P_DRS_DZ_24={PROC_ON*AGAUSS(0,0.1,3)}
.param P_DBV_DZ_24={PROC_ON*AGAUSS(0,0.03,3)}
.param P_DCJO_DZ_24={PROC_ON*AGAUSS(0,0.05,3)}
.param P_DTT_DZ_24={PROC_ON*AGAUSS(0,0.1,3)}
* Die-to-die absolute tolerance is layer-dependent (random part of "absolute
* accuracy"). Low-sheet poly is tightest; lightly-doped well is widest. Ranges
* follow the trend in Allen, CMOS Analog Circuit Design (poly ~+/-30%, n-well
* ~+/-40% absolute) and the high-sheet-implant tolerance note in US Pat 6,313,516.
.param P_DRSH_RPOLY_HI={PROC_ON*AGAUSS(0,0.18,3)}
.param P_DRSH_RPOLY_LO={PROC_ON*AGAUSS(0,0.12,3)}
.param P_DRSH_RNWELL={PROC_ON*AGAUSS(0,0.30,3)}
.param P_DRSH_RNPLUS={PROC_ON*AGAUSS(0,0.18,3)}
.param P_DRSH_RPPLUS={PROC_ON*AGAUSS(0,0.18,3)}
.param P_DCJ_CMIM_STD={PROC_ON*AGAUSS(0,0.05,3)}
.param P_DCJ_CMIM_HI={PROC_ON*AGAUSS(0,0.05,3)}
.param P_DCJ_CMOM={PROC_ON*AGAUSS(0,0.05,3)}
.param P_DCJ_CFRINGE={PROC_ON*AGAUSS(0,0.05,3)}
.param P_DCJSW_CFRINGE={PROC_ON*AGAUSS(0,0.05,3)}


* === VDMOS temperature coefficients (deterministic; CALIBRATE) ===========
* Applied via runtime 'temper' to vto/kp/rd/rs of each HV drift-MOS card.
* Sign convention: rd,rs rise with T (+), kp falls (-), vto falls (-).
.param TC_RD_NDMOS20=0.005
.param TC_RS_NDMOS20=0.004
.param TC_KP_NDMOS20=-0.005
.param TC_VTO_NDMOS20=-0.002
.param TC_RD_PDMOS20=0.005
.param TC_RS_PDMOS20=0.004
.param TC_KP_PDMOS20=-0.005
.param TC_VTO_PDMOS20=-0.002
.param TC_RD_DNMOS20=0.005
.param TC_RS_DNMOS20=0.004
.param TC_KP_DNMOS20=-0.005
.param TC_VTO_DNMOS20=-0.002
.param TC_RD_NDMOS40=0.0055
.param TC_RS_NDMOS40=0.0045
.param TC_KP_NDMOS40=-0.0052
.param TC_VTO_NDMOS40=-0.0022
.param TC_RD_PDMOS40=0.0055
.param TC_RS_PDMOS40=0.0045
.param TC_KP_PDMOS40=-0.0052
.param TC_VTO_PDMOS40=-0.0022
.param TC_RD_NDMOS60=0.006
.param TC_RS_NDMOS60=0.0048
.param TC_KP_NDMOS60=-0.0055
.param TC_VTO_NDMOS60=-0.0023
.param TC_RD_PDMOS60=0.006
.param TC_RS_PDMOS60=0.0048
.param TC_KP_PDMOS60=-0.0055
.param TC_VTO_PDMOS60=-0.0023
.param TC_RD_NDMOS80=0.0065
.param TC_RS_NDMOS80=0.005
.param TC_KP_NDMOS80=-0.0055
.param TC_VTO_NDMOS80=-0.0024
.param TC_RD_PDMOS80=0.0065
.param TC_RS_PDMOS80=0.005
.param TC_KP_PDMOS80=-0.0055
.param TC_VTO_PDMOS80=-0.0024
.param TC_RD_NDMOS120=0.0075
.param TC_RS_NDMOS120=0.0055
.param TC_KP_NDMOS120=-0.0058
.param TC_VTO_NDMOS120=-0.0025
.param TC_RD_PDMOS120=0.0075
.param TC_RS_PDMOS120=0.0055
.param TC_KP_PDMOS120=-0.0058
.param TC_VTO_PDMOS120=-0.0025
.param TC_RD_NDMOS200=0.009
.param TC_RS_NDMOS200=0.006
.param TC_KP_NDMOS200=-0.006
.param TC_VTO_NDMOS200=-0.0028
.param TC_RD_PDMOS200=0.009
.param TC_RS_PDMOS200=0.006
.param TC_KP_PDMOS200=-0.006
.param TC_VTO_PDMOS200=-0.0028
* =========================================================================

* === VDMOS parse-time statistical params (corner * (1+P_D*) products) ====
* These hoist the agauss-bearing part of each VDMOS vto/kp/rd/rs out of the
* model-card expressions, so the braced expressions on the cards contain
* only numbers + the runtime 'temper'. ngspice defers any expression that
* mentions temper to runtime per-temperature evaluation, where agauss is
* unresolvable; isolating the statistical product here keeps it parse-time.
* Each card line then reads e.g. vto={VTO_<dev>_STAT + TC_VTO_<dev>*(temper-27)}.
.param VTO_NDMOS20_STAT={(((1*_isTT + 0.96*_isFF + 1.06*_isSS + 0.96*_isFS + 1.06*_isSF))+P_DVTO_NDMOS20)}
.param KP_NDMOS20_STAT={(((2.8*_isTT + 3.248*_isFF + 2.408*_isSS + 3.248*_isFS + 2.408*_isSF))*(1+P_DKP_NDMOS20))}
.param RD_NDMOS20_STAT={(((0.045*_isTT + 0.0396*_isFF + 0.05175*_isSS + 0.0396*_isFS + 0.05175*_isSF))*(1+P_DRD_NDMOS20))}
.param RS_NDMOS20_STAT={(((0.025*_isTT + 0.022*_isFF + 0.02875*_isSS + 0.022*_isFS + 0.02875*_isSF))*(1+P_DRS_NDMOS20))}
.param VTO_PDMOS20_STAT={(((-1.05*_isTT + -1*_isFF + -1.11*_isSS + -1.11*_isFS + -1*_isSF))+P_DVTO_PDMOS20)}
.param KP_PDMOS20_STAT={(((1.3*_isTT + 1.482*_isFF + 1.144*_isSS + 1.144*_isFS + 1.482*_isSF))*(1+P_DKP_PDMOS20))}
.param RD_PDMOS20_STAT={(((0.07*_isTT + 0.063*_isFF + 0.0791*_isSS + 0.0791*_isFS + 0.063*_isSF))*(1+P_DRD_PDMOS20))}
.param RS_PDMOS20_STAT={(((0.04*_isTT + 0.036*_isFF + 0.0452*_isSS + 0.0452*_isFS + 0.036*_isSF))*(1+P_DRS_PDMOS20))}
.param VTO_NDMOS60_STAT={(((1.1*_isTT + 1.05*_isFF + 1.17*_isSS + 1.05*_isFS + 1.17*_isSF))+P_DVTO_NDMOS60)}
.param KP_NDMOS60_STAT={(((1.2*_isTT + 1.368*_isFF + 1.056*_isSS + 1.368*_isFS + 1.056*_isSF))*(1+P_DKP_NDMOS60))}
.param RD_NDMOS60_STAT={(((0.16*_isTT + 0.144*_isFF + 0.1808*_isSS + 0.144*_isFS + 0.1808*_isSF))*(1+P_DRD_NDMOS60))}
.param RS_NDMOS60_STAT={(((0.08*_isTT + 0.072*_isFF + 0.0904*_isSS + 0.072*_isFS + 0.0904*_isSF))*(1+P_DRS_NDMOS60))}
.param VTO_PDMOS60_STAT={(((-1.15*_isTT + -1.09*_isFF + -1.23*_isSS + -1.23*_isFS + -1.09*_isSF))+P_DVTO_PDMOS60)}
.param KP_PDMOS60_STAT={(((0.55*_isTT + 0.616*_isFF + 0.4895*_isSS + 0.4895*_isFS + 0.616*_isSF))*(1+P_DKP_PDMOS60))}
.param RD_PDMOS60_STAT={(((0.35*_isTT + 0.3185*_isFF + 0.392*_isSS + 0.392*_isFS + 0.3185*_isSF))*(1+P_DRD_PDMOS60))}
.param RS_PDMOS60_STAT={(((0.18*_isTT + 0.1638*_isFF + 0.2016*_isSS + 0.2016*_isFS + 0.1638*_isSF))*(1+P_DRS_PDMOS60))}
.param VTO_NDMOS120_STAT={(((1.2*_isTT + 1.14*_isFF + 1.28*_isSS + 1.14*_isFS + 1.28*_isSF))+P_DVTO_NDMOS120)}
.param KP_NDMOS120_STAT={(((0.45*_isTT + 0.4995*_isFF + 0.405*_isSS + 0.4995*_isFS + 0.405*_isSF))*(1+P_DKP_NDMOS120))}
.param RD_NDMOS120_STAT={(((0.55*_isTT + 0.506*_isFF + 0.6105*_isSS + 0.506*_isFS + 0.6105*_isSF))*(1+P_DRD_NDMOS120))}
.param RS_NDMOS120_STAT={(((0.25*_isTT + 0.23*_isFF + 0.2775*_isSS + 0.23*_isFS + 0.2775*_isSF))*(1+P_DRS_NDMOS120))}
.param VTO_PDMOS120_STAT={(((-1.25*_isTT + -1.1875*_isFF + -1.34375*_isSS + -1.34375*_isFS + -1.1875*_isSF))+P_DVTO_PDMOS120)}
.param KP_PDMOS120_STAT={(((0.21*_isTT + 0.2331*_isFF + 0.189*_isSS + 0.189*_isFS + 0.2331*_isSF))*(1+P_DKP_PDMOS120))}
.param RD_PDMOS120_STAT={(((1.15*_isTT + 1.058*_isFF + 1.2765*_isSS + 1.2765*_isFS + 1.058*_isSF))*(1+P_DRD_PDMOS120))}
.param RS_PDMOS120_STAT={(((0.58*_isTT + 0.5336*_isFF + 0.6438*_isSS + 0.6438*_isFS + 0.5336*_isSF))*(1+P_DRS_PDMOS120))}
.param VTO_NDMOS40_STAT={(((1.05*_isTT + 1*_isFF + 1.11*_isSS + 1*_isFS + 1.11*_isSF))+P_DVTO_NDMOS40)}
.param KP_NDMOS40_STAT={(((1.9*_isTT + 2.185*_isFF + 1.653*_isSS + 2.185*_isFS + 1.653*_isSF))*(1+P_DKP_NDMOS40))}
.param RD_NDMOS40_STAT={(((0.09*_isTT + 0.0801*_isFF + 0.1026*_isSS + 0.0801*_isFS + 0.1026*_isSF))*(1+P_DRD_NDMOS40))}
.param RS_NDMOS40_STAT={(((0.045*_isTT + 0.04005*_isFF + 0.0513*_isSS + 0.04005*_isFS + 0.0513*_isSF))*(1+P_DRS_NDMOS40))}
.param VTO_PDMOS40_STAT={(((-1.1*_isTT + -1.04*_isFF + -1.17*_isSS + -1.17*_isFS + -1.04*_isSF))+P_DVTO_PDMOS40)}
.param KP_PDMOS40_STAT={(((0.85*_isTT + 0.9605*_isFF + 0.748*_isSS + 0.748*_isFS + 0.9605*_isSF))*(1+P_DKP_PDMOS40))}
.param RD_PDMOS40_STAT={(((0.16*_isTT + 0.144*_isFF + 0.1808*_isSS + 0.1808*_isFS + 0.144*_isSF))*(1+P_DRD_PDMOS40))}
.param RS_PDMOS40_STAT={(((0.09*_isTT + 0.081*_isFF + 0.1017*_isSS + 0.1017*_isFS + 0.081*_isSF))*(1+P_DRS_PDMOS40))}
.param VTO_NDMOS80_STAT={(((1.15*_isTT + 1.09*_isFF + 1.22*_isSS + 1.09*_isFS + 1.22*_isSF))+P_DVTO_NDMOS80)}
.param KP_NDMOS80_STAT={(((0.8*_isTT + 0.904*_isFF + 0.712*_isSS + 0.904*_isFS + 0.712*_isSF))*(1+P_DKP_NDMOS80))}
.param RD_NDMOS80_STAT={(((0.26*_isTT + 0.2366*_isFF + 0.2912*_isSS + 0.2366*_isFS + 0.2912*_isSF))*(1+P_DRD_NDMOS80))}
.param RS_NDMOS80_STAT={(((0.12*_isTT + 0.1092*_isFF + 0.1344*_isSS + 0.1092*_isFS + 0.1344*_isSF))*(1+P_DRS_NDMOS80))}
.param VTO_PDMOS80_STAT={(((-1.2*_isTT + -1.14*_isFF + -1.29*_isSS + -1.29*_isFS + -1.14*_isSF))+P_DVTO_PDMOS80)}
.param KP_PDMOS80_STAT={(((0.38*_isTT + 0.4218*_isFF + 0.342*_isSS + 0.342*_isFS + 0.4218*_isSF))*(1+P_DKP_PDMOS80))}
.param RD_PDMOS80_STAT={(((0.55*_isTT + 0.506*_isFF + 0.6105*_isSS + 0.6105*_isFS + 0.506*_isSF))*(1+P_DRD_PDMOS80))}
.param RS_PDMOS80_STAT={(((0.28*_isTT + 0.2576*_isFF + 0.3108*_isSS + 0.3108*_isFS + 0.2576*_isSF))*(1+P_DRS_PDMOS80))}
.param VTO_NDMOS200_STAT={(((1.25*_isTT + 1.19*_isFF + 1.34*_isSS + 1.19*_isFS + 1.34*_isSF))+P_DVTO_NDMOS200)}
.param KP_NDMOS200_STAT={(((0.22*_isTT + 0.2398*_isFF + 0.2024*_isSS + 0.2398*_isFS + 0.2024*_isSF))*(1+P_DKP_NDMOS200))}
.param RD_NDMOS200_STAT={(((1.2*_isTT + 1.116*_isFF + 1.32*_isSS + 1.116*_isFS + 1.32*_isSF))*(1+P_DRD_NDMOS200))}
.param RS_NDMOS200_STAT={(((0.55*_isTT + 0.5115*_isFF + 0.605*_isSS + 0.5115*_isFS + 0.605*_isSF))*(1+P_DRS_NDMOS200))}
.param VTO_PDMOS200_STAT={(((-1.31*_isTT + -1.247*_isFF + -1.404*_isSS + -1.404*_isFS + -1.247*_isSF))+P_DVTO_PDMOS200)}
.param KP_PDMOS200_STAT={(((0.088*_isTT + 0.0959*_isFF + 0.081*_isSS + 0.081*_isFS + 0.0959*_isSF))*(1+P_DKP_PDMOS200))}
.param RD_PDMOS200_STAT={(((3.0*_isTT + 2.79*_isFF + 3.3*_isSS + 3.3*_isFS + 2.79*_isSF))*(1+P_DRD_PDMOS200))}
.param RS_PDMOS200_STAT={(((1.38*_isTT + 1.283*_isFF + 1.518*_isSS + 1.518*_isFS + 1.283*_isSF))*(1+P_DRS_PDMOS200))}
.param VTO_DNMOS20_STAT={(((-0.9*_isTT + -0.94*_isFF + -0.85*_isSS + -0.94*_isFS + -0.85*_isSF))+P_DVTO_DNMOS20)}
.param KP_DNMOS20_STAT={(((1*_isTT + 1.12*_isFF + 0.9*_isSS + 1.12*_isFS + 0.9*_isSF))*(1+P_DKP_DNMOS20))}
.param RD_DNMOS20_STAT={(((0.12*_isTT + 0.108*_isFF + 0.1344*_isSS + 0.108*_isFS + 0.1344*_isSF))*(1+P_DRD_DNMOS20))}
.param RS_DNMOS20_STAT={(((0.06*_isTT + 0.054*_isFF + 0.0672*_isSS + 0.054*_isFS + 0.0672*_isSF))*(1+P_DRS_DNMOS20))}
* =========================================================================

* ============================== DEVICE MODELS ===============================
.model NMOS18_INT NMOS (
+ level=49
+ version=3.3.0
+ tnom=27
+ binunit=1  $ NOTE: single global fit, no L/W bins defined
+ mobmod=1
+ capmod=3
+ noimod=2
+ tox={((4.25e-09*_isTT + 4.2075e-09*_isFF + 4.2925e-09*_isSS + 4.25e-09*_isFS + 4.25e-09*_isSF))*(1+P_TOX_18)}
+ xj=1.4e-07
+ nch=2.2e+17
+ nsub=5.5e+16
+ vth0={((0.48*_isTT + 0.4*_isFF + 0.56*_isSS + 0.4*_isFS + 0.56*_isSF))+P_DVTH_NMOS18}
+ k1=0.56
+ k2=-0.045
+ u0={((420*_isTT + 495.6*_isFF + 352.8*_isSS + 495.6*_isFS + 352.8*_isSF))*(1+P_DU0_NMOS18)}
+ ua=1.8e-09
+ ub=5e-19
+ uc=-5e-11
+ vsat={((140000*_isTT + 142520*_isFF + 137760*_isSS + 142520*_isFS + 137760*_isSF))*(1+P_DVSAT_NMOS18)}
+ a0=1
+ ags=0.22
+ nfactor=1.6
+ voff=-0.09
+ dvt0=2.2
+ dvt1=0.53
+ dvt2=-0.035
+ eta0=0.08
+ etab=-0.02
+ pclm={(1.2*_isTT + 1.21728*_isFF + 1.18464*_isSS + 1.2*_isFS + 1.2*_isSF)}
+ pdiblc1=0.18
+ pdiblc2=0.015
+ drout=0.45
+ prwg=0.08
+ prwb=-0.02
+ wr=1
+ wint=5e-09
+ lint=1.2e-08
+ dwg=3e-09
+ dwb=2e-09
+ rdsw={((120*_isTT + 101.69492*_isFF + 142.85714*_isSS + 101.69492*_isFS + 142.85714*_isSF))*(1+P_DRDSW_NMOS18)}
+ cgso=2.2e-10
+ cgdo=2.2e-10
+ cgbo=5e-10
+ cj={((0.001*_isTT + 0.0010009*_isFF + 0.0009991*_isSS + 0.001*_isFS + 0.001*_isSF))*(1+P_CJ_18)}
+ cjsw={((2.8e-10*_isTT + 2.80252e-10*_isFF + 2.79748e-10*_isSS + 2.8e-10*_isFS + 2.8e-10*_isSF))*(1+P_CJSW_18)}
+ pb=0.92
+ pbsw=0.92
+ mj=0.46
+ mjsw=0.32
+ js={((2e-08*_isTT + 2.036e-08*_isFF + 1.968e-08*_isSS + 2e-08*_isFS + 2e-08*_isSF))*(1+P_DJS_NMOS18)}
+ )

.model PMOS18_INT PMOS (
+ level=49
+ version=3.3.0
+ tnom=27
+ binunit=1  $ NOTE: single global fit, no L/W bins defined
+ mobmod=1
+ capmod=3
+ noimod=2
+ tox={((4.25e-09*_isTT + 4.2075e-09*_isFF + 4.2925e-09*_isSS + 4.25e-09*_isFS + 4.25e-09*_isSF))*(1+P_TOX_18)}
+ xj=1.5e-07
+ nch=2.5e+17
+ nsub=6e+16
+ vth0={((-0.52*_isTT + -0.44*_isFF + -0.6*_isSS + -0.6*_isFS + -0.44*_isSF))+P_DVTH_PMOS18}
+ k1=0.63
+ k2=-0.055
+ u0={((145*_isTT + 174*_isFF + 118.9*_isSS + 118.9*_isFS + 174*_isSF))*(1+P_DU0_PMOS18)}
+ ua=2.2e-09
+ ub=8e-19
+ uc=-1e-10
+ vsat={((100000*_isTT + 102000*_isFF + 98200*_isSS + 98200*_isFS + 102000*_isSF))*(1+P_DVSAT_PMOS18)}
+ a0=1.05
+ ags=0.24
+ nfactor=1.75
+ voff=-0.1
+ dvt0=2.3
+ dvt1=0.56
+ dvt2=-0.04
+ eta0=0.09
+ etab=-0.02
+ pclm={(1.35*_isTT + 1.3716*_isFF + 1.33056*_isSS + 1.35*_isFS + 1.35*_isSF)}
+ pdiblc1=0.22
+ pdiblc2=0.02
+ drout=0.55
+ prwg=0.1
+ prwb=-0.025
+ wr=1
+ wint=7e-09
+ lint=1.5e-08
+ dwg=4e-09
+ dwb=3e-09
+ rdsw={((180*_isTT + 150*_isFF + 219.5122*_isSS + 219.5122*_isFS + 150*_isSF))*(1+P_DRDSW_PMOS18)}
+ cgso=2.4e-10
+ cgdo=2.4e-10
+ cgbo=5.2e-10
+ cj={((0.00105*_isTT + 0.001050945*_isFF + 0.001049055*_isSS + 0.00105*_isFS + 0.00105*_isSF))*(1+P_CJ_18)}
+ cjsw={((3e-10*_isTT + 3.0027e-10*_isFF + 2.9973e-10*_isSS + 3e-10*_isFS + 3e-10*_isSF))*(1+P_CJSW_18)}
+ pb=0.9
+ pbsw=0.9
+ mj=0.45
+ mjsw=0.31
+ js={((3e-08*_isTT + 3.06e-08*_isFF + 2.946e-08*_isSS + 3e-08*_isFS + 3e-08*_isSF))*(1+P_DJS_PMOS18)}
+ )

.model NMOS33_INT NMOS (
+ level=49
+ version=3.3.0
+ tnom=27
+ binunit=1  $ NOTE: single global fit, no L/W bins defined
+ mobmod=1
+ capmod=3
+ noimod=2
+ tox={((6.75e-09*_isTT + 6.6825e-09*_isFF + 6.8175e-09*_isSS + 6.75e-09*_isFS + 6.75e-09*_isSF))*(1+P_TOX_33)}
+ xj=1.8e-07
+ nch=1.7e+17
+ nsub=4e+16
+ vth0={((0.66*_isTT + 0.58*_isFF + 0.74*_isSS + 0.58*_isFS + 0.74*_isSF))+P_DVTH_NMOS33}
+ k1=0.62
+ k2=-0.04
+ u0={((300*_isTT + 354*_isFF + 252*_isSS + 354*_isFS + 252*_isSF))*(1+P_DU0_NMOS33)}
+ ua=2e-09
+ ub=6e-19
+ uc=-4e-11
+ vsat={((110000*_isTT + 111980*_isFF + 108240*_isSS + 111980*_isFS + 108240*_isSF))*(1+P_DVSAT_NMOS33)}
+ a0=1
+ ags=0.2
+ nfactor=1.65
+ voff=-0.08
+ dvt0=2
+ dvt1=0.48
+ dvt2=-0.025
+ eta0=0.06
+ etab=-0.015
+ pclm={(1.1*_isTT + 1.11584*_isFF + 1.08592*_isSS + 1.1*_isFS + 1.1*_isSF)}
+ pdiblc1=0.14
+ pdiblc2=0.012
+ drout=0.42
+ prwg=0.06
+ prwb=-0.015
+ wr=1
+ wint=8e-09
+ lint=1.8e-08
+ dwg=5e-09
+ dwb=3e-09
+ rdsw={((160*_isTT + 135.59322*_isFF + 190.47619*_isSS + 135.59322*_isFS + 190.47619*_isSF))*(1+P_DRDSW_NMOS33)}
+ cgso=2e-10
+ cgdo=2e-10
+ cgbo=4.5e-10
+ cj={((0.00082*_isTT + 0.000820738*_isFF + 0.000819262*_isSS + 0.00082*_isFS + 0.00082*_isSF))*(1+P_CJ_33)}
+ cjsw={((2.4e-10*_isTT + 2.40216e-10*_isFF + 2.39784e-10*_isSS + 2.4e-10*_isFS + 2.4e-10*_isSF))*(1+P_CJSW_33)}
+ pb=0.95
+ pbsw=0.95
+ mj=0.45
+ mjsw=0.3
+ js={((1.2e-08*_isTT + 1.2216e-08*_isFF + 1.1808e-08*_isSS + 1.2e-08*_isFS + 1.2e-08*_isSF))*(1+P_DJS_NMOS33)}
+ )

.model PMOS33_INT PMOS (
+ level=49
+ version=3.3.0
+ tnom=27
+ binunit=1  $ NOTE: single global fit, no L/W bins defined
+ mobmod=1
+ capmod=3
+ noimod=2
+ tox={((6.75e-09*_isTT + 6.6825e-09*_isFF + 6.8175e-09*_isSS + 6.75e-09*_isFS + 6.75e-09*_isSF))*(1+P_TOX_33)}
+ xj=2e-07
+ nch=1.9e+17
+ nsub=4.6e+16
+ vth0={((-0.74*_isTT + -0.66*_isFF + -0.82*_isSS + -0.82*_isFS + -0.66*_isSF))+P_DVTH_PMOS33}
+ k1=0.7
+ k2=-0.05
+ u0={((115*_isTT + 138*_isFF + 94.3*_isSS + 94.3*_isFS + 138*_isSF))*(1+P_DU0_PMOS33)}
+ ua=2.5e-09
+ ub=8.5e-19
+ uc=-8e-11
+ vsat={((85000*_isTT + 86700*_isFF + 83470*_isSS + 83470*_isFS + 86700*_isSF))*(1+P_DVSAT_PMOS33)}
+ a0=1.05
+ ags=0.22
+ nfactor=1.8
+ voff=-0.09
+ dvt0=2.1
+ dvt1=0.5
+ dvt2=-0.03
+ eta0=0.07
+ etab=-0.02
+ pclm={(1.2*_isTT + 1.2192*_isFF + 1.18272*_isSS + 1.2*_isFS + 1.2*_isSF)}
+ pdiblc1=0.18
+ pdiblc2=0.015
+ drout=0.5
+ prwg=0.08
+ prwb=-0.02
+ wr=1
+ wint=1e-08
+ lint=2e-08
+ dwg=6e-09
+ dwb=4e-09
+ rdsw={((240*_isTT + 200*_isFF + 292.68293*_isSS + 292.68293*_isFS + 200*_isSF))*(1+P_DRDSW_PMOS33)}
+ cgso=2.2e-10
+ cgdo=2.2e-10
+ cgbo=4.8e-10
+ cj={((0.00088*_isTT + 0.000880792*_isFF + 0.000879208*_isSS + 0.00088*_isFS + 0.00088*_isSF))*(1+P_CJ_33)}
+ cjsw={((2.6e-10*_isTT + 2.60234e-10*_isFF + 2.59766e-10*_isSS + 2.6e-10*_isFS + 2.6e-10*_isSF))*(1+P_CJSW_33)}
+ pb=0.93
+ pbsw=0.93
+ mj=0.44
+ mjsw=0.29
+ js={((1.6e-08*_isTT + 1.632e-08*_isFF + 1.5712e-08*_isSS + 1.6e-08*_isFS + 1.6e-08*_isSF))*(1+P_DJS_PMOS33)}
+ )

.model NMOS50_INT NMOS (
+ level=49
+ version=3.3.0
+ tnom=27
+ binunit=1  $ NOTE: single global fit, no L/W bins defined
+ mobmod=1
+ capmod=3
+ noimod=2
+ tox={((1.1e-08*_isTT + 1.089e-08*_isFF + 1.111e-08*_isSS + 1.1e-08*_isFS + 1.1e-08*_isSF))*(1+P_TOX_50)}
+ xj=2.6e-07
+ nch=1.2e+17
+ nsub=2.8e+16
+ vth0={((0.88*_isTT + 0.8*_isFF + 0.96*_isSS + 0.8*_isFS + 0.96*_isSF))+P_DVTH_NMOS50}
+ k1=0.68
+ k2=-0.03
+ u0={((190*_isTT + 224.2*_isFF + 159.6*_isSS + 224.2*_isFS + 159.6*_isSF))*(1+P_DU0_NMOS50)}
+ ua=2.3e-09
+ ub=6.5e-19
+ uc=-3e-11
+ vsat={((80000*_isTT + 81440*_isFF + 78720*_isSS + 81440*_isFS + 78720*_isSF))*(1+P_DVSAT_NMOS50)}
+ a0=1
+ ags=0.18
+ nfactor=1.7
+ voff=-0.07
+ dvt0=1.8
+ dvt1=0.4
+ dvt2=-0.02
+ eta0=0.04
+ etab=-0.01
+ pclm={(0.95*_isTT + 0.96368*_isFF + 0.93784*_isSS + 0.95*_isFS + 0.95*_isSF)}
+ pdiblc1=0.1
+ pdiblc2=0.01
+ drout=0.35
+ prwg=0.05
+ prwb=-0.01
+ wr=1
+ wint=1.2e-08
+ lint=2.5e-08
+ dwg=8e-09
+ dwb=5e-09
+ rdsw={((280*_isTT + 237.28814*_isFF + 333.33333*_isSS + 237.28814*_isFS + 333.33333*_isSF))*(1+P_DRDSW_NMOS50)}
+ cgso=1.8e-10
+ cgdo=1.8e-10
+ cgbo=4.2e-10
+ cj={((0.0006*_isTT + 0.00060054*_isFF + 0.00059946*_isSS + 0.0006*_isFS + 0.0006*_isSF))*(1+P_CJ_50)}
+ cjsw={((1.8e-10*_isTT + 1.80162e-10*_isFF + 1.79838e-10*_isSS + 1.8e-10*_isFS + 1.8e-10*_isSF))*(1+P_CJSW_50)}
+ pb=0.97
+ pbsw=0.97
+ mj=0.43
+ mjsw=0.28
+ js={((6e-09*_isTT + 6.108e-09*_isFF + 5.904e-09*_isSS + 6e-09*_isFS + 6e-09*_isSF))*(1+P_DJS_NMOS50)}
+ )

.model PMOS50_INT PMOS (
+ level=49
+ version=3.3.0
+ tnom=27
+ binunit=1  $ NOTE: single global fit, no L/W bins defined
+ mobmod=1
+ capmod=3
+ noimod=2
+ tox={((1.1e-08*_isTT + 1.089e-08*_isFF + 1.111e-08*_isSS + 1.1e-08*_isFS + 1.1e-08*_isSF))*(1+P_TOX_50)}
+ xj=2.9e-07
+ nch=1.4e+17
+ nsub=3.2e+16
+ vth0={((-0.98*_isTT + -0.9*_isFF + -1.06*_isSS + -1.06*_isFS + -0.9*_isSF))+P_DVTH_PMOS50}
+ k1=0.78
+ k2=-0.04
+ u0={((80*_isTT + 96*_isFF + 65.6*_isSS + 65.6*_isFS + 96*_isSF))*(1+P_DU0_PMOS50)}
+ ua=2.8e-09
+ ub=9e-19
+ uc=-6e-11
+ vsat={((65000*_isTT + 66300*_isFF + 63830*_isSS + 63830*_isFS + 66300*_isSF))*(1+P_DVSAT_PMOS50)}
+ a0=1.05
+ ags=0.2
+ nfactor=1.9
+ voff=-0.08
+ dvt0=1.9
+ dvt1=0.42
+ dvt2=-0.025
+ eta0=0.05
+ etab=-0.015
+ pclm={(1*_isTT + 1.016*_isFF + 0.9856*_isSS + 1*_isFS + 1*_isSF)}
+ pdiblc1=0.12
+ pdiblc2=0.012
+ drout=0.42
+ prwg=0.06
+ prwb=-0.015
+ wr=1
+ wint=1.4e-08
+ lint=2.8e-08
+ dwg=9e-09
+ dwb=6e-09
+ rdsw={((380*_isTT + 316.66667*_isFF + 463.41463*_isSS + 463.41463*_isFS + 316.66667*_isSF))*(1+P_DRDSW_PMOS50)}
+ cgso=1.9e-10
+ cgdo=1.9e-10
+ cgbo=4.3e-10
+ cj={((0.00064*_isTT + 0.000640576*_isFF + 0.000639424*_isSS + 0.00064*_isFS + 0.00064*_isSF))*(1+P_CJ_50)}
+ cjsw={((1.9e-10*_isTT + 1.90171e-10*_isFF + 1.89829e-10*_isSS + 1.9e-10*_isFS + 1.9e-10*_isSF))*(1+P_CJSW_50)}
+ pb=0.95
+ pbsw=0.95
+ mj=0.42
+ mjsw=0.27
+ js={((8e-09*_isTT + 8.16e-09*_isFF + 7.856e-09*_isSS + 8e-09*_isFS + 8e-09*_isSF))*(1+P_DJS_PMOS50)}
+ )

.model NMOS12_INT NMOS (
+ level=49
+ version=3.3.0
+ tnom=27
+ mobmod=1
+ capmod=3
+ noimod=2
+ tox=2e-08
+ xj=5e-07
+ nch=9e+16
+ nsub=2e+16
+ vth0={((1.35*_isTT + 1.27*_isFF + 1.43*_isSS + 1.27*_isFS + 1.43*_isSF))+P_DVTO_NMOS12}
+ k1=0.75
+ k2=-0.03
+ u0={((120*_isTT + 141.6*_isFF + 100.8*_isSS + 141.6*_isFS + 100.8*_isSF))*(1+P_DUO_NMOS12)*(1+P_DKP_NMOS12)}
+ ua=2.5e-09
+ ub=7e-19
+ uc=-2e-11
+ vsat={((75000*_isTT + 76200*_isFF + 73800*_isSS + 76200*_isFS + 73800*_isSF))*(1+P_DVMAX_NMOS12)}
+ a0=1
+ ags=0.16
+ nfactor=1.7
+ voff=-0.07
+ dvt0=1.6
+ dvt1=0.38
+ dvt2=-0.018
+ eta0=0.03
+ etab=-0.008
+ pclm=0.9
+ pdiblc1=0.08
+ pdiblc2=0.008
+ drout=0.32
+ prwg=0.04
+ prwb=-0.008
+ wr=1
+ wint=1.5e-08
+ lint=3e-08
+ dwg=1e-08
+ dwb=6e-09
+ rdsw={((30*_isTT + 25.42*_isFF + 35.71*_isSS + 25.42*_isFS + 35.71*_isSF))*(1+P_DRSH_NMOS12)}
+ cgso=1.5e-10
+ cgdo=1.5e-10
+ cgbo=5e-11
+ cj=0.00035
+ cjsw=1.2e-10
+ pb=0.98
+ pbsw=0.98
+ mj=0.4
+ mjsw=0.26
+ js=3e-09
+ )

.model PMOS12_INT PMOS (
+ level=49
+ version=3.3.0
+ tnom=27
+ mobmod=1
+ capmod=3
+ noimod=2
+ tox=2.1e-08
+ xj=5.5e-07
+ nch=1.1e+17
+ nsub=2.4e+16
+ vth0={((-1.55*_isTT + -1.47*_isFF + -1.63*_isSS + -1.63*_isFS + -1.47*_isSF))+P_DVTO_PMOS12}
+ k1=0.82
+ k2=-0.04
+ u0={((60*_isTT + 72*_isFF + 49.2*_isSS + 49.2*_isFS + 72*_isSF))*(1+P_DUO_PMOS12)*(1+P_DKP_PMOS12)}
+ ua=3e-09
+ ub=9e-19
+ uc=-4e-11
+ vsat={((62000*_isTT + 62992*_isFF + 61256*_isSS + 61256*_isFS + 62992*_isSF))*(1+P_DVMAX_PMOS12)}
+ a0=1.05
+ ags=0.18
+ nfactor=1.85
+ voff=-0.08
+ dvt0=1.7
+ dvt1=0.4
+ dvt2=-0.022
+ eta0=0.04
+ etab=-0.01
+ pclm=0.95
+ pdiblc1=0.1
+ pdiblc2=0.01
+ drout=0.38
+ prwg=0.05
+ prwb=-0.01
+ wr=1
+ wint=1.6e-08
+ lint=3.2e-08
+ dwg=1.1e-08
+ dwb=7e-09
+ rdsw={((34*_isTT + 28.33*_isFF + 41.46*_isSS + 41.46*_isFS + 28.33*_isSF))*(1+P_DRSH_PMOS12)}
+ cgso=1.6e-10
+ cgdo=1.6e-10
+ cgbo=5.2e-11
+ cj=0.00038
+ cjsw=1.3e-10
+ pb=0.97
+ pbsw=0.97
+ mj=0.39
+ mjsw=0.25
+ js=4e-09
+ )

.model NDMOS20_INT VDMOS (nchan
+ vto={VTO_NDMOS20_STAT+TC_VTO_NDMOS20*(temper-27)}
+ kp={KP_NDMOS20_STAT*(1+TC_KP_NDMOS20*(temper-27))}
+ lambda=0.008
+ theta=0.04
+ rd={RD_NDMOS20_STAT*(1+TC_RD_NDMOS20*(temper-27))}
+ rs={RS_NDMOS20_STAT*(1+TC_RS_NDMOS20*(temper-27))}
+ rg=2
+ rds=1e+09
+ cgdmax=4.032e-10
+ cgdmin=3.5e-11
+ a=0.32
+ cgs=4.992e-10
+ cjo=1.4e-10
+ is=5e-13
+ rb=0.06
+ bv={((24*_isTT + 23.4*_isFF + 24.6*_isSS + 23.4*_isFS + 24.6*_isSF))*(1+P_DBV_NDMOS20)}
+ ibv=5e-05
+ nbv=1.6
+ tt=1.8e-08
+ rq=0.12
+ vq=25
+ mtriode=0.65
+ ksubthres=0.095
+ )

.model PDMOS20_INT VDMOS (pchan
+ vto={VTO_PDMOS20_STAT+TC_VTO_PDMOS20*(temper-27)}
+ kp={KP_PDMOS20_STAT*(1+TC_KP_PDMOS20*(temper-27))}
+ lambda=0.007
+ theta=0.045
+ rd={RD_PDMOS20_STAT*(1+TC_RD_PDMOS20*(temper-27))}
+ rs={RS_PDMOS20_STAT*(1+TC_RS_PDMOS20*(temper-27))}
+ rg=3
+ rds=1e+09
+ cgdmax=3.456e-10
+ cgdmin=3e-11
+ a=0.3
+ cgs=4.032e-10
+ cjo=1.5e-10
+ is=8e-13
+ rb=0.08
+ bv={((22*_isTT + 21.45*_isFF + 22.55*_isSS + 22.55*_isFS + 21.45*_isSF))*(1+P_DBV_PDMOS20)}
+ ibv=6e-05
+ nbv=1.7
+ tt=2.2e-08
+ rq=0.15
+ vq=24
+ mtriode=0.62
+ ksubthres=0.11
+ )

.model NDMOS60_INT VDMOS (nchan
+ vto={VTO_NDMOS60_STAT+TC_VTO_NDMOS60*(temper-27)}
+ kp={KP_NDMOS60_STAT*(1+TC_KP_NDMOS60*(temper-27))}
+ lambda=0.004
+ theta=0.03
+ rd={RD_NDMOS60_STAT*(1+TC_RD_NDMOS60*(temper-27))}
+ rs={RS_NDMOS60_STAT*(1+TC_RS_NDMOS60*(temper-27))}
+ rg=3
+ rds=5e+09
+ cgdmax=1.536e-10
+ cgdmin=1.4e-11
+ a=0.28
+ cgs=2.112e-10
+ cjo=7.5e-11
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

.model PDMOS60_INT VDMOS (pchan
+ vto={VTO_PDMOS60_STAT+TC_VTO_PDMOS60*(temper-27)}
+ kp={KP_PDMOS60_STAT*(1+TC_KP_PDMOS60*(temper-27))}
+ lambda=0.0035
+ theta=0.035
+ rd={RD_PDMOS60_STAT*(1+TC_RD_PDMOS60*(temper-27))}
+ rs={RS_PDMOS60_STAT*(1+TC_RS_PDMOS60*(temper-27))}
+ rg=4
+ rds=5e+09
+ cgdmax=1.152e-10
+ cgdmin=1e-11
+ a=0.26
+ cgs=1.44e-10
+ cjo=6.5e-11
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

.model NDMOS120_INT VDMOS (nchan
+ vto={VTO_NDMOS120_STAT+TC_VTO_NDMOS120*(temper-27)}
+ kp={KP_NDMOS120_STAT*(1+TC_KP_NDMOS120*(temper-27))}
+ lambda=0.002
+ theta=0.022
+ rd={RD_NDMOS120_STAT*(1+TC_RD_NDMOS120*(temper-27))}
+ rs={RS_NDMOS120_STAT*(1+TC_RS_NDMOS120*(temper-27))}
+ rg=5
+ rds=1e+10
+ cgdmax=6.24e-11
+ cgdmin=5e-12
+ a=0.24
+ cgs=8.64e-11
+ cjo=3.5e-11
+ is=5e-14
+ rb=0.35
+ bv={((135*_isTT + 128.25*_isFF + 141.75*_isSS + 128.25*_isFS + 141.75*_isSF))*(1+P_DBV_NDMOS120)}
+ ibv=8e-06
+ nbv=2.1
+ tt=8e-08
+ rq=0.65
+ vq=160
+ mtriode=0.5
+ ksubthres=0.07
+ )

.model PDMOS120_INT VDMOS (pchan
+ vto={VTO_PDMOS120_STAT+TC_VTO_PDMOS120*(temper-27)}
+ kp={KP_PDMOS120_STAT*(1+TC_KP_PDMOS120*(temper-27))}
+ lambda=0.0018
+ theta=0.025
+ rd={RD_PDMOS120_STAT*(1+TC_RD_PDMOS120*(temper-27))}
+ rs={RS_PDMOS120_STAT*(1+TC_RS_PDMOS120*(temper-27))}
+ rg=6
+ rds=1e+10
+ cgdmax=4.7e-11
+ cgdmin=4e-12
+ a=0.225
+ cgs=6.1e-11
+ cjo=2.9e-11
+ is=7e-14
+ rb=0.45
+ bv={((128*_isTT + 122.88*_isFF + 133.12*_isSS + 133.12*_isFS + 122.88*_isSF))*(1+P_DBV_PDMOS120)}
+ ibv=8e-06
+ nbv=2.15
+ tt=9.5e-08
+ rq=0.79
+ vq=153
+ mtriode=0.47
+ ksubthres=0.077
+ )

.model NDMOS40_INT VDMOS (nchan
+ vto={VTO_NDMOS40_STAT+TC_VTO_NDMOS40*(temper-27)}
+ kp={KP_NDMOS40_STAT*(1+TC_KP_NDMOS40*(temper-27))}
+ lambda=0.0055
+ theta=0.035
+ rd={RD_NDMOS40_STAT*(1+TC_RD_NDMOS40*(temper-27))}
+ rs={RS_NDMOS40_STAT*(1+TC_RS_NDMOS40*(temper-27))}
+ rg=3
+ rds=2e+09
+ cgdmax=2.52e-10
+ cgdmin=2.2e-11
+ a=0.30
+ cgs=3.36e-10
+ cjo=1.0e-10
+ is=2.5e-13
+ rb=0.10
+ bv={((48*_isTT + 46.56*_isFF + 49.44*_isSS + 46.56*_isFS + 49.44*_isSF))*(1+P_DBV_NDMOS40)}
+ ibv=3e-05
+ nbv=1.7
+ tt=2.8e-08
+ rq=0.18
+ vq=55
+ mtriode=0.61
+ ksubthres=0.088
+ )

.model PDMOS40_INT VDMOS (pchan
+ vto={VTO_PDMOS40_STAT+TC_VTO_PDMOS40*(temper-27)}
+ kp={KP_PDMOS40_STAT*(1+TC_KP_PDMOS40*(temper-27))}
+ lambda=0.0048
+ theta=0.039
+ rd={RD_PDMOS40_STAT*(1+TC_RD_PDMOS40*(temper-27))}
+ rs={RS_PDMOS40_STAT*(1+TC_RS_PDMOS40*(temper-27))}
+ rg=3
+ rds=2e+09
+ cgdmax=1.92e-10
+ cgdmin=1.7e-11
+ a=0.285
+ cgs=2.52e-10
+ cjo=1.05e-10
+ is=3.3e-13
+ rb=0.13
+ bv={((45*_isTT + 43.65*_isFF + 46.35*_isSS + 46.35*_isFS + 43.65*_isSF))*(1+P_DBV_PDMOS40)}
+ ibv=3.5e-05
+ nbv=1.8
+ tt=3.5e-08
+ rq=0.22
+ vq=52
+ mtriode=0.59
+ ksubthres=0.096
+ )

.model NDMOS80_INT VDMOS (nchan
+ vto={VTO_NDMOS80_STAT+TC_VTO_NDMOS80*(temper-27)}
+ kp={KP_NDMOS80_STAT*(1+TC_KP_NDMOS80*(temper-27))}
+ lambda=0.003
+ theta=0.027
+ rd={RD_NDMOS80_STAT*(1+TC_RD_NDMOS80*(temper-27))}
+ rs={RS_NDMOS80_STAT*(1+TC_RS_NDMOS80*(temper-27))}
+ rg=4
+ rds=7e+09
+ cgdmax=1.0e-10
+ cgdmin=8.5e-12
+ a=0.26
+ cgs=1.35e-10
+ cjo=5.5e-11
+ is=9e-14
+ rb=0.22
+ bv={((95*_isTT + 91.2*_isFF + 98.8*_isSS + 91.2*_isFS + 98.8*_isSF))*(1+P_DBV_NDMOS80)}
+ ibv=1.5e-05
+ nbv=1.95
+ tt=5.5e-08
+ rq=0.38
+ vq=110
+ mtriode=0.55
+ ksubthres=0.075
+ )

.model PDMOS80_INT VDMOS (pchan
+ vto={VTO_PDMOS80_STAT+TC_VTO_PDMOS80*(temper-27)}
+ kp={KP_PDMOS80_STAT*(1+TC_KP_PDMOS80*(temper-27))}
+ lambda=0.0027
+ theta=0.031
+ rd={RD_PDMOS80_STAT*(1+TC_RD_PDMOS80*(temper-27))}
+ rs={RS_PDMOS80_STAT*(1+TC_RS_PDMOS80*(temper-27))}
+ rg=5
+ rds=7e+09
+ cgdmax=7.5e-11
+ cgdmin=7e-12
+ a=0.245
+ cgs=9.5e-11
+ cjo=4.5e-11
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

.model NDMOS200_INT VDMOS (nchan
+ vto={VTO_NDMOS200_STAT+TC_VTO_NDMOS200*(temper-27)}
+ kp={KP_NDMOS200_STAT*(1+TC_KP_NDMOS200*(temper-27))}
+ lambda=0.0012
+ theta=0.018
+ rd={RD_NDMOS200_STAT*(1+TC_RD_NDMOS200*(temper-27))}
+ rs={RS_NDMOS200_STAT*(1+TC_RS_NDMOS200*(temper-27))}
+ rg=6
+ rds=2e+10
+ cgdmax=3.5e-11
+ cgdmin=3e-12
+ a=0.22
+ cgs=4.8e-11
+ cjo=2.2e-11
+ is=2.5e-14
+ rb=0.65
+ bv={((225*_isTT + 211.5*_isFF + 238.5*_isSS + 211.5*_isFS + 238.5*_isSF))*(1+P_DBV_NDMOS200)}
+ ibv=4e-06
+ nbv=2.2
+ tt=1.3e-07
+ rq=1.10
+ vq=260
+ mtriode=0.45
+ ksubthres=0.060
+ )

.model PDMOS200_INT VDMOS (pchan
+ vto={VTO_PDMOS200_STAT+TC_VTO_PDMOS200*(temper-27)}
+ kp={KP_PDMOS200_STAT*(1+TC_KP_PDMOS200*(temper-27))}
+ lambda=0.0011
+ theta=0.021
+ rd={RD_PDMOS200_STAT*(1+TC_RD_PDMOS200*(temper-27))}
+ rs={RS_PDMOS200_STAT*(1+TC_RS_PDMOS200*(temper-27))}
+ rg=7.5
+ rds=2e+10
+ cgdmax=2.6e-11
+ cgdmin=2.5e-12
+ a=0.21
+ cgs=3.4e-11
+ cjo=1.8e-11
+ is=3.6e-14
+ rb=0.82
+ bv={((207*_isTT + 194.58*_isFF + 219.42*_isSS + 219.42*_isFS + 194.58*_isSF))*(1+P_DBV_PDMOS200)}
+ ibv=4e-06
+ nbv=2.27
+ tt=1.55e-07
+ rq=1.33
+ vq=248
+ mtriode=0.43
+ ksubthres=0.065
+ )

.model DNMOS20_INT VDMOS (nchan
+ vto={VTO_DNMOS20_STAT+TC_VTO_DNMOS20*(temper-27)}
+ kp={KP_DNMOS20_STAT*(1+TC_KP_DNMOS20*(temper-27))}
+ lambda=0.005
+ theta=0.038
+ rd={RD_DNMOS20_STAT*(1+TC_RD_DNMOS20*(temper-27))}
+ rs={RS_DNMOS20_STAT*(1+TC_RS_DNMOS20*(temper-27))}
+ rg=2
+ rds=1e+09
+ cgdmax=1.44e-10
+ cgdmin=1.2e-11
+ a=0.3
+ cgs=2.016e-10
+ cjo=7e-11
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

.model NPN_LV_INT NPN (
+ is={((2e-16*_isTT + 2.12e-16*_isFF + 1.892e-16*_isSS + 2.12e-16*_isFS + 1.892e-16*_isSF))*(1+P_DIS_NPN_LV)}
+ bf={((140*_isTT + 168*_isFF + 114.8*_isSS + 168*_isFS + 114.8*_isSF))*(1+P_DBF_NPN_LV)}
+ nf=1
+ vaf=80
+ ikf=0.12
+ ise=6e-15
+ ne=1.5
+ br=4
+ nr=1
+ var=20
+ ikr=0.03
+ isc=2e-13
+ nc=2
+ rb={((30*_isTT + 25*_isFF + 36.585366*_isSS + 25*_isFS + 36.585366*_isSF))*(1+P_DRB_NPN_LV)}
+ irb=0.2
+ rbm=5
+ re={((0.6*_isTT + 0.5*_isFF + 0.73170732*_isSS + 0.5*_isFS + 0.73170732*_isSF))*(1+P_DRE_NPN_LV)}
+ rc={((0.7*_isTT + 0.58333333*_isFF + 0.85365854*_isSS + 0.58333333*_isFS + 0.85365854*_isSF))*(1+P_DRC_NPN_LV)}
+ cje=1.6e-12
+ vje=0.78
+ mje=0.33
+ tf={((4.5e-11*_isTT + 3.75e-11*_isFF + 5.4878e-11*_isSS + 3.75e-11*_isFS + 5.4878e-11*_isSF))*(1+P_DTF_NPN_LV)}
+ xtf=3
+ vtf=4
+ itf=0.08
+ cjc=5.5e-13
+ vjc=0.65
+ mjc=0.28
+ tr={((1.2e-08*_isTT + 1e-08*_isFF + 1.46341e-08*_isSS + 1e-08*_isFS + 1.46341e-08*_isSF))*(1+P_DTR_NPN_LV)}
+ eg=1.11
+ xti=3
+ xtb=1.5
+ kf=1e-12
+ af=1
+ )

.model PNP_LAT_INT PNP (
+ is={((8e-16*_isTT + 8.48e-16*_isFF + 7.568e-16*_isSS + 7.568e-16*_isFS + 8.48e-16*_isSF))*(1+P_DIS_PNP_LAT)}
+ bf={((35*_isTT + 42*_isFF + 28.7*_isSS + 28.7*_isFS + 42*_isSF))*(1+P_DBF_PNP_LAT)}
+ nf=1.02
+ vaf=35
+ ikf=0.04
+ ise=2e-14
+ ne=1.6
+ br=2
+ nr=1.05
+ var=10
+ ikr=0.01
+ isc=8e-13
+ nc=2.1
+ rb={((90*_isTT + 75*_isFF + 109.7561*_isSS + 109.7561*_isFS + 75*_isSF))*(1+P_DRB_PNP_LAT)}
+ irb=0.08
+ rbm=20
+ re={((2*_isTT + 1.6666667*_isFF + 2.4390244*_isSS + 2.4390244*_isFS + 1.6666667*_isSF))*(1+P_DRE_PNP_LAT)}
+ rc={((3*_isTT + 2.5*_isFF + 3.6585366*_isSS + 3.6585366*_isFS + 2.5*_isSF))*(1+P_DRC_PNP_LAT)}
+ cje=2.8e-12
+ vje=0.76
+ mje=0.35
+ tf={((1.8e-10*_isTT + 1.5e-10*_isFF + 2.19512e-10*_isSS + 2.19512e-10*_isFS + 1.5e-10*_isSF))*(1+P_DTF_PNP_LAT)}
+ xtf=1.8
+ vtf=2
+ itf=0.02
+ cjc=8e-13
+ vjc=0.6
+ mjc=0.3
+ tr={((2.5e-08*_isTT + 2.08333e-08*_isFF + 3.04878e-08*_isSS + 3.04878e-08*_isFS + 2.08333e-08*_isSF))*(1+P_DTR_PNP_LAT)}
+ eg=1.11
+ xti=3
+ xtb=1.7
+ kf=1e-12
+ af=1
+ )

.model NPN_HV_INT NPN (
+ is={((4e-17*_isTT + 4.24e-17*_isFF + 3.784e-17*_isSS + 4.24e-17*_isFS + 3.784e-17*_isSF))*(1+P_DIS_NPN_HV)}
+ bf={((80*_isTT + 96*_isFF + 65.6*_isSS + 96*_isFS + 65.6*_isSF))*(1+P_DBF_NPN_HV)}
+ nf=1
+ vaf=120
+ ikf=0.06
+ ise=2e-15
+ ne=1.45
+ br=3
+ nr=1
+ var=40
+ ikr=0.015
+ isc=8e-14
+ nc=2
+ rb={((60*_isTT + 50*_isFF + 73.170732*_isSS + 50*_isFS + 73.170732*_isSF))*(1+P_DRB_NPN_HV)}
+ irb=0.1
+ rbm=10
+ re={((1.5*_isTT + 1.25*_isFF + 1.8292683*_isSS + 1.25*_isFS + 1.8292683*_isSF))*(1+P_DRE_NPN_HV)}
+ rc={((1*_isTT + 0.83333333*_isFF + 1.2195122*_isSS + 0.83333333*_isFS + 1.2195122*_isSF))*(1+P_DRC_NPN_HV)}
+ cje=9e-13
+ vje=0.79
+ mje=0.31
+ tf={((9e-11*_isTT + 7.5e-11*_isFF + 1.09756e-10*_isSS + 7.5e-11*_isFS + 1.09756e-10*_isSF))*(1+P_DTF_NPN_HV)}
+ xtf=2
+ vtf=6
+ itf=0.03
+ cjc=3.5e-13
+ vjc=0.7
+ mjc=0.25
+ tr={((1.8e-08*_isTT + 1.5e-08*_isFF + 2.19512e-08*_isSS + 1.5e-08*_isFS + 2.19512e-08*_isSF))*(1+P_DTR_NPN_HV)}
+ eg=1.11
+ xti=3
+ xtb=1.4
+ kf=1e-12
+ af=1
+ )

.model PNP_HV_INT PNP (
+ is={((1e-16*_isTT + 1.06e-16*_isFF + 9.46e-17*_isSS + 9.46e-17*_isFS + 1.06e-16*_isSF))*(1+P_DIS_PNP_HV)}
+ bf={((18*_isTT + 21.6*_isFF + 14.76*_isSS + 14.76*_isFS + 21.6*_isSF))*(1+P_DBF_PNP_HV)}
+ nf=1.03
+ vaf=50
+ ikf=0.015
+ ise=8e-15
+ ne=1.65
+ br=1.6
+ nr=1.06
+ var=15
+ ikr=0.005
+ isc=2e-13
+ nc=2.2
+ rb={((120*_isTT + 100*_isFF + 146.34146*_isSS + 146.34146*_isFS + 100*_isSF))*(1+P_DRB_PNP_HV)}
+ irb=0.05
+ rbm=25
+ re={((2.2*_isTT + 1.8333333*_isFF + 2.6829268*_isSS + 2.6829268*_isFS + 1.8333333*_isSF))*(1+P_DRE_PNP_HV)}
+ rc={((1.8*_isTT + 1.5*_isFF + 2.195122*_isSS + 2.195122*_isFS + 1.5*_isSF))*(1+P_DRC_PNP_HV)}
+ cje=1.4e-12
+ vje=0.77
+ mje=0.34
+ tf={((2.5e-10*_isTT + 2.08333e-10*_isFF + 3.04878e-10*_isSS + 3.04878e-10*_isFS + 2.08333e-10*_isSF))*(1+P_DTF_PNP_HV)}
+ xtf=1.6
+ vtf=3
+ itf=0.01
+ cjc=4.5e-13
+ vjc=0.62
+ mjc=0.28
+ tr={((3e-08*_isTT + 2.5e-08*_isFF + 3.65854e-08*_isSS + 3.65854e-08*_isFS + 2.5e-08*_isSF))*(1+P_DTR_PNP_HV)}
+ eg=1.11
+ xti=3
+ xtb=1.8
+ kf=1e-12
+ af=1
+ )

.model DIO_PN_INT D (
+ is={((2e-14*_isTT + 2.1e-14*_isFF + 1.91e-14*_isSS + 2e-14*_isFS + 2e-14*_isSF))*(1+P_DIS_DIO_PN)}
+ n=1.05
+ rs={((1.2*_isTT + 1*_isFF + 1.4634146*_isSS + 1.2*_isFS + 1.2*_isSF))*(1+P_DRS_DIO_PN)}
+ bv={((100*_isTT + 95*_isFF + 105*_isSS + 100*_isFS + 100*_isSF))*(1+P_DBV_DIO_PN)}
+ ibv=1e-05
+ nbv=1.2
+ cjo={((2.8e-13*_isTT + 2.884e-13*_isFF + 2.716e-13*_isSS + 2.8e-13*_isFS + 2.8e-13*_isSF))*(1+P_DCJO_DIO_PN)}
+ vj=0.78
+ m=0.36
+ tt={((6e-09*_isTT + 5e-09*_isFF + 7.31707e-09*_isSS + 6e-09*_isFS + 6e-09*_isSF))*(1+P_DTT_DIO_PN)}
+ eg=1.11
+ xti=3
+ )

.model DIO_FAST_INT D (
+ is={((8e-13*_isTT + 8.4e-13*_isFF + 7.64e-13*_isSS + 8e-13*_isFS + 8e-13*_isSF))*(1+P_DIS_DIO_FAST)}
+ n=1.03
+ rs={((0.8*_isTT + 0.66666667*_isFF + 0.97560976*_isSS + 0.8*_isFS + 0.8*_isSF))*(1+P_DRS_DIO_FAST)}
+ bv={((80*_isTT + 76*_isFF + 84*_isSS + 80*_isFS + 80*_isSF))*(1+P_DBV_DIO_FAST)}
+ ibv=2e-05
+ nbv=1.2
+ cjo={((1.8e-13*_isTT + 1.854e-13*_isFF + 1.746e-13*_isSS + 1.8e-13*_isFS + 1.8e-13*_isSF))*(1+P_DCJO_DIO_FAST)}
+ vj=0.72
+ m=0.32
+ tt={((2e-09*_isTT + 1.66667e-09*_isFF + 2.43902e-09*_isSS + 2e-09*_isFS + 2e-09*_isSF))*(1+P_DTT_DIO_FAST)}
+ eg=1.11
+ xti=3
+ )

.model DIO_SCH_INT D (
+ is={((3e-08*_isTT + 3.15e-08*_isFF + 2.865e-08*_isSS + 3e-08*_isFS + 3e-08*_isSF))*(1+P_DIS_DIO_SCH)}
+ n=1.08
+ rs={((0.45*_isTT + 0.375*_isFF + 0.54878049*_isSS + 0.45*_isFS + 0.45*_isSF))*(1+P_DRS_DIO_SCH)}
+ bv={((45*_isTT + 42.75*_isFF + 47.25*_isSS + 45*_isFS + 45*_isSF))*(1+P_DBV_DIO_SCH)}
+ ibv=5e-05
+ nbv=1.1
+ cjo={((1.4e-13*_isTT + 1.442e-13*_isFF + 1.358e-13*_isSS + 1.4e-13*_isFS + 1.4e-13*_isSF))*(1+P_DCJO_DIO_SCH)}
+ vj=0.45
+ m=0.22
+ tt={((3e-10*_isTT + 2.5e-10*_isFF + 3.65854e-10*_isSS + 3e-10*_isFS + 3e-10*_isSF))*(1+P_DTT_DIO_SCH)}
+ eg=0.69
+ xti=2
+ )

.model DZ_5V6_INT D (
+ is={((5e-13*_isTT + 5.25e-13*_isFF + 4.775e-13*_isSS + 5e-13*_isFS + 5e-13*_isSF))*(1+P_DIS_DZ_5V6)}
+ n=1.15
+ rs={((1.8*_isTT + 1.5*_isFF + 2.195122*_isSS + 1.8*_isFS + 1.8*_isSF))*(1+P_DRS_DZ_5V6)}
+ bv={((5.6*_isTT + 5.32*_isFF + 5.88*_isSS + 5.6*_isFS + 5.6*_isSF))*(1+P_DBV_DZ_5V6)}
+ ibv=0.00025
+ nbv=2.5
+ cjo={((1.2e-10*_isTT + 1.236e-10*_isFF + 1.164e-10*_isSS + 1.2e-10*_isFS + 1.2e-10*_isSF))*(1+P_DCJO_DZ_5V6)}
+ vj=0.75
+ m=0.35
+ tt={((4e-08*_isTT + 3.33333e-08*_isFF + 4.87805e-08*_isSS + 4e-08*_isFS + 4e-08*_isSF))*(1+P_DTT_DZ_5V6)}
+ eg=1.11
+ xti=3
+ )

.model DZ_12_INT D (
+ is={((2.5e-13*_isTT + 2.625e-13*_isFF + 2.3875e-13*_isSS + 2.5e-13*_isFS + 2.5e-13*_isSF))*(1+P_DIS_DZ_12)}
+ n=1.18
+ rs={((2.5*_isTT + 2.0833333*_isFF + 3.0487805*_isSS + 2.5*_isFS + 2.5*_isSF))*(1+P_DRS_DZ_12)}
+ bv={((12*_isTT + 11.4*_isFF + 12.6*_isSS + 12*_isFS + 12*_isSF))*(1+P_DBV_DZ_12)}
+ ibv=0.00012
+ nbv=2.2
+ cjo={((5.5e-11*_isTT + 5.665e-11*_isFF + 5.335e-11*_isSS + 5.5e-11*_isFS + 5.5e-11*_isSF))*(1+P_DCJO_DZ_12)}
+ vj=0.78
+ m=0.33
+ tt={((5.5e-08*_isTT + 4.58333e-08*_isFF + 6.70732e-08*_isSS + 5.5e-08*_isFS + 5.5e-08*_isSF))*(1+P_DTT_DZ_12)}
+ eg=1.11
+ xti=3
+ )

.model DZ_24_INT D (
+ is={((1.2e-13*_isTT + 1.26e-13*_isFF + 1.146e-13*_isSS + 1.2e-13*_isFS + 1.2e-13*_isSF))*(1+P_DIS_DZ_24)}
+ n=1.22
+ rs={((3.5*_isTT + 2.9166667*_isFF + 4.2682927*_isSS + 3.5*_isFS + 3.5*_isSF))*(1+P_DRS_DZ_24)}
+ bv={((24*_isTT + 22.8*_isFF + 25.2*_isSS + 24*_isFS + 24*_isSF))*(1+P_DBV_DZ_24)}
+ ibv=8e-05
+ nbv=2
+ cjo={((2.8e-11*_isTT + 2.884e-11*_isFF + 2.716e-11*_isSS + 2.8e-11*_isFS + 2.8e-11*_isSF))*(1+P_DCJO_DZ_24)}
+ vj=0.8
+ m=0.3
+ tt={((7.5e-08*_isTT + 6.25e-08*_isFF + 9.14634e-08*_isSS + 7.5e-08*_isFS + 7.5e-08*_isSF))*(1+P_DTT_DZ_24)}
+ eg=1.11
+ xti=3
+ )

.model RPOLY_HI_INT R (
+ rsh={((1200*_isTT + 1080*_isFF + 1344*_isSS + 1200*_isFS + 1200*_isSF))*(1+P_DRSH_RPOLY_HI)}
+ tc1=0.0006
+ tc2=1e-06
+ defw=1e-06
+ narrow=1.2e-07
+ short=1e-07
+ kf=1e-24
+ af=1
+ wf=1
+ lf=1
+ ef=1
+ )

.model RPOLY_LO_INT R (
+ rsh={((25*_isTT + 22.5*_isFF + 28*_isSS + 25*_isFS + 25*_isSF))*(1+P_DRSH_RPOLY_LO)}
+ tc1=0.001
+ tc2=2e-06
+ defw=2e-06
+ narrow=1.5e-07
+ short=1.2e-07
+ kf=5e-25
+ af=1
+ wf=1
+ lf=1
+ ef=1
+ )

.model RNWELL_INT R (
+ rsh={((1800*_isTT + 1620*_isFF + 2016*_isSS + 1800*_isFS + 1800*_isSF))*(1+P_DRSH_RNWELL)}
+ tc1=0.004
+ tc2=5e-06
+ defw=2e-06
+ narrow=1.8e-07
+ short=1.5e-07
+ kf=2e-24
+ af=1
+ wf=1
+ lf=1
+ ef=1
+ )

.model RNPLUS_INT R (
+ rsh={((32*_isTT + 28.8*_isFF + 35.84*_isSS + 32*_isFS + 32*_isSF))*(1+P_DRSH_RNPLUS)}
+ tc1=0.0009
+ tc2=1.5e-06
+ defw=2e-06
+ narrow=1.8e-07
+ short=1.4e-07
+ kf=5e-25
+ af=1
+ wf=1
+ lf=1
+ ef=1
+ )

.model RPPLUS_INT R (
+ rsh={((58*_isTT + 52.2*_isFF + 64.96*_isSS + 58*_isFS + 58*_isSF))*(1+P_DRSH_RPPLUS)}
+ tc1=0.0011
+ tc2=1.6e-06
+ defw=2e-06
+ narrow=1.8e-07
+ short=1.4e-07
+ kf=7e-25
+ af=1
+ wf=1
+ lf=1
+ ef=1
+ )

.model CMIM_STD_INT C (
+ cj={((0.001*_isTT + 0.00103*_isFF + 0.00097*_isSS + 0.001*_isFS + 0.001*_isSF))*(1+P_DCJ_CMIM_STD)}
+ cjsw=0
+ thick=6.64066e-08
+ di=7.5
+ defw=1e-05
+ defl=1e-05
+ tc1=3.5e-05
+ tc2=5e-08
+ tnom=27
+ )

.model CMIM_HI_INT C (
+ cj={((0.002*_isTT + 0.00206*_isFF + 0.00194*_isSS + 0.002*_isFS + 0.002*_isSF))*(1+P_DCJ_CMIM_HI)}
+ cjsw=0
+ thick=3.32033e-08
+ di=7.5
+ defw=1e-05
+ defl=1e-05
+ tc1=4.5e-05
+ tc2=6e-08
+ tnom=27
+ )

.model CMOM_INT C (
+ cj={((0.00035*_isTT + 0.0003605*_isFF + 0.0003395*_isSS + 0.00035*_isFS + 0.00035*_isSF))*(1+P_DCJ_CMOM)}
+ cjsw=0
+ thick=1.89733e-07
+ di=7.5
+ defw=1e-05
+ defl=1e-05
+ tc1=2e-05
+ tc2=3e-08
+ tnom=27
+ )

.model CFRINGE_INT C (
+ cj={((0.00018*_isTT + 0.0001854*_isFF + 0.0001746*_isSS + 0.00018*_isFS + 0.00018*_isSF))*(1+P_DCJ_CFRINGE)}
+ cjsw={((2.5e-11*_isTT + 2.575e-11*_isFF + 2.425e-11*_isSS + 2.5e-11*_isFS + 2.5e-11*_isSF))*(1+P_DCJSW_CFRINGE)}
+ thick=3.68926e-07
+ di=7.5
+ defw=5e-06
+ defl=5e-06
+ tc1=1.5e-05
+ tc2=2e-08
+ tnom=27
+ )
