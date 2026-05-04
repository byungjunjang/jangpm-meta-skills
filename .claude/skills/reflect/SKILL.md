---
name: reflect
description: >-
  Session wrap-up and fix-learning capture skill. Use when the user explicitly
  asks for "/reflect", "reflect", "session reflect", "end session", "세션 정리",
  "오늘 한 거 정리", or "마무리", or when the user clearly confirms that a
  concrete issue from the current coding session is fixed ("고쳐졌다",
  "해결됐다", "it's fixed", "working now", "that worked", "problem solved").
  Explicit invocation runs Full Reflect; confident fix confirmation runs Quick
  Reflect.
---

# Reflect

Wrap up a session or capture one confirmed fix as reusable project knowledge.

- Default architecture: single agent, inline analysis, no task-based subagents
- Explicit invocation runs **Full Reflect**
- Confident fix confirmation runs **Quick Reflect**
- When uncertain, prefer doing less: no-op instead of saving weak learnings

## Mode Selection (first)

Choose the mode before doing any work.

- **Full Reflect**: the user explicitly asks for `"/reflect"`, `reflect`, `session reflect`, `end session`, `세션 정리`, `오늘 한 거 정리`, or `마무리`
- **Quick Reflect**: the user clearly confirms that a concrete issue from the current coding session is now fixed

Quick Reflect requires all of the following:

1. The recent conversation contains a real bug, implementation issue, or debugging thread
2. The user's latest message is a concrete fix confirmation, not casual acknowledgment
3. The repo state or recent turns provide enough evidence to explain the problem and fix
4. At least one reusable learning can be stated cleanly

If those conditions are not met, do not save anything.

If both modes seem possible, explicit invocation wins and you run **Full Reflect**.

## Storage Model

- Canonical records live in `docs/solutions/<category>/<id>.md`
- `docs/solutions/index.json` is a derived artifact
- Never append blindly to `index.json`; rebuild it from solution docs after every write
- Categories: `bug-fix`, `pattern`, `tool-usage`, `architecture`, `workflow`
- Keep frontmatter fields consistent across all solution docs

## First Run Initialization

If `docs/solutions/index.json` does not exist:

1. Create `docs/solutions/`
2. Create subdirectories: `bug-fix/`, `pattern/`, `tool-usage/`, `architecture/`, `workflow/`
3. Create `docs/solutions/index.json` with `[]`
4. Briefly note the initialization only when reflection output is already being shown

## Quick Reflect

Purpose: capture one high-signal resolved issue without turning every "fixed" into a save.

### 1. Run the Eligibility Gate

- Review the last 5-10 turns plus relevant repo context
- Require a resolved problem plus a concrete cause or fix
- Reject casual confirmations, speculative ideas, or vague "it works now" statements with no evidence
- Save at most **one** learning in Quick Reflect

If the eligibility gate fails during implicit invocation:

- do not create or modify files
- do not emit a reflection block

### 2. Extract One Candidate Learning

Capture:

- concise title
- category
- 2-4 tags
- `Problem`
- `Solution`
- `Key Insight`
- optional `Context`

### 3. Check Overlap

Read `docs/solutions/index.json`.

For the candidate learning:

- compare tags and title keywords against existing entries
- if there is a likely match, read the existing solution doc before deciding
- classify as `NEW`, `REINFORCE`, or `SUPERSEDE`

### 4. Save the Learning

For all write paths below, rebuild `index.json` after the document updates.

**NEW**

- Generate ID `sol-YYYYMMDD-NNN`
- Write `docs/solutions/<category>/<id>.md`
- Set:
  - `confidence: 0.50`
  - `created: YYYY-MM-DD`
  - `last_reinforced: YYYY-MM-DD`
  - `reinforcement_count: 0`
  - `supersedes: null`
  - `superseded_by: null`

**REINFORCE**

- Read the existing solution doc
- Update frontmatter:
  - `confidence += 0.15` with cap `0.95`
  - `last_reinforced = today`
  - `reinforcement_count += 1`
