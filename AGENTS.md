# AGENTS.md

This repository packages Codex skills for PRD workflows.

## Rules

- Keep skill source under `.agents/skills/`.
- Do not commit machine-local paths, API keys, tokens, cookies, or personal Codex config.
- Validate all skills after edits with `scripts/validate.ps1` or `scripts/validate.sh`.
- PRD discussion skills must use native structured choice UI when asking users to decide scope or requirements.
- Do not add a text `1/2/3` fallback for `prd-pipeline` or `requirements-clarity`.

## Release Checklist

1. Run validation scripts.
2. Search for secrets and local paths.
3. Confirm install scripts copy all skills.
4. Confirm README examples match skill names.
