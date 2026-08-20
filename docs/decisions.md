# Decisions

- 2026-08-20: Renamed `ai-software-team` to `software-team` and rebuilt it as a real subagent-orchestrator plugin (was a single-conversation role-play skill with no subagent spawning) — user wanted actual delegation, mirroring the `agent-office` plugin architecture, per fable-advisor consult.
- 2026-08-20: Keep `agent-office` published alongside `software-team` rather than deprecating it — user's explicit choice; the two skill descriptions must stay differentiated (software-team's is the always-delegate, zero-self-edit variant with a dedicated reviewer) to avoid trigger collision.
- 2026-08-20: Orchestrator spawns `software-team:builder` on every task that touches a project file, T0 included, rather than doing trivial edits inline — user's explicit choice, confirmed over the agent-office default of handling T0 in-context.
- 2026-08-20: Ported team-agent-workflow's guard_bash/guard_secrets/log_agent/pre_compact hooks as first-class plugin hooks (`hooks/hooks.json`); skipped guard_tier.py (path-heuristic T2 detection judged too noisy) and the project-vendored ground-truth doc templates (docs/product.md etc. — project-specific, not plugin material).
