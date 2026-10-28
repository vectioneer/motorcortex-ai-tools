#!/usr/bin/env python3
"""
Motorcortex Core MCP Server

Exposes live parameter tree access on a connected Motorcortex controller —
the tool surface behind the mcx-core param-explore and param-write skills.

Connection settings are loaded in priority order:
  1. Environment variables (MCX_URL, MCX_LOGIN, MCX_PASSWORD, MCX_CERT)
  2. Saved settings (motorcortex_config.json in the plugin's data folder,
     $CLAUDE_PLUGIN_DATA; next to this script when that is not set)
  3. Defaults (wss://localhost / admin / vectioneer)

Use the configure_connection tool to save settings in chat — no file editing needed.
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)

from server import mcp          # noqa: E402
import tools_connection         # noqa: E402, F401
import tools_parameters         # noqa: E402, F401
from tools_connection import configure_connection, check_connection
from tools_parameters import (
    get_parameter, set_parameter,
    list_parameters, get_parameter_info,
    get_parameter_list, set_parameter_list,
)

if __name__ == "__main__":
    mcp.run()
