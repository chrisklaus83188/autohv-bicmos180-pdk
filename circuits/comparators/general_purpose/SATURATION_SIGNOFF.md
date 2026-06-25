# cmp_gp saturation-margin sign-off (Vds/Vdsat > 1.4)

Sign-off of the `cmp_gp.lib` comparators against the rule: **every device intended
to operate in saturation keeps Vds/Vdsat > 1.4** over the operating envelope.

Reproduce: `python run_saturation.py --pvt` (ICMR bands) and
`python run_saturation.py --cm-scan` (per-device detail at a fixed CM).

## Envelope checked

| Axis | Values |
|------|--------|
| Process | TT, FF, SS, FS, SF (5 corners) |
| Temperature | −40 °C, +27 °C, +125 °C |
| Supply (5 V rail) | **3.2 V, 5.0 V, 5.5 V** (rated range 3.2–5.5) |
| Input common mode | swept to find the band where the rule holds (ICMR) |

Binding case is **3.2 V + 125 °C + a slow corner (SS/FS)**: low supply squeezes
tail headroom and hot raises Vdsat (mobility drops). Process-only at 27 °C / 5 V
hides this — temperature and low supply are the axes that bind.

## ICMR definition

The **input common-mode range** is the common-mode span — inputs tied **equal**
(balanced diff pair) — over which every input-stage device intended to be saturated
keeps **Vds/Vdsat ≥ 1.4**. The binding device is the **tail current source**: as the
common mode approaches the tail's rail, the tail runs out of Vds and the range
ends. (Stricter of the two natural definitions; the looser one sets the edge at
Vds = Vdsat, ratio = 1.0.)

## Methodology

- **Evaluated at the trip** (`v(o2) = VDD/2`): the operating point where the whole
  signal chain is simultaneously in its active region. At a resolved output,
  stage-2 and the buffer legitimately enter triode/cutoff — not a violation.
- **Included** (must stay saturated): bias diode, tail, input pair, mirror
  diode + output, stage-2 driver + load, hysteresis current source.
- **Excluded** (large-signal switches by role): output inverter `Xm7/Xm8`,
  hysteresis steering switches `Xmha/Xmhb`.

### Device roles — the current sources are what really matter

A comparator spends most of its time decided, so most signal nodes are railed.
What must stay biased in *all* states vs what rails by design:

- **Always-on current sources / bias:** the **bias reference `Xmb`** and the
  **tail `Xtail`** (and hysteresis tail `Xhtail`). Drains on stable nodes; saturated
  in every output state.
- **Signal devices:** input pair, mirror diode/output `Xm3/Xm4`, stage-2
  driver/load `Xm5/Xm6` — saturated only in the active region; rail by design when
  decided (`Xm6` is a current source but its drain is the railing output `o2`).

Measured (`nin_gp`, 5 V, CM 2.5, SS, 125 °C), balanced (trip) vs decided (railed):

| device | role | balanced | decided |
|--------|------|---------:|--------:|
| `Xmb` bias ref   | current source | 4.51 | **4.51** (rail-independent) |
| `Xtail` tail     | current source | 3.57 | **4.21** |
| `Xm6` stg2 load  | signal (drain rails) | 8.23 | ~0 |
| `Xm4` mirror out | signal (drain rails) | 2.83 | ~0 |

The bias reference and tail hold across all output states; the tail also sets the
ICMR. Signal devices railing when decided is correct behaviour, not a violation.

## Sizing principle (why there is no `WB` knob)

ICMR is set by device **overdrives** (Vgs_in, Vdsat_tail) → by current and W/L
*ratios*. Input offset is set by absolute gate **area** (W·L). Two consequences:

1. The offset↔area knob `FIN` scales the stage-1 matching set (input pair + load
   mirror), W and L together → overdrives (ICMR) and gm (gain) hold, offset ∝
   1/FIN. So `gp`(FIN1)/`lo`(FIN2)/`lo2`(FIN3) all **share an ICMR** (bands above
   match within ~0.05 V) and differ only in offset/area.
