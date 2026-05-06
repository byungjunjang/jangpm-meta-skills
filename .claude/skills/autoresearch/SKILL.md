---
name: autoresearch
description: Autonomously optimize any Claude Code skill or agent system by running it repeatedly, scoring outputs against evals (binary for rules + comparative for quality), mutating any owned artifact — the skill's prompt, reference assets, and executable artifacts (scripts, agent/subagent definitions, MCP servers, hooks, harness code) — and keeping improvements. Based on Karpathy's autoresearch methodology. Use this skill whenever the user mentions optimizing a skill, improving a skill or agent, running autoresearch, making a skill or agent better, self-improving a skill, benchmarking a skill, evaluating a skill, running evals on a skill, optimizing an agent system, or any request to iteratively test and refine a skill or agent — even if they don't use the word "autoresearch" explicitly. Also trigger on 스킬 개선, 스킬 최적화, 스킬 벤치마크, 스킬 평가, 에이전트 개선, 에이전트 최적화. Outputs an improved target skill file (and any mutated executable artifacts), a results log, a changelog, and a research log of meaningful direction shifts.
---

# Autoresearch for Skills

Most skills work about 70% of the time. The other 30% you get garbage. The fix isn't to rewrite the skill from scratch. It's to let an agent run it dozens of times, score every output, and tighten the right artifact — prompt, reference asset, or executable code — until that 30% disappears.

This skill adapts Andrej Karpathy's autoresearch methodology (autonomous experimentation loops) to Claude Code skills and agent systems. Karpathy mutated ML training code; here we mutate every artifact a skill owns: SKILL.md prose, reference assets in `references/`, and executable artifacts the skill invokes (scripts, agent/subagent definitions, MCP servers, hooks, harness code).

---

## the core job

Run a loop: generate outputs → score against evals → mutate the skill → keep improvements → repeat.

**Output:** An improved target skill file + `results.json` + `results.tsv` + `changelog.md` + `research-log.json` + live HTML dashboard.

---

## project setup (required)

autoresearch modifies the target skill file on every experiment. To prevent Claude Code from prompting for approval each time, add the following permissions to `.claude/settings.json` at the project root.

```json
{
  "permissions": {
    "allow": [
      "Edit(.claude/skills/**)",
      "Write(.claude/skills/**)",
      "Edit(~/.claude/skills/**)",
      "Write(~/.claude/skills/**)"
    ]
  }
}
```

The project-local paths (`.claude/skills/**`) cover skills in this repo and are safe to commit. If you're optimizing a globally installed skill (`~/.claude/skills/`), also add the global paths locally — but do not commit them, as they grant broad write access to all installed skills on any collaborator's machine.

If `.claude/settings.json` already exists, add only the entries you need to the `permissions.allow` array. Without these permissions, autoresearch will require manual approval every time it modifies the target skill file, which breaks the autonomous loop.

---

## step 0: gather context

**STOP. Do not run any experiments until all fields below are confirmed with the user.**

1. **Target skill(s)** — Which skill to optimize? (exact path to the target `SKILL.md`). For pipelines, list all skills in execution order.
2. **Pipeline mode** — Single skill or multi-skill pipeline? Default: single. See `references/pipeline-guide.md` for pipeline details.
3. **Owned executable artifacts** — Every script, tool implementation, agent/subagent definition, MCP server, hook, and harness file the skill invokes. List them with paths. Default: all in-scope as L2b mutation candidates unless the user explicitly excludes them. If the skill is pure prompt + static references, this list is empty and L2b is unused. See `references/mutation-guide.md` for the L2a/L2b distinction.
4. **Test inputs** — 3-5 different prompts/scenarios covering different use cases. See `references/eval-guide.md` (Test prompt design section) for what makes a good test input.
5. **Eval criteria** — Binary checks for rules (3-6) + comparative checks for quality dimensions (0-5). See `references/eval-guide.md`.
6. **Runs per experiment** — How many times to run the skill per mutation? Default: 5.
7. **Budget cap** — Optional. Max experiment cycles before stopping. Default: no cap.
8. **Termination conditions** — When to stop auto mode. Default: 95%+ binary pass rate for 3 consecutive experiments. See `references/mutation-guide.md` for custom conditions.
9. **Human review mode** — Review the first few experiments before full auto? Default: yes (first 3). Set to `skip` for fully autonomous.

