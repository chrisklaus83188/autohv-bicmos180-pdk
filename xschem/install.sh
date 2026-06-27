#!/bin/bash
# Per-machine activation of the AutoHV BiCMOS180 Xschem library.
# Run once on each laptop (inside WSL/Ubuntu):  bash xschem/install.sh
# Handles the two machine-specific things: $HOME/username and the spaces in the
# PDK repo path. Everything versioned in the repo stays path-agnostic.
set -e
SD="$(cd "$(dirname "$0")" && pwd -P)"   # <repo>/xschem (physical path)
REPO="$(cd "$SD/.." && pwd -P)"          # <repo> root (may contain spaces)

# 1) no-space symlink to the PDK root, used by the model .include
ln -sfn "$REPO" "$HOME/autohv_pdk"
echo "symlink: ~/autohv_pdk -> $REPO"

# 2) no-space xschem library dir; symlink the (versioned) symbol folder into it
mkdir -p "$HOME/xschem_lib"
if [ -e "$HOME/xschem_lib/autohv" ] && [ ! -L "$HOME/xschem_lib/autohv" ]; then
  rm -rf "$HOME/xschem_lib/autohv"     # drop any stale real copy
fi
ln -sfn "$SD/autohv" "$HOME/xschem_lib/autohv"
echo "symlink: ~/xschem_lib/autohv -> $SD/autohv"

# 2b) designs dir (YOUR schematics) on the lib path via a no-space symlink
mkdir -p "$SD/designs"
if [ -e "$HOME/xschem_lib/designs" ] && [ ! -L "$HOME/xschem_lib/designs" ]; then
  rm -rf "$HOME/xschem_lib/designs"
fi
ln -sfn "$SD/designs" "$HOME/xschem_lib/designs"
echo "symlink: ~/xschem_lib/designs -> $SD/designs"

# 2c) logic-cell symbols (logic/ subdir) on the lib path
if [ -e "$HOME/xschem_lib/logic" ] && [ ! -L "$HOME/xschem_lib/logic" ]; then
  rm -rf "$HOME/xschem_lib/logic"
fi
ln -sfn "$SD/logic" "$HOME/xschem_lib/logic"
echo "symlink: ~/xschem_lib/logic -> $SD/logic"

# 2d) comparator-cell symbols (comparators/ subdir) on the lib path
if [ -e "$HOME/xschem_lib/comparators" ] && [ ! -L "$HOME/xschem_lib/comparators" ]; then
  rm -rf "$HOME/xschem_lib/comparators"
fi
ln -sfn "$SD/comparators" "$HOME/xschem_lib/comparators"
echo "symlink: ~/xschem_lib/comparators -> $SD/comparators"

# 2e) delay/pulse-cell symbols (delay_pulse/ subdir) on the lib path
if [ -e "$HOME/xschem_lib/delay_pulse" ] && [ ! -L "$HOME/xschem_lib/delay_pulse" ]; then
  rm -rf "$HOME/xschem_lib/delay_pulse"
fi
ln -sfn "$SD/delay_pulse" "$HOME/xschem_lib/delay_pulse"
echo "symlink: ~/xschem_lib/delay_pulse -> $SD/delay_pulse"

# 3) generate the machine-local include helpers (only files with an abs path)
sed "s|__HOME__|$HOME|g" "$SD/autohv_lib.sym.in" > "$HOME/xschem_lib/autohv_lib.sym"
echo "wrote:   ~/xschem_lib/autohv_lib.sym (model include + corner)"
sed "s|__HOME__|$HOME|g" "$SD/logic_lib.sym.in" > "$HOME/xschem_lib/logic_lib.sym"
echo "wrote:   ~/xschem_lib/logic_lib.sym (cells.lib include + global vdd)"
sed "s|__HOME__|$HOME|g" "$SD/cmp_lib.sym.in" > "$HOME/xschem_lib/cmp_lib.sym"
echo "wrote:   ~/xschem_lib/cmp_lib.sym (comparators_all.lib include + global vdd)"
sed "s|__HOME__|$HOME|g" "$SD/dly_lib.sym.in" > "$HOME/xschem_lib/dly_lib.sym"
echo "wrote:   ~/xschem_lib/dly_lib.sym (delay cells.lib + gear + global vdd)"
rm -f "$HOME/cmp_pdk"   # obsolete: comparators now live in the canonical PDK tree

# 4) register the lib path in this machine's xschemrc (idempotent)
RC="$HOME/.xschem/xschemrc"
mkdir -p "$(dirname "$RC")"
if ! grep -q 'AutoHV BiCMOS180 PDK symbols' "$RC" 2>/dev/null; then
  printf '\n# --- AutoHV BiCMOS180 PDK symbols (added by install.sh) ---\nappend XSCHEM_LIBRARY_PATH :~/xschem_lib\n' >> "$RC"
  echo "xschemrc: registered ~/xschem_lib"
else
  echo "xschemrc: already registered"
fi
echo "DONE. Devices appear under autohv/ in Xschem's library browser."
