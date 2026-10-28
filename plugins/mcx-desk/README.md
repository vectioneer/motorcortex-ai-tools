# mcx-desk

Lets an AI assistant drive a running Motorcortex Desk tab: plot live
controller signals and custom computed signals, frame the view, capture
screenshots, export buffered data as CSV, save and load trace setups, and
compute statistics, FFT spectra and step-response metrics over what is
plotted.

Builds on `mcx-core`, which is installed with it and adds the parameter-tree
skills.

## Install

```
/plugin marketplace add vectioneer/motorcortex-ai-tools
/plugin install mcx-desk@motorcortex
```

## Prerequisites

- Node.js 18 or newer on your `PATH`. A session-start hook warns when it is
  missing.
- Motorcortex Desk open in Chrome, Edge or Firefox, connected to a
  controller. Safari blocks the connection from an HTTPS page to the local
  bridge. The deployed Desk at `desk.motorcortex.io` is allowed by default;
  other Desk origins are added with `GLPLOT_HUB_ORIGINS` (see
  `mcp/README.md`).

## Skills

| Skill | Covers |
|---|---|
| `desk-plot` | Search parameters, add traces with unit-aware axis placement, custom signals, update rate, view |
| `desk-capture` | Screenshot the plot, export CSV, save or load the trace setup |
| `desk-analyze` | Statistics, spectra, overshoot, settling and rise time, lag between traces |

## What it runs and connects to

- **The MCP server** (`mcp/server.mjs`, Node.js, no dependencies to install)
  listens on `127.0.0.1:8474` only. The Desk tab connects to it from your
  browser; nothing is reachable from other machines.
- **The controller connection** is the one the Desk tab already has. The
  bridge does not open its own.
- **Files** — CSV exports, screenshots, trace setups — are read and written
  only inside `~/glplot-hub-files`, or the directory set in
  `GLPLOT_HUB_FILE_DIR`.
- **Parameter writes** through `write_parameter` change a real machine. The
  assistant is instructed to ask you to approve each exact path and value
  first, one approval per write, and to mark the call as approved. The bridge
  does not verify that approval: it is a flag the caller sets.
- **Who can reach the bridge**: any program on this computer, and any page
  served from `localhost`, can connect to the bridge port and use it like the
  Desk tab, parameter writes included. Run the plugin only on a computer you
  trust and do not share.

Port, origins and file directory settings: `mcp/README.md`.
