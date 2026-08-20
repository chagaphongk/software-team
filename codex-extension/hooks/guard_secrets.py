#!/usr/bin/env python3
"""PreToolUse guard for file read/write/edit/apply_patch: blocks access to secret files (exit 2).

Ported from the Claude Code version. Codex's apply_patch tool may carry the target path
under a different field than a plain Read/Edit/Write call -- see hooks/PORT_NOTES.md.
This checks every plausible field name/nesting defensively.
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


path = find_path(data)

ALLOW = re.compile(r"\.env\.(example|sample|template)$", re.IGNORECASE)
DENY = re.compile(r"(\.env(\..+)?$|(^|/)id_rsa[^/]*$|(^|/)id_ed25519[^/]*$|\.pem$|\.key$|(^|/)(credentials?|secrets?)\.(json|ya?ml|toml)$)", re.IGNORECASE)

if path and DENY.search(path) and not ALLOW.search(path):
    print(f"BLOCKED by policy hook: '{path}' looks like a secret file. Ask the user to handle it.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
