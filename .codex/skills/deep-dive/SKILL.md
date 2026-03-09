---
name: deep-dive
description: 상세 요구사항 인터뷰와 스펙 문서 작성을 위한 Codex 스킬. 여러 라운드의 질문으로 핵심 동작, 기술 제약, UX, 트레이드오프, 실패 조건을 구체화하고 새 스펙을 작성하거나 기존 문서를 업데이트한다. Use when the user asks for "/deep-dive", "deep dive", "interview me", "create a spec", or wants a structured requirements deep dive in Codex.
metadata:
  short-description: Run a deep requirements interview and spec write-up
---

# Deep Dive

## Overview

모호한 요청을 여러 라운드의 인터뷰로 구체화해서 스펙 문서로 정리한다.

- 기본 출력 파일은 `spec-<topic-slug>.md`
- **CRITICAL / 필수 원칙**: 관련 문서가 이미 있으면 반드시 그 문서를 업데이트한다. 기존 문서가 있는데 새 파일을 만드는 것은 잘못된 동작이다.
- 새 파일 생성은 관련 문서가 전혀 없거나, 사용자가 인터뷰 전에 명시적으로 `new`를 요청했을 때만 허용된다.
- 질문은 적게, 깊게, 누적적으로 묻는다

## Workflow

### 1. Read `$ARGUMENTS`

사용자 요청에서 주제, 의도, 기대 산출물을 먼저 파악한다.

- 핵심 키워드와 후보 토픽 슬러그를 메모한다
- 요청이 기존 문서 보강인지 새 기획인지 바로 단정하지 말고 다음 단계에서 문서를 찾는다

### 2. Scan the Workspace First

현재 작업 디렉터리에서 기존 스펙 또는 기획 문서를 먼저 찾는다.

- 파일 탐색은 `rg --files`를 우선 사용
- 우선 후보 패턴:
  - `spec-*.md`
  - `*-spec.md`
  - `*planning*.md`
  - `*requirements*.md`
  - `*PRD*.md`
  - `*기획*.md`
  - `*설계*.md`
- 관련 문서가 있으면 먼저 읽고, 각 문서의 목적과 현재 섹션 구조를 요약한다
- 관련 문서가 있으면 인터뷰 전에 그 문서를 사용자에게 보여줄 준비를 한다

### 3. Confirm Update vs New Before Interview

관련 문서가 하나라도 있으면 인터뷰 전에 반드시 사용자 확인을 먼저 받는다. 긴 인터뷰 동안 기존 문서의 존재를 잊지 않기 위한 단계다.

- `request_user_input`에 의존하지 말고 일반 assistant 메시지로 묻는다
- 문서가 1개면 그 문서를 보여주고 업데이트 여부를 묻는다
- 문서가 여러 개면 후보를 번호와 함께 보여주고, 어떤 문서를 업데이트할지 또는 `new`를 입력할지 묻는다
- 예시:

```text
다음 기존 문서를 찾았습니다:
1. `filename.md` — [한 줄 요약]

이 문서를 업데이트할까요? 새 파일을 만들려면 `new`라고 답해주세요.
```

- 사용자가 명시적으로 `new`라고 하지 않으면 기존 문서 업데이트를 기본으로 한다
- 이 단계에서 정한 결정은 FINAL이다. 이후 단계에서 다시 판단하거나 뒤집지 않는다

### 4. Interview in Rounds

질문 규칙:

- 한 라운드에 1~2개만 질문한다
- 직전 답변을 바탕으로 더 깊게 묻는다
- 뻔한 질문 대신 구체적인 운영 조건이나 예외를 캐낸다
- 보통 3~5라운드 안에서 끝낸다

반드시 순환해서 다룰 범주:

1. Core behavior: 정상 흐름, 예외 흐름, 종료 조건
2. Inputs and outputs: 형식, 출처, 저장 위치, 검증 기준
3. Technical constraints: 스택, 외부 시스템, 권한, 성능 한계
4. UX or operator flow: 누가 언제 어떻게 쓰는지
5. Tradeoffs: 속도 vs 정확도, 단순성 vs 확장성
6. Failure modes: 입력 오류, 외부 장애, 재시도 기준
7. Future change: 규모 증가, 후속 단계, 확장 포인트
8. Concerns: 사용자가 가장 불안해하는 부분

Default mode 기준:

- `request_user_input`에 의존하지 말고, 일반 assistant 메시지로 질문한다
- 답변이 부족해도 작업을 멈추지 말고 가정을 분명히 적은 뒤 진행한다

### 5. Follow the Step 3 Decision

Step 3에서 정한 결정을 그대로 따른다. 여기서 다시 자동 판단하지 않는다.

- DO NOT re-evaluate. Follow the decision from Step 3.
- HARD RULE: 기존 문서가 있고 사용자가 명시적으로 `new`라고 하지 않았다면 반드시 기존 문서를 업데이트한다.
- 새 파일 생성은 아래 둘 중 하나일 때만 가능하다:
  - 관련 문서가 전혀 없었다
  - 사용자가 Step 3에서 명시적으로 `new`를 요청했다

### 5a. Update Existing Document Carefully

기존 문서를 수정할 때 규칙:

- 수정 전에 반드시 아래 분석을 먼저 한다:
  1. 기존 문서의 모든 섹션 제목을 나열한다
  2. 인터뷰 결과 각 항목을 어떤 섹션에 들어갈지 매핑한다
  3. 각 항목을 `APPEND` / `REVISE` / `NEW_SECTION`으로 분류한다
- 병합 규칙:
  - `APPEND`: 해당 섹션 끝에 추가한다
  - `REVISE`: 기존 내용을 유지한 채 필요한 부분만 수정하고, 변경 지점에 아래 마커를 남긴다
  - `NEW_SECTION`: 문서 끝에 추가하되, `Open Questions`가 있으면 그 앞에 넣는다
- 인터뷰에서 다루지 않은 기존 내용은 절대 수정, 삭제, 재정렬, 재포맷하지 않는다
- 관련 없는 내용은 건드리지 않는다
- 인터뷰 결과가 기존 내용과 충돌하면 조용히 덮어쓰지 말고 아래 형식으로 표시한다

```markdown
> ⚠️ Updated: [what changed and why]
```

- 실제 파일 수정은 섹션 단위 `apply_patch`로 한다
- 기존 문서가 있는데도 새 파일을 만드는 쪽으로 우회하지 않는다

### 5b. Create a New Spec Only When Allowed

아래 조건일 때만 이 단계로 온다.

```markdown
> ⚠️ Only reach this step if: (a) no existing document was found, OR (b) user explicitly requested a new file.
> If neither condition is true, STOP and go back to Step 5a.
```

새 문서를 만들 때 기본 구조:

```markdown
# Spec: [Topic]

## Overview
[1-2 sentence summary]

## Goals
- ...

## Requirements
### Functional
- ...
### Non-functional
- ...

## Technical Notes
- ...

## UX / Operator Flow
- ...

## Tradeoffs and Decisions
- ...

## Failure Modes
- ...

## Open Questions
- ...
```

### 6. Hand-off

마지막에 아래만 간단히 알려준다.

- 수정하거나 생성한 파일 경로
- 이번 인터뷰로 명확해진 핵심 결정
- 남아 있는 불확실성
