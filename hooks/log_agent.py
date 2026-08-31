#!/usr/bin/env python3
"""SubagentStart logger: appends real workflow state to .claude/state/agent-log.jsonl.
Records that a subagent spawn occurred; does not prove the orchestrator made no direct
edits (hook payloads carry no caller identity). SubagentStop is not hooked — its
payload carries no agent identity, so stop entries added only noise."""
import json, os, sys, datetime

data = json.load(sys.stdin)
entry = {
    "ts": datetime.datetime.now().isoformat(timespec="seconds"),
    "event": data.get("hook_event_name", "unknown"),
    "agent": data.get("agent_type", "unknown"),
    "session": (data.get("session_id") or "")[:8],
}
state_dir = os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", "."), ".claude", "state")
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
