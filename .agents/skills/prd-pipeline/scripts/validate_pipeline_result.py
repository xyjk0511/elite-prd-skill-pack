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


REQUIRED_ARTIFACTS = ("discussion_context", "prd", "audit", "handoff", "qa")
VALIDATION_MODES = {
    "pipeline-audit-artifact",
    "human-approval-artifact",
    "custom-validator-script",
}


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
    for key in REQUIRED_ARTIFACTS:
        artifact_value = artifacts[key]
        if not isinstance(artifact_value, str):
            return fail("invalid_artifact_path", "artifact path must be a string", key=key)
        artifact_path = resolve_artifact(root, artifact_value)
        if not artifact_path.exists():
            missing_files.append({"key": key, "path": str(artifact_path)})
    if missing_files:
        return fail("missing_artifact_files", "referenced artifacts do not exist", files=missing_files)

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
