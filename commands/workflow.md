---
description: Show current workflow status (tier, state, pending gates) from the hook-written agent log
allowed-tools: Bash(tail:*), Bash(cat:*), Bash(uniq:*)
---

## Hook-grounded: recent agent activity (from `.claude/state/agent-log.jsonl`, written by hooks/log_agent.py)
!`tail -n 20 .claude/state/agent-log.jsonl 2>/dev/null | uniq | tail -n 10`

## Recent decisions (from docs/decisions.md)
!`tail -n 5 docs/decisions.md 2>/dev/null`

Using the log above plus conversation context, report status as a compact table, with a
Source column marking each row hook-grounded or conversation-derived:

| Field | Value | Source |
|---|---|---|
| Task | one-line description, or "idle" | conversation-derived |
| Risk tier | T0 / T1 / T2, with the one-line reason | conversation-derived |
| State | current step in RESEARCH → PLAN → BUILD → REVIEW → VERIFY → DONE | conversation-derived |
| Last agent activity | from the hook-grounded log above | hook-grounded |
| Review verdict | not started / pending / APPROVED / CHANGES REQUIRED | conversation-derived |
| Verification | not started / pending / PASS / FAIL / BLOCKED | conversation-derived |
| Next step | one line | conversation-derived |

Only "Last agent activity" (and a `PreCompact` marker, if present) is hook-grounded — read
directly from hooks/log_agent.py's output with no interpretation. Every other row is
conversation-derived: drawn from this conversation's context, not verified against a log.
For "Last agent activity", if the log conflicts with conversation memory, trust the log —
that is the entire reason `log_agent.py` exists. If a `PreCompact` event appears in the
hook-grounded log above, note that context was compacted and re-read `docs/decisions.md`
before continuing work. If the log file is missing entirely, say the hooks are not
installed or not firing rather than presenting a memory-only report with the same
confidence as a verified one. Keep the answer under 14 lines.
