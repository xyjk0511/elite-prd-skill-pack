# Metrics and Events Reference

Use this reference when a PRD changes user behavior, creates a funnel, or affects measurable product outcomes.

## Event Naming

Use snake_case:

```text
<feature>_<object>_<action>
<feature>_<step>_<result>
```

Examples:

```text
item_publish_entry_click
item_publish_image_upload
item_publish_submit_click
item_publish_submit_success
item_publish_submit_fail
```

## Metric Naming

Prefer two-level names:

```text
<feature>.<funnel_stage>.<metric>
<domain>.<kpi_name>
```

Examples:

```text
item_publish.entry.ctr
item_publish.submit.success_rate
item_publish.review.pass_rate
marketplace.supply.daily_new_items
```

## Success Metrics Table

```md
| 指标 | 定义 | 口径 | 目标值 | 观察周期 |
|---|---|---|---|---|
```

Include a primary metric, funnel metrics, quality metrics, guardrail metrics, and failure metrics.

## Event Tracking Table

```md
| 事件名 | 触发时机 | 事件属性 | 说明 |
|---|---|---|---|
| feature_entry_click | 用户点击入口 | user_id, source_page | 记录入口点击 |
| feature_page_view | 用户进入页面 | user_id, source_page | 记录页面曝光 |
| feature_submit_click | 用户点击提交 | user_id, item_id | 记录提交动作 |
| feature_submit_success | 提交成功 | user_id, item_id, duration_ms | 记录成功 |
| feature_submit_fail | 提交失败 | user_id, fail_reason | 记录失败原因 |
```

## Event Properties Table

```md
| 属性 | 类型 | 是否必填 | 说明 |
|---|---|---|---|
```

Always include failure reasons when the feature can fail.
