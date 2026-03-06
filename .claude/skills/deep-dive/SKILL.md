---
name: deep-dive
description: Interview user in-depth to create a detailed spec. Use when the user wants to deeply explore requirements, clarify a task, or create a specification document. Trigger on "/deep-dive", "deep dive", "interview me", "create a spec", "요구사항 정리", "기획서 만들어", or "스펙 작성". Also trigger when the user seems unsure about what they want and needs structured questioning to figure it out — e.g., requests to flesh out an idea, write a PRD, clarify scope, explore edge cases, or when they say things like "I have a rough idea but need to think it through".
---

# deep-dive

An in-depth interview skill that asks non-obvious, probing questions across all dimensions — technical implementation, UI/UX, tradeoffs, concerns, and edge cases — then either writes a new spec file or updates an existing document.

## Execution Flow

1. Read the user's instructions (topic/goal) from `$ARGUMENTS`
2. Scan the current working directory for an existing spec/planning document
3. Conduct a multi-round interview using `AskUserQuestion`
4. If an existing document was found → update it; otherwise → create a new spec file

---

## Step 1: Understand the Topic & Scan for Existing Document

1. Read the `$ARGUMENTS` to understand what the user wants to spec out. If no argument is given, ask what topic to deep-dive into as the first question.
2. Use `Glob` to scan the current working directory for existing spec or planning documents. Look for patterns such as:
   - `spec-*.md`, `*-spec.md`
   - `*기획*.md`, `*설계*.md`, `*planning*.md`, `*PRD*.md`, `*requirements*.md`
   - Any `.md` file that looks like a design/planning document based on its name
3. If a matching file is found, read it with `Read` to understand its current content and structure. Keep this in context for Step 4.

---

## Step 2: Conduct the Interview

Use `AskUserQuestion` to interview the user continuously. Follow these rules:

- **Ask 1–2 questions per round** — never dump many questions at once
- **Cover all dimensions** — rotate across categories below, don't skip any
- **Avoid obvious questions** — never ask "what is the goal?" or "who are the users?" without more depth
- **Build on previous answers** — each question should reference what was just learned
- **Continue until complete** — keep going until all critical areas are covered (typically 5–8 rounds)

### Question Categories (rotate through all)

1. **Core behavior** — What exactly should it do? What are the happy path and edge cases?
2. **Technical implementation** — What stack, constraints, or existing systems apply?
3. **UI/UX** — What does the user experience look like? What interactions matter?
4. **Tradeoffs** — What are you willing to sacrifice? Speed vs. accuracy? Simplicity vs. flexibility?
5. **Failure modes** — What should happen when things go wrong?
6. **Scale & future** — What does "done" look like? What might need to change later?
7. **Concerns** — What are you most worried about?

---

## Step 3: Save Results — Auto-detect Mode

Do **not** ask the user. Decide automatically based on Step 1's scan result:

- **Existing document found** → go to Step 4a (Update)
- **No document found** → go to Step 4b (Create)

---

## Step 4a: Update Existing Document

1. The file was already read in Step 1 — use that content
2. Analyze its structure: identify existing sections and their scope
3. Merge the interview findings intelligently:
   - **Existing sections**: revise or append only the relevant parts; do not touch unrelated content
   - **New sections**: add at the bottom if the document doesn't already cover them
   - **Conflicts**: if the interview contradicts existing content, mark the change with a `> ⚠️ Updated:` callout rather than silently overwriting
4. Use `Edit` tool for targeted updates (prefer `Edit` over `Write` to preserve existing content)
5. Tell the user the filename and summarize exactly what was changed

---

## Step 4b: Create New Spec File

- Filename: `spec-[topic-slug].md` in the current working directory
- Format:

```markdown
# Spec: [Topic]

## Overview
[1–2 sentence summary]

## Goals
- ...

## Requirements
### Functional
- ...
### Non-functional
- ...

## Technical Notes
- ...

## UI/UX Notes
- ...

## Tradeoffs & Decisions
- ...

## Open Questions
- ...
```

Use `Write` tool to save the file, then tell the user the filename.
