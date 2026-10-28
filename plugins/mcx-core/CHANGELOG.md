# Changelog — mcx-core

## 2.8.1 — 2026-10-28

- `get_parameter_info` now reports the parameter type (input, output,
  parameter…), data type, unit, permissions and link flags, so `param-write`
  can refuse outputs and mismatched values before anything is sent.
- Saved connection settings are kept in the plugin's data folder, so they
  survive plugin updates. The file is readable only by you.

## 2.8.0 — 2026-10-28

- First public release: the `terminology`, `architecture-overview` and
  `docs-map` skills, and the `param-explore` and `param-write` skills with
  their bundled controller MCP server.
