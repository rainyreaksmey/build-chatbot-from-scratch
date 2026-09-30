"""Train the chatbot model from data/intents.json."""

import json
from pathlib import Path

from chatbot import IntentChatbot


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "intents.json"
MODEL_PATH = ROOT / "model" / "intent_model.json"


def train_model() -> dict[str, int]:
    dataset = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    bot = IntentChatbot()
    metrics = bot.train(dataset)
    bot.save(MODEL_PATH)
    return metrics


if __name__ == "__main__":
    result = train_model()
    print(f"Model saved to {MODEL_PATH}")
    print(
        f"Trained {result['documents']} examples across {result['intents']} "
        f"intents with {result['vocabulary']} unique words."
    )
