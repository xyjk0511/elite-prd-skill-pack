# Native Choice UI

`prd-pipeline` and `requirements-clarity` are designed to use Codex native structured choice UI.

## Required Codex Feature

For Codex versions that support it, enable:

```bash
codex features enable default_mode_request_user_input
```

Check feature status:

```bash
codex features list
```

You should see:

```text
default_mode_request_user_input ... true
```

## Expected Behavior

When the workflow asks a PRD discussion question, Codex should show a native choice box with 2-3 options and a client-provided Other/custom input path.

The skill intentionally does not fall back to Markdown text choices. If native UI is unavailable, the workflow should stop and report the missing capability.

## Why No Text Fallback

Plain text choices are easy to miss and easy to answer ambiguously. Native choice UI makes the decision explicit, parseable, and consistent across the PRD pipeline.
