# comparators/ — AutoHV comparator cell symbols

9 comparator symbols for the canonical PDK comparator library,
`circuits/comparators/comparators_all.lib`. Regenerate with
`bash xschem/gen_cmp_syms.sh`.

All cells share the same interface — single-output, ports
**`inp inn out vdd vss <bias> EN`**, OUT high when V(inp) > V(inn). The bias pin is
**`ibp_5uA`** (NIN, RR) or **`ibn_5uA`** (PIN); **`EN`** is the enable input:

| Family | Variants | Input stage |
|---|---|---|
| CMP_NIN | _1V8 / _3V3 / _5V0 | general-purpose, NMOS input |
| CMP_PIN | _1V8 / _3V3 / _5V0 | general-purpose, PMOS input |
| CMP_RR  | _1V8 / _3V3 / _5V0 | rail-to-rail input |

Params (editable per instance with `q`): NIN/PIN carry `IREF WSCALE WIN LIN LANA FIN HYSK`
(WIN 40u for NIN, 80u for PIN); RR carries `IREF FIN`.

## Power is connected BY TEXT (no wires/pins)
Only signal pins (`inp inn out nb`) are exposed. Supply/ground are net-name
properties `VPWR` (default **vdd**) and `VGND` (default **0**), shown as text.
Netlists as `xU1 inp inn out vdd 0 ibp_5uA EN CMP_NIN_5V0 …`. Drive net `vdd`
once; ground `0` is automatic. The bias pin (`ibp_5uA`/`ibn_5uA`) takes a 5 µA
reference (e.g. `Ib vdd <bias> 5u`); `EN` is the enable.

## Using them
1. Place a comparator (`Insert -> comparators/<CELL>`), wire inp/inn/out and nb.
2. Drop **`autohv_lib`** (PDK models + corner) and **`cmp_lib`** (includes
   `comparators_all.lib`, `.global vdd`) — both resolve via `~/autohv_pdk`.
3. Drive `vdd`; bias `nb`.

All 9 verified: correct port order/params, resolve from `comparators_all.lib`.
