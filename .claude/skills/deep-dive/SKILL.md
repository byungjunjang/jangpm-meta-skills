---
name: deep-dive
description: Socratic interview skill to deepen a spec or refine an existing agent blueprint. Use when the user wants to clarify a task, stress-test design decisions, or fill gaps in a blueprint produced by /blueprint. Trigger on "/deep-dive", "deep dive", "interview me", "create a spec", "요구사항 정리", "기획서 만들어", "스펙 작성", "blueprint 심화", "설계 보강".
---

# deep-dive

## 사용하지 말아야 할 때

요구사항이 이미 명확해서 문서만 작성하면 되는 경우에는 이 스킬을 쓰지 않는다 — 인터뷰(forcing question) 루프가 불필요하므로 바로 문서를 작성한다.

An in-depth interview skill that asks **forcing questions** (not obvious ones), challenges premises, generates alternatives, and validates the final spec with a fresh-context reviewer. Produces or updates a spec/blueprint document.

Primary use case: **blueprint 심화** — `/blueprint`로 만든 에이전트 설계 초안을 받아 빈틈·암묵 전제·결정 근거를 인터뷰로 파고들어 문서를 단단하게 만든다. Fallback use case: blueprint 없이 새 주제를 처음부터 스펙화.

**CRITICAL DEFAULT BEHAVIOR**: When an existing spec/blueprint document is found, you MUST update that document unless the user explicitly requests a new file. Creating a new file when a relevant document already exists is INCORRECT behavior — unless the user overrides this in Phase 1. New file creation is the default ONLY when no related document exists at all.

---

## References (로드 규칙)

아래 4개 파일을 **해당 Phase 진입 시에만** Read로 로드한다. 처음부터 전부 읽지 말 것 (컨텍스트 낭비).

- [references/question-library.md](references/question-library.md) — 일반 스펙용 forcing 질문 라이브러리 (Phase 3 진입 시)
- [references/agent-design-questions.md](references/agent-design-questions.md) — 에이전트 blueprint 심화 전용 질문 축 (Phase 3 진입 시, 심화 모드일 때만)
- [references/anti-patterns.md](references/anti-patterns.md) — 어조 가이드 & 피할 표현 (Phase 3 진입 시 1회)
- [references/reviewer-checklist.md](references/reviewer-checklist.md) — Spec Reviewer Loop 5차원 기준 (Phase 7 진입 시)

---

## Execution Flow (7 Phases)

1. **Phase 1** — Context & Doc Scan: 기존 설계 문서 스캔
2. **Phase 2** — Topic Framing + Blueprint 로딩: 심화 모드 / 스크래치 모드 분기
3. **Phase 3** — Forcing Interview: 한 질문씩 밀어붙이기
4. **Phase 4** — Premise Naming: 전제 명시 & 확인
5. **Phase 5** — Alternative Framings (MANDATORY): 대안 제시 & 승인
6. **Phase 6** — Write / Update Spec
7. **Phase 7** — Spec Review Loop: 서브에이전트 5차원 리뷰 (최대 3회)

---

## Phase 1: Context & Doc Scan

1. `$ARGUMENTS`를 읽어 주제를 파악한다. 비어 있으면 Phase 2에서 첫 질문으로 묻는다.
2. `Glob`으로 현재 작업 디렉토리에서 기존 설계 문서를 스캔한다:
   - **Blueprint 우선 패턴**: `blueprint-*.md`, `*-blueprint.md`, `agent-design*.md`, `design-*.md`
   - **Spec 패턴**: `spec-*.md`, `*-spec.md`
   - **한국어 패턴**: `*기획*.md`, `*설계*.md`, `*planning*.md`
   - **기타**: `*PRD*.md`, `*requirements*.md`, `architecture.md`, `roadmap.md`, `overview.md`, `notes.md`
   - **항상 확인**: `README.md` (이름과 무관하게 스펙 내용을 담을 수 있음)
   - ⚠️ **CLAUDE.md는 context-only**: 읽어서 프로젝트 규칙·제약은 이해하되, **업데이트 후보로 제시하지 말 것** — 에이전트 지시 파일이지 스펙 문서가 아니다.
3. 감지된 파일을 Read로 읽어 내용을 파악한다. blueprint 패턴이 매칭된 파일은 **전체**를 읽는다 — 이후 Phase 3에서 이미 답한 내용을 다시 묻지 않기 위함.
4. **User confirmation (문서가 발견되었을 때)**:
   - CLAUDE.md는 후보 리스트에서 제외.
   - 1개 발견: "기존 문서 `[filename]`을 업데이트하겠습니다. 괜찮으면 계속, 새 파일로 만들 거면 'new'라고 답해주세요."
   - 여러 개 발견: `AskUserQuestion`으로 어느 것을 업데이트할지 또는 'new'를 선택하게 함.
   - **사용자가 'new'를 명시하지 않으면 기본값은 업데이트**.
