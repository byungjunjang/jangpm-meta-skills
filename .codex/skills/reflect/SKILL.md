---
name: reflect
description: Codex 작업 세션 마무리 스킬. 이번 세션의 변경 사항을 정리하고, 문서 반영 포인트, 자동화 아이디어, 학습 포인트, 다음 액션을 한 번에 정리한다. Use when the user asks for "/reflect", "reflect", "session reflect", "end session", or wants a Codex session wrap-up.
metadata:
  short-description: Summarize a Codex session and next actions
---

# Reflect

## Overview

Codex 세션을 마무리하면서 변경 사항과 후속 조치를 정리한다.

- Claude Code의 `Task` 기반 병렬 서브에이전트 흐름을 그대로 쓰지 않는다
- Codex 안에서 직접 파일과 변경 사항을 조사하고, 결과를 스스로 통합한다
- 기본값은 `report first, edit only when needed`다

## Workflow

### 1. Inspect Session State

먼저 현재 상태를 짧게 정리한다.

- 현재 워크스페이스 파일 구조
- 이번 세션에 생성/수정한 파일
- `git status --short` 또는 관련 diff가 보여주는 변경 범위
- 주요 문서(`README.md`, `AGENTS.md`, 최근 스펙/설계 문서) 존재 여부

이 정보를 한두 문장짜리 `PROJECT_STATE`로 압축해 내부 기준으로 사용한다.

### 2. Produce Four Analyses

아래 네 범주를 모두 점검한다.

1. Docs to update
   - 어떤 문서가 실제 변경을 반영하지 못하는지
2. Automation ideas
   - 반복 작업 중 스킬, 스크립트, 훅으로 뺄 만한 것이 있는지
3. Learnings
   - 이번 세션에서 새로 확인한 패턴, 제약, 도구 사용법
4. Next actions
   - 지금 당장 이어서 해야 할 후속 작업 1~3개

규칙:

- 실제로 한 일만 바탕으로 적는다
- 중복되는 항목은 하나로 합친다
- 중요도와 실행 가능성이 낮은 항목은 버린다

### 3. Decide Whether to Apply Changes

사용자가 명시적으로 문서 갱신까지 원하면 바로 적용한다.

그 외에는 먼저 요약을 보여주고, 아래 중 어떤 후속 작업을 할지 한 문장으로 확인한다.

- 문서 반영
- 자동화 아이디어 기록
- 학습 노트 기록
- 요약만 제공

### 4. Apply Updates Carefully

후속 편집을 할 때 규칙:

- 기존 문서가 있으면 거기에 반영한다
- 관련 없는 문서는 만들지 않는다
- 학습 노트나 로그 파일이 없으면 임의의 잡문서를 늘리지 말고 추천 경로만 제안한다
- 파일 수정은 `apply_patch`를 사용한다

### 5. Final Output Format

결과는 아래 순서로 짧게 정리한다.

1. Session summary
2. Docs to update
3. Automation ideas
4. Learnings
5. Next actions

실제 파일을 수정했다면 수정한 파일 경로도 함께 적는다.

## Notes

- Codex에서는 이 스킬을 실행할 때 별도 서브에이전트나 `AskUserQuestion` 전용 도구를 가정하지 않는다.
- 필요한 병렬 읽기 작업만 `multi_tool_use.parallel`로 묶고, 판단과 통합은 메인 흐름에서 처리한다.
