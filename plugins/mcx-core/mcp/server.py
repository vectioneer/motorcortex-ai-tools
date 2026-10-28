"""FastMCP server instance and lifespan."""

import logging
from contextlib import asynccontextmanager

from fastmcp import FastMCP

from connection import _get_config, _is_default_config, _get_connection, _reset_connection


@asynccontextmanager
async def core_lifespan(_: FastMCP):
    url, _, _, _ = _get_config()
    if not _is_default_config():
        try:
            _get_connection()
            logging.info("Motorcortex connected on startup to %s", url)
        except Exception as e:
            logging.warning("Motorcortex startup connection failed (%s) — parameter tools unavailable", e)
    try:
        yield {}
    finally:
        _reset_connection()
        logging.info("Motorcortex disconnected on shutdown")


mcp = FastMCP("Motorcortex Core", lifespan=core_lifespan)
