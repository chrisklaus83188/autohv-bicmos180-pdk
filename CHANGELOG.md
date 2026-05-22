# Changelog

## [Unreleased]

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

### Symbols
- Schematic symbols for all 38 devices, with corrected device-specific artwork
  (core FET orientation, HV DMOS extended-drain symbol, zig-zag resistors).

### Docs / tooling
- Added the PDK reference manual (`docs/`) and runnable example decks (`examples/`).
