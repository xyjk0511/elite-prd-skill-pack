---
name: implementation-handoff
description: 当用户明确要求基于已批准 PRD 生成工程交接、开发计划、任务拆解、tickets、API stub、数据对象草案、联调计划、发布计划或实现前交接文档时使用本技能；输入应是已有 PRD 或明确需求基线。不要用于从零写 PRD、需求澄清、PRD 审计、直接编码或生成 QA 全量用例。
---

# Implementation Handoff

## 目标

把已批准或基本稳定的 PRD 转成设计、前端、后端、数据、QA 可以执行和联调的工程交接文档。

完成标准：

- 保持产品需求和技术实现的边界。
- 输出任务拆解、建议 tickets、接口/数据对象草案、联调计划和发布关注点。
- 不伪造具体代码文件，除非已经检查仓库。
- 标出仍会阻塞实现的待确认问题。

## 前置条件

进入本技能前应满足：

- 对应 PRD 已存在或用户提供了完整需求基线。
- `prd-auditor` 已给出可以进入 handoff，或用户明确要求跳过审计。
- 范围与非范围已明确。
- 核心状态机已明确。
- 权限边界已明确。
- 待确认问题不阻塞当前实现。

如果不满足，先改用 `requirements-clarity` 或 `prd-auditor`。

## 工作流程

1. 读取 PRD 和仓库 `AGENTS.md`。
2. 读取 `PRD Packet` 和 `Audit Packet`；缺失时从 PRD 正文提取并标记不确定项。
3. 检查是否有现有架构、API、任务和文档规范。
4. 按 `references/handoff-template.md` 输出工程交接。
5. 需要 API 或数据对象草案时读取 `references/api-stub-template.md`。
6. 输出 `Handoff Packet`，供联调和 `qa-generator` 使用。
7. 如果用户要求落盘，默认保存到 `docs/handoff/handoff-[feature-name].md`。

## 输出必须包含

- 需求来源。
- 功能拆解。
- 前端任务。
- 后端任务。
- 数据任务。
- 测试任务。
- Suggested tickets。
- API / 数据对象草案。
- 联调计划。
- 发布与回滚要点。
- 风险与待确认问题。

## 脚本

需要确定性写文件时，使用 `scripts/save_doc.py`：

```bash
python .agents/skills/implementation-handoff/scripts/save_doc.py --path docs/handoff/handoff-[feature-name].md < handoff.md
```

## Handoff Packet

```md
## Handoff Packet

- handoff 文件路径：
- 需求来源 PRD：
- 模块拆解：
- Suggested tickets：
- API / 数据对象草案：
- 联调计划：
- 发布与回滚要点：
- 实现待确认问题：
```

## 与其他技能的衔接

- 输入应来自 `prd-auditor` 通过后的 PRD。
- 输出的 `Handoff Packet` 可交给 `qa-generator` 补充联调用例和回归矩阵。
- 如果发现 PRD 范围、状态机、权限或 P0 验收标准缺失，停止拆任务并回到 `prd-auditor` 或 `elite-prd-writer`。

## 严格禁止

- 不要在 PRD 未稳定时强行拆任务。
- 不要把内部实现写成唯一方案，除非仓库架构已约束。
- 不要伪造具体源码路径、函数名或现有接口。
- 不要直接编码；本技能只做工程交接。
