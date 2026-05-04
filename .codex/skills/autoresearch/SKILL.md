---
name: autoresearch
description: Autonomously optimize any Codex skill by running it repeatedly, scoring outputs against evals (binary for rules + comparative for quality), mutating the skill's prompt and reference assets, and keeping improvements. Based on Karpathy's autoresearch methodology. Use this skill whenever the user mentions optimizing a skill, improving a skill, running autoresearch, making a skill better, self-improving a skill, benchmarking a skill, evaluating a skill, running evals on a skill, or any request to iteratively test and refine a skill — even if they don't use the word "autoresearch" explicitly. Also trigger on 스킬 개선, 스킬 최적화, 스킬 벤치마크, 스킬 평가. Outputs an improved SKILL.md, a results log, a changelog, and a research log of meaningful direction shifts.
metadata:
  short-description: Eval-driven optimization for Codex skills and pipelines
---

# Autoresearch for Skills

Most skills work about 70% of the time. The remaining 30% is where vague instructions, weak examples, and brittle rules show up. The fix is not "rewrite it from scratch." The fix is to run the skill repeatedly, score the outputs, mutate the skill, and keep only what measurably helps.

This skill adapts Andrej Karpathy's autoresearch methodology to Codex skills.

## The Core Job

Take an existing skill, define what good output looks like, then run a loop that:

1. Generates outputs from the skill using test inputs
2. Scores each output against eval criteria
3. Mutates the skill, references, templates, or UI metadata
4. Keeps improvements and discards regressions
5. Repeats until a stop condition is reached

Expected outputs for the target skill path:

- improved target skill file
- `results.tsv`
- `changelog.md`
- `research-log.json`
- `dashboard.html`

## Before Starting: Gather the Experiment Contract

Do not block on a perfect spec, but do establish a minimum viable experiment contract.

1. **Target skill(s)** — exact path to the target `SKILL.md`; for a pipeline, list all skills in order
2. **Pipeline mode** — single skill or multi-skill pipeline; default is single
3. **Test inputs** — 3-5 prompts or scenarios; if missing, draft a starter set and state the assumption
4. **Eval criteria** — 3-6 binary checks plus 1-2 comparative quality checks where possible
5. **Runs per experiment** — default: 3 for light skills, 1-2 for heavy skills, 5 only when cheap
6. **Budget cap** — default: 5 total experiments in one Codex turn unless the user wants more
7. **Termination conditions** — default: stop at budget cap or after 95%+ binary pass rate for 3 consecutive accepted experiments
8. **Human review mode** — default: review baseline plus the first meaningful keep; use `skip` only when the user explicitly wants unattended mode
9. **Execution mode** — default: sequential in the current agent; use subagents only if the user explicitly asks for delegation or parallel agent work
10. **Run harness** — define the exact repeatable command or workflow that constitutes "running the skill"
11. **Versioning mode** — default: `git-assisted` when a clean local git workflow is practical, otherwise `file-checkpoint`

If the user provides an `evals.json`, use that instead of drafting items 3-4.

Execution mode rules:

- Use `sequential` by default
- Do not spawn subagents unless the user explicitly authorized delegation
- Treat "run the skill" as an explicit harness, not a vague conversational attempt
- If fresh runs are unavailable, continue sequentially and note context contamination risk
- Do not assume git is available or appropriate; decide versioning mode explicitly before baseline

## Step 1: Read the Target Skill

Before changing anything:

1. Read the target skill file at the exact path captured in the experiment contract
2. Read linked files in `references/` and relevant helpers in `scripts/`
3. Identify the core job, workflow, output format, and anti-patterns
4. Note any existing quality checks already embedded in the skill
5. If the target is a Codex skill and `agents/openai.yaml` exists, read it and verify the UI metadata still matches the skill

## Step 2: Design the Eval Suite

Use the eval guidance in `references/eval-guide.md`.

Three eval types are allowed:

- **Binary evals** — pass/fail rule compliance
- **Comparative evals** — win/tie/loss on subjective quality dimensions
- **Fidelity evals** — pipeline stage consistency in multi-skill mode

Scoring:

- Binary: pass = 1, fail = 0
- Comparative: win = 1, tie = 0.5, loss = 0
- Fidelity: pass = 1, fail = 0
- `max_score = total assertions x runs per experiment`

Use the highest-determinism eval you can. LLM-as-judge is acceptable only when the rubric is explicit enough for repeatable scoring.

### Eval Determinism Hierarchy

When designing evals, prefer the highest-determinism check available.

**Tier 1 - Deterministic checks**

- regex, required section presence, file existence
- JSON/YAML parse success
- character-count or item-count bounds

**Tier 2 - Structural validation**

- heading hierarchy
- table shape consistency
- code block formatting or schema-level structure

**Tier 3 - LLM-as-judge**

- tone, usefulness, completeness, quality, or other subjective criteria that cannot be checked programmatically

