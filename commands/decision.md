---
description: Record a course-changing decision as one line in docs/decisions.md
---

Append a decision line to `docs/decisions.md` (create the file with a `# Decisions`
heading on first use).

This direct append is not a silent exception to the orchestrator's zero-self-edit rule:
SKILL.md's invariant definition explicitly carves out docs/decisions.md decision-log
entries (along with `.claude/state/*`) as "office state" the orchestrator may edit
directly, without spawning a builder.

Input: $ARGUMENTS — the decision, optionally with its reason.

Format exactly one line:

```
- YYYY-MM-DD: <decision> — <why>
```

Use today's date. If the reason is missing from the input, derive it from the recent
conversation; if it is genuinely unclear, ask — a decision line without a "why" fails its
one purpose, which is stopping a future session from re-litigating the choice.

Only course-changing decisions belong here: architecture choices, scope cuts, tier
escalations, human approvals or rejections. If the input describes a routine step (a file
edited, a test fixed), say it does not belong in the log and do not append it.

After appending, show the last 5 lines of the file.
