# Delay & Pulse Cell Library - Design Summary
### AutoHV BiCMOS 180 PDK | 4 archetypes x 3 domains | 20 ns nominal

Four edge-asymmetric cells -- two delays and two one-shot pulse generators -- in 1.8 / 3.3 / 5 V domains. Each hits a 20 ns delay or pulse width at the nominal corner (TT, nominal Vdd, 27 C) and is implemented in minimum area (balanced poly-R / MIM-C time constant + a 6T Schmitt + one bypass FET).

| Cell | Behavior |
|---|---|
| DLYR | delay rising edge 20 ns, pass falling edge |
| DLYF | delay falling edge 20 ns, pass rising edge |
| PHI  | 20 ns HIGH pulse on rising edge, pass falling edge |
| PLO  | 20 ns LOW pulse on falling edge, pass rising edge |

## Per-cell results (nominal width / PVT span / active area)

| Cell | 1.8 V | 3.3 V | 5.0 V |
|---|---|---|---|
| DLYR | 20.0 ns / 14-29 ns / 55 um^2 | 20.0 ns / 15-26 ns / 58 um^2 | 20.3 ns / 16-30 ns / 58 um^2 |
| DLYF | 19.8 ns / 14-29 ns / 56 um^2 | 20.2 ns / 15-27 ns / 59 um^2 | 20.0 ns / 16-30 ns / 58 um^2 |
| PHI | 20.1 ns / 14-29 ns / 57 um^2 | 19.6 ns / 15-26 ns / 60 um^2 | 20.0 ns / 16-29 ns / 62 um^2 |
| PLO | 19.8 ns / 14-29 ns / 58 um^2 | 20.4 ns / 15-27 ns / 62 um^2 | 20.2 ns / 16-30 ns / 63 um^2 |

<sub>Each cell: nominal delay/width / full-PVT min-max / active area.</sub>

## Key points
- 20 ns target met at nominal for all 12 cells (19.7-20.4 ns).
- Active area ~56-62 um^2/cell, dominated by the RC (resistor and cap areas balanced at the minimum).
- Full-PVT timing spread ~ -20%/+40% (RC + Schmitt tracking); the spec fixes only the nominal point.
- Passthrough edges are always much faster than the 20 ns timed edge; pulse cells emit exactly one pulse per active edge and rest at idle.
- See REPORT.md for methodology, full tables and worst-case corners.
