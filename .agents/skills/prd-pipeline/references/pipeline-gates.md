# PRD Pipeline Gates

Use these gates to decide whether to continue, stop, or return to an earlier stage.

## Stage Gates

| Stage | Continue When | Stop / Return When |
|---|---|---|
| Product research | Research mission, sandbox, facts/assumptions, gray area candidates, and research result are available | Research cannot separate facts from assumptions, or no product-specific gray areas can be produced |
| Product discussion | Required question target is met, ambiguity score passes, and non-goals / decision boundaries / locked decisions are present | User has not discussed any gray area, native UI is unavailable, ambiguity score is too low, or required sections are missing |
| Requirements clarity | Clarity score >= 85, or 70-84 with explicit assumptions | Score < 50, or core target user/problem/scope missing |
| PRD writing | Scope, P0 requirements, state, permission, fields, analytics, and acceptance criteria are present | Missing P0 acceptance criteria, scope boundary, state machine, or permissions |
| PRD audit | Audit says “可以开工” or “补充后开工” without P0 blockers | Audit says “暂不建议开工” or has P0 blockers |
| Handoff | PRD and audit packets are available, implementation blockers are explicit | Handoff exposes missing product decisions |
| QA generation | PRD has testable acceptance criteria and enough state/permission/field rules | QA cannot cover P0 paths due to missing PRD details |
| Integrated delivery | Integrated Markdown exists; DOCX exists when requested or declared in result JSON | Integrated source paths are missing, DOCX export fails, or DOCX is treated as the only source of truth |

## Required Packets

```text
Research Packet -> PRD Discussion Context -> Pipeline State -> Requirements Packet -> PRD Packet -> Audit Packet -> Handoff Packet -> QA Packet -> Integrated Delivery Package
```

Each packet should preserve paths, scope, blockers, and next-step status.

## Autoresearch-Style Completion Gate

The pipeline is not complete until a completion artifact exists and passes validation. Do not treat a generated PRD, model confidence, or a one-time stop condition as completion evidence.

## Validation Modes

| Mode | Use When | Required Completion Evidence |
|---|---|---|
| `pipeline-audit-artifact` | Default mode for normal PRD packages | `pipeline-result-[feature].json` has `passed: true`, required artifact paths, audit verdict, and no P0 blockers |
| `human-approval-artifact` | A human stakeholder must approve before downstream work | Result JSON records an explicit approval verdict and required artifact paths |
| `custom-validator-script` | The repository has a deterministic validator or CI check | Result JSON records the validator command and a passing validator result |

## Research Artifact Schema

Recommended paths:

```text
docs/prd/research-[feature-name].md
docs/prd/research-result-[feature-name].json
```

Minimum JSON shape:

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

Research fails the gate when `ready_for_discussion` is not true and the user has not explicitly chosen to continue with assumptions.

## Completion Artifact Schema

Recommended path:

```text
docs/prd/pipeline-result-[feature-name].json
```

Minimum shape:

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
    "pipeline_state": "docs/prd/pipeline-state-feature.json",
    "prd": "docs/prd/prd-feature.md",
    "audit": "docs/prd/audit-feature.md",
    "handoff": "docs/handoff/handoff-feature.md",
    "qa": "docs/qa/qa-feature.md",
    "integrated_markdown": "docs/prd/prd-handoff-package-feature.md",
    "integrated_docx": "docs/prd/prd-handoff-package-feature.docx"
  },
  "discussion": {
    "mode": "detailed",
    "question_count": 14,
    "ambiguity_score": 88,
    "continue_with_assumptions": false,
    "required_sections": {
      "non_goals": true,
      "decision_boundaries": true,
      "locked_decisions": true
    }
  },
  "audit": {
    "verdict": "可以开工",
    "p0_blockers": []
  },
  "summary": "PRD package passed pipeline validation."
}
```

## Pipeline State Schema

Recommended path:

```text
docs/prd/pipeline-state-[feature-name].json
```

Minimum shape:

```json
{
  "feature": "feature",
  "current_stage": "validated",
  "validation_mode": "pipeline-audit-artifact",
  "question_count": 14,
  "ambiguity_score": 88,
  "loop_counts": {
    "audit_to_prd": 1
  },
  "return_to_prd_reason": "",
  "stages": {
    "product_research": {"status": "passed"},
    "product_discussion": {"status": "passed"},
    "requirements_clarity": {"status": "passed"},
    "prd_writing": {"status": "passed"},
    "prd_audit": {"status": "passed"},
    "implementation_handoff": {"status": "passed"},
    "qa_generation": {"status": "passed"},
    "integrated_delivery": {"status": "passed"},
    "completion_validation": {"status": "passed"}
  }
}
```

Resume rule: if the state file exists and `current_stage` is not `validated`, resume from the earliest stage whose status is not `passed` / `completed` / `validated`.

Audit loop rule: if audit has P0 blockers, set `current_stage` to `prd_writing`, fill `return_to_prd_reason`, increment `loop_counts.audit_to_prd`, and regenerate PRD before re-auditing. Stop with diagnosis when `audit_to_prd` exceeds 3.

For `human-approval-artifact`, include:

```json
{
  "approval": {
    "verdict": "approved",
    "source": "user",
    "summary": "Approved for implementation handoff."
  }
}
```

For `custom-validator-script`, include:

```json
{
  "validator": {
    "command": "python scripts/check_prd_package.py docs/prd/pipeline-result-feature.json",
    "status": "passed",
    "passed": true
  }
}
```

## Final Stop Rule

Only stop with “complete” when:

1. Required Markdown artifacts exist.
2. The result JSON exists.
3. The research result exists and is discussion-ready.
4. The pipeline state exists and is at `validated`.
5. The discussion metadata passes question-count, ambiguity-score, and required-section gates.
6. Any declared integrated Markdown or DOCX artifact exists.
7. `passed` is `true`.
8. The selected validation mode's required evidence is present.
9. No P0 blockers remain.

If any item fails, return to the earliest stage that can repair the missing evidence.
