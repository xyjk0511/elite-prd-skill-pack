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

When the workflow asks PRD discussion questions, Codex should show a native choice box.

Default detailed discussion is cumulative:

- Fast mode: 6-8 total questions.
- Detailed/default mode: 12-20 total questions.
- Exhaustive mode: 20+ total questions when the user explicitly asks for deep discussion.

One native UI round can contain up to 3 questions. A full detailed discussion normally takes 4-7 rounds; one popup with 3 questions is not enough to finish the pipeline discussion.

Each question should provide 3 formal options when possible. Codex adds the Other/custom input row automatically, so the user typically sees 4 visible rows: 3 formal options plus Other.

Do not provide 4 formal options manually. The current `request_user_input` schema accepts 2-3 formal options, then the client adds Other.

The skill intentionally does not fall back to Markdown text choices. If native UI is unavailable, the workflow should stop and report the missing capability.

## Why No Text Fallback

Plain text choices are easy to miss and easy to answer ambiguously. Native choice UI makes the decision explicit, parseable, and consistent across the PRD pipeline.
