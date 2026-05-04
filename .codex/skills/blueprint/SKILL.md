---
name: blueprint
description: Codex용 자동화 에이전트 시스템 설계서 생성 스킬. 사용자 인터뷰로 요구사항을 정리하고 Codex 구현 기준의 통합 설계 문서(.md)를 작성한다. Use when the user asks for "$blueprint", "blueprint", "에이전트 설계", "설계서 만들어", "agentic workflow design", or any request to plan a Codex automation or agent workflow.
metadata:
  short-description: Create a Codex automation blueprint
---

# Blueprint

## Overview

Conduct a short interview about the task the user wants to automate, then produce a single design document `./blueprint-<task-name>.md` based on Codex implementation standards.

- Default assumption: `single Codex agent + skills/scripts as needed`.
- Do not include Claude Code-specific elements such as `.claude/commands`, `.claude/agents`, `AGENT.md`, or `Task`-based sub-agent structures.
- Distinguish clearly between Codex skills and Codex custom agents:
  - Skills live under `.codex/skills/<skill-name>/`
  - Custom subagents live under `.codex/agents/<agent-name>.toml`
- Implementation spec covers structure and responsibilities only — do not write actual code bodies or lengthy prompts.

## Workflow

### 1. Assess Gaps First

Check the three areas below first, and ask only about what is missing. Skip to Phase 2 if all sufficiency criteria are met.

| Area | Sufficiency criteria (all must be answerable) |
|---|---|
| Goal and success criteria | (1) Observable completion condition exists (2) Failure state can be identified |
| Task procedure | (1) Input format and source are specified (2) Output format and destination are specified (3) Branch conditions have clear decision criteria |
| Tools and constraints | (1) Tools/APIs are identified or can be recommended (2) Technical constraints (API limits, format restrictions) are known |

> **Agent organization** (single vs multi-agent) is NOT an interview topic. The agent decides this in Phase 2 based on `design-principles.md` › "Default Architecture" rules, and explains the rationale in Phase 4.

Interview rules:

- Ask at most 3 questions per turn.
- In default mode, ask directly in plain text messages.
- For items the user does not know, apply a reasonable default and state that assumption explicitly in the document.
- **Maximum 4 turns total.** If gaps remain after 4 turns, apply reasonable defaults, document them as assumptions, and proceed to the writing phase.

### 2. Write the Blueprint

Read the following two reference documents and apply them faithfully.

- `references/document-template.md`
- `references/design-principles.md`

If you want a calibration sample for specificity and decision framing, also skim:

- `references/example-blueprint.md`

**Interview findings → document section mapping (confirm before writing):**

| Interview finding | → Document section |
|---|---|
| Why it is needed, what problem it solves | `## 0. Goals and Deliverables` + `### Background` + `### Objective` |
| What is in / out of scope | `### Out of Scope` + `### Scope` |
| Input format, output format, trigger | `### Inputs` + `### Outputs` + `### End-to-End Flow` |
| Technical constraints, API limits | `### Constraints` |
| Domain-specific terminology | `### Terms` |
| Step-by-step processing, branch conditions | `#### Step NN` blocks + `### State Model` |
| Agent judgment vs script processing | `### LLM vs Code Boundary` |
| Tools / APIs used | `### Skill and Script Inventory` |
| Failure conditions, retry expectations | `#### Step NN` → `7) Failure Handling:` |

> **Agent decides these sections** (no interview needed): `### Recommended Folder Structure`, `### AGENTS.md Responsibilities`, `### Custom Agent Definitions`, `### AGENTS.md 작성 원칙`, `### Core Artifacts`. These are filled by the agent based on synthesized interview findings and design-principles.md rules.

Writing rules:

- Final output path: `./blueprint-<task-name>.md` at the project root
- Intermediate artifacts use the `output/stepNN_<name>.<ext>` naming convention
- Every workflow step must include all 9 fields below:
  1. Step Goal
  2. Input / Output
  3. LLM Decision Area
  4. Code Processing Area
  5. Success Criteria
  6. Validation Method
  7. Failure Handling
  8. Skills / Scripts
  9. Intermediate Artifact Rule
- Include all state tokens: `COLLECTING_REQUIREMENTS`, `PLANNING`, `RUNNING_SCRIPT`, `VALIDATING`, `NEEDS_USER_INPUT`, `DONE`, `FAILED`.

### 3. Validate Before Hand-off

After saving the document, run the validation below.

Do not assume a relative path from the target project — run the validation script from the **currently installed blueprint skill path**.

Example (adapt the path to your installation):

```bash
python ~/.codex/skills/blueprint/scripts/validate_blueprint_doc.py ./blueprint-<task-name>.md
# or if installed elsewhere:
# python /path/to/skills/blueprint/scripts/validate_blueprint_doc.py ./blueprint-<task-name>.md
```

- If validation fails, fix the document and run again.
- This validation checks document structure only.
- Use `./.codex/skills/blueprint/scripts/validate_blueprint_doc.py` only when working directly on this repository copy of the skill.
- When adding or modifying a Codex skill itself, use the separately installed `skill-creator` skill's `quick_validate.py`.

### 4. Review

Show the user the document path and summarize the key design decisions:

- Agent structure choice (single vs multi) and the reason
- Any tradeoffs locked in (e.g., "LLM judges step X because rule-based detection was too fragile")
- Any constraints that shaped the design
- Any assumptions applied (from "I don't know" responses or turn limit)

Then ask: "Do these decisions match your intent? Let me know if there's anything you'd like to change."

If user says "looks fine" / "not sure, just proceed" — confirm the specific assumptions that will be locked in: "The following assumptions will be finalized: [list]. Changing these after implementation is costly, so please review now." Then proceed.

## Notes

- Document structure follows English headers from the template — the validation script operates based on those headers.
- All design documents must include an **AGENTS.md 작성 원칙** section with the 4 principles (Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution), each with a self-verification test, plus a tradeoff statement and success metrics. See `references/design-principles.md` › "AGENTS.md / CLAUDE.md 작성 원칙".
- All design documents must have a **skill-creator usage requirement** section — every skill defined in the document must be created via `skill-creator` at implementation time, regardless of whether skill creation is a primary focus. See `references/design-principles.md` › "Skill Creation Standards" for exact wording. The validator checks for the literal string `skill-creator`.
- New Codex skills must be stored under `.codex/skills/<skill-name>/` for repo scope or `~/.codex/skills/<skill-name>/` for user scope.
- When designing a new skill folder, write paths relative to `.codex/skills/<skill-name>/`.
- When designing a custom subagent, write paths relative to `.codex/agents/<agent-name>.toml` and include `name`, `description`, and `developer_instructions`.