5. **아무 문서도 없으면** Phase 2로. 이 경우 최종 단계는 암묵적으로 "create new".

⚠️ Phase 1에서 내린 "업데이트 대상" 결정은 **FINAL**. Phase 6에서 재평가하지 않는다.

---

## Phase 2: Topic Framing + Blueprint 로딩

이 Phase의 목적: 이후 Forcing Interview에서 어떤 질문 세트·어떤 톤으로 갈지 결정한다. 두 가지 모드가 있다.

### 심화 모드 (Blueprint Deepening)
**진입 조건**: Phase 1에서 blueprint 패턴이 매칭된 문서 1개 이상 감지됨 + 사용자가 그걸 업데이트하기로 확정.

**행동**:
1. blueprint 문서 내용을 요약해서 사용자에게 되돌려 읽어준다 — "현재 이 blueprint가 이렇게 설계돼 있네요: [3–5줄 요약]. 오늘은 이 설계의 어느 부분을 제일 깊이 파고들고 싶으세요? (전체를 훑는 것도 가능)"
2. 사용자 답을 기준으로 **심화 초점**을 정한다. 초점이 좁으면 그 축으로만 질문, 넓으면 `agent-design-questions.md`의 A–G 축을 순회.
3. Phase 3에서 `agent-design-questions.md`와 `question-library.md`를 **둘 다** 로드한다.

### 스크래치 모드 (From Scratch)
**진입 조건**: Phase 1에서 관련 문서 없음, 또는 사용자가 'new'를 선택.

**행동**:
1. 사용자에게 짧게 묻는다 — "기존 blueprint 없이 새로 스펙을 짜는 거네요. 이 주제를 한 문장으로 정의해주세요: `[이것]이 [누구]를 위해 [무엇]을 한다`."
2. 답을 받아 주제 문장을 잠정 고정. 이후 인터뷰에서 이 문장이 흔들리면 되돌아와 수정.
3. Phase 3에서 `question-library.md`만 로드 (`agent-design-questions.md`는 필요 시 보조).

---

## Phase 3: Forcing Interview

Phase 2에서 결정한 모드대로 references를 Read하고, 다음 규칙으로 인터뷰한다.

### 대화 규칙

- **한 번의 `AskUserQuestion` = 질문 한 개**. 여러 질문 묶지 말 것. office-hours 방식.
- **references의 질문을 그대로 복붙하지 말고** 현재 주제의 용어로 바꿔 쓸 것.
- **사용자 답이 Red flag(참고: references)면 같은 축으로 한 번 더 찌른다 (Follow-up).** 구체적·증거 기반 답이 나올 때까지.
- **Escape hatch**: 같은 축에서 사용자가 **2회 연속** Follow-up을 거부하거나 회피하면 → 그 축은 접고 "Open Questions"로 메모해둔 뒤 다음 축으로. 강요하지 말 것.
- **어조**: `references/anti-patterns.md`의 중간 밸런스. 칭찬·회피·일반론 금지. 사용자 답을 그대로 인용해 모순·모호함을 짚기.
- **이미 답된 질문 스킵**: 심화 모드라면 blueprint에 명시돼 있는 내용은 다시 묻지 말 것. blueprint의 **빈틈·암묵 전제·근거 미명시**만 파고든다.
- **라운드 상한 없음**. "사용자가 모든 축에서 구체적 답을 냈거나 Escape hatch로 모두 접힐 때까지". 평균 6–12개 질문, 경우에 따라 그 이상.

### 카테고리 커버리지

- **항상 다뤄야 할 축** (`question-library.md` 기준): Core Behavior (1), Tradeoffs (4), Failure Modes (5).
- **주제에 맞으면 다뤄야 할 축**: Technical Implementation (2), UI/UX (3 — 비대화형 도구는 스킵), Scale & Future (6), Concerns (7).
- **심화 모드**: `agent-design-questions.md`의 축 A–G를 기준으로 blueprint 내용과 대조. 이미 충분히 결정된 축은 건너뛴다.

각 질문 후 사용자 답을 내부 메모에 정리해둔다 (Phase 6에서 스펙 쓸 때 사용).

### Phase 3 종료 조건

