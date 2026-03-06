---
name: reflect
description: A skill for wrapping up a session — summarizing work done, updating docs, and logging learnings. Trigger on "/reflect", "reflect", "session reflect", "end session", "세션 정리", "오늘 한 거 정리", or "마무리". Use this skill at the end of any substantial work session (30+ minutes), when the user says "done", "wrap up", "what did we do", or when a significant feature or milestone is completed — even if they don't explicitly ask for reflection.
---

# reflect

A session wrap-up skill that runs 4 analysis agents in parallel, then validates with a duplicate-checker, and lets you choose which actions to take.

## Execution Flow

```
┌─────────────────────────────────────────────────────┐
│  Step 1: Check current project state (inline)        │
├─────────────────────────────────────────────────────┤
│  Step 2: Phase 1 — Launch 4 agents IN PARALLEL       │
│     ┌──────────────┬──────────────┐                  │
│     │ doc-updater  │ automation-  │                  │
│     │              │ scout        │                  │
│     ├──────────────┼──────────────┤                  │
│     │ learning-    │ followup-    │                  │
│     │ extractor    │ suggester    │                  │
│     └──────────────┴──────────────┘                  │
├─────────────────────────────────────────────────────┤
│  Step 3: Phase 2 — duplicate-checker (sequential)    │
├─────────────────────────────────────────────────────┤
│  Step 4: Consolidate + user selection                │
└─────────────────────────────────────────────────────┘
```

---

## Step 1: Check Current Project State

Before launching any agents, gather context inline:

- List files in the current working directory
- Note any files created or modified in this session (check conversation history)
- Produce a concise `PROJECT_STATE` string summarizing the session activity

This `PROJECT_STATE` will be passed as context to each Phase 1 agent.

---

## Step 2: Phase 1 — Parallel Analysis

Launch all 4 agents in a single response — running them sequentially would take 4x longer, and since the agents don't depend on each other's results, parallel execution is both faster and produces better analysis because each agent works from the same unbiased project state.

Use the Agent tool with `subagent_type: "general-purpose"` for each:

### Task 1 — doc-updater

```
subagent_type: general-purpose
prompt: |
  You are a documentation specialist performing a focused analysis.

  PROJECT STATE:
  {PROJECT_STATE}

  Your job: Review existing documentation files (CLAUDE.md, README.md, any .md files
  in the project) and identify what needs updating based on the session's work.

  Steps:
  1. Use Glob to find all .md files in the project
  2. Read the most relevant ones (CLAUDE.md first, then README.md)
  3. Compare their content against the PROJECT STATE

  Return ONLY a structured list:
  ## doc-updater results
  - File: [filename] | Section: [section] | Update: [what to add/change]
  (If nothing needs updating, say "No doc updates needed.")
```

### Task 2 — automation-scout

```
subagent_type: general-purpose
prompt: |
  You are an automation specialist performing a focused analysis.

  PROJECT STATE:
  {PROJECT_STATE}

  Your job: Identify repeating patterns in this session's work that could be automated
  as a skill, script, or CLAUDE.md hook.

  Steps:
  1. Review the PROJECT STATE for repeated actions or manual steps
  2. Check .claude/skills/ to avoid suggesting skills that already exist
  3. Propose specific automations

  Return ONLY a structured list:
  ## automation-scout results
  - Pattern: [what was repeated] | Type: [skill/script/hook] | Suggestion: [how to automate]
  (If nothing to automate, say "No automation opportunities found.")
```

### Task 3 — learning-extractor

```
subagent_type: general-purpose
prompt: |
  You are a learning specialist performing a focused analysis.

  PROJECT STATE:
  {PROJECT_STATE}

  Your job: Extract and summarize the key learnings from this session.

  Steps:
  1. Review what was built, fixed, or explored in this session
  2. Identify new concepts, tools, patterns, or techniques encountered
  3. Note connections to existing knowledge

  Return ONLY a structured list:
  ## learning-extractor results
  - Learned: [concept/tool/pattern] | Detail: [brief explanation] | Explore more: [yes/no]
  (If nothing new was learned, say "No new learnings identified.")
```

### Task 4 — followup-suggester

```
subagent_type: general-purpose
prompt: |
  You are a task planning specialist performing a focused analysis.

  PROJECT STATE:
  {PROJECT_STATE}

  Your job: Identify what should be done next based on this session's work.

  Steps:
  1. Review what was completed and what was left unfinished
  2. Identify natural follow-up tasks or improvements
  3. Prioritize by impact

  Return ONLY a structured list:
  ## followup-suggester results
  - Task: [what to do] | Priority: [high/medium/low] | Reason: [why]
  (List 3–5 items maximum.)
```

---

## Step 3: Phase 2 — Validation (sequential, after all Phase 1 agents complete)

After collecting all 4 results, launch ONE more Task:

```
subagent_type: general-purpose
prompt: |
  You are a duplicate checker. Review the following 4 analysis results and remove
  or merge any overlapping suggestions.

  {PHASE_1_RESULTS}

  Rules:
  - Full duplicate (same suggestion from 2+ agents): keep the more detailed one, remove the rest
  - Partial overlap (similar intent): merge into a single, better suggestion and note the source
  - Unique items: keep as-is

  Return a single clean consolidated list organized by category:
  📄 Docs to update
  ⚡ Automation ideas
  📚 Learnings
  ➡️  Next actions
```

---

## Step 4: Consolidate + User Selection

Present the duplicate-checked results clearly, then ask:

```json
AskUserQuestion({
  "questions": [{
    "question": "세션 정리가 완료됐습니다. 어떤 작업을 실행할까요?",
    "header": "작업 선택",
    "options": [
      {"label": "문서 업데이트", "description": "CLAUDE.md 또는 README에 변경 사항 반영"},
      {"label": "자동화 생성", "description": "반복 패턴을 스킬 또는 스크립트로 만들기"},
      {"label": "학습 기록 저장", "description": "오늘 배운 것을 노트 파일에 저장"},
      {"label": "건너뛰기", "description": "결과 확인만 — 별도 작업 없음"}
    ],
    "multiSelect": true
  }]
})
```

Execute only the selected actions.

---

## Quick Reference

**Use when:**
- After a long work session (30+ minutes)
- Before switching to a different project
- After completing a significant feature or milestone

**Skip when:**
- Short Q&A session with no file changes
- Only read code, made no modifications
- Already wrapped up manually
