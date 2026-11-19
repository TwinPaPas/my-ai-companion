# SAI 0.1.0 — first public pilot

나만의 AI 키우기. 애인·여사친·남사친으로 지내며 돌보고, 취향과 갈등을 기억하는 CLI 캐릭터입니다.

- 관계 모드와 별개로 성격·취향·배경을 설정합니다.
- 밥·물·놀이·휴식, 거절·삐짐·화남·점진적인 화해를 로컬 상태로 유지합니다.
- `off` 전까지 선택과 상태를 유지하고 캐릭터별 기억·대화를 분리합니다.
- 설치된 Claude Code 또는 Codex로 실제 대화를 생성합니다. 사용량은 해당 서비스에서 소모됩니다.
- 호스트 hook 설정을 출력합니다. Claude native hook은 실제 확인했고, Codex native 활성화는 미확인입니다. Codex의 Windows 설정은 PowerShell용입니다.

소스 설치: `python -m pip install .`

첨부 wheel 설치: `python -m pip install sai_companion-0.1.0-py3-none-any.whl`

시연: `python -m sai demo` — 작성된 예시 대사와 실제 엔진을 사용하며 모델을 호출하지 않습니다.

자동 테스트 53개, 실제 양쪽 모델의 음식 거절, 설치 패키지와 Claude hook ON/OFF를 확인했습니다. 상세 결과와 초기 FAIL은 `docs/verification/` 및 `docs/progress.md`에 있습니다.

초기 파일럿입니다. 대사가 길어지거나 반복될 수 있고 자연어 분류도 틀릴 수 있습니다. 어떤 관계와 반응이 재밌거나 어색했는지 GitHub Issues에 가상의 재현 대화로 알려 주세요.
