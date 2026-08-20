# Hook port notes — read before relying on `hooks.json`

**2026-08-20 update, after a real local install** (`codex plugin marketplace add` +
`codex plugin add`, see the repo's `docs/decisions.md`): declaring `"hooks": "./hooks/hooks.json"`
in `.codex-plugin/plugin.json` **is accepted by real plugin ingestion** — the local
`plugin-creator` skill's `validate_plugin.py` rejecting that field was a false negative
(a stricter/staler scaffold-only check, not the real ingestion path); the field is kept
in the shipped manifest on that evidence. Separately, **the skill was confirmed loading
live**: a sandboxed, read-only, ephemeral `codex exec` probe against a fresh session saw
`software-team:software-team` in its skill list with the matching description. **Hook
firing itself was not confirmed** even with the field declared — two such probes showed
`SessionStart`/`UserPromptSubmit`/`Stop` firing for already-installed plugins (`ponytail`,
this user's own global hooks) but no `software-team` entry ever appeared in
`~/.codex/config.toml`'s `[hooks.state]`. The most plausible explanation is an
interactive first-use hook-trust gate (`codex exec --dangerously-bypass-hook-trust`
exists specifically for "automation that already vets hook sources", implying trust is
normally granted interactively) that a non-interactive `--ephemeral --approval never`
probe session can't satisfy — not pursued further here since that flag is explicitly
marked dangerous and bypassing it wasn't something the user asked for. **Function-test
this yourself in an interactive session** (not `codex exec`) before trusting the guard
hooks for anything security-sensitive.


Ported from the Claude Code plugin's `hooks/hooks.json`, same event names and the same
`${CLAUDE_PLUGIN_ROOT}` variable. Verified and unverified pieces, separated honestly:

**Confirmed** (this Codex install, v0.147.0, via `~/.codex/config.toml`'s `[hooks.state]`
entries for the already-installed `ponytail` plugin and this user's own global
`~/.codex/hooks.json`):
- Event names `SessionStart`, `UserPromptSubmit`, `SubagentStart`, `PostToolUse`, `Stop`
  all fired at least once and left a state entry.
- `${CLAUDE_PLUGIN_ROOT}` is the correct variable name for a Codex plugin's own root —
  ponytail's `hooks/claude-codex-hooks.json` (the exact same file used for both Claude
  Code and Codex per its `docs/agent-portability.md`) uses it and installs cleanly.
- The matcher `Edit|Write|apply_patch` is real — it's the literal matcher in this user's
  own global `~/.codex/hooks.json` `PostToolUse` entry.

**A validation quirk, tested and resolved**: `.codex-plugin/plugin.json` declares
`"hooks": "./hooks/hooks.json"` despite this machine's own `plugin-creator` skill
validator (`scripts/validate_plugin.py`) rejecting that field outright ("field `hooks` is
not accepted by plugin validation"). The 2026-08-20 real-install test above confirms the
field is accepted by actual `codex plugin add` ingestion — the scaffold validator is
simply stricter/staler than the real ingestion path, consistent with `ponytail`'s
installed plugin (which also declares the field and visibly registers hook state for its
own events). Trust the real install over the scaffold validator on this specific point.

**Not confirmed**:
- `PreToolUse` — only `PostToolUse` was observed. If Codex does not fire `PreToolUse`,
  `guard_bash.py`/`guard_secrets.py` block *after* the command already ran, which
  defeats the point of a guard (blocking a force-push after it already pushed is
  useless). Trigger a blocked pattern yourself and confirm it's actually rejected
  before-the-fact before relying on this for anything security-sensitive.
- `SubagentStop` and `PreCompact` — carried over from the Claude version unverified.
- The Bash-equivalent tool name in the `PreToolUse` matcher (`Bash|shell|exec` is a
  guess covering the common names; the confirmed evidence only covers the file-edit
  matcher, not a shell-command one).
- The exact JSON field names inside a hook's stdin payload (`tool_input.command`,
  `tool_input.file_path`, `hook_event_name`, `agent_type`, `session_id`) — the scripts in
  this directory parse several plausible key names defensively (same approach as the
  Gemini CLI port) rather than assuming Codex's shape matches Claude's exactly.
- Whether `collaboration.spawn_agent` sub-agents actually trigger `SubagentStart` at all,
  as opposed to only interactive multi-agent sessions.

Function-test before trusting this in production: trigger `git push --force` inside a
throwaway repo and confirm it's rejected *before* it reaches the network, and touch a
`.env` file and confirm the read/write is rejected.
