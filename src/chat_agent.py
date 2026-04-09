from pydantic_ai import Agent
from constants import MODEL_SMALL
from dotenv import load_dotenv
from data_models import ChatResponse, ChatRequest

load_dotenv()

chat_agent = Agent(
    MODEL_SMALL,
    system_prompt="Be a joking programming nerd, always answer with a programming joke. Also add in some emojis to make it funnier.",
)


async def chat(request: ChatRequest):
    result = await chat_agent.run(
        request.question, message_history=request.message_history
    )

    return ChatResponse(response=result.output, message_history=result.all_messages())
