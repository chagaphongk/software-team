#!/usr/bin/env python3
"""PreToolUse guard for file read/write/edit/apply_patch: blocks access to secret files (exit 2).

Ported from the Claude Code version. Codex's apply_patch tool may carry the target path
under a different field than a plain Read/Edit/Write call -- see hooks/PORT_NOTES.md.
This checks every plausible field name/nesting defensively, and falls back to scanning
apply_patch's raw patch-body string for its own file-header format when no structured
path field is present.
"""
import json, re, sys

data = json.load(sys.stdin)


def find_path(d):
    if not isinstance(d, dict):
        return ""
    for container_key in ("tool_input", "toolInput", "args", "input", "parameters"):
        container = d.get(container_key)
        if isinstance(container, dict):
            for path_key in ("file_path", "filePath", "path", "target_path"):
                if isinstance(container.get(path_key), str):
                    return container[path_key]
    for path_key in ("file_path", "filePath", "path", "target_path"):
        if isinstance(d.get(path_key), str):
            return d[path_key]
    return ""


# Known ceiling: assumes apply_patch's real grammar uses this exact header casing/spacing;
# a more lenient real parser could evade this fallback scan (best-effort, not the primary check).
APPLY_PATCH_FILE_HEADER = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+?)\s*$", re.MULTILINE)
APPLY_PATCH_MOVE_HEADER = re.compile(r"^\*\*\* Move to: (.+?)\s*$", re.MULTILINE)


def find_patch_paths(d):
    paths = []

    def walk(v):
        if isinstance(v, str):
            paths.extend(APPLY_PATCH_FILE_HEADER.findall(v))
            paths.extend(APPLY_PATCH_MOVE_HEADER.findall(v))
        elif isinstance(v, dict):
            for vv in v.values():
                walk(vv)
        elif isinstance(v, list):
            for vv in v:
                walk(vv)

    walk(d)
    return paths


path = find_path(data)
paths = ([path] if path else []) + find_patch_paths(data)

ALLOW = re.compile(r"\.env\.(example|sample|template)$", re.IGNORECASE)
DENY = re.compile(r"(\.env(\..+)?$|(^|/)\.envrc$|(^|/)id_(rsa|dsa|ecdsa|ed25519)[^/]*$|\.pem$|\.key$|(^|/)(credentials?|secrets?)\.(json|ya?ml|toml)$)", re.IGNORECASE)

for p in paths:
    normalized = p.replace("\\", "/")
    if DENY.search(normalized) and not ALLOW.search(normalized):
        print(f"BLOCKED by policy hook: '{p}' looks like a secret file. Ask the user to handle it.", file=sys.stderr)
        sys.exit(2)
sys.exit(0)
