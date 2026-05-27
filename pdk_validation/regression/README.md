# PDK regression suite

Automated smoke / regression harness for `autohv_bicmos180_case.lib`.
Pinned to **ngspice-45.2**.

## Phases A + B — instantiation smoke + per-op wall-time budget (`run_smoke.py`)

Generates a minimal bias circuit for every `.subckt` device (all 38),
runs `op` in `ngspice_con -b`, and asserts that:

- the deck reaches the `SMOKE_OK` marker (`op` converged),
- ngspice prints no fatal-error patterns (e.g. `no such function`,
  `singular matrix`, `iteration limit reached`), **and**
- the op completes within `--max-op-secs` seconds (default 2.0).
  Catches convergence/stiffness regressions like the pre-fix `abs()`
  kink (which took >120 s on a passive transient vs. ~3 s after the
  smooth-`|V|` fix).

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

# Tighten the wall-time budget (default 2.0s); disable with 0
python pdk_validation/regression/run_smoke.py --max-op-secs 1.0
python pdk_validation/regression/run_smoke.py --max-op-secs 0
```

Exit code is `0` on full pass, `1` on any failure, `2` on setup error
(ngspice not found, lib missing, etc.).

### Op-time stats

Every run prints `median / p95 / max` op time at the end:

```
Op time: median=53ms  p95=67ms  max=204ms
Passed: 760/760   (42.8s wall)
ALL PASS
```

The current baseline on ngspice-45.2: median ~55 ms, p95 ~80 ms, max
~200 ms. The default 2.0 s budget gives roughly 10× headroom over the
worst observed op, so a Newton/LTE regression of even ~10× would trip
the gate. If `--jobs > 1`, individual op times are still measured per
subprocess but may inflate slightly under sibling contention — bump
`--max-op-secs` if you see flaky budget hits under parallelism.

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

## Phase C — passive R(V) / C(V) golden-curve diff (`run_passives.py`)

Catches VCR/VCC coefficient drift, re-introduced `abs()` kinks (a cusp at
V=0 would change the bias-dependent curve), unit-typo regressions on
`rsh`/`cj`, and similar passive-card changes.

- **Resistors (5):** `RPOLY_HI`, `RPOLY_LO`, `RNWELL`, `RNPLUS`,
  `RPPLUS`. Single `.dc Vp -5 5 0.25` sweep; extract
  `R(V) = V / -i(Vp)`.
- **Capacitors (4):** `CMIM_STD`, `CMIM_HI`, `CMOM`, `CFRINGE`. PWL
  ramp 0 → 5 V over 1 ms (so `dV/dt = 5000 V/s`) inside a `.tran`;
  extract `C(V) = -i(Vp) / dV/dt`.

Each device's curve is interpolated onto a fixed comparison grid and
diffed against a stored golden in `goldens/`. Tolerance is relative
(default `--tol 1e-3` = 0.1 %).

### Running

```sh
# Check against the stored goldens (~9 ngspice runs, a couple of seconds)
python pdk_validation/regression/run_passives.py

# Overwrite goldens from the current lib (use only when the lib's
# passive behavior is the new accepted baseline)
python pdk_validation/regression/run_passives.py --regenerate

# Restrict to specific devices
python pdk_validation/regression/run_passives.py --device CMIM_STD RNWELL

# Tighter or looser tolerance
python pdk_validation/regression/run_passives.py --tol 1e-4
```

### Goldens

Stored under `pdk_validation/regression/goldens/<device>.json`, one
file per device:

```json
{
  "device": "RPOLY_HI",
  "type": "r",
  "ngspice_version": "45.2",
  "v_grid": [-5.0, -4.75, ..., 5.0],
  "values": [12289.42, 12286.36, ..., 12289.42]
}
```

The current goldens were generated on the post-P0 lib. If you make a
deliberate change to a VCR/VCC coefficient or a passive `rsh`/`cj`,
re-run with `--regenerate` and commit the updated goldens alongside
the lib change so the diff stays clean.

### Sanity of current baseline

| Device     | R or C range (V = ±5 V)      | Comment                                |
|------------|------------------------------|----------------------------------------|
| `RPOLY_HI` | 12.27 – 12.29 kΩ             | rsh=1200, L/W=10 → 12 kΩ; VCR ~0.16 %  |
| `RNWELL`   | 18.65 – 19.55 kΩ             | strongest VCR (~5 % at 5 V)            |
| `CMIM_HI`  | 20.00 – 20.03 pF             | cj=0.002, area=1e-8 m² → 20 pF; VCC ~0.15 % |
| `CFRINGE`  | 1.81 pF (flat)               | weakest VCC                            |

## Phase D — short transient per device class (`run_transients.py`)

One canonical `.cir` per device class lives under `transients/`:

| Deck                       | Class  | Stress                                                |
|----------------------------|--------|-------------------------------------------------------|
| `bsim_inverter.cir`        | BSIM3  | NMOS18+PMOS18 inverter switching at 1.8 V w/ 10 fF    |
| `vdmos_switching.cir`      | VDMOS  | NDMOS20 switching a 10 Ω load from 12 V (5 V gate)    |
| `bjt_common_emitter.cir`   | BJT    | NPN_LV common-emitter pulse response                  |
| `diode_rectifier.cir`      | Diode  | DIO_PN half-wave rectifier, 5 V / 1 MHz, RC load      |
| `r_thru_zero.cir`          | R      | RNWELL with 1 MHz sine — V(p,n) crosses 0 V each ½-cycle |
| `c_thru_zero.cir`          | C      | CMIM_HI same — strongest VCC, charge thru V=0         |

The last two are the "abs() kink killers": pre-fix, those AC-through-zero
sinusoidal sweeps hung at >120 s because the non-smooth `|V|` term in
the VCR/VCC expressions destabilized the Newton/LTE timestep loop. The
post-fix `sqrt(V*V + 1e-6)` runs each in ~55 ms.

The harness asserts:
- the deck reaches its `TRAN_OK` marker,
- ngspice prints no fatal-error / timestep-too-small patterns,
- wall time stays under the deck's budget (2 s for active devices,
  3 s for the passive AC-through-zero decks).

### Running

```sh
# Full run (~0.4 s wall total on the current lib)
python pdk_validation/regression/run_transients.py

# Restrict to one or more decks
python pdk_validation/regression/run_transients.py --deck r_thru_zero c_thru_zero

# Tighten or loosen budgets uniformly (e.g. for a deliberately slower deck)
python pdk_validation/regression/run_transients.py --max-overrun 2.0
```

Baseline on the post-P0 lib (ngspice-45.2):

| Deck                  | Wall    | Budget |
|-----------------------|---------|--------|
| BSIM3 inverter        | ~120 ms | 2.0 s  |
| VDMOS switching load  | ~55 ms  | 2.0 s  |
| BJT common-emitter    | ~60 ms  | 2.0 s  |
| Diode rectifier       | ~60 ms  | 2.0 s  |
| RNWELL AC thru 0 V    | ~55 ms  | 3.0 s  |
| CMIM_HI AC thru 0 V   | ~55 ms  | 3.0 s  |

Every deck uses <10 % of its budget — there's headroom for a 20×+
regression before the gate trips. The decks are intentionally short
so the suite stays usable as a pre-commit smoke check.

## Remaining phases (planned)

- **Phase E**: Monte Carlo harness (validates AGAUSS re-randomization
  across MC iterations — see handoff P1 "Monte Carlo validation").
- **Phase F**: GitHub Actions wiring with pinned ngspice version.

See `docs/PDK_HANDOFF.md` (or the handoff source) for the full backlog.
