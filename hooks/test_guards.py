#!/usr/bin/env python3
"""Self-check for guard_secrets.py / guard_bash.py. Stdlib-only, assert-based, no framework."""
import sys

# A regex/command blocklist can never be fully complete: interpreter one-liners
# (e.g. `python -c "..."`) are a known bypass class this doesn't close, only narrows.

from guard_secrets import is_secret_path
from guard_bash import blocked_reason

CASES = [
    ("forward-slash secret path", "foo/credentials.json", True),
    ("windows backslash secret path", "foo\\credentials.json", True),
    (".envrc path", "foo/.envrc", True),
    ("benign unrelated file path", "foo/notes.txt", False),
    ("benign bash command", "ls", False),
    ("dangerous command against sensitive path", "cat ~/.ssh/id_rsa", True),
    ("type-check flag not a Get-Content alias", "npm run type-check -- --env .env.local", False),
]

if __name__ == "__main__":
    passed = 0
    failed = 0
    for desc, value, expected_blocked in CASES:
        if desc in ("benign bash command", "dangerous command against sensitive path", "type-check flag not a Get-Content alias"):
            actual_blocked = blocked_reason(value) is not None
        else:
            actual_blocked = is_secret_path(value)
        try:
            assert actual_blocked == expected_blocked, (
                f"{desc}: expected blocked={expected_blocked}, got {actual_blocked}"
            )
            print(f"PASS: {desc}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {e}")
            failed += 1

    print(f"\n{passed} PASS, {failed} FAIL")
    sys.exit(1 if failed else 0)
