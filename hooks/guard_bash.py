#!/usr/bin/env python3
"""PreToolUse guard for Bash: blocks destructive/irreversible commands (exit 2)."""
import json, re, shlex, sys

GIT_NAMES = ("git", "git.exe", "git.cmd")
RM_NAMES = ("rm", "rm.exe")
GIT_GLOBAL_OPTS_WITH_VALUE = ("-C", "-c", "--git-dir", "--work-tree", "--namespace")
ROOT_TARGETS = ("/", "~", "$HOME", "${HOME}")
DRIVE_ROOT_RE = re.compile(r"^[A-Za-z]:[/\\]?$")
SEPARATOR_TOKENS = (";", "&&", "||", "|", "&", "(", ")")
ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\+?=")
SKIP_LEADING_WORDS = ("command", "exec", "time", "nohup", "sudo", "if", "then", "else", "elif", "fi", "while", "until", "do", "done", "{", "}")

# git push/clean/rm are parsed into tokens rather than matched with a single regex:
# a regex that tolerates leading global flags (git -C . push) also has to tolerate
# arbitrary skipped words, which then matches "push"/"-f" appearing in an unrelated
# subcommand ("git grep push -f file"). Token parsing finds the real subcommand and
# its actual arguments instead of pattern-matching substrings of the raw string.
#
# Accepted ceiling (defense-in-depth narrowing, not the enforcement boundary): this
# hook does not implement bash lexing, and no hand-rolled scanner here ever will --
# compound commands, shell functions, here-docs, `eval`, and git/shell aliases can
# all reach a blocked command through a spelling this file doesn't recognize. If
# that gap matters, the answer is a real shell parser or enforcement moved to the
# approval gate, not more patterns here. Also out of scope: interpreter one-liners
# (python -c "..."), indirection through env/xargs/find -exec, non-POSIX delete
# verbs (PowerShell Remove-Item), and a quoted absolute git/rm path containing
# backslashes (shlex's posix-mode backslash handling can consume them). The actual
# hard boundary for an outward push/deploy is the human-approval gate and the
# deployer role (see SKILL.md hard rule #2) — this hook only narrows what an
# unattended Bash spawn can do before that gate.
TEXT_BLOCK = [
    (r"git(?:\.exe|\.cmd)?\s+(?:\S+\s+)*?reset\s+(?:\S+\s+)*?--hard(?=[\s;&|)]|$)", "git reset --hard is blocked; use it only via explicit user approval."),
    (r"\bdrop\s+(database|table)\b", "DROP DATABASE/TABLE is blocked from automated execution."),
    (r"\b(cat|less|more|head|tail|grep|awk|sed|cp|scp|base64|xxd|strings|Get-Content|Select-String)\b[^\n|;&]*\.env\b(?!\.(example|sample|template)\b)",
     "Reading .env files via shell is blocked. Ask the user to handle secrets."),
    (r"\b(cat|less|more|head|tail|grep|cp|scp|base64|xxd|strings|awk|sed|Get-Content|Select-String)\b[^\n|;&]*(id_rsa|id_dsa|id_ecdsa|id_ed25519|\.pem\b|\.key\b)",
     "Reading key/credential files via shell is blocked."),
]


