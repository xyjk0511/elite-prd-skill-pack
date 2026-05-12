#!/usr/bin/env bash
set -euo pipefail

CODEX_HOME_DIR="${CODEX_HOME:-"$HOME/.codex"}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_SKILLS="$REPO_ROOT/.agents/skills"
TARGET_SKILLS="$CODEX_HOME_DIR/skills"

if [[ ! -d "$SOURCE_SKILLS" ]]; then
  echo "Skill source directory not found: $SOURCE_SKILLS" >&2
  exit 1
fi

mkdir -p "$TARGET_SKILLS"

for skill in "$SOURCE_SKILLS"/*; do
  [[ -d "$skill" ]] || continue
  name="$(basename "$skill")"
  rm -rf "$TARGET_SKILLS/$name"
  cp -R "$skill" "$TARGET_SKILLS/$name"
  echo "Installed $name -> $TARGET_SKILLS/$name"
done

if command -v codex >/dev/null 2>&1; then
  echo "Enabling Codex native choice UI feature..."
  codex features enable default_mode_request_user_input || true
else
  echo "codex CLI not found. Enable native choice UI manually: codex features enable default_mode_request_user_input" >&2
fi

bash "$REPO_ROOT/scripts/validate.sh"
echo "Install complete."
