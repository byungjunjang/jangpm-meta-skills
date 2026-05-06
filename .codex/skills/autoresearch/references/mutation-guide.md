# Mutation Guide

How to choose what to change and how to change it when optimizing a skill.

---

## Mutation levels — what to change

Skills are rarely a single SKILL.md. Most skills are a system: prompt text + reference assets (templates, examples, CSS, design tokens) + executable artifacts (scripts, tools, agent/subagent definitions, MCP servers, hooks, harness code) the skill orchestrates. Mutations target the right level:

| Level | Target | When to use | Examples |
|-------|--------|-------------|---------|
| **L1: Prompt rules** | SKILL.md text only (inline subagent prompt templates inside SKILL.md count as L1; external subagent/agent definition files are L2b) | Rule violations, missing or ambiguous instructions | Add anti-pattern, reword ambiguous rule, add example |
| **L2a: Reference assets** | `references/` — templates, patterns, CSS, examples, design tokens | Output follows rules but quality is flat | Change a pattern's HTML/CSS, adjust design tokens, add new template variant |
| **L2b: Executable artifacts** | Scripts, tool implementations, agent definition files (e.g., `agents/openai.yaml`), MCP servers, hooks, harness code that the skill invokes | Output failure stems from how the skill *executes* (wrong format, build error, tool returns garbage, subagent produces malformed result) rather than how it *instructs* | Fix a converter script's algorithm, adjust a subagent's role/permissions, improve an MCP tool's schema or error handling, tune a hook's validation logic |
| **L3: Eval calibration** | Eval criteria or thresholds | Eval produces false positives/negatives | Exclude edge case from check, adjust threshold, fix measurement logic |

**Cost ordering:** L1 (cheapest, fastest feedback) → L2a → L2b (larger blast radius, may require build/run cost) → L3 (use sparingly, only with evidence of eval mismatch).

If the skill has no executable artifacts (pure prompt + static references), L2b is unused. If `Step 0` enumerated executable artifacts, L2b is in scope from the start.

---

## Transition signals — when to leave L1

### L1 → L2a (reference assets)

Switch to reference asset mutations when:

- Binary evals are 90%+ but comparative evals are stagnant
- 3 consecutive L1 mutations are discarded (rules aren't the bottleneck anymore)
- Outputs follow all the rules but quality feels flat — "correct but not good"

Staying at L1 too long is the most common autoresearch mistake for documentation- and template-heavy skills. Once the rules are solid, the leverage shifts to patterns, templates, examples, and design tokens in `references/`.

### L1 / L2a → L2b (executable artifacts)

Switch to executable artifact mutations when:

- Output failures stem from the skill's *execution* — wrong output format, build error, tool returns garbage, subagent produces malformed result, agent triggers wrongly
- L1 + L2a mutations have been tried and the bottleneck is clearly downstream of the prompt and static assets
- The same prompt + same templates would still fail without changing the script/tool/agent code

Skipping L2b when needed is the most common autoresearch failure mode for skills that orchestrate code, agents, or tools — the loop converges on a "perfectly worded skill that still produces broken output" because the real bug is in the script, not the prompt.

---

## L1 good mutations (prompt rules)

- Add a specific instruction that addresses the most common failure
- Reword an ambiguous instruction to be more explicit
- Add an anti-pattern ("Do NOT do X") for a recurring mistake
- Move a buried instruction higher in the skill (priority = position)
- Add or improve an example that shows the correct behavior
- Remove an instruction that's causing over-optimization

## L2a good mutations (reference assets)

- Modify a pattern/template's structure (HTML, CSS, layout)
- Adjust design system tokens (colors, spacing, typography scale)
- Add a new pattern variant or example file
- Change default values in a config template
- Update code snippets or boilerplate embedded in reference docs

## L2b good mutations (executable artifacts)

- Fix or refactor a converter/transformer script's algorithm (e.g., HTML→PPTX mapping, parser logic)
- Adjust a tool's input/output schema, validation, or error handling
- Tune a subagent's system prompt, tool permissions, or capability scope in its definition file
- Update an agent definition file's metadata, triggers, or descriptions (e.g., `agents/openai.yaml`)
- Add or relax validation logic in a hook script
- Replace a brittle implementation with a more deterministic one
- Tighten an MCP server's tool descriptions or argument schemas

## Bad mutations (any level)

- Rewriting the entire skill from scratch
- Adding 10 new rules at once
- Making the skill longer without a specific reason
- Adding vague instructions like "make it better" or "be more creative"
- Touching L2b code when the failure is clearly in the prompt (or vice versa) — match the level to the actual bottleneck

---

## Bundled mutations (L2a / L2b)

Some changes are interdependent — modifying one thing without adjusting related things makes the output worse. This is common at L2a (where token + template + pattern are coupled) and especially at L2b (where a script change must align with a schema change must align with a downstream tool's expectations). When changes are clearly coupled, bundle them into a single experiment instead of testing each in isolation:

```
Mutation bundle: "content-cards pattern redesign"
Level: L2a
Changes:
  - card internal padding 16px → 20px
  - icon size 24px → 32px
  - add accent color badge to card header
Rationale: These are interdependent — testing them separately
           would produce 3 experiments that each look worse in isolation.
```

```
Mutation bundle: "subagent dispatch contract tightening"
Level: L2b
Changes:
  - subagent system prompt: add explicit output-schema requirement
  - dispatch helper script: validate returned JSON against the schema
  - agents/openai.yaml: update tool description to reference the schema
Rationale: The prompt change alone would still ship malformed output
           because the dispatch helper does not validate; the schema
           change alone would not propagate to the subagent's prompt.
```

Log bundled mutations as a single experiment with all changes listed. If the bundle fails, you can unbundle and test individual changes — but start bundled when changes are clearly coupled.

---

## Custom termination conditions

The default stop condition (95%+ for 3 consecutive) is too simple for most real optimizations. Define termination as a combination of criteria using AND/OR:

```
termination_conditions:
  - name: "Quality convergence"
    criteria: "Comparative win rate >=80% for 3 consecutive experiments"
  - name: "Fidelity threshold"
    criteria: "Fidelity score >=90%"
  - name: "Minimum experiments"
    criteria: "At least 10 auto experiments completed"
  operator: AND  # ALL conditions must be met
```

**Common condition patterns:**
- **Convergence** — Score >=X for N consecutive experiments (quality has plateaued)
- **Threshold** — A specific metric exceeds a minimum (e.g., fidelity >=90%)
- **Minimum runs** — At least N experiments completed (prevents premature stopping)
- **Combined** — All of the above with AND (strictest), or any with OR (fastest)

Track termination progress in results.json under `termination_check`.
