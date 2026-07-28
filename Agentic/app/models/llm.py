from langchain_groq import ChatGroq

from app.config.settings import settings

if not settings.GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set. Add it to Agentic/.env.")

llm = ChatGroq(
    model=settings.LLM_MODEL,
    groq_api_key=settings.GROQ_API_KEY,
    temperature=0,
)
