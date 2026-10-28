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
  runs through `uv run`, which resolves `mcp/requirements.txt` on start and
  caches it; there is no virtualenv to create.
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

- **On session start** a hook checks that `uv` is installed and prepares the
  Python environment, which downloads `fastmcp` and `motorcortex-python` from
  PyPI the first time.
- **The MCP server** (`mcp/`) connects only to the controller you configure,
  over WebSocket with TLS (`wss://`), using the bundled Motorcortex Root CA
  certificate (`mcp/mcx.cert.crt`).
- **Connection settings** resolve in this order: the `MCX_URL`, `MCX_LOGIN`,
  `MCX_PASSWORD` and `MCX_CERT` environment variables, then
  `mcp/motorcortex_config.json` (written when you give the assistant a
  controller address in chat), then the factory defaults (`wss://localhost`,
  login `admin`).
- **The saved config file** holds the login and password in plain text, inside
  the plugin's install folder. A plugin update replaces that folder, so the
  setting is lost and you give the address again. To keep credentials out of
  that file and across updates, set the environment variables instead.
- **Writes** go through the `param-write` skill, which checks each path's
  type and shape first and asks before mode, state and logic changes.

For API-level detail, consult https://docs.motorcortex.io.
