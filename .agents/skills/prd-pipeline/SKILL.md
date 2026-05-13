---
name: prd-pipeline
description: 当用户要求把一个产品想法、需求草稿、issue、会议纪要或 PRD 从“调查研究/需求讨论/澄清”一路串到“完整 PRD、PRD 审计、工程交接、QA 测试用例”时使用本总控技能；适用于全链路、端到端、从想法到研发开工、从 PRD 到 tickets/测试矩阵等场景。必须先像 autoresearch 一样建立 research mission、sandbox、result，再像 gsd-discuss-phase 一样分析产品灰区、让用户选择讨论区域、逐区追问关键决策；所有讨论问题必须使用 Codex 原生结构化选择 UI（request_user_input / AskUserQuestion），不得退回文本 1/2/3 选择题；如果当前 mode 不允许原生选择 UI，停止并提示启用 default_mode_request_user_input 或切到支持原生选择 UI 的交互模式。默认详细讨论 12-20 个问题，再调度 requirements-clarity、elite-prd-writer、prd-auditor、implementation-handoff、qa-generator。不要用于只写代码或只处理单一步骤。
---

# PRD Pipeline

## 目标

把 PRD skill-pack 的五个独立技能串成一个可执行链路：

```text
requirements-clarity
-> elite-prd-writer
-> prd-auditor
-> implementation-handoff
-> qa-generator
```

这个技能是总控入口，不直接替代子技能。它负责判断当前阶段、调用对应技能规则、维护交接包、执行 gate，并把产物落到统一目录。

默认行为是**先调查，再详细讨论，再产出**。除非用户明确说“快速版”“直接写”“不要问”“按你判断”或传入 `--auto`，否则不要从一句想法直接生成全套文档。

参考 `autoresearch` 的两段方法：

- 调查阶段：先定义 research mission、sandbox、validator，再产出 evidence-backed result。
- 完成阶段：pipeline 不能因为 Codex 说“完成”就结束，必须有明确的 completion artifact 证明通过验证。

默认讨论深度：

- 生成 3-4 个产品专属灰区。
- 推荐覆盖全部关键灰区，而不是只选一个。
- 每个灰区问 4-5 个问题。
- 总问题量目标为 12-20 个。
- 用户要求“快速版”时降到 6-8 个问题；用户要求“深入版/详细版”时保持 12-20 个问题；用户要求“极细”时可超过 20 个问题。
- 所有讨论问题都必须使用 Codex 原生结构化选择 UI。不得退回文本 1/2/3 选择题；如果 `request_user_input`、`AskUserQuestion` 或等价结构化提问工具在当前 mode 中不可调用，停止当前 pipeline，并提示用户切到 Plan mode 或启用支持原生选择 UI 的交互模式。
- 不要把“一次弹出的 3 个问题”当成完整讨论。原生 UI 每轮最多弹 3 个问题；用户回答后必须继续下一轮，直到达到当前模式的问题目标或用户明确要求停止/生成。

## 选择题交互规则

无论是选择灰区、回答产品决策、确认是否继续，都必须先判断当前客户端是否支持原生结构化选择题。

### 原生 UI 强制

必须使用当前运行环境提供的 `request_user_input`、`AskUserQuestion` 或等价结构化提问工具，而不是在聊天里打印 1/2/3 文本列表。仅检测到 Codex App 不够，必须以工具实际可调用为准；Default mode 中该工具可能不可用。

原生 UI 规则：

- 每轮提问默认 1-3 个问题；最多把 3 个强相关问题合并到同一次 UI 提问。
- 每个问题尽量提供 3 个互斥选项；只有确实不存在第三种合理路径时才用 2 个。
- Codex 客户端会自动提供 Other，所以用户看到的通常是 3 个正式选项 + Other，共 4 行。不要尝试提供 4 个正式选项；当前 `request_user_input` 工具只接受 2-3 个正式选项。
- 把推荐选项放第一位；如果工具要求，在 label 上加 `(Recommended)`。
- 不要手动添加 `其他` 选项；如果客户端会自动提供 Other，就依赖客户端自动 Other。
- 每个选项都必须有一句简短 description，说明选择后的产品含义或取舍。
- header 必须短，优先使用 12 个字符以内的中文短标题，例如“讨论范围”“训练目标”“适用人群”。
- 需要多选但当前工具不支持多选时，把选项设计成组合项，例如“全部关键灰区”“先 A+B”“先 C+D”。

## 问题数量规则

默认不是只问一轮。按模式累计问题数：

