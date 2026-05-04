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

REQUIRED_GOAL_SUBHEADERS = [
    "### Primary Goal",
    "### Success Definition",
    "### Out of Scope",
]

REQUIRED_WORKFLOW_SUBHEADERS = [
    "### End-to-End Flow",
    "### LLM vs Code Boundary",
    "### State Model",
]

REQUIRED_IMPLEMENTATION_SUBHEADERS = [
    "### Recommended Folder Structure",
    "### AGENTS.md Responsibilities",
    "### Custom Agent Definitions",
    "### Skill and Script Inventory",
    "### AGENTS.md 작성 원칙",
    "### Skill Creation Rules",
    "### Core Artifacts",
]

REQUIRED_AGENTS_GUIDE_SNIPPETS = [
    "| 원칙 | 핵심 | 자기 검증 테스트 |",
    "구현 전에 생각하라",
    "단순함 우선",
    "수술적 변경",
    "목표 중심 실행",
    "**트레이드오프**:",
    "**이 가이드라인이 잘 작동하고 있다면:**",
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


# Matches Step 01:, Step 2A:, Step 2M:, Step 03: etc.
STEP_HEADING_RE = re.compile(r"^#### Step (\d+)([A-Za-z]?):", flags=re.MULTILINE)
FENCED_BLOCK_RE = re.compile(r"```.*?```", flags=re.DOTALL)
CHECKLIST_ITEM_RE = re.compile(r"^- \[ \] .+$", flags=re.MULTILINE)


def strip_fenced_code_blocks(text: str) -> str:
    return re.sub(FENCED_BLOCK_RE, "", text)


def assert_in_order(text: str, items: list[str], issues: list[str], label: str) -> None:
    cursor = -1
    for item in items:
        idx = text.find(item)
        if idx == -1:
            issues.append(f"Missing {label}: {item}")
            continue
        if idx < cursor:
            issues.append(f"Out-of-order {label}: {item}")
        cursor = idx


def split_step_blocks(text: str) -> list[tuple[str, str]]:
    """Return list of (step_label, block_text) tuples."""
    matches = list(STEP_HEADING_RE.finditer(text))
    blocks: list[tuple[str, str]] = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        label = f"Step {match.group(1)}{match.group(2)}"
        blocks.append((label, text[start:end]))
    return blocks


def check_step_continuity(blocks: list[tuple[str, str]], issues: list[str]) -> None:
    """Check that base step numbers are continuous (1, 2, 3...).

    Variants like 2A, 2B, 2M are allowed and don't break continuity.
    """
    if not blocks:
        return

    base_numbers: list[int] = []
    for label, _ in blocks:
        match = re.match(r"Step (\d+)", label)
        if match:
            num = int(match.group(1))
            if num not in base_numbers:
                base_numbers.append(num)

    base_numbers.sort()
    for i in range(len(base_numbers) - 1):
        if base_numbers[i + 1] - base_numbers[i] > 1:
            gap_start = base_numbers[i]
            gap_end = base_numbers[i + 1]
            issues.append(
                f"Step number gap: Step {gap_start} -> Step {gap_end} "
                f"(missing Step {gap_start + 1})"
            )


def validate(path: Path) -> tuple[bool, list[str]]:
    if not path.exists():
        return False, [f"File not found: {path}"]

    text = path.read_text(encoding="utf-8")
    text_no_code = strip_fenced_code_blocks(text)
    issues: list[str] = []

    if not re.fullmatch(r"blueprint-.+\.md", path.name):
        issues.append("Filename should follow blueprint-<task-name>.md")

    assert_in_order(text_no_code, REQUIRED_TOP_HEADERS, issues, "top header")
    assert_in_order(text_no_code, REQUIRED_GOAL_SUBHEADERS, issues, "goal section")
    assert_in_order(text_no_code, REQUIRED_CONTEXT_SUBHEADERS, issues, "context section")
    assert_in_order(text_no_code, REQUIRED_WORKFLOW_SUBHEADERS, issues, "workflow section")
    assert_in_order(
        text_no_code,
        REQUIRED_IMPLEMENTATION_SUBHEADERS,
        issues,
        "implementation section",
    )

    for item in REQUIRED_STATES:
        if item not in text_no_code:
            issues.append(f"Missing state token: {item}")

    if "| LLM handles | Code handles |" not in text_no_code:
        issues.append("Missing LLM vs Code Boundary table header")

    if "| State | Entry Condition | Exit Condition | Next State |" not in text_no_code:
        issues.append("Missing State Model table header")

    step_blocks = split_step_blocks(text_no_code)
    if len(step_blocks) < 2:
        issues.append("Require at least two workflow steps using '#### Step NN:' headings")
    else:
        for label, block in step_blocks:
            for field in REQUIRED_STEP_FIELDS:
                if field not in block:
                    issues.append(f"Missing step field in {label}: {field}")
        check_step_continuity(step_blocks, issues)

    if "output/step01_" not in text_no_code:
        issues.append("Expected at least one intermediate artifact path using output/stepNN_<name>.<ext>")

    for item in REQUIRED_AGENTS_GUIDE_SNIPPETS:
        if item not in text_no_code:
            issues.append(f"Missing AGENTS.md guidance content: {item}")

    checklist_count = len(CHECKLIST_ITEM_RE.findall(text_no_code))
    if checklist_count < 8:
        issues.append("Validation checklist should contain at least 8 unchecked items")

    if "skill-creator" not in text_no_code:
        issues.append("Missing required skill-creator usage rule")

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