다음 중 하나를 만족하면 Phase 4로 진행:
- 필수 축(Core/Tradeoffs/Failure) 전부에서 구체적 답을 받음 + 주제에 해당되는 선택 축도 다룸.
- 사용자가 "이 정도면 됐다" / "충분해요" / "다음으로 넘어가자"라고 명시.

---

## Phase 4: Premise Naming

Phase 3이 어느 정도 진행된 뒤(일반적으로 4–6개 질문 이후), 인터뷰를 **잠깐 멈추고** 다음을 수행한다.

1. 지금까지의 답변 + (심화 모드면) blueprint 내용에서 **암묵적으로 깔려 있는 전제 3–5개**를 추출한다. 전제 예시:
   - "사용자가 한국어로만 입력한다"
   - "이 에이전트는 한 번에 한 사용자만 쓴다"
   - "외부 API가 항상 응답한다"
   - "blueprint가 LLM 호출로 잡은 X 단계는 코드로는 불가능하다"
2. `AskUserQuestion`으로 3–5개를 나열하며 사용자에게 확인받는다:
   - "제가 지금까지 이런 전제를 깔고 이해했는데, 맞는지 확인 부탁드립니다: ① ... ② ... ③ .... 이 중 틀리거나 재고해야 할 게 있나요?"
3. 사용자가 특정 전제를 부인하거나 흔들면 → **Phase 3로 되돌아가** 해당 축으로 질문을 추가한다. 전제가 모두 확인되면 Phase 5로.

이 Phase는 **반드시 한 번** 수행한다. 스펙 품질의 절반은 전제를 명시적으로 꺼냈느냐에 달려 있다.

---

## Phase 5: Alternative Framings (MANDATORY)

**스펙을 쓰기 전에 반드시 이 Phase를 거친다.** 여기서 `AskUserQuestion`으로 사용자 승인을 받지 못하면 Phase 6으로 진행 금지.

### 심화 모드

1. blueprint의 **핵심 설계 결정 1–2개**를 고른다 (예: "병렬 서브에이전트 구조", "단계 X를 LLM으로 처리", "체크포인트를 3군데 둠").
2. 각각에 대해 "반대로 했다면?" 대안을 1–2개 제시한다. 포맷:
   ```
   현재 결정: [blueprint의 결정을 한 줄 인용]
   대안 A:   [반대/다른 방식] — 효과: [Pros 1–2개] / 비용: [Cons 1–2개]
   대안 B:   [또 다른 각도] — 효과: ... / 비용: ...
   권장:     [A / B / 현재 유지] — 근거: [Phase 3·4에서 들은 사용자 답을 인용]
   ```
3. `AskUserQuestion`으로 "현재 결정 유지 / 대안 A 채택 / 대안 B 채택 / 더 논의 필요"를 선택받는다. 사용자 선택이 Phase 6 스펙에 반영된다.

### 스크래치 모드

1. 주제에 대해 **2–3개 접근안**을 제시한다. 각각 다음 속성:
   - 이름
   - 한 줄 요약
   - Effort: S/M/L
   - Risk: Low/Med/High
   - Pros: 2–3개
   - Cons: 2–3개
   - Reuses: 재사용 가능한 기존 자산
2. 최소 2개, 가능하면 3개. 셋 중 하나는 **최소 실행 가능안** (가장 빨리 배포 가능), 하나는 **이상적 아키텍처** (장기적으로 최선), 하나는 **색다른 각도** (의외의 프레이밍).
3. `AskUserQuestion`으로 사용자가 하나를 승인해야 Phase 6으로.

### Phase 5를 건너뛸 수 없는 이유

대안을 생성해 보지 않은 설계는 "처음 떠오른 생각"에 고착된다. 이 Phase가 forcing function 역할. 사용자가 "대안 필요 없어요"라고 하더라도 한 번은 제시하고 "현재 유지" 선택지를 주는 것으로 형식은 지킨다.

---

## Phase 6: Write / Update Spec

Phase 1에서 내린 결정에 따라:

- **업데이트 대상이 정해진 경우** → Phase 6a (Update)
- **새 파일을 만드는 경우** → Phase 6b (Create)

⚠️ **HARD RULE**: Phase 1에서 기존 문서를 업데이트하기로 했고 사용자가 중간에 'new'를 요청하지 않았다면, 반드시 6a로. 6b로 도망가지 말 것.

### Phase 6a: 기존 문서 업데이트

1. Phase 1에서 이미 읽은 파일 내용을 기준으로.
2. **Pre-merge 분석 (필수)**:
   - 기존 문서의 모든 섹션 heading 나열
   - Phase 3–5에서 얻은 각 결정을 기존 섹션에 매핑
   - 각 항목을 분류: **APPEND** / **REVISE** / **NEW_SECTION**
