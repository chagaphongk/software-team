#!/usr/bin/env python3
"""PreToolUse guard for Read/Edit/Write: blocks access to secret files (exit 2)."""
import json, re, sys

ALLOW = re.compile(r"\.env\.(example|sample|template)$", re.IGNORECASE)
DENY = re.compile(r"(\.env(\..+)?$|(^|/)\.envrc$|(^|/)id_(rsa|dsa|ecdsa|ed25519)[^/]*$|\.pem$|\.key$|(^|/)(credentials?|secrets?)\.(json|ya?ml|toml)$)", re.IGNORECASE)


def is_secret_path(path):
    path = (path or "").replace("\\", "/")
    return bool(path and DENY.search(path) and not ALLOW.search(path))


if __name__ == "__main__":
    data = json.load(sys.stdin)
    path = (data.get("tool_input") or {}).get("file_path", "") or ""
    if is_secret_path(path):
        print(f"BLOCKED by policy hook: '{path}' looks like a secret file. Ask the user to handle it.", file=sys.stderr)
        sys.exit(2)
    sys.exit(0)
