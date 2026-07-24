# Brief: architecting a high-side voltage monitor when the only HV devices are subthreshold at the available bias current

I'm designing a charge-pump voltage monitor on a 180 nm automotive BiCMOS process
with 200 V LDMOS. I've hit a device-level wall and want the **architecture**
question analyzed before I size anything further. Everything you need is inline —
you don't have access to the PDK or my schematics.

---

## 1. The question I want analyzed

**How should this monitor be partitioned so that its trip accuracy is not set by
the 200 V devices?** Concretely: which functions must live in the HV domain, which
can be pushed into the 5 V domain, and what is the cleanest interface between them?

Secondary: is there a way to use the HV devices as *precision* elements that I've
missed, or is "HV = standoff only" the correct conclusion?

---

## 2. The process

180 nm BiCMOS, automotive high-voltage. Relevant inventory:

| Class | Devices | Notes |
|---|---|---|
| Core MOS | NMOS/PMOS at 1.2, 1.8, 3.3, 5.0 V | Full BSIM3, well characterized |
| HV LDMOS | NDMOS 20/40/60/80/120/200 V, PDMOS 20/40/60/80/120/200 V | VDMOS macromodel + subckt wrapper |
| Bipolar | NPN_LV (BV_CBO 14 V), PNP_LAT (18 V), NPN_HV (45 V), PNP_HV (32 V) | Gummel-Poon + behavioural avalanche |
| Zeners | DZ_5V6, DZ_12, DZ_24 | |
| Resistors | RPOLY_HI, RPOLY_LO, RNWELL, RNPLUS, RPPLUS | |
| Caps | CMIM_STD, CMIM_HI, CMOM, CFRINGE | |

**Critical gap: there is no analog MOS device between 5 V and 20 V.** The core MOS
stop at 5 V and the next device up is a 20 V LDMOS. Nothing in between.

### The 200 V devices in detail

`NDMOS200` / `PDMOS200`, parameters `W`, `L`, `M`:

- **`L` is not channel length** — it's the drift/extended-drain length. Only the
  200 V pair exposes it; all lower-voltage LDMOS have it fixed at process minimum.
  Reference value `L_REF = 8 µm`, hard clamp at 5 µm, recommended RESURF window
  5–16 µm.
- The drift resistance is modeled as a *delta* on top of the 8 µm reference:
  `RDRIFT = k·(L_eff/8µm − 1)/m`, floored at ~0. So **L < 8 µm buys nothing**
  (it clamps) and only L > 8 µm costs you resistance. L = 8 µm is the calibration
  point, not an optimum.
- **Breakdown is held at the model rating regardless of L.** Physically shortening
  the drift would collapse BV; the model won't show it. Short-L devices look
  free in simulation and would fail in silicon.
- BV: 225 V (N), 207 V (P). Vth: +1.25 V (N), −1.31 V (P).
- **Mismatch scales as 1/√(W/W_REF) — width only, not √(W·L).** σ(Vth) = 3.67 mV
  at W = 10 µm. Length buys no matching, only drift resistance.
- The 200 V models are **engineered** (scaled from the fitted 80 V pair), not
  silicon-fit. Trends are trustworthy; absolute magnitudes are not calibrated.

---

## 3. Characterization I ran (ngspice, typical corner, L = 8 µm)

### Current capability is a non-issue

| | W = 10 µm | W = 100 µm | W = 1000 µm |
|---|---:|---:|---:|
| NDMOS200 I_max | 1.8 A | 18 A | 180 A |
| PDMOS200 I_max | 0.69 A | 6.9 A | 69 A |

My budget is ~100 µA. That's four decades of margin. Conduction is never the limit.

### But at 100 µA every geometry is in subthreshold

PDMOS200, Vds = 200 V, I = 100 µA:

| W (µm) | V_ov (mV) | gm/I (1/V) | σ(Vth) (mV) | σ(I)/I, matched pair |
|---:|---:|---:|---:|---:|
| 2 | +80 | 15.7 | 8.20 | 18.2 % |
| 10 | −4 | 21.8 | 3.67 | 11.3 % |
| 100 | −95 | 27.2 | 1.16 | 4.5 % |
| 300 | −134 | 28.5 | 0.67 | 2.7 % |
| 1000 | −175 | 29.1 | 0.37 | 1.5 % |

gm/I is pinned near the subthreshold ceiling (~26/V) at every usable size. The
devices don't reach moderate inversion until roughly **1 mA** — the transconductance
parameter is a power-FET value (kp = 0.088 A/V² for the PMOS), so a device sized
for any sane area sits in weak inversion at analog currents.