| 模式 | 累计问题数 | 典型轮数 |
|---|---:|---:|
| 快速版 | 6-8 | 2-3 轮 |
| 详细版 / 默认 | 12-20 | 4-7 轮 |
| 极细版 | 20+ | 7+ 轮 |

执行规则：

- 第一轮通常只问“讨论范围/灰区选择”，计入问题数。
- 用户选择灰区后，按灰区逐轮追问；每轮最多 3 个问题。
- 每轮结束后，如果尚未达到该模式的问题目标，不要总结生成 PRD；继续弹下一轮原生选择题。
- 只有达到问题目标，或用户明确选择“停止讨论 / 生成 PRD / 直接继续”，才进入 Requirements Packet 或后续 PRD 产出。

## Autoresearch-Style 验证契约

PRD pipeline 采用 artifact-gated completion。完成条件不是“文档已生成”，而是验证产物明确通过。

### Init: 选择验证模式

开始全流程时必须选择一个验证模式，优先用原生结构化选择 UI：

| 验证模式 | 适用场景 | 完成条件 |
|---|---|---|
| `pipeline-audit-artifact` | 默认推荐；适合多数 PRD -> handoff -> QA 流程 | PRD 审计无 P0 blocker，必需文档都存在，`pipeline-result-[feature].json` 记录 `passed: true` |
| `human-approval-artifact` | 用户或团队要先人工确认 PRD 再算完成 | 结果文件记录人工 approval，且产物路径齐全 |
| `custom-validator-script` | 团队已有自己的检查脚本或 CI 规则 | 指定 validator command 返回通过，并写入结果文件 |

如果用户没有选择，默认使用 `pipeline-audit-artifact`。

### State: 持久化运行状态

全流程落盘时，必须同时维护一个结果文件：

```text
docs/prd/pipeline-result-[feature-name].json
```

如果仓库使用 `.omx/` 状态目录，也可以额外写入：

```text
.omx/specs/prd-pipeline-[feature-name]/result.json
```

结果文件至少包含：

```json
{
  "status": "passed",
  "passed": true,
  "validation_mode": "pipeline-audit-artifact",
  "completion_artifact_path": "docs/prd/pipeline-result-feature.json",
  "artifacts": {
    "research": "docs/prd/research-feature.md",
    "research_result": "docs/prd/research-result-feature.json",
    "discussion_context": "docs/prd/context-feature.md",
    "prd": "docs/prd/prd-feature.md",
    "audit": "docs/prd/audit-feature.md",
    "handoff": "docs/handoff/handoff-feature.md",
    "qa": "docs/qa/qa-feature.md"
  },
  "audit": {
    "verdict": "可以开工",
    "p0_blockers": []
  },
  "summary": "PRD package passed pipeline validation."
}
```

### Completion: 只允许 artifact 通过后结束

不得因为以下情况声称 pipeline 完成：

- PRD 文档已经写完，但 audit / handoff / QA 缺失。
- audit 说“补充后开工”但仍有 P0 blocker。
- 只完成一轮选择题或少于当前模式的问题目标。
- 模型主观判断“应该够了”，但没有 completion artifact。
- result JSON 不存在，或 `passed` 不是 `true`。

如果验证未通过，必须回到对应步骤修复：调查缺口回 Step 0，需求讨论缺口回 Step 1，PRD 缺口回 Step 3，审计阻塞回 Step 4，handoff/QA 缺口回 Step 5/6。

## Autoresearch-Style 调查契约

产品调查不是随手搜几条资料，也不是直接问用户 20 个问题。调查阶段必须像 `$autoresearch` 一样先明确 mission、sandbox 和 validator，然后再进入讨论。

### Research Init: 选择调查模式

在生成灰区和选择题之前，先判断调查模式：

| 调查模式 | 适用场景 | 证据要求 |
|---|---|---|
| `repo-context-research` | 默认；仓库已有 README、docs、issue、历史 PRD、代码或用户输入足够 | 检查本地上下文，列出事实、假设、缺口 |
| `source-backed-research` | 涉及法规、竞品、市场、平台规则、医疗/金融/教育等当前事实 | 使用可引用来源，区分事实、推断、待确认 |
| `assumption-declared-research` | 用户要求快速、直接写、不要查太多 | 明确列出假设和风险，不伪装成事实 |

如果缺少调查模式选择，默认用 `repo-context-research`；如果需求涉及高风险或当前事实，升级到 `source-backed-research`。

### Research Artifacts

调查阶段应产出两类 artifact：

```text
docs/prd/research-[feature-name].md
docs/prd/research-result-[feature-name].json
```

