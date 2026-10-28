---
name: desk-capture
description: Capture or export what a Motorcortex Desk tab is showing — zoom to the region of interest, screenshot the plot as PNG, export buffered trace data as CSV, save or load the trace setup as a JSON file. Use when the user says "screenshot the plot", "export the data", "save this trace setup". For adding signals first, use desk-plot.
owner: coen
review-by: 2027-01-28
---

Capture or export from Motorcortex Desk: "$ARGUMENTS"

Requires traces already plotted (use `desk-plot` otherwise) and a connected
hub tab.

Parse the arguments for:
- **what**: `screenshot`, `csv`, `save-setup`, or `load-setup`
- **region**: time window / y-range of interest, if any
- **file_path**: destination file, if given (see the sandbox rule below)

## Where files go

File tools run in the MCP server process and are confined to one directory:
`GLPLOT_HUB_FILE_DIR`, default `~/glplot-hub-files`. Paths outside it are
refused — `..`, an absolute path elsewhere, and symlinks pointing out all
fail. Pass a **plain relative name** (`step-response.csv`, `runs/today.csv`)
and let it resolve inside that directory; the tool reports the full path it
actually wrote, which is what you quote back to the user.

An existing file is never silently replaced: the call fails with "file
exists" unless you pass `overwrite=true`. Only set that after the user has
agreed to replace that specific file — otherwise pick a different name.

If a user asks for a location outside the sandbox, tell them the file lands
in the bridge directory instead, and that moving it means setting
`GLPLOT_HUB_FILE_DIR` when registering the server.

## Screenshot

1. `get_plot_state` — check paused state and current viewports.
2. Frame the shot: `set_view(xMin=..., xMax=...)` to zoom into the region of
   interest; optionally `pause` first so the window stops moving. A screenshot
   of an unframed auto-following plot is rarely what the user wants.
3. `screenshot` — returns the PNG (WebGL traces + axes/grid/cursor overlay).
4. Restore: `resume` and/or `set_view(reset=true)` if you changed them.

## CSV export

`export_traces(file_path=...)` — always pass `file_path`; without it the full
CSV comes back inline and floods the context. Optional `xMin`/`xMax` limit
the window, `maxRows` caps rows (uniformly decimated, default 100000). Time
column is in ms. Report the path the tool returns and the row count.

## Save / load trace setup

- `save_trace_file(file_path=...)` — writes the trace list (paths, channels,
  axes, colors, hidden flags) as JSON; same format as the hub's Save button.
- `load_trace_file(file_path=...)` — replaces all current traces with the
  file's list, read from the same sandbox directory. Warn that existing
  traces are replaced before calling it.

## Notes

- Exports and saves are read-only with respect to the controller.
- Group related runs in subdirectories of the sandbox (`runs/`, `traces/`)
  rather than flat files with long names — subdirectories are created for
  you.
- After a controller restart or redeploy, calls fail with "not connected to
  controller" or find no data in range. Reconnect and re-add the traces as in
  `desk-plot` Step 1 before capturing or measuring again — the buffer from
  before the restart is gone.
- If a tool fails with "no hub tab connected" or "port in use", call
  `bridge_status` before telling the user anything: it reports whether this
  session owns the bridge, which process does, and whether a tab is attached.
