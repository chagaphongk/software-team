---
description: Show current workflow status (tier, state, pending gates) from the hook-written agent log
allowed-tools: Bash(tail:*), Bash(cat:*), Bash(uniq:*)
---

## Recent agent activity (ground truth from hooks — not conversation memory)
!`{ tail -n 20 .claude/state/agent-log.jsonl 2>/dev/null || echo "no agent activity logged yet"; } | uniq | tail -n 10`

## Recent decisions (ground truth from docs/decisions.md)
!`tail -n 5 docs/decisions.md 2>/dev/null || echo "no decisions logged yet"`

Using the log above plus conversation context, report status as a compact table:

| Field | Value |
|---|---|
| Task | one-line description, or "idle" |
| Risk tier | T0 / T1 / T2, with the one-line reason |
| State | current step in RESEARCH → PLAN → BUILD → REVIEW → VERIFY → DONE |
| Last agent activity | from the log above |
| Review verdict | not started / pending / APPROVED / CHANGES REQUIRED |
| Verification | not started / pending / PASS / FAIL / BLOCKED |
| Next step | one line |

The log is ground truth: if it conflicts with conversation memory, trust the log — that is
the entire reason `log_agent.py` exists. If a `PreCompact` event appears above, note that
context was compacted and re-read `docs/decisions.md` before continuing work. If the log
file is missing entirely, say the hooks are not installed or not firing rather than
presenting a memory-only report with the same confidence as a verified one. Keep the
answer under 14 lines.