3. **Merge 규칙**:
   - **APPEND**: 해당 섹션 끝에 추가
   - **REVISE**: 낡은 내용을 **직접 교체**. 과거 내용을 병기하지 말 것 (`<!-- 이전 -->` 같은 마커 금지). Git blame이 히스토리 역할.
   - **NEW_SECTION**: 문서의 마지막 섹션 직전에 삽입. "Open Questions"가 있으면 그 앞에, 없으면 맨 끝에 추가.
   - **손대지 않을 내용**: 인터뷰에서 다루지 않은 기존 내용은 그대로 유지. 리포맷·재정리 금지.
   - **도구**: `Edit` 사용. **`Write`로 전체 덮어쓰지 말 것.**
4. 파일 말미에 **"What I noticed"** 섹션 추가/갱신: 이 세션에서 관찰한 사용자의 사고 패턴 2–3줄 (예: "트레이드오프에서 속도보다 정확도를 일관되게 우선시함", "기존 도구와의 경계는 잘 잡지만 실패 모드는 상대적으로 덜 고려"). 다음 세션에 참고.
5. 사용자에게 파일 경로와 변경 요약 보고.

### Phase 6b: 새 파일 생성

> ⚠️ 이 단계로 들어올 조건: (a) Phase 1에서 기존 문서 없음, 또는 (b) 사용자가 Phase 1에서 'new' 요청.
> 두 조건 모두 아니면 Phase 6a로.

- 파일명: `spec-[topic-slug].md` (현재 작업 디렉토리)
- 포맷:

```markdown
# Spec: [Topic]

## Overview
[1–2문장 요약]

## Goals
- ...

## Scope
- In:
- Out:

## Inputs and Outputs
- ...

## Requirements
### Functional
- ...
### Non-functional
- ...

## Technical Notes
- ...

## UI/UX Notes
(비해당 시 생략)

## Tradeoffs & Decisions
- ...

## Failure Modes
- ...

## Premises (Phase 4에서 확인된 전제)
- ...

## Alternatives Considered (Phase 5 결과)
- 채택: ...
- 거부된 대안: ... (거부 이유)

## Open Questions
- ...

## What I noticed
[사용자 사고 패턴 2–3줄]
```

`Write`로 저장 후 파일 경로 보고.

---

## Phase 7: Spec Review Loop

스펙이 저장된 후, **맥락을 공유하지 않은** Explore 서브에이전트를 띄워 `references/reviewer-checklist.md`의 5차원으로 리뷰한다. 최대 3회.

### Round 1

1. `references/reviewer-checklist.md`를 Read.
2. `Agent` 도구로 subagent_type=`Explore` 호출. 프롬프트에 포함할 것:
   - 스펙 파일 절대경로
   - (심화 모드) 원본 blueprint 파일 절대경로
   - 체크리스트 5차원 요약 (Completeness / Consistency / Clarity / Scope / Feasibility)
   - 요구 출력 포맷 (reviewer-checklist.md 참고)
   - **중요**: 서브에이전트에게 "대화 맥락 없이 오직 문서만 보고 판단하라"고 명시.
3. 서브에이전트 결과를 받는다.

### Round 1 결과 처리

- Overall이 `Converged` → Phase 7 종료, 사용자에게 최종 보고.
- `Needs revision` → Priority fixes를 반영해 스펙 수정 (Edit 사용). Round 2로.

### Round 2

Round 1과 동일하지만 **새 서브에이전트**로 재호출 (맥락 오염 방지). 수정된 스펙 파일 경로만 넘긴다. 결과 처리도 동일.

### Round 3

마지막 반복. Round 2와 동일 방식.

### 종료 시 남은 이슈 처리

Round 3 후에도 Converged가 아니면, 남은 Fail/Partial 항목을 스펙 말미에 다음 형식으로 추가:

```markdown
## Reviewer Concerns

Round 3까지 수렴하지 않은 항목:

- [Completeness] [항목]
- [Clarity] [항목]
- ...
```

이 섹션은 다음 세션에 참고하도록 보존. 삭제하지 말 것.

### Phase 7 중단 조건

- 사용자가 "그만 하자" / "이 정도면 됐다" → 현재 Round에서 중단, 남은 이슈를 Reviewer Concerns로.
- Converged 결과가 나오면 Round 수와 무관하게 종료.

### 최종 보고

Phase 7 끝나면 사용자에게:
- 스펙 파일 경로
- 최종 수렴 상태 (Converged / Reviewer Concerns 존재)
- 주요 변경점 3–5줄 요약
