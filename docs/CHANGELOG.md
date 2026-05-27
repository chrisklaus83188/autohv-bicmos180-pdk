# Changelog

## [Unreleased]

### 2026-05-27 — Library refinements

- MOS Vth mismatch (NMOS/PMOS 12/18/33/50): replaced the external
  `Vshift g g_int DC {DVTH_MM}` + node-split workaround with BSIM3's
  native `delvto` instance parameter on `M0`. Removes the extra
  series voltage source and dangling `g_int` node per device while
  delivering the same mismatch Vth shift through the model's
  intrinsic mechanism.
- Smoothed `|V|` in voltage-coefficient expressions: replaced
  `abs(V(p,n))` with `sqrt(V(p,n)*V(p,n)+1e-6)` in the VCR
  branches of `RPOLY_HI`, `RPOLY_LO`, `RNWELL`, `RNPLUS`, `RPPLUS`
  and the VCC branches of `CMIM_STD`, `CMIM_HI`, `CMOM`, `CFRINGE`.
  Removes the cusp at V=0 (now C∞) so Newton/DC convergence is
  cleaner; bias dependence is unchanged for |V| >> 1 mV.

### Initial snapshot

Initial tracked version of the AutoHV BiCMOS 180 PDK for Qucs-S.

### Library
- Collapsed the original five corner-sectioned libraries into a single flat library;
  the corner is selected by a global `case` parameter (0=TT, 1=FF, 2=SS, 3=FS, 4=SF).
- Orthogonal statistics: `PROC_ON` (die-to-die process) and `MM_ON` (local mismatch),
  both off by default.
- Removed the redundant `_MC` device wrappers (statistics live in the base devices),
  reducing the library from 76 to 38 `.subckt` devices.
- DMOS/LDMOS sizing reworked from `AREA` to physical `W`/`M` (all DMOS) and an
  additional drift-length `L` on the 200 V `NDMOS200`. Width scales current linearly
  via an internal multiplier; `L` raises modeled on-resistance (breakdown held at the
  model rating).

### Models
- Bipolar breakdown reinstated. Removed the inert `bv`/`ibv` from the four
  Gummel-Poon BJT cards (they are not GP parameters and were silently ignored,
  so the `P_DBV_*` draws varied nothing) and rebuilt breakdown behaviorally in
  the subckts as a collector-base avalanche branch keyed to the original ratings
  (now `BVCBO`), with the `P_DBV_*` draws kept live. Model beta now sets
  BVceo < BVcbo.
- 12 V devices (`NMOS12`/`PMOS12`) converted from MOS Level 3 to BSIM3
  (level 49) for smooth output conductance, charge-conserving capacitances and a
  real subthreshold region, matching the 18/33/50 family. Also removes a Level-3
  `lambda`/`kappa` ambiguity that made gds differ between ngspice and SmartSpice.
  Corner Vth/u0/vsat/rdsw carried over from the Level-3 sets; Monte-Carlo draws
  remapped with none added and none left dead.
- HV drift-MOS (VDMOS, all 11 cards) given temperature dependence (on-resistance
  rises, Kp/Vth fall with T) via per-device tempco constants grouped at the top
  of the models include. Previously the VDMOS array had no temperature behavior.
- Bipolars given 1/f (flicker) noise (`kf`/`af`); flicker was previously zero.
- Annotated the inert `binunit=1` on the BSIM3 cards (no L/W bins are shipped).

### Symbols
- Schematic symbols for all 38 devices, with corrected device-specific artwork
  (core FET orientation, HV DMOS extended-drain symbol, zig-zag resistors).

### Docs / tooling
- Added the PDK reference manual (`docs/`) and runnable example decks (`examples/`).

### Notes & known limitations
- Calibration required. Signs and mechanisms are validated on ngspice 42,
  but the magnitudes are engineered, not fit to silicon: the BSIM3 12 V secondary
  coefficients, the VDMOS tempco constants (`TC_*`), and the BJT avalanche
  sharpness (`MAV_BJT`) and `kf`/`af`. The converted BSIM3 12 V cards
  intentionally do not reproduce the old Level-3 I-V.
- `AGAUSS` in `.param` is not parsed by stock ngspice in its default mode; the
  statistics rely on Qucs-S preprocessing, an HSPICE-compatibility path, or
  SmartSpice (native `AGAUSS`).
- The avalanche subckts use ngspice idioms (`temper` re-evaluation in `.model`
  braces, the `**` operator, `min`/`max`, and the `i(Vsen)` current probe);
  confirm equivalents when porting to SmartSpice.
- Deferred: cap VCC charge-form conversion; substrate/junction caps and a
  self-heating thermal node on the HV array (interface change); and calibrated
  MOS 1/f (`noia/noib/noic`, currently on `noimod=2` defaults).
