from langchain_google_genai import ChatGoogleGenerativeAI

from app.config.settings import settings


llm = ChatGoogleGenerativeAI(
    model=settings.LLM_MODEL,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0,
)