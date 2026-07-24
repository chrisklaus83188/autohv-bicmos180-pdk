# Brief: realism review of the 200 V LDMOS models in an automotive BiCMOS PDK

I characterized the 200 V devices in a 180 nm BiCMOS PDK and think I've found a
systematic scaling error in the DC parameters. I want the physics and the reasoning
reviewed by someone who hasn't been staring at it. Everything is inline — you don't
have access to the PDK.

**Please distinguish, in your reply, between what my measurements show and what my
physical assumptions inject.** I've labelled every number as `[model]` (read out of
the PDK), `[measured]` (my ngspice runs), or `[assumed]` (my estimate of what
physical silicon should do). The `[assumed]` values are the weak link and I want
them attacked.

---

## 1. What I want reviewed

1. Is my claim right that the DC parameters (`kp`, `rd`, `rs`) of these devices are
   scaled to a discrete power-FET die rather than to the 10 µm drawn cell the
   wrapper claims?
2. Are my `[assumed]` physical reference values sane for a 200 V LDMOS in a 180 nm
   BiCMOS process — saturation current density, specific on-resistance, cell pitch,
   gate oxide thickness, and Pelgrom A_VT?
3. Is there an interpretation under which the model is *correct* and I'm
   misreading it?
4. Anything else in the model cards that looks unphysical to you.

---

## 2. How the device is constructed

ngspice `VDMOS` macromodel wrapped in a subcircuit. **The `VDMOS` primitive has no
W/L** — device size enters only through the multiplier `m`. The wrapper converts a
drawn width into that multiplier:

```spice
.subckt NDMOS200 d g s params: W=10u L=8u M=1 MM_SIGMA=0
* 200V LDMOS: W free (m=W/W_REF); L = drift length. RESURF window ~5u..16u.
.param W_REF=10u
.param L_REF=8u
.param L_MIN=5u
.param Leff={max(L,L_MIN)}
.param mtot={(W/W_REF)*M}
.param DVTH_MM={MM_ON*AGAUSS(0, 0.011, 3)/sqrt(max(mtot,1e-6)) + ...}
.param RDRIFT={max(1.2*(Leff/L_REF-1)/mtot, 1e-6)}
Rdrift d dd {RDRIFT}
M0 dd g_int s NDMOS200_INT m={mtot}
.ends
```

So **`W_REF = 10 µm` is asserted to be the drawn width of the reference cell**, and
all electricals scale linearly from it via `m`. The PDK's own device-limit table
documents `W` as "total drawn width (um)", range 2 µm … 100 000 µm.

Note `L` is **not** channel length — it's the drift/extended-drain length, clamped
below at 5 µm, and it only adds series resistance for L > 8 µm. Channel length is
documented separately as fixed at process minimum, 0.6–1.0 µm.

## 3. The model card, verbatim `[model]`

```spice
.model NDMOS200_INT VDMOS (nchan
+ vto=1.25          kp=0.22           lambda=0.0012     theta=0.018
+ rd=1.2            rs=0.55           rg=6              rds=2e+10
+ cgdmax=3.5e-14    cgdmin=3e-15      cgs=4.8e-14       cjo=2.2e-14
+ a=0.22            is=2.5e-14        rb=0.65
+ bv=225            ibv=4e-06         nbv=2.2           tt=1.3e-07
+ rq=1.10           vq=260            mtriode=0.45      ksubthres=0.060 )
```

PDMOS200 is the same shape: `vto=-1.31, kp=0.088, rd=3.0, rs=1.38, bv=207`.

`kp` across the whole DMOS family `[model]` — note it is **monotonic in voltage
class**, which is the signature of systematic generation:

| | 20 V | 40 V | 60 V | 80 V | 120 V | 200 V |
|---|---:|---:|---:|---:|---:|---:|
| N-channel kp (A/V²) | 2.80 | 1.90 | 1.20 | 0.80 | 0.45 | 0.22 |
| P-channel kp (A/V²) | 1.30 | 0.85 | 0.55 | 0.38 | 0.21 | 0.088 |

