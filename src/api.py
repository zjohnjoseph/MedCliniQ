from fastapi import FastAPI
from chat_agent import chat
from data_models import ChatRequest, ChatResponse

app = FastAPI()

@app.post("/chat", response_model=ChatResponse)
async def chatbot_chat(request: ChatRequest) -> ChatResponse:
    return await chat(request)