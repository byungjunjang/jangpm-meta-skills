#!/usr/bin/env python3
"""
Minimal structural validator for Codex blueprint documents.

Usage:
  python .codex/skills/blueprint/scripts/validate_blueprint_doc.py ./blueprint-my-task.md
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REQUIRED_TOP_HEADERS = [
    "## 0. Goals and Deliverables",
    "## 1. Working Context",
    "## 2. Workflow Definition",
    "## 3. Implementation Spec",
    "## 4. Validation Checklist",
]

REQUIRED_CONTEXT_SUBHEADERS = [
    "### Background",
    "### Objective",
    "### Scope",
    "### Inputs",
    "### Outputs",
    "### Constraints",
    "### Terms",
]

REQUIRED_STEP_FIELDS = [
    "1) Step Goal:",
    "2) Input / Output:",
    "3) LLM Decision Area:",
    "4) Code Processing Area:",
    "5) Success Criteria:",
    "6) Validation Method:",
    "7) Failure Handling:",
    "8) Skills / Scripts:",
    "9) Intermediate Artifact Rule:",
]

REQUIRED_STATES = [
    "`COLLECTING_REQUIREMENTS`",
    "`PLANNING`",
    "`RUNNING_SCRIPT`",
    "`VALIDATING`",
    "`NEEDS_USER_INPUT`",
    "`DONE`",
    "`FAILED`",
]


def validate(path: Path) -> tuple[bool, list[str]]:
    if not path.exists():
        return False, [f"File not found: {path}"]

    text = path.read_text(encoding="utf-8")
    issues: list[str] = []

    for item in REQUIRED_TOP_HEADERS:
        if item not in text:
            issues.append(f"Missing top header: {item}")

    for item in REQUIRED_CONTEXT_SUBHEADERS:
        if item not in text:
            issues.append(f"Missing context section: {item}")

    for item in REQUIRED_STEP_FIELDS:
        if item not in text:
            issues.append(f"Missing step field: {item}")

    for item in REQUIRED_STATES:
        if item not in text:
            issues.append(f"Missing state token: {item}")

    step_count = len(re.findall(r"^#### Step \d{2}:", text, flags=re.MULTILINE))
    if step_count < 2:
        issues.append("Require at least two workflow steps using '#### Step NN:' headings")

    if "./blueprint-" not in text:
        issues.append("Final output path should reference ./blueprint-<task-name>.md")

    if "output/step01_" not in text:
        issues.append("Expected at least one intermediate artifact path using output/stepNN_<name>.<ext>")

    return len(issues) == 0, issues


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python validate_blueprint_doc.py <blueprint-md-path>")
        return 1

    ok, issues = validate(Path(sys.argv[1]))
    if ok:
        print("Blueprint document is structurally valid.")
        return 0

    print("Blueprint document validation failed:")
    for issue in issues:
        print(f"- {issue}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
