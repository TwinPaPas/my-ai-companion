"""Small deterministic rules; the language model supplies the performance."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import time
import uuid

ROLES = ("lover", "female-friend", "male-friend", "custom")
TEMPERAMENTS = ("playful", "warm", "blunt")
ACTIONS = ("feed", "water", "play", "rest", "gift", "tease", "apologize", "comfort", "talk")


def checked_text(value: str, label: str, limit: int = 1000, empty: bool = True) -> str:
    if not isinstance(value, str) or len(value) > limit:
        raise ValueError(f"{label}: expected text of at most {limit} characters")
    if any(ord(c) < 32 and c not in "\n\t" for c in value):
        raise ValueError(f"{label}: control characters are not allowed")
    value = value.strip()
    if not empty and not value:
        raise ValueError(f"{label}: empty text")
    return value


def new_character(name, role, temperament="playful", likes=(), dislikes=(), boundaries=(), backstory=""):
    name = checked_text(name, "name", 60, False)
    if role not in ROLES or temperament not in TEMPERAMENTS:
        raise ValueError("Unknown role or temperament")
    backstory = checked_text(backstory, "backstory")
    if role == "custom" and not backstory:
        raise ValueError("custom role needs a backstory describing the relationship")
    tastes = {}
    for label, values in [("likes", likes), ("dislikes", dislikes), ("boundaries", boundaries)]:
        if isinstance(values, str) or len(values) > 12:
            raise ValueError(f"{label}: provide up to 12 separate entries")
        tastes[label] = list(dict.fromkeys(checked_text(v, label, 100, False) for v in values))
    return {
        "id": uuid.uuid4().hex[:12], "name": name, "role": role,
        "temperament": temperament, "backstory": backstory, **tastes,
        "needs": {"hunger": 25, "thirst": 25, "boredom": 25, "fatigue": 15},
        "affection": 25, "trust": 40, "irritation": 0, "concern": "", "mood": "curious",
        "xp": 0, "stage": "getting-to-know-you", "updated_at": time.time(),
        "last_reward": {}, "reward_day": "", "rewards_today": 0,
    }


def apply_action(state, action, detail="", now=None):
    if action not in ACTIONS:
        raise ValueError(f"Unknown action: {action}")
    detail = checked_text(detail, "detail")
    now = time.time() if now is None else float(now)
    s = deepcopy(state)
    hours = min(8.0, max(0.0, now - s["updated_at"]) / 3600)
    for key, rate in [("hunger", 3), ("thirst", 4), ("boredom", 2), ("fatigue", 1)]:
        s["needs"][key] = min(100, s["needs"][key] + hours * rate)
    s["updated_at"] = max(now, s["updated_at"])
    accepted, reason = True, "You spent some time talking together."
    reward = action != "tease"
    disliked = next((v for v in s["dislikes"] if v.casefold() in detail.casefold()), "")
    boundary = next((v for v in s["boundaries"] if v.casefold() in detail.casefold()), "")
    if action in ("feed", "gift", "play") and disliked:
        accepted, reward = False, False
        reason = f"They declined: {disliked} is not their thing. Try offering something else."
    elif action == "tease" and boundary:
        s["irritation"] = min(100, s["irritation"] + 35)
        s["trust"] = max(0, s["trust"] - 7)
        s["concern"] = boundary
        reason = f"Teasing about {boundary} hurt their feelings; they had set a boundary about it."
    elif action == "tease":
        reward = False
        reason = "They noticed the teasing and may tease back or draw a line, depending on their personality and mood."
    elif action == "apologize":
        if s["concern"] and s["concern"].casefold() in detail.casefold():
            s["irritation"] = max(0, s["irritation"] - 25)
            s["trust"] = min(100, s["trust"] + 3)
            reason = f"Your apology acknowledged {s['concern']}. They are starting to soften."
            if s["irritation"] == 0:
                s["concern"] = ""
                reason = "They accepted the apology that addressed what hurt. You have made up."
        elif s["concern"]:
            accepted, reward = False, False
            reason = f"They are still upset about {s['concern']} and want that concern acknowledged."
        else:
            reward = False
            reason = "There is no unresolved disagreement right now."
    elif action == "play" and (s["irritation"] >= 60 or s["needs"]["fatigue"] >= 85):
        accepted, reward = False, False
        reason = "They are not in the mood to play. Try some rest or talk about what upset them."
    elif action == "feed":
        s["needs"]["hunger"] = max(0, s["needs"]["hunger"] - 35)
        reason = f"You brought them {detail or 'a meal'}."
    elif action == "water":
        s["needs"]["thirst"] = max(0, s["needs"]["thirst"] - 45)
        reason = "You brought them some water."
    elif action == "play":
        s["needs"]["boredom"] = max(0, s["needs"]["boredom"] - 35)
        s["needs"]["fatigue"] = min(100, s["needs"]["fatigue"] + 8)
        reason = f"You enjoyed {detail or 'a little game'} together."
    elif action == "rest":
        s["needs"]["fatigue"] = max(0, s["needs"]["fatigue"] - 45)
        reason = "They had some time to rest."
    elif action == "gift":
        reason = f"They received {detail or 'a small gift'}."
        if s["concern"]:
            reason += f" They appreciate it, but the disagreement about {s['concern']} is still unresolved."
    elif action == "comfort":
        s["needs"]["boredom"] = max(0, s["needs"]["boredom"] - 10)
        reason = "You listened to how they feel. There is room to talk calmly about anything unresolved."
    day = datetime.fromtimestamp(now, timezone.utc).date().isoformat()
    if s["reward_day"] != day:
        s["reward_day"], s["rewards_today"] = day, 0
    reward_key = action + ":" + detail.casefold()
    if reward and s["rewards_today"] < 10 and now - s["last_reward"].get(reward_key, -1e12) >= 30:
        s["xp"] += 1
        s["affection"] = min(100, s["affection"] + 1)
        s["rewards_today"] += 1
        s["last_reward"][reward_key] = now
        s["last_reward"] = dict(sorted(s["last_reward"].items(), key=lambda x: x[1])[-30:])
    s["stage"] = "familiar" if s["xp"] >= 10 else "getting-to-know-you"
    if s["xp"] >= 30:
        s["stage"] = "shared-history"
    s["mood"] = ("angry" if s["irritation"] >= 60 else "sulking" if s["concern"]
                 else "tired" if s["needs"]["fatigue"] >= 80 else "comfortable" if s["xp"] >= 10
                 else "curious")
    return s, {"accepted": accepted, "reason": reason, "action": action,
               "detail": detail, "mood": s["mood"]}