Target at least 50% of the eval suite to be Tier 1-2. If most evals are Tier 3, the loop becomes too noisy to trust.

### Eval Quality Check

Before locking the eval suite, run this 3-question test on each eval:

1. Would two different reviewers likely score the same output the same way?
2. Could the skill game this check without becoming genuinely better?
3. Does this check capture something the user actually cares about?

If any answer is weak, tighten or replace the eval.

## Step 3: Define the Run Harness

Each experiment needs a repeatable harness that executes the skill and collects outputs.

Acceptable harnesses:

- A local script or command that runs the workflow end to end
- A bounded manual protocol with fixed prompt, fixed output path, and deterministic artifact capture
- A delegated subagent task only when the user explicitly approved delegation

Before baseline, write the harness into `run-harness.md` inside the run folder so future experiments are comparable.

Also create the live dashboard before running experiments. Follow `references/dashboard-guide.md` and create `dashboard.html` as a self-contained file that is updated by inlining the latest `results.json` data after each experiment.

If you cannot define a trustworthy harness, stop calling it autoresearch and switch to "skill rewrite + manual review" mode.

See `references/execution-guide.md`.

## Step 4: Establish Baseline

If `autoresearch-[skill-name]/` already exists, skip baseline creation and go to `Resuming a Previous Run`.

Baseline is experiment `#0`.

1. Create `autoresearch-[skill-name]/` and `runs/baseline/`
2. Create `results.json`, `results.tsv`, `changelog.md`, `research-log.json`, `dashboard.html`, and `run-harness.md`
3. Back up the original skill as `<target-skill-filename>.baseline` in the run folder
4. Run the skill as-is with the selected test inputs
5. Copy **all outputs** into `runs/baseline/<prompt-id>/`
6. Score every output against every eval
7. Record the baseline score
8. If versioning mode is `git-assisted`, create a git branch: `autoresearch/[skill-name]` (add `-N` suffix if needed)
9. If versioning mode is `git-assisted` and the run folder should stay untracked, add the autoresearch folder to `.gitignore` only when that is safe for the repo
10. Persist the baseline snapshot:
    - `git-assisted`: commit the baseline skill files explicitly by path, for example
      `git add <target-skill-path> .gitignore && git commit -m "autoresearch: baseline ([score]/[max])"`
    - `file-checkpoint`: record baseline hashes in `run-harness.md` and keep the copied `.baseline` file as the restore source

After baseline, choose one mode explicitly:

- `interactive`: report baseline and wait for approval
- `unattended`: continue until budget or stop condition is hit

Default is `interactive` unless the user explicitly requested unattended looping.

## Step 5: Human Review Phase

Skip this only when the user explicitly set human review mode to `skip`.

In Codex, human review is usually bounded:

- review baseline
- review the first meaningful keep
- expand to 2-3 reviewed experiments only when the skill has strong subjective quality dimensions

For each reviewed experiment:

1. Analyze failures and form one clear hypothesis
2. Make one bounded change
3. Commit only the files mutated in that experiment
4. Run the experiment and score it
5. Present before/after score plus 2-3 representative outputs
6. Ask whether the direction feels right or whether the evals miss something
7. Log human insight as `[HUMAN INSIGHT]` in `changelog.md`
8. Keep or discard using the rollback rules from step 6
9. Mark the result as `human-reviewed`

Only switch to unattended mode if the user explicitly approves it.

## Step 6: Run the Mutation Loop

Autonomy in Codex is batch-based, not open-ended.

Run unattended only when all of these are true:

- the user explicitly asked for unattended auto mode
- the run harness is reliable
- rollback is safe for touched files
- budget cap and stop conditions are written down

Otherwise run a bounded batch and report results.

Loop steps:

1. Analyze failing evals and inspect real failing outputs
2. Form one mutation hypothesis at the right level
3. Checkpoint only the files you plan to touch
4. Make the bounded change
5. If a Codex skill's user-facing purpose changes, update `agents/openai.yaml` too
6. Persist the mutation:
   - `git-assisted`: `git add <mutated-files> && git commit -m "autoresearch: [description]"`
   - `file-checkpoint`: save explicit pre-mutation copies or hashes for each touched file inside the run folder before evaluation
7. Run the experiment and save every produced artifact under `runs/exp-N/<prompt-id>/`
8. Score the outputs
9. Decide `KEEP` or `DISCARD`
10. Log the result
11. If this changed direction meaningfully, record it in `research-log.json`
12. Repeat until batch budget is exhausted or a stop condition is hit

### Mutation Safety Rules

- Each mutation is checkpointed before evaluation
- `KEEP` -> the accepted version becomes the new baseline
- `DISCARD` -> use a non-destructive rollback that matches the selected versioning mode:
  - `git-assisted`: `git reset --soft HEAD~1`, then restore only the checkpointed files to their pre-experiment contents by explicit path
  - `file-checkpoint`: restore only the touched files from the saved pre-mutation copies or the latest accepted baseline copies
