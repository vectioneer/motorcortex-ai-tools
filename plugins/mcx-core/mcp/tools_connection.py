"""Tools: configure_connection, check_connection."""

import json

from fastmcp import Context

import connection as _conn
from server import mcp


@mcp.tool()
def configure_connection(
    url: str,
    login: str = "admin",
    password: str = "vectioneer",
    cert: str = _conn._default_cert,
    ctx: Context | None = None,
) -> dict:
    """Save Motorcortex connection settings and immediately reconnect.

    Call this after the user provides their controller IP/hostname and credentials.
    Settings are saved to a local config file — no need to edit .mcp.json or restart.

    Args:
        url:      WebSocket URL, e.g. wss://192.168.1.100
        login:    Username (default: admin)
        password: Password (default: vectioneer)
        cert:     Path to TLS certificate file (default: mcx.cert.crt in plugin folder)
    """
    config = {
        "MCX_URL": url,
        "MCX_LOGIN": login,
        "MCX_PASSWORD": password,
        "MCX_CERT": cert,
    }
    _conn._config_file.write_text(json.dumps(config, indent=2))
    _conn._reset_connection()

    if ctx:
        ctx.info(f"Connecting to Motorcortex at '{url}' as '{login}'...")

    try:
        _conn._get_connection()
        if ctx:
            ctx.info(f"Connected to Motorcortex at '{url}'")
        return {
            "status": "connected",
            "config": {"MCX_URL": url, "MCX_LOGIN": login, "MCX_CERT": cert},
            "message": f"Connected to Motorcortex at '{url}' as '{login}'.",
        }
    except Exception as e:
        if ctx:
            ctx.warning(f"Connection failed: {e}")
        return {
            "status": "failed",
            "config": {"MCX_URL": url, "MCX_LOGIN": login, "MCX_CERT": cert},
            **_conn._connection_error_message(e),
        }


@mcp.tool()
def check_connection(ctx: Context | None = None) -> dict:
    """Check the current Motorcortex connection status and configuration.

    Use this before any parameter tool to verify the connection is working.
    If not configured or failing, this returns instructions for what to ask the user.
    """
    url, login, _, cert = _conn._get_config()
    config = {"MCX_URL": url, "MCX_LOGIN": login, "MCX_CERT": cert}

    if _conn._is_default_config():
        return {
            "status": "not_configured",
            "config": config,
            "message": (
                "Motorcortex connection not configured yet. "
                "Ask the user: 'What is the IP address of your Motorcortex controller?' "
                "Optionally ask for login and password if they differ from the defaults (admin/vectioneer). "
                "Then call configure_connection(url='wss://<ip>', login=..., password=...)."
            ),
        }

    if ctx:
        ctx.info(f"Checking connection to '{url}'...")
    try:
        _conn._reset_connection()
        _conn._get_connection()
        if ctx:
            ctx.info(f"Connected to '{url}' as '{login}'")
        return {
            "status": "connected",
            "config": config,
            "message": f"Successfully connected to Motorcortex at '{url}' as '{login}'.",
        }
    except Exception as e:
        if ctx:
            ctx.warning(f"Connection failed: {e}")
        return {
            "status": "failed",
            "config": config,
            **_conn._connection_error_message(e),
        }
