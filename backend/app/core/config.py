from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str = ""
    REDIS_URL: str = ""
    JWT_SECRET_KEY: str = "temp-secret-change-later"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config:
        env_file = ".env"    
    
settings = Settings()