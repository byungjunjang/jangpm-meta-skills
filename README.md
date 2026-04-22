# Jangpm Meta Skills (Claude Code & Codex용)

Claude Code와 Codex에서 에이전트 시스템 설계, 요구사항 구체화, 세션 마무리, 스킬 자동 최적화를 위한 메타 스킬 모음.

- Claude Code 배포: `.claude/`
- Codex 배포: `.agents/skills/` 또는 사용자 전역 `~/.agents/skills/`

## 스킬 목록

| 스킬 | 역할 | Claude Code | Codex |
|---|---|---|---|
| `blueprint` | 자동화/에이전트 시스템 설계 문서 작성 — 구조 검증 스크립트 포함 | `blueprint` 스킬 | `blueprint` 또는 `$blueprint` |
| `deep-dive` | 다단계 인터뷰를 통해 상세 스펙 문서 생성 | `deep-dive` 스킬 | `deep-dive` 또는 `$deep-dive` |
| `reflect` | 세션 마무리, 문서 반영, 학습 저장, 후속 액션 정리. 구체적 fix 확인 시 빠른 학습 캡처 포함 | `reflect` 스킬 | `reflect` 또는 `$reflect` |
| `autoresearch` | 스킬 자동 최적화 (반복 실행 + 평가 + 프롬프트 변형) — 개선된 스킬, `results.json`, `changelog.md`, 실시간 HTML 대시보드 생성 | `autoresearch` 스킬 | `autoresearch` 또는 `$autoresearch` |

## 스킬 워크플로우

네 가지 스킬은 다음 순서로 함께 사용할 때 가장 효과적입니다:

```
blueprint → deep-dive → [구현] → autoresearch → reflect
```

| 단계 | 스킬 | 사용 시점 |
|------|-------|-------------|
| 1. 설계 | `blueprint` | 새로운 에이전트/자동화 시작 시 — 코드 작성 전 완전한 설계 문서 생성 |
| 2. 스펙 | `deep-dive` | 요구사항 구체화가 필요할 때 — 구조화된 인터뷰로 스펙 문서 생성 |
| 3. 구현 | *(직접 코딩)* | 블루프린트와 스펙을 바탕으로 시스템 구축 |
| 4. 최적화 | `autoresearch` | 스킬 동작 확인 후 — 자동 평가 루프로 반복 개선 |
| 5. 마무리 | `reflect` | 작업 세션 종료 시 — 요약, 문서 반영, 학습 저장, 후속 액션 정리 |

**상황별 간단 패턴:**
- 새 프로젝트: `blueprint` → `deep-dive` → 구현 → `autoresearch` → `reflect`
- 중간 기능 추가: `deep-dive` → 구현 → `reflect`
- 스킬 최적화만: `autoresearch` 단독 실행
- 세션 마무리만: `reflect` 단독 실행
- 버그 수정 직후: 구현 → 구체적 fix 확인 문맥에서 `reflect`의 빠른 학습 캡처

## 디렉토리 구조

```text
.claude/
  skills/
    autoresearch/
      SKILL.md
      references/
        dashboard-guide.md     # 실행 중 실시간 HTML 대시보드
        eval-guide.md          # 이진/비교 평가 작성 방법
        execution-guide.md     # 실행 루프 동작 방식
        logging-guide.md       # results.json / results.tsv 스키마
        mutation-guide.md      # 프롬프트 변형 전략
        pipeline-guide.md      # 전체 파이프라인 개요
        worked-example.md      # 주석 포함 엔드투엔드 예시
    blueprint/
      SKILL.md
      references/
        document-template.md   # 출력 문서 섹션별 템플릿
        design-principles.md   # 에이전트 구조 및 설계 원칙
        example-blueprint.md   # 주석 포함 샘플 블루프린트
      scripts/
        validate_blueprint_doc.py  # 블루프린트 문서 구조 검증 스크립트
    deep-dive/
      SKILL.md
      references/
        question-library.md
        agent-design-questions.md
        anti-patterns.md
        reviewer-checklist.md
    reflect/
      SKILL.md

.agents/
  skills/
    autoresearch/
      SKILL.md
      agents/openai.yaml       # Codex UI 메타데이터
      references/              # (Claude Code와 동일)
    blueprint/
      SKILL.md
      agents/openai.yaml
      references/
      scripts/
    deep-dive/
      SKILL.md
      agents/openai.yaml
      references/
    reflect/
      SKILL.md
      agents/openai.yaml

.agents/
  agents/
    reviewer.toml             # optional: create only when you need a custom subagent
    explorer.toml             # optional: create only when you need a custom subagent
```

