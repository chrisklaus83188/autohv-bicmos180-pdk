# PMOS Current-Mirror Characterization — AutoHV BiCMOS180, 5 V domain (PMOS50)

A general-purpose DC characterization of PMOS current mirrors for the 5 V (PMOS50)
domain: three topologies, four decades of bias current, two sizing strategies, full
PVT, and 9 000 Monte-Carlo runs. The deliverable is a set of **specified, controlled
mirror designs** and the `I_out(V_out)` curves that describe them completely, so a
downstream block can predict its own bias/ramp behaviour by quadrature from the data
here.

**Instrumentation & discipline.** All mirror devices are PDK `PMOS50` (sources at Vdd,
bulk tied to source → V_SB = 0). `I_in` is an ideal forced current source; the
wide-swing cascode bias is an ideal Vdd-referenced source — both are *instruments*,
and the wide-swing source is additionally cross-checked against a self-biased build.
**No resistors anywhere.** Every reported number is a `.dc`/`.op`/`.meas` result from a
deck in `netlists/`; `metrics.csv` carries a provenance tag per row; `[projection]`
items are walled off and feed no measured number.

**Metric anchors are supply-agnostic** (no application trip point): gain is quoted at
`V_out = Vdd/2`; λ_eff, r_out and ramp-nonlinearity are averaged over a fixed
**0 → 2.0 V in-saturation window** — inside the saturation region of all three
topologies at every supply in the study, including the 3.2 V UVLO floor.

---

## 0. TL;DR

- **Lock L = 2 µm** for the 5 V mirror family: λ·L is minimized there, it hits
  λ_eff ≈ 0.019 /V, and longer L only buys area (∝ L²).
- **Ship `MIR_CS` (standard diode-stack cascode)** as the default: it drops λ_eff by
  **~1000×** (0.019 → 2×10⁻⁵ /V) and r_out by ~850×, holds gain = 1.0000 and λ flat
  across the whole PVT box, for the cost of one extra device. The simple mirror's +2
  to +11 % PVT gain error and 3× λ swing are the price of that saved device.
- **The mirror's entire supply sensitivity is one curve**: I_out(V_SD) collapses across
  Vdd to machine precision, so a downstream block's supply term is fully computable
  from the data here.
- **All three topologies are compliant to well past mid-rail even at the 3.2 V UVLO
  floor** — the standard cascode keeps gain = 1.0000 with compliance to 2.49 V.

---

## 1. Phase 0 — locking L  (`run_phase0.py`, `phase0.json`, `plots/04_*`)

At I_in = 10 µA, TT/5 V/27 °C, W sized for V_ov ≈ 200 mV (gm/I_D ≈ 10.2, IC ≈ 5.5,
moderate inversion); λ_eff and r_out measured in-band:

| L (µm) | W (µm) | V_ov (mV) | λ_eff MIR_S (/V) | λ·L | r_out MIR_S | area (µm²) | λ_eff MIR_CS |
|-------:|-------:|----------:|-----------------:|----:|------------:|----------:|-------------:|
| 0.5 | 16.2 | 201 | 0.1701 | 0.085 | 0.36 MΩ | 16 | 3.6×10⁻³ |
| 1.0 | 37.5 | 200 | 0.0466 | 0.047 | 1.89 MΩ | 75 | 1.8×10⁻⁴ |
| **2.0** | **81.2** | **199** | **0.0191** | **0.038** | **4.99 MΩ** | 325 | 2×10⁻⁵ |
| 4.0 | 163.9 | 201 | 0.0104 | 0.042 | 9.35 MΩ | 1311 | 1×10⁻⁵ |

**Lock L = 2 µm.** λ·L is minimized there (0.038): below it, short-channel DIBL blows
λ·L up (0.085 at 0.5 µm; λ itself explodes to 0.17); above it λ·L stops improving, so
L = 4 µm halves λ only at **4× the area** (∝ L²). λ_eff = 0.019 /V at V_ov = 200 mV is
a good supply-sensitivity operating point for a 5 V bias block.

---

## 2. The locked designs  (data of record: `designs.json`)

