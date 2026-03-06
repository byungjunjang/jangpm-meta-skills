# Jangpm Meta Skills for Claude Code and Codex

에이전트 시스템을 설계하고 요구사항을 파고들고 세션을 마무리하기 위한 메타 스킬 모음입니다.

- Claude Code 배포본: `.claude/`
- Codex 배포본: `.codex/skills/`

## 포함된 스킬

| Skill | 역할 | Claude Code | Codex |
|---|---|---|---|
| `blueprint` | 자동화/에이전트 시스템 설계서 작성 | `/blueprint` 커맨드 + skill | `blueprint` 또는 `$blueprint` |
| `deep-dive` | 다회차 인터뷰로 상세 스펙 문서 작성 | `/deep-dive` 커맨드 + skill | `deep-dive` 또는 `$deep-dive` |
| `reflect` | 작업 세션 정리, 문서 반영 포인트, 다음 액션 도출 | `/reflect` 커맨드 + skill | `reflect` 또는 `$reflect` |

## 저장소 구조

```text
.claude/
  commands/
  skills/

.codex/
  skills/
    blueprint/
    deep-dive/
    reflect/
```

## Codex 설치

Codex 사용자는 세 스킬 폴더를 `~/.codex/skills/`로 복사하면 됩니다.

### Windows PowerShell

```powershell
Copy-Item -Recurse .\.codex\skills\blueprint  "$env:USERPROFILE\.codex\skills\"
Copy-Item -Recurse .\.codex\skills\deep-dive  "$env:USERPROFILE\.codex\skills\"
Copy-Item -Recurse .\.codex\skills\reflect    "$env:USERPROFILE\.codex\skills\"
```

### macOS / Linux

```bash
cp -r ./.codex/skills/blueprint ~/.codex/skills/
cp -r ./.codex/skills/deep-dive ~/.codex/skills/
cp -r ./.codex/skills/reflect   ~/.codex/skills/
```

## Claude Code 설치

기존 Claude Code 배포 방식도 그대로 유지합니다.

### Windows PowerShell

```powershell
Copy-Item -Recurse .\.claude\skills\blueprint  "$env:USERPROFILE\.claude\skills\"
Copy-Item -Recurse .\.claude\skills\deep-dive  "$env:USERPROFILE\.claude\skills\"
Copy-Item -Recurse .\.claude\skills\reflect    "$env:USERPROFILE\.claude\skills\"

Copy-Item .\.claude\commands\blueprint.md  "$env:USERPROFILE\.claude\commands\"
Copy-Item .\.claude\commands\deep-dive.md  "$env:USERPROFILE\.claude\commands\"
Copy-Item .\.claude\commands\reflect.md    "$env:USERPROFILE\.claude\commands\"
```

### macOS / Linux

```bash
cp -r ./.claude/skills/blueprint ~/.claude/skills/
cp -r ./.claude/skills/deep-dive ~/.claude/skills/
cp -r ./.claude/skills/reflect   ~/.claude/skills/

cp ./.claude/commands/blueprint.md ~/.claude/commands/
cp ./.claude/commands/deep-dive.md ~/.claude/commands/
cp ./.claude/commands/reflect.md   ~/.claude/commands/
```

## Codex 배포본에서 바뀐 점

- Claude 전용 `/commands` 래퍼를 제거하고 `SKILL.md` 중심 구조로 정리했습니다.
- `.claude/...` 경로, `Task` 기반 서브에이전트, `AskUserQuestion` 전제를 Codex 흐름에 맞게 바꿨습니다.
- `blueprint`에는 Codex 기준 문서 템플릿, 설계 원칙, 구조 검증 스크립트를 포함했습니다.
- 세 스킬 모두 `agents/openai.yaml`을 추가해 Codex UI 메타데이터를 함께 배포합니다.

## 라이선스

MIT