If the user provides an `evals.json` file, use that instead of asking for items 4-5.

---

## step 1: read the skill

Before changing anything, read and understand the target skill completely.

1. Read the full target skill file
2. Read any files in `references/` that the target skill links to (L2a candidates)
3. Read every executable artifact the skill invokes — scripts, tool implementations, agent/subagent definitions (e.g., `agents/openai.yaml`), MCP server code, hook scripts, harness code (L2b candidates). Use the list captured in `Step 0` item 3 as the starting set; verify by tracing every command, tool call, and subagent dispatch the skill performs.
4. Identify the skill's core job, process steps, and output format
5. Note any existing quality checks or anti-patterns already in the skill

Do NOT skip this. You need to understand what the skill does before you can improve it. Skipping step 3 in particular causes the loop to converge on prompt-only mutations even when the real bottleneck is in the script or agent code.

For **pipeline mode**, read `references/pipeline-guide.md` and map the full data flow across all skills.

---

## step 2: build the eval suite

Convert the user's eval criteria into a structured test. See `references/eval-guide.md` for full templates, examples, and the assertion taxonomy.

**Three eval types:**

- **Binary evals** — objective rule compliance (yes/no). Use for hard rules.
- **Comparative evals** — subjective quality improvement. Judge whether a mutation improved quality along a specific dimension (win=1, tie=0.5, loss=0). Every skill should have at least 1-2 comparative evals alongside binary checks — binary alone plateaus quickly.
- **Fidelity evals** — pipeline stage consistency (pipeline mode only). See `references/pipeline-guide.md`.

**Scoring — two axes, reported separately:**

- **Binary pass rate** = `binary_passes / (binary_evals × runs)` → tracks rule compliance
- **Comparative win rate** = `comparative_wins / (comparative_evals × runs)` (ties = 0.5) → tracks quality improvement

Report both numbers. A mutation that improves comparative win rate while holding binary pass rate is a win even if the combined number looks flat. Termination conditions apply to binary pass rate by default.

### Eval type hierarchy (ordered by determinism)

When writing evals, use the highest tier possible. LLM-as-judge is a last resort.

**Tier 1 — Deterministic checks (first choice)**
grep, regex, file existence, JSON/YAML parse success, character count range, required section presence, etc.
Same input → always same result. Most reliable.

Examples:
- "Does the output have a ## 요약 section?" → `grep -q "^## 요약" output.md`
- "Is it valid JSON?" → `python -c "import json; json.load(open('output.json'))"`
- "Is it between 500 and 2000 characters?" → `wc -c output.txt | awk '{exit ($1<500 || $1>2000)}'`

**Tier 2 — Structural validation**
Programmatically verify structural properties of the output. Requires some parsing logic but is still deterministic.

Examples:
- Do markdown headings follow the correct hierarchy? (H1 → H2 → H3)
- Does the table have the same column count across all rows?
- Do code blocks have a language specifier?

**Tier 3 — LLM-as-judge (last resort)**
Use only for items that cannot be verified programmatically — content quality, tone, accuracy.

**Goal: at least 50% of all evals should be Tier 1-2.** An eval suite built entirely on Tier 3 has too much noise to reliably detect the effect of mutations.

### Rules for all evals

- Specific enough to be consistent. "Is the text readable?" is too vague. "Are all words spelled correctly with no truncated sentences?" is testable.
- Not so narrow that the skill games the eval.
- Each eval should test something distinct — no overlapping checks.

**Before finalizing, run the 3-question test on each eval:**

1. Could two different agents score the same output and agree? (if not → tighten)
2. Could a skill game this eval without actually improving? (if yes → too narrow)
3. Does this eval test something the user actually cares about? (if not → drop it)

---

## step 3: define the live dashboard

Read `references/dashboard-guide.md` for the full dashboard spec. Do not create any files here — `autoresearch-[skill-name]/dashboard.html` is created as part of step 5 folder setup.

**Key rule for dashboard HTML:** Never use `fetch()` or XHR to load data from the browser. After each experiment, inline the latest data directly into `<script>const RESULTS_DATA = ...;</script>` inside dashboard.html. This lets the file be opened with the `file://` protocol without a server. This rule applies to the dashboard HTML only — reading `results.json` as an agent step is expected and required.

---

## step 4: define the run harness

Before running any experiments, define the exact repeatable procedure that constitutes "running the target skill." Write the harness content here; the file is saved to `autoresearch-[skill-name]/run-harness.md` as part of step 5 folder setup.

