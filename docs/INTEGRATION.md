# 기존 AI CLI 연동

이 파일럿은 두 경로를 제공합니다.

1. `python -m sai chat --backend claude|codex`: SAI 터미널에서 실제 모델 대화. SAI가 각 턴의 상태·context를 직접 준비합니다.
2. `SessionStart` / `UserPromptSubmit` hook: 평소 CLI에 현재 캐릭터 context를 추가합니다. 실제 작업 도구는 기존 호스트가 담당합니다.

## 설정안을 출력하고 병합하기

먼저 CLI가 사용하는 Python에 패키지를 설치하고 `python -m sai status`를 확인하세요.

```console
python -m sai config claude
python -m sai config codex
```

출력은 다음 구조입니다. 실행은 `python -m sai hook` 하나이며 설치된 패키지가 읽힐 수 있어야 합니다. 전역 설치 경로에 맞는 Python을 사용하세요. 다른 Python을 쓰는 환경에서는 host가 사용하는 셸에 맞게 실행 파일 경로를 인용해 바꿔야 합니다.

```json
{
  "hooks": {
    "SessionStart": [{"hooks": [{"type": "command", "command": "python -m sai hook", "timeout": 5}]}],
    "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "python -m sai hook", "timeout": 5}]}]
  }
}
```

- Claude Code: 사용자 `~/.claude/settings.json` 또는 원하는 프로젝트의 `.claude/settings.local.json`.
- Codex: 사용자 `~/.codex/hooks.json` 또는 원하는 프로젝트의 `.codex/hooks.json`.
- **기존 파일 전체를 위 내용으로 교체하지 마세요.** 기존 `hooks`의 두 이벤트 목록에 handler를 추가합니다. 이미 같은 command가 있으면 중복 추가하지 않습니다.
- 모든 프로젝트에 적용하려면 사용자 설정에 설치합니다. 프로젝트 설정은 그 프로젝트에서만 적용됩니다.
- Codex의 `/hooks`에서 native 검토/신뢰가 필요합니다. 이 저장소는 신뢰 hash를 쓰거나 검토를 우회하지 않습니다. 기존 세션이 설정을 다시 읽기 전에는 적용된 것으로 간주하지 마세요.
- 여러 설정 경로에 동시에 설치하면 hook이 중복될 수 있습니다. 한 범위만 선택하세요.

## 동작과 해제

저장된 활성 캐릭터를 매 세션/입력마다 불러옵니다. 저장소가 없으면 빈 context를 반환합니다. `/sai act ...`를 입력하면 hook이 행동을 적용하고 결과를 넘깁니다. 자연어 돌봄은 주입된 안내를 읽은 모델이 CLI를 호출해야 적용됩니다. 별도의 LLM 요청을 hook 자체에서 보내지는 않습니다.

```console
python -m sai off
```

다음 입력에서 `SAI_MODE=OFF`를 전달해 이전 캐릭터 안내를 해제합니다. 데이터는 보존됩니다. 이미 모델이 생성 중인 답변을 중간에 되돌리는 기능은 아닙니다.

설정 자체를 제거하려면 **추가한 `python -m sai hook` handler만** 삭제하고 호스트를 다시 시작하세요. 다른 hook은 보존합니다.

## 확인 방법

설정 출력 확인, stdin/stdout 계약 테스트, 호스트에서 실제 실행된 확인은 별개입니다. 실제 확인에서는 새 세션에서 캐릭터 이름과 저장한 기억을 물어본 뒤, 외부 터미널에서 `sai off`를 실행하고 다음 입력에 해제 상태가 반영되는지 확인하세요.

같은 state DB를 공유하는 모든 세션에 모드 변경이 영향을 줍니다. 동시에 서로 다른 캐릭터를 쓰려면 별도 `SAI_HOME`을 사용합니다. 명확한 `turn_id`/`event_id`가 전달된 행동만 중복 제거를 보장합니다. 호스트가 ID를 제공하지 않으면 같은 문장을 다시 말하는 것과 재전달을 완벽하게 구분하지 못합니다.

공식 근거: [Codex hooks](https://learn.chatgpt.com/docs/hooks), [Claude Code hooks](https://code.claude.com/docs/en/hooks). 실제 검증 범위는 [검증 기록](verification/README.md)에 따릅니다.