**Controlled-comparison rule:** within every design the input diode device, the output
device, and the cascode device are **identical geometry** — only the topology differs,
so any curve difference is attributable to the cascode device alone.

**Strategy B — sized per current** (L = 2 µm, W scaled to hold V_ov ≈ 200 mV):

| design | I_in | W (µm) | V_ov (mV) | gm/I_D | IC | inversion |
|--------|-----:|-------:|----------:|-------:|---:|-----------|
| B_100n | 100 nA | 0.88 | 202 | 10.2 | 5.7 | moderate |
| B_1u   | 1 µA   | 8.29 | 199 | 10.3 | 5.5 | moderate |
| B_10u  | 10 µA  | 81.2 | 199 | 10.3 | 5.5 | moderate |
| B_100u | 100 µA | 795.6| 200 | 10.2 | 5.6 | moderate |

> Sizing did **not** hit a W_min clamp at 100 nA — V_ov = 200 mV needs only W = 0.88 µm
> (> the 0.5 µm floor). Strategy B stays in moderate inversion at every decade.

**Strategy A — one cell (10 µA geometry, W = 81.2 µm) programmed over four decades**
(the "fixed layout, sweep the bias current" use case — programmable current source /
variable bias):

| design | I_in | V_ov (mV) | gm/I_D | IC | inversion |
|--------|-----:|----------:|-------:|---:|-----------|
| A_100n | 100 nA | **−76** | 20.4 | 0.67 | **deep subthreshold** |
| A_1u   | 1 µA   | +40 | 18.5 | 0.98 | weak/moderate |
| A_10u  | 10 µA  | +199 | 10.3 | 5.5 | moderate (≡ B_10u) |
| A_100u | 100 µA | +641 | 2.9 | 97 | strong |

Strategy B answers *"what does a well-sized mirror look like at each current?"*;
Strategy A answers *"what happens to one fixed cell when its bias is programmed over
decades?"* The divergence (below) is the point.

---

## 3. Systematic behaviour at nominal (TT/5 V/27 °C)  (`metrics.csv`)

Locked 10 µA design, gain at Vdd/2, λ_eff/r_out over the 0→2 V window:

| topology | gain @Vdd/2 | λ_eff (/V) | r_out (in-band) | ramp nonlin | compliance V_out,max (1 %) | area (µm²) |
|----------|------------:|-----------:|----------------:|------------:|---------------------------:|-----------:|
| MIR_S  (simple)      | **1.0233** | 0.0191 | 5.0 MΩ | 2.1 % | 0.43 V\* | 325 |
| MIR_CS (std cascode) | **1.0000** | 2.3×10⁻⁵ | 4305 MΩ | 0.002 % | 4.29 V | 650 |
| MIR_CW (wide-swing)  | **1.0001** | 1.1×10⁻⁴ | 920 MΩ | 0.011 % | 4.70 V | 650 |

\* The simple mirror has no compliance *knee* — its 1 % point is just where λ·ΔV_out
reaches 1 % (a continuous droop), not a headroom wall. The cascodes have true knees.

- Cascode drops **λ_eff ~1000× and r_out ~850×** vs the simple mirror.
- Wide-swing adds +0.4 V of compliance over the standard cascode (4.70 vs 4.29 V) —
  its intended benefit — at equal device count.
- `plots/01_topology_family.png` (I_out and gain vs V_out).

---

## 4. The V_SD collapse — **exact**  (`crosscheck.json`, `plots/02_*`)

With ideal I_in and V_SB = 0, I_out must depend on Vdd and V_out only through
V_SD = Vdd − V_out. Resampling the four Vdd sweeps (3.2/4.5/5.0/5.5 V) onto a common
V_SD grid:

> **Max residual across every design and topology = 3×10⁻¹⁶ (machine epsilon).**

Iout at V_SD = 3.0 V reads **10.32326 µA identically** across all four supplies
(B_10u MIR_S). The mirror's *entire* supply sensitivity is captured by the single
I_out(V_SD) curve — including MIR_CW, whose ideal bias is Vdd-referenced and therefore
tracks the supply. There is no Vdd-dependent path that isn't V_SD.

**Consequence:** any downstream block's supply term is computable from this one curve.

---