In this macromodel `kp` is the **whole-device** transconductance for the reference
cell (there is no W/L to divide by). Empirically `Id ≈ kp·V_ov²` — verified: at
W=10 µm, V_ov=70 mV, the model gives 1.0 mA and `kp·V_ov²` = 1.08 mA.

---

## 4. What I measured `[measured]`

All ngspice, typical corner, self-heating off, L = 8 µm.

### 4a. Operating point at 100 µA — PDMOS200, Vds = 200 V

| W (µm) | V_ov (mV) | gm/I (1/V) | σ(Vth) (mV) | σ(I)/I, matched pair |
|---:|---:|---:|---:|---:|
| 2 | +80 | 15.7 | 8.20 | 18.2 % |
| 10 | −4 | 21.8 | 3.67 | 11.3 % |
| 100 | −95 | 27.2 | 1.16 | 4.5 % |
| 300 | −134 | 28.5 | 0.67 | 2.7 % |
| 1000 | −175 | 29.1 | 0.37 | 1.5 % |

gm/I is pinned near the subthreshold ceiling (~26/V, i.e. 1/(n·kT/q) with n≈1.5) at
every width above ~10 µm. The device doesn't reach moderate inversion until ~1 mA.
σ(Vth) is computed from the wrapper's own mismatch expression, 1σ = 3.67 mV at
W = 10 µm scaling as 1/√W; σ(I)/I = (gm/I)·σ(Vth)·√2.

### 4b. Saturation current at drawn W = 10 µm, V_ov = +4 V

| device | Id | mA per µm of drawn width |
|---|---:|---:|
| NDMOS20 | 16.74 A | 1674 |
| NDMOS40 | 11.33 A | 1133 |
| NDMOS60 | 6.92 A | 692 |
| NDMOS80 | 4.59 A | 459 |
| NDMOS120 | 2.48 A | 248 |
| NDMOS200 | 1.19 A | 119 |
| PDMOS200 | 0.47 A | 47 |

### 4c. On-resistance at drawn W = 10 µm, V_ov = +4 V, Vds = 0.1 V

| device | R_on | R_on·W (Ω·µm) |
|---|---:|---:|
| NDMOS200 | 4.47 Ω | 44.7 |
| PDMOS200 | 11.59 Ω | 115.9 |
| NDMOS20 | 0.23 Ω | 2.3 |
| PDMOS20 | 0.48 Ω | 4.8 |

---

## 5. My physical reference values — **please check these** `[assumed]`

| quantity | value I used | basis |
|---|---|---|
| LDMOS saturation current density | 0.2 mA/µm | order-of-magnitude for HV LDMOS; 180 nm 5 V NMOS is ~0.6 mA/µm and an LDMOS should be well below that |
| 200 V LDMOS specific R_on | 2 mΩ·cm² | mid-range for a 200 V RESURF LDMOS |
| cell pitch | 20 µm | plausible for a 200 V drift region |
| gate oxide | 20–40 nm | the PDK's 12 V BSIM3 device uses 20 nm; LDMOS gate ox usually tracks the MV device |
| Pelgrom A_VT | 10–20 mV·µm | thick-oxide HV device |

These are the numbers I'd most like corrected. My conclusions are 2–4 orders of
magnitude effects, so I don't think ±3× on any of these changes the verdict — but
tell me if I'm wrong about that.

---

## 6. The inference

Dividing the measured electricals by the assumed physical densities gives the width
each parameter *implies*, against a drawn width of 10 µm:

| device | implied W from `kp` | implied W from `R_on` | ratio between them |
|---|---:|---:|---:|
| NDMOS200 | 5936 µm | 2235 µm | 2.7× |
| PDMOS200 | 2353 µm | 863 µm | 2.7× |
| NDMOS20 | 83 720 µm | 43 288 µm | 1.9× |
| PDMOS20 | 40 066 µm | 20 865 µm | 1.9× |

