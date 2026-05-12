---
name: qa-generator
description: 当用户明确要求基于 PRD、产品规格、功能需求或验收标准生成 QA 测试矩阵、测试用例、回归清单、边界用例、权限用例、状态流转用例或埋点验证用例时使用本技能。输入应是已有 PRD 或稳定需求。不要用于从零写 PRD、需求澄清、PRD 审计、开发任务拆解或直接编码。
---

# QA Generator

## 目标

把稳定 PRD 转成 QA 可以执行的测试设计、测试矩阵和高优先级测试用例。

完成标准：

- 覆盖主流程、反向流程、边界、权限、状态冲突、失败恢复和埋点验证。
- 每条用例有前置条件、步骤、预期结果和优先级。
- 标出 PRD 中阻碍测试设计的缺口。

## 前置条件

输入应是已有 PRD、产品规格、验收标准或稳定需求基线。

如果需求仍模糊，改用 `requirements-clarity`。如果 PRD 是否可开工不明确，改用 `prd-auditor`。如果已有 `Handoff Packet`，优先结合 handoff 中的模块、tickets、API 草案和联调计划生成测试覆盖。

## 工作流程

1. 读取 PRD 和仓库测试/文档约定。
2. 读取 `PRD Packet`、`Audit Packet` 和可用的 `Handoff Packet`；缺失时从 PRD 正文提取。
3. 提取功能、角色、状态机、字段规则、异常场景、埋点要求。
4. 按 `references/qa-template.md` 输出测试矩阵和测试用例。
5. 输出 `QA Packet`。
6. 如果 PRD 缺少必要测试依据，列为阻塞或待确认问题。
7. 用户要求落盘时，默认建议 `docs/qa/qa-[feature-name].md`。

## 必须覆盖

- Positive cases。
- Negative cases。
- Required field validation。
- Boundary values。
- Permission failures。
- Empty states。
- Network/API failures。
- Duplicate submission。
- State conflicts。
- Data consistency。
- Compatibility。
- Analytics verification。
- Regression risks。

## 输出格式

使用 `references/qa-template.md`。若用户只要简版，至少输出高优先级用例表。

## QA Packet

```md
## QA Packet

- QA 文件路径：
- 需求来源 PRD：
- 来源 handoff：
- 测试矩阵：
- P0 测试用例：
- 回归清单：
- 埋点验证清单：
- 测试阻塞项：
```

## 与其他技能的衔接

- 如果 `prd-auditor` 不允许进入 QA，先回到 `elite-prd-writer` 修 PRD。
- 如果 handoff 已存在，QA 输出必须覆盖 handoff 中的模块、tickets、API 草案和联调计划。
- 如果发现验收标准、状态流转、权限或字段规则缺失，应列为测试阻塞项，并建议回到 `prd-auditor`。

## 严格禁止

- 不要凭空补造 PRD 中不存在的核心业务规则；应标为待确认。
- 不要只覆盖 happy path。
- 不要遗漏权限、异常、状态和埋点验证。
- 不要直接修改代码或测试文件，除非用户明确要求实现测试。
