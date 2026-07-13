# PDK backlog

Open engineering findings surfaced by downstream tasks that were **investigated
but not resolved**. None is blocking today — each is something to look into when
the time is right. The full write-up (symptoms, measured data, standalone
reproducers, acceptance criteria) lives in the linked handoff doc.

Resolved handoffs — where the fix already landed in the PDK — are archived
separately under [`../handoffs/`](../handoffs/).

| # | Item | Devices | Impact | Reproducer |
|---|------|---------|--------|------------|
| 1 | [HV DMOS are subthreshold at analog (µA) currents](HANDOFF_dmos200_subthreshold_analog.md) | `NDMOS200`, `PDMOS200` | `kp` is a power-FET value, so the devices sit in subthreshold below ~mA. A current mirror at a µA budget hits max gm/I, amplifying ~2 mV Vth mismatch into a ~400 mV (1σ) trip shift — unusable as a precision analog mirror. | Self-biased diode sweep in the doc (§Reproducer) |
| 2 | [Fast HV transients micro-step into timeouts above ~100 V](HANDOFF_dynamic_transient_microstepping.md) | `NDMOS200`, `PDMOS200` | With ≥1 floating HV LDMOS front-end, a fast edge / slew drives the timestep toward zero above ~120 V and never completes. DC and quasi-static transients are fine (the `Rcond` fix handled those). | [`repro_slew_vin{100,200}.cir`](../../repro_slew_vin100.cir), [`repro_delay_vin{100,200}.cir`](../../repro_delay_vin100.cir) at repo root |

## Notes on each

### 1 — Subthreshold `kp` (open design question)

The core question is **intent**: are `KP_NDMOS200` / `KP_PDMOS200` meant to model
an HV *drift* MOSFET used as an analog device, or a discrete power FET? The
handoff proposes three resolutions: re-fit `kp`/`vto`/`theta` for moderate
inversion at µA, confirm the family is power-only and add a separate HV analog
device, or document the intended analog operating current. Needs a maintainer
decision before any model-card change.

### 2 — Fast-transient micro-stepping (open investigation)

Likely the interaction of the VDMOS nonlinear junction caps (Cgd/Cds) with the
floating high-impedance internal mirror/cascode nodes when the drain swings fast
at high Vds — the same node structure `Rcond` conditioned for DC, now stressed
dynamically. The reporting task exhausted the testbench/tolerance/option space
(documented in the handoff) without a fix. Open question: can the model (cap
formulation, internal conditioning, charge smoothing, or a transient-friendly
macromodel) take a fast 150–200 V drain transient with several floating
instances without the timestep collapsing — or is it inherent? The four
`repro_*.cir` decks at the repo root are the standalone reproducers (the
100 V / 200 V pairs are identical except VIN level).
