#!/usr/bin/env python3
"""Self-check for guard_secrets.py / guard_bash.py. Stdlib-only, assert-based, no framework."""
import sys

# A regex/command blocklist can never be fully complete. This hook does not implement
# bash lexing and no hand-rolled scanner here ever will: compound commands, shell
# functions, here-docs, `eval`, and git/shell aliases can all reach a blocked command
# through a spelling this file doesn't recognize. If that gap matters, the answer is a
# real shell parser or enforcement moved to the approval gate, not more patterns here.
# Also accepted, not chased: interpreter one-liners (e.g. `python -c "..."`),
# indirection through env/xargs/find -exec, non-POSIX delete verbs (PowerShell
# Remove-Item), and a quoted absolute git/rm path containing backslashes (shlex's
# posix-mode backslash handling can consume them). The actual hard boundary for an
# outward push/deploy is the human-approval + deployer gate (SKILL.md hard rule #2);
# this hook only narrows what an unattended Bash spawn can do before that gate.

from guard_secrets import is_secret_path
from guard_bash import blocked_reason

SECRET_PATH = "secret_path"
BASH = "bash"

CASES = [
    ("forward-slash secret path", "foo/credentials.json", True, SECRET_PATH),
    ("windows backslash secret path", "foo\\credentials.json", True, SECRET_PATH),
    (".envrc path", "foo/.envrc", True, SECRET_PATH),
    ("benign unrelated file path", "foo/notes.txt", False, SECRET_PATH),
    ("benign bash command", "ls", False, BASH),
    ("dangerous command against sensitive path", "cat ~/.ssh/id_rsa", True, BASH),
    ("type-check flag not a Get-Content alias", "npm run type-check -- --env .env.local", False, BASH),
    ("bare git reset --hard with no ref", "git reset --hard", True, BASH),
    ("git reset --hard chained with semicolon", "git reset --hard; rm -rf build", True, BASH),
    ("git reset --hard chained with &&", "git reset --hard&&echo done", True, BASH),
    ("git reset --hard with a flag before --hard", "git reset -q --hard", True, BASH),
    ("git reset --hard with a flag before reset", "git -C . reset --hard", True, BASH),
    ("git.exe reset --hard on Windows", "git.exe reset --hard HEAD~1", True, BASH),
    ("awk reading id_ecdsa key", "awk '{print}' ~/.ssh/id_ecdsa", True, BASH),
    ("git reset --hard as a quoted grep search string, not a real command", 'git grep "git reset --hard"', False, BASH),
    ("force push with a flag before push", "git -C . push --force", True, BASH),
    ("git.exe force push short flag", "git.exe push -f", True, BASH),
    ("force push via + refspec, no --force flag", "git push origin +main", True, BASH),
    ("git clean -fd with a flag before clean", "git -C . clean -fd", True, BASH),
    ("git.exe clean -f", "git.exe clean -f", True, BASH),
    ("rm -rf with -- before the root target", "rm -rf -- /", True, BASH),
    ("benign push to a named branch", "git push origin main", False, BASH),
    ("benign recursive delete of a project subdir", "rm -rf ./build", False, BASH),
    ("force push with combined short flags", "git push -vf", True, BASH),
    ("force push via quoted + refspec", 'git push origin "+main:main"', True, BASH),
    ("git clean with long --force flag", "git clean --force -d", True, BASH),
    ("rm with split -r -f flags on root", "rm -r -f /", True, BASH),
    ("rm with long --recursive --force flags on root", "rm --recursive --force /", True, BASH),
    ("rm -rf on quoted $HOME", 'rm -rf "$HOME"', True, BASH),
    ("--force-if-includes alone does not force a push", "git push --force-if-includes origin main", False, BASH),
    ("git grep for the word push is not a push", "git grep push -f patterns.txt", False, BASH),
    ("push --force appearing after a shell separator, not the git subcommand", "git status && echo push --force", False, BASH),
    ("rm -rf on a real subdirectory under home, not home itself", "rm -rf ~/project/build", False, BASH),
    ("force push glued to && with no space", "git push --force&&echo done", True, BASH),
    ("force clean glued to ; with no space", "git clean --force;echo done", True, BASH),
    ("rm -rf / glued to a pipe", "rm -rf /|echo done", True, BASH),
    ("force push on the line after a newline-separated command", "git status\ngit push --force", True, BASH),
    ("force push inside parens (subshell-shaped)", "(git push --force)", True, BASH),
    ("force push inside a $(...) command substitution", "$(git push --force)", True, BASH),
    ("git invoked via an absolute unix path", "/usr/bin/git push --force", True, BASH),
    ("rm invoked via an absolute unix path", "/bin/rm -rf /", True, BASH),
    ("force push via an unambiguous --force-w abbreviation", "git push --force-w origin main", True, BASH),
    ("rm -rf on quoted $HOME with a trailing slash", 'rm -rf "$HOME/"', True, BASH),
    ("rm -rf on quoted ${HOME}/. (dir-then-self)", 'rm -rf "${HOME}/."', True, BASH),
    ("rm -rf on a bare Windows drive root", "rm -rf C:/", True, BASH),
    ("echo'ing the words git push --force is not a push", "echo git push --force", False, BASH),
    ("echo'ing the words rm -rf / is not a delete", "echo rm -rf /", False, BASH),
    ("printf with git push --force as its argument text", "printf %s git push --force", False, BASH),
    ("git clean -n with -foo as a literal pathspec after --", "git clean -n -- -foo", False, BASH),
    ("a quoted semicolon inside a commit message stays one token", 'git commit -m "fix; rm -rf /"', False, BASH),
    ("force push with an env-var assignment prefix", "FOO=bar git push --force", True, BASH),
    ("--recursive appearing as a literal operand after --, not a flag", "rm -f -- --recursive /", False, BASH),
    ("force push hidden inside a $(...) substitution, even in double quotes", 'echo "$(git push --force)"', True, BASH),
    ("force push after a lone & background operator", "git status & git push --force", True, BASH),
    ("force push text that is actually a bash comment", "echo safe # ; git push --force", False, BASH),
    ("git clean force via an unambiguous --forc abbreviation", "git clean --forc -d", True, BASH),
    ("rm recursive+force via unambiguous --recursiv/--forc abbreviations", "rm --recursiv --forc $HOME", True, BASH),
    ("--follow-tags is not an abbreviation of --force", "git push --follow-tags origin main", False, BASH),
    ("force push after a multiline comment, comment ends at the newline", "echo safe # harmless\ngit push --force", True, BASH),
    ("force push inside a $(...) whose own quoted ')' must not close it early", "echo \"$(printf ')'; git push --force)\"", True, BASH),
    ("single-quoted $(...) does not execute, must not be blocked", "echo '$(git push --force)'", False, BASH),
    ("escaped \\$(...) does not execute, must not be blocked", 'echo "\\$(git push --force)"', False, BASH),
    ("force push with a += assignment prefix", "FOO+=bar git push --force", True, BASH),
    ("git push --fo is ambiguous to git but blocked anyway (accepted over-block)", "git push --fo origin main", True, BASH),
    ("git push --forceful is invalid to git but blocked anyway (accepted over-block)", "git push --forceful origin main", True, BASH),
    ("--force-i is a valid abbreviation of --force-if-includes, not --force", "git push --force-i origin main", False, BASH),
    ("force push behind the transparent 'command' builtin", "command git push --force", True, BASH),
    ("force push behind 'exec'", "exec git push --force", True, BASH),
    ("force push behind 'time'", "time git push --force", True, BASH),
    ("force push inside an if/then/fi control structure", "if true; then git push --force; fi", True, BASH),
    ("force push split by a bash line continuation", "git push --for\\\nce", True, BASH),
]

if __name__ == "__main__":
    passed = 0
    failed = 0
    for desc, value, expected_blocked, checker in CASES:
        actual_blocked = blocked_reason(value) is not None if checker == BASH else is_secret_path(value)
        try:
            assert actual_blocked == expected_blocked, (
                f"{desc}: expected blocked={expected_blocked}, got {actual_blocked}"
            )
            print(f"PASS: {desc}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {e}")
            failed += 1

    print(f"\n{passed} PASS, {failed} FAIL")
    sys.exit(1 if failed else 0)
