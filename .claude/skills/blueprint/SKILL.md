---
name: blueprint
description: Agentic system design blueprint generator. Interviews the user to understand a task they want to automate, then produces a comprehensive integrated design document (.md file) that serves as a concrete implementation plan for Claude Code. The design document includes task context, workflow definition with LLM vs code boundaries, and implementation spec (folder structure, agent architecture, skills/scripts list, sub-agent design). Trigger on "/blueprint", "blueprint", "에이전트 설계", "설계서 만들어", "agentic workflow design". Use this skill when the user mentions automation design, workflow planning, agent architecture, system blueprinting, or multi-step AI workflow planning.
---

# Blueprint

## When NOT to use this skill

Simple task planning or to-do organizing — where a design document is not the deliverable — does not need this skill. Use blueprint only when the user wants an agentic system design document as the output.

## Overview

Conduct a structured interview to understand the user's automation task, then generate a complete agentic system design document. The deliverable is a single `.md` file ready for use as an implementation reference in Claude Code.

## Before Starting

**Read both reference files before doing anything else.** They contain the document structure and design rules you'll apply in Phase 2. Skip them and the output will be incomplete.

1. Read `references/document-template.md` — the full section-by-section template for the output file
2. Read `references/design-principles.md` — design rules for agent structure, validation, data transfer, skill vs sub-agent
3. *(Optional)* Skim `references/example-blueprint.md` — a fully annotated sample blueprint document for calibration

## Workflow

### Phase 1: Assess & Interview

Evaluate user input against these three areas. **Ask only about gaps.** If all sufficiency criteria are met, skip directly to Phase 2.

| Area | Sufficiency criteria (all must be answerable) | Example question |
|------|----------------------------------------------|------------------|
| **Goal & success criteria** | (1) 완료 상태를 판별하는 구체적 기준이 1개 이상 (2) 실패 상태를 판별할 수 있는가 | "어떤 결과가 나와야 이 에이전트가 성공했다고 볼 수 있나요?" |
| **Task procedure** | (1) 입력 형식과 출처가 특정됨 (2) 출력 형식과 저장 위치가 특정됨 (3) 분기 조건이 있다면 판단 기준이 명확함 | "A 이후 B로 갈지 C로 갈지는 어떤 기준으로 판단하나요?" |
| **Tools & constraints** | (1) 사용할 도구/API가 정해졌거나 추천 가능 (2) 기술적 제약(API 한도, 포맷 제한 등)이 파악됨 | "지금 쓰는 도구가 있나요? 없다면 이런 방식들이 가능한데 어떤 게 맞을까요?" |

> **Agent organization**(단일 vs 멀티 에이전트)은 인터뷰 대상이 아니다. `design-principles.md`의 "Agent Structure Choice" 기준에 따라 에이전트가 Phase 2에서 자체 결정하고, Phase 3에서 근거를 설명한다.

**Interview rules:**
- Questions must be specific and probing, never generic or formulaic
- If user says "모르겠다" or "알아서 해줘": apply reasonable defaults, state your choice and reasoning, ask only for unavoidable decisions
- Group related questions — never ask more than 3 questions per turn
- **Maximum 4 turns total.** If gaps remain after 4 turns, apply reasonable defaults, document them as assumptions in the design document, and proceed to Phase 2

### Phase 2: Generate Design Document

Once requirements are clear, map interview findings to document sections before writing:

| Interview finding | → Document section |
|---|---|
| Why this is needed, what problem it solves | § 1. 작업 컨텍스트 › 배경 및 목적 |
| What's in scope / out of scope | § 1. 작업 컨텍스트 › 범위 |
| Input format, output format, trigger | § 1. 작업 컨텍스트 › 입출력 정의 |
| Technical constraints, API limits | § 1. 작업 컨텍스트 › 제약조건 |
| Domain-specific terminology | § 1. 작업 컨텍스트 › 용어 정의 |
| Step-by-step process, branching logic | § 2. 전체 흐름도 + 단계별 상세 |
| What the agent decides vs what code handles | § 2. LLM 판단 vs 코드 처리 구분 |
| State transitions between steps | § 2. 상태 전이 |
| What tools/APIs are used | § 3. 스킬/스크립트 목록 |
| Failure conditions, retry expectations | § 2. 단계별 상세 › 실패 시 처리 |

