# PRD Pipeline Discussion Guide

Use this before generating PRD artifacts unless the user explicitly asks to skip discussion.

## Purpose

Capture product decisions that downstream PRD, audit, handoff, and QA steps need. The user is the visionary; Codex is the builder. Ask about product vision, behavior, UX, content, boundaries, data policy, and acceptance expectations. Do not ask about technical architecture or implementation details.

## Process

1. Identify the product domain from the user's request.
2. Generate 3-4 domain-specific gray areas.
3. Present those gray areas with the native structured question UI. Do not use text 1/2/3 fallback. Recommend discussing all critical areas for full PRD quality.
4. For each selected area, ask 4-5 concrete multiple-choice questions, again preferring native structured UI.
5. Target 12-20 questions total in the default detailed mode.
6. Ask at most 3 questions per native UI round; after the user answers, continue with the next round until the mode's question target is reached.
7. After each area, ask whether to continue that area or move to the next using a native choice control question.
8. Summarize decisions into `PRD Discussion Context`.
9. Ask whether to generate the PRD package now using a native choice control question.

## Discussion Depth

Default to detailed mode unless the user explicitly asks otherwise.

| Mode | When to Use | Question Target |
|---|---|---:|
| Quick | User says “快速版”, “少问点”, or wants a lightweight brief | 6-8 |
| Detailed | Default for `prd-pipeline`; user wants full PRD / handoff / QA | 12-20 |
| Exhaustive | User says “极细”, “多问”, “深挖” | 20+ |

In detailed mode, cover at least 3 gray areas when possible. If the user selects only 1 area, explain that the resulting PRD will be under-specified and ask whether to include the other critical areas.

Native UI rounds are not the same as total question count:

- A native UI round may contain 1-3 questions.
- A default detailed discussion usually needs 4-7 rounds to reach 12-20 total questions.
- Do not stop after the first 3 questions unless the user explicitly asks to stop or continue with assumptions.

## Gray Area Identification

Gray areas are product decisions that could go multiple ways and materially change the PRD.

Avoid generic labels such as UI, UX, Behavior. Use product-specific labels.

Examples:

### Cognitive Training Game

- 训练目标与适用人群：面向儿童、成人、康复用户还是普通训练？训练注意力、工作记忆、抑制控制还是综合能力？
- 训练任务结构：N-back、Go/No-Go、Stroop、颜色干扰、反应时任务如何组合？
- 单局节奏与反馈：每局多长、多少轮、是否即时反馈、是否有奖励和趋势页？
- 难度递进与安全边界：如何调难度、失败时如何降级、哪些医疗/诊断表述要排除？

### AI Resume Rewriter

- 目标用户与场景：应届生、转岗、资深候选人、内部 HR 工具？
- 输入与隐私：粘贴文本、上传文件、是否保存原文、是否记录修改历史？
- AI 输出形态：诊断建议、逐句改写、完整新版本、岗位匹配建议？
- 用户确认与导出：采纳、复制、导出、版本对比、人工确认边界？

### Marketplace Item Publishing

- 发布字段与类目：标题、描述、价格、成色、类目、地点、联系方式。
- 图片与内容规则：图片数量、大小、违规内容、敏感词、缺图状态。
- 审核与风控：人工审核、机器审核、发布频次、违规处理。
- 发布后状态：草稿、待审核、已发布、已拒绝、下架、删除。

## Native Choice UI Rule

All discussion questions must be multiple-choice. Do not ask pure open-ended questions.

Use native structured question UI whenever the runtime exposes and permits a tool such as `request_user_input`, `AskUserQuestion`, or an equivalent picker. Do not print a Markdown numbered list. Codex App alone is not enough; the tool must be callable in the current mode. If it is not callable, stop the pipeline and report that native choice UI must be enabled first.

Native UI rules:

