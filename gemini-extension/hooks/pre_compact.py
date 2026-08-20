#!/usr/bin/env python3
"""PreCompress marker: logs compaction events to .gemini/state/agent-log.jsonl.
Zero-token by design -- a script, not a model call. The next context window (and
/workflow) sees the marker and knows to re-read ground truth (docs/decisions.md) instead
of trusting compacted memory. Ported from the Claude Code PreCompact version; Gemini
CLI's hooks docs name this event PreCompress."""
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
    "event": "PreCompress",
    "trigger": find_first(data, ["trigger"]) or "unknown",
    "session": (find_first(data, ["session_id", "sessionId"]) or "")[:8],
}
state_dir = os.path.join(os.environ.get("GEMINI_PROJECT_DIR", "."), ".gemini", "state")
os.makedirs(state_dir, exist_ok=True)
with open(os.path.join(state_dir, "agent-log.jsonl"), "a") as f:
    f.write(json.dumps(entry) + "\n")
sys.exit(0)