**The counter-intuitive consequence:** widening the device pushes it *deeper* into
subthreshold, but matching still improves monotonically, because σ falls as 1/√W
faster than gm/I creeps up (21.8 → 29.1). So you size for matching and simply
accept weak inversion. Narrowing toward moderate inversion is the wrong move.

### Why this is fatal for precision

In subthreshold gm/I is maximal, so the mirror pair's Vth mismatch is amplified
~80–170× into the sensed threshold. A Monte-Carlo of an HV mirror front-end on
this process gives **σ(trip) ≈ 340–440 mV** — a half-volt-class monitor. Sizing
barely helps: bigger W lowers σ(Vth) but lowers current density further. Running
at mA to escape subthreshold blows the current budget.

This is a known, **open, unresolved** issue in the PDK's own backlog. The
maintainers have not decided whether to re-fit the transconductance or to declare
the family power-only and add a separate HV analog device. **I cannot wait for
that and I cannot change the model card.**

---

## 4. The design as it stands

`CP_VoltageMonitor` — senses a charge-pump output (`CP`) relative to a high-side
input rail (`VIN`, up to 200 V), and closes a regulation loop. Current contents:

- 4 × NDMOS200 and 2 × PDMOS200, **all at the default W = 10 µm, L = 8 µm**
- 3 × RPOLY_HI resistor strings (L = 100 µm, W = 10 µm)
- 6 × NMOS50, 1 × PMOS50, 2 × 5 V inverters
- 1 × 5 V two-stage comparator (`CMP_PIN_5V0`)
- An `IBIAS` current input
- Basic sensing and regulation loop; **no disable switches yet**

At the as-built W = 10 µm, the HV pair mismatch is 11.3 % — the worst point on the
table above. The HV devices are sitting at library defaults that were never chosen
for this job.

---

## 5. Constraints

1. **The current budget is genuinely µA.** The charge-pump output is
   current-limited; I can't bias the HV front end at mA.
2. **No HV analog MOS below 20 V.** Anything precise has to happen at ≤5 V or be
   built from LDMOS/bipolar.
3. **Bipolars can't stand off the rail alone** — best is NPN_HV at 45 V, PNP_HV at
   32 V, against a 200 V rail. They'd need an LDMOS cascode above them.
4. **Model fidelity is limited.** The 200 V cards are engineered, not silicon-fit.
   I should not design something whose correctness depends on the absolute value of
   an uncalibrated HV parameter.
5. **Transient simulation above ~120 V is unreliable.** A second open PDK issue:
   fast HV edges with floating LDMOS front-ends drive the timestep toward zero and
   never complete. DC and quasi-static transients are fine. So a topology that can
   only be validated by a fast HV transient is a topology I can't verify.

---

## 6. Options I see (critique these, and add what I've missed)

- **A — Size up the HV mirror.** W = 300–1000 µm gets pair mismatch to 1.5–2.7 %.
  Cheapest change, keeps the current topology. Costs a lot of area, and the trip
  accuracy still rests on uncalibrated HV devices in weak inversion.
- **B — Push precision into the 5 V domain.** HV devices do standoff and level
  shifting only; a resistor divider does the attenuation; the actual comparison
  happens at 5 V where there are well-characterized devices and a cascode mirror
  that holds gain to 1.0000 flat across PVT. Accuracy then rests on resistor
  *ratio* matching, which is a much better-behaved quantity.
- **C — Resistive divider with a zener clamp front end.** Simplest, but static
  current through a divider off a 200 V rail against a µA budget needs checking.
- **D — Bipolar front end under an LDMOS cascode.** Vbe matching is typically far
  better than subthreshold Vth matching and bipolars have no weak-inversion
  pathology. But the LDMOS cascode is still in the signal path, and NPN_HV/PNP_HV
  need protection from the full rail.
- **E — Something structurally different that I haven't considered.**

---

## 7. What I'd like back

1. A recommended partition, with the reasoning made explicit — especially *where
   the accuracy actually comes from* in your choice, and what that quantity's own
   tolerance is.
2. The failure modes of that choice: what breaks it, what it's sensitive to, what
   it silently depends on.
3. Honest treatment of option B's weak points if you land there — divider loading,
   the HV-to-5 V interface, what happens during CP startup and at the UVLO floor,
   and whether the level shift itself reintroduces the mismatch problem I'm trying
   to escape.
4. A short list of simulations that would confirm or kill the recommendation,
   preferring DC/quasi-static ones given constraint 5.

Push back if you think the framing is wrong — including if you think the right
answer is that this monitor shouldn't be built as a continuous-time analog
comparison at all.