def _prepare(cmd):
    """One quote/escape-aware pass over the raw command: strips a bash line
    continuation (backslash-newline), truncates each unquoted, word-initial '#'
    comment to its own line only (bash comments end at the newline, not the whole
    string), and collects every live $(...)/`...` substitution span seen outside
    single quotes and not after an escaped '$' or backtick — those are the only two
    things that change bash's own view of the command, so a single scanner has to
    track quote state for both or the two checks disagree with each other."""
    cmd = cmd.replace("\\\n", "")
    out = []
    subs = []
    in_single = in_double = False
    prev_ws = True
    i, n = 0, len(cmd)
    while i < n:
        c = cmd[i]
        if in_single:
            out.append(c)
            if c == "'":
                in_single = False
            i += 1
            prev_ws = False
            continue
        if c == "\\" and i + 1 < n:
            out.append(c)
            out.append(cmd[i + 1])
            i += 2
            prev_ws = False
            continue
        if c == "'" and not in_double:
            in_single = True
            out.append(c)
            i += 1
            prev_ws = False
            continue
        if c == '"':
            in_double = not in_double
            out.append(c)
            i += 1
            prev_ws = False
            continue
        if c == "#" and prev_ws and not in_double:
            j = cmd.find("\n", i)
            if j == -1:
                break
            i = j
            prev_ws = True
            continue
        if cmd[i:i + 2] == "$(":
            depth, j = 1, i + 2
            start = j
            s_single = s_double = False
            while j < n and depth > 0:
                cj = cmd[j]
                if s_single:
                    if cj == "'":
                        s_single = False
                elif s_double:
                    if cj == '"':
                        s_double = False
                    elif cj == "\\" and j + 1 < n:
                        j += 1
                elif cj == "\\" and j + 1 < n:
                    j += 1
                elif cj == "'":
                    s_single = True
                elif cj == '"':
                    s_double = True
                elif cj == "(":
                    depth += 1
                elif cj == ")":
                    depth -= 1
                j += 1
            subs.append(cmd[start:j - 1 if depth == 0 else j])
            out.append(cmd[i:j])
            i = j
            prev_ws = False
            continue
        if c == "`":
            start_tick = i
            j = i + 1
            while j < n and cmd[j] != "`":
                if cmd[j] == "\\" and j + 1 < n:
                    j += 1
                j += 1
            end = min(j, n)
            subs.append(cmd[i + 1:end])
            close = min(j + 1, n)
            out.append(cmd[start_tick:close])
            i = close
            prev_ws = False
            continue
        out.append(c)
        prev_ws = c.isspace()
        i += 1
    return "".join(out), subs


def _pad_shell_metachars(cmd):
    """Insert spaces around shell separators so they always tokenize as their own
    token, even glued to adjacent text (`--force&&echo`) — quoting still groups
    correctly afterward, since shlex only splits on whitespace outside quotes."""
    cmd = cmd.replace("\r\n", "\n").replace("\n", " ; ")
    cmd = re.sub(r"&&", " && ", cmd)
    cmd = re.sub(r"\|\|", " || ", cmd)
    cmd = re.sub(r"(?<!&)&(?!&)", " & ", cmd)
    cmd = re.sub(r"(?<!\|)\|(?!\|)", " | ", cmd)
    cmd = re.sub(r"[;()]", lambda m: " " + m.group(0) + " ", cmd)
    return cmd


def _tokenize(cmd):
    padded = _pad_shell_metachars(cmd)
    try:
        return shlex.split(padded, posix=True)
    except ValueError:
        return padded.replace('"', " ").replace("'", " ").split()


def _segments(tokens):
    seg = []
    for t in tokens:
        if t in SEPARATOR_TOKENS:
            if seg:
                yield seg
            seg = []
        else:
            seg.append(t)
    if seg:
        yield seg


def _basename(token):
    return re.split(r"[\\/]", token)[-1].lower()


def _leading_command(segment):
    """The executable actually run: skip leading VAR=val assignments and
    transparent wrappers/control words (`sudo`, `exec`, `time`, `if`, `then`, ...),
    then return the index and basename of the first remaining token — a later
    token matching 'git'/'rm' is an argument to something else
    (`echo git push --force`), and the index lets callers slice the skipped
    prefix off before parsing the command's own arguments."""
    for i, t in enumerate(segment):
        if ASSIGNMENT_RE.match(t) or t in SKIP_LEADING_WORDS:
            continue
        return i, _basename(t)
    return None, None


def _option_area(args):
    """Tokens before a `--` end-of-options marker — the only tokens that can be
    flags; anything after `--` is a literal operand (a pathspec, a filename)."""
    if "--" in args:
        return args[: args.index("--")]
    return args


def _has_short_flag(args, letter):
    return any(a.startswith("-") and not a.startswith("--") and letter in a[1:] for a in _option_area(args))


