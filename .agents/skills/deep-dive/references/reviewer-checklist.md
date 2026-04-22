# Reviewer Checklist

SKILL.md의 Phase 7(Spec Review Loop)에서 사용하는 5차원 리뷰 기준. deep-dive 세션의 메인 에이전트가 스펙 초안을 저장한 뒤, **문서 내용만 근거로 삼는 document-grounded reviewer pass**로 문서를 재검토한다.

최대 3회 반복. 수렴하지 않으면 미해결 항목을 스펙 말미의 "Reviewer Concerns" 섹션에 남기고 종료.

---

## 리뷰어 실행 방식 (Codex 환경)

Codex에서는 별도 세션이 항상 보장되지 않으므로, reviewer pass의 기본 계약을 다음처럼 둔다:

1. **가능하면 권장**: Codex의 별도 세션/프로세스를 새로 시작해 리뷰 프롬프트를 실행. 인터뷰 대화 히스토리는 공유하지 않는다.
2. **기본 fallback**: 같은 세션에서 진행하되, 리뷰 시작 전에 체크리스트와 대상 문서를 다시 읽고, **판단 근거를 문서에 적힌 내용으로만 제한**한다.
3. 이전 인터뷰 기억, 작성 의도, 직전 Round의 수정 이유를 근거로 Pass 판정을 내리지 않는다. 문서에 안 써 있으면 "없는 것"으로 본다.

핵심은 "fresh session" 자체보다 **document-grounded 판정 discipline**이다.

## 리뷰어에게 제공할 입력

1. 스펙 파일의 절대경로 (리뷰어가 읽을 것)
2. (심화 모드일 때) 원본 blueprint 문서의 절대경로
3. 이 체크리스트의 5차원 기준 요약
4. 요구 출력 포맷 (아래 참조)

## 리뷰어 출력 포맷

```
## Completeness
Pass / Fail / Partial — [한 줄 이유]
Missing items: [있다면 bullet로]

## Consistency
Pass / Fail / Partial — [한 줄 이유]
Contradictions: [있다면 bullet로]

## Clarity
Pass / Fail / Partial — [한 줄 이유]
Vague spots: [있다면 bullet로 — 구체적 문장 인용]

## Scope
Pass / Fail / Partial — [한 줄 이유]
Scope issues: [있다면 bullet로]

## Feasibility
Pass / Fail / Partial — [한 줄 이유]
Infeasible items: [있다면 bullet로]

## Overall
Converged / Needs revision — [전체 판정 한 줄]
Priority fixes (이번 반복에서 고쳐야 할 것): [최대 3개]
```

---

## 5차원 기준

### 1. Completeness (완결성)
스펙이 **이 주제에 대해 의사결정에 필요한 내용을 다 담았는가**.

Pass 조건:
- Core Behavior / Tradeoffs / Failure Modes 세 섹션이 전부 채워짐 (빈 bullet·placeholder 금지)
- 심화 모드라면 blueprint에서 건드려야 할 축들(`agent-design-questions.md`의 A–G)에 대해 최소 한 개 이상의 결정·변경·유지 사유가 적혀 있음
- "TBD", "나중에 결정", "추후 논의"가 핵심 섹션에 3개 이상 있으면 Fail

### 2. Consistency (일관성)
스펙 안에서 **모순되지 않는가**.

Pass 조건:
- 앞 섹션의 전제와 뒤 섹션의 결론이 어긋나지 않음 (예: Tradeoffs에 "속도 우선"이라고 쓰고 Technical Notes에 "정확도 99% 보장"이라고 쓰면 모순)
- Scope In/Out의 경계와 Requirements의 범위가 맞음
- 용어가 섹션마다 달리 쓰이지 않음 (같은 개념은 같은 이름)

### 3. Clarity (명료성)
구체적 명사·동사·수치를 쓰는가, 범주·추상어로 도망가지 않는가.

Pass 조건:
- "자동으로", "잘", "깔끔하게", "효율적으로", "유연하게" 같은 모호어가 핵심 결정에 쓰이지 않음
- 사용자·역할을 지칭할 때 "일반 사용자" 같은 범주가 아니라 구체적 역할 (예: "주 1회 이 에이전트를 돌리는 admin")
- 수치가 필요한 곳(성능, 실패율, 실행 시간, 크기)에 수치가 있음

### 4. Scope (범위)
**들어가는 것과 빠지는 것**이 뚜렷한가.

Pass 조건:
- "Scope — In" / "Scope — Out" 양쪽에 항목이 있음 (Out이 비어 있으면 결정이 없었다는 뜻)
- In 범위가 실행 가능한 크기인가 (한 명이 한 주기에 끝낼 수준인지, 아니면 분할이 필요한지 명시)
- 대안 접근(Alternative Framings 단계에서 거부한 안) 중 주요 것이 Out에 명시됨

### 5. Feasibility (실행 가능성)
기존 도구·코드·시간으로 **정말 만들 수 있는가**.

Pass 조건:
- Technical Notes의 기술 선택이 현재 가용한 도구로 구현 가능
- 외부 의존(API, MCP 서버, 사용자 권한)이 명시되고, 각 의존의 현 상태(있다/없다/확보 필요)가 적힘
- 심화 모드라면 blueprint에서 요구한 기존 자산(스크립트, 에이전트, 참조 문서)이 실제 존재하는지 검증 가능

---

## 반복 루프 운영 원칙

1. **Round 1**: 리뷰어가 5차원 판정 → 메인 에이전트가 Priority fixes를 `apply_patch`로 스펙에 반영.
2. **Round 2**: 재검토. 수정된 스펙을 같은 포맷으로 다시 리뷰하되, 앞선 리뷰 기록을 판정 근거로 사용하지 않는다.
3. **Round 3**: 마지막 반복. Overall이 `Converged`가 아니어도 여기서 멈춘다.
4. **미해결 이슈 처리**: Round 3에서도 남은 Fail/Partial 항목은 스펙 말미에 다음 형식으로 남긴다:

```markdown
## Reviewer Concerns

Round 3까지 수렴하지 않은 항목 (리뷰 기록):

- [Completeness] Failure Modes 섹션에 조용한 실패 시나리오가 명시되지 않음
- [Clarity] "효율적으로 처리" 표현이 3군데에 남음 — 구체 수치로 대체 필요
- [Feasibility] 외부 도구 X 의존은 명시됐으나 접근 가능 여부 확인 안 됨
```

**이 Reviewer Concerns는 삭제하지 말 것**. 다음 세션에서 deep-dive나 사람이 후속 해결해야 할 목록이다.

---

## 반복 종료 조건

- Round n에서 Overall이 `Converged`로 나오면 즉시 종료 (반복 비용 아끼기).
- Round 3 완료 시 강제 종료.
- 사용자가 "이 정도면 됐다"고 말하면 현재 Round에서 강제 종료하고 남은 이슈를 Reviewer Concerns로 저장.
