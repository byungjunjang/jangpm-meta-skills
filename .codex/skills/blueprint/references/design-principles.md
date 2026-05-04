# Design Principles for Codex Agent Workflows

## 1. Default Architecture

에이전트가 Phase 2에서 아래 기준으로 자체 결정한다. 사용자에게 묻지 않는다.

- 기본값은 `single Codex agent + skills/scripts` 조합이다.
- Claude Code의 `Task` 기반 서브에이전트 설계를 그대로 옮기지 않는다.
- 역할 분리가 필요해도 먼저 skill 분리로 해결하고, 문서 안에는 조정 비용과 이유를 적는다.

**Custom subagent 분리 기준** (`.codex/agents/*.toml`):
- 전체 지시가 컨텍스트 윈도우의 30%를 초과할 때
- 명확히 독립적인 작업 블록이 있고, 각각 다른 도메인 지식이 필요할 때
- 병렬 실행이 가능하고 그로 인한 속도 이점이 명확할 때

> 판단이 애매하면 단일 에이전트를 선택한다. 멀티 에이전트의 조정 비용(데이터 전달, 오류 전파, 디버깅 복잡도)은 과소평가되기 쉽다.

## 2. Folder Structure

```text
/project-root
  AGENTS.md
  /.codex
    /skills/<skill-name>/
      SKILL.md
      /agents/openai.yaml      # optional UI metadata
      /scripts/       # optional
      /references/    # optional
      /assets/        # optional
    /agents/<agent-name>.toml   # optional custom subagent
  /output/
  /scripts/           # optional
  /docs/              # optional
```

원칙:

- 최종 문서는 프로젝트 루트의 `./blueprint-<task-name>.md`
- 중간 산출물은 `output/` 아래에 저장
- Claude 전용 경로인 `.claude/commands`, `.claude/agents`, `AGENT.md`는 Codex 설계에 넣지 않는다
- Codex skill과 custom subagent를 혼동하지 않는다. 스킬은 `.codex/skills/`, 에이전트는 `.codex/agents/*.toml`이다.
- 새 Codex 스킬은 repo 범위에서는 `.codex/skills/<skill-name>/`, 사용자 전역 범위에서는 `~/.codex/skills/<skill-name>/`에 저장한다.

## 3. LLM vs Deterministic Work

| LLM이 맡는 일 | 코드/스크립트가 맡는 일 |
|---|---|
| 분류, 우선순위 판단, 정성 평가, 요약, 누락 탐지 | 파일 I/O, 포맷 변환, 반복 처리, 외부 API 호출, 정적 검사, 스키마 검증 |

판단이 필요한 부분은 LLM에 남기고, 재현성과 실패 복구가 중요한 부분은 스크립트로 뺀다.

**경계 사례 판단 기준:**

| 작업 | 판단 | 이유 |
|------|------|------|
| 데이터 정제 (규칙 기반 필터) | 스크립트 | 조건이 명확하면 재현성이 중요 |
| 데이터 정제 (맥락 의존 판단) | LLM | "이 데이터가 유효한가?"는 판단이 필요 |
| 에러 메시지 분류 | LLM | 패턴이 다양하고 새로운 유형이 등장 |
| 포맷 변환 + 예외 처리 | 스크립트 + LLM 폴백 | 정상 케이스는 스크립트, 파싱 실패 시 LLM이 판단 |

## 4. Validation Pattern

각 단계마다 최소 하나의 검증 방식을 정의한다.

| 유형 | 사용할 때 |
|---|---|
| Schema validation | JSON, CSV, 정형 산출물 |
| Rule-based validation | 개수, 섹션 유무, 경로 규칙 |
| LLM self-check | 요약 품질, 누락 여부, 톤 |
| Human review | 고위험 의사결정, 외부 전달 문서 |

## 5. Failure Handling

| 패턴 | 기준 |
|---|---|
| Auto retry | 누락, 형식 오류처럼 자동 복구 가능한 경우 |
| Needs user input | 판단 기준이 모호하거나 정책 선택이 필요한 경우 |
| Abort with log | 잘못된 입력, 권한 부족, 복구 불가 오류 |

실패 처리는 단계 설명 안에 구체적으로 적고, 재시도 횟수나 중단 기준을 명시한다.

## 6. Skill Design Rules

- skill 이름은 소문자 하이픈 형식 사용
- SKILL frontmatter 검증은 설치된 `skill-creator` 스킬의 `quick_validate.py`를 사용
- blueprint 문서 구조 검증은 설치된 `blueprint` 스킬의 `scripts/validate_blueprint_doc.py`를 사용
- skill 폴더에는 꼭 필요한 파일만 넣고 `README.md`, `CHANGELOG.md` 같은 부가 문서는 만들지 않는다

## AGENTS.md / CLAUDE.md 작성 원칙

블루프린트로 설계된 시스템의 AGENTS.md(또는 CLAUDE.md)는 아래 4가지 원칙을 따라 작성해야 한다. 규칙을 나열하지 말고, 원칙을 깊이 이해시켜라.

### 원칙 1: 구현 전에 생각하라 (Think Before Coding)

가정을 숨기지 말고, 트레이드오프를 드러내라.

- 에이전트가 구현 전에 가정을 명시적으로 진술하도록 지시
- 해석이 여러 개일 때 조용히 하나를 고르지 말고 선택지를 제시하도록 유도
- 더 단순한 접근이 있으면 말하도록 허용 — 필요 시 pushback 권한 부여
- 불명확한 부분은 멈추고 물어보도록 명시

### 원칙 2: 단순함 우선 (Simplicity First)

문제를 해결하는 최소한의 코드. 추측성 구현 금지.

