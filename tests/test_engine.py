import unittest

from sai.engine import apply_action, new_character


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.s = new_character("하루", "female-friend", likes=["떡볶이"],
                               dislikes=["오이"], boundaries=["외모"])
        self.s["updated_at"] = 1000.0

    def act(self, action, detail="", now=1000):
        self.s, result = apply_action(self.s, action, detail, now)
        return result

    def test_care_changes_specific_needs(self):
        self.s["needs"] = dict(hunger=75, thirst=75, boredom=75, fatigue=75)
        for action, key in [("feed", "hunger"), ("water", "thirst"),
                            ("play", "boredom"), ("rest", "fatigue")]:
            before = self.s["needs"][key]
            self.assertTrue(self.act(action, "떡볶이" if action == "feed" else "")["accepted"])
            self.assertLess(self.s["needs"][key], before)

    def test_tastes_survive_high_affection(self):
        self.s["affection"] = 100
        before = self.s["needs"]["hunger"]
        r = self.act("feed", "오이")
        self.assertFalse(r["accepted"])
        self.assertEqual(self.s["needs"]["hunger"], before)

    def test_hurt_has_cause_and_gift_does_not_erase_it(self):
        self.act("tease", "외모")
        self.assertEqual(self.s["mood"], "sulking")
        self.assertEqual(self.s["concern"], "외모")
        self.act("tease", "외모", 1061)
        self.assertEqual(self.s["mood"], "angry")
        self.act("gift", "꽃", 1122)
        self.assertEqual(self.s["concern"], "외모")
        self.assertEqual(self.s["mood"], "angry")

    def test_apology_must_address_cause_and_repair_is_gradual(self):
        self.act("tease", "외모")
        self.act("tease", "외모", 1061)
        anger = self.s["irritation"]
        self.act("apologize", "그냥 미안", 1122)
        self.assertEqual(self.s["irritation"], anger)
        self.act("apologize", "외모를 놀려서 미안", 1183)
        self.assertGreater(self.s["irritation"], 0)
        self.assertLess(self.s["irritation"], anger)
        self.assertEqual(self.s["concern"], "외모")
        self.act("apologize", "외모 이야기는 그만할게", 1244)
        self.assertLess(self.s["irritation"], anger)

    def test_offline_time_does_not_remove_trust(self):
        trust = self.s["trust"]
        self.act("talk", "안녕", 1000 + 365 * 86400)
        self.assertEqual(self.s["trust"], trust)
        self.assertLessEqual(max(self.s["needs"].values()), 100)
        self.assertNotIn(self.s["mood"], ["angry", "sulking"])

    def test_repeat_care_does_not_farm_experience(self):
        self.act("water")
        xp = self.s["xp"]
        self.act("water", now=1001)
        self.assertEqual(self.s["xp"], xp)

    def test_invalid_action_and_oversized_details_leave_input_unchanged(self):
        import copy
        before = copy.deepcopy(self.s)
        for action, detail in [("delete", "all"), ("feed", "x" * 1001)]:
            with self.assertRaises(ValueError):
                apply_action(self.s, action, detail, 1000)
        self.assertEqual(self.s, before)

    def test_gender_does_not_choose_temperament(self):
        for role in ["lover", "female-friend", "male-friend"]:
            self.assertEqual(new_character("윤", role, "blunt")["temperament"], "blunt")


if __name__ == "__main__":
    unittest.main()
