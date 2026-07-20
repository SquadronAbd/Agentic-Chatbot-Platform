from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# Async engine needs the "+asyncpg" dialect in the URL, e.g.:
# postgresql+asyncpg://postgres:apppass@localhost:5432/chatbot_db
engine = create_async_engine(settings.DB_URL, pool_pre_ping=True, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()