#!/usr/bin/env python3
"""Subagent-spawn logger: appends real workflow state to .gemini/state/agent-log.jsonl.

Ported from the Claude Code version (SubagentStart/SubagentStop there). Gemini CLI has no
SubagentStart/SubagentStop event; its docs describe subagents as "exposed to the main
agent as a tool of the same name" (geminicli.com/docs/core/subagents/), so this fires on
BeforeTool/AfterTool matched against the 9 role names instead of the main-turn
BeforeAgent/AfterAgent events (which fire once per user turn, not per subagent spawn, per
geminicli.com/docs/hooks/reference/ -- confirmed wrong for this purpose and dropped).
Whether BeforeTool/AfterTool actually fire around a subagent-as-tool call the same way
they do for a built-in tool is not spelled out in the docs either -- unverified by live
testing. The event/agent-name field lookups below are defensive for the same reason.
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
    "agent": find_first(data, ["tool_name", "toolName", "agent_type", "agentType", "agentName", "agent_name", "agent", "subagent"]) or "unknown",
    "session": (find_first(data, ["session_id", "sessionId"]) or "")[:8],
}
state_dir = os.path.join(os.environ.get("GEMINI_PROJECT_DIR", "."), ".gemini", "state")
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
