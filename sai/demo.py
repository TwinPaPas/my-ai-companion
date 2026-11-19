"""A repeatable mechanics demonstration, explicitly not model inference."""
from .engine import apply_action, new_character


def demo():
    state = new_character("Ari", "female-friend", likes=["spicy noodles"], dislikes=["cucumber"], boundaries=["appearance"])
    state["updated_at"] = 1000
    script = [
        ("feed", "cucumber", "Cucumber? You know that's not my thing. How about spicy noodles?"),
        ("feed", "spicy noodles", "You remembered my favorite? Come on, let's share."),
        ("water", "", "Water too? Someone's being thoughtful today."),
        ("play", "word game", "You're on. I get to go first this time."),
        ("tease", "appearance", "Hey. I told you I don't like jokes about my appearance."),
        ("tease", "appearance", "I asked you to stop. I'm not laughing this time."),
        ("gift", "flowers", "The flowers are lovely. But we still need to talk about earlier."),
        ("apologize", "I'm sorry for teasing your appearance", "Thanks for understanding why it hurt. Give me a little time."),
        ("apologize", "I'll stop joking about your appearance", "Okay. I'll remember that promise. I feel a little better."),
        ("apologize", "I won't tease your appearance again", "All right. We're okay. Next time, pick something we can both laugh about."),
    ]
    events = []
    for i, (action, detail, line) in enumerate(script):
        state, result = apply_action(state, action, detail, 1000 + i * 61)
        events.append({"action": action, "detail": detail, "accepted": result["accepted"],
                       "mood": state["mood"], "concern": state["concern"], "line": line})
    return {"kind": "scripted-demo", "note": "These lines are written examples. Mood and care changes come from the real engine.", "events": events}