def _matches_long_flag(token, flag):
    """True if token is exactly `flag`, an unambiguous abbreviation of it
    (`--forc` for `--force`), or a longer form built on it
    (`--force-with-lease`)."""
    if not token.startswith("--") or len(token) <= 2:
        return False
    return token.startswith(flag) or flag.startswith(token)


FORCE_IF_INCLUDES = "--force-if-includes"


def _is_force_push_flag(a):
    if not a.startswith("--") or len(a) <= 2:
        return False
    if a == "--force":
        return True
    # A token longer than "--force" that is itself a prefix of the (safe)
    # --force-if-includes flag -- e.g. --force-i, --force-if -- is that flag's
    # abbreviation, not --force's; only check this once `a` is long enough that
    # it can no longer just be a short abbreviation of "--force" itself.
    if len(a) > len("--force") and FORCE_IF_INCLUDES.startswith(a):
        return False
    return a.startswith("--force") or "--force".startswith(a)


def _is_force_push(args):
    opts = _option_area(args)
    for a in opts:
        if _is_force_push_flag(a):
            return True
    for a in args:
        stripped = a.strip("'\"").lstrip("$")
        if stripped.startswith("+") and len(stripped) > 1:
            return True
    return _has_short_flag(args, "f")


def _is_force_clean(args):
    return any(_matches_long_flag(a, "--force") for a in _option_area(args)) or _has_short_flag(args, "f")


def _git_subcommand_args(segment):
    # segment[0] is already confirmed to be the git executable.
    j = 1
    while j < len(segment) and segment[j].startswith("-"):
        opt = segment[j]
        j += 1
        if opt in GIT_GLOBAL_OPTS_WITH_VALUE and j < len(segment):
            j += 1
    if j < len(segment):
        return segment[j], segment[j + 1:]
    return None


def _normalize_target(t):
    t = t.strip("'\"")
    if t.endswith("/."):
        t = t[:-2]
    while len(t) > 1 and t.endswith("/"):
        t = t[:-1]
    return t


def _rm_targets_root(segment):
    # segment[0] is already confirmed to be rm.
    args = segment[1:]
    opts = _option_area(args)
    has_r = any(_matches_long_flag(a, "--recursive") for a in opts) or any(a in ("-r", "-R") for a in opts) or _has_short_flag(args, "r") or _has_short_flag(args, "R")
    has_f = any(_matches_long_flag(a, "--force") for a in opts) or _has_short_flag(args, "f")
    if not (has_r and has_f):
        return False
    targets = [_normalize_target(a) for a in args if not a.startswith("-")]
    return any(t in ROOT_TARGETS or DRIVE_ROOT_RE.match(t) for t in targets)


def blocked_reason(cmd):
    cmd, subs = _prepare(cmd or "")
    for inner in subs:
        reason = blocked_reason(inner)
        if reason:
            return reason
    for segment in _segments(_tokenize(cmd)):
        idx, name = _leading_command(segment)
        if idx is None:
            continue
        exec_segment = segment[idx:]
        if name in GIT_NAMES:
            sub = _git_subcommand_args(exec_segment)
            if sub:
                subcommand, args = sub
                if subcommand == "push" and _is_force_push(args):
                    return "Force push is blocked. Ask the user to run it themselves if truly needed."
                if subcommand == "clean" and _is_force_clean(args):
                    return "git clean -f is blocked (deletes untracked files irreversibly)."
        elif name in RM_NAMES:
            if _rm_targets_root(exec_segment):
                return "Recursive delete of / or home is blocked."
    for pattern, reason in TEXT_BLOCK:
        if re.search(pattern, cmd, re.IGNORECASE):
            return reason
    return None


if __name__ == "__main__":
    try:
        data = json.load(sys.stdin)
        cmd = (data.get("tool_input") or {}).get("command", "") or ""
    except Exception:
        print("BLOCKED by policy hook: malformed hook input, failing closed.", file=sys.stderr)
        sys.exit(2)
    reason = blocked_reason(cmd)
    if reason:
        print(f"BLOCKED by policy hook: {reason}", file=sys.stderr)
        sys.exit(2)
    sys.exit(0)
