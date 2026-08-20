#!/usr/bin/env python3
"""PreCompact marker: logs compaction events to .claude/state/agent-log.jsonl.
Zero-token by design — a script, not a model call. The next context window (and
/software-team:workflow) sees the marker and knows to re-read docs/decisions.md instead
of trusting compacted memory."""
import json, os, sys, datetime

data = json.load(sys.stdin)
entry = {
    "ts": datetime.datetime.now().isoformat(timespec="seconds"),
    "event": "PreCompact",
    "trigger": data.get("trigger", "unknown"),
    "session": (data.get("session_id") or "")[:8],
}
state_dir = os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", "."), ".claude", "state")
os.makedirs(state_dir, exist_ok=True)
with open(os.path.join(state_dir, "agent-log.jsonl"), "a") as f:
    f.write(json.dumps(entry) + "\n")
sys.exit(0)
