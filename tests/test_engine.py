import json
import tempfile
import unittest
from pathlib import Path

from chatbot import IntentChatbot


ROOT = Path(__file__).resolve().parents[1]


class IntentChatbotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        dataset = json.loads((ROOT / "data" / "intents.json").read_text())
        cls.bot = IntentChatbot(threshold=0.25, seed=1)
        cls.metrics = cls.bot.train(dataset)

    def test_training_metrics(self) -> None:
        self.assertEqual(self.metrics["intents"], 10)
        self.assertGreaterEqual(self.metrics["documents"], 50)
        self.assertGreater(self.metrics["vocabulary"], 50)

    def test_predicts_python_question(self) -> None:
        prediction = self.bot.predict("Could you teach me Python programming?")
        self.assertEqual(prediction.intent, "python")
        self.assertGreater(prediction.confidence, 0.25)

    def test_predicts_training_question(self) -> None:
        prediction = self.bot.predict("How can I retrain the chatbot?")
        self.assertEqual(prediction.intent, "training")

    def test_blank_message_uses_fallback(self) -> None:
        prediction = self.bot.predict("   ")
        self.assertEqual(prediction.intent, "fallback")

    def test_saved_model_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.json"
            self.bot.save(path)
            restored = IntentChatbot.load(path)
            self.assertEqual(restored.predict("hello").intent, "greeting")


if __name__ == "__main__":
    unittest.main()
