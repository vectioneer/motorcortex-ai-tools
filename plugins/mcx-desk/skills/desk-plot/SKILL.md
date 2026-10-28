---
name: desk-plot
description: Plot live Motorcortex controller signals in a running Motorcortex Desk tab — search parameters, add traces with unit-aware axis placement, set the update rate, frame the view. Also covers custom signals (expressions like actual-minus-reference) for quantities the controller does not publish. Use when the user says "plot X", "show me the velocity live", "compare actual vs reference", "plot the tracking error". Requires an open Motorcortex Desk browser tab; for reading values without plotting, use param-explore; for a frequency plot or a statistic over what is already plotted, use desk-analyze.
review-by: 2027-03-04
---

Plot live controller signals in Motorcortex Desk: "$ARGUMENTS"

This skill calls the mcx-desk MCP tools (`connection_state`, `add_trace`, …).
They relay to a Motorcortex Desk tab open in the user's browser. If a call reports
"no hub tab connected" or "port in use", call `bridge_status` before saying
anything to the user — it reports whether this session owns the bridge port
or relays through another session that does, which process owns it, and
whether a tab is attached. Then act on what it says: no tab means ask the
user to open Motorcortex Desk (or click the dimmed "Claude" badge if another tab
owns it); "port in use" means a non-bridge process holds the port, and the
relay will pick it up by itself once that frees.

Several Claude sessions can share one hub tab, so traces you did not add may
already be on the plot. Check `list_traces` before assuming the plot is
yours, and don't call `remove_all_traces` without asking.

Parse the arguments for:
- **signals**: parameter names or fragments to plot
- **controller**: hostname/IP (only needed when not yet connected)
- **layout hints**: axis wishes, compare-against pairs, rate, time window

## Step 1: Verify the chain

Call `connection_state`.
- **connected**: proceed.
- **disconnected / no hub tab**: if a host is known, call
  `connect(host=...)` and poll `connection_state` until `connected`
  (a few seconds). If no host given, ask the user once.
- **reconnecting**: `connect` is refused while the tab is still retrying
  ("cannot connect while reconnecting"). Call `disconnect` first, then
  `connect`.
- Self-signed controller cert: the browser must have accepted it once
  (visit `https://<controller>` directly) before `connect` can succeed —
  mention this if connecting fails.

**After a controller restart or redeploy** the tab loses its connection and
calls fail with "not connected to controller", or `read_*`/`export_traces`
find no data. Run Step 1 again (`connection_state`, then `disconnect` +
`connect` as needed) and re-add the traces — a redeployed config may have
changed the tree, so resolve the paths again rather than reusing old ones.

## Step 2: Resolve paths

`search_parameters(query=...)` per requested signal. `*` wildcards, matching
case-insensitive. Confirm ambiguous hits with the user; note
`numberOfElements` (array size) for the next step.

The tree is the source of truth. Controllers publish far more than people
expect — error, filtered, derived and setpoint signals are usually already
there under names the user did not think to ask for. Search before concluding
anything is missing: `*error*`, `*Error*`, `*ref*`, `*target*`, `*filtered*`.
Only if a wanted quantity genuinely is not in the tree does Step 3b apply.

## Step 3: Add traces

One `add_trace` call for everything: pass all signals as a
`traces` array — `add_trace(traces=[{path, channel?, axis?}, …])`. The
single form `add_trace(path, channel?, axis?)` remains for one-off adds.
Axis placement — group by physical unit:
- Signals sharing a unit/scale → same y-axis; different unit or magnitude →
  the other axis.
- 6-element pose/twist/wrench arrays: channels 0-2 on `y1`, channels 3-5 on
  `y2` (explicit per-channel entries — a channel-less entry puts all six on
  one axis).
- Actual-vs-reference comparisons: matching channels on the same axis so
  they overlay.

Tune with `set_trace_options` (color, axis, hidden) if the user asks.

Send trace changes one after another, never in parallel. A `remove_all_traces`
issued alongside an `add_trace` can land after it and leave the plot empty —
wait for the clear to return before adding.

## Step 3b: Custom signals — only for what the controller does not publish

