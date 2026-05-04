# Eval Guide

How to write eval criteria that actually improve your skills instead of giving you false confidence.

## Table of Contents

1. [The golden rule](#the-golden-rule) — every eval needs a stable scoring rule
2. [Assertion category taxonomy](#the-assertion-category-taxonomy) — 6 categories to pull from
3. [Converting subjective criteria](#converting-subjective-criteria-to-binary-checks) — decompose vibes into checks
4. [Good evals vs bad evals](#good-evals-vs-bad-evals) — examples by skill type
5. [Common mistakes](#common-mistakes) — too many, too narrow, overlapping
6. [evals.json schema](#evalsjson-schema) — structured format for automation
7. [The eval template](#the-eval-template) — copy-paste formats
8. [Generating evals with AI](#asking-the-agent-to-generate-evals-for-you) — prompt template
9. [False positive tracking](#false-positive-tracking-outer-loop--periodic) — when evals lie

---

## the golden rule

Every eval must have a stable scoring rule. Not a 1-7 vibe scale. Not an ungrounded impression.

Preferred order:

1. Binary pass/fail
2. Comparative win/tie/loss
3. Fidelity pass/fail between pipeline stages

Why: arbitrary scales compound variability. Binary, comparative, and fidelity evals can still be reliable as long as the rubric is explicit and repeatable.

The test: **could two different agents score the same pair of outputs and mostly agree?** If not, tighten the rubric.

---

## the assertion category taxonomy

When writing evals for any skill, pull from these six categories. You don't need all six — pick the ones that matter for your skill.

### Structure
- Does the output contain all required sections/headings?
- Are sections in the correct order?
- Is the markdown/formatting valid? (code blocks, lists, etc.)

### Length
- Is the total length within the upper/lower bound?
- Is each section within its length limit?
- Are individual sentences/paragraphs within limits?

### Inclusion
- Are required keywords/terms present?
- Are specific numbers, data points, or examples included?
- Is a CTA (call to action) present where required?
- Are rules from reference files reflected in the output?

### Exclusion
- Are banned words/phrases absent? (synergy, leverage, game-changer, etc.)
- Are banned formats absent? (em dash, emoji, etc.)
- Are AI-isms absent? ("As an AI...", "I'd be happy to...", "Here's the kicker")

### Format
- Is the output file type correct? (JSON, Markdown, etc.)
- Does the filename follow the naming convention?
- Is metadata/frontmatter correct and complete?

### Logic
- Are input values accurately reflected in the output?
- Are calculations correct?
- Are external data references accurate?

### Comparative (for any skill with subjective quality)
- Is the output better than the baseline on [specific dimension]?
- Examples: layout appeal, tone consistency, code readability, information hierarchy

**How to use this:** Scan each category and ask "does this apply to my skill?" Extract 3-6 binary checks from the first six categories. If your skill has subjective quality dimensions, also add 3-5 comparative checks — these push quality beyond rule compliance.

---

## converting subjective criteria to binary checks

The hardest part of writing evals: your real quality standards feel subjective. Here's how to decompose them.

**The technique:** Ask "what would I point to if I had to prove this to someone?"

| Subjective criteria | Binary decomposition |
|---|---|
| "Professional tone" | "No emoji" + "No exclamation marks beyond 1" + "No casual contractions (gonna, wanna)" |
| "Well-structured" | "Has 3+ H2 headings" + "Each section has 2+ paragraphs" |
| "References the source material" | "Contains 5+ keywords from the reference file" |
| "Engaging opening" | "First sentence contains a specific claim, story, or question (not a generic statement)" |
| "Actionable content" | "Contains 3+ concrete steps the reader can do today" |
| "Appropriate length" | "Total word count between 1500-3000" |
| "Natural Korean writing" | "No em dash (—)" + "Uses ~해요 체, not ~합니다 체" + "No direct English loan-phrases where Korean equivalents exist" |

**Warning:** You'll never capture 100% of a subjective quality through binary checks. That's OK. The human review phase in the main loop catches what the evals miss. The goal is to automate the 80% that IS checkable.

---

## good evals vs bad evals

### Text/copy skills (newsletters, tweets, emails, blog posts)

**Bad evals:**
- "Is the writing good?" -> too vague
- "Rate the engagement potential 1-10" -> scale = unreliable
- "Does it sound like a human?" -> subjective, inconsistent scoring

**Good evals:**
- "Does the output contain zero phrases from this banned list: [game-changer, here's the kicker, the best part, level up]?"
- "Does the opening sentence reference a specific time, place, or sensory detail?"
- "Is the output between 150-400 words?"
- "Does it end with a specific CTA that tells the reader exactly what to do next?"

### Visual/design skills (diagrams, images, slides)

**Bad evals:**
- "Does it look professional?" -> subjective
- "Rate the visual quality 1-5" -> scale
- "Is the layout good?" -> vague

**Good binary evals (rule compliance):**
- "Is all text in the image legible with no truncated or overlapping words?"
- "Does the color palette use only soft/pastel tones with no neon, bright red, or high-saturation colors?"
- "Is the layout linear — flowing either left-to-right or top-to-bottom with no scattered elements?"
- "Is the image free of numbered steps, ordinals, or sequential numbering?"

**Good comparative evals (quality beyond compliance):**

Binary evals plateau once the skill follows the rules. Comparative evals push quality past that ceiling by asking "is the mutated output *better*?"

**Visual/design examples:**
```
EVAL C1: Layout composition — more intentional whitespace and visual grouping?
EVAL C2: Visual richness — more effective use of color, icons, charts?
EVAL C3: Information density — more info per slide without clutter?
```

**Writing examples:**
```
EVAL C1: Opening hook — does the first paragraph grab attention more effectively?
EVAL C2: Paragraph flow — do ideas connect more naturally?
EVAL C3: Tone consistency — is the voice more consistent throughout?
```

**Code examples:**
```
EVAL C1: Readability — is the code easier to scan and understand?
EVAL C2: Naming quality — are variables/functions named more clearly?
EVAL C3: Idiomatic patterns — does the code follow language conventions better?
```

**Comparative eval scoring:**
- Win = 1 point (mutated version is clearly better)
- Tie = 0.5 points (no meaningful difference)
- Loss = 0 points (baseline was better — mutation hurt this dimension)

**Key rule:** Comparative evals only work when comparing outputs from the SAME prompt. Never compare outputs from different prompts.

**When to use comparative evals:**
- Binary evals are at or near 100% but output quality feels flat
- The skill has subjective quality dimensions (aesthetics, tone, readability, elegance)
- You want to push from "correct" to "excellent"

### Code/technical skills (code generation, configs, scripts)

**Bad evals:**
- "Is the code clean?" -> subjective
- "Does it follow best practices?" -> which best practices?

**Good evals:**
- "Does the code run without errors?"
- "Does the output contain zero TODO or placeholder comments?"
- "Are all function and variable names descriptive (no single-letter names except loop counters)?"
- "Does the code include error handling for all external calls (API, file I/O, network)?"

### Document skills (proposals, reports, decks)

**Bad evals:**
- "Is it comprehensive?" -> compared to what?
- "Does it address the client's needs?" -> too open-ended

**Good evals:**
- "Does the document contain all required sections: [list them]?"
- "Is every claim backed by a specific number, date, or source?"
- "Is the document under [X] pages/words?"
- "Does the executive summary fit in one paragraph of 3 sentences or fewer?"

---

## common mistakes

### 1. Too many evals
More than 6 evals and the skill starts gaming them — optimizing for passing the test instead of producing good output. Like a student who memorizes answers without understanding the material.

**Fix:** Pick the 3-6 checks that matter most. If everything passes those, the output is probably good.

### 2. Too narrow / rigid
"Must contain exactly 3 bullet points" or "Must use the word 'because' at least twice" — these create skills that technically pass but produce weird, stilted output.

**Fix:** Evals should check for qualities you care about, not arbitrary structural constraints.

### 3. Overlapping evals
If eval 1 is "Is the text grammatically correct?" and eval 4 is "Are there any spelling errors?" — these overlap. You're double-counting.

**Fix:** Each eval should test something distinct.

### 4. Unmeasurable by an agent
"Would a human find this engaging?" — an agent can't reliably answer this. It'll say "yes" almost every time.

**Fix:** Use the subjective-to-binary conversion technique above. "Engaging" -> "Does the first sentence contain a specific claim, story, or question?"

### 5. Overfitting evals (teaching to the test)
If evals are too specific to the test inputs, the skill gets better at those exact scenarios but worse at everything else.

**Fix:** Write evals at the principle level, not the micro-rule level. "Contains concrete examples" is better than "Contains an example about databases specifically."

---

## evals.json schema

Define your test suite as a structured file (recommended for reuse and automation):

```json
{
  "skill_name": "blog-writer",
  "evals": [
    {
      "id": 1,
      "prompt": "Write a blog post about AI automation for small businesses",
      "expected_output": "1500-3000 word blog post with practical advice and CTAs",
      "assertions": [
        {
          "text": "Does the first paragraph start with empathy or a problem statement?",
          "type": "binary",
          "category": "structure",
          "pass": "The opening names a concrete scenario, data point, or provocative question",
          "fail": "The opening is a vague generality"
        },
        {
          "text": "Are there between 3 and 6 H2 headings?",
          "type": "binary",
          "category": "structure",
          "pass": "3-6 H2 headings present",
          "fail": "Fewer than 3 or more than 6 H2 headings"
        },
        {
          "text": "Is the total length between 1500-3000 characters?",
          "type": "binary",
          "category": "length",
          "pass": "Word count is within range",
          "fail": "Word count is outside range"
        },
        {
          "text": "Is there a CTA at the end of the post?",
          "type": "binary",
          "category": "inclusion",
          "pass": "Clear call to action present in final section",
          "fail": "No actionable CTA found"
        },
        {
          "text": "Is the post free of em dashes?",
          "type": "binary",
          "category": "exclusion",
          "pass": "No em dashes found",
          "fail": "One or more em dashes present"
        }
      ]
    }
  ]
}
```

### Design guidelines

| Item | Recommendation | Reason |
|---|---|---|
| Test prompts | 3-5 | Cover variety without excessive cost |
| Assertions per prompt | 4-6 | Sufficient coverage, not overwhelming |
| Total assertions | 15-30 | Statistically meaningful pass rate |
| Assertion text | Natural language yes/no | So the AI grader can judge it |

### Test prompt design

Cover different scenarios:
- **Prompt 1:** Most common use case
- **Prompt 2:** Edge case (short input, unusual request)
- **Prompt 3:** Complex use case (multiple requirements at once)
- **Prompt 4:** A pattern that has failed before
- **Prompt 5:** A case that requires reference file usage

---

## the eval template

**Binary eval** — copy this for each:

```
EVAL [N]: [Short name]
Type: binary
Question: [Yes/no question]
Pass: [What "yes" looks like — one sentence, specific]
Fail: [What triggers "no" — one sentence, specific]
Category: [structure | length | inclusion | exclusion | format | logic]
```

**Comparative eval** — copy this for each:

```
EVAL [N]: [Short name]
Type: comparative
Dimension: [One specific quality aspect to compare]
Method: Screenshot baseline + mutated output from same prompt. Agent picks winner.
Win: [What "mutated is better" looks like]
Loss: [What "baseline was better" looks like]
Category: comparative
```

Example:

```
EVAL 1: Opening hook
Question: Does the first sentence contain a specific claim, story, or question rather than a generic statement?
Pass: The opening names a concrete scenario, data point, or provocative question
Fail: The opening is a vague generality like "In today's fast-paced world..." or "AI is changing everything..."
Category: structure
```

---

## asking the agent to generate evals for you

```
Analyze this SKILL.md and create an evals.json file.
- 5 test prompts covering different scenarios
- 5 binary assertions per prompt
- Every assertion must be judgeable as true/false
- Convert any subjective criteria into specific, observable signals
- Tag each assertion with a category: structure, length, inclusion, exclusion, format, or logic
```

Review the generated evals before running them. The human review phase in the main autoresearch loop will also catch any evals that don't work in practice.

---

## false positive tracking (outer loop — periodic)

> Run this only when real-world performance data is available.

The inner loop optimizes the skill against eval criteria. But what if the eval criteria themselves are wrong? A high eval score with poor real-world results = **false positive**.

| Eval Score | Real Performance | Meaning | Action |
|---|---|---|---|
| High | High | Evals are working | Keep evals |
| High | Low | **False positive** | Fix evals |
| Low | High | Missing success pattern | Add new eval criteria |
| Low | Low | Correctly filtered | Keep evals |

**When to run:** After 10+ real-world outputs with performance data. Monthly review, not after every experiment.

**How to run:**
1. Compare eval winners against real performance
2. Identify false positives: high eval score but low real performance
3. Analyze what the evals missed
4. Update eval criteria and log with `"source": "false-positive-correction"`
5. Re-run the inner loop with updated evals

**Caution:** Need minimum 10 data points. Account for external factors (SEO changes, seasonality). Blog content has 1-2 week lag; social media is faster (24-48h).
