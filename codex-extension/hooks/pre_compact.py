#!/usr/bin/env python3
"""PreCompact marker: logs compaction events to .software-team/state/agent-log.jsonl.
Zero-token by design -- a script, not a model call. The next context window sees the
marker and knows to re-read docs/decisions.md instead of trusting compacted memory.

Ported from the Claude Code version. Whether Codex fires a PreCompact-equivalent event
at all was not confirmed by live testing -- see hooks/PORT_NOTES.md.
"""
import json, os, sys, datetime

data = json.load(sys.stdin)


def find_first(d, keys):
    if not isinstance(d, dict):
        return None
    for k in keys:
        v = d.get(k)
        if isinstance(v, str) and v:
            return v
    return None


entry = {
    "ts": datetime.datetime.now().isoformat(timespec="seconds"),
    "event": "PreCompact",
    "trigger": find_first(data, ["trigger", "reason"]) or "unknown",
    "session": (find_first(data, ["session_id", "sessionId"]) or "")[:8],
}
project_dir = os.environ.get("CODEX_PROJECT_DIR") or os.environ.get("CLAUDE_PROJECT_DIR") or "."
state_dir = os.path.join(project_dir, ".software-team", "state")
os.makedirs(state_dir, exist_ok=True)
with open(os.path.join(state_dir, "agent-log.jsonl"), "a") as f:
    f.write(json.dumps(entry) + "\n")
sys.exit(0)
