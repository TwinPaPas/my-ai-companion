"""A repeatable mechanics demonstration, explicitly not model inference."""
from .engine import apply_action, new_character


def demo():
    state = new_character("하루", "female-friend", likes=["떡볶이"], dislikes=["오이"], boundaries=["외모"])
    state["updated_at"] = 1000
    script = [
        ("feed", "오이", "오이는 싫어. 떡볶이로 바꾸면 안 돼?"),
        ("feed", "떡볶이", "내가 좋아하는 거 기억했네? 같이 먹자."),
        ("water", "", "물까지? 오늘 제법 세심한데."),
        ("play", "끝말잇기", "좋아. 이번엔 내가 먼저 할래."),
        ("tease", "외모", "외모로 놀리는 건 싫다고 했잖아."),
        ("tease", "외모", "그만하라고 했어. 지금은 그 장난 안 받아 줄 거야."),
        ("gift", "꽃", "꽃은 고마워. 근데 아까 얘기는 아직 안 끝났어."),
        ("apologize", "외모를 놀려서 미안", "왜 속상했는지 알아준 건 고마워. 조금만 기다려 줘."),
        ("apologize", "외모 이야기를 멈출게", "응. 그 약속은 기억할게. 좀 풀리는 것 같아."),
        ("apologize", "외모로 다시 놀리지 않을게", "알았어. 이제 풀자. 다음엔 좋아하는 걸로 장난쳐."),
    ]
    events = []
    for i, (action, detail, line) in enumerate(script):
        state, result = apply_action(state, action, detail, 1000 + i * 61)
        events.append({"action": action, "detail": detail, "accepted": result["accepted"],
                       "mood": state["mood"], "concern": state["concern"], "line": line})
    return {"kind": "scripted-demo", "note": "대사는 작성된 예시입니다. 감정·돌봄 상태는 실제 엔진으로 계산합니다.", "events": events}
