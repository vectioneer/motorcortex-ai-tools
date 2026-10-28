"""Tools: get/set/list parameter operations (single and batch)."""

import struct
from typing import Any

from fastmcp import Context
from motorcortex import motorcortex_pb2 as _pb

import connection as _conn
import param_tree as _pt
from server import mcp

# MCP delivers an untyped `value` as any JSON scalar, and motorcortex-python's
# encoder assumes the value already matches the parameter's declared type: a str
# takes a branch that builds the struct format '%di' % -1 and raises
# "bad char in struct format". Cast to the declared DataType before writing.
# Verified against motorcortex-python v1.0.3 (motorcortex.proto DataType).
_INT_TYPES = frozenset({_pb.INT8, _pb.UINT8, _pb.INT16, _pb.UINT16,
                        _pb.INT32, _pb.UINT32, _pb.INT64, _pb.UINT64})
_FLOAT_TYPES = frozenset({_pb.FLOAT, _pb.DOUBLE})
_STRING_TYPES = frozenset({_pb.CHAR, _pb.STRING})
_TRUE_STRINGS = frozenset({"1", "true", "yes", "on"})
_FALSE_STRINGS = frozenset({"0", "false", "no", "off"})

# Raised by the encoder when a value cannot be packed; never a connection fault.
_ENCODE_ERRORS = (struct.error, ValueError, TypeError, OverflowError)


def _type_name(data_type: int) -> str:
    try:
        return _pb.DataType.Name(data_type)
    except ValueError:
        return str(data_type)


def _coerce_scalar(data_type: int, value: Any, path: str) -> Any:
    """Cast one scalar to the parameter's declared data type."""
    if data_type in _INT_TYPES:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            text = value.strip()
            try:
                return int(text, 10)
            except ValueError:
                pass
            try:
                return int(float(text))
            except ValueError:
                pass  # fall through to the message below
    elif data_type in _FLOAT_TYPES:
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.strip())
            except ValueError:
                pass  # fall through to the message below
    elif data_type == _pb.BOOL:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            text = value.strip().lower()
            if text in _TRUE_STRINGS:
                return True
            if text in _FALSE_STRINGS:
                return False
    elif data_type in _STRING_TYPES:
        return value if isinstance(value, str) else str(value)
    else:
        # BYTES, USER_TYPE, or a type this mapping does not know: pass through
        # and let the controller be the authority.
        return value

    raise ValueError(
        f"Cannot write {value!r} ({type(value).__name__}) to {path}: "
        f"parameter type is {_type_name(data_type)}."
    )


def _coerce_value(tree: Any, path: str, value: Any) -> Any:
    """Cast value (scalar or list) to the declared type of `path`.

    Returns the value untouched when the type is unknown — an unfamiliar path
    should reach the controller and get the controller's error, not ours.
    """
    if isinstance(value, bytes):
        return value
    data_type = tree.getDataType(path) if tree is not None else None
    if data_type is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_coerce_scalar(data_type, item, path) for item in value]
    return _coerce_scalar(data_type, value, path)


def _write_error(e: Exception, **details: Any) -> dict:
    """Report a rejected write without discarding a healthy connection."""
    return {
        "error": str(e),
        "diagnostics": [
            "The value was rejected before it reached the controller; the "
            "connection is still up — no need to call configure_connection().",
            "Check the parameter's declared type and element count with "
            "get_parameter_info(), then retry with a matching value.",
        ],
        **details,
    }


@mcp.tool()
def get_parameter(path: str, ctx: Context | None = None) -> dict:
    """Read a parameter value from the Motorcortex parameter tree.

    Args:
        path: Full parameter path, e.g. root/Control/dummyDouble
    """
    if ctx:
        ctx.debug(f"Reading {path}")
    try:
        req, _ = _conn._get_connection()
        result = req.getParameter(path).get()
        if result is None:
            return {"error": f"No result returned for: {path}"}
        value = list(result.value)
        return {
            "path": path,
            "value": value[0] if len(value) == 1 else value,
        }
    except Exception as e:
        _conn._reset_connection()
        return _conn._connection_error_message(e)


@mcp.tool()
def set_parameter(path: str, value: Any, ctx: Context | None = None) -> dict:
    """Write a value to a Motorcortex parameter.

    Only works on 'input', 'parameter', and 'parameter_volatile' type parameters.
    Writing to 'output' type parameters will fail.

    Args:
        path:  Full parameter path, e.g. root/Services/MyApp/serviceParameters/userParameters/StartButton
        value: Scalar (int, float, bool, str) or list for array parameters.
               Cast to the parameter's declared type before writing, so "254"
               and 254 both write an integer parameter.
    """
    if ctx:
        ctx.info(f"Writing {value!r} → {path}")
    try:
        req, tree = _conn._get_connection()
    except Exception as e:
        _conn._reset_connection()
        return _conn._connection_error_message(e)

    try:
        coerced = _coerce_value(tree, path, value)
        req.setParameter(path, coerced).get()
    except _ENCODE_ERRORS as e:
        return _write_error(e, path=path, value=value)
    except Exception as e:
        _conn._reset_connection()
        return _conn._connection_error_message(e)
    return {"path": path, "written": coerced, "status": "ok",
            "controller": _conn._get_config()[0]}