**Two independent DC parameters agree with each other to within ~2×, while both
disagree with the drawn width by 200–8000×.** The residual 2× is presumably my
current-density and R_sp assumptions being mutually inconsistent; the tight scatter
across four devices is what I'm leaning on. So `kp` is not wrong *relative to*
`rd`/`rs` — they describe the same transistor, and it is a millimetre-scale one.
Those are discrete power-FET die widths.

### The other half of the same subcircuit disagrees

- **Capacitances** `[model]`: `cgs = 48 fF` for the reference cell. For a real
  10 µm × 0.6 µm channel at tox ≈ 20 nm, C_ox·W·L ≈ 10 fF. Same order — consistent
  with a **10 µm** device, not a millimetre one (which would need ~6 pF).
- **Mismatch** `[model]`: σ(Vth) = 3.67 mV at the reference cell. Pelgrom with
  A_VT = 15 mV·µm on 10 µm × 0.6 µm gives ~6 mV. Again consistent with a **10 µm**
  device. A 6 mm device should be ~24× tighter, ~0.15 mV.

So caps and mismatch are scaled to the drawn 10 µm cell; `kp`, `rd`, `rs` are scaled
to a power die.

### There is a direct precedent in this PDK's own history

The capacitances **had exactly this bug and it was found and fixed** a few months
ago. All 13 VDMOS cards had `cgs`/`cgdmax`/`cgdmin`/`cjo` set ~1000× too large for
the 10 µm reference cell; a 40 µm NDMOS200 measured 172 pF of drain capacitance
where the physical figure is tens of fF. The maintainers' diagnosis was that the
values were *"monotonic in voltage class, so they were generated systematically"* —
a unit slip in the generator — and a uniform 1/1000 rescale landed every device in
the physical range.

That fix establishes the intended convention: **`W_REF = 10 µm` is meant to be a
genuine 10 µm drawn cell.** The caps were corrected to it. The DC parameters were
not — and my `kp` table above is monotonic in voltage class in exactly the same way.
It looks like the same generator bug, caught on the AC parameters and missed on the
DC ones.

### Why it matters practically

The two halves get multiplied together. The high gm/I of a millimetre-scale device
in weak inversion, times the Vth mismatch of a 10 µm device, produces an enormous
apparent current mismatch. A downstream design task on this PDK reported σ(trip)
≈ 340–440 mV for an HV current-mirror front end and concluded the family was
unusable as a precision analog device. I now think that number is an artifact of
combining two inconsistently-scaled halves of the same subcircuit, not a silicon
limitation.

If `kp` were physically scaled (~1×10⁻³ A/V² for 10 µm/0.6 µm at tox 20–40 nm), a
W = 10 µm device at 100 µA would sit at V_ov ≈ 300 mV, gm/I ≈ 7 — an ordinary analog
operating point.

---

## 7. Questions

1. Does the inference in §6 hold, or is there a reading in which the model is
   self-consistent and correct?
2. Are the `[assumed]` values in §5 reasonable? Which would you change, and does any
   change alter the conclusion?
3. `kp` and `rd`/`rs` imply widths differing by ~2×. Is that comfortably inside my
   assumption error, or is it telling me something?
4. Does anything else in the §3 card look off — `theta`, `lambda`, `ksubthres`,
   `mtriode`, `a`, `rq`/`vq`, the avalanche parameters, the tempcos?
5. Is modelling drift length as a *pure series resistance* with breakdown held
   constant defensible? The model keeps BV at its rating no matter how short the
   drift gets, which seems backwards — shortening drift should collapse BV.
6. The mismatch model scales as 1/√(W/W_REF) — width only, not √(W·L). For an LDMOS
   where the matched element is the channel, is width-only defensible?

## 8. Where I'm least confident

- All of §5. I derived those from general knowledge, not this process's data.
- Whether `Id ≈ kp·V_ov²` is the right reading of ngspice's `VDMOS` — I verified it
  numerically at one point but haven't read the source.
- Whether a 200 V LDMOS channel really is ~0.6 µm. The PDK says so, but if the true
  channel is much longer, my `kp` target moves.
- I have not checked the 40/60/80/120 V cards as carefully as the 20 V and 200 V
  ones, or the capacitances post-fix.