> **에이전트가 자체 결정하는 섹션** (인터뷰 불필요): § 3. 에이전트 구조 (design-principles.md 기준 적용), § 3. 폴더 구조, § 3. CLAUDE.md 핵심 섹션 목록, § 3. 주요 산출물 파일. 이 섹션들은 인터뷰 결과를 종합하여 에이전트가 추론으로 채운다.

Fill every section using the template in `references/document-template.md`. Apply design rules from `references/design-principles.md`.

Save as `blueprint-<task-name>.md` in the current working directory.

**Output rules:**
- CLAUDE.md, AGENT.md, skill file contents are **NOT written** — only their names and roles
- Implementation spec covers structure and responsibilities, not code or prompts
- Every workflow step must have: success criteria, validation method, failure handling
- **Always include a "CLAUDE.md 작성 원칙" section** in the implementation spec. Apply the 4 principles (Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution) from `references/design-principles.md` › "CLAUDE.md / AGENTS.md 작성 원칙". Each principle must include a self-verification test. Include tradeoff statement and success metrics.
- **Always include a "스킬 생성 규칙" section** in every blueprint document. All skills defined in this document must be created via `skill-creator` at implementation time — direct manual authoring of SKILL.md is prohibited (see `references/design-principles.md` › Skill Creation Standards for the exact section text). The document **must contain the literal string `skill-creator`** — the structural validator checks for this and will fail without it.

**Completeness check before saving** — confirm each item is filled:
- [ ] Every workflow step has success criteria + validation method + failure handling
- [ ] LLM vs script responsibility table is filled
- [ ] Folder structure is defined
- [ ] "CLAUDE.md 작성 원칙" section is present with 4 principles + self-verification tests + tradeoff + success metrics
- [ ] "스킬 생성 규칙" section is present and mentions `skill-creator`
- [ ] No table cell left blank or "TBD"

### Phase 2.5: Validate Document

After saving, run the structural validation script before presenting the document to the user.

Do not assume a relative path from the target project — run the script from the **currently installed blueprint skill path**.

```bash
# When installed globally (normal usage):
python ~/.claude/skills/blueprint/scripts/validate_blueprint_doc.py ./blueprint-<task-name>.md

# When working inside the skill repository itself (development/testing only):
python .claude/skills/blueprint/scripts/validate_blueprint_doc.py ./blueprint-<task-name>.md
```

If validation fails, fix the document and run again. This script checks structure only (required sections, step fields, and implementation/workflow section presence) — it does not check content quality.

If the script is not found (e.g., first install or missing file), skip script validation and manually verify the Phase 2 completeness checklist instead:
- [ ] Every workflow step has success criteria + validation method + failure handling
- [ ] LLM vs script responsibility table is filled
- [ ] Folder structure is defined
- [ ] "CLAUDE.md 작성 원칙" section is present with 4 principles + self-verification tests + tradeoff + success metrics
- [ ] "스킬 생성 규칙" section is present and mentions `skill-creator`
- [ ] No table cell left blank or "TBD"

### Phase 3: Review

After presenting the document, summarize the key design decisions:

- Agent structure choice (single vs multi) and the reason
- Any tradeoffs locked in (e.g., "LLM judges step X because rule-based detection was too fragile")
- Any constraints that shaped the design
- Any assumptions applied (from "모르겠다" responses or turn limit)

Then ask: "이 결정들이 의도에 맞는지 확인해 주세요. 변경할 부분이 있으면 말씀해 주세요."

If user says "괜찮아" / "잘 모르겠는데 진행해" — confirm the specific assumptions that will be locked in: "다음 가정들이 확정됩니다: [list]. 구현 후 변경하면 비용이 크니 지금 확인해 주세요." Then proceed.

Apply any requested changes and re-confirm.

## References

- **`references/document-template.md`**: Full template for the output design document (all sections, formats, tables)
- **`references/design-principles.md`**: Design rules for folder structure, agent architecture, validation patterns, failure handling, data transfer, and skill vs sub-agent distinctions
