---
name: param-explore
description: Explore the live Motorcortex parameter tree on the connected controller — list paths under a prefix, read values, fetch type/array metadata, or batch-read many paths. Use to inspect runtime state, find paths by name, or verify a path exists before referencing it.
review-by: 2027-01-28
---

Explore the live Motorcortex parameter tree: "$ARGUMENTS"

This skill calls the controller MCP tools (`check_connection`,
`get_parameter`, …) from this plugin's own bundled `mcx-core` MCP
server — no other plugin is required. Other Motorcortex plugins may expose
the same tool surface; if several are connected, prefer the `mcx-core`
server's tools.

Parse the arguments for:
- **action**: one of `list`, `get`, `info`, `batch`, `find` — infer from phrasing if not explicit
- **path** / **prefix**: full parameter path (`root/...`) or a name fragment to search for
- **paths**: list of paths (for `batch`)

If unclear, ask the user once.

## Step 1: Verify connection

Call `check_connection`.
- **Configured + connected**: proceed.
- **Not configured / failed**: ask the user for the controller IP. Then call `configure_connection(url="wss://<ip>")`. If it still fails, stop and report the error.

## Step 2: Run the action

### `list` — one level under a prefix
```
list_parameters(prefix="root/<branch>")
```
Returns the level below the prefix, not the subtree: each entry is a `leaf`, or
a `branch` with a `descendants` count standing in for everything under it.
Descend by calling again with that branch as the prefix — do not raise `depth`
to see more of the tree at once, and never pass `depth=0` on `root`.

The result is self-describing: `truncated` with a `note` when a level was cut
(narrow the prefix rather than raising `limit`), `suggestions` when the prefix
matched nothing, and `private_hidden` counting the runtime-private `:` pipes
left out. Pass `include_private=True` only if the user asks about them.

### `get` — read a single value
```
get_parameter(path="root/...")
```
Report the value. For arrays show length + first ~10 elements, then `...` if truncated.

### `info` — fetch metadata
```
get_parameter_info(path="root/...")
```
Report `param_type` (`INPUT`, `OUTPUT`, `PARAMETER`, …), `data_type`, `elements` (array size), `unit` when present, and any `flags` — `LINK_IS_ACTIVE` means a link drives the value.

### `batch` — read many paths in one round-trip
```
get_parameter_list(paths=[...])
```
Use this whenever the user wants ≥3 values together — a single call is faster than N `get_parameter` calls.

### `find` — locate paths by name fragment
```
list_parameters(prefix="root", contains="<fragment>")
```
The search runs on the controller side, at any depth under the prefix, and is
case-insensitive. Never fetch a level and filter it yourself — that pulls the
subtree into the session to throw most of it away. If the result is
`truncated`, narrow the prefix or lengthen the fragment.

## Step 3: Output

For reads, present in compact form:
```
root/Foo/bar             = 3.14    (DOUBLE, scalar, m)
root/Foo/positions       = [0.0, 1.5, ...] (DOUBLE[6])
```

If a path is missing, `list_parameters` on it already returns `suggestions`
from the deepest prefix that does exist — offer those rather than computing
matches yourself.

## Notes
- The tree on the controller is authoritative. Snapshots in `control/control.xml` may be partial.
- Read-only — never write here. For writes use the `param-write` skill.
- `:`-segments (e.g. `root/Logic/:stateToBus/...`) are internal IPC pipes,
  filtered out by the tool; mention they are runtime-private if a user asks
  about the `private_hidden` count.
