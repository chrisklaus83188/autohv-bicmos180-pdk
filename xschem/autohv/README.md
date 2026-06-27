# AutoHV_BiCMOS180 — Xschem symbol library

40 device symbols, one per `.subckt` in `../../autohv_bicmos180_case.lib`. Each symbol
netlists as an `x`-prefixed subckt call resolved against the PDK model library.
This package is **portable**: nothing here hardcodes a machine path. The single
machine-specific file (the model-include helper) is generated locally by `install.sh`.

## Install on a machine (once per laptop, in WSL/Ubuntu)
```
bash xschem/install.sh
```
This creates `~/autohv_pdk` (no-space symlink to the PDK root, for the model `.include`),
symlinks `~/xschem_lib/autohv -> xschem/autohv`, generates `~/xschem_lib/autohv_lib.sym`
with this machine's path, and registers `~/xschem_lib` in `~/.xschem/xschemrc`.

## Using the devices
Place any `autohv/<DEVICE>` part. Editable instance params:
- 4-pin MOS (NMOS/PMOS 12·18·33·50), pins **d g s b**: `W L M MM_SIGMA`
- 3-pin DMOS (N/P DMOS 20·40·60·80·120, DNMOS20), pins **d g s**: `W M MM_SIGMA`
- DMOS200 (N/P), pins **d g s**: `W L M MM_SIGMA`  (L default 8u)
- BJT (NPN_LV/HV, PNP_LAT/HV), pins **c b e**: `AREA MM_SIGMA`
- Diodes/Zeners (DIO_*, DZ_*), pins **a c**: `AREA MM_SIGMA`
- Resistors (RPOLY_*, RNWELL, RNPLUS, RPPLUS), pins **p n**: `L W MM_SIGMA`
- Caps (CMIM_*, CMOM, CFRINGE), pins **p n**: `L W MM_SIGMA`

## Model include + corner
Drop one `autohv_lib` block on the testbench. Set its `CASE` attribute:
**0=TT 1=FF 2=SS 3=FS 4=SF**. It emits the `.include` + `.param case=`.
Per-device mismatch: set `MM_SIGMA` on the instance (needs global `MM_ON=1`).

## Regenerating symbols
Edit `xschem/gen_syms.sh`, then `bash xschem/gen_syms.sh` (rewrites `autohv/*.sym`).
Do not hand-edit the 40 files individually.

## Example
`autohv/examples/tb_nmos12_idvg.sch` — NMOS12 Id-Vgs sweep, label-wired (TT corner).
Headless: `xschem -n -x -q -o ~/_netout autohv/examples/tb_nmos12_idvg.sch`
then `ngspice -b ~/_netout/tb_nmos12_idvg.spice`  (Id ramps to ~2.7 mA at Vgs=12 V).
