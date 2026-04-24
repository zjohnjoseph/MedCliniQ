from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str = Field(description="User's message or question to Chatbot")
    message_history: list[ChatMessage] = Field(default_factory=list)
    conversation_id: str
    user_id: str

class ChatResponse(BaseModel):
    response: str
    message_history: list[ChatMessage]