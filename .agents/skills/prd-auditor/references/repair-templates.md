# PRD Repair Templates

Use these snippets when an audit finds missing sections.

## Out-of-Scope Repair

```md
## 非本期范围

| 项目 | 不做原因 | 后续处理 |
|---|---|---|
|  |  |  |
```

## State Machine Repair

```md
## 状态定义

| 状态 | 含义 | 用户可见 | 可操作项 | 进入条件 | 退出条件 |
|---|---|---|---|---|---|

## 状态流转规则

| 当前状态 | 触发动作 | 下一个状态 | 操作人 | 系统处理 |
|---|---|---|---|---|
```

## Acceptance Criteria Repair

```md
### AC-001 正常完成主流程

Given 用户已登录并满足前置条件
When 用户完成必要操作并提交
Then 系统应成功创建记录，并展示成功反馈

### AC-002 权限不足

Given 用户不具备该操作权限
When 用户访问入口或调用相关接口
Then 系统应阻止操作，并展示权限不足提示；后端必须拒绝请求
```

## Analytics Repair

```md
| 事件名 | 触发时机 | 事件属性 | 说明 |
|---|---|---|---|
| feature_entry_click | 用户点击入口 | user_id, source_page | 记录入口点击 |
| feature_submit_success | 提交成功 | user_id, duration_ms | 记录成功 |
| feature_submit_fail | 提交失败 | user_id, fail_reason | 记录失败原因 |
```
