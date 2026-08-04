from app.config.settings import settings

_model_name = settings.LLM_MODEL or "gemini-2.0-flash"

if settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY:
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model=_model_name,
        google_api_key=settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY,
        temperature=0,
        max_output_tokens=2048,
    ).with_retry(stop_after_attempt=3, wait_exponential_jitter=True)
elif settings.GROQ_API_KEY:
    from langchain_groq import ChatGroq

    llm = ChatGroq(
        model=_model_name if settings.LLM_MODEL else "llama-3.3-70b-versatile",
        groq_api_key=settings.GROQ_API_KEY,
        temperature=0,
        max_tokens=2048,
    ).with_retry(stop_after_attempt=3, wait_exponential_jitter=True)
else:
    raise RuntimeError("Set GEMINI_API_KEY/GOOGLE_API_KEY or GROQ_API_KEY in Agentic/.env.")
