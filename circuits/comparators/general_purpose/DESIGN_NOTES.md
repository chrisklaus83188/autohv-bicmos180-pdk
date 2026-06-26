# General-purpose comparator — topology & tuning guide

How the `cmp_gp.lib` comparator works, what sets each spec, and how to re-size or
re-architect it for different performance. Companion to `CHARACTERIZATION.md`
(measured numbers) and `SATURATION_SIGNOFF.md` (Vds/Vdsat sign-off).

---

## 1. Architecture

A two-stage transconductance comparator with a digital output buffer. Three gain
stages plus a current-mirror bias. NMOS-input (`CMP_NIN`, high common mode) shown;
PMOS-input (`CMP_PIN`, low common mode) is the vertical mirror (swap N↔P, gnd↔vdd).

```
            vdd                              vdd            vdd
             |                                |              |
        Xm3=||  ||=Xm4   (PMOS mirror load)  ||=Xm5        ||=Xm7
        n1 --+----+-- n2 -------------------- gate         (PMOS)
             |    |        (stage-1 out)       |            |
   inp --||Xm1   Xm2||-- inn                  o2 ----+----- out --> 0/VDD
             |    |                            |     |      |
             +-tail+                           |    gate   ||=Xm8
                |                          Xm6=||  (stage-3 (NMOS)
          Xtail=||  (tail, 2*IREF)        (NMOS  inverter)  |
                |     M=2                  4*IREF)          gnd
               gnd                            |
                                             gnd
   bias pin --||Xmb diode, IREF;  drives Xtail, Xm6, Xhtail
```

- **Stage 1 — transconductor (Xm1/Xm2 + Xm3/Xm4 + Xtail).** NMOS differential
  pair on a tail current source, loaded by a PMOS current mirror that converts the
  differential current to a single-ended voltage at `n2`. Gain ≈ gm₁·(ro₂‖ro₄).
- **Stage 2 — gain / level shift (Xm5 + Xm6).** PMOS common-source amp (`Xm5`,
  gate = `n2`) with an NMOS current-source load (`Xm6`). Gain ≈ gm₅·(ro₅‖ro₆).
  Self-biased: `Xm5` is 4× the mirror unit and `Xm6 = 4·IREF`, so at balance the
  two currents match without a separate bias.
- **Stage 3 — output buffer (Xm7/Xm8).** Plain CMOS inverter; squares the slow
  internal swing into a rail-to-rail logic edge and drives the load.
- **Bias (Xmb, Xtail, Xm6).** One mirror off the bias pin (`ibp_5uA` on CMP_NIN, `ibn_5uA` on CMP_PIN) distributes the
  external reference: `Xmb` = IREF (diode), `Xtail` = 2·IREF, `Xm6` = 4·IREF.
- **Enable (`EN`).** Active-high power-down: a 2-inverter buffer (`ENB=/EN`, `ENbuf=EN`)
  drives a PMOS header (`vdd→vdda`) + NMOS footer (`vssa→vss`) that isolate the core when
  `EN=0` (zero static Iq), with `OUT` forced low. The EN buffer runs on the true rails;
  the header/footer are sized wide so their IR drop doesn't eat the saturation margin
  (verified to still pass, incl. the 1.8 V brown-out corner).

Nodes: `n1` (mirror diode), `n2` (stage-1 output / stage-2 input), `o2` (stage-2
output / buffer input), `tail` (pair source). Ports: `inp inn out vdd vss <bias> EN` (`ibp_5uA`/`ibn_5uA` bias; `EN` = active-high enable).

### Polarity (OUT high when V(inp) > V(inn))
inp↑ → I(Xm1)↑ → mirror copies it to Xm4, which pushes `n2` **up** → Xm5 (PMOS)
current **down** → `o2` **down** → inverter output `out` **up**. Net: non-inverting.

---

## 2. What sets each spec

| Spec | Set by | Direction |
|------|--------|-----------|
| **Input offset (σ)** | gate AREA of stage-1 matching pair + load (Xm1-4) | σ ∝ 1/√(W·L) |
| **DC gain** | output resistance of stage-1 & stage-2 → device **L** | gain ↑ with L |
| **Speed (tpd)** | current **density** on the high-Z nodes (n2, o2); buffer drive into load | faster with I/C, i.e. higher overdrive |
| **ICMR (CM range)** | tail Vdsat + input Vgs (overdrives) → current and W/L *ratios* | wider with lower current / lower overdrive |
| **Quiescent current** | IREF (Iq ≈ 7·IREF, state-dependent ~2:1) | ↑ with IREF |
| **Area** | all device W·L; dominated by stage-1 (at high FIN) | — |
| **Hysteresis** | steered current HYSK·IREF into stage-1 | window ≈ HYSK·IREF/gm_in |

