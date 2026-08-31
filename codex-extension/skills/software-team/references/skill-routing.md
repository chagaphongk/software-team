# Skill Routing — matching the stack to the right expertise

Read this before PLAN or BUILD when the work targets a specific framework, language, or
platform. The office's job is to get the work verified; this file is about getting it
written to the conventions the stack actually uses, instead of generic-looking code that
passes tests and reads as foreign to the codebase.

This file states the rule only — the mapping of "this stack → that skill" is not
hardcoded here on purpose. A project's actual installed skills (`codex plugin list`, or
the harness's own skill listing) are the ground truth; a table baked into a plugin goes
stale the moment the project's stack changes. Re-derive it per project instead.

## The rule

**Detect the stack from the repo, not from the request.** The human says "add an
endpoint"; the manifest says which framework's idioms that endpoint has to follow. Look
at `package.json` / `pyproject.toml` / `go.mod` / `Gemfile` / `*.csproj`, the config
files next to them, and one neighboring source file in the area you are about to touch.
One glance, not an investigation — if a researcher is already being spawned, fold the
question into its task message instead of running a second pass.

## Precedence when several skills cover the same topic

1. **A skill vendored in this repo** — it encodes decisions this project already made, so
   it outranks anything general.
2. **The official/vendor skill for that exact technology** — the one published by the
   framework's own team, or named for the exact tool.
3. **The generic skill for the category** — use it only when nothing more specific
   exists, or when the specific one doesn't cover the task.

Ties go to the more specific skill. When the vendor-specific skill contradicts the
generic one, the vendor-specific one wins — that is the whole reason it exists.

## Budget

Load **at most 2–3 skills per task**; skills cost context and a third one rarely changes
the code. Skip skills entirely on T0 — a typo fix does not need a framework consultant.
Security-sensitive surfaces are the one place to spend a slot without hesitation.

## Getting it to the people doing the work

A sub-agent spawned via `collaboration.spawn_agent` starts with zero context and does not
inherit anything you loaded, and has no separate `Skill`-loading tool call of its own
confirmed on this port (unlike Claude Code's builder, which holds a dedicated `Skill`
tool). Two ways to get framework guidance to it, in order of preference:

- **Name it on `Load skill:` and let the role figure out access.** State the exact skill
  name in the task message's `Load skill:` line; if the sub-agent's own environment
  exposes a way to load it, that's the cheap path. This was not independently confirmed
  during this port — verify it works before relying on it for anything security-sensitive.
- **Distill it yourself.** When you already have the guidance from your own context (you
  loaded the skill for PLAN, or the guidance is three conventions rather than a document),
  put those conventions in the task message's `Context:` block as explicit rules. This is
  the reliable path on Codex until skill-loading-by-a-sub-agent is confirmed — never
  assume a sub-agent knows a convention you did not write down.

`reviewer`, `security-reviewer`, and `verifier` do **not** get framework skills by
default. Their loyalty is to the acceptance criteria and the diff; a style guide loaded
into any of them turns into invented criteria the builder never received.

## When the right skill is not installed

Never install silently and never fail silently. Name the missing skill to the human, say
where it comes from if the project keeps a `skills-sources.md`, and ask before
installing. If they decline or no source exists, continue on base knowledge and say in
the report that you did.
