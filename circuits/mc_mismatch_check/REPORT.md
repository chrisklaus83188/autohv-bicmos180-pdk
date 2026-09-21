# Monte Carlo check + NMOS5V0 current-mirror mismatch

Two questions, answered in order: does the PDK's Monte Carlo machinery actually
randomize, and what does local mismatch do to a simple 10 uA mirror.

| | |
|---|---|
| simulator | ngspice `ngspice-45` |
| model tag | `v2-grounded` |
| corner / supply / temp | TT (`case=0`) / 5 V / 27 C |
| switches | `MM_ON=1`, `PROC_ON=0` (local mismatch only) |
| runs | 200 |

## 1. Does Monte Carlo work?

Yes. `docs/characterization-inventory.md` item 22 suspects the in-deck
`reset` + `op` loop of being statistically inert, and marks the suspicion **not
confirmed by running**. Running it settles the question the other way: on
ngspice-45 `reset` does re-draw every `.param AGAUSS` in the circuit, so the
loop is live and item 22 can be closed as not reproduced -- with one exception
noted below.

| check | what was driven | distinct samples | sigma/mu | reproducible |
|---|---|---|---|---|
| C1 | MM_ON=0 (negative control) | 1 / 10 | 0.000 % | - |
| C2 | in-deck reset+op loop, unseeded | 40 / 40 | 4.349 % | no |
| C3 | separate invocations, unseeded | 40 / 40 | 4.538 % | no |
| C4 | separate runs, .control `set rndseed=k` | 40 / 40 | 4.947 % | no |
| C5 | separate runs, netlist `.option seed=k` | 40 / 40 | 5.029 % | yes |
| C5b | in-deck loop + fixed `.option seed` | 1 / 40 | 0.000 % | yes |

Per-instance independence is direct, not inferred. In a single run the two
mirror devices report different applied offsets:

```
X1  delvto -7.578 mV   W 4.69712 um
X2  delvto -10.069 mV   W 4.70831 um
```

Both the threshold term and the geometry term are drawn per instance, which is
what makes a mirror ratio move at all.

### Two traps in how you drive it

1. **`set rndseed` inside `.control` does not pin the draw.** It is applied
   after `.param AGAUSS` has already been evaluated at parse time, so the same
   seed gives a different answer every time (check C4). This matters:
   `circuits/current_mirror_char/run_mc.py` documents itself as *"Reproducible:
   run k uses `set rndseed=k`"*, and that claim does not hold on this build.
   Its statistics are still valid, since the draws are live; only the
   reproducibility claim fails.
2. **A netlist `.option seed=N` plus an in-deck loop freezes the loop.** `reset`
   re-seeds the generator to the same value, so all N iterations return one
   identical result (check C5b). That is exactly the inert-loop failure item 22
   predicted, reachable only by adding a fixed seed.

**Use one invocation per sample with `.option seed=k` in the netlist.** That is
the only pattern measured to be both statistically live and bit-reproducible
(check C5), and it is what the mirror run below uses.

## 2. The mirror

Simple two-transistor NMOS mirror, nothing cascoded. Both devices `NMOS5V0`,
W = 4.7 um, L = 1 um, which is the sizing guide's own gm/Id ~ 6 entry for
NMOS5V0 at 10 uA. Reference is an ideal 10 uA source into the diode-connected
device; the output sits at Vdd/2.

```spice
Vdd  dd 0 5
Iref dd in 10u
X1 in  in 0 0 NMOS5V0 W=4.7u L=1u    ; diode-connected reference
X2 out in 0 0 NMOS5V0 W=4.7u L=1u    ; mirror output
Vout out 0 2.5
```

## 3. Result

| quantity | value |
|---|---|
| mean output current | 10.6488 uA |
| standard deviation | 0.4612 uA |
| **sigma / mu** | **4.33 %** |
| min / max over 200 runs | 9.472 / 11.937 uA |
| 1st / 50th / 99th percentile | 9.637 / 10.683 / 11.658 uA |
| mean gain, Iout / Iref | 1.0649 |
| gain with mismatch off | 1.0640 |
| gm/Id at the operating point | 5.58 /V |

The 6.4 % by which the mean sits above 10 uA is **not** mismatch. It is the
systematic gain error of a simple mirror: the reference device runs at
Vds = Vgs = 1.366 V
while the output device sits at 2.5 V, and channel-length modulation makes up the
difference. Turning mismatch off leaves it unchanged at 1.0640. Mismatch is the
spread around that mean, not the offset of it.

Distribution of the output current over the 200 runs:

```
 9.523 uA | ####                                       2
 9.626 uA | ##                                         1
 9.729 uA | #####                                      3
 9.831 uA | #####                                      3
 9.934 uA | #########                                  5
10.037 uA | ###############                            8
10.139 uA | ######################                    12
10.242 uA | ########################                  13
10.345 uA | ###############################           17
10.447 uA | ###########################               15
10.550 uA | ##################                        10
10.653 uA | #################################         18
10.756 uA | ####################                      11
10.858 uA | #################################         18
10.961 uA | ########################################  22
11.064 uA | ######################                    12
11.166 uA | ###########                                6
11.269 uA | #########################                 14
11.372 uA | #######                                    4
11.474 uA |                                            0
11.577 uA | #####                                      3
11.680 uA | ##                                         1
11.783 uA | ##                                         1
11.885 uA | ##                                         1
```

## 4. Cross-check against the model's own numbers

The spread is not only self-consistent, it matches what the wrapper's mismatch
formula says it should be before any simulation is run. `NMOS5V0` in
`autohv_bicmos180_case.lib` draws its threshold offset as

