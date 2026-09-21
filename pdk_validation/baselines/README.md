# Frozen baselines

These files are a **historical snapshot**, not live data. They record what the PDK produced
at the tagged points they are named for, and they are deliberately **not** edited when the
repository changes around them. Editing a baseline to match the present defeats its only
purpose: a baseline you are willing to rewrite cannot tell you that something moved.

## They still use the pre-rename device names

The device rename (`models/device_rename_map.json`) renamed 23 devices —
`NMOS50 → NMOS5V0`, `NMOS12 → NMOS12V`, `NDMOS200 → NDMOS200V`, and so on — because
`NMOS50` read as a 50 V device and `NMOS12` as a 1.2 V one. That rename was applied across
every tracked file **except this directory**, which still carries the old names in
**2878** places.

**Any tool that compares against these files must apply the map when reading them**, not
rewrite the files. The mapping is available as:

```python
import sys; sys.path.insert(0, "tools")
from rename_devices import load_map, token_re
mapping = load_map()
rx = token_re(mapping)
current = rx.sub(lambda m: mapping[m.group(1)], baseline_text)
```

`tools/check_naming.py` exempts this directory from its retired-device-name scan for the
same reason. The exemption is narrow and deliberate: everywhere else, an old device name is
a defect.

## Contents

| path | what it is |
|---|---|
| `mc_baseline_v2.2.json` | the MC realism program baseline, written by `circuits/mc_mismatch_check/05_baseline.py` |
| `v2_2/` | a tree snapshot of docs, characterization results and circuit results at `v2.2-defaults` |
