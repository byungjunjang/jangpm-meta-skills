---
name: blueprint
description: Codex용 자동화 에이전트 시스템 설계서 생성 스킬. 사용자 인터뷰로 요구사항을 정리하고 Codex 구현 기준의 통합 설계 문서(.md)를 작성한다. Use when the user asks for "/blueprint", "blueprint", "에이전트 설계", "설계서 만들어", "agentic workflow design", or any request to plan a Codex automation or agent workflow.
metadata:
  short-description: Create a Codex automation blueprint
---

# Blueprint

## Overview

사용자가 자동화하려는 작업을 짧게 인터뷰한 뒤, Codex 구현 기준의 단일 설계 문서 `./blueprint-<task-name>.md`를 작성한다.

- 기본 가정은 `단일 Codex 에이전트 + 필요 시 skills/scripts 조합`이다.
- Claude Code 전용 요소인 `.claude/commands`, `.claude/agents`, `AGENT.md`, `Task` 기반 서브에이전트 구조는 설계에 넣지 않는다.
- 구현 스펙은 구조와 역할 수준까지만 다루고, 실제 코드 본문이나 장문 프롬프트는 쓰지 않는다.

## Workflow

### 1. Assess Gaps First

아래 네 영역을 먼저 점검하고, 비어 있는 부분만 질문한다.

| 영역 | 최소 확인 항목 |
|---|---|
| 목표와 성공 기준 | 무엇이 완료 상태인지, 실패는 무엇인지 |
| 작업 절차 | 입력, 출력, 분기 조건, 사람 개입 지점 |
| 실행 환경 | 파일 형식, API, 외부 도구, 저장 위치 |
| 제약 조건 | 정확도, 비용, 속도, 보안, 권한, 운영 범위 |

질문 규칙:

- 한 번에 최대 3개까지만 묻는다.
- Default mode에서는 평문 메시지로 직접 질문한다.
- 사용자가 모르는 항목은 합리적인 기본값을 채우고, 문서에 그 가정을 명시한다.
- 최대 3라운드 안에 끝내고, 그 뒤에는 가정과 리스크를 적고 작성 단계로 넘어간다.

### 2. Write the Blueprint

다음 두 참고 문서를 읽고 그대로 반영한다.

- `references/document-template.md`
- `references/design-principles.md`

작성 규칙:

- 최종 산출물 경로는 프로젝트 루트의 `./blueprint-<task-name>.md`
- 중간 산출물은 `output/stepNN_<name>.<ext>` 규칙 사용
- 각 워크플로우 단계는 반드시 아래 9개 필드를 모두 포함
  1. Step Goal
  2. Input / Output
  3. LLM Decision Area
  4. Code Processing Area
  5. Success Criteria
  6. Validation Method
  7. Failure Handling
  8. Skills / Scripts
  9. Intermediate Artifact Rule
- 상태 토큰은 `COLLECTING_REQUIREMENTS`, `PLANNING`, `RUNNING_SCRIPT`, `VALIDATING`, `NEEDS_USER_INPUT`, `DONE`, `FAILED`를 모두 넣는다.

### 3. Validate Before Hand-off

문서를 저장한 뒤 아래 검증을 수행한다.

```powershell
python .codex/skills/blueprint/scripts/validate_blueprint_doc.py ./blueprint-<task-name>.md
```

- 실패하면 문서를 수정하고 다시 실행한다.
- 이 검증은 문서 구조 검사용이다.
- Codex skill 자체를 추가/수정하는 경우에는 별도로 `skill-creator`의 `quick_validate.py`를 사용한다.

### 4. Review

사용자에게 문서 경로와 핵심 결정사항을 짧게 요약해서 보여주고, 수정이 필요한지만 확인한다.

## Notes

- 문서 구조는 템플릿의 영문 헤더를 유지한다. 검증 스크립트가 그 헤더를 기준으로 동작한다.
- Skill 설계나 추가가 스코프에 포함되면 `skill-creator`를 사용한다고 문서에 명시한다.
- 새 skill 폴더를 설계할 때는 `.codex/skills/<skill-name>/` 기준으로 적고, 불필요한 문서는 만들지 않는다.