2. To buy ICMR, lowering current (or sizing the input pair) is far more
   area-efficient than widening the bias mirror. An earlier revision had a `WB`
   knob that quadrupled the bias mirror to hold the tail margin at 3.2 V/hot — it
   cost ~400 µm² for ~0.25 V of low-end ICMR and was **removed**. We accept the
   natural (narrower) ICMR instead; see the 3.2 V note below.

## Input common-mode range per VDD (worst over process + −40/+125 °C)

Within each band, all included input-stage devices hold Vds/Vdsat ≥ 1.4. The
`gp`/`lo`/`lo2`/`hyst` set **shares an ICMR** (the `FIN` offset knob scales W and L
together → overdrives unchanged); `lp` (lower current) is a touch wider.

| Variant   | 3.2 V        | 5.0 V        | 5.5 V        |
|-----------|--------------|--------------|--------------|
| `nin_gp`  | 1.71–2.72 V  | 1.71–4.73 V  | 1.70–5.27 V  |
| `nin_lo`  | 1.71–2.76 V  | 1.69–4.77 V  | 1.70–5.28 V  |
| `nin_lo2` | 1.68–2.75 V  | 1.69–4.77 V  | 1.68–5.28 V  |
| `nin_hyst`| 1.71–2.71 V  | 1.71–4.70 V  | 1.70–5.25 V  |
| `nin_lp`  | 1.33–2.97 V  | 1.32–4.79 V  | 1.34–5.28 V  |
| `pin_gp`  | 0.21–1.26 V  | 0.22–3.07 V  | 0.22–3.58 V  |
| `pin_lo`  | 0.21–1.29 V  | 0.22–3.08 V  | 0.22–3.58 V  |
| `pin_lo2` | 0.21–1.29 V  | 0.22–3.10 V  | 0.22–3.60 V  |
| `pin_hyst`| 0.21–1.3 V*  | 0.22–3.07 V  | 0.22–3.57 V  |
| `pin_lp`  | 0.21–1.72 V  | 0.22–3.52 V  | 0.22–4.02 V  |

NIN low edge ~1.7 V (absolute, VDD-independent); high edge tracks the rail. PIN
low edge ~0.2 V; its high edge is the PMOS-tail headroom limit, lower because PMOS
needs more Vsg and has higher Vdsat hot. `lp`'s lower current drops both tails'
Vdsat → wider band. *Hysteresis-variant bands are approximate (the regenerative
load complicates the trip-point evaluation).

## Joint NIN + PIN coverage (gp pair)

| VDD   | Joint coverage | Notes |
|-------|----------------|-------|
| 3.2 V | 0.21–1.26 V **and** 1.71–2.72 V | **~0.45 V gap at mid-rail** (1.26–1.71) |
| 5.0 V | **0.22 – 4.73 V** (continuous) | overlap 1.71–3.07 |
| 5.5 V | **0.22 – 5.27 V** (continuous) | overlap 1.71–3.58 |

At 5.0/5.5 V the pair covers ~0.2 V to within ~0.2 V of the top rail with no gap.
**At 3.2 V there is a ~0.43 V gap around mid-rail** — the cost of not widening the
bias mirror. The parts still *function* through the gap; the tail merely dips below
the 1.4 margin there. To close it: raise `IREF`/tail sizing, or sense that band
with whichever part has its tail on the far rail. (Accepted as-is — the library is
a set of general starting points, not a sign-off to a specific spec.)

## Differential-overdrive note (separate from ICMR)

ICMR is the **common-mode** (inputs-equal) definition, by design. With a large
**differential** overdrive (decided state) one input device carries the full Itail,
raising its Vgs and pushing the tail ~0.4·Vov closer to its rail — so the tail can
dip below 1.4 even at a common mode inside the ICMR, near the edges, at 3.2 V. This
is intentionally **not** part of the spec (arbitrary input pairs are not required
to hold the margin). At 5.0/5.5 V there is ample headroom in all input states.

## Limits / notes

- A single part cannot hold the margin to *both* rails — inherent to a simple
  tail+pair stage, tightest at 3.2 V. Use the NIN+PIN pair (with the 3.2 V mid-rail
  caveat) or a different input stage for full-rail sensing at 3.2 V.
- Bands are from BSIM3 model sign-off, not silicon.
