"""FastAPI application for the locally trained chatbot."""

from pathlib import Path
from threading import Lock

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from chatbot import IntentChatbot
from train import DATA_PATH, MODEL_PATH, train_model


ROOT = Path(__file__).resolve().parent
WEB_DIR = ROOT / "web"
model_lock = Lock()


def load_current_model() -> IntentChatbot:
    if not MODEL_PATH.exists() or MODEL_PATH.stat().st_mtime < DATA_PATH.stat().st_mtime:
        train_model()
    return IntentChatbot.load(MODEL_PATH)


bot = load_current_model()
app = FastAPI(
    title="Nova Trainable Chatbot",
    description="A beginner-friendly local intent chatbot built with Python.",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    reply: str
    intent: str
    confidence: float


@app.get("/api/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "trained": bot.trained,
        "intents": len(bot.responses),
        "examples": bot.document_count,
    }


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be blank")
    with model_lock:
        reply, prediction = bot.reply(message)
    return ChatResponse(
        reply=reply,
        intent=prediction.intent,
        confidence=round(prediction.confidence, 4),
    )


@app.post("/api/train")
def retrain() -> dict[str, object]:
    global bot
    with model_lock:
        metrics = train_model()
        bot = IntentChatbot.load(MODEL_PATH)
    return {"status": "trained", **metrics}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")
