"""Connection state, configuration, and low-level helpers."""

import json
import os
import logging
from pathlib import Path

import motorcortex
from motorcortex import McxConnectionError, McxLoginError

def _state_dir() -> Path:
    """Where saved settings live.

    Claude Code's per-plugin data folder when it runs the server: it survives
    plugin updates, which replace the install folder this script sits in.
    Next to this script otherwise (tests, a server started by hand).
    """
    data = os.environ.get("CLAUDE_PLUGIN_DATA")
    return Path(data) if data else Path(__file__).parent


_config_file = _state_dir() / "motorcortex_config.json"
_default_cert = str(Path(__file__).parent / "mcx.cert.crt")

_req: "motorcortex.Request | None" = None
_sub: "motorcortex.Subscribe | None" = None
_parameter_tree: "motorcortex.ParameterTree | None" = None
_loaded_hash: "int | None" = None


def _get_config() -> tuple[str, str, str, str]:
    url = "wss://localhost"
    login = "admin"
    password = "vectioneer"
    cert = _default_cert

    if _config_file.exists():
        try:
            saved = json.loads(_config_file.read_text())
            url = saved.get("MCX_URL", url)
            login = saved.get("MCX_LOGIN", login)
            password = saved.get("MCX_PASSWORD", password)
            # A saved path into an earlier install folder is gone after an
            # update; the bundled certificate stands in for it.
            saved_cert = saved.get("MCX_CERT")
            if saved_cert and Path(saved_cert).is_file():
                cert = saved_cert
        except Exception:
            pass

    url = os.environ.get("MCX_URL", url)
    login = os.environ.get("MCX_LOGIN", login)
    password = os.environ.get("MCX_PASSWORD", password)
    cert = os.environ.get("MCX_CERT", cert)

    return url, login, password, cert



def save_config(config: dict) -> Path:
    """Write the connection settings to the saved-settings file.

    The bundled certificate is not stored by path: its path changes with every
    plugin update, and it is the default anyway. The file holds a password, so
    only the user can read it.
    """
    config = dict(config)
    if config.get("MCX_CERT") == _default_cert:
        config.pop("MCX_CERT")
    _config_file.parent.mkdir(parents=True, exist_ok=True)
    _config_file.write_text(json.dumps(config, indent=2))
    _config_file.chmod(0o600)
    return _config_file

def _is_default_config() -> bool:
    url, _, _, _ = _get_config()
    return url == "wss://localhost"


def _tree_hash() -> "int | None":
    try:
        return _req.getParameterTreeHash().get(timeout_ms=2000).hash
    except Exception:
        return None


def _refresh_tree_if_changed() -> None:
    """Reload the cached tree when the controller's tree hash has moved.

    `reconnect=True` restores the session after a controller restart but
    keeps the tree loaded at first connect, so a redeployed config would
    otherwise stay invisible until the MCP server restarts.
    """
    global _loaded_hash
    current = _tree_hash()
    if current is None or current == _loaded_hash:
        return
    try:
        msg = _req.getParameterTree().get(timeout_ms=10000)
    except Exception:
        return
    # ParameterTree.load() adds to its path map without clearing it;
    # re-init so paths removed by the new config disappear too.
    _parameter_tree.__init__()
    _parameter_tree.load(msg)
    _loaded_hash = current
    logging.info("Parameter tree changed on the controller; reloaded")


def _get_connection() -> "tuple[motorcortex.Request, motorcortex.ParameterTree]":
    """Return (req, parameter_tree), connecting on first call."""
    global _req, _sub, _parameter_tree, _loaded_hash

    if _req is not None:
        _refresh_tree_if_changed()
        return _req, _parameter_tree

    url, login, password, cert = _get_config()

    _parameter_tree = motorcortex.ParameterTree()
    types = motorcortex.MessageTypes()

    _req, _sub = motorcortex.connect(
        url,
        types,
        _parameter_tree,
        certificate=cert,
        timeout_ms=5000,
        login=login,
        password=password,
        reconnect=True,
    )
    _loaded_hash = _tree_hash()
    logging.info("Connected to Motorcortex at %s", url)
    return _req, _parameter_tree


def _connection_error_message(e: Exception) -> dict:
    """Return a structured error with diagnostics and remediation steps."""
    url, login, _, cert = _get_config()
    msg = str(e)
    host = url.replace("wss://", "").replace("ws://", "").split("/")[0]

    hints = []

    if isinstance(e, McxConnectionError):
        hints.append(
            f"Connection timed out connecting to '{url}'. "
            "Check that the Motorcortex controller is powered on and reachable."
        )
        hints.append(f"Test connectivity: ping {host}")

    elif isinstance(e, McxLoginError):
        hints.append(
            f"Authentication failed for user '{login}'. "
            "Ask the user for the correct login and password, then call configure_connection()."
        )

    else:
        hints.append(
            f"Could not connect to Motorcortex at '{url}' as '{login}'. "
            "Ask the user to verify the controller IP, login, and password, "
            "then call configure_connection()."
        )

    return {
        "error": msg,
        "diagnostics": hints,
        "current_config": {
            "MCX_URL": url,
            "MCX_LOGIN": login,
            "MCX_CERT": cert,
        },
        "next_step": "Call configure_connection(url=..., login=..., password=...) with the correct values from the user.",
    }


def _reset_connection() -> None:
    global _req, _sub, _parameter_tree, _loaded_hash
    _req = None
    _sub = None
    _parameter_tree = None
    _loaded_hash = None
