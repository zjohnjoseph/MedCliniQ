from pydantic import BaseModel, Field
from pydantic_ai import ModelMessage


class ChatRequest(BaseModel):
    question: str = Field(description="User's message or question to Chatbot")
    message_history: list[ModelMessage] = Field(default_factory=list)

    model_config = {
        "json_schema_extra": {
            "example": {"question": "How to improve mental health"}
        }
    }


class ChatResponse(BaseModel):
    response: str = Field(
        description="Chatbot's response including a detailed response to the user's question."
    )
    message_history: list[ModelMessage]