- 요청한 것 이상의 기능 금지
- 일회성 코드에 추상화 금지
- 요청하지 않은 "유연성"이나 "설정 가능성" 금지
- 불가능한 시나리오에 대한 에러 핸들링 금지

**자기 검증 테스트**: "시니어 엔지니어가 보고 '이거 너무 복잡하다'고 할까?" → 그렇다면 단순화.

### 원칙 3: 수술적 변경 (Surgical Changes)

건드려야 할 것만 건드려라. 자기가 만든 잔해만 정리하라.

- 인접 코드, 주석, 포매팅을 "개선"하지 말 것
- 깨지지 않은 것을 리팩터링하지 말 것
- 기존 스타일과 다르더라도 기존 스타일에 맞출 것
- 관련 없는 데드 코드는 언급만 하고 삭제하지 말 것

**자기 검증 테스트**: "변경된 모든 줄이 사용자의 요청에 직접 연결되는가?" → 아니면 되돌려라.

### 원칙 4: 목표 중심 실행 (Goal-Driven Execution)

성공 기준을 정의하고, 검증될 때까지 반복하라.

작업을 검증 가능한 목표로 변환:
- "유효성 검사 추가" → "잘못된 입력에 대한 테스트를 쓰고, 통과시켜라"
- "버그 수정" → "재현하는 테스트를 쓰고, 통과시켜라"

### 적용 방법

AGENTS.md(또는 CLAUDE.md)에 이 4가지 원칙을 직접 넣되, **50줄 이내의 간결한 형태**로 압축한다. 규칙 50개보다 원칙 4개가 LLM의 실제 준수율이 높다.

각 원칙에는 반드시 **자기 검증 질문**을 포함한다 — 추상적 지시 대신 에이전트가 스스로 판단할 수 있는 구체적 기준을 제공한다.

**트레이드오프 명시**: 원칙의 적용 범위와 한계를 명시한다. 예: "이 가이드라인은 신중함 쪽에 편향되어 있다. 단순 작업에는 판단력을 사용하라." 절대적 규칙은 역효과를 낸다.

**성공 지표**: 지시 파일 끝에 "이 가이드라인이 잘 작동하고 있다면:" 항목을 추가한다. 예:
- diff에 불필요한 변경이 줄어든다
- 과도한 복잡성으로 인한 재작성이 줄어든다
- 구현 전에 명확화 질문이 먼저 나온다

---

### Skill Creation Standards

블루프린트 설계서에 스킬이 포함될 경우, 구현 단계에서 반드시 **`skill-creator` 스킬**을 사용하여 스킬을 생성·검증해야 한다. 직접 SKILL.md를 손으로 작성하면 규격 불일치가 발생하므로 이를 방지하기 위한 필수 규칙이다.

#### 왜 skill-creator를 거쳐야 하는가

- **SKILL.md frontmatter 규격**: `name`, `description` 필수 필드 + 트리거 정확도를 위한 description 최적화가 필요
- **폴더 구조 규격**: `SKILL.md` + `scripts/`, `references/`, `assets/` 구조를 준수해야 함
- **Codex 저장 위치 규격**: repo 스킬은 `.codex/skills/<skill-name>/`, 사용자 전역 스킬은 `~/.codex/skills/<skill-name>/`
- **커스텀 에이전트 규격**: `.codex/agents/<agent-name>.toml`에 `name`, `description`, `developer_instructions` 필수
- **Progressive disclosure**: SKILL.md 본문 500줄 이내, 대용량 참조는 `references/`로 분리
- **Description 최적화**: skill-creator의 description optimization 루프를 거쳐야 트리거 정확도가 보장됨
- **테스트 검증**: 테스트 프롬프트 실행 → 평가 → 개선 루프를 통해 스킬 품질 확보

#### 설계서에 포함할 내용

블루프린트 문서의 **구현 스펙 > Skill and Script Inventory** 또는 별도 섹션에 아래 내용을 명시:

```markdown
## 스킬 생성 규칙

이 설계서에 정의된 모든 스킬은 구현 시 반드시 `skill-creator` 스킬(`/skill-creator`)을 사용하여 생성할 것.
직접 SKILL.md를 수동 작성하지 말 것 — 규격 불일치 및 트리거 실패의 원인이 됨.

skill-creator가 보장하는 규격:
1. SKILL.md frontmatter (name, description) 필수 필드 준수
2. description의 트리거 정확도 최적화 (eval 기반 optimization loop)
3. 스킬 저장 위치 `.codex/skills/<skill-name>/` 규격 준수
4. 폴더 구조 (SKILL.md + scripts/ + references/) 규격 준수
5. 테스트 프롬프트 실행 및 품질 검증 완료
```

## Blueprint 복잡도 한계

이 스킬로 설계하는 시스템의 권장 한계:

| 항목 | 권장 한계 | 초과 시 |
|------|----------|---------|
| 워크플로우 단계 수 | 10개 이내 | 하위 워크플로우로 분할 검토 |
| Custom subagent 수 | 4개 이내 | 조정 복잡도 급증 — 계층 분리 검토 |
| 스킬 수 | 8개 이내 | 스킬 간 중복/의존성 점검 |

한계를 초과하면 설계서에 경고를 명시하고, 분할 방안을 함께 제시한다.

## 7. Artifact Strategy

- 큰 중간 결과는 파일로 저장하고 경로만 다음 단계에 넘긴다
- 파일 이름 규칙은 `output/stepNN_<name>.<ext>`
- 최종 산출물은 루트에 두고, 중간 산출물과 분리한다

## 8. Documentation Scope

- 설계 문서에는 구조, 역할, 인터페이스, 검증 규칙만 쓴다
- 코드 본문, 장문 프롬프트, 세부 구현은 제외한다
- 구현 중 추정이 들어간 내용은 `Assumptions`나 해당 섹션 본문에서 명확히 표시한다
