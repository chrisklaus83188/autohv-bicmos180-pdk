# Handoff archive (resolved)

Historical engineering correspondence between PDK-maintainer and downstream
eval-task sessions. Every item here was **investigated and resolved** — the fix
is already in the PDK source and recorded in [`../CHANGELOG.md`](../CHANGELOG.md).
Kept for provenance; nothing here is an open action item.

Open findings that are *not* yet resolved live under [`../backlog/`](../backlog/).

## Two threads

### ngspice compatibility (2026-05-28)

A four-claim report that the PDK's behavioral elements broke ngspice, walked
back to a single real issue through disciplined mini-repros.

| Doc | Role |
|-----|------|
| [HANDOFF_ngspice_compat.md](HANDOFF_ngspice_compat.md) | Original report — 4 claims, proposed a global `NGSPICE_COMPAT` switch |
| [HANDOFF_ngspice_compat_REPRO_REQUEST.md](HANDOFF_ngspice_compat_REPRO_REQUEST.md) | Pushback — regression suite contradicts 3 of 4 claims; asks for repros |
| [HANDOFF_ngspice_compat_REPRO_RESULTS.md](HANDOFF_ngspice_compat_REPRO_RESULTS.md) | Retracts claims #1/#2/#4; confirms only #3 (Vshift singular matrix) |
| [HANDOFF_ngspice_compat_REPLY_FIX_LANDED.md](HANDOFF_ngspice_compat_REPLY_FIX_LANDED.md) | `Rgmin` gmin-shunt fix landed for the 13 VDMOS subckts |
| [HANDOFF_ngspice_compat_REPLY_VERIFIED.md](HANDOFF_ngspice_compat_REPLY_VERIFIED.md) | Verification — realistic level-shifter case fixed; minimal repro still fails on ngspice 46 |
| [HANDOFF_ngspice_compat_REPLY_FINAL.md](HANDOFF_ngspice_compat_REPLY_FINAL.md) | Close-out — `Rgmin` is the ship state; `delvto` / B-source alternatives are dead ends on VDMOS |

**Resolution:** `Rgmin` shunt in all 13 VDMOS wrappers. No global switch. The
high-fidelity BVCR / Cextra / Bavl behavioral elements were left untouched.

### DMOS200 device issues (2026-06)

Four distinct findings against the 200 V LDMOS, all from HV switching /
level-shifter tasks.

| Doc | Finding | Resolution in source |
|-----|---------|----------------------|
| [HANDOFF_cascode_vshift_singularity.md](HANDOFF_cascode_vshift_singularity.md) | `Rgmin` insufficient when the gate is driven by a real (non-stiff) network | `Rcond g_int s` added |
| [HANDOFF_dmos200_vshift_multiinstance.md](HANDOFF_dmos200_vshift_multiinstance.md) | Same singularity in multi-instance floating mirrors | `Rcond` (13 instances in the `.lib`) |
| [HANDOFF_dmos200_vshift_multiinstance_REPLY.md](HANDOFF_dmos200_vshift_multiinstance_REPLY.md) | `delvto` rejected by VDMOS; `Rcond` to a determined node is the working fix | `Rcond` landed |
| [HANDOFF_dmos200_breakdown.md](HANDOFF_dmos200_breakdown.md) | PDMOS200 broke down at 194.58 V (< 200 V) at FF/SF | `bv` re-rated to 216.2 V FF/SF |
| [HANDOFF_vdmos_caps.md](HANDOFF_vdmos_caps.md) | VDMOS terminal caps ~1000× too large | `cgs`/`cgd`/`cjo` scaled ÷1000 (e.g. NDMOS200 `cjo` 2.2e-11 → 2.2e-14) |

The two DMOS200 findings that were **not** resolved (subthreshold `kp`,
fast-transient micro-stepping) are tracked in [`../backlog/`](../backlog/).
