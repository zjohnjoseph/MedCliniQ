from dotenv import load_dotenv
from pydantic_ai import Agent

from constants import MODEL_SMALL
from data_models import ChatRequest, ChatResponse

load_dotenv()

chat_agent = Agent(
    MODEL_SMALL,
    system_prompt=(
        "You are Therabot, a friendly and helpful AI chatbot. "
        "Answer user questions clearly and naturally. "
        "Only use very basic emojis occasionally, such as 🙂, 😊, or 👍. "
        "Do not use excessive, flashy, or unusual emojis. "
        "If emojis are not needed, respond without them."
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