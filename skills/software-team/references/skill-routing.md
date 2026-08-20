# Skill Routing — matching the stack to the right expertise

Read this before PLAN or BUILD when the work targets a specific framework, language, or
platform. The office's job is to get the work verified; this file is about getting it
written to the conventions the stack actually uses, instead of generic-looking code that
passes tests and reads as foreign to the codebase.

This file states the rule only — the mapping of "this stack → that skill" is not
hardcoded here on purpose. A project's actual installed skills (`ls .claude/skills/`, or
the harness's own skill listing) are the ground truth; a table baked into a plugin goes
stale the moment the project's stack changes. Re-derive it per project instead.

## The rule

**Detect the stack from the repo, not from the request.** The human says "add an
endpoint"; the manifest says which framework's idioms that endpoint has to follow. Look
at `package.json` / `pyproject.toml` / `go.mod` / `Gemfile` / `*.csproj`, the config
files next to them, and one neighboring source file in the area you are about to touch.
One glance, not an investigation — if a researcher is already being spawned, fold the
question into its prompt instead of running a second pass.

## Example mappings — a starting point, not ground truth

Typical stack → skill picks, assuming the `fullstack-dev-skills` plugin (or equivalents)
is installed. **Verify each name against the actual installed skill list before putting
it on a `Load skill:` line** — these examples do not override the re-derive-per-project
rule above.

| Stack detected in the repo | Skill to load |
|---|---|
| Next.js | `fullstack-dev-skills:nextjs-developer`; for component-level React work inside it, `fullstack-dev-skills:react-expert` |
| React (no Next.js) | `fullstack-dev-skills:react-expert` |
| Angular | `fullstack-dev-skills:angular-architect` |
| Vue / Nuxt | `fullstack-dev-skills:vue-expert` |
| Django | `fullstack-dev-skills:django-expert` |
| FastAPI | `fullstack-dev-skills:fastapi-expert` |
| Plain Python (typed, tested) | `fullstack-dev-skills:python-pro` |
| TypeScript-heavy (advanced types, tRPC) | `fullstack-dev-skills:typescript-pro` |
| Go | `fullstack-dev-skills:golang-pro` |
| PostgreSQL tuning / queries | `fullstack-dev-skills:postgres-pro` |
| Spring Boot / enterprise Java | `fullstack-dev-skills:java-architect` |

## Precedence when several skills cover the same topic

1. **A skill vendored in this repo** (`.claude/skills/`) — it encodes decisions this
   project already made, so it outranks anything general.
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

## Getting it to the people writing the code

A subagent starts with zero context and does not inherit anything you loaded. Two ways to
close that, in order of preference:

- **Let the builder load it.** The `software-team:builder` agent is granted the `Skill`
  tool. Name the skill on the prompt's `Load skill:` line and let the builder load it
  into its own disposable context — the cheaper option, since the framework guidance
  never enters the orchestrator's context at all.

  **Name the handle, not the nickname.** A skill provided by a plugin resolves as
  `plugin:skill`; a bare name resolves only to a personal or in-repo skill. Write the
  exact string the `Skill` tool will accept.
- **Distill it yourself.** When you already loaded the skill for PLAN, or the guidance is
  three conventions rather than a document, put those conventions in the prompt's
  `Context:` block as explicit rules. Never assume a subagent knows a convention you did
  not write down.

`software-team:reviewer` and `software-team:verifier` do **not** get framework skills by
default. Their loyalty is to the acceptance criteria and the diff; a style guide loaded
into either turns into invented criteria the builder never received.

## When the right skill is not installed

Never install silently and never fail silently. Name the missing skill to the human, say
where it comes from if the project keeps a `skills-sources.md`, and ask before
installing. If they decline or no source exists, continue on base knowledge and say in
the report that you did.
