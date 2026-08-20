#!/usr/bin/env python3
"""PreToolUse guard for Bash: blocks destructive/irreversible commands (exit 2)."""
import json, re, sys

data = json.load(sys.stdin)
cmd = (data.get("tool_input") or {}).get("command", "") or ""

BLOCK = [
    (r"git\s+push\s+[^\n]*(--force|-f)\b", "Force push is blocked. Ask the user to run it themselves if truly needed."),
    (r"rm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)\s+(/|~|\$HOME)(\s|$)", "Recursive delete of / or home is blocked."),
    (r"git\s+reset\s+--hard\s+", "git reset --hard is blocked; use it only via explicit user approval."),
    (r"\bdrop\s+(database|table)\b", "DROP DATABASE/TABLE is blocked from automated execution."),
    (r"git\s+clean\s+-[a-zA-Z]*f", "git clean -f is blocked (deletes untracked files irreversibly)."),
    (r"\b(cat|less|more|head|tail|grep|awk|sed|cp|scp|base64|xxd|strings)\b[^\n|;&]*\.env\b(?!\.(example|sample|template)\b)",
     "Reading .env files via shell is blocked. Ask the user to handle secrets."),
    (r"\b(cat|less|more|head|tail|grep|cp|scp|base64|xxd|strings)\b[^\n|;&]*(id_rsa|id_ed25519|\.pem\b|\.key\b)",
     "Reading key/credential files via shell is blocked."),
]

for pattern, reason in BLOCK:
    if re.search(pattern, cmd, re.IGNORECASE):
        print(f"BLOCKED by policy hook: {reason}", file=sys.stderr)
        sys.exit(2)
sys.exit(0)