```
AGAUSS(0, 0.033/sqrt(W*L), 3)
```

and ngspice's `AGAUSS(nom, avar, n)` has standard deviation `avar/n`, so the
0.033 V.um figure is a 3-sigma coefficient and the per-device sigma at
W*L = 4.7 um^2 is 5.074 mV.

| quantity | formula | measured over 200 runs | error |
|---|---|---|---|
| sigma(delvto), one device | 5.074 mV | 5.263 mV | +3.7 % |
| sigma(delvto2 - delvto1) | 7.176 mV | 7.394 mV | +3.0 % |
| sigma/mu of Iout | 4.006 % | 4.331 % | +8.1 % |

The predicted current spread is `(gm/Id) x sigma(delta Vth)` = 5.58 x 7.176 mV =
4.00 %, with the W and L mismatch terms adding 0.19 % in quadrature -- they are
negligible here, so this mirror's matching is a threshold-voltage problem and
nothing else.

Independently, `docs/sizing-guide.md` pre-registers **4.08 %** as the matched-pair
sigma(dI/I) for exactly this device, current and geometry. Three numbers derived
three different ways agree:

| source | sigma(dI/I) |
|---|---|
| sizing guide, pre-registered | 4.08 % |
| wrapper formula, hand-computed | 4.01 % |
| this Monte Carlo, 200 runs | 4.33 % |

At 200 samples the standard error on a standard deviation is about 5.0 %, so the
8.1 % gap between measurement and formula is roughly 1.6 standard errors --
ordinary sampling noise, not a discrepancy.

One thing this run does *not* settle: the largest threshold draw seen was 3.14
sigma. The `AGAUSS(..., 3)` third argument is a scale factor in ngspice, not a
truncation, and 200 samples cannot distinguish a truncated tail from a Gaussian one.
If the tails matter for a design, that needs its own experiment.

## 5. Does `M` reduce mismatch?

No. Every mismatch term in the v2.2 MOS wrapper scales as `1/sqrt(AUM2)` with
`AUM2 = W*L`, and `M` is not in it. Same mirror, 120 fixed-seed runs per row,
four times the baseline area reached three ways:

| geometry | total area | sigma(delvto), pooled | formula, v2.2 wrapper | formula, `M` in `AUM2` | sigma/mu(Iout) |
|---|---|---|---|---|---|
| W=4.7 L=1 M=1 | 4.7 um^2 | 5.421 mV | 5.074 mV | 5.074 mV | 4.563 % |
| W=4.7 L=1 M=4 | 18.8 um^2 | 5.421 mV | 5.074 mV | 2.537 mV | 9.164 % |
| W=18.8 L=1 M=1 | 18.8 um^2 | 2.710 mV | 2.537 mV | 2.537 mV | 4.637 % |
| W=4.7 L=4 M=1 | 18.8 um^2 | 2.710 mV | 2.537 mV | 2.537 mV | 1.071 % |

Quadrupling the area through `M` leaves sigma(delvto) where the v2.2 formula
puts it; through W or L it halves. The sigma/mu column also moves with gm/Id --
a wider device at fixed current sits closer to weak inversion, a longer one
further from it -- which is legitimate; the delvto column is the clean evidence.
This table is the "before" for acceptance A1 of the MC realism program: after
the `AUM2` fix the M=4 row must follow the right-hand formula column.

## 6. Runtime, 200 samples

Best of 3, including deck writing and process start-up. Host: Windows-11-10.0.26200-SP0, 12 logical CPUs.

| pattern | wall clock | HANDOFF section 4 |
|---|---|---|
| in-deck loop, one invocation | 0.63 s | 0.7 s |
| `.option seed=k` per invocation, 8 parallel workers | 3.09 s | 3.1 s |
| external driver (alterparam), one invocation | 0.71 s | 0.7 s |

The in-deck loop is fast but not reproducible (check C2). Per-invocation seeding
is reproducible but pays a process start per sample. The external driver keeps
both properties in one invocation, which is the pattern the program's Phase 3
driver builds on (acceptance A11: under 2 s).

## 7. External random-number driver prototype

Each device carries its own knob (`MM_SIGMA={S1}` on X1, `{S2}` on X2) with
`MM_ON=0`; Python draws the unit-normal values (numpy `default_rng(0)`) and
one ngspice invocation steps `alterparam` + `reset` + `op` through all 200 samples.

| quantity | value |
|---|---|
| sigma/mu of Iout | 3.965 % |
| distinct samples | 200 / 200 |
| bit-identical on repeat | yes |
| first-order prediction, one knob per device | 3.936 % |
| wrapper formula, independent terms (section 4) | 4.006 % |
| native `MM_ON=1` measurement (section 3) | 4.331 % |
| HANDOFF section 4 prototype | 3.71 % |

One `MM_SIGMA` scales a device's Vth, W and L terms by the same z, so the three
are perfectly correlated; the W term then partly cancels the Vth term, which is
why the one-knob prediction sits slightly below the independent-terms one. The
program replaces `MM_SIGMA` with independent `Z_VT`, `Z_W`, `Z_L` (R5 as ruled).

## 8. Reproduce

```bash
cd circuits/mc_mismatch_check
python 00_mc_mechanism.py       # does MC randomize, and how must it be driven
python 01_mc_mirror.py          # the 200-run mirror measurement
python 02_mc_m_sweep.py         # does M reduce mismatch (not in the v2.2 wrappers)
python 04_mc_external_proto.py  # external random-number driver prototype
python 03_mc_runtime.py         # wall clock of the three patterns; run last, alone
python report.py
```

Seeds 1..200, one ngspice invocation each, so the numbers above are
bit-reproducible on this build.

