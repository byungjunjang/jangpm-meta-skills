# Mutation Guide

How to choose what to change and how to change it when optimizing a skill.

---

## Mutation levels — what to change

Skills are not just a SKILL.md file. Most skills have reference files, templates, examples, and design assets. Mutations should target the right level:

| Level | Target | When to use | Examples |
|-------|--------|-------------|---------|
| **L1: Prompt rules** | SKILL.md text | Rule violations, missing instructions | Add anti-pattern, reword ambiguous rule, add example |
| **L2: Reference assets** | `references/` files (templates, patterns, CSS, examples) | Output follows rules but quality is flat | Change a pattern's HTML/CSS, adjust design tokens, add new template variant |
| **L3: Eval calibration** | Eval criteria or thresholds | Eval produces false positives/negatives | Exclude edge case from check, adjust threshold, fix measurement logic |

Start at L1 (cheapest, fastest feedback). Move to L2 when L1 hits diminishing returns. Use L3 sparingly and only when you have evidence of eval mismatch.

---

## L1 → L2 transition signals

Switch to reference asset mutations when:

- Binary evals are 90%+ but comparative evals are stagnant
- 3 consecutive L1 mutations are discarded (rules aren't the bottleneck anymore)
- The outputs follow all the rules but quality feels flat — "correct but not good"

Staying at L1 too long is the most common autoresearch mistake. Once the rules are solid, the leverage shifts to the patterns, templates, and examples in `references/`.

---

## L1 good mutations (prompt rules)

- Add a specific instruction that addresses the most common failure
- Reword an ambiguous instruction to be more explicit
- Add an anti-pattern ("Do NOT do X") for a recurring mistake
- Move a buried instruction higher in the skill (priority = position)
- Add or improve an example that shows the correct behavior
- Remove an instruction that's causing over-optimization

## L2 good mutations (reference assets)

- Modify a pattern/template's structure (HTML, CSS, layout)
- Adjust design system tokens (colors, spacing, typography scale)
- Add a new pattern variant or example file
- Change default values in a config template
- Update code snippets or boilerplate in reference files

## Bad mutations (any level)

- Rewriting the entire skill from scratch
- Adding 10 new rules at once
- Making the skill longer without a specific reason
- Adding vague instructions like "make it better" or "be more creative"

---

## Bundled mutations (L2)

Some changes are interdependent — modifying one thing without adjusting related things makes the output worse. This is especially common at L2 (reference assets). When you can identify a coherent group of related changes, bundle them into a single experiment instead of testing each in isolation:

```
Mutation bundle: "content-cards pattern redesign"
Level: L2
Changes:
  - card internal padding 16px → 20px
  - icon size 24px → 32px
  - add accent color badge to card header
Rationale: These are interdependent — testing them separately
           would produce 3 experiments that each look worse in isolation.
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
