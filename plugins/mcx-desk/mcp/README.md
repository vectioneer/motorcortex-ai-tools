# mcx-desk MCP server (bundled)

`server.mjs` is the self-contained Motorcortex Desk MCP bridge — a stdio MCP
server that relays tool calls over a local WebSocket (`127.0.0.1:8474`) to a
running Motorcortex Desk browser tab. Requires Node.js 18 or newer; there is
nothing to install.

If a tool named in a skill is missing from your session, update the plugin:
the installed copy predates that tool. If the Desk page is older than the
bridge, a call it does not support returns an error that asks for the page to
be updated.

## Environment

| Variable | Default | Purpose |
|---|---|---|
| `GLPLOT_HUB_MCP_PORT` | `8474` | Bridge port; pair with `?mcpPort=<n>` on the Desk page |
| `GLPLOT_HUB_ORIGINS` | *(empty)* | Extra page origins allowed to connect, for a self-hosted Desk; loopback is always allowed |
| `GLPLOT_HUB_FILE_DIR` | `~/glplot-hub-files` | Only directory the file tools may read or write. Paths escaping it (`..`, absolute elsewhere, symlinks out) are refused, and existing files need `overwrite=true` |

Set them in your environment before starting Claude Code. Keep the file
directory outside the plugin folder: the plugin cache is replaced on every
update.

## Bridge ownership

Only one process can bind the port, so the first Claude session to start owns
the tab and later sessions relay through it as peers; if the owner exits, a
peer is promoted automatically. All sessions therefore drive the *same* tab
and trace list. `bridge_status` reports which role a session has and who owns
the port — it is answered by the server itself, so it works even when no tab
is reachable.
