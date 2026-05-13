#!/usr/bin/env python3
"""Validate a PRD pipeline completion artifact.

The script intentionally checks only deterministic completion evidence:
JSON shape, selected validation mode, referenced artifact paths, and blocker
status. It does not judge PRD quality by itself; the audit artifact owns that.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_ARTIFACTS = (
    "research",
    "research_result",
    "discussion_context",
    "pipeline_state",
    "prd",
    "audit",
    "handoff",
    "qa",
)
VALIDATION_MODES = {
    "pipeline-audit-artifact",
    "human-approval-artifact",
    "custom-validator-script",
}
REQUIRED_STAGES = (
    "product_research",
    "product_discussion",
    "requirements_clarity",
    "prd_writing",
    "prd_audit",
    "implementation_handoff",
    "qa_generation",
    "completion_validation",
)
COMPLETE_STATUSES = {"passed", "complete", "completed", "validated"}
VALIDATED_STAGES = {"validated", "complete", "completed"}
DISCUSSION_MIN_QUESTIONS = {
    "quick": 6,
    "detailed": 12,
    "default": 12,
    "exhaustive": 20,
}
REQUIRED_DISCUSSION_SECTIONS = (
    "non_goals",
    "decision_boundaries",
    "locked_decisions",
)


def fail(code: str, message: str, **extra: Any) -> int:
    payload = {"ok": False, "code": code, "message": message, **extra}
    print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
    return 1


def ok(result_path: Path, data: dict[str, Any]) -> int:
    payload = {
        "ok": True,
        "path": str(result_path),
        "validation_mode": data.get("validation_mode"),
        "status": data.get("status"),
        "passed": data.get("passed"),
    }
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("top-level JSON value must be an object")
    return data


def resolve_artifact(base_dir: Path, artifact_path: str) -> Path:
    path = Path(artifact_path)
    if not path.is_absolute():
        path = base_dir / path
    return path


def validate_discussion(data: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    discussion = data.get("discussion")
    if not isinstance(discussion, dict):
        return "discussion object is required", {}

    mode = str(discussion.get("mode", "detailed")).strip().lower()
    min_questions = DISCUSSION_MIN_QUESTIONS.get(mode, 12)

    question_count = discussion.get("question_count")
    if not isinstance(question_count, int) or question_count < 0:
        return "discussion.question_count must be a non-negative integer", discussion

    ambiguity_score = discussion.get("ambiguity_score")
    if not isinstance(ambiguity_score, int) or not 0 <= ambiguity_score <= 100:
        return "discussion.ambiguity_score must be an integer from 0 to 100", discussion

    continue_with_assumptions = discussion.get("continue_with_assumptions") is True
    if question_count < min_questions and not continue_with_assumptions:
        return (
            "discussion.question_count is below the minimum for the selected mode "
            "and continue_with_assumptions is not true"
        ), discussion

    if ambiguity_score < 85:
        if not continue_with_assumptions or ambiguity_score < 70:
            return (
                "discussion.ambiguity_score must be >=85, or >=70 with "
                "continue_with_assumptions=true"
            ), discussion

    required_sections = discussion.get("required_sections")
    if not isinstance(required_sections, dict):
        return "discussion.required_sections must be an object", discussion
    missing_sections = [
        key for key in REQUIRED_DISCUSSION_SECTIONS if required_sections.get(key) is not True
    ]
    if missing_sections:
        return "discussion required sections are not confirmed: " + ", ".join(missing_sections), discussion

    return None, discussion


def validate_pipeline_state(state_path: Path) -> tuple[str | None, dict[str, Any]]:
    try:
        state = load_json(state_path)
    except ValueError as exc:
        return str(exc), {}

    current_stage = str(state.get("current_stage", "")).strip()
    if current_stage not in VALIDATED_STAGES:
        return "pipeline_state.current_stage must be validated for a passed result", state

    stages = state.get("stages")
    if not isinstance(stages, dict):
        return "pipeline_state.stages must be an object", state

    incomplete = []
    for stage in REQUIRED_STAGES:
        entry = stages.get(stage)
        status = entry.get("status") if isinstance(entry, dict) else None
        if status not in COMPLETE_STATUSES:
            incomplete.append({"stage": stage, "status": status})
    if incomplete:
        return "pipeline_state has incomplete required stages", {"incomplete": incomplete}

    loop_counts = state.get("loop_counts", {})
    if loop_counts is not None and not isinstance(loop_counts, dict):
        return "pipeline_state.loop_counts must be an object", state
    audit_loops = (loop_counts or {}).get("audit_to_prd", 0)
    if not isinstance(audit_loops, int) or audit_loops < 0:
        return "pipeline_state.loop_counts.audit_to_prd must be a non-negative integer", state
    if audit_loops > 3:
        return "pipeline_state.loop_counts.audit_to_prd exceeds the maximum of 3", state

    if str(state.get("return_to_prd_reason", "")).strip():
        return "pipeline_state.return_to_prd_reason must be empty after validation passes", state

    return None, state


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate docs/prd/pipeline-result-[feature].json"
    )
    parser.add_argument("--result", required=True, help="Path to pipeline result JSON")
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root used to resolve relative artifact paths",
    )
    args = parser.parse_args()

    result_path = Path(args.result)
    root = Path(args.root)
    if not result_path.exists():
        return fail("missing_result", f"result file does not exist: {result_path}")

    try:
        data = load_json(result_path)
    except ValueError as exc:
        return fail("invalid_result_json", str(exc))

    mode = data.get("validation_mode")
    if mode not in VALIDATION_MODES:
        return fail(
            "invalid_validation_mode",
            "validation_mode must be one of the supported modes",
            validation_mode=mode,
            supported=sorted(VALIDATION_MODES),
        )

    if data.get("passed") is not True or data.get("status") != "passed":
        return fail(
            "not_passed",
            "result must contain status='passed' and passed=true",
            status=data.get("status"),
            passed=data.get("passed"),
        )

    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict):
        return fail("missing_artifacts", "artifacts must be an object")

    missing_keys = [key for key in REQUIRED_ARTIFACTS if not artifacts.get(key)]
    if missing_keys:
        return fail("missing_artifact_keys", "required artifact paths are missing", keys=missing_keys)

    missing_files = []
    resolved_artifacts: dict[str, Path] = {}
    for key in REQUIRED_ARTIFACTS:
        artifact_value = artifacts[key]
        if not isinstance(artifact_value, str):
            return fail("invalid_artifact_path", "artifact path must be a string", key=key)
        artifact_path = resolve_artifact(root, artifact_value)
        resolved_artifacts[key] = artifact_path
        if not artifact_path.exists():
            missing_files.append({"key": key, "path": str(artifact_path)})
    if missing_files:
        return fail("missing_artifact_files", "referenced artifacts do not exist", files=missing_files)

    discussion_error, discussion = validate_discussion(data)
    if discussion_error:
        return fail("invalid_discussion_gate", discussion_error, discussion=discussion)

    state_error, state = validate_pipeline_state(resolved_artifacts["pipeline_state"])
    if state_error:
        return fail("invalid_pipeline_state", state_error, state=state)

    try:
        research_result = load_json(resolved_artifacts["research_result"])
    except ValueError as exc:
        return fail("invalid_research_result_json", str(exc))
    if research_result.get("ready_for_discussion") is not True:
        return fail(
            "research_not_ready",
            "research result must contain ready_for_discussion=true",
            ready_for_discussion=research_result.get("ready_for_discussion"),
        )
    gray_areas = research_result.get("gray_area_candidates", [])
    if not isinstance(gray_areas, list) or len(gray_areas) < 3:
        return fail(
            "insufficient_gray_areas",
            "research result must contain at least 3 gray_area_candidates",
            count=len(gray_areas) if isinstance(gray_areas, list) else None,
        )

    if mode == "pipeline-audit-artifact":
        audit = data.get("audit")
        if not isinstance(audit, dict):
            return fail("missing_audit", "audit object is required for pipeline-audit-artifact")
        blockers = audit.get("p0_blockers", [])
        if blockers:
            return fail("p0_blockers_present", "audit still has P0 blockers", p0_blockers=blockers)
        verdict = str(audit.get("verdict", "")).strip()
        if verdict not in {"可以开工", "approved", "ready"}:
            return fail("audit_not_approved", "audit verdict is not ready", verdict=verdict)

    if mode == "human-approval-artifact":
        approval = data.get("approval")
        if not isinstance(approval, dict) or approval.get("verdict") not in {"approved", "同意", "通过"}:
            return fail("approval_missing", "human approval verdict is required")

    if mode == "custom-validator-script":
        validator = data.get("validator")
        if not isinstance(validator, dict) or validator.get("passed") is not True:
            return fail("validator_not_passed", "custom validator must record passed=true")

    return ok(result_path, data)


if __name__ == "__main__":
    raise SystemExit(main())
