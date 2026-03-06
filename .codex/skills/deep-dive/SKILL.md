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
- 이미 관련 문서가 있으면 새 파일보다 기존 문서를 우선 업데이트
- 질문은 적게, 깊게, 누적적으로 묻는다

## Workflow

### 1. Scan the Workspace First

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
- 관련 문서가 있으면 먼저 읽고, 어떤 섹션을 보완해야 할지 파악한다

### 2. Interview in Rounds

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

### 3. Decide Update vs Create

사용자에게 따로 묻지 말고 자동 판단한다.

- 관련 문서가 있으면 그 문서를 업데이트
- 없으면 `spec-<topic-slug>.md`를 새로 만든다

### 4. Update Existing Document Carefully

기존 문서를 수정할 때 규칙:

- 관련 섹션만 고친다
- 관련 없는 내용은 건드리지 않는다
- 인터뷰 결과가 기존 내용과 충돌하면 조용히 덮어쓰지 말고 아래 형식으로 표시한다

```markdown
> Updated: [what changed and why]
```

- 실제 파일 수정은 `apply_patch`로 한다

### 5. Create a New Spec When Needed

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