Two facts that make tuning predictable:
- **Overdrives (Vov, Vdsat) depend on current and W/L *ratios*, not absolute size.**
  → ICMR, gain region, and gm are set by ratios; you can change absolute size
  freely without moving them.
- **Matching depends on absolute gate *area* (W·L).** → offset is the one thing
  that moves when you scale a device's area at fixed W/L.

---

## 3. Tuning recipes (re-size for different performance)

These use the existing knobs (`IREF`, `WSCALE`, `WIN/LIN`, `LANA`, `FIN`, `HYSK`)
— no netlist change.

### Lower input offset
- **`FIN` up.** Scales stage-1 (pair + load) W and L together → area ∝ FIN²,
  σ ∝ 1/FIN, while ICMR/gm/gain hold. This is `gp`→`lo`→`lo2`. Continuous — set
  `FIN=6` for ~0.3 mV. Costs area and a little input capacitance (slower).
- Floor: matching only. For **sub-100 µV** you need dynamic cancellation
  (auto-zero / chopper) — a different cell, not a sizing change.

### Higher DC gain
- **`LANA` up** (longer L on mirror/stage-2 → higher ro). Cheap gain, costs area
  and a little speed. Watch the DIBL floor (below).
- Structural: add a **cascode** to the mirror or stage-2 load (more gain per L, but
  eats ICMR/output-swing headroom — poor fit at low supply), or add a **third
  gain stage** (needs care to stay fast/stable open-loop).

### Faster (lower tpd)
- **Current *density* up** (raise `IREF` at the same widths) → higher overdrive →
  faster internal slew. This is `fast` (2× density ≈ 1.6×). **Caveat:** higher
  Vov raises Vdsat → **narrower ICMR** (and fails Vds/Vdsat>1.4 at low supply if
  pushed too far). It is the direct trade against the saturation margin.
- **Do NOT current-scale** (raise IREF *and* widths together): it holds I/C
  constant on the internal nodes → same speed at more power/area. Verified.
- Stronger **output buffer** (`WSCALE` up, or split Xm7/Xm8 wider) helps the edge
  into a heavy load, at more input cap on `o2`.
- Shorter **L** raises fT, but keep **L ≥ 1 µm on Xm6** (and the bias devices):
  at 0.5 µm the stage-2 load (≈VDD across it) runs away on DIBL — its current
  inflated ~3× and Iq blew up. The input-pair L can go shorter (it only affects
  offset/gain).

### Lower power
- **`IREF` down.** This is `lp` (~8 µA). Slower; also note **offset rises** as the
  pair enters weak inversion (gm_load/gm_in → 1, so the load mismatch contributes
  more). Lower current also *widens* ICMR (lower Vdsat).

### Wider ICMR
- **Lower current density** (lower IREF, or wider tail at fixed current) → lower
  Vdsat → the tail-limited edge moves toward its rail. The tail current source is
  almost always the limiting device; its drain rides with the input common mode,
  so the edge facing the tail's own rail is what runs out.
- ICMR is **VDD-dependent**: each input stage burns ~1.9 V from its own rail
  (Vgs/Vsg + tail headroom + 1.4× margin), so the rail-facing edge tracks VDD. At
  3.2 V a single part can't span mid-rail from both directions — see the joint-
  coverage gap in `SATURATION_SIGNOFF.md`.
- For **full 0–VDD input**, run a **complementary NIN+PIN pair** (NMOS-input for
  the upper CM, PMOS-input for the lower) and OR/merge their outputs.

### Add / tune hysteresis
- **`HYSK`** (fraction of IREF steered back into stage 1). Window ≈ HYSK·IREF/gm_in;
  bounded (HYSK<1) so it can't latch. `hyst` uses 0.2 (~10–13 mV). Continuous.

### Different common-mode region
- Pick the flavor: `CMP_NIN` (high CM), `CMP_PIN` (low CM). They are sized
  differently for the two mobilities (PMOS pair is ~2× wider).

---

## 4. Design rules & gotchas (hard-won)

- **L ≥ 1 µm on the current sources / stage-2 load** (DIBL current blow-up below).
- **Tail = the ICMR limiter**, and its Vds/Vdsat is best at balance, worse with a
  large differential overdrive (one input device then carries the full tail
  current). The ICMR is the *balanced* (inputs-equal) common-mode range.
- **Iq is state-dependent (~2:1)** — the single-ended stage-2 branch conducts in
  one output state and is off in the other. Spec the worst case.
- **tpd is asymmetric** (rise vs fall) and flips sign N↔P — inherent to the
  single-ended output node; quote the slow edge.
- **Current sources must stay saturated in every state; signal nodes rail by
  design.** Apply the Vds/Vdsat>1.4 rule to the tail/bias/mirror at the linear
  point, not to the output buffer or to railed nodes.