- Never use `git reset --hard` or any broad revert that can destroy unrelated user changes
- If the repo was already dirty, record which files were pre-modified and exclude unrelated work from rollback
- If git is unavailable, unwanted, or unsafe for the current repo, stay in `file-checkpoint` mode for the whole run

### KEEP vs DISCARD Rules

Record `skill_lines` for every experiment with `wc -l <target-skill-path>`.

Use these defaults unless the user defined a stricter rule:

| Score change | Prompt size change | Default decision |
|---|---|---|
| Improved meaningfully | Any reasonable increase | `KEEP` |
| Improved marginally | Large prompt increase | `DISCARD` unless the gain fixes an important failure |
| Flat | Shorter or simpler prompt | `KEEP` |
| Flat | Longer or more complex prompt | `DISCARD` |
| Worse | Any | `DISCARD` |

Additional guardrails:

- If an eval that previously passed now fails, treat that as a regression and strongly prefer `DISCARD` even if the total score rose
- When two versions score the same, prefer the shorter and simpler one
- If the mutation changes user-facing behavior, compare representative outputs before keeping it

### Deletion Experiments

Every 5th experiment, try a deletion mutation.

- Remove recently added rules that may not contribute to score
- If the score holds, keep the deletion
- If the target skill file grows past 200% of baseline size, record a bloat warning

### Stop Conditions

Stop when any of these is true:

- budget cap reached
- 95%+ binary pass rate sustained for 3 consecutive accepted experiments
- user stops the run
- system resource or time limit reached
- the run harness is no longer trustworthy

Running out of ideas is not a reason to stop; change mutation level or revisit eval design.

## Step 7: Logging Rules

Use `references/logging-guide.md`.

At minimum:

- `results.tsv` records experiment number, score, keep/discard, and concise rationale
- `changelog.md` records each mutation, per-eval movement, and human insights
- `research-log.json` stores direction shifts only, not every micro edit
- `dashboard.html` should visualize baseline-to-current progress without external runtime dependencies when possible

## Step 8: Report Back

When the loop pauses or ends, present:

1. Score summary: baseline -> final
2. Total experiments tried
3. Keep rate
4. Top 3 helpful changes
5. Human insights incorporated
6. Remaining failure patterns
7. Direction shifts
8. Prompt size change
9. Output file locations
10. Accepted git history

## Step 9: Next Steps

Autoresearch is a continuous improvement system.

- **1 week later:** validate against real-world usage; if the skill still feels wrong, the evals are wrong
- **When upgrading the model:** resume from prior logs instead of starting blind
- **When changing structure heavily:** archive the old run and establish a new baseline
- **Monthly:** review discard patterns, deletion results, and stalled score trends

## Step 10: False Positive Tracking

If eval scores are high but actual output quality is low, you have a false positive problem.

- collect 10+ real outputs
- review where evals failed to capture quality
- tighten the eval suite
- restart from a clean baseline if necessary

## Output Structure

```text
autoresearch-[skill-name]/
├── results.json
├── results.tsv
├── dashboard.html
├── changelog.md
├── research-log.json
├── <target-skill-filename>.baseline
├── run-harness.md
└── runs/
    ├── baseline/
    ├── exp-1/
    └── ...
```

## Resuming a Previous Run

If `autoresearch-[skill-name]/` already exists:

1. Read `changelog.md` and `research-log.json`
2. Read `results.json` to find the best score and next experiment number
3. Read `<target-skill-filename>.baseline`
4. Reconstruct the prior experiment contract from `run-harness.md`, including target path, eval suite, versioning mode, and termination settings
5. Compare the current target files against the last accepted baseline using hashes, git history, or explicit file diff
6. If the target skill, eval contract, or harness changed materially, do **not** resume blindly:
   - either archive the old run and start a fresh baseline
   - or document exactly why the old baseline is still comparable
7. If versioning mode is `git-assisted`, re-checkout the autoresearch branch if needed
8. Re-validate the run harness before resuming
9. Continue from the next experiment number

If the model changed, read the prior research log and avoid re-running obviously poor directions.

## Limitations

| Limitation | Mitigation |
|---|---|
| Evals can check structure better than true quality | Human review plus false-positive tracking |
| Strict evals can suppress creativity | Keep only core rules binary; use comparative evals for quality |
| AI can game evals | Write principle-level assertions, not brittle micro-rules |
| Sequential runs can leak context | Log contamination risk and prefer fresh runs when available |
| Cost grows quickly | Control runs-per-experiment and budget cap |
| Overfitting to prompts | Use diverse prompts and rotate periodically |

## The Test

A good autoresearch run:

1. established a real harness
2. created a baseline before mutating
3. used evals that produce stable scores
4. saved artifacts per experiment
5. improved score without hiding regressions
6. used safe git ratcheting
7. kept the skill simpler when possible
8. recorded direction shifts
9. improved actual output quality, not just compliance

If the skill passes evals but still feels worse in practice, the evals are the problem. Fix them and rerun.