## 5. PVT robustness (5 corners × 3 temps, Vdd = 5 V)  (`metrics.csv`)

λ_eff [min, max] and gain@Vdd/2 [min, max] over corner×temp:

| design | topo | λ_eff range (/V) | gain@Vdd/2 range |
|--------|------|------------------|------------------|
| B_10u  | MIR_S  | 0.0113 – 0.0314 | 1.011 – 1.045 |
| B_10u  | MIR_CS | 1×10⁻⁵ – 5×10⁻⁵ | 1.0000 – 1.0000 |
| B_100n | MIR_S  | 0.0108 – 0.0299 | 1.009 – 1.036 |
| A_100n | MIR_S  | 0.0139 – 0.0373 | 1.018 – 1.063 |
| A_100u | MIR_S  | 0.0077 – 0.0221 | 1.003 – 1.025 |

- Simple mirror λ_eff **swings ~3×** across PVT; its gain error reaches +5 % here and
  **+11 % worst-case over the full box** (B_10u incl. all Vdd: gain@Vdd/2 ∈ [1.002, 1.104]
  when the low-Vdd/high-VSD corners are included).
- **Cascode λ_eff stays ~2×10⁻⁵ across the entire box** and gain stays 1.0000 — the
  cascode's advantage is not just a lower nominal λ but a λ that *doesn't move*.

---

## 6. Monte Carlo — mismatch dominates the ratio, process moves λ  (`mc_results.json`, 500×)

Nominal PVT, two separate modes (mismatch-only = MM_ON; process+mismatch = MM_ON &
PROC_ON), 500 runs each, on the full V_out grid; σ/µ of I_out at Vdd/2:

| design | topo | mode | σ/µ of I_out@Vdd/2 | σ(λ_eff) |
|--------|------|------|-------------------:|---------:|
| B_10u | MIR_S  | mismatch | 0.52 % | 8.7×10⁻⁶ |
| B_10u | MIR_S  | proc+mm  | 0.55 % | **5.2×10⁻⁴** |
| B_10u | MIR_CS | mismatch | 0.54 % | 4.0×10⁻⁸ |
| B_100n | MIR_S | mismatch | **5.48 %** | 8.6×10⁻⁵ |
| A_100n | MIR_S | mismatch | 1.12 % | 3.3×10⁻⁶ |

1. **A mirror is a ratio → global process cancels.** Adding global process to local
   mismatch barely widens σ/µ of I_out/I_in (0.52 → 0.55 %). Mismatch dominates the
   gain. `plots/05_mc_clouds.png`.
2. **But process does *not* cancel for λ_eff.** σ(λ) jumps **60×** (8.7×10⁻⁶ → 5.2×10⁻⁴)
   when global process is added — the *ratio* is preserved but the *absolute supply
   sensitivity* swings with process. A block that leans on λ inherits this spread.
3. **Matching scales with area (Pelgrom).** The small 100 nA device (B_100n, W = 0.88 µm)
   matches **~10× worse** (5.5 %) than B_10u (0.52 %). The under-driven subthreshold
   cell (A_100n, W = 81 µm) is 1.1 % — better than B_100n (bigger device) but 2× worse
   than B_10u, because subthreshold gm/I_D amplifies V_th mismatch into current
   mismatch. `plots/06_mc_area_effect.png`.
