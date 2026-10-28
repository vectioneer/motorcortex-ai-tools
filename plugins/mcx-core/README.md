# mcx-core

Motorcortex platform context and live parameter access for AI assistants.
Gives the assistant the platform's terminology and a picture of how a
Motorcortex system is put together, and lets it explore and write the
parameter tree of a controller you connect it to.

Other Motorcortex plugins, such as `mcx-desk`, build on this one.

## Install

```
/plugin marketplace add vectioneer/motorcortex-ai-tools
/plugin install mcx-core@motorcortex
```

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) on your `PATH`. The controller MCP server
  runs through `uv run --locked`, which installs the exact package versions
  in `mcp/uv.lock`; there is no virtualenv to create.
  macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh` —
  Windows: `winget install astral-sh.uv`

## Skills

| Skill | Covers |
|---|---|
| `terminology` | Platform-wide terms (Motorcortex, MCX, MCX-Robot, Motion Controller, …) and one word per machine type |
| `architecture-overview` | What a Motorcortex system consists of: runtime, parameter tree, communication layer, client APIs, tools, test environments, security model |
| `docs-map` | Every page on docs.motorcortex.io by section, so the right page is fetched instead of guessed |
| `param-explore` | Browse the live controller parameter tree — list, get, info, batch, find |
| `param-write` | Write values to live parameters with pre-flight checks, confirmation for risky writes, and read-back |

## What it runs and connects to

- **On session start** a hook checks that `uv` is installed and prints how to
  install it if not. It runs nothing else.
- **On its first start** after an install or update, the MCP server downloads
  `fastmcp`, `motorcortex-python` and their dependencies from PyPI, at the
  versions pinned in `mcp/uv.lock`, into a Python environment in the plugin's
  data folder (`~/.claude/plugins/data/`).
- **The MCP server** (`mcp/`) connects only to the controller you configure,
  over WebSocket with TLS (`wss://`), using the bundled Motorcortex Root CA
  certificate (`mcp/mcx.cert.crt`).
- **Connection settings** resolve in this order: the `MCX_URL`, `MCX_LOGIN`,
  `MCX_PASSWORD` and `MCX_CERT` environment variables, then the saved
  settings (written when you give the assistant a controller address in
  chat), then the factory defaults (`wss://localhost`, login `admin`).
- **Saved settings** are kept in `motorcortex_config.json` in the plugin's
  data folder (`~/.claude/plugins/data/`), so they survive plugin updates and
  are removed when you uninstall the plugin. The file holds the login and
  password in plain text and is readable only by you; to keep credentials out
  of it, set the environment variables instead.
- **Writes** go through the `param-write` skill, which checks each path's
  type, shape, unit and active links first and asks before mode, state and
  logic changes.
- **What Claude sees**: parameter paths and values the assistant reads
  become part of your conversation with Claude, like anything else you share
  with it. The plugin sends nothing anywhere else: no telemetry, no other
  servers.

For API-level detail, consult https://docs.motorcortex.io.
