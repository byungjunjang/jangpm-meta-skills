# Logging Guide

Three files, three different jobs. Keep them separate.

## changelog.md — every experiment, kept or discarded

```markdown
## Experiment [N] — [keep/discard/human-reviewed]

**Score:** [X]/[max] ([percent]%) | **skill_lines:** [N]
**Change:** [One sentence describing what was changed]
**Reasoning:** [Why this change was expected to help]
**Result:** [What actually happened — which evals improved/declined]
**Per-eval detail:** [Which individual evals passed/failed vs previous]
**Failing outputs:** [Brief description of what still fails]
**Human insight:** [If any subjective feedback was given]
**Git:** [commit hash or "soft reset + checkpoint restore"]
```

## research-log.json — direction shifts only

NOT every experiment goes here. Only log **direction shifts** — meaningful changes in approach, strategy, or framing.

```json
{
  "skill_name": "[name]",
  "entries": [
    {
      "revision_number": 3,
      "date": "2026-03-25",
      "change_summary": "Switched from announcement tone to curiosity-trigger tone",
      "change_rationale": "Announcement tone passed evals but felt generic in human review",
      "score_before": 32,
      "score_after": 35,
      "skill_lines_before": 85,
      "skill_lines_after": 89,
      "direction_shift": "announcement -> curiosity trigger",
      "source": "human-review | auto-loop | false-positive-correction",
      "model_used": "[model identifier]"
    }
  ]
}
```

The research log survives model upgrades. When a new model comes out, hand it the research log and it picks up where the previous model left off.

**Maintenance:** If exceeds 30 entries, keep the 10 most recent in full detail + a pattern summary of the rest.

## results.tsv — raw score data

Tab-separated, one row per experiment. Updated automatically. Powers the dashboard.

**Columns:**

```
experiment	score	max_score	pass_rate	skill_lines	status	description
```

**Example:**

```tsv
0	13	20	65%	85	baseline	Initial baseline run
1	16	20	80%	89	keep	필수 섹션 규칙 추가
2	16	20	80%	101	discard	섹션별 분량 가이드라인 상세 추가
3	17	20	85%	91	keep	본문 분량 범위 규칙 추가
4	17	20	85%	88	keep	불필요한 규칙 삭제 (삭제 실험)
5	19	20	95%	93	keep	부정형→긍정형 전환 + 좋은 출력 예시
```

`skill_lines`는 해당 실험 시점의 대상 스킬 파일 줄 수이다. `wc -l <target-skill-path>`로 측정.