- Append to `## Context` only when there is genuinely new information

**SUPERSEDE**

- Update the old doc with `superseded_by: <new-id>`
- Lower old confidence to `min(current_confidence, 0.25)`
- Create the new doc with `supersedes: <old-id>` and `superseded_by: null`

### 5. Rebuild `index.json`

Read all solution docs under `docs/solutions/**` and write a JSON array containing:

- `id`
- `title`
- `tags`
- `category`
- `confidence`
- `created`
- `last_reinforced`
- `reinforcement_count`
- `supersedes`
- `superseded_by`
- `related`

Sort by:

1. `confidence` descending
2. `last_reinforced` descending
3. `id` ascending

### 6. Confirm Briefly

Use a short confirmation only when reflection output is appropriate:

- `📚 Saved: [title] (new, confidence: 0.50)`
- `📚 Reinforced: [title] (0.50 -> 0.65)`
- `📚 Superseded: [old-id] -> [new-id]`

## Full Reflect

Purpose: explicit wrap-up after substantial work.

### 1. Inspect Session State

Collect concrete evidence first:

- current workspace structure
- files changed in this session from repo state and recent turns
- relevant documentation files for the work just completed
- existing `docs/solutions/index.json` entries, if present

Compress this into a short internal `PROJECT_STATE` summary before moving on.

### 2. Produce Four Analysis Buckets Inline

Analyze the session in four buckets:

1. **Docs to update**
2. **Automation ideas**
3. **Learnings**
4. **Next actions**

Rules:

- base every item on actual work performed
- merge duplicates across buckets
- drop vague or low-value items
- keep learnings to 0-3 high-signal items
- keep next actions to 1-5 concrete tasks

### 3. Apply Changes Carefully

**Learnings**

- Save using the exact same `NEW / REINFORCE / SUPERSEDE` pipeline as Quick Reflect
- Rebuild `docs/solutions/index.json` after writes

**Doc updates**

- Only target `README.md`, `CHANGELOG.md`, and `docs/**/*.md`
- Exclude `docs/solutions/**`
- Classify each edit as `APPEND`, `REVISE`, or `NEW_SECTION`
- Keep edits narrow and factual
- Never modify agent/config files:
  - `CLAUDE.md`
  - `AGENTS.md`
  - `SKILL.md`
  - `GEMINI.md`
  - anything under `.claude/`
  - anything under `.codex/`

**Automation ideas**

- Report only
- Do not scaffold code, skills, hooks, or scripts during reflection

### 4. Scan for Stale Learnings

After rebuilding `index.json`, flag stale entries for awareness:

- stale = `last_reinforced` older than 60 days
- report stale entries only
- do not auto-decay, auto-delete, or archive anything

### 5. Report

Present results in this order:

```text
📚 학습 저장
  - [NEW/REINFORCE/SUPERSEDE] [id] [title] (confidence: X.XX)

⏳ Stale 학습
  - [id] [title] (last reinforced: YYYY-MM-DD)

📄 문서 업데이트
  - [filename]: [what changed]

⚡ 자동화 아이디어
  - [suggestion]

➡️ 후속 작업
  - [priority] [task]
```

Omit empty sections except `후속 작업`, which may say `없음`.

## Solution Document Template

```yaml
---
id: sol-YYYYMMDD-NNN
title: "concise title"
tags: [tag1, tag2, tag3]
category: bug-fix | pattern | tool-usage | architecture | workflow
confidence: 0.50
created: YYYY-MM-DD
last_reinforced: YYYY-MM-DD
reinforcement_count: 0
supersedes: null
superseded_by: null
related: []
---

## Problem
What was the problem?

## Solution
How was it solved?

## Key Insight
What general lesson should be reused?

## Context
Project-specific background when it adds value.
```

## Notes

- Best after meaningful implementation work
- Quick Reflect should stay conservative; false positives are worse than missed saves
- Prefer concrete repo evidence over memory
- Keep the storage schema stable so future reinforcement remains cheap