**A trustworthy harness specifies:**
1. **Input** — which test prompt, in what format, passed how
2. **Execution** — which command or agent invocation runs the skill
3. **Output capture** — where artifacts land and how they're saved to `runs/exp-N/<prompt-id>/`

**Acceptable harnesses:**
- A local script or command that runs the workflow end to end
- A bounded agent invocation with a fixed prompt and deterministic artifact capture
- A manual protocol — as long as the procedure is written down and followed identically each run

If you cannot define a trustworthy harness, do not proceed with autoresearch. Switch to "skill rewrite + manual review" mode instead.

See `references/execution-guide.md` for execution patterns (subagent vs direct) and key rules.

---

## step 5: establish baseline (or resume)

**First, check if `autoresearch-[skill-name]/` already exists.**

### If the folder already exists → RESUME

Do NOT create a new folder or re-establish baseline. Continue from the previous run:

1. Read `changelog.md` and `research-log.json` to understand what was already tried
2. Load `results.json` to find the current best score and next experiment number
3. Read `<target-skill-filename>.baseline` to understand the original starting point
4. If autoresearch branch exists, `git checkout autoresearch/[skill-name]`
5. Tell the user the path to `dashboard.html` — open it with `file://` in a browser to track progress
6. Resume the experiment loop from where it left off — skip directly to step 6 or step 7 as appropriate
7. New experiment numbers continue from the last one (e.g., if last was exp-7, next is exp-8)

If a new model is being used, also read the research log to continue from the last direction.

### If the folder does NOT exist → NEW BASELINE

Run the skill AS-IS before changing anything. This is experiment #0.

1. Create `autoresearch-[skill-name]/` with `runs/baseline/`
2. Create `results.json`, `changelog.md`, `research-log.json`, `dashboard.html`, `run-harness.md` (content from step 4) → tell the user the path to `dashboard.html` so they can open it with `file://` in a browser
3. Back up the original skill as `<target-skill-filename>.baseline`
4. Run the skill with test inputs, copy all outputs into `runs/baseline/<prompt-id>/`
5. Score every output against every eval, record baseline score
6. `git checkout -b autoresearch/[skill-name]` (if branch already exists, use `-N` suffix)
7. Add `autoresearch-[skill-name]/` to `.gitignore` (logs accumulate independently of rollbacks)
8. `git add <target-skill-path> .gitignore && git commit -m "autoresearch: baseline ([score]/[max])"`

**IMPORTANT:** If baseline is 90%+, confirm with the user whether further optimization is worthwhile.

For prompt rotation and heavy pipelines, see `references/pipeline-guide.md`.

---

## step 6: human review phase (optional)

> Skip this step entirely if the user set human review mode to `skip`.

The first 3 experiments run with human review. This is where subjective judgment — tone, aesthetic sense, brand fit, personal preference — gets baked into the optimization direction before the autonomous loop takes over.

**For each human-reviewed experiment:**

1. **Analyze failures** and form a hypothesis (same as step 7)
2. **Make ONE change** to the target skill file
3. **Commit the change:** `git add <mutated-files> && git commit -m "autoresearch: [one-line description]"`
4. **Run the experiment** and score it
5. **Present results** showing: the change and why, before/after score, 2-3 sample outputs, keep/discard recommendation
6. **Ask the user:** "Does this direction feel right?" / "Anything the evals aren't catching?"
7. **If subjective feedback is given**, note it in changelog.md as `[HUMAN INSIGHT]` and incorporate into the target skill file. Do NOT add it as a new eval.
8. **Keep or discard** (same rules as step 7). DISCARD → check for unrelated uncommitted changes first (`git status --porcelain`). If any exist outside the checkpointed target files, stash them: `git stash`. Then `git reset --soft HEAD~1`. Restore only the mutated files by explicit path, for example `git restore <target-skill-path> <reference-path>`. Then `git stash pop` if you stashed.
9. **Log the result** with status `human-reviewed`.

**After 3 human-reviewed experiments (or "go auto"):** Switch to auto mode. Tell the user: "Switching to auto mode. Check the dashboard anytime."

---

## step 7: run the autonomous experiment loop

**You are now past the confirmation phase (step 0) and the human review phase (step 6). The following autonomous loop rules apply from this point forward.**

This is the core autoresearch loop. Once started, run autonomously until stopped.

