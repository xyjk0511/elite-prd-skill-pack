# Elite PRD Skill Pack for Codex

一套面向 Codex 的产品需求工作流技能包，用于把产品想法从调查研究推进到需求讨论、PRD、审计、工程交接和 QA 测试设计。

## What It Includes

| Skill | Purpose |
|---|---|
| `prd-pipeline` | 总控入口：调查研究 -> 需求讨论 -> 澄清 -> PRD -> 审计 -> 工程交接 -> QA |
| `requirements-clarity` | 模糊需求澄清，输出清晰度评分和 Requirements Packet |
| `elite-prd-writer` | 创建、重写、补全完整 PRD |
| `prd-auditor` | 审计 PRD 是否达到设计、研发、测试开工标准 |
| `implementation-handoff` | 基于已批准 PRD 生成工程交接、tickets、API 草案和联调计划 |
| `qa-generator` | 基于 PRD / handoff 生成测试矩阵、测试用例和回归清单 |

## Key Behavior

`prd-pipeline` 和 `requirements-clarity` 默认不直接脑补 PRD。`prd-pipeline` 会先按 `$autoresearch` 的方法建立 research mission、sandbox 和 result，确认已知事实、假设和调查缺口，再识别 3-4 个产品专属灰区，并通过 Codex 原生结构化选择 UI 让用户点选决策。

This pack is intentionally strict:

- It requires native structured choice UI such as `request_user_input` / `AskUserQuestion`.
- It does not fall back to plain text `1/2/3` choice lists.
- If native choice UI is unavailable, the workflow should stop and ask the user to enable it.
- Investigation is mission-gated, inspired by `$autoresearch`: before discussion, the pipeline should produce `docs/prd/research-[feature].md` and `docs/prd/research-result-[feature].json`.
- Research modes are `repo-context-research`, `source-backed-research`, and `assumption-declared-research`.
- Default detailed discussion asks 12-20 cumulative questions across multiple native UI rounds, not just one popup.
- One native UI round can contain up to 3 questions; the workflow should continue asking follow-up rounds until the selected discussion depth is complete.
- Each question should provide 3 formal options when possible. Codex adds the Other/custom input row automatically, so users typically see 4 visible rows.
- Do not provide 4 formal options manually: the current `request_user_input` schema accepts 2-3 formal options, then the client adds Other.
- Discussion is ambiguity-gated, inspired by `$deep-interview`: question count alone is not enough. The pipeline tracks a 100-point ambiguity score and requires non-goals, decision boundaries, and locked decisions before PRD writing.
- The pipeline is resumable: it should maintain `docs/prd/pipeline-state-[feature].json` and continue from the earliest incomplete stage instead of restarting.
- Audit is a loop, not a terminal comment. P0 audit blockers return to PRD writing with `return_to_prd_reason`; repeated blockers stop with a diagnosis instead of silently continuing.
- Full delivery can include an integrated review Word file: `docs/prd/prd-handoff-package-[feature].docx`. The Markdown package remains the source of truth; DOCX is a derived review/share artifact.
- Completion is artifact-gated, inspired by `$autoresearch`: the full pipeline should write `docs/prd/pipeline-result-[feature].json` and only report complete when that result records `passed: true`.
- The default validation mode is `pipeline-audit-artifact`; advanced teams can use `human-approval-artifact` or `custom-validator-script`.

## Install

### Windows PowerShell

```powershell
git clone https://github.com/xyjk0511/elite-prd-skill-pack.git
cd elite-prd-skill-pack
.\scripts\install.ps1
```

### macOS / Linux

```bash
git clone https://github.com/xyjk0511/elite-prd-skill-pack.git
cd elite-prd-skill-pack
bash scripts/install.sh
```

The installer copies skills to:

```text
$CODEX_HOME/skills
```

If `CODEX_HOME` is not set, it uses:

- Windows: `%USERPROFILE%\.codex`
- macOS / Linux: `$HOME/.codex`

The installer also tries to run:

```bash
codex features enable default_mode_request_user_input
```

This enables native choice prompts in Default mode when the installed Codex version supports it.

## Validate

```powershell
.\scripts\validate.ps1
```

or:

```bash
bash scripts/validate.sh
```

Validation checks that each skill has a `SKILL.md` with required frontmatter fields.

To validate a generated PRD pipeline result:

```bash
python .agents/skills/prd-pipeline/scripts/validate_pipeline_result.py --result docs/prd/pipeline-result-item-publishing.json
```

The pipeline result validator also checks that the research artifact and research result exist, that `ready_for_discussion` is true, that pipeline state reached `validated`, and that discussion metadata passes the question-count and ambiguity-score gates.

To build an integrated Word file from generated Markdown artifacts:

```bash
python .agents/skills/prd-pipeline/scripts/build_integrated_docx.py \
  --output docs/prd/prd-handoff-package-item-publishing.docx \
  --title "商品发布功能 PRD Handoff Package" \
  --part "PRD=docs/prd/prd-item-publishing.md" \
  --part "Engineering Handoff=docs/handoff/handoff-item-publishing.md" \
  --part "QA Test Design=docs/qa/qa-item-publishing.md"
```

## Usage

Start from the full pipeline:

```text
$prd-pipeline 我想做一个校园二手交易平台的商品发布功能
```

For focused tasks:

```text
$requirements-clarity 我想做一个认知训练游戏，但需求还很模糊
$elite-prd-writer 帮我写完整 PRD
$prd-auditor 审查 docs/prd/prd-item-publishing.md
$implementation-handoff 基于 PRD 生成工程交接和 tickets
$qa-generator 根据 PRD 生成测试矩阵
```

## Recommended Repository Layout

If the target project has no existing convention, generated artifacts should use:

```text
docs/prd/
docs/handoff/
docs/qa/
tasks/
```

## Notes

- Skill format follows Codex / Agent Skills conventions: every skill is a directory containing `SKILL.md`.
- `agents/openai.yaml` files are included where useful to control implicit invocation.
- Scripts are local-only and do not call external services, except the installer optionally invoking the local `codex` CLI to enable the UI feature.

## License

MIT
