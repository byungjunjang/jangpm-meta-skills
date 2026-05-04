# Dashboard Guide

The dashboard is the user's window into the optimization. Without it, auto mode is a black box.

## Creating the dashboard

Create a live HTML dashboard at `autoresearch-[skill-name]/dashboard.html` and open it before running any experiments.

The dashboard must:

- Show a score progression line chart (experiment on X, pass rate % on Y)
- Show a skill_lines progression line (to track prompt bloat)
- Show colored bars per experiment: green=keep, red=discard, blue=baseline, yellow=human-reviewed
- Show a table of all experiments with: #, score, pass rate, skill_lines, status, description
- Show per-eval breakdown: which evals pass most/least
- Show current status: "Running experiment [N]..." or "Awaiting human review" or "Idle"

**If comparative evals are used — add a comparison view** with before/after output pairs and per-dimension verdicts.

Generate as a single self-contained HTML file with inline CSS/JS. Prefer zero external dependencies so the dashboard still works over `file://` and in network-restricted environments. If you want charts, use inline SVG or canvas code you write into the file.

## Serving — no server needed

**Do NOT use `python -m http.server`.** Instead, inline the data directly into the HTML file.

Every time you update `results.json`, also update `dashboard.html` by replacing the data inline:

```html
<script>
// This line gets replaced after every experiment
const RESULTS_DATA = /* results.json content inserted here */;
</script>
```

The update process after each experiment:
1. Update `results.json` with the latest experiment data
2. Read the current `dashboard.html`
3. Replace the `RESULTS_DATA = ...;` line with the updated JSON content
4. Write the updated `dashboard.html`

The file works with `file://` protocol directly — just open it:
- macOS: `open autoresearch-[skill-name]/dashboard.html`
- Linux: `xdg-open autoresearch-[skill-name]/dashboard.html`

The browser will show the latest data when the page is refreshed. No auto-refresh needed since data is inlined, but you can add a meta refresh tag for convenience:

```html
<meta http-equiv="refresh" content="30">
```

## results.json schema

Update `results.json` after every experiment with:

```json
{
  "skill_name": "[name]",
  "status": "running | complete | paused",
  "mode": "human-review | auto",
  "current_experiment": 5,
  "baseline_skill_lines": 85,
  "experiments": [
    {
      "id": 0,
      "score": 13,
      "max_score": 20,
      "pass_rate": 0.65,
      "skill_lines": 85,
      "status": "baseline",
      "description": "Initial baseline run",
      "comparative_verdicts": {}
    }
  ],
  "eval_breakdown": {
    "eval_1_name": { "pass": 4, "fail": 1 },
    "eval_2_name": { "pass": 3, "fail": 2 }
  },
  "termination_check": {
    "consecutive_95_plus": 0,
    "target": 3
  }
}
```

When the run finishes, set status to `"complete"`.
