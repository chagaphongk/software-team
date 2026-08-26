#!/usr/bin/env python3
"""BeforeTool guard for read_file/replace/write_file: blocks access to secret files (exit 2).

Ported from the Claude Code version. Same caveat as guard_bash.py: the exact JSON field
name for the target path was not confirmed by live testing, so this checks every
plausible field name/nesting instead of assuming one.
"""
import json, re, sys

data = json.load(sys.stdin)


def find_path(d):
    if not isinstance(d, dict):
        return ""
    for container_key in ("tool_input", "toolInput", "args", "input", "parameters"):
        container = d.get(container_key)
        if isinstance(container, dict):
            for path_key in ("file_path", "filePath", "path", "target", "file"):
                if isinstance(container.get(path_key), str):
                    return container[path_key]
    for path_key in ("file_path", "filePath", "path", "target", "file"):
        if isinstance(d.get(path_key), str):
            return d[path_key]
    return ""


path = find_path(data).replace("\\", "/")

ALLOW = re.compile(r"\.env\.(example|sample|template)$", re.IGNORECASE)
DENY = re.compile(r"(\.env(\..+)?$|(^|/)\.envrc$|(^|/)id_rsa[^/]*$|(^|/)id_ed25519[^/]*$|\.pem$|\.key$|(^|/)(credentials?|secrets?)\.(json|ya?ml|toml)$)", re.IGNORECASE)

if path and DENY.search(path) and not ALLOW.search(path):
    print(f"BLOCKED by policy hook: '{path}' looks like a secret file. Ask the user to handle it.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
