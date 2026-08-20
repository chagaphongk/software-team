# software-team

A Claude Code plugin that runs a task through a real engineering office — an
orchestrator that classifies risk and delegates, plus spawned `researcher` / `builder` /
`reviewer` / `security-reviewer` / `documenter` / `verifier` / `deployer` / `designer`
subagents — instead of one Claude instance role-playing hats in a single conversation.
The orchestrator never edits a project file itself, at any tier: even a one-character fix
goes through a spawned builder, so the guard hooks and the agent log can prove delegation
happened rather than trusting a transcript. The same invariant covers shipping: deploy,
publish, and push always run through `software-team:deployer`, never the orchestrator.
Independent spawns run in parallel batches by default — three unrelated builders, or a
reviewer alongside a security-reviewer on the same finished diff — never one at a time
just because that's the simpler control flow.

## Why this exists next to `agent-office`

[agent-office](https://github.com/chagaphongk/agent-office) already does real subagent
delegation with risk-tier routing. `software-team` is its stricter sibling, not a
replacement — both stay published. Reach for `software-team` specifically when you want:

- **Zero self-edit, every tier.** agent-office lets the orchestrator handle T0 (typos,
  trivial single-file changes) inline. `software-team` spawns a builder even for that —
  the always-delegate invariant is the point.
- **A dedicated reviewer.** agent-office folds review into VERIFY. `software-team` runs a
  separate `reviewer` subagent against a 5-category checklist (correctness, security,
  performance, impact, plan conformance) before the verifier executes anything.
- **Hooks installed by default.** Destructive-command blocking, secret-file blocking, and
  subagent-spawn logging ship as first-class plugin hooks (`hooks/hooks.json`), not an
  opt-in `examples/` folder you wire up yourself.

Reach for `agent-office` instead when you want the leaner default — trivial work handled
inline, no reviewer round trip.

## What it does

- **RESEARCH → PLAN → BUILD → REVIEW → VERIFY** — real subagents at every step past
  RESEARCH, spawned by name (`software-team:builder`, not a bare `builder`).
- **Risk-tier routing (T0/T1/T2)** — T0 still spawns a builder (fast model, orchestrator
  verifies by diff); T1 always gets an independent verifier; T2 requires human plan
  approval, opus-tier subagents, and a mandatory reviewer plus security-reviewer.
- **Read-only deliverables skip the plan gate** — a code review or audit spawns
  `software-team:reviewer` (or `software-team:security-reviewer` for a security-focused
  ask) directly; its findings are the deliverable.
- **Full-office roster, not just build/verify** — `security-reviewer` runs a dedicated
  OWASP-class pass before DONE on T2 security-sensitive work; `documenter` updates
  README/CHANGELOG/docstrings after a `PASS`, tracing every line to the diff; `deployer`
  is the only agent allowed to run a deploy/publish/push, and only with the human's
  quoted approval in its prompt — the orchestrator itself never runs one; `designer`
  produces a UI/UX spec before BUILD for a new screen (DESIGN mode) and audits any diff
  that changes rendered output for hierarchy/accessibility/consistency before DONE
  (REVIEW mode) — a distinct lens from the standard reviewer's correctness/security/
  performance/impact/plan-conformance checklist.
- **Parallel by default when scopes are disjoint** — multiple independent builders, or a
  reviewer/security-reviewer/designer all reading the same finished diff, spawn in one
  batch instead of one at a time. Complexity within a tier (many interacting files,
  concurrency, an ambiguous judgment call, a second attempt after a failed round) can
  escalate a spawn's model up from its tier's floor — the tier is a floor, not a fixed
  assignment.
- **Deterministic guard hooks** — `hooks/guard_bash.py` blocks force-push, `git reset
  --hard`, `git clean -f`, and destructive shell reads of secrets; `hooks/guard_secrets.py`
  blocks Read/Edit/Write of `.env*`, key files, and `credentials.*`; `hooks/log_agent.py`
  writes every subagent start/stop to `.claude/state/agent-log.jsonl`; `hooks/pre_compact.py`
  marks context-compaction events so `/software-team:workflow` knows to re-read
  `docs/decisions.md` instead of trusting compacted memory.
- **`/software-team:workflow`** — reports tier/state/verdicts from the hook-written log,
  not conversation memory. **`/software-team:decision`** — appends a one-line,
  course-changing decision to `docs/decisions.md`.

## Install

Requires `python3` on `PATH` (the hooks use it).

```
/plugin marketplace add chagaphongk/software-team
/plugin install software-team@software-team-marketplace
```

For local development, point the marketplace at a clone instead:

```
/plugin marketplace add /path/to/software-team
/plugin install software-team@software-team-marketplace
```

If you previously copy-installed the old single-conversation `ai-software-team` skill
(`~/.claude/skills/ai-software-team` or `./.claude/skills/ai-software-team`), remove that
directory — otherwise both the old and new skill are live and can trigger-collide.

Update with `claude plugin update software-team`. Recommended: add the same
`permissions.deny` block agent-office documents for `.env*` / `*.pem` / `*.key` /
`id_rsa*` files in your own `settings.json` — the plugin's hooks are the second guard
layer, not a substitute for the harness-level deny rule.

## Benchmark

The old single-conversation skill was evaluated with-skill vs. no-skill baseline on 3
evals (aggregate ~80% vs ~33%) — see `docs/decisions.md` and git history for that run.
This version's evals (`skills/software-team/evals/evals.json`) were adapted to check for
actual subagent delegation instead of in-transcript role-play text; a fresh baseline run
against this architecture is pending.

## Related

[agent-office](https://github.com/chagaphongk/agent-office) — the leaner sibling; T0
handled inline, no dedicated reviewer.
