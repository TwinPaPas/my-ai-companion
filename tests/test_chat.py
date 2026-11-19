import json
import tempfile
import unittest

from sai.chat import Conversation, parse_intent
from sai.store import Store


class FixtureModel:
    """Scripted external model responses; assertions target engine/state effects."""
    def __init__(self, *replies):
        self.replies = iter(replies)

    def generate(self, prompt):
        response = next(self.replies)
        if isinstance(response, Exception):
            raise response
        return response


class ChatTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = Store(self.tmp.name)
        self.store.create("하루", "female-friend", dislikes=["오이"], boundaries=["외모"])

    def test_natural_care_updates_engine_before_reply(self):
        model = FixtureModel('{"action":"feed","detail":"오이"}', "오이는 싫어. 다른 거 먹자.")
        result = Conversation(self.store, model).turn("오이 먹자")
        self.assertFalse(result["event"]["accepted"])
        self.assertEqual(result["reply"], "오이는 싫어. 다른 거 먹자.")
        self.assertEqual(self.store.history()[0]["reply"], result["reply"])

    def test_bad_intent_is_not_applied(self):
        before = self.store.status()
        for response in ['{"action":"erase","detail":"all"}', 'not json', '{"action":"feed","detail":{}}']:
            with self.assertRaises(ValueError):
                Conversation(self.store, FixtureModel(response)).turn("밥 먹자")
        self.assertEqual(self.store.status(), before)
        self.assertEqual(self.store.history(), [])

    def test_failed_classifier_does_not_mutate_state(self):
        before = self.store.status()
        with self.assertRaises(RuntimeError):
            Conversation(self.store, FixtureModel(RuntimeError("offline"))).turn("안녕")
        self.assertEqual(self.store.status(), before)

    def test_failed_dialogue_has_no_fabricated_history(self):
        model = FixtureModel('{"action":"water","detail":"물"}', RuntimeError("offline"))
        with self.assertRaises(RuntimeError):
            Conversation(self.store, model).turn("물 줄게")
        self.assertEqual(self.store.history(), [])
        self.assertLess(self.store.status()["needs"]["thirst"], 25)

    def test_off_command_works_without_model(self):
        result = Conversation(self.store, FixtureModel()).turn("/sai off")
        self.assertFalse(self.store.status()["enabled"])
        self.assertFalse(result["enabled"])
        with self.assertRaises(ValueError):
            Conversation(self.store, FixtureModel()).turn("안녕")

    def test_explicit_action_does_not_need_classification(self):
        result = Conversation(self.store, FixtureModel("물 고마워.")).turn("/sai act water")
        self.assertEqual(result["reply"], "물 고마워.")
        self.assertLess(self.store.status()["needs"]["thirst"], 25)

    def test_classifier_cannot_modify_personality_or_remember_implicitly(self):
        with self.assertRaises(ValueError):
            parse_intent('{"action":"talk","detail":"","trust":100}')

    def test_remember_and_forget_are_explicit(self):
        convo = Conversation(self.store, FixtureModel())
        result = convo.turn('/sai remember "민트초코를 좋아해"')
        self.assertEqual(len(self.store.memories()), 1)
        convo.turn("/sai forget " + result["id"])
        self.assertEqual(self.store.memories(), [])


if __name__ == "__main__":
    unittest.main()
