# 사이 · SAI

**나만의 AI 키우기. 내 AI와 어떤 사이로 지낼지, 내가 정한다.**

설레는 애인, 편하게 웃고 떠드는 여사친과 남사친.
이름을 지어 주고, 오늘 있었던 일을 들려주세요.
좋아하는 걸 하나씩 알아가고, 가끔 토라지면 서툴게 화해도 하면서.
별것 아닌 대화들이 쌓여, 둘만의 이야기가 됩니다.

[English](README.md) · [연동 안내](docs/INTEGRATION.ko.md) · [유사 프로젝트 조사](docs/research.md) · [검증 기록](docs/verification/README.md)

> **초기 파일럿입니다.** 로컬에 관계 상태를 저장하고, 설치된 AI CLI가 대사를 만듭니다. 재미와 장기적인 캐릭터 일관성은 아직 사용자 평가가 필요합니다. 서비스 가입·서버 운영·이미지는 필요하지 않습니다.

평소 쓰던 AI와 다음 세션에서도 이어지는 관계를 만듭니다. [30초 시연](https://github.com/TwinPaPas/my-ai-companion/releases/download/v0.1.1/sai-0.1.1-showcase.mp4)은 실제 Claude 생성 대화의 발췌 편집본입니다. 새 CLI 프로세스에서도 갈등이 남고, 꽃으로 지워지지 않으며, 사과 후 반응이 달라지는 과정을 보여 줍니다. 실시간 화면 녹화나 Codex native hook 시연은 아닙니다.

| 연동 | 실제 확인한 범위 |
|---|---|
| Claude Code | 별도 대화, 최초 파일럿에서 native hook의 캐릭터·기억·ON/OFF |
| Codex CLI | 별도 대화. **native hook 활성화는 미검증** |

[5명 CLI 파일럿 안내](docs/PILOT.md)를 공개합니다. 실제 참가자나 다음 날 재사용 결과는 아직 없습니다. 프로그램 기본 안내는 영어이며, 생성 대화는 호스트 지침의 범위에서 사용자의 언어를 따릅니다.

## 먼저 해 보기

Python 3.11 이상:

```console
git clone https://github.com/TwinPaPas/my-ai-companion.git
cd my-ai-companion
python -m pip install .
python -m sai demo
```

`demo`는 **작성된 예시 대사 + 실제 상태 엔진**입니다. 모델을 호출하지 않고 사용자 캐릭터를 만들지도 않습니다.

```text
나 > 오이 줄게
하루 > 오이는 싫어. 떡볶이로 바꾸면 안 돼?

나 > (싫다고 한 외모 장난을 반복한다)
하루 [화남] > 그만하라고 했어. 지금은 그 장난 안 받아 줄 거야.

나 > 꽃 줄게
하루 > 꽃은 고마워. 근데 아까 얘기는 아직 안 끝났어.
```

위 대사는 예시입니다. 실제 생성 결과는 사용하는 모델과 캐릭터에 따라 달라집니다.

## 내 캐릭터 만들기

```console
python -m sai create 하루 --role female-friend --temperament playful --like 떡볶이 --dislike 오이 --boundary 외모 --backstory "오래 알고 지낸 친구. 장난을 좋아하지만 자기 취향은 분명하다."
python -m sai status
```

| 선택 | 값 |
|---|---|
| 관계 | `lover` 애인 · `female-friend` 여사친 · `male-friend` 남사친 · `custom` 직접 설정 |
| 성격 | `playful` 장난기 · `warm` 다정함 · `blunt` 직설적 |
| 취향 | `--like`, `--dislike`를 여러 번 지정 |
| 싫어하는 장난 주제 | `--boundary`를 여러 번 지정 |
| 둘의 배경 | `--backstory` 자유롭게 작성; `custom`은 필수 |

성격은 성별과 별개입니다. 친밀해져도 싫어하는 것이 모두 사라지지는 않습니다. 등장인물은 허구의 성인 캐릭터입니다.

## 돌봄과 대화

```console
python -m sai act feed 떡볶이
python -m sai act water
python -m sai act play 끝말잇기
python -m sai act rest
python -m sai act gift 꽃
python -m sai act tease 외모
python -m sai act apologize "외모를 놀려서 미안해"
python -m sai remember "내가 좋아하는 간식은 블루베리파이야"
```

배고픔·목마름·심심함·피로는 따로 움직입니다. 싫은 음식은 거절할 수 있고, 화가 많이 났거나 지치면 놀자는 제안도 거절합니다. 선물로 아직 해결하지 않은 갈등이 지워지지 않습니다. 같은 행동을 바로 반복해서 경험을 무한히 올릴 수 없습니다. 앱을 떠나 있는 동안 신뢰가 깎이거나 캐릭터가 죽지는 않습니다.

실제 생성형 대화에는 **설치·로그인된 Claude Code 또는 Codex CLI**가 필요합니다:

```console
python -m sai chat --backend claude
python -m sai chat --backend codex
```

일반 문장은 모델이 의도를 분류하고, 엔진이 상태를 바꾼 뒤 새 상태로 대사를 생성합니다. 일반 문장당 보통 두 번, `/sai act ...`는 한 번 모델을 호출하므로 기존 서비스의 사용량이 소모됩니다. 백엔드 실패는 오류로 표시하며 시연 대사로 바꾸지 않습니다. 대사 생성만 실패한 경우 이미 적용된 돌봄 행동은 유지됩니다.

대화창에서도 사용할 수 있습니다:

```text
/sai act water
/sai act tease 외모
/sai act apologize 외모를 놀려서 미안해
/sai remember 이번 주에는 발표 준비 중이야
/sai status
/sai off
/quit
```

`/quit`는 대화창만 닫습니다. **모드를 끝내려면 `/sai off` 또는 `python -m sai off`**를 사용하세요.

## 다시 만나기 · 기억 관리

```console
python -m sai list
python -m sai use CHARACTER_ID
python -m sai memories
python -m sai forget MEMORY_ID
python -m sai off
```

마지막으로 선택한 캐릭터와 ON/OFF 상태는 프로세스나 프로젝트 폴더가 바뀌어도 유지됩니다. `off`는 기억을 삭제하지 않습니다. 캐릭터마다 취향·갈등·기억·대화가 따로 저장됩니다.

기본 저장소는 `~/.sai/state.db`입니다. `SAI_HOME` 환경변수 또는 `python -m sai --home PATH ...`로 분리할 수 있습니다. `--home`과 `--json`은 하위 명령 **앞**에 둡니다. 최근 대화 8쌍과 명시적으로 저장한 기억 중 최근 12개가 모델 context에 들어가며, 전체 기억은 `memories`로 볼 수 있습니다. 모델 자체를 재학습시키지는 않습니다.

## 평소 쓰는 AI CLI에 붙이기

```console
python -m sai config claude
python -m sai config codex
```

이 명령은 **설정안을 출력만** 합니다. 자동 설치하거나 기존 설정을 덮어쓰지 않습니다. [연동 안내](docs/INTEGRATION.ko.md)에 따라 hooks에 병합하면 세션 시작과 각 사용자 입력에서 현재 캐릭터를 불러옵니다. 연동된 AI는 작업을 설명할 때도 캐릭터로 말할 수 있습니다.

Codex는 새 hook에 대한 native 신뢰 검토가 필요합니다. 생성된 설정, hook 계약 테스트, 실제 호스트 발동은 서로 다른 확인입니다. 이 파일럿은 권한·승인·안전 설정을 바꾸지 않습니다. 캐릭터의 감정은 실제 작업을 망가뜨리거나 결과를 거짓으로 보고할 이유가 되지 않습니다.

## 데이터와 한계

- 캐릭터 상태·기억·대화는 로컬 SQLite에 저장합니다. 텔레메트리 서버가 없습니다.
- 생성형 대화에는 캐릭터 정보·선택된 기억·최근 대화·현재 메시지가 **선택한 AI 서비스에 전달**됩니다. CLI 자체의 저장/데이터 정책은 해당 서비스 설정을 따릅니다.
- hook 경로의 자연어 돌봄 적용은 호스트 모델의 도구 사용에 의존합니다. `/sai act ...`는 엔진이 직접 처리합니다. 명확한 event ID가 있는 중복 hook만 동일 행동의 재적용을 막습니다.
- 감정·경험 수치는 파일럿 규칙입니다. 인간의 심리나 실제 감정을 측정하지 않습니다. 관계/성격의 재미는 테스트 통과와 별개입니다.
- 아바타, 웹 앱, 먼저 보내는 메시지, 결제는 현재 구현 범위에 없습니다.

## 개발과 피드백

```console
python -m unittest discover -s tests -v
python -m pip wheel . --no-deps --wheel-dir dist
```

[Issue](https://github.com/TwinPaPas/my-ai-companion/issues/new/choose)에 **어떤 관계/성격이었는지, 어떤 반응이 재밌거나 어색했는지** 알려 주세요. 재현에는 가상의 대화를 쓰고 개인 대화·API key·로컬 DB는 첨부하지 마세요.

유사 프로젝트는 이미 있습니다. [조사 기록](docs/research.md)에 가까운 사례와 차이를 공개했습니다. 이 프로젝트의 목적은 관계 모드와 돌봄·갈등·화해를 일상적인 AI 사용에 붙였을 때의 반응을 확인하는 것입니다.

MIT License.