**NEVER STOP.** Once the loop starts, never pause to ask for confirmation. The user may be away. Keep running until the user manually stops you or a stop condition is reached.

**LOOP:**

1. **Analyze failures.** Look at which evals fail most. Read the actual failing outputs. Identify the pattern.

2. **Form a hypothesis.** Pick a mutation at the right level. See `references/mutation-guide.md` for the four mutation levels (L1: prompt rules, L2a: reference assets, L2b: executable artifacts the skill invokes, L3: eval calibration), good/bad mutation examples, bundled mutations, and transition signals. If the failure stems from execution (wrong format, build error, tool returns garbage, subagent malformed result), go to L2b — do not paper over execution bugs with more prompt rules.

3. **Make the change.** Edit the target file(s) at the chosen mutation level.

4. **Commit the change:** `git add <mutated-files> && git commit -m "autoresearch: [one-line description]"`

5. **Run the experiment.** Execute the skill with the test inputs. **Save all outputs into `runs/exp-N/`** — copy or move every artifact the skill produces into `runs/exp-N/<prompt-id>/` so every experiment is self-contained and comparable.

6. **Score it.** Run every output through every eval. Calculate total score. Measure `skill_lines` with `wc -l <target-skill-path>`.

7. **Decide: keep or discard.**

   Consider line count changes in the target skill file alongside the score:

   | Score change | Line count change | Decision |
   |-----------|-----------|------|
   | Improved (+2 or more) | Increased | **KEEP** — meaningful improvement justifies added complexity |
   | Marginal improvement (+1) | Increased by 10+ lines | **DISCARD** — not enough improvement for the added complexity |
   | Same (±0) | Decreased | **KEEP** — same performance with a shorter prompt |
   | Same (±0) | Increased | **DISCARD** — complexity grew with no benefit |
   | Worse | Any | **DISCARD** |

   When two versions have the same score, always prefer the shorter one.

   - **KEEP** → keep this commit. It is the new baseline.
   - **DISCARD** → check for unrelated uncommitted changes first (`git status --porcelain`). If any exist outside the checkpointed target files, stash them: `git stash`. Then `git reset --soft HEAD~1`. Restore only the mutated files by explicit path. Then `git stash pop` if you stashed.

   **Individual eval regression detection:** Even if the total score goes up, strongly consider DISCARD if an eval that previously passed now fails. A gain in one area that hides a regression in another degrades the skill's long-term quality.

8. **Log the result** and update results.json / dashboard.

9. **If this was a direction-level change**, log it in research-log.json (see step 8).

10. **Repeat.** Go back to step 1.

### Periodic deletion experiments

Every 5th experiment, intentionally attempt a "deletion mutation." Find recently added rules that are not actually contributing to the score and remove them. If the score holds after removing a rule, that is the best possible experiment result. If the target skill file has grown to more than 200% of its baseline size, record a warning in the changelog.

### stop conditions

- The user manually stops you
- Budget cap reached
- 95%+ pass rate for 3 consecutive experiments (or custom termination conditions — see `references/mutation-guide.md`)
- System-level timeout or resource limit

Running out of ideas is not a reason to stop → see the "when stuck" strategies below.

### when stuck — strategies specific to skill prompt optimization

After 3 consecutive discards or when ideas run dry:

1. **Reorder instructions**: Move the instruction most related to the most frequently failing eval to the top of the target skill file. LLMs tend to follow instructions near the start of the prompt more strongly.
2. **Negative → positive framing**: Convert "do not X" into "always do Y." Example: "do not number the list" → "start every list item with a bullet (•)"
3. **Replace examples**: Instead of adding new examples, replace existing ones with examples that directly address the failure pattern. Do not increase the total number of examples.
4. **Deletion experiment**: Remove one instruction and measure the score. If two instructions conflict, removing one is itself an improvement.
5. **Increase specificity**: Add concrete numbers or formats to vague instructions. Example: "write concisely" → "limit each section to 3-5 sentences"
6. **Adjust the persona**: Change the role description at the top of the skill. Example: "You are a professional technical writer" → "You are a technical guide writer for non-developers"
7. **Combine previous near-misses**: Apply two mutations from the changelog that were each discarded but scored close to baseline — simultaneously. (This is the one exception to the "one change at a time" rule.)

---

## step 8: maintain the logs

