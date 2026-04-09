from dotenv import load_dotenv
from pydantic_ai import Agent

from constants import MODEL_SMALL
from data_models import ChatRequest, ChatResponse

load_dotenv()

chat_agent = Agent(
    MODEL_SMALL,
    system_prompt=(
        "You are a funny programming bot named Ro Båt. "
        "Always answer with a programming joke. "
        "Keep it short, fun, and include emojis."
    ),
)


async def chat(request: ChatRequest) -> ChatResponse:
    result = await chat_agent.run(
        request.question,
        message_history=request.message_history,
    )

    return ChatResponse(
        response=result.output,
        message_history=result.all_messages(),
    )