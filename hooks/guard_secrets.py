#!/usr/bin/env python3
"""PreToolUse guard for Read/Edit/Write: blocks access to secret files (exit 2)."""
import json, re, sys

data = json.load(sys.stdin)
path = (data.get("tool_input") or {}).get("file_path", "") or ""

ALLOW = re.compile(r"\.env\.(example|sample|template)$", re.IGNORECASE)
DENY = re.compile(r"(\.env(\..+)?$|(^|/)id_rsa[^/]*$|(^|/)id_ed25519[^/]*$|\.pem$|\.key$|(^|/)(credentials?|secrets?)\.(json|ya?ml|toml)$)", re.IGNORECASE)

if path and DENY.search(path) and not ALLOW.search(path):
    print(f"BLOCKED by policy hook: '{path}' looks like a secret file. Ask the user to handle it.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
