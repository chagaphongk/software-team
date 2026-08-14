# ai-software-team

A Claude Code skill that runs a task as a five-role "team" — Researcher, Architect,
Developer, Reviewer, Verifier — inside a single conversation. One Claude instance
switches hats, with human approval gates between planning and building, instead of
answering in one unchecked pass. No subagents are spawned; it works anywhere Claude Code
runs, with or without Task-tool access.

## Why

Answering a non-trivial task in one pass tends to skip two things: a plan the human
signs off on before code gets written, and an independent check that the result actually
does what was asked. This skill forces both, at the cost of an extra turn.

## When to use this vs. a real subagent-orchestration skill

If your setup also has a skill that dispatches *real* subagents (risk-tier
classification, parallel researcher/builder/verifier delegation, tiered model routing —
e.g. [agent-office](https://github.com/chagaphongk/agent-office)), prefer that one for
multi-file builds, large migrations, or anything that benefits from real parallel
delegation.

Reach for `ai-software-team` instead when:
- You want the audit trail and gate discipline of a single inspectable turn.
- No subagent/Task-tool access is available in this environment.
- It's a quick review/critique or a non-code deliverable (design doc, data analysis,
  spec) that benefits from a plan-then-review pass without the overhead of real
  delegation.

## What it does

- **Five roles, one conversation** — Researcher gathers facts (skippable when context is
  already complete), Architect plans with explicit per-task acceptance criteria,
  Developer builds, Reviewer inspects against a 5-category checklist
  (correctness/security/performance/impact/plan-conformance), Verifier actually runs the
  result rather than trusting the report.
- **Three approval gates** — GATE 1 (plan approval, before any code is written), GATE 2
  (escalation to the user if 3 rounds of review/fix don't converge), GATE 3 (delivery
  summary + final confirmation with a traceability line per requirement).
- **Read-only deliverables skip GATE 1** — a code review, security audit, or design
  critique has nothing to build, so there's no action for the gate to protect; the
  Reviewer's findings are the deliverable, produced directly in turn one.
- **Anti-rubber-stamp rules** — a bare `APPROVED` is invalid; every checklist category
  needs a one-line evidence statement, findings or not. Verification needs a negative
  test, not just happy-path checks, and an honest `NOT VERIFIABLE HERE` when execution
  isn't possible beats a fabricated "it works."
- **Optional subagent hand-off** — if a spawn tool is available, the Reviewer/Verifier
  pass may delegate to a fresh-context subagent given the same acceptance criteria, to
  avoid the same context reviewing its own blind spots. Not required — this is a
  strengthening, not a dependency.

## Install

```
git clone https://github.com/chagaphongk/ai-software-team.git
bash ai-software-team/scripts/install.sh              # -> ~/.claude/skills/ai-software-team
bash ai-software-team/scripts/install.sh --project     # -> ./.claude/skills/ai-software-team (this repo only)
```

Or skip the script — copy `SKILL.md` (and `evals/` if you want the benchmark) into your
skills directory by hand. That's the whole install either way: no plugin manifest, no
dependencies. Re-run the script to update an existing install after a `git pull`.

## Benchmark

Evaluated with-skill vs a no-skill baseline on 3 evals (build a function + tests, design
a REST API with a double-booking constraint, security-review an existing rate limiter),
graded on 5 hand-written assertions each. Full run history and reasoning in
`evals/evals.json` and the iteration workspace.

| Eval | With skill | Baseline |
|---|---|---|
| build-feature | 3/5 (60%) | 1/5 (20%) |
| design-api | 4-5/5 (80-100%, run variance) | 2/5 (40%) |
| code-review | 5/5 (100%) | 2/5 (40%) |
| **Aggregate** | **~80%** | **~33%** |

Two real bugs were found and fixed this way, not by inspection:

1. **GATE 1 was blocking read-only reviews.** The first version forced a plan-approval
   gate even for "review this code" requests, so it delivered zero review content in
   turn one — the no-skill baseline beat it outright on that eval. Fixed by adding the
   read-only-deliverable exception above; re-test went from 1/5 to 4/5 with no regression
   on the other two evals.
2. **Reviewer findings didn't map back to the stated checklist.** Findings were ordered
   by severity but never tagged by category, so the anti-rubber-stamp rule ("every
   category needs evidence") was unenforceable in practice. Fixed by adding an explicit
   output-shape example (severity-ordered findings tagged `[Category]`, closed by a
   per-category evidence block); re-test went 4/5 → 5/5.

A side effect of the second fix: the with-skill code-review run started writing and
executing real proof-of-concept code to back its findings instead of reasoning
statically, and caught a bug (a non-decaying lockout counter enabling a permanent
denial-of-service against any known username) that neither the original run nor the
baseline found.

## Related

[agent-office](https://github.com/chagaphongk/agent-office) — the real-subagent
orchestration counterpart to this skill. Several rules here (the read-only-deliverable
gate skip, the negative-test requirement, the 3-round escalation, the traceability
summary) were upstreamed there after this benchmark surfaced them.
