---
name: deep-dive
description: Interview user in-depth to create a detailed spec. Use when the user wants to deeply explore requirements, clarify a task, or create a specification document. Trigger on "/deep-dive", "deep dive", "interview me", "create a spec", "요구사항 정리", "기획서 만들어", or "스펙 작성". Also trigger when the user seems unsure about what they want and needs structured questioning to figure it out — e.g., requests to flesh out an idea, write a PRD, clarify scope, explore edge cases, or when they say things like "I have a rough idea but need to think it through".
---

# deep-dive

An in-depth interview skill that asks non-obvious, probing questions across all dimensions — technical implementation, UI/UX, tradeoffs, concerns, and edge cases — then saves results to a spec document.

**CRITICAL DEFAULT BEHAVIOR**: When an existing spec or planning document is found, you MUST update that document unless the user explicitly requests a new file. Creating a new file when a relevant document already exists is INCORRECT behavior — unless the user overrides this in Step 1. New file creation is the default ONLY when no related document exists at all.

## Execution Flow

1. Read the user's instructions (topic/goal) from `$ARGUMENTS`
2. Scan the current working directory for existing spec/planning documents
3. **If documents found → present them to the user and confirm which to update**
4. Conduct a multi-round interview using `AskUserQuestion`
5. Save results: update the chosen document (default) or create new only if user requested a new file in step 3

---

## Step 1: Understand the Topic & Scan for Existing Document

1. Read the `$ARGUMENTS` to understand what the user wants to spec out. If no argument is given, ask what topic to deep-dive into as the first question.
2. Use `Glob` to scan the current working directory for existing spec or planning documents. Look for patterns such as:
   - `spec-*.md`, `*-spec.md`
   - `*기획*.md`, `*설계*.md`, `*planning*.md`, `*PRD*.md`, `*requirements*.md`
   - Any `.md` file that looks like a design/planning document based on its name
3. If a matching file is found, read it with `Read` to understand its current content and structure.
4. **If no documents found** → skip to Step 2 (interview). The decision is implicitly **create new** — Step 4b will apply after the interview.
5. **User confirmation (REQUIRED when documents are found)**:
   - Present the candidate document(s) to the user via `AskUserQuestion`
   - If **one document** found: "I found an existing document: `[filename]`. I'll update this with the interview results. OK? (Type 'new' if you want a separate file instead.)"
   - If **multiple documents** found: "I found these existing documents: [list]. Which one should I update? Or type 'new' to create a fresh spec file."
   - If the user picks a document (or confirms the single one) → that is the **update target** (proceed to interview, then Step 4a)
   - If the user indicates they want a new/separate file (e.g., "new", "따로 만들어줘", "separate file", "새로 만들어") → mark as **create new** (proceed to interview, then Step 4b)
   - If the user does not request a new file → **default is update**
   - ⚠️ This decision is **FINAL** — do not re-evaluate or change it in later steps.

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

## Step 3: Save Results — Follow Step 1 Decision

DO NOT re-evaluate. Follow the decision made in Step 1:

- **Update target was chosen in Step 1** → go to Step 4a (Update)
- **No document was found, or user requested a new file** → go to Step 4b (Create)

⚠️ **HARD RULE**: If an existing document was found AND the user did NOT request a new file, you MUST go to Step 4a. Do not create a new file.

---

## Step 4a: Update Existing Document

1. The file was already read in Step 1 — use that content.

2. **Pre-merge analysis (REQUIRED):**
   - List every section heading in the existing document
   - Map each interview finding to an existing section
   - Classify each item as one of:
     - **APPEND** — new content that belongs in an existing section
     - **REVISE** — content that updates/corrects something already written
     - **NEW_SECTION** — content with no matching section

3. **Merge rules:**
   - **APPEND**: Add at the end of the matching section
   - **REVISE**: Keep existing content, add changes with `> ⚠️ Updated:` marker to show what changed and why
   - **NEW_SECTION**: Insert before the last section (typically "Open Questions") — do not scatter new sections randomly
   - **Untouched content**: Any existing content NOT covered by the interview must remain exactly as-is — do not reformat, rephrase, or reorganize it
   - Use `Edit` tool for section-by-section targeted updates. **Do NOT use `Write` to overwrite the entire file.**

4. Tell the user the filename and summarize exactly what was changed.

---

## Step 4b: Create New Spec File

> ⚠️ Only reach this step if: (a) no existing document was found in Step 1, OR (b) user explicitly requested a new file in Step 1.
> If neither condition is true, STOP and go back to Step 4a.

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
