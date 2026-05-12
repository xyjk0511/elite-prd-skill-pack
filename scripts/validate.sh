#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-"$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"}"
SKILLS_DIR="$ROOT/.agents/skills"

if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "Missing skills directory: $SKILLS_DIR" >&2
  exit 1
fi

found=0
for skill in "$SKILLS_DIR"/*; do
  [[ -d "$skill" ]] || continue
  found=1
  skill_file="$skill/SKILL.md"
  if [[ ! -f "$skill_file" ]]; then
    echo "Missing SKILL.md for $(basename "$skill")" >&2
    exit 1
  fi
  if ! grep -q '^---' "$skill_file" || ! grep -q '^name:' "$skill_file" || ! grep -q '^description:' "$skill_file"; then
    echo "Invalid frontmatter in $skill_file" >&2
    exit 1
  fi
  echo "Valid: $(basename "$skill")"
done

if [[ "$found" -eq 0 ]]; then
  echo "No skills found under: $SKILLS_DIR" >&2
  exit 1
fi

echo "All skills valid."