- Ask 1 question per round by default.
- Ask at most 3 closely related questions in one structured UI call.
- Provide 3 mutually exclusive options per question whenever possible. Use 2 only when there is no meaningful third path.
- The Codex client automatically adds Other/custom input, so 3 provided options appear to the user as 4 visible rows. Do not attempt to provide 4 formal options; `request_user_input` accepts 2-3 provided options.
- Put the recommended option first and label it as recommended when the tool convention requires it.
- Provide a short description for every option, explaining the product implication.
- Do not manually add `Other` if the client automatically provides Other.
- Keep question headers short, ideally <= 12 characters.
- If multi-select is needed but unsupported, encode common combinations as options.

Use this native shape conceptually:

```text
header: 讨论范围
question: 这次 PRD 讨论范围怎么选？
options:
  - 全部关键灰区 (Recommended): 适合完整 PRD、handoff 和 QA。
  - 先做 MVP 核心: 先锁定最小可上线范围。
  - 先做合规安全: 先处理高风险边界。
Other: client-provided
```

## Tool Unavailable Rule

When native structured question UI is unavailable or blocked in the current mode:

- Do not print text 1/2/3 choice lists.
- Do not continue to PRD generation.
- Stop and explain that `default_mode_request_user_input` or another native choice UI mode is required.

Rules:

- Use 2-3 options by default.
- Do not manually add an Other option when the client provides Other automatically.
- If multiple answers are allowed, say `可多选` in the question.
- Make each option concrete enough that the downstream PRD would change based on the answer.
- When the user chooses `其他`, summarize their free-form answer into a concrete decision before continuing.
- Control questions must also be multiple-choice, for example:

```text
这个灰区下一步怎么处理？
Use native structured UI options:
- 继续追问这个灰区
- 进入下一个灰区
- 汇总当前决策并生成 PRD
Other: client-provided
```

Good:

```text
这个认知训练游戏的首期训练目标更偏哪一个？
Use native structured UI options:
- 注意力维持：训练持续专注和抗干扰能力
- 工作记忆：训练短时记忆、更新和回忆
- 抑制控制：训练冲动抑制和反应控制
Other: client-provided
```

Bad:

```text
你想要什么体验？
```

## Detailed Question Batch Template

For each gray area, ask 4-5 questions like:

1. Primary decision: Which direction should this area take? Use 3 concrete choices plus client-provided Other.
2. Boundary decision: What is explicitly out of scope? Use 3 scope choices plus client-provided Other.
3. State/flow decision: What should happen before, during, after? Use 3 flow choices plus client-provided Other.
4. Acceptance decision: What would make this area count as working? Use 3 acceptance choices plus client-provided Other.
5. Edge decision: What failure, exception, or misuse case must be handled? Use 3 edge-case choices plus client-provided Other.

Then ask:

```text
这个灰区下一步怎么处理？
Use native structured UI options:
- 继续追问这个灰区
- 进入下一个灰区
- 汇总当前决策并生成 PRD
Other: client-provided
```

## Question Coverage

Across the full discussion, cover these categories when relevant:

1. Target users and usage context.
2. Core problem and product promise.
3. In-scope capability boundary.
4. Explicit out-of-scope items.
5. Main user flow.
6. Branch flows and alternate paths.
7. Object states and state transitions.
8. Roles and permission boundaries.
9. Required fields and data constraints.
10. Empty, loading, error, and disabled states.
11. Failure handling and retry rules.
12. Abuse, safety, privacy, or compliance boundaries.
13. Success metrics and guardrail metrics.
14. Event tracking and funnel points.
15. Launch, rollback, and support needs.
16. Acceptance criteria for P0 behaviors.

## PRD Discussion Context

```md
## PRD Discussion Context

### Product Boundary

### Discussed Gray Areas

### Locked Decisions

### Claude's Discretion

### Deferred Ideas

### Open Questions
```

## Scope Guardrail

If the user suggests a new capability:

```text
这个能力可以作为后续阶段，我会记到 Deferred Ideas。当前先聚焦：[当前产品边界]。
```

Do not lose deferred ideas, but do not include them in current scope.
