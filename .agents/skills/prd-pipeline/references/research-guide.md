# PRD Pipeline Research Guide

Use this before Product Discussion. The goal is not to replace user discussion; it is to make the discussion sharper by grounding it in known facts, repository context, and explicit assumptions.

This guide borrows the useful loop from `$autoresearch`: mission -> sandbox -> result -> validator gate.

## Purpose

Before asking 12-20 product questions, identify what is already known and what must be decided by the user.

Research should produce:

- Facts that can be treated as context.
- Assumptions that must remain visibly labeled.
- Open questions that materially change the PRD.
- Product-specific gray area candidates.
- A clear verdict on whether the workflow can enter Product Discussion.

## Research Modes

| Mode | When to Use | Evidence Standard |
|---|---|---|
| `repo-context-research` | Default; user input and local repo context are enough | Inspect available local docs/code/issues and separate facts from assumptions |
| `source-backed-research` | Current external facts matter, such as compliance, platform rules, market, medical, education, finance, or competitors | Use source-backed notes and include links/citations when available |
| `assumption-declared-research` | User wants speed or says direct/auto | Continue only with explicitly labeled assumptions and risk notes |

Escalate from `repo-context-research` to `source-backed-research` when external current facts could materially change scope, safety, compliance, launch, or metrics.

## Mission

Create a short research mission before investigating:

```md
# PRD Research Mission

## Feature

## Product Question

## Key Unknowns

## Allowed Sources

## Out Of Scope

## Evidence Standard
```

## Sandbox

Record what was checked and what could not be checked:

```md
# PRD Research Sandbox

## Local Context Checked

## External Sources Checked

## Unavailable Or Unchecked Sources

## High-Risk Assumptions

## Scope Guardrails
```

## Result

The research result should be both human-readable and machine-checkable.

Recommended Markdown:

```md
# [Feature] PRD Research

## Facts

## Assumptions

## Open Questions

## Gray Area Candidates

## Risk Notes

## Discussion Readiness
```

Recommended JSON:

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

## Validator Gate

Enter Product Discussion only when:

1. A research mission exists.
2. A sandbox lists checked and unchecked context.
3. Facts and assumptions are separated.
4. At least 3 product-specific gray area candidates exist, unless the user explicitly asks for a narrow quick version.
5. `ready_for_discussion` is true, or the user explicitly chooses to continue with assumptions.

If the gate fails:

- Continue local repo inspection when local context is missing.
- Use source-backed research when current external facts matter.
- Ask the user via native structured choice UI whether to continue with assumptions.

## Do Not

- Do not turn research into full PRD writing.
- Do not hide assumptions inside facts.
- Do not ask generic UX/UI questions before the research result identifies product-specific gray areas.
- Do not browse external sources for every simple feature; use external research only when it can materially change the PRD.