如果仓库使用 `.omx/`，也可以镜像到：

```text
.omx/specs/prd-research-[feature-name]/mission.md
.omx/specs/prd-research-[feature-name]/sandbox.md
.omx/specs/prd-research-[feature-name]/result.json
```

`mission.md` 至少说明：

- 本次 PRD 要解决的产品问题。
- 需要调查的关键未知项。
- 哪些来源允许使用：用户输入、仓库文档、代码、issue、外部官方资料、竞品公开信息。
- 哪些内容不在调查范围内。
- 进入讨论前的证据标准。

`sandbox.md` 至少说明：

- 已检查的本地文件、目录或外部来源。
- 不能确认的来源或不可访问内容。
- 高风险假设。
- 不允许越界的范围，例如不要直接进入技术实现。

`result.json` 至少包含：

```json
{
  "status": "passed",
  "passed": true,
  "research_mode": "repo-context-research",
  "research_artifact_path": "docs/prd/research-feature.md",
  "facts": [],
  "assumptions": [],
  "open_questions": [],
  "gray_area_candidates": [],
  "ready_for_discussion": true,
  "validator": {
    "verdict": "passed",
    "reason": "Enough context exists to ask targeted product questions."
  }
}
```

### Research Completion Gate

只有满足以下条件，才能进入 Product Discussion：

- 已定义 research mission。
- 已列出已知事实、合理假设、关键缺口。
- 已给出 3-4 个产品专属灰区候选。
- `research-result-[feature].json` 的 `ready_for_discussion` 为 `true`，或用户明确选择带假设继续。
- 对高风险事实没有把假设写成事实。

如果调查未通过，不要进入选择题讨论；先继续查本地上下文、查外部来源，或用原生选择 UI 问用户是否允许带假设继续。

### 工具不可用时

如果原生结构化选择工具不可用：

- 不要打印文本 1/2/3 选择题。
- 不要继续生成 PRD、handoff 或 QA。
- 停止并说明阻塞原因：当前 mode 不允许原生选择 UI；需要启用 `default_mode_request_user_input` 或切到支持 `request_user_input` / `AskUserQuestion` 的交互模式后再继续。

## 适用场景

使用本技能处理：

- “从想法到 PRD、研发交接、QA 全流程跑一遍”
- “把这个需求打通到研发能开工”
- “生成 PRD + audit + handoff + QA”
- “一条龙做完产品需求链路”
- “端到端产出需求文档和测试用例”

不要处理：

- 用户只要求单一步骤。只写 PRD 用 `elite-prd-writer`；只审 PRD 用 `prd-auditor`；只拆任务用 `implementation-handoff`；只做测试用例用 `qa-generator`。
- 用户要求直接编码。
- 用户要求纯技术架构设计。

## 前置检查

开始前检查：

- `AGENTS.md`
- `README.md`
- `docs/prd/`
- `docs/handoff/`
- `docs/qa/`
- `tasks/`
- 历史 PRD、handoff、QA 文档、issue、roadmap

如果仓库已有目录和命名规则，优先遵循仓库规则。否则使用：

- Research：`docs/prd/research-[feature-name].md`
- Research Result：`docs/prd/research-result-[feature-name].json`
- PRD：`docs/prd/prd-[feature-name].md`
- Handoff：`docs/handoff/handoff-[feature-name].md`
- QA：`docs/qa/qa-[feature-name].md`

## 总控流程

### Step 0: Product Research

按 `references/research-guide.md` 执行调查前置。

目标：先把产品领域、仓库上下文、已知事实、假设、风险和调查缺口梳理清楚，再生成灰区和选择题。

流程：

1. 建立 Research Mission：说明本次 PRD 的目标、待调查问题、允许来源和证据标准。
2. 建立 Research Sandbox：记录已检查的仓库文件、用户输入、外部来源和不可确认信息。
3. 选择调查模式：`repo-context-research` / `source-backed-research` / `assumption-declared-research`。
4. 输出 Research Result：事实、假设、风险、open questions、灰区候选、是否可进入讨论。
5. 如果 `ready_for_discussion` 不是 `true`，继续调查或用原生选择 UI 问用户是否允许带假设继续。

Gate:

- `ready_for_discussion = true`：进入 Step 1。
- 用户选择带假设继续：进入 Step 1，并把高风险假设写入 `PRD Discussion Context`。
- 核心领域、目标用户、合规边界完全不可判断：停在 Step 0，输出需要补充的资料。

### Step 1: Product Discussion

