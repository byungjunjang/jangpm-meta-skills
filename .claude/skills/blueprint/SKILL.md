---
name: blueprint
description: Agentic system design blueprint generator. Interviews the user to understand a task they want to automate, then produces a comprehensive integrated design document (.md file) that serves as a concrete implementation plan for Claude Code. The design document includes task context, workflow definition with LLM vs code boundaries, and implementation spec (folder structure, agent architecture, skills/scripts list, sub-agent design). Trigger on "/blueprint", "blueprint", "에이전트 설계", "설계서 만들어", "agentic workflow design", or any request to design/plan an agent or automation system. Use this skill whenever the user mentions automation design, workflow planning, agent architecture, system blueprinting, multi-step AI workflow planning, or wants to structure any complex task into an agentic system — even if they don't explicitly say "blueprint".
---

# Blueprint

## Overview

Conduct a structured interview to understand the user's automation task, then generate a complete agentic system design document. The deliverable is a single `.md` file ready for use as an implementation reference in Claude Code.

## Workflow

### Phase 1: Assess & Interview (max 3 turns)

Evaluate user input against these four areas. **Ask only about gaps.** If all areas are sufficiently clear, skip directly to Phase 2.

| Area | What to assess | Example question |
|------|---------------|------------------|
| **Goal & success criteria** | Is the ultimate goal clear? Can success/failure be judged? | "어떤 결과가 나와야 이 에이전트가 성공했다고 볼 수 있나요?" |
| **Task procedure** | Are input→output steps defined? Are branch conditions known? | "A 이후 B로 갈지 C로 갈지는 어떤 기준으로 판단하나요?" |
| **Agent organization** | Single vs multi-agent preference? Any clear role separations? | "하나의 에이전트가 순차 처리하면 되나요, 아니면 분리할 역할이 있나요?" |
| **Tools & tech** | Any existing tools/APIs in use? If none, suggest options. | "지금 쓰는 도구가 있나요? 없다면 이런 방식들이 가능한데 어떤 게 맞을까요?" |

**Interview rules:**
- Questions must be specific and probing, never generic or formulaic
- If user says "모르겠다" or "알아서 해줘": apply reasonable defaults, state your choice and reasoning, ask only for unavoidable decisions
- Group related questions — never ask more than 3 questions per turn

### Phase 2: Generate Design Document

Once requirements are clear, produce the design document. Save as `blueprint-<task-name>.md` in the current working directory.

See `references/document-template.md` for the full document structure and section details.
See `references/design-principles.md` for design rules to apply while authoring.

**Output rules:**
- CLAUDE.md, AGENT.md, skill file contents are **NOT written** — only their names and roles
- Implementation spec covers structure and responsibilities, not code or prompts
- Every workflow step must have: success criteria, validation method, failure handling

### Phase 3: Review

After presenting the document, ask: "수정하거나 보완할 부분이 있나요?"

Apply any requested changes and re-confirm.

## References

- **`references/document-template.md`**: Full template for the output design document (all sections, formats, tables)
- **`references/design-principles.md`**: Design rules for folder structure, agent architecture, validation patterns, failure handling, data transfer, and skill vs sub-agent distinctions
