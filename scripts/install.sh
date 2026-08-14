#!/usr/bin/env bash
# Installs (or updates) the ai-software-team skill into a local Claude Code
# skills directory. Run from a clone of this repo — this is a plain copy,
# no plugin manifest or dependencies involved.
#
# Usage:
#   bash scripts/install.sh                 # -> ~/.claude/skills/ai-software-team
#   bash scripts/install.sh --project       # -> ./.claude/skills/ai-software-team
#   bash scripts/install.sh --target DIR    # -> DIR

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ "${1:-}" = "--project" ]; then
  TARGET="./.claude/skills/ai-software-team"
elif [ "${1:-}" = "--target" ] && [ -n "${2:-}" ]; then
  TARGET="$2"
else
  TARGET="$HOME/.claude/skills/ai-software-team"
fi

mkdir -p "$TARGET/evals"
cp "$REPO_ROOT/SKILL.md" "$TARGET/SKILL.md"
cp "$REPO_ROOT/evals/evals.json" "$TARGET/evals/evals.json"

echo "Installed ai-software-team -> $TARGET"
ls "$TARGET"
