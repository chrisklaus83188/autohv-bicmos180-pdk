"""
analysis.py -- shared metric extraction from an I_out(V_out) sweep.

All metrics operate on a measured (Vout[], Iout[]) sweep from a real deck.
Nothing here back-solves or substitutes analytic forms; it is pure numerics on
the sweep points.

Metrics are anchored to GENERAL, supply-agnostic points, not to any application
trip voltage:
  * gain           : I_out/I_in at V_out = Vdd/2 (mid-compliance) and at V_out=0.
  * lambda_eff / r_out : averaged over a fixed in-saturation window V_out in
    [0, VBAND] where VBAND = 2.0 V.  That window is inside the saturation region
    of ALL topologies at every supply in the study (the standard cascode's
    compliance is >2.3 V even at the 3.2 V UVLO floor), so the same window is
    valid across Vdd and lets I(V_SD) curves be compared directly.
"""
import numpy as np

VBAND = 2.0   # general in-saturation window for averaged metrics (V)


def _interp(v, i, x):
    return float(np.interp(x, v, i))


def band_metrics(v, i, Vdd, Iin, vband=VBAND):
    """Compute the general mirror metrics for one sweep.  V_SD = Vdd-Vout, so a
    rising V_out is a falling V_SD.  lambda_eff and r_out are averaged in-band
    (slope fit over [0, min(vband, Vdd/2 rounded up)] ), not single-point."""
    v = np.asarray(v, float); i = np.asarray(i, float)
    order = np.argsort(v); v, i = v[order], i[order]
    # keep the averaging window inside saturation even at the lowest supply
    hi = min(vband, Vdd - 1.0)          # leave >=1 V of headroom below the rail
    m = (v >= -1e-9) & (v <= hi + 1e-9)
    vb, ib = v[m], i[m]
    out = {}
    out["I_at_0"]       = _interp(v, i, 0.0)
    out["I_at_vddhalf"] = _interp(v, i, Vdd/2.0)
    out["gain_vddhalf"] = out["I_at_vddhalf"]/Iin
    out["gain_at_0"]    = out["I_at_0"]/Iin
    out["band_hi_V"]    = float(hi)
    if len(vb) >= 2:
        A = np.polyfit(vb, ib, 1)
        slope = A[0]                    # dI/dVout  (negative)
        Ibar = float(np.mean(ib))
        out["rout_inband"] = float(1.0/abs(slope)) if slope != 0 else np.inf
        # lambda_eff = (1/I) dI/dVSD = (1/I)(-dI/dVout)
        out["lambda_eff"]  = float(-slope/Ibar)
        out["ramp_nonlin_pct"] = float(100.0*np.max(np.abs(ib-Ibar))/Ibar)
    else:
        out["rout_inband"] = np.nan; out["lambda_eff"] = np.nan
        out["ramp_nonlin_pct"] = np.nan
    # compliance: Vout where I has fallen 1% / 0.1% below I(Vout=0)
    i0 = out["I_at_0"]
    out["vmax_1pct"]   = _compliance(v, i, i0, 0.01)
    out["vmax_0p1pct"] = _compliance(v, i, i0, 0.001)
    return out


def _compliance(v, i, i0, frac):
    """First Vout where i < (1-frac)*i0.  Returns that Vout (interp), else v[-1]."""
    thr = (1.0-frac)*i0
    below = np.where(i < thr)[0]
    if len(below) == 0:
        return float(v[-1])
    k = below[0]
    if k == 0:
        return float(v[0])
    x = v[k-1] + (thr-i[k-1])*(v[k]-v[k-1])/(i[k]-i[k-1])
    return float(x)
