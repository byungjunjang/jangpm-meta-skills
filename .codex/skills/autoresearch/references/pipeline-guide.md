# Pipeline Guide

How to optimize multi-skill pipelines where skills chain together (e.g., `/slide` -> `/export-pptx`).

---

## Reading a multi-skill pipeline

When the target is a **multi-skill pipeline**, read ALL skills in the pipeline and map the data flow:

```
Skill A (generate) -> Output A -> Skill B (convert) -> Output B -> Skill C (publish) -> Output C
```

For each pipeline stage, identify:
1. **What it receives** as input (previous stage's output)
2. **What it produces** as output
3. **Where quality can degrade** between stages (fidelity gaps)

---

## Pipeline mutation strategy

When an eval fails, determine which stage is responsible:
- If the *source* output is wrong -> fix the upstream skill
- If the source is correct but the *target* doesn't match -> fix the downstream skill (converter, helper functions, tokens)
- If both are wrong -> fix upstream first, then re-evaluate downstream

---

## Pipeline eval strategy

Use all three eval types:
- **Binary evals:** applied to the final output (catches rule violations)
- **Comparative evals:** applied to the upstream output vs baseline (catches quality regression)
- **Fidelity evals:** applied between stages (catches conversion degradation)

---

## Fidelity evals — pipeline stage consistency

Fidelity evals measure how accurately the downstream output preserves the upstream output's quality. Neither binary nor comparative evals catch this — you need to compare two representations of the *same* content.

```
EVAL [number]: [Short name]
Type: fidelity
Source: [upstream output — e.g., HTML screenshot, source code]
Target: [downstream output — e.g., PPTX screenshot, compiled binary]
Dimension: [One specific fidelity aspect to compare]
Method: Side-by-side comparison of source vs target on this dimension.
Pass condition: Target faithfully reproduces source on this dimension.
Fail condition: Target has visible degradation, missing elements, or misalignment.
```

**Common fidelity dimensions:**

| Pipeline type | Example fidelity dimensions |
|--------------|---------------------------|
| Visual (HTML->PPTX/PDF) | Layout match, color fidelity, element completeness, text sizing, grid spacing, card internal layout |
| Code (generate->build) | Build success, runtime behavior match, API contract fidelity |
| Data (transform->load) | Row count preservation, value accuracy, schema conformance |
| Translation (lang A->B) | Meaning preservation, format retention, terminology consistency |

**Fidelity eval rules:**
- Each eval tests ONE dimension — "layout match" and "color fidelity" are separate evals
- Capture both source and target screenshots/outputs for comparison
- Known technical limitations are exempt (document them explicitly as "accepted differences")
- When fidelity fails, determine which pipeline stage to fix
- Score: pass=1, fail=0 (same as binary)

**Fidelity gap improvement loop:**

When fidelity evals reveal gaps, run a targeted sub-loop:
1. Compare source vs target for every item (e.g., every slide, every page)
2. List specific gaps with severity (HIGH/MED/LOW)
3. Fix the responsible code (converter, helper functions, tokens)
4. Regenerate the target
5. Re-compare — repeat until gaps reach zero

This loop runs *within* a single experiment, not as a separate experiment. Log the gaps found and fixes applied in the experiment's changelog entry.

---

## Prompt rotation strategy

When running multiple test prompts, don't run all prompts every experiment — it's too slow for medium/heavy pipelines. Use rotation:

| Strategy | When to use | How it works |
|----------|-------------|-------------|
| **Round-robin** | Medium/heavy pipelines (>2 min per run) | One prompt per experiment, cycle through all. E.g., P1->P2->P3->P1->... |
| **Full eval** | Light pipelines (<1 min) or at milestones | All prompts in one experiment. Also run at every Nth experiment (e.g., every 3rd) as a comprehensive check. |
| **Weighted** | When one prompt is harder/more important | Run the hard prompt 2x more often. E.g., P1->P2->P1->P3->P1->... |

**Rotation prevents overfitting.** If you only test with one prompt, the skill will optimize for that specific case. Different prompts exercise different patterns, languages, and edge cases.

**Log which prompt was used** for each experiment in results.json.

---

## Adapting to heavy pipelines

Some skills have heavyweight execution pipelines (e.g., MCP tool calls -> code generation -> build -> export). If a single skill run takes more than 5 minutes, adapt the experiment parameters:

| Pipeline weight | Single run time | Runs per experiment | Strategy |
|----------------|-----------------|---------------------|----------|
| **Light** | < 1 min | 5 (default) | Run all test prompts every experiment |
| **Medium** | 1-10 min | 2-3 | Rotate test prompts (different prompt each experiment) |
| **Heavy** | 10+ min | 1 | One prompt per experiment, rotate across experiments; create a light-mode shortcut |

**Light-mode shortcuts for heavy pipelines:**

If the pipeline has expensive steps that don't affect the eval (e.g., MCP visual design when evals only check code output), create a bypass:
1. Identify which pipeline steps the eval actually measures
2. Cache or skip upstream steps that don't change between mutations
3. Document the shortcut so the full pipeline is still run for final validation

**Example:** A slide pipeline that runs Pencil MCP -> React -> Build -> PPTX. If evals check the React code, skip Pencil and write React directly. Run the full pipeline only for the final 3 experiments to validate end-to-end.
