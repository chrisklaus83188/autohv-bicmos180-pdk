# PDK regression suite

Automated smoke / regression harness for `autohv_bicmos180_case.lib`.
Pinned to **ngspice-45.2**.

## Phase A — device instantiation smoke (`run_smoke.py`)

Generates a minimal bias circuit for every `.subckt` device (all 38),
runs `op` in `ngspice_con -b`, and asserts that:

- the deck reaches the `SMOKE_OK` marker (`op` converged), and
- ngspice prints no fatal-error patterns (e.g. `no such function`,
  `singular matrix`, `iteration limit reached`).

Sweeps the full corner × statistics matrix:

| Axis     | Values                                  |
|----------|-----------------------------------------|
| `case`   | 0, 1, 2, 3, 4   (TT / FF / SS / FS / SF) |
| `PROC_ON`| 0, 1                                    |
| `MM_ON`  | 0, 1                                    |

Total: **38 × 5 × 4 = 760 ops**, ~45 s on a typical laptop.

### Running

```sh
# Full matrix (760 ops, ~45 s)
python pdk_validation/regression/run_smoke.py

# Smoke only (38 ops, ~3 s) — quick gate while iterating
python pdk_validation/regression/run_smoke.py --quick

# Restrict to specific devices
python pdk_validation/regression/run_smoke.py --device NDMOS200 RPOLY_HI

# Parallelize for faster CI runs
python pdk_validation/regression/run_smoke.py --jobs 4
```

Exit code is `0` on full pass, `1` on any failure, `2` on setup error
(ngspice not found, lib missing, etc.).

### ngspice binary discovery

The harness looks for `ngspice_con` in this order:

1. `$NGSPICE_BIN` (env var, full path to binary)
2. `ngspice_con` / `ngspice_con.exe` on `PATH`
3. Windows defaults: `C:\Spice64\bin\ngspice_con.exe`,
   `C:\Program Files\ngspice\bin\ngspice_con.exe`

> Use `ngspice_con.exe` on Windows, not `ngspice.exe`. The latter is
> the interactive GUI/console variant — it opens its own window and
> doesn't stream stdout back to the calling shell, so the harness sees
> no output and timeouts as if the test hung.

### Interpreting failures

Each failure prints the device, axes, and the matched error line:

```
  NDMOS20 (2 fail(s)):
    case=1 PROC=1 MM=1 -> Error: no such function 'agauss'
    case=2 PROC=1 MM=1 -> Error: no such function 'agauss'
```

The exact error patterns the harness watches for live at the top of
`run_smoke.py` (`ERROR_PATTERNS`).

## Out of scope for Phase A (planned)

- **Phase B**: per-test wall-time assertion (catches convergence /
  stiffness regressions like the pre-fix `abs()` kink).
- **Phase C**: DC-sweep R/C and diff R(V)/C(V) against golden curves.
- **Phase D**: short transient per device class with timestep budget.
- **Phase E**: Monte Carlo harness (validates AGAUSS re-randomization
  across MC iterations — see handoff P1 "Monte Carlo validation").
- **Phase F**: GitHub Actions wiring with pinned ngspice version.

See `docs/PDK_HANDOFF.md` (or the handoff source) for the full backlog.
