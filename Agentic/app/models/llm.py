from langchain_groq import ChatGroq

from app.config.settings import settings

if not settings.GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set. Add it to Agentic/.env.")

# max_tokens: prevents runaway responses and controls Groq token spend.
# with_retry: 3 attempts with exponential back-off handles transient
#             rate-limit (429) and server errors (5xx) from the Groq API.
llm = ChatGroq(
    model=settings.LLM_MODEL,
    groq_api_key=settings.GROQ_API_KEY,
    temperature=0,
    max_tokens=2048,
).with_retry(stop_after_attempt=3, wait_exponential_jitter=True)
