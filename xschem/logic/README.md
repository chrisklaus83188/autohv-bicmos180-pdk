# logic/ — AutoHV async-logic cell symbols

24 static-CMOS gate symbols for `circuits/async_logic_design/cells.lib`:
**INV, BUF, NAND2, NOR2, AND2, OR2, XOR2, XNOR2** in **1V8 / 3V3 / 5V0**.
Regenerate with `bash xschem/gen_logic_syms.sh`.

## Power is connected BY TEXT (no wires, no pins)
Each gate has only signal pins (`in/out` or `a b out`). Supply and ground are
**net names** carried by the symbol, shown as text:
- `VPWR` (default **vdd**) — the supply net. Drive it once in your testbench.
- `VGND` (default **0**) — ground; node `0` is global, so ground auto-connects.

The gate netlists as e.g. `xU1 a b out vdd 0 NAND2_3V3`. To use a different
supply net (e.g. a 5 V rail), select the gate, press `q`, and change `VPWR`.

## Using the gates
1. Place gates (`Insert` -> `logic/<CELL>`), wire only the **signals**.
2. Drop one **`autohv_lib`** block (PDK models + corner) and one **`logic_lib`**
   block (includes `cells.lib`, declares `.global vdd`).
3. Add a supply: a `vsource` driving net `vdd`. Ground is `0` automatically.

Verified: `INV_3V3` inverts (Vin 0->3.3 gives OUT 3.3->0) with power by text only.
