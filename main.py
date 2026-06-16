
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import ChatRequest
from chatbot_engine import ChatbotEngine


app = FastAPI(
    title="SwiftIntelli Chatbot API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

bot = ChatbotEngine()


@app.get("/")
def home():

    return {
        "status": "running",
        "project": "SwiftIntelli Chatbot",
        "version": "1.0.0"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    result = bot.process(
        session_id=request.session_id,
        question=request.message,
        user_id=request.user_id
    )

    return result


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }