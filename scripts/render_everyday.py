"""Render the everyday capture with the same established terminal playback design."""
def scenes(record):
    entries = {step["scene"]: dict(step) for step in record["steps"] if "reply" in step}
    quotes = {
        "recall": "Your short talk about sourdough, tomorrow. Welcome back.",
        "small-win": "Nice, the opening slide is the hardest one to commit to.",
        "own-taste": "Kind of you, but no, cucumber and I are not on speaking terms.",
        "back-to-work": "Sourdough is the only pet you feed for a week and then bake.",
        "break": "Spicy noodles, easy. The kind with enough heat to make my nose run",
    }
    for scene, quote in quotes.items():
        entry = entries[scene]
        reply = " ".join(entry["reply"].split())
        assert quote in reply
        entry["excerpt"] = quote + (" ..." if quote != reply else "")
        entry["display_prompt"] = entry["command"][-1].removesuffix(" Please reply in English.")
    work_prompt = "Help me choose a lighthearted opening line about sourdough."
    assert work_prompt in entries["back-to-work"]["display_prompt"]
    entries["back-to-work"]["display_prompt"] = work_prompt
    return [
        (3, "SAI / a little company", "One command. Pick up your story.", None,
         "python -m sai start\nReal Claude dialogue · standalone chat · v0.1.2"),
        (6, "01 / They remember", entries["recall"]["display_prompt"], entries["recall"],
         "A saved memory, recalled by a fresh chat process."),
        (4, "02 / A small win", entries["small-win"]["display_prompt"], entries["small-win"],
         "A moment of encouragement during the day."),
        (6, "03 / Their own taste", entries["own-taste"]["display_prompt"], entries["own-taste"],
         "Cucumber is a saved dislike. The engine declines it."),
        (5, "04 / Back to your day", entries["back-to-work"]["display_prompt"], entries["back-to-work"],
         "After a disagreement and apology: a new topic.\nThe concern remains saved; it need not dominate every reply."),
        (6, "05 / A little break", entries["break"]["display_prompt"], entries["break"],
         "Short replies. A familiar preference. Your story stays.\nTry it: python -m sai start"),
    ]


if __name__ == "__main__":
    from render_showcase import main
    raise SystemExit(main(everyday=True))
