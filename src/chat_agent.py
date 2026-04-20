from dotenv import load_dotenv
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

from constants import MODEL_NAME, MAX_NEW_TOKENS, TEMPERATURE, TOP_P
from data_models import ChatRequest, ChatResponse, ChatMessage

load_dotenv()

SYSTEM_PROMPT = (
    "You are Chatbot, a friendly and helpful AI chatbot. "
    "Answer user questions clearly and naturally. "
    "Only use very basic emojis occasionally, such as 🙂, 😊, or 👍. "
    "Do not use excessive, flashy, or unusual emojis. "
    "If emojis are not needed, respond without them."
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    dtype=torch.bfloat16
)


async def chat(request: ChatRequest) -> ChatResponse:
    messages = []

    for i, msg in enumerate(request.message_history):
        role = "model" if msg.role == "assistant" else "user"
        messages.append({"role": role, "content": msg.content})

    user_input = request.question

    if not request.message_history:
        user_input = f"{SYSTEM_PROMPT}\n\nUser: {request.question}"

    messages.append({"role": "user", "content": user_input})

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            do_sample=True
        )

    generated_tokens = outputs[0][inputs["input_ids"].shape[1]:]
    response_text = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

    updated_history = request.message_history + [
        ChatMessage(role="user", content=request.question),
        ChatMessage(role="assistant", content=response_text),
    ]

    return ChatResponse(
        response=response_text,
        message_history=updated_history
    )