`add_custom_signal(name, formula)` computes a signal in the plot from other
signals. **It is a last resort, not a convenience.** Plot the controller's own
parameter whenever one exists: a computed copy starts empty, is only as fast as
the subscription, and can drift from the value the controller actually uses —
so it is strictly worse than the real thing, and misleading if the user assumes
they are looking at the controller's own number.

Reach for it only after `search_parameters` shows the quantity is absent:

| The user asks for | Do this |
|---|---|
| "position error" and `*positionError*` exists | `add_trace` on it |
| "position error", tree has only actual + reference | `add_custom_signal` |
| "speed" and a velocity parameter exists | `add_trace` on it |
| tip distance from x/y/z components | `add_custom_signal` with `hypot(…)` |
| a value in degrees, tree publishes radians | `add_custom_signal` with `deg(…)` |
| a limit line to compare against | `add_custom_signal` with a constant |

Say which one you did and why, so the user knows whether they are looking at
the controller's own signal or an expression you built.

Writing the formula:
- `${full/parameter/path}` reads a signal, `${full/path[0]}` one element of an
  array, `${x}` the x axis (time in seconds).
- An **unindexed** array reference is element-wise: over 6-element arrays,
  `${…/jointPositionsActual} - ${…/jointPositionsTarget}` becomes six traces,
  element *i* from element *i* of each input. This is the normal way to plot a
  per-joint error — do not write six separate signals. A scalar mixed in
  broadcasts across the elements.
- Operators `+ - * / % ^` with parentheses; `abs sqrt exp log log10 log2 sin
  cos tan asin acos atan sinh cosh tanh floor ceil round sign deg rad atan2
  pow hypot min max clamp`; constants `pi`, `e`, `tau`.
- Inputs are subscribed automatically and hidden, so they do not need plotting
  first and nothing is drawn that the user did not ask for. `list_traces`
  flags those `autoAdded` — leave them hidden.
- Calling it again with the same name replaces the expression.
- Read the values back with `read_samples` on `formulas/<name>`;
  `read_values` will not work — the controller has never heard of it.
- Removing any element of a custom signal removes the whole signal.

## Step 4: Rate and view

- Fast signals or "full rate": `set_frequency(divider=1)`; long observations:
  higher divider (UI presets 1/10/100/1000).
- Specific time window or y-range: `set_view`. Default auto-follow is right
  for live watching; `set_view(reset=true)` restores it.

## Step 4b: A frequency plot is a different panel

"Plot the spectrum of X" is not an `add_trace` — the plot draws signals against
time (or against another signal in XY), never against frequency. Plot the
signal first so its samples buffer, then `show_spectrum(path, channel?)` opens
the Spectrum tab beside the plot and draws its FFT there. `desk-analyze` covers
reading the numbers behind it.

## Step 5: Report

`list_traces` and summarize: path, channel, axis, color. Tell the user the
plot is live in their browser tab. Name any custom signal separately, with its
expression and the reason the controller's own parameter could not be used —
a computed signal must never be mistaken for a published one.

## Notes

- An error that reads `[object Object]` (seen from `read_values`) hides the
  real message — usually one path in the list does not exist. Check each path
  with `search_parameters` before retrying.
- Read-only workflow. The `write_parameter` tool exists for setpoint tweaks
  while plotting, but it changes a real machine and may cause motion. Ask the
  user for explicit approval of the exact path and value, and only then set
  `user_approved=true` — every call, even in auto-accept or fully autonomous
  sessions, and never batch approvals: one approval covers one write. Nothing
  downstream re-checks this, so the question you ask is the only safeguard.
  For structured write work use the param-write skill. If the session's
  permission mode blocks the call even after the user approved, do not retry
  or work around it — give the user the path and value to write themselves.
- A one-shot `write_parameter` cannot jog a machine. Velocity and jog inputs
  (`hostInTargetVelocity`, `hostInJointVelocity`, `hostInJogVelocity`,
  `hmiInTargetVelocity`…) are watchdogged: the controller forces them back to
  zero once no write has arrived for `hostInSignalTimeout` — compiled default
  0.1 s — so a single write is a twitch, not a move. Driving a machine needs a
  client writing repeatedly at half that interval; do not try to reproduce it
  with repeated approved writes from here. Writing clients are covered by the
  client API documentation on docs.motorcortex.io.
- To capture or export what is now on screen, continue with `desk-capture`;
  to measure it, `desk-analyze`.
