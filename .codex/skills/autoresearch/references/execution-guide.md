# How to Run the Target Skill

Each experiment requires a repeatable run harness. In Codex, "I read the skill and tried to follow it" is not enough. You must be able to say exactly how one run starts, where its outputs go, and how the next run stays comparable.

## Method 1: Sequential current-agent run (default)

Run the target skill in the current agent from the target project's working directory using a written harness. This is the default because it avoids unauthorized delegation and is always available.

Use this mode when:
- The user did not explicitly authorize subagents
- The target skill can be executed inside the current workspace/session
- Some context contamination risk is acceptable and will be noted in the log

## Method 2: Fresh subagent run (explicit user approval only)

If the user explicitly asked for delegation, parallel runs, or subagents, use `spawn_agent` to run a bounded execution task in the target project's working directory.

Use this mode when:
- You need a fresher execution context to reduce optimizer bias
- The skill depends on a clean conversational context
- The delegated task is narrowly scoped to "run the skill once and save outputs"

Execution rules for subagents:
- Pass only task-local context: target path, exact test prompt, output location, and any required runtime inputs.
- Do not pass your hypotheses, suspected bug, intended fix, or full eval reasoning unless the execution task truly requires them.
- Use `fork_context: true` only when the target skill depends on the exact current thread context. Otherwise keep the subagent context minimal.
- If you are blocked waiting for results, use `wait_agent` sparingly.

Example shape:

```text
spawn_agent(
  agent_type="default",
  message="Work in /path/to/project. Execute the target skill once with this prompt: <test prompt>. Save every produced artifact under <run-dir> and report only the produced files and notable failures."
)
```

## Key rules

- Never use external services, APIs, or intermediary servers just to orchestrate the run. Keep the execution loop local to Codex unless the target skill itself explicitly requires an external dependency and the user already approved that operating mode.
- Each experiment must start from a clean state — don't let outputs from one experiment leak into the next.
- If the current agent is not fresh, note the context contamination risk in the changelog or results.
- If the skill takes longer than 10 minutes per prompt, reduce the test scope (fewer items, simpler sites) rather than increasing timeouts.
- **Save all outputs into `runs/exp-N/<prompt-id>/`** — copy or move every artifact the skill produces (files, screenshots, generated code, etc.) into the experiment's run folder. Never leave experiment outputs only in the skill's native output directory.
- Before baseline, write `run-harness.md` with the exact execution protocol. Treat harness drift as a stop condition until revalidated.
