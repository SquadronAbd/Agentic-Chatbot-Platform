from app.config.settings import settings


def _build_llm():
    if settings.GROQ_API_KEY:
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=settings.LLM_MODEL,
            groq_api_key=settings.GROQ_API_KEY,
            temperature=0,
        )
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0,
    )


llm = _build_llm()
