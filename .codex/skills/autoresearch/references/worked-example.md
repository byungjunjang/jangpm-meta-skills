# Worked Example: 문서 생성 스킬 최적화

이 예시는 git ratcheting, skill_lines 추적, simplicity 판단, 주기적 삭제 실험, Tier 1/2/3 혼합 eval이 실제 실험에서 어떻게 맞물리는지 보여준다.

## Setup

- **Target skill:** `~/.codex/skills/report-generator/SKILL.md`
- **Test inputs:** "AI 도입 현황 보고서", "분기 매출 분석", "프로젝트 회고 문서"
- **Evals:**
  1. .docx 파일이 에러 없이 생성되는가? [Tier 1 — 파일 존재 + validate.py]
  2. 목차, 요약, 본문, 결론 4개 섹션이 모두 있는가? [Tier 1 — grep]
  3. 본문이 1000자 이상 5000자 이하인가? [Tier 1 — wc]
  4. 비개발자가 읽기 쉬운 톤인가? [Tier 3 — LLM-as-judge]
- **Runs per experiment:** 5
- **Max score:** 20 (4 evals × 5 runs)
- **Tier 1-2 비율:** 75% (3/4) ✓ 목표 50% 초과

## Git branch

```bash
git checkout -b autoresearch/report-generator
```

## Experiment Flow

### Baseline (experiment 0): 13/20 (65%) | skill_lines: 85

```bash
git add .codex/skills/report-generator/SKILL.md .gitignore && git commit -m "autoresearch: baseline (13/20)"
```

실패 패턴 분석:
- 2건 결론 섹션 누락 (eval 2 fail)
- 3건 분량 초과 6000자+ (eval 3 fail)
- 2건 톤 딱딱함 (eval 4 fail)

### Experiment 1 — KEEP (16/20, 80%) | skill_lines: 89 (+4)

**Change:** "출력은 반드시 목차/요약/본문/결론 4개 섹션을 포함하라" 규칙 추가
**Result:** 섹션 누락 0건. 분량 초과 여전히 2건. Tier 1 eval 3개 모두 개선.
**Simplicity 판단:** +3점, +4줄 → **KEEP** (의미 있는 개선이 복잡성 증가를 정당화)

```bash
# commit 유지됨
```

**results.tsv:**
```
1	16	20	80%	89	keep	필수 섹션 규칙 추가
```

### Experiment 2 — DISCARD (16/20, 80%) | skill_lines: 101 (+12)

**Change:** 각 섹션별 분량 가이드라인 상세 추가 (목차 100자, 요약 300자, ...)
**Result:** 분량 초과는 해결됐지만 톤 eval이 1건 추가 fail. total 동일.
**Simplicity 판단:** ±0점, +12줄 → **DISCARD** (복잡성만 증가)
**개별 eval 퇴행:** eval 4(톤)가 3/5 → 2/5로 퇴행. 추가적 DISCARD 근거.

```bash
git reset --soft HEAD~1
git restore --source=HEAD --staged --worktree -- SKILL.md
```

**results.tsv:**
```
2	16	20	80%	101	discard	섹션별 분량 가이드라인 상세 추가
```

### Experiment 3 — KEEP (17/20, 85%) | skill_lines: 91 (+2)

**Change:** "본문은 3000자를 목표로 하되, 1000~5000자 범위를 벗어나지 마라" 한 줄 추가
**Result:** 분량 초과 0건. 간결한 규칙이 상세 가이드라인보다 효과적.
**Simplicity 판단:** +1점, +2줄 → **KEEP** (미미한 개선이지만 줄 수 증가도 미미)

```bash
# commit 유지됨
```

### Experiment 4 — KEEP (17/20, 85%) | skill_lines: 88 (-3)

**[주기적 삭제 실험 — 5번째 실험이지만 의도적으로 앞당김]**

**Change:** 기존 "전문적인 어조를 유지하라" 규칙 삭제
**Result:** 점수 동일. 이 규칙 없이도 톤 eval 결과 불변.
**Simplicity 판단:** ±0점, -3줄 → **KEEP** (같은 성능, 더 짧은 프롬프트)

```bash
# commit 유지됨 — 삭제가 최고의 실험
```

### Experiment 5 — KEEP (19/20, 95%) | skill_lines: 93 (+5)

**Change:** "~하지 마라" 3건을 "~하라" 형태로 전환 + 좋은 출력 예시 1개 추가
**Result:** 톤 eval 대폭 개선 (Tier 3). 퇴행 없음.
**Simplicity 판단:** +2점, +5줄 → **KEEP** (의미 있는 개선)

```bash
# commit 유지됨
```

## 최종 결과

```
Baseline 65% → Final 95% (5회 실험, 4 keep, 1 discard)
프롬프트 크기: 85줄 → 93줄 (+9.4%, 비대화 없이 개선)
```

## Git log

```bash
$ git log --oneline autoresearch/report-generator
a1b2c3d autoresearch: 부정형→긍정형 전환 + 좋은 출력 예시 추가
d4e5f6g autoresearch: "전문적인 어조를 유지하라" 규칙 삭제
h7i8j9k autoresearch: 본문 분량 범위 규칙 추가
l0m1n2o autoresearch: 필수 섹션 규칙 추가
p3q4r5s autoresearch: baseline (13/20)
```

성공한 mutation들만의 선형 히스토리. 실험 2 (discard)는 `git reset --soft HEAD~1` 후 `git restore --source=HEAD --staged --worktree -- SKILL.md`로 되돌려져서 히스토리에 없다.

## Key Takeaways

이 예시가 보여주는 것:
- **results.tsv의 skill_lines 컬럼**이 매 실험마다 기록됨
- **simplicity 판단 테이블**이 실제 keep/discard에 영향 (실험 2)
- **주기적 삭제 실험**의 실제 사례 (실험 4)
- **개별 eval 퇴행 감지**가 DISCARD 근거를 강화 (실험 2)
- **git commit/non-destructive rollback**이 실험 흐름에 자연스럽게 녹아듦
- **Tier 1 eval과 Tier 3 eval**이 혼합된 eval suite (75% Tier 1-2)
