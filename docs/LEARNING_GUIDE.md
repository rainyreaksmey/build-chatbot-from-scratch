# Build and train a Python chatbot: complete learning guide

## What you built

Nova has four layers:

- **Training data:** example phrases grouped by intent in JSON.
- **Machine-learning engine:** a Naive Bayes classifier written with the Python
  standard library.
- **API:** FastAPI validates messages and returns structured predictions.
- **Interface:** HTML, CSS, and JavaScript provide a responsive chat experience.

This architecture is deliberately small. You can inspect every calculation,
retrain in a fraction of a second, and learn the full lifecycle before using a
large model.

## Training data

An intent describes what a user is trying to accomplish. The `greeting` intent,
for example, contains several ways a person might greet the bot. Its responses
are possible answers.

Good patterns are:

- varied rather than repeated with one word changed;
- realistic messages your users would actually write;
- clearly associated with one intent;
- balanced so one intent does not dominate the dataset.

Keep test phrases separate from the training examples. Otherwise you measure
memorization instead of the ability to generalize.

## Tokenization and word counts

The function `tokenize()` lowercases the text and extracts words. During
training, the engine records:

- how many example documents belong to each intent;
- how many times each token appears in each intent;
- the total number of tokens in each intent;
- the complete vocabulary.

For every intent `c` and message tokens `x`, prediction estimates:

```text
score(c) = log P(c) + sum(log P(token | c))
```

Adding logarithms is numerically safer than multiplying many tiny
probabilities. Laplace smoothing adds one to the token counts so an unseen word
does not force a probability to zero.

## Confidence and fallback

Raw log scores are transformed into normalized probabilities with a stable
softmax calculation. If the best probability is below the configured
threshold, the bot returns a fallback response.

Confidence is not the same as correctness. Evaluate the model on real held-out
messages before using it for important decisions.

## Improving accuracy

Use this loop:

1. Collect messages the bot answered incorrectly.
2. Label each one with the correct intent.
3. Add genuinely different examples—not dozens of duplicates.
4. Retrain the model.
5. Run automated tests and a separate evaluation set.
6. Compare the new results with the previous model.

If two intents repeatedly conflict, redefine them so their purposes are more
distinct or combine them.

## Security and production checklist

Before deploying publicly:

- protect or remove `/api/train`;
- add authentication and request-rate limits;
- restrict allowed origins if the frontend is hosted separately;
- avoid logging private user messages without consent;
- cap request sizes and set server timeouts;
- run behind HTTPS;
- add monitoring and a human support path;
- explain that the bot can be wrong.

Never use this simple model for medical, legal, financial, or safety-critical
decisions.

## Moving toward an LLM chatbot

A language model generates new text, while Nova selects responses associated
with predicted intents. An effective next step is usually RAG:

1. Break trusted documents into small chunks.
2. Create embeddings for those chunks.
3. Retrieve the most relevant chunks for a question.
4. Give the question and retrieved evidence to a language model.
5. Return an answer with citations.

This is far more practical than training a frontier model from scratch. Large
models require vast datasets, specialized hardware, extensive evaluation, and
significant engineering and safety work.

## Exercises

1. Add an `opening_hours` intent and test three unseen phrases.
2. Change the confidence threshold and observe when fallback is selected.
3. Create a CSV evaluation set with expected intents and calculate accuracy.
4. Store conversations in SQLite.
5. Require an admin token for `/api/train`.
6. Add a retrieval layer that answers from your own documentation.

## Video walkthrough

The `docs/video/` folder contains a Remotion-ready source composition and a
storyboard. It explains the flow from training examples to the browser reply.
Use the render command documented there to create an MP4.