## 설치 (Codex)

네 개의 스킬 폴더를 `~/.agents/skills/`에 복사합니다.

### Windows PowerShell

```powershell
Copy-Item -Recurse .\.agents\skills\autoresearch "$env:USERPROFILE\.agents\skills\"
Copy-Item -Recurse .\.agents\skills\blueprint   "$env:USERPROFILE\.agents\skills\"
Copy-Item -Recurse .\.agents\skills\deep-dive   "$env:USERPROFILE\.agents\skills\"
Copy-Item -Recurse .\.agents\skills\reflect     "$env:USERPROFILE\.agents\skills\"
```

### macOS / Linux

```bash
mkdir -p ~/.agents/skills
cp -r ./.agents/skills/autoresearch ~/.agents/skills/
cp -r ./.agents/skills/blueprint    ~/.agents/skills/
cp -r ./.agents/skills/deep-dive    ~/.agents/skills/
cp -r ./.agents/skills/reflect      ~/.agents/skills/
```

## 설치 (Claude Code)

Claude Code 배포 방식도 동일하게 지원됩니다.

### Windows PowerShell

```powershell
Copy-Item -Recurse .\.claude\skills\autoresearch "$env:USERPROFILE\.claude\skills\"
Copy-Item -Recurse .\.claude\skills\blueprint   "$env:USERPROFILE\.claude\skills\"
Copy-Item -Recurse .\.claude\skills\deep-dive   "$env:USERPROFILE\.claude\skills\"
Copy-Item -Recurse .\.claude\skills\reflect     "$env:USERPROFILE\.claude\skills\"
```

### macOS / Linux

```bash
cp -r ./.claude/skills/autoresearch ~/.claude/skills/
cp -r ./.claude/skills/blueprint    ~/.claude/skills/
cp -r ./.claude/skills/deep-dive    ~/.claude/skills/
cp -r ./.claude/skills/reflect      ~/.claude/skills/
```

## Codex vs Claude Code 차이점

- 이 저장소는 `SKILL.md` 중심의 스킬 폴더로 두 플랫폼 배포를 모두 제공합니다. Claude 슬래시 커맨드(`/commands`) 래퍼 파일은 포함하지 않습니다.
- `.claude/...` 경로, `Task` 기반 서브에이전트, `AskUserQuestion` 처리를 Codex 흐름에 맞게 조정했습니다.
- `blueprint`는 Codex 호환 문서 템플릿, 설계 원칙, 구조 검증 스크립트를 포함합니다.
- `autoresearch`는 Claude Code와 Codex 양쪽에서 동일한 기능을 제공합니다. Codex에서는 명시적 위임 승인이 있는 기본 순차 실행 모델을 따릅니다.
- Codex 배포에는 각 스킬 폴더에 선택적 UI 메타데이터를 담은 `agents/openai.yaml` 파일이 포함됩니다.
- 공개 배포용 기본 정책으로 `blueprint`, `deep-dive`는 암묵 호출을 허용하고, `reflect`는 명시 호출과 구체적 fix confirmation 문맥에서의 제한적 암묵 호출을 함께 허용합니다. `autoresearch`는 명시 호출(`$autoresearch`)만 허용합니다.
- Codex의 커스텀 서브에이전트는 스킬 폴더가 아니라 `.agents/agents/*.toml`에 정의해야 합니다.
- 이 저장소는 커스텀 서브에이전트를 아직 포함하지 않으므로 `.agents/agents/` 디렉터리는 기본적으로 체크인하지 않습니다. 필요할 때만 `.agents/agents/`를 추가하면 됩니다.

## 라이선스

MIT
