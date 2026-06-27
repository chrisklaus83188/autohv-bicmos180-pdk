# designs/ — your schematics & testbenches

Put your own `.sch` files here. This folder is versioned in the PDK repo (so it
syncs to your other laptop) and is symlinked to `~/xschem_lib/designs`, which is
on `XSCHEM_LIBRARY_PATH` — so Xschem's library browser shows it and it resolves
with no spaces in the path.

## Save / open from Xschem
- **Save As:** point the dialog at `~/xschem_lib/designs/` (a no-space path that
  follows the symlink into this repo folder).
- **Open:** same location, or `xschem ~/xschem_lib/designs/<name>.sch`.

## In a design
- Place devices as `autohv/<DEVICE>` (e.g. `autohv/NMOS12`).
- Drop one `autohv_lib` block and set its `CASE` (0=TT 1=FF 2=SS 3=FS 4=SF) to
  pull in the model `.include` + corner.
- Copy stimulus from `autohv/examples/device_sheet.sch` (PWL sources, etc.).

## Other laptop
After syncing the repo, run `bash xschem/install.sh` once — it recreates the
`~/xschem_lib/designs` symlink so your designs are in the same place there.
