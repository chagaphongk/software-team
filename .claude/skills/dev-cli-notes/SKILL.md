---
name: dev-cli-notes
description: Verified local CLI facts for working in the software-team repo itself (not the plugin it ships) — how to get a codex second opinion/review non-interactively, where the full plugin-update procedure lives, and a Bash-tool gotcha that bit a prior run. Use before probing codex/gemini/agy CLI help text from scratch, before consulting codex for a review, or before writing a multi-step script that relies on a shell variable surviving across separate Bash tool calls.
---

# Dev CLI notes (software-team repo)

Facts confirmed live on this machine across prior sessions, kept here so they don't get
re-discovered (and re-spend tool calls) every time. If a command below stops matching
reality, fix this file in the same diff that discovers the drift — don't silently keep
re-probing help text each session instead of updating the record.

Never pipe credentials, API keys, or other secrets into a prompt file handed to `codex`,
`gemini`, or any other external CLI — treat prompt files the same as any other place you
wouldn't paste a secret. These are third-party tools outside this repo's control; if a
command below stops matching what you observe, trust the live `--help`/behavior over this
file and fix this file in the same diff.

## Consulting codex non-interactively

`~/.codex/config.toml` sets `model = "gpt-5.6-luna"` as the default — NOT the model you
usually want for a second opinion. Always pass `-m` explicitly:

```bash
codex exec -m gpt-5.6-sol -s read-only --skip-git-repo-check - < prompt.md
```

- `-s read-only` keeps it from touching files; drop `--skip-git-repo-check` only if you
  are certain you're inside the repo you want reviewed.
- For a dedicated review pass instead of open consultation, `codex exec review` is a
  separate subcommand with its own `--help` (custom review instructions via stdin or arg).
- Large output gets persisted to a tool-results file automatically; don't re-run the same
  command a second time just to see the full text — read the persisted file instead.

## Updating the plugin across ports on this machine

README.md is the canonical, step-by-step reference for this — see its **Update**
subsections under "## Gemini CLI port" and "## Codex CLI port", and the "## agy CLI"
section. Read those before re-deriving the commands from `--help` output. Don't duplicate
those procedures here; if you find them out of date, fix README.md directly rather than
patching around it in this file.

One machine-local gotcha not worth a README line: a third-party CLI's `--help` flag isn't
guaranteed read-only — `agy plugin import gemini --help` was observed to actually attempt
an import/write in agy 1.1.22 instead of printing help. Use `agy plugin help` (a separate
subcommand) to check usage safely instead of appending `--help` to a mutating subcommand.

## Bash-tool shell state does not persist across separate tool calls

A variable set with `export`/assignment in one Bash tool call (e.g.
`REPORT_DIR="$(mktemp -d ...)"`) is gone by the next Bash call — the working directory
persists, but shell variables do not. A script that does `mktemp` in one call and then
references `$REPORT_DIR` in a *later* call will silently expand to empty string, which
can point a script's `--out`/output flag at the current directory instead of the intended
scratch path.

Fix: chain the variable creation and every command that needs it into **one** Bash
invocation (`&&` or newlines in the same call), or resolve the path once and paste the
literal resolved path into subsequent calls instead of the `$VAR` reference. Before
trusting any multi-step shell script pasted from a skill or doc, check whether it assumes
cross-call variable persistence.
