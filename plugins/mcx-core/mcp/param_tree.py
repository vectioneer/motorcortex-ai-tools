"""Turning a flat parameter-path list into a listing that fits in a session.

`tree.getParameterTree()` hands back every path on the controller as one flat
list. A machine application's tree runs to thousands of them, so returning the
lot — which is what `list_parameters(prefix="root")` used to do — costs more
context than any answer it could support. Exploration is a walk: name a level,
see what is under it, descend.

So the listing is one level deep by default, every entry says whether anything
lives beneath it, and the result states what was left out rather than silently
cutting. `contains` switches to a search across the subtree, for the case where
the user knows a name but not where it sits.

Stdlib only.
"""

# A listing bigger than this is a context problem, not an answer.
DEFAULT_LIMIT = 200
DEFAULT_DEPTH = 1


def is_private(path: str) -> bool:
    """Is any segment of this path runtime plumbing rather than a parameter?

    Two kinds. `root/Logic/:stateToBus/...` is an IPC pipe — the runtime's own
    wiring. `root/Control/.type` is a metadata leaf naming the branch's module
    class (`MainControlLoop`), and one hangs under nearly every branch.

    Both are numerous, neither is what a user means by "what parameters are
    there", and filtering them here rather than after the fact keeps them out
    of the transcript entirely. Measured on a live controller
    (2026-09-04): 839 of ~13,900 paths.
    """
    return any(seg.startswith((":", ".")) for seg in path.split("/"))


def relative_depth(path: str, prefix: str) -> int | None:
    """How many levels `path` sits below `prefix`, or None if it is outside.

    The prefix itself is depth 0. Matching is on path segments, so the prefix
    `root/Axis1` never matches `root/Axis10`.
    """
    if path == prefix:
        return 0
    if not prefix:
        return path.count("/") + 1
    if not path.startswith(prefix + "/"):
        return None
    return path[len(prefix) + 1:].count("/") + 1


def _ancestor_at(path: str, prefix: str, depth: int) -> str:
    """The ancestor of `path` that is exactly `depth` levels under `prefix`."""
    rest = path[len(prefix) + 1:] if prefix else path
    return (prefix + "/" if prefix else "") + "/".join(rest.split("/")[:depth])


def deepest_existing_prefix(paths, prefix: str) -> str:
    """The longest ancestor of `prefix` that something in the tree lives under.

    Used to answer a miss with a usable suggestion instead of an empty list —
    a mistyped level is the common case, and the tree cannot be re-read cheaply.
    """
    candidate = prefix
    while candidate:
        if any(relative_depth(p, candidate) is not None for p in paths):
            return candidate
        if "/" not in candidate:
            return ""
        candidate = candidate.rsplit("/", 1)[0]
    return ""


def list_tree(paths, prefix: str = "root", depth: int = DEFAULT_DEPTH,
              limit: int = DEFAULT_LIMIT, contains: str = "",
              include_private: bool = False) -> dict:
    """One level of the tree (or a subtree search), capped and self-describing.

    `depth` counts levels below `prefix`; `depth=0` means no limit, for the
    caller that really does want a subtree flattened. `contains` searches every
    descendant regardless of depth, case-insensitively. Runtime plumbing — `:`
    pipes and `.` metadata leaves — is left out unless asked for, and the count
    that is reported covers the prefix being listed, not the whole tree.
    """
    prefix = (prefix or "").rstrip("/")
    limit = max(int(limit), 1)
    needle = contains.lower().strip()

    # Plumbing is filtered out of the *entries*, never out of the structure.
    # Removing it from the paths themselves erased any branch whose only child
    # was metadata — a configured but empty communication branch is exactly
    # that, and worth seeing.
    visible = paths if include_private else [p for p in paths if not is_private(p)]
    hidden = 0 if include_private else sum(
        1 for p in paths if is_private(p) and relative_depth(p, prefix) is not None)

    inside = [(p, relative_depth(p, prefix)) for p in paths]
    inside = [(p, d) for p, d in inside if d is not None and d > 0]

    def entry(path: str) -> dict:
        below = _descendant_count(path, visible)
        return {"path": path, "kind": "leaf" if below == 0 else "branch",
                **({"descendants": below} if below else {})}

    if needle:
        matched = [p for p, _ in inside
                   if needle in p.lower() and (include_private or not is_private(p))]
        entries = [entry(p) for p in sorted(matched)]
        mode = f"search for {contains!r} under {prefix}"
    else:
        cut = depth if depth and depth > 0 else max((d for _, d in inside), default=1)
        # Collapse everything deeper than the cut into the ancestor that sits
        # exactly at it, so a branch appears once with a count, not N times.
        seen = {path if level <= cut else _ancestor_at(path, prefix, cut)
                for path, level in inside}
        entries = [entry(p) for p in sorted(seen)
                   if include_private or not is_private(p)]
        mode = f"level {cut} under {prefix}"

    total = len(entries)
    shown = entries[:limit]
    out = {
        "prefix": prefix,
        "mode": mode,
        "entries": shown,
        "returned": len(shown),
        "total": total,
        "truncated": total > limit,
    }
    if hidden:
        out["private_hidden"] = hidden
    if out["truncated"]:
        out["note"] = (f"{total - limit} more not shown — narrow with a longer prefix "
                       f"or `contains`, or raise `limit` if the whole level is needed")
    if total == 0 and needle:
        out["note"] = (f"no path under {prefix!r} contains {contains!r} — the prefix "
                       "itself is fine, so widen the term or search from a shorter "
                       "prefix")
    elif total == 0:
        anchor = deepest_existing_prefix(visible, prefix)
        out["note"] = (f"nothing under {prefix!r}"
                       + (f" — the deepest prefix that exists is {anchor!r}" if anchor
                          else " — and no ancestor of it exists either"))
        if anchor and anchor != prefix:
            out["suggestions"] = [e["path"] for e in
                                  list_tree(visible, anchor, 1, 20)["entries"]]
    return out


def _descendant_count(path: str, paths) -> int:
    return sum(1 for p in paths if p != path and p.startswith(path + "/"))


def _is_leaf(path: str, paths) -> bool:
    return _descendant_count(path, paths) == 0