4. The cascode does **not** improve gain-mismatch σ/µ (set by the mirror pair's V_th
   mismatch, which the cascode can't fix) — but its λ distribution is orders tighter,
   so on *supply residual* it wins in both nominal and spread.

---

## 7. UVLO compliance at the 3.2 V floor  (`crosscheck.json`)

At the 3.2 V UVLO floor of the 5 V domain, is each topology still a good current source
up through mid-rail (Vdd/2 = 1.6 V)? (Locked B_10u design.)

| topology | gain @Vdd/2 | droop 0→1.6 V | compliance V_out,max (1 %) |
|----------|------------:|--------------:|---------------------------:|
| MIR_S  | 1.0070 | 2.80 % | 0.57 V\* |
| MIR_CS | **1.0000** | 0.00 % | **2.49 V** |
| MIR_CW | 1.0000 | 0.02 % | **2.90 V** |

Even at UVLO the standard cascode holds gain = 1.0000 with ~0.9 V of compliance margin
above mid-rail. **Cascode headroom is not a limiting concern in this domain** — a
standard diode-stack cascode fits comfortably at the lowest supply.

---

## 8. Known model gap — 100 nA / 150 °C junction leakage  `[projection]`

The PDK MOS subckts set AD/AS/PD/PS = 0, so BSIM3 computes **exactly zero** junction
leakage. At 100 nA / 150 °C this makes results optimistic — flagged. Estimating what
leakage *would* be for the drawn output-device drain (≈ W × 0.6 µm area, plausible HV
p⁺/nwell Js/Jsw at 150 °C):

| design | W (µm) | A_D (µm²) | I_leak est. | fraction of I_in |
|--------|-------:|----------:|------------:|-----------------:|
| B_100n | 0.88 | 0.53 | ~4×10⁻¹⁵ A | < 0.0001 % |
| A_100n | 81.2 | 48.7 | ~3×10⁻¹³ A | < 0.001 % |

`[projection]` — Js/Jsw are order-of-magnitude HV values; feeds no measured number.
**Conclusion:** even pessimistically, junction leakage is a negligible fraction of
100 nA. The 100 nA design point is **real, not a modelling artefact**; its dominant risk
is *mismatch* (~5 % σ/µ), not leakage.

---

## 9. Recommended locked designs

**Selection criterion:** minimum supply-sensitivity residual (nominal λ_eff *and* its
PVT + MC spread) at acceptable area, with guaranteed compliance at the UVLO floor.

| use case | topology | L | W | why |
|----------|----------|---|---|-----|
| **default 5 V mirror (ship this)** | **MIR_CS** | 2 µm | per current (Strategy B) | λ_eff 2×10⁻⁵, flat over PVT, gain 1.0000, compliance 2.49 V at UVLO; +1 device |
| area-critical / λ tolerable | MIR_S | 2 µm | per current | half the devices; accept +2–11 % gain error and 3× λ swing |
| max output swing (rail-limited) | MIR_CW | 2 µm | per current | +0.4 V compliance over MIR_CS; ideal-bias validated against self-biased W/4 build (gain 1.001) |

- **Program the bias, not the geometry.** Strategy B (resize per current) keeps every
  decade in moderate inversion (IC ≈ 5.5, gain-clean). Strategy A (fixed 81 µm cell
  swept over decades) drives the 100 nA point into subthreshold (V_ov = −76 mV) with 2×
  the mismatch and up to +6 % gain error over PVT — usable, but the worst corner of the
  space.
- **Wide-swing bias is an instrument here.** The primary MIR_CW decks use an ideal
  Vdd-referenced source (calibrated per design for max compliance at gain = 1); a
  self-biased W/4 Sooch build reproduces it (gain 1.001, V_out,max 4.50 V), confirming
  the ideal source is faithful — see `mirror_lib.py:build_core` (`MIR_CW_SB`).

---

## Files

```
netlists/        24 decks (8 designs × 3 topologies) + 8 Phase-0, geometry inline
designs.json     every device of every design: W,L,M, V_ov, V_DSAT, gm/ID, IC, area, vbias
results.json     data of record — 1440 sweeps, 100 mV grid every PVT, fine grid at nominal
metrics.csv      metrics table, 1440 rows, each with a provenance tag
mc_results.json  9 000 MC runs (3 designs × 3 topo × 2 modes × 500), every run kept
crosscheck.json  V_SD collapse residuals, UVLO compliance, leakage projection
phase0.json      L-selection sweep
plots/           topology family, V_SD collapse, Strategy A/B, Phase-0 λ(L), MC clouds
mirror_lib.py    deck builders + runner + W-sizing + vbias calibration
analysis.py      band-metric extraction (λ_eff, r_out, compliance) — supply-agnostic anchors
run_phase0.py  build_designs.py  run_dc.py  run_mc.py  compute_metrics.py  make_plots.py
```

Reproduce: `python3 run_phase0.py && python3 build_designs.py && python3 run_dc.py &&
python3 run_mc.py && python3 compute_metrics.py && python3 make_plots.py` (~3 min, 8 cores).
