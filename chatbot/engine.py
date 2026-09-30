"""A compact multinomial Naive Bayes intent classifier.

This is deliberately implemented with the Python standard library so a
beginner can read the complete training algorithm.  It is useful for focused
FAQ and support bots; it is not a replacement for a generative large language
model.
"""

from __future__ import annotations

import json
import math
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(r"[a-z0-9']+")


def tokenize(text: str) -> list[str]:
    """Normalize text into lowercase word tokens."""
    return TOKEN_RE.findall(text.lower())


@dataclass(frozen=True)
class Prediction:
    intent: str
    confidence: float
    probabilities: dict[str, float]


class IntentChatbot:
    """Train, save, load, and query a simple intent-classification chatbot."""

    def __init__(self, threshold: float = 0.25, seed: int = 7) -> None:
        self.threshold = threshold
        self.random = random.Random(seed)
        self.intent_documents: Counter[str] = Counter()
        self.token_counts: dict[str, Counter[str]] = defaultdict(Counter)
        self.total_tokens: Counter[str] = Counter()
        self.responses: dict[str, list[str]] = {}
        self.vocabulary: set[str] = set()
        self.document_count = 0

    @property
    def trained(self) -> bool:
        return self.document_count > 0 and bool(self.responses)

    def train(self, dataset: dict[str, Any]) -> dict[str, int]:
        """Fit the model from an intents JSON object."""
        self.intent_documents.clear()
        self.token_counts.clear()
        self.total_tokens.clear()
        self.responses.clear()
        self.vocabulary.clear()
        self.document_count = 0

        intents = dataset.get("intents", [])
        if not intents:
            raise ValueError("Training data must contain at least one intent")

        for item in intents:
            tag = str(item["tag"])
            patterns = item.get("patterns", [])
            responses = item.get("responses", [])
            if not patterns or not responses:
                raise ValueError(f"Intent '{tag}' needs patterns and responses")
            self.responses[tag] = [str(response) for response in responses]
            for pattern in patterns:
                tokens = tokenize(str(pattern))
                if not tokens:
                    continue
                self.document_count += 1
                self.intent_documents[tag] += 1
                self.token_counts[tag].update(tokens)
                self.total_tokens[tag] += len(tokens)
                self.vocabulary.update(tokens)

        if self.document_count == 0:
            raise ValueError("Training patterns did not contain any words")
        return {
            "documents": self.document_count,
            "intents": len(self.responses),
            "vocabulary": len(self.vocabulary),
        }

    def predict(self, message: str) -> Prediction:
        """Return the most likely intent and normalized probability scores."""
        if not self.trained:
            raise RuntimeError("The chatbot must be trained before prediction")
        tokens = tokenize(message)
        if not tokens:
            return Prediction("fallback", 0.0, {})

        vocab_size = max(1, len(self.vocabulary))
        intent_count = len(self.responses)
        scores: dict[str, float] = {}
        for intent in self.responses:
            prior = (self.intent_documents[intent] + 1) / (
                self.document_count + intent_count
            )
            score = math.log(prior)
            denominator = self.total_tokens[intent] + vocab_size
            for token in tokens:
                likelihood = (self.token_counts[intent][token] + 1) / denominator
                score += math.log(likelihood)
            scores[intent] = score

        highest = max(scores.values())
        exponentials = {name: math.exp(score - highest) for name, score in scores.items()}
        normalizer = sum(exponentials.values())
        probabilities = {
            name: value / normalizer for name, value in exponentials.items()
        }
        intent = max(probabilities, key=probabilities.get)
        confidence = probabilities[intent]
        if confidence < self.threshold:
            intent = "fallback"
        return Prediction(intent, confidence, probabilities)

    def reply(self, message: str) -> tuple[str, Prediction]:
        prediction = self.predict(message)
        if prediction.intent == "fallback":
            response = (
                "I am not confident about that yet. Try asking about Python, "
                "AI training, what I can do, or add examples to data/intents.json."
            )
        else:
            response = self.random.choice(self.responses[prediction.intent])
        return response, prediction

    def save(self, path: str | Path) -> None:
        if not self.trained:
            raise RuntimeError("Cannot save an untrained chatbot")
        data = {
            "threshold": self.threshold,
            "document_count": self.document_count,
            "intent_documents": dict(self.intent_documents),
            "token_counts": {key: dict(value) for key, value in self.token_counts.items()},
            "total_tokens": dict(self.total_tokens),
            "responses": self.responses,
            "vocabulary": sorted(self.vocabulary),
        }
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "IntentChatbot":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        bot = cls(threshold=float(data["threshold"]))
        bot.document_count = int(data["document_count"])
        bot.intent_documents.update(data["intent_documents"])
        for intent, counts in data["token_counts"].items():
            bot.token_counts[intent].update(counts)
        bot.total_tokens.update(data["total_tokens"])
        bot.responses = data["responses"]
        bot.vocabulary = set(data["vocabulary"])
        return bot