Three files, three different jobs. Keep them separate. See `references/logging-guide.md` for templates and schemas.

- **changelog.md** — every experiment, kept or discarded. Score, change, reasoning, result, failing outputs, human insight.
- **research-log.json** — direction shifts only. Survives model upgrades. If exceeds 30 entries, keep 10 most recent + pattern summary.
- **results.json** — machine-readable score file, one object per experiment. Contains the same fields as results.tsv plus full eval breakdowns. This is the file inlined into dashboard.html after each experiment.
- **results.tsv** — tab-separated, one row per experiment. Columns: `experiment	score	max_score	pass_rate	skill_lines	status	description`. Used for external analysis and as the authoritative score log.

---

## step 9: deliver results

When the user returns or the loop stops, present:

1. **Score:** Baseline → Final, reported on both axes:
   - Binary pass rate: `X% → Y%` (rule compliance)
   - Comparative win rate: `X% → Y%` (quality improvement, if comparative evals were used)
2. **Experiments:** total tried, keep rate
3. **Top 3 changes** that helped most (from changelog)
4. **Human insights** incorporated (if any)
5. **Remaining failures** (if any)
6. **Prompt size:** baseline → final line count
7. **Git log:** `git log --oneline autoresearch/[skill-name]`
8. **File locations** for all output files

---

## after the run

These are not loop steps — they apply after autoresearch completes or is paused.

### Real-world validation (recommended 1 week after)

Check the output quality of the improved skill in actual use. If binary pass rate is high but real outputs fall short of expectations, the eval criteria are wrong.
→ Fix the evals and restart from a new baseline.

### When upgrading the model

Reference changelog.md and results.tsv to continue optimizing from where the previous model left off.

### When changing the skill structure

Archive the existing autoresearch folder and start from a new baseline. Use the previous changelog as reference material for what directions worked.

### Periodic review (recommended monthly)

Review the patterns in changelog.md:
- If the same type of mutation is repeatedly discarded → change the approach itself
- If deletion experiments keep getting KEEP → signal that the skill is bloating
- If the last 5 experiments all scored ±0 → time to re-examine the eval criteria

### False positive tracking

If eval score is high but actual output quality is low, that is a false positive. Run a monthly review after 10+ real-world outputs have accumulated. See `references/eval-guide.md` (false positive tracking section) for the full process.

---

## output format

```
autoresearch-[skill-name]/
├── dashboard.html          # live browser dashboard (inline data, no server needed)
├── results.json            # data file (also inlined into dashboard)
├── results.tsv             # raw score log with skill_lines column
├── changelog.md            # detailed log of every mutation
├── research-log.json       # direction shifts and strategic patterns only
├── <target-skill-filename>.baseline       # original skill before optimization
├── run-harness.md          # repeatable procedure for executing the skill
└── runs/                   # one folder per experiment
    ├── baseline/
    ├── exp-1/
    └── exp-N/
```

Plus the improved target skill saved back to its original location.
The git branch `autoresearch/[skill-name]` retains a linear history of all accepted mutations.

---

## worked example

For a concrete walkthrough of 5 experiments (git ratcheting, skill_lines, simplicity decisions, deletion experiments, and mixed Tier 1/2/3 evals), see `references/worked-example.md`.

---

## the test

A good autoresearch run:

1. **Started with a baseline** — never changed anything before measuring
2. **Defined a run harness** — a repeatable execution procedure was written down before any experiment ran
3. **Used appropriate eval types** — binary for rules, comparative for quality, fidelity for pipelines; at least 50% Tier 1-2 evals
4. **Got human input early** — direction validated before going autonomous
5. **Mutated at the right level** — L1 for rules, L2a for static assets, L2b for executable artifacts the skill invokes, L3 for eval calibration
6. **Kept a complete log** — every experiment recorded with skill_lines
7. **Used git ratcheting** — each mutation committed, discards reset, clean linear history
8. **Maintained simplicity** — prompt didn't bloat; periodic deletion experiments ran
9. **Maintained a research log** — direction shifts captured for future models
10. **Reported both axes** — binary pass rate + comparative win rate shown separately
11. **Didn't overfit** — the skill got better at the actual job, not just at passing tests
12. **Quality improved, not just compliance** — before/after comparisons confirm real improvement

If the skill passes all evals but actual output quality hasn't improved — the evals are bad, not the skill. Go to "False positive tracking" in the After the Run section and fix the evals.
