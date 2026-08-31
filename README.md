# software-team

A Claude Code plugin that runs a task through a real engineering office — an
orchestrator that classifies risk and delegates, plus spawned `researcher` / `builder`
(with a strict TDD mode) / `security-reviewer` / `verifier` (which also carries the
5-category review) / `deployer` / `designer` subagents — instead of one Claude instance role-playing hats
in a single conversation.
The orchestrator never edits a project file itself, at any tier: even a one-character fix
goes through a spawned builder. This no-self-edit invariant, and the deployer-only
invariant covering shipping (deploy, publish, and push always run through
`software-team:deployer`, never the orchestrator), are **instruction-enforced, not
hook-proven** — the hooks log every subagent spawn and block a destructive-command/secret
blocklist, but Claude Code's hook payloads carry no caller identity, so there's no
deterministic way today to prove the orchestrator made zero direct writes. One explicit
exception: the orchestrator may directly append to "office state" — `docs/decisions.md`
decision-log entries and `.claude/state/*` — which isn't covered by the invariant.
Independent spawns run in parallel batches by default — three unrelated builders, or a
verifier alongside a security-reviewer on the same finished diff — never one at a time
just because that's the simpler control flow.

## Why this exists next to `agent-office`

[agent-office](https://github.com/chagaphongk/agent-office) already does real subagent
delegation with risk-tier routing. `software-team` is its stricter sibling, not a
replacement — both stay published. Reach for `software-team` specifically when you want:

- **Zero self-edit, every tier.** agent-office lets the orchestrator handle T0 (typos,
  trivial single-file changes) inline. `software-team` spawns a builder even for that —
  the always-delegate invariant is the point.
- **A review pass with teeth.** agent-office folds review into VERIFY with no fixed
  checklist. `software-team`'s verifier carries an explicit 5-category checklist
  (correctness, security, performance, impact, plan conformance) on any non-mechanical
  logic change, and a Fable-model gated review holds the same checklist on every T2
  diff — in parallel with the verifier over the same finished diff.
- **Hooks installed by default.** Destructive-command blocking, secret-file blocking, and
  subagent-spawn logging ship as first-class plugin hooks (`hooks/hooks.json`), not an
  opt-in `examples/` folder you wire up yourself.

Reach for `agent-office` instead when you want the leaner default — trivial work handled
inline.

## What it does

- **RESEARCH → PLAN → BUILD → REVIEW → VERIFY** — real subagents at every step past
  RESEARCH, spawned by name (`software-team:builder`, not a bare `builder`).
- **PLAN sizes itself before drafting** — if a task turns out to hide more than two or
  three genuine forks, or its destination can't be stated in a line or two, PLAN stops
  and proposes a phase breakdown for approval instead of forcing an oversized,
  likely-to-break plan into one turn; each phase then gets its own normal plan.
- **Bugs get a root-cause pass, unsettled requirements get a clarification pass** — both
  fully self-contained (reproduce/trace/hypothesize-and-falsify/cross-reference for a
  bug; state-understanding/surface-every-fork/stop-and-wait for unsettled scope), before
  PLAN drafts anything. Brand-new, large-scope requirements route to a brainstorming
  skill first when one is installed, then return with settled input for PLAN; work too
  big for one session prefers `wayfinder`'s decision-ticket map over the in-repo Phase
  Map when installed — either way, the office loop (PLAN → BUILD → REVIEW → VERIFY) is
  what actually builds each settled piece, never bypassed by the hand-off.
- **Stack-aware skill selection** — `references/skill-routing.md` detects the framework
  from the repo (not the request) and has the builder load the matching installed skill,
  re-derived per project from the actual installed-skill list rather than a hardcoded
  mapping.
- **Risk-tier routing (T0/T0.5/T1/T2) via a single spawn matrix** — T0 is a
  self-contained fast path (one Haiku builder, orchestrator verifies by diff, nothing
  else loads); T0.5 is a fast lane for a small, scoped, low-judgment change: a no-wait
  PLAN, then `BUILD → VERIFY` with the verifier as sole checking role; T1 always gets
  an independent verifier whose pass includes the 5-category review on any
  non-mechanical logic change, and a
  settled fork-free T1 plan proceeds without an approval wait; T2 requires human plan
  approval, opus-tier subagents (except a fully-specified, no-judgment-left build,
  which may run its builder at the T1 floor), a Fable gated review of the finished diff
  as the T2 review pass, and a security-reviewer when the work touches
  auth/payments/PII/secrets/a public API. Review and verify passes over the same
  finished diff run in one parallel batch.
- **Read-only deliverables skip the plan gate** — a code review or audit spawns
  `software-team:verifier` in `Mode: REVIEW` directly, `software-team:security-reviewer`
  for a security-focused audit, or both in parallel when the ask covers correctness and
  security together; its findings are the deliverable.
- **Full-office roster, not just build/verify** — `security-reviewer` runs a dedicated
  OWASP-class pass before DONE on T2 security-sensitive work; documentation the
  criteria call for (README/CHANGELOG/docstrings) is the builder's work inside BUILD,
  tracing every claim to the diff; `deployer` is the only agent allowed to run a
  deploy/publish/push/delete, and only
  with the human's quoted approval in its prompt — the orchestrator itself never runs one; `designer`
  produces a UI/UX spec before BUILD for a new screen or flow, and the verifier
  statically flags UI basics on any diff that changes rendered output.
- **Parallel by default when scopes are disjoint** — multiple independent builders, or
  the read-only passes (verifier, security-reviewer, T2's Fable review) all reading the
  same finished diff, spawn in one batch instead of one at a time.
- **Model picked per spawn by difficulty, never a fixed default** — mechanical work
  gets Haiku, a small well-understood change gets Sonnet, anything complex (interacting
  files, concurrency, a real judgment call, a failed round) gets Opus. The risk tier
  sets a floor the difficulty pick can't undercut; a T1 Opus build gets an independent
  Opus verifier, while the Fable review is T2's gate.
- **A strict TDD mode** — `software-team:builder` with `Mode: TDD` (used for every bug
  fix) implements through red (a test confirmed to fail for the right reason) → green
  (the minimum code to pass) → refactor, reporting the red/green trail per criterion as
  evidence, with the full suite run once at the end.
- **Deterministic guard hooks** — `hooks/guard_bash.py` parses the shell command into
  real tokens (not a substring regex) to block force-push (including abbreviated and
  refspec forms), `git reset --hard`, `git clean -f`, `rm -rf` on `/`/`~`/`$HOME`/a drive
  root, and destructive shell reads of secrets, while staying quote- and
  comment-aware so it doesn't trip on a quoted `;` in a commit message or a `#`
  comment. It does not implement full bash lexing — compound commands, shell
  functions, here-docs, `eval`, and aliases can still reach a blocked command
  through a spelling it doesn't recognize; the actual hard boundary for an outward
  push/deploy is the human-approval + deployer gate (hard rule #2), not this hook.
  `hooks/guard_secrets.py` blocks Read/Edit/Write of `.env*`, key files, and
  `credentials.*`; `hooks/log_agent.py` writes every subagent start to
  `.claude/state/agent-log.jsonl` (stop events carry no agent identity and are not
  logged); `hooks/pre_compact.py` marks context-compaction
  events so `/software-team:workflow` knows to re-read `docs/decisions.md` instead
  of trusting compacted memory.
- **Known limit: review roles keep Bash.** `security-reviewer` and `verifier`
  subagents have no Write/Edit tool, but they keep Bash access — needed for `git diff` and
  running tests. Their read-only status is instruction-enforced, not sandboxed; nothing
  stops a Bash command from writing a file, the role contract just says not to.
- **`/software-team:workflow`** — reports two kinds of fact, kept distinct: hook-grounded
  (last agent spawn activity and PreCompact markers, read straight from
  `.claude/state/agent-log.jsonl`) and conversation-derived (task, tier, state, and
  verdicts — inferred from the conversation, then checked against the log, not read from
  it; `log_agent.py` only ever writes a timestamp, event, agent name, and session id, so
  it has no verdict or task-state fields to read). **`/software-team:decision`** —
  appends a one-line, course-changing decision to `docs/decisions.md`.

## Install

Requires `python3` on `PATH` (the hooks use it). Current version: `0.4.2`.

1. Register the marketplace, once per machine:

   ```
   /plugin marketplace add chagaphongk/software-team
   ```

   For local development, point at a clone instead of the GitHub repo:

   ```
   /plugin marketplace add /path/to/software-team
   ```

2. Install the plugin from it:

   ```
   /plugin install software-team@software-team-marketplace
   ```

3. Restart the session — plugin agents, commands, and hooks load at startup, so a
   mid-session install won't take effect until you do.

4. If you previously copy-installed the old single-conversation `ai-software-team` skill
   (`~/.claude/skills/ai-software-team` or `./.claude/skills/ai-software-team`), remove
   that directory — otherwise both the old and new skill are live and can trigger-collide.

5. Recommended: add a `permissions.deny` block for `.env*` / `*.pem` / `*.key` /
   `id_rsa*` files in your own `settings.json` — the plugin's hooks (`guard_secrets.py`)
   are the second guard layer, not a substitute for the harness-level deny rule.

### Verify it's working

Run any trivial task (a T0-sized change), then:

```
/software-team:workflow
```

should report a tier, state, and pending gates — the tier/state are conversation-derived,
checked against (not read from) `.claude/state/agent-log.jsonl`'s hook-grounded spawn
activity — if that file doesn't exist yet or the command says hooks aren't firing, the
plugin installed but the hooks didn't register; re-check step 3 (restart) before anything
else.

### Update

```
/plugin marketplace update software-team-marketplace
/plugin update software-team
```

(or `/plugin uninstall software-team` followed by a fresh `/plugin install` from step 2,
if the update command isn't available in your Claude Code version). Restart the session
afterward — same reason as a fresh install. Check `docs/decisions.md` in this repo after
updating for anything course-changing since your installed version.

## Benchmark

The old single-conversation skill was evaluated with-skill vs. no-skill baseline on 3
evals (aggregate ~80% vs ~33%) — see `docs/decisions.md` and git history for that run.
This version's evals (`skills/software-team/evals/evals.json`) were adapted to check for
actual subagent delegation instead of in-transcript role-play text; a fresh baseline run
against this architecture is pending.

## Gemini CLI port

`gemini-extension/` is a parallel port of this same design to Gemini CLI's own extension
format (`gemini-extension.json` + `agents/*.md` + `skills/software-team/SKILL.md` +
`commands/*.toml` + `hooks/hooks.json`), for people who use Gemini CLI instead of (or
alongside) Claude Code. Install with:

```
gemini extensions install /path/to/software-team/gemini-extension --consent
```

(`--consent` skips the interactive trust/security prompt for a non-interactive install;
review the extension first if you're installing from someone else's clone. If it
launches non-interactively and shows a "trust this folder" prompt anyway, set
`GEMINI_CLI_TRUST_WORKSPACE=true` for that command.)

**Update**

```
gemini extensions update software-team
```

(or `gemini extensions update --all` to refresh every installed extension.) A `local`
install (the default from the command above) is a **snapshot copy** taken at install
time, not a live link — editing files under `gemini-extension/` does nothing to the
installed copy until you re-run `update`. Confirm the version bumped with
`gemini extensions list`. If you're actively developing this repo rather than just
consuming it, `gemini extensions link /path/to/software-team/gemini-extension` instead of
`install` keeps the installed copy always in sync with the source tree, no `update` step
needed — trade-off: a link can't be pinned to an older version the way a snapshot can.
The `update` command may prompt for the same trust confirmation as a fresh install; pipe
`y` (`echo y | gemini extensions update software-team`) if running it non-interactively.

**Known gaps in this port, disclosed rather than glossed over:**
- Model tiers are described generically (cheapest/fastest, balanced, most capable,
  extended-reasoning) rather than pinned to a specific Gemini model string, since
  Gemini's model catalog names change faster than this file should need updating —
  resolve the current model string for each tier yourself when spawning.
- The two guard hooks (`guard_bash.py`, `guard_secrets.py`) and the agent-log hook
  (`log_agent.py`) parse the incoming hook JSON defensively (several plausible field-name
  variants), because the exact payload shape Gemini CLI's `BeforeTool`/`AfterTool` events
  send was not confirmed by a live session during this port — this
  machine's Gemini CLI account could not authenticate at the time. The hook *event names*
  and the extension's overall structure (`agents/`, `skills/`, `commands/`, `hooks/`) are
  confirmed against Gemini CLI's own docs and its `extensions validate` / `extensions
  list` / `skills list` tooling — those passed clean. Function-test the hooks yourself
  once you have a working session (trigger a `run_shell_command` call with a blocked
  pattern and confirm it's actually rejected) before relying on them.
- `evals/evals.json` was not ported (benchmark harness, not required for the extension to
  function).

## Codex CLI port

`codex-extension/` is a parallel port to Codex's own plugin format
(`.codex-plugin/plugin.json` + `skills/software-team/SKILL.md` + `hooks/hooks.json`), for
people who use OpenAI Codex CLI instead of (or alongside) Claude Code. This port required
a real architecture change, not just a file-format translation: **Codex has no
plugin-declarable named-persona agent file** (confirmed against the official Codex plugin
manifest schema — no `agents` field exists). Its native subagent primitive,
`collaboration.spawn_agent`, takes a task message and an optional `fork_turns: "none"` for
fresh context, but has no system-prompt/persona parameter (confirmed empirically via a
sandboxed, read-only `codex exec` probe on 2026-08-20). So instead of an `agents/`
directory, `skills/software-team/references/roles.md` holds all 6 role contracts
(builder with its TDD mode, security-reviewer, verifier with its REVIEW mode,
researcher, deployer, designer) as text to copy verbatim into the spawn's task message — the office's
state machine, tiers, and hard rules are otherwise unchanged.

**Installed and confirmed loading live** (2026-08-20): registered as its own marketplace
(`codex-extension/` carries a self-contained `.claude-plugin/marketplace.json` +
`.codex-plugin/plugin.json` pair — it cannot share the repo root's Claude marketplace,
because Codex's `skills` manifest field is validated to resolve to the literal path
`skills`, so co-locating with Claude would force both hosts to read the exact same
`skills/software-team/SKILL.md`, and the two hosts' spawn semantics are incompatible).
Install with:

```
codex plugin marketplace add /path/to/software-team/codex-extension
codex plugin add software-team@software-team-codex-marketplace
```

A sandboxed, read-only, ephemeral `codex exec` probe against a fresh session afterward
confirmed the skill actually loads (`software-team:software-team` appeared in the
session's skill list with the matching description).

**Update**

```
codex plugin marketplace upgrade software-team-codex-marketplace
codex plugin add software-team@software-team-codex-marketplace
```

`marketplace upgrade` only re-fetches a **Git**-sourced marketplace; a local-path
marketplace (the install command above) already reads the current files on disk, so that
step is a no-op for it — the `plugin add` line is what actually refreshes the
**installed** copy (`~/.codex/plugins/cache/...`), which is its own snapshot and won't
pick up source changes until you re-run `add`. Confirm the version bumped with
`codex plugin list`.

**If you moved or renamed the local clone** (this repo itself was renamed from
`ai-software-team` to `software-team` during development), the registered marketplace
still points at the old path and both `codex plugin list` and `codex plugin add` fail
with `marketplace root does not contain a supported manifest`. Fix by re-registering the
marketplace at its new path, then reinstalling the plugin from it:

```
codex plugin marketplace remove software-team-codex-marketplace
codex plugin marketplace add /path/to/software-team/codex-extension
codex plugin add software-team@software-team-codex-marketplace
```

**Known gaps in this port, disclosed rather than glossed over** (full detail in
`codex-extension/hooks/PORT_NOTES.md`):
- No `commands/` support on Codex (confirmed — not in the official plugin manifest
  schema) — there is no `/software-team:workflow` or `/software-team:decision` slash
  command on this port; read `docs/decisions.md` and `.software-team/state/agent-log.jsonl`
  directly instead.
- Per-spawn `model`/`reasoning_effort` selection is available (confirmed by live
  introspection of the spawn tool's schema — it's the tool name and field set that drift:
  named `collaboration.spawn_agent` when this port was written, `multi_agent_v1__spawn_agent`
  as of this update; introspect your own tool set rather than trusting either string).
- **Hooks did not confirm firing**, even though `.codex-plugin/plugin.json` declares
  `"hooks": "./hooks/hooks.json"` and real `codex plugin add` ingestion accepts that field
  (the local `plugin-creator` skill's scaffold validator rejects it — a stricter/staler
  check than actual ingestion, confirmed by this real install). Two sandboxed `codex exec`
  probes after install showed other already-trusted plugins' hooks firing
  (`SessionStart`/`UserPromptSubmit`/`Stop`) but no `software-team` entry ever appeared in
  `~/.codex/config.toml`'s `[hooks.state]` — most likely an interactive first-use
  hook-trust gate that a non-interactive `--ephemeral --approval never` session can't
  satisfy (`--dangerously-bypass-hook-trust` exists for exactly this, and wasn't used
  since it's explicitly flagged dangerous and wasn't asked for). Test this yourself in an
  **interactive** Codex session — trigger a blocked command and confirm rejection —
  before trusting the guard hooks for anything security-sensitive.
- Hook payload field names (`tool_input.command`, `tool_input.file_path`,
  `hook_event_name`, `agent_type`, `session_id`) are parsed defensively across several
  plausible key names, same approach as the Gemini CLI port, since Codex's exact shape
  wasn't confirmed live.

## agy CLI

`agy` is a separate, third-party multi-model CLI (not maintained by this project) that
can import an already-installed Gemini CLI extension or Claude Code plugin into its own
config as an agent skill. This isn't a fourth port — there's no
`agy-extension/` directory here — just usage notes for people who already run one of the
two supported installs above and also use agy.

```
agy plugin import gemini --force
```

`agy plugin import` **copies** the plugin at the moment you run it — it is not a live
link, and by default it **skips a name it already imported**, so `--force` is required to
pick up a version bump (confirmed: without `--force` it printed `already imported, use
--force to re-import` and left the stale copy in place). Run `gemini extensions update
software-team` (see above) first if the Gemini CLI extension itself is stale, since agy
copies whatever is currently installed there, not the git repo directly. Confirm with:

```
agy plugin list
```

and check the `importedAt` timestamp for `software-team` advanced.

**Known gap, disclosed rather than glossed over:** `agy plugin import claude` (or the
bare `agy plugin import`, which tries both sources) reported `No claude extensions
found` in testing, even though the Claude Code plugin was confirmed installed and
current (`~/.claude/plugins/installed_plugins.json` showed the right version). Only the
`gemini` source reliably picked up this plugin. If you rely on agy, keep the Gemini CLI
extension installed (even alongside Claude Code) as the path agy actually reads from —
treat `agy plugin import claude` as best-effort, not a substitute for that.

## Related

[agent-office](https://github.com/chagaphongk/agent-office) — the leaner Claude Code
sibling; T0 handled inline.
