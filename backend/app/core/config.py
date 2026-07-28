from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:apppass@localhost:5432/chatbot_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET_KEY: str = "temp-secret-change-later"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    INTERNAL_API_KEY: str = "change-me-internal-key"
    AGENTIC_SERVICE_URL: str = "http://localhost:8001"

    class Config:
        env_file = ".env"    
    
settings = Settings()