@mcp.tool()
def list_parameters(prefix: str = "root", depth: int = _pt.DEFAULT_DEPTH,
                    limit: int = _pt.DEFAULT_LIMIT, contains: str = "",
                    include_private: bool = False,
                    ctx: Context | None = None) -> dict:
    """List one level of the Motorcortex parameter tree under `prefix`.

    Exploring is a walk: name a level, see what is under it, descend. Each entry
    says whether anything lives beneath it, so a branch is one line rather than
    its whole subtree.

    Args:
        prefix: the level to list, e.g. "root", "root/Control", "root/Axis1".
        depth: levels below the prefix; 1 by default, 0 for the whole subtree.
        limit: maximum entries returned; the result reports what was cut.
        contains: search the subtree for paths containing this text, at any
                  depth, instead of listing a level.
        include_private: include runtime plumbing — `:` IPC pipes and `.type`
                  metadata leaves — left out by default. The result says how
                  many were hidden under this prefix.
    """
    if ctx:
        ctx.debug(f"Listing parameters under '{prefix}' (depth={depth}, contains={contains!r})")
    try:
        _, tree = _conn._get_connection()
        paths = [p.path for p in tree.getParameterTree()]
    except Exception as e:
        _conn._reset_connection()
        return _conn._connection_error_message(e)
    return _pt.list_tree(paths, prefix=prefix, depth=depth, limit=limit,
                         contains=contains, include_private=include_private)


def _enum_name(enum, value: int) -> str:
    """A protobuf enum value by name, or its number when this client does not know it."""
    try:
        return enum.Name(value)
    except ValueError:
        return str(value)


def _describe(p) -> dict:
    """The metadata of one ParameterInfo message, as get_parameter_info reports it."""
    info: dict = {
        "path": p.path,
        "param_type": _enum_name(_pb.ParameterType, p.param_type),
        "data_type": _enum_name(_pb.DataType, p.data_type),
        "elements": p.number_of_elements,
        "permissions": format(p.permissions, "o"),
    }
    if p.unit:
        info["unit"] = _enum_name(_pb.Unit, p.unit)
    flags = [name for name, bit in _pb.ParameterFlag.items() if p.flags & bit]
    if flags:
        info["flags"] = flags
    return info


@mcp.tool()
def get_parameter_info(path: str, ctx: Context | None = None) -> dict:
    """Get metadata about a parameter, to check it before reading or writing.

    Returns:
        path:        full parameter path
        param_type:  INPUT, OUTPUT, PARAMETER, PARAMETER_VOLATILE or
                     PARAMETER_PERSISTENT — outputs are computed by the
                     controller and cannot be written
        data_type:   element type (DOUBLE, INT32, BOOL, …)
        elements:    array size; 1 for a scalar
        permissions: access bits in octal, user/group/others, as for files
        unit:        physical unit, when the parameter declares one
        flags:       LINK_IS_ACTIVE (a link drives the value, so a written
                     value is overwritten) and OVERWRITE_IS_ACTIVE (the
                     value is being overridden), when set

    Args:
        path: Full parameter path
    """
    if ctx:
        ctx.debug(f"Getting info for {path}")
    try:
        _, tree = _conn._get_connection()
        for p in tree.getParameterTree():
            if p.path == path:
                return _describe(p)
        return {"error": f"Parameter not found: {path}"}
    except Exception as e:
        _conn._reset_connection()
        return _conn._connection_error_message(e)


@mcp.tool()
def get_parameter_list(paths: list[str], ctx: Context | None = None) -> list[dict] | dict:
    """Read multiple parameter values in a single request.

    More efficient than calling get_parameter() repeatedly.

    Args:
        paths: List of full parameter paths
    """
    if ctx:
        ctx.debug(f"Batch reading {len(paths)} parameters")
    try:
        req, _ = _conn._get_connection()
        result = req.getParameterList(paths).get()
        if result is None:
            return {"error": "No result returned"}
        out = []
        for param in result.params:
            value = list(param.value)
            out.append({
                "path": param.info.path,
                "value": value[0] if len(value) == 1 else value,
            })
        return out
    except Exception as e:
        _conn._reset_connection()
        return _conn._connection_error_message(e)


@mcp.tool()
def set_parameter_list(items: list[dict], ctx: Context | None = None) -> dict:
    """Write values to multiple parameters in a single request.

    More efficient than calling set_parameter() repeatedly.

    Args:
        items: List of {"path": str, "value": any} dicts.
               Optionally include "offset" and "length" for partial array writes.
    """
    if ctx:
        ctx.info(f"Batch writing {len(items)} parameters")
    try:
        import motorcortex
        req, tree = _conn._get_connection()
    except Exception as e:
        _conn._reset_connection()
        return _conn._connection_error_message(e)

    incomplete = [i for i, item in enumerate(items)
                  if "path" not in item or "value" not in item]
    if incomplete:
        return {
            "error": f"items[{incomplete[0]}] is missing 'path' or 'value'",
            "items": items,
        }

    try:
        coerced = [
            {**item, "value": _coerce_value(tree, item["path"], item["value"])}
            for item in items
        ]
    except _ENCODE_ERRORS as e:
        return _write_error(e, items=items)

    try:
        result = req.setParameterList(coerced).get()
    except _ENCODE_ERRORS as e:
        return _write_error(e, items=coerced)
    except Exception as e:
        _conn._reset_connection()
        return _conn._connection_error_message(e)

    if result.status != motorcortex.OK:
        return {"error": f"Set failed with status {result.status}", "items": coerced}
    return {"status": "ok", "written": len(coerced),
            "controller": _conn._get_config()[0]}
