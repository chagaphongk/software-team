#!/usr/bin/env python3
"""SubagentStart/SubagentStop logger: appends real workflow state to
.software-team/state/agent-log.jsonl. Proof the always-delegate invariant is honored --
the log shows real collaboration.spawn_agent calls, not role-play.

Ported from the Claude Code version. Field names inside the hook payload were not
confirmed by live testing on Codex -- see hooks/PORT_NOTES.md -- so this looks up
several plausible key names defensively rather than assuming Claude's shape.
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
    "event": find_first(data, ["hook_event_name", "hookEventName", "event", "eventName"]) or "unknown",
    "agent": find_first(data, ["agent_type", "agentType", "agentName", "agent_name", "agent", "subagent"]) or "unknown",
    "session": (find_first(data, ["session_id", "sessionId"]) or "")[:8],
}
project_dir = os.environ.get("CODEX_PROJECT_DIR") or os.environ.get("CLAUDE_PROJECT_DIR") or "."
state_dir = os.path.join(project_dir, ".software-team", "state")
os.makedirs(state_dir, exist_ok=True)
log_path = os.path.join(state_dir, "agent-log.jsonl")
with open(log_path, "a") as f:
    f.write(json.dumps(entry) + "\n")
try:
    with open(log_path) as f:
        lines = f.readlines()
    if len(lines) > 500:
        with open(log_path, "w") as f:
            f.writelines(lines[-100:])
except OSError:
    pass
sys.exit(0)
