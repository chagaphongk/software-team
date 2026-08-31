---
name: dev-cli-notes
description: Verified local CLI facts for working in the software-team repo itself (not the plugin it ships) — how to get a codex second opinion/review non-interactively, where the full plugin-update procedure lives, and Bash-tool gotchas on this Windows machine (shell state, /c/ vs C:\ paths for python, backgrounding, prompt length) that bit prior runs. Use before probing codex/gemini/agy CLI help text from scratch, before consulting codex for a review, before passing a file path from Bash into python3, or before writing a multi-step script that relies on a shell variable surviving across separate Bash tool calls.
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
- If codex errors with something like "prompt is too long", the fix is to shrink the
  *prompt*, not to keep resubmitting the same oversized one — point codex at file paths in
  the repo and let it read them itself (it can), instead of pasting large file contents or
  long context inline into the prompt string.
- Don't append your own `&`/background operator to a `codex exec` command that you're also
  launching with the tool's own `run_in_background` — the two interact badly and can report
  a false "exited with code 0" before codex has actually finished. Launch the command
  plainly and let `run_in_background` (or the harness's own background/task tracking)
  handle it; check real progress via the task's own output file or notification, not by
  polling `ps`/`tasklist` for the process.

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

## Bash tool on this machine is Git Bash; python3 is Windows-native

The Bash tool runs Git Bash, so `/c/Users/...` paths work for `ls`, `cat`, `cp`, `mv`,
`mktemp`, and other shell builtins/utilities. **`python3` is a native Windows binary and
cannot open a `/c/...` path** — `open('/c/Users/...')` raises `FileNotFoundError` even
though the file exists. When handing a path from Bash to python (as an argument, in a
`-c` snippet, or in a heredoc script), use the Windows form: `C:/Users/...` (forward
slashes are fine) or a raw string `r'C:\Users\...'`. Conversely, the Read/Write/Edit tools
want Windows paths too; only Bash-side commands understand the `/c/` form.

Two related inline-`python -c` traps: a backslash inside a bash double-quoted string is
eaten before python sees it (so `split('\\')` or `r'C:\..'` behave differently than
expected), and a `'` inside single-quoted python inside `"..."` needs care. For anything
beyond a one-liner, write the script to the scratchpad with the Write tool and run
`python3 "C:/…/script.py"` instead of fighting quoting.

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

Also: the Read tool refuses a re-read of a file that hasn't changed since your last Read
("Wasted call — file unchanged"). After an Edit, the harness already holds the new state;
don't Read it back to "verify" — run the actual check (tests, syntax parse, `git diff`)
instead.

## Gemini CLI extension update on this machine

`gemini extensions update software-team` hangs forever when run non-interactively (it
asks a `Do you want to continue? [Y/n]` consent question on stdin) — pipe answers in
(`printf 'y\ny\n' | gemini extensions update software-team`) or avoid the prompt
entirely on install with `--consent --skip-settings`. `extensions install` takes the
local path as a **positional** `<source>` argument (there is no `--path` flag). Trap
confirmed live: a consent-interrupted update can still have copied the new version
into `~/.gemini/extensions/<name>`, after which a retry reports "already up to date"
while the installed copy holds broken/partial files — fix by `uninstall` then a fresh
`install <path> --consent`. The `Assertion failed ... src\win\async.c` line printed
after a successful install/uninstall is benign node teardown noise, not a failure.
`agy plugin import gemini --force` has the same stdin trait — run it foreground with
piped `y`s, not as a detached background command, or it hangs indefinitely.