- **Don't widen the bias mirror to buy ICMR** (the removed `WB` knob): it cost
  ~4× bias area for ~0.25 V. Trim current or size the pair instead.
- Keep the **stage-2 self-bias ratio** (Xm5 = 4× mirror unit, Xm6 = 4·IREF) when
  re-sizing, or stage 2 won't sit in its active region at balance.

---

## 5. When the knobs aren't enough (topology-level changes)

| Goal | Change |
|------|--------|
| Sub-100 µV offset | Auto-zero (output/input offset storage) or chopper around this core |
| Much higher gain | Cascode the loads, or telescopic/folded-cascode stage 1, or a 3rd stage |
| ps-class speed, clocked | Replace with a StrongARM / double-tail dynamic latch (no static Iq) |
| Full rail-to-rail input | Complementary input pairs summed in a folded cascode — **built**: see `../rail_to_rail_5v0/` and § 7 below |
| Different supply class | Re-map devices: NMOS33/PMOS33 (3.3 V), NMOS18/PMOS18 (1.8 V), NMOS12/PMOS12 (12 V) — re-bias and re-check ICMR/saturation |
| HV input sensing | Resistive/cascode attenuator (NDMOS) ahead of a low-voltage core |

The first three move outside the "general-purpose CT" family by design; the PDK's
separate Cells A–D set already covers clocked, bipolar-precision/auto-zero,
low-Iq monitor, and 200 V HV-sense roles if you need those.

---

## 6. Knob reference

| Param | Scales | Moves | Holds |
|-------|--------|-------|-------|
| `IREF` | all bias currents | speed, power, ICMR | offset, area |
| `FIN`  | stage-1 pair + load (W&L) | offset (1/FIN), area (FIN²) | ICMR, gm, ~gain |
| `WSCALE` | mirror/tail/stage-2/buffer width | drive, area | (ratios → ICMR/gain) |
| `WIN/LIN` | input-pair base geometry | offset, input cap | — |
| `LANA` | mirror/gain/bias length | gain, area | (current via mirror) |
| `HYSK` | steered hysteresis current | hysteresis window | — |

Re-characterize any change with `run_comparators.py` (specs/offset) and
`run_saturation.py --pvt` (ICMR / Vds·Vdsat sign-off).

---

## 7. Rail-to-rail input variant (`CMP_RR`, `../rail_to_rail_*`)

The GP `CMP_NIN`/`CMP_PIN` pair covers the rail in two halves; where their ICMRs
don't overlap (mid-rail at low VDD) there's a *coverage gap*. `CMP_RR` removes it
by sensing rail to rail in one cell.

**Architecture.** An NMOS pair (high CM) and a PMOS pair (low CM) run in parallel
and their currents are **summed in a folded-cascode stage**: top fold current
sources feed the NMOS-pair drains, PMOS cascodes fold those into the summing
nodes where the PMOS pair also injects, and a bottom NMOS mirror converts to
single-ended. Then the usual CS stage-2 + inverter. Near each rail one pair is
cut off and contributes ~0 *current*; mid-rail both are active (gm roughly
doubles).

**Why not just OR two comparators?** A pair starved near a rail makes its
preamp/output rail to a *stuck* level (and NIN vs PIN stick to opposite states),
which corrupts any digital combine. Summing at the transconductance level is what
lets the off pair drop out cleanly. You pay ~2× Iq for the second pair + fold.

**The one bias rule that matters — reference the cascode bias to the rail it must
track.** The PMOS cascode gate `vcp` is generated **VDD-referenced** (VDD − 2|Vsg|
from PMOS diodes), not from ground-referenced NMOS diodes. A ground-referenced
bias pins the NMOS-pair drains `x,y` at a fixed level; when VDD sags to brown-out
the top fold sources (from VDD to `x`) lose all their Vds and fall out of
saturation (seen: fold Vds/Vdsat 0.2 at 3.2 V). VDD-referencing makes `x` track
the rail, holding the fold-source headroom ~constant across the whole supply
(0.2 → 4.7). This is the single most headroom-critical spot in the cell.

**Knob.** Only `FIN` — scales both input pairs and the bottom mirror (W&L
together): offset ≈ 1/FIN, matching area ∝ FIN². gp/lo/lo2 = FIN 1/2/3.

**Sign-off.** `run_saturation.py --pvt` checks every *always-on* device over the
full 0→VDD CM (input pairs exempt in their hand-off, by design). Result: 5 V and
3.3 V hold Vds/Vdsat > 1.4 rail-to-rail across PVT; 1.8 V holds > 1.1 (the
low-voltage relaxation), and notably **closes the GP 1.8 V brown-out gap**.

**Porting.** Same as the GP family — swap the device class, re-tune the `vcp`
PMOS-diode count for the rail (1.8 V uses fewer drops), re-run the two scripts.
