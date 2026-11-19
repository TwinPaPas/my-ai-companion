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
    accepted, reason = True, "함께 이야기를 나눴습니다."
    reward = action != "tease"
    disliked = next((v for v in s["dislikes"] if v.casefold() in detail.casefold()), "")
    boundary = next((v for v in s["boundaries"] if v.casefold() in detail.casefold()), "")
    if action in ("feed", "gift", "play") and disliked:
        accepted, reward = False, False
        reason = f"{disliked}은/는 취향에 맞지 않아 거절했습니다. 다른 제안을 해 주세요."
    elif action == "tease" and boundary:
        s["irritation"] = min(100, s["irritation"] + 35)
        s["trust"] = max(0, s["trust"] - 7)
        s["concern"] = boundary
        reason = f"싫다고 정한 {boundary}에 관한 놀림 때문에 마음이 상했습니다."
    elif action == "tease":
        reward = False
        reason = "장난을 받았습니다. 성격과 현재 기분에 맞게 받아치거나 선을 그을 수 있습니다."
    elif action == "apologize":
        if s["concern"] and s["concern"].casefold() in detail.casefold():
            s["irritation"] = max(0, s["irritation"] - 25)
            s["trust"] = min(100, s["trust"] + 3)
            reason = f"{s['concern']}에 대한 사과를 들었습니다. 마음이 조금 풀렸습니다."
            if s["irritation"] == 0:
                s["concern"] = ""
                reason = "이유를 짚은 사과를 받아들이고 화해했습니다."
        elif s["concern"]:
            accepted, reward = False, False
            reason = f"아직 {s['concern']} 때문에 속상합니다. 그 일을 짚어 주었으면 합니다."
        else:
            reward = False
            reason = "현재 풀어야 할 갈등은 없습니다."
    elif action == "play" and (s["irritation"] >= 60 or s["needs"]["fatigue"] >= 85):
        accepted, reward = False, False
        reason = "지금은 놀 기분이 아닙니다. 먼저 쉬거나 마음 상한 이유를 이야기해 주세요."
    elif action == "feed":
        s["needs"]["hunger"] = max(0, s["needs"]["hunger"] - 35)
        reason = f"{detail or '식사'}을/를 챙겨 주었습니다."
    elif action == "water":
        s["needs"]["thirst"] = max(0, s["needs"]["thirst"] - 45)
        reason = "물을 챙겨 주었습니다."
    elif action == "play":
        s["needs"]["boredom"] = max(0, s["needs"]["boredom"] - 35)
        s["needs"]["fatigue"] = min(100, s["needs"]["fatigue"] + 8)
        reason = f"{detail or '작은 놀이'}을/를 함께 했습니다."
    elif action == "rest":
        s["needs"]["fatigue"] = max(0, s["needs"]["fatigue"] - 45)
        reason = "편히 쉴 시간을 가졌습니다."
    elif action == "gift":
        reason = f"{detail or '작은 선물'}을/를 받았습니다."
        if s["concern"]:
            reason += f" 선물은 고맙지만 {s['concern']}에 대한 갈등은 그대로입니다."
    elif action == "comfort":
        s["needs"]["boredom"] = max(0, s["needs"]["boredom"] - 10)
        reason = "마음을 들어 주었습니다. 해결되지 않은 일은 차분히 이야기할 수 있습니다."
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