按 `references/discussion-guide.md` 执行讨论前置。

目标：提取后续 PRD、审计、handoff、QA 都需要的产品决策，而不是让 Codex 自己脑补。

流程：

1. 分析用户输入，识别产品类型和边界。
2. 生成 3-4 个**当前产品专属灰区**，不要用“UI / UX / Behavior”这类泛泛标签。
3. 把灰区展示给用户，让用户用选择题选择要讨论哪些；默认推荐“讨论全部关键灰区”，不要提供“跳过”作为默认选项。
4. 对每个选中的灰区先通过原生结构化选择 UI 问 4-5 个问题，每题尽量有 3 个具体选项，并依赖客户端自动提供 Other。
5. 追问总量默认控制在 12-20 个问题；如果用户只选了 1 个灰区，也要提醒“这样问题会偏少，是否补选其他关键灰区”。
6. 每轮最多弹 3 个问题；用户回答后继续下一轮，直到当前灰区 4-5 个问题问完。
7. 每个灰区问完后用原生选择 UI 确认：“继续问这个灰区 / 进入下一个 / 汇总当前决策”。
8. 所有选中灰区讨论完后，汇总决策并询问是否准备生成 PRD。
9. 输出 `PRD Discussion Context`，作为 `Requirements Packet` 的上游输入。

灰区示例：

- 认知训练游戏：训练目标与人群、训练任务结构、单局节奏与反馈、难度递进与安全边界。
- AI 简历修改：目标用户与使用场景、输入/隐私边界、AI 输出形态、用户确认与导出路径。
- 校园二手发布：发布字段与类目、审核与风控、图片/位置/联系方式规则、发布后状态与卖家反馈。

Scope guardrail:

- 讨论澄清“这个能力怎么做”，不是扩功能。
- 用户提出新能力时，记录到“Deferred Ideas”，不要纳入当前 PRD 范围。
- 不问技术架构、具体实现方案、性能优化细节；这些交给后续 handoff 或工程设计。

Auto mode:

- 只有用户明确说“直接写”“不要问”“按你判断”或传入 `--auto` 时，才跳过互动。
- 跳过时必须输出自动假设，并标记哪些假设影响 PRD 风险。

Gate:

- 用户完成至少 12 个关键问题，或明确要求缩短/自动继续：进入 Step 2。
- 如果只完成少于 12 个问题，先提示哪些灰区仍缺决策，再询问是否继续讨论。
- 用户回答表明目标用户、核心问题或范围完全不成立：停止，输出澄清问题。

### Step 2: Requirements Clarity

按 `requirements-clarity` 的规则识别已知事实、假设、缺口和清晰度评分。

输入：`PRD Discussion Context`。

输出：`Requirements Packet`。

Gate:

- 评分 >= 85：进入 Step 3。
- 评分 70-84：带显式假设进入 Step 3，并在 PRD 中保留待确认问题。
- 评分 50-69：如果用户要求继续，可带高风险假设进入 Step 3；否则先停在澄清问题。
- 评分 < 50：停止，不生成完整 PRD，输出澄清问题和调研建议。

### Step 3: PRD Writing

按 `elite-prd-writer` 的规则生成完整 PRD。

要求：

- 使用 `Requirements Packet`。
- 明确本期范围和非本期范围。
- P0 功能必须有验收标准。
- 有状态对象时必须有状态机。
- 多角色时必须有权限矩阵。
- 行为改变型功能必须有埋点。

输出 `PRD Packet`。

Gate:

- PRD 缺 P0 验收标准、核心状态机、权限边界或范围边界：先修 PRD，再进入 Step 4。
- PRD 基本完整：进入 Step 4。

### Step 4: PRD Audit

按 `prd-auditor` 的规则评分和判断开工状态。

输出 `Audit Packet`。

Gate:

- 可以开工：进入 Step 5 和 Step 6。
- 补充后开工：若无 P0 阻塞，进入 Step 5 和 Step 6，并保留待确认问题；若有 P0 阻塞，回到 Step 3 修 PRD。
- 暂不建议开工：停止，输出阻塞项和修复建议。

### Step 5: Implementation Handoff

按 `implementation-handoff` 的规则生成工程交接。

输入：

- PRD
- `PRD Packet`
- `Audit Packet`

输出 `Handoff Packet`。

Gate:

- 如果发现 PRD 范围、状态机、权限或 P0 验收标准仍缺失，停止 handoff，回到 Step 3 或 Step 4。
- 否则进入 Step 6。

### Step 6: QA Generation

