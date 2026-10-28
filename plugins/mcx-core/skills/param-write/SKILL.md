---
name: param-write
description: Write values to live Motorcortex parameters on the connected controller — single value, bulk write, or partial array slice. Confirms writability and reports failures clearly. Use to command setpoints, toggle inputs, or push test values.
owner: coen
review-by: 2027-01-28
---

Write to live Motorcortex parameter(s): "$ARGUMENTS"

This skill calls the controller MCP tools (`check_connection`,
`set_parameter`, …) from this plugin's own bundled `mcx-core` MCP
server — no other plugin is required. Other Motorcortex plugins may expose
the same tool surface; if several are connected, prefer the `mcx-core`
server's tools.

Parse the arguments for:
- **path** + **value** for a single write, OR
- **items**: list of `{path, value [, offset, length]}` for bulk writes

If the user gave a value but no path, or vice versa, ask once.

## Step 1: Verify connection

Call `check_connection`. If not connected, ask for the controller IP and call `configure_connection(url="wss://<ip>")`. Stop on persistent failure.

**Confirm it is the right machine.** The connection persists across sessions,
so it may still point at a controller from earlier work. Compare the
`MCX_URL` it reports with the machine the user is talking about: if they
mention a local simulation (`localhost`, `127.0.0.1`), a portal VM, or a
different IP than the one connected, stop and ask before writing. Name the
controller URL in the Step 3 summary and in the final report — every write
result carries it as `controller`.

## Step 2: Pre-flight each path

For every target path, call `get_parameter_info(path)` and inspect:
- **Type flag**: must be `input`, `parameter`, or `parameter_volatile`. `output` → refuse, explain that outputs are computed by the controller.
- **Array size**: scalar (size 1) vs array. The provided value shape must match — scalar to scalar, list-of-N to array of size N (or use `offset`/`length` for a slice).
- **Element type**: coerce numeric literals correctly (`bool` → true/false, `int32` → integer, `double` → float).

If any path fails pre-flight, list the issues and stop **before** writing anything. Do not partial-write.

## Step 3: Confirm intent for risky writes

Live parameter writes affect the running controller. Before writing, summarize what you are about to do (controller URL, then path → old value → new value) and ask the user to confirm if any of the following apply:
- Mode/state commands (paths matching `*/stateCommand`, `*/modeCommand`, `*/enable*`, `*/reset*`)
- Anything under `root/Logic/...` or `root/MainControlLoop/...`
- The user is on a real (non-simulation) machine — check `config.json:Mode == "Production"` if the package is at hand, or just ask.

For obviously safe scratch values (e.g. user parameters under `root/UserParameters/...`), proceed without extra confirmation.

## Step 4: Write

Single write:
```
set_parameter(path="root/...", value=<scalar or list>)
```

Bulk (≥2 values, atomic round-trip — preferred when targeting multiple paths):
```
set_parameter_list(items=[
  {"path": "root/Foo/a", "value": 1.0},
  {"path": "root/Foo/b", "value": [0, 0, 0]},
  {"path": "root/Bar/slice", "value": [9, 9], "offset": 2, "length": 2}
])
```

## Step 5: Verify

After writing, read the values back (`get_parameter` or `get_parameter_list`) and report, starting with the controller URL the write went to:
- ✓ written + verified for each path, OR
- ✗ mismatch → show requested vs actual (the controller may clamp, reject, or overwrite from a feedback loop)

## Notes
- Writing to an `output` parameter will be rejected by the MCP — do not retry, fix the path.
- `parameter_volatile` is not persisted across controller restarts; mention this if the user expects persistence.
- For test/setpoint sweeps, use `set_parameter_list` in a loop — never `set_parameter` per element.