按 `qa-generator` 的规则生成测试矩阵和测试用例。

输入：

- PRD
- `PRD Packet`
- `Audit Packet`
- `Handoff Packet`（如已生成）

输出 `QA Packet`。

必须覆盖主流程、必填校验、边界值、权限失败、空状态、网络/API 失败、重复提交、状态冲突、埋点验证和回归风险。

### Step 7: Completion Validation

按 `references/pipeline-gates.md` 执行最终验证，并写入 `pipeline-result-[feature-name].json`。

必须检查：

- `PRD Discussion Context` 存在，且记录已讨论灰区和锁定决策。
- `Research Result` 存在，且 `ready_for_discussion` 为 `true` 或显式记录带假设继续。
- `Requirements Packet` 存在，且清晰度评分达到当前 gate。
- PRD 文件存在，且 P0 验收标准、范围边界、状态机、权限、字段和埋点不缺失。
- Audit 文件存在，且没有 P0 blocker。
- Handoff 文件存在，且包含任务拆解、接口/数据草案、联调计划和发布/回滚要点。
- QA 文件存在，且覆盖主流程、异常、权限、边界、状态冲突和埋点验证。
- result JSON 存在，`passed` 为 `true`。

如果仓库允许运行本技能脚本，可用：

```bash
python .agents/skills/prd-pipeline/scripts/validate_pipeline_result.py --result docs/prd/pipeline-result-[feature-name].json
```

只有验证通过后，`Pipeline Summary` 的“是否完整跑完”才能写“是”。

## 输出格式

默认输出：

```md
## Pipeline Summary

- 功能名称：
- 当前阶段：
- 产物：
- 是否完整跑完：
- 阻塞项：

## Research Packet

- research_mode:
- research_artifact_path:
- facts:
- assumptions:
- open_questions:
- ready_for_discussion:

## PRD Discussion Context

- 产品边界：
- 已讨论灰区：
- 已锁定决策：
- Claude 可自行决定：
- Deferred Ideas：

## Requirements Packet

## PRD Packet

## Audit Packet

## Handoff Packet

## QA Packet

## Completion Validation

- validation_mode:
- completion_artifact_path:
- passed:
- validator:
- remaining_blockers:

## 文件清单

| 类型 | 路径 | 状态 |
|---|---|---|

## 下一步
```

## 落盘规则

如果用户要求落盘，或当前仓库已有文档目录规范，默认创建：

```text
docs/prd/context-[feature-name].md
docs/prd/research-[feature-name].md
docs/prd/research-result-[feature-name].json
docs/prd/prd-[feature-name].md
docs/prd/audit-[feature-name].md
docs/prd/pipeline-result-[feature-name].json
docs/handoff/handoff-[feature-name].md
docs/qa/qa-[feature-name].md
```

需要确定性写入时，使用子技能自带脚本：

```bash
python .agents/skills/elite-prd-writer/scripts/save_doc.py --path docs/prd/prd-[feature-name].md < prd.md
python .agents/skills/implementation-handoff/scripts/save_doc.py --path docs/handoff/handoff-[feature-name].md < handoff.md
```

QA 文档可直接由 Codex 写入目标 Markdown 文件；若仓库有更具体脚本，优先用仓库脚本。

最终必须写入 completion artifact；没有 result JSON 时，只能报告“文档已生成但 pipeline 未验证完成”。

## 失败与回退

- 用户还没讨论关键灰区：不要生成完整文档，先问。
- 调查未通过：不要进入 PRD 讨论，先补 research mission / sandbox / result。
- 详细模式下讨论少于 12 个问题：不要直接进入文档产出，先提示未覆盖灰区。
- 需求不清：停在 Step 2，不假装已完成 PRD。
- PRD 不完整：回到 Step 3 修 PRD。
- 审计不通过：停在 Step 4，输出阻塞项。
- handoff 发现需求缺口：回到 Step 3 或 Step 4。
- QA 无法生成关键用例：回到 Step 3 补验收标准、状态机、权限或字段规则。
- completion artifact 不存在或未通过：不要声称 pipeline 完成，先修复缺失产物或阻塞项。

## 严格禁止

- 不要在用户没有选择讨论灰区、也没有明确要求自动模式时，从一句想法直接生成全套文档。
- 不要跳过 gate 强行生成后续产物。
- 不要把待确认问题当作已确认需求。
- 不要在 pipeline 里直接开始编码。
- 不要只输出 happy path。
- 不要在 PRD 未通过审计时声称研发可开工。
- 不要在缺少 completion artifact 时声称全流程完成。
