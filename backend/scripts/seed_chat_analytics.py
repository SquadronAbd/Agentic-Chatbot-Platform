import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

import asyncio
import random
from datetime import datetime, timedelta, timezone

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password

from app.models.users import User
from app.models.conversations import Conversation
from app.models.messages import Message


ROLES = [
    "admin",
    "manager",
    "agent",
    "agent",
    "agent",
    "agent",
    "viewer",
    "viewer",
    "viewer",
    "viewer",
]


USER_NAMES = [
    "Admin User",
    "Manager User",
    "Agent One",
    "Agent Two",
    "Agent Three",
    "Agent Four",
    "Viewer One",
    "Viewer Two",
    "Viewer Three",
    "Viewer Four",
]


QUESTIONS = [
    "What is LangGraph?",
    "Explain FastAPI.",
    "How does JWT work?",
    "Tell me about PostgreSQL.",
    "Explain Airflow.",
    "How does Redis work?",
    "What are embeddings?",
    "What is RAG?",
]


ANSWERS = [
    "LangGraph manages agent workflows.",
    "FastAPI is a Python backend framework.",
    "JWT is used for authentication.",
    "PostgreSQL stores relational data.",
    "Airflow schedules ETL pipelines.",
    "Redis stores temporary data in memory.",
    "Embeddings convert text into vectors.",
    "RAG combines retrieval with LLM generation.",
]


async def seed():

    async with AsyncSessionLocal() as session:

        users = []

        print("Creating users...")

        for i in range(10):

            user = User(
                email=f"user{i+1}@chatbot.com",
                hashed_password=hash_password("Password123!"),
                full_name=USER_NAMES[i],
                role=ROLES[i],
                is_active=True,
            )

            session.add(user)
            users.append(user)

        await session.commit()

        # refresh IDs

        for u in users:
            await session.refresh(u)

        print("Users created.")

        conversations = []

        print("Creating conversations...")

        for user in users:

            for j in range(2):

                conv = Conversation(
                    user_id=user.id,
                    title=f"{user.full_name} Conversation {j+1}",
                )

                session.add(conv)
                conversations.append(conv)

        await session.commit()

        for c in conversations:
            await session.refresh(c)

        print("Conversations created.")

        print("Creating messages...")

        for conv in conversations:

            for i in range(8):

                created_time = datetime.now(timezone.utc) - timedelta(
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                )

                user_msg = Message(
                    conversation_id=conv.id,
                    role="user",
                    content=random.choice(QUESTIONS),
                    tokens=str(random.randint(30, 120)),
                    created_at=created_time,
                )

                assistant_msg = Message(
                    conversation_id=conv.id,
                    role="assistant",
                    content=random.choice(ANSWERS),
                    tokens=str(random.randint(120, 450)),
                    created_at=created_time + timedelta(seconds=3),
                )

                session.add(user_msg)
                session.add(assistant_msg)

        await session.commit()

        print("Messages created.")

        print("------------------------------------")
        print("Seed completed successfully")
        print(f"Users          : {len(users)}")
        print(f"Conversations  : {len(conversations)}")
        print(f"Messages       : {len(conversations)*16}")
        print("------------------------------------")


if __name__ == "__main__":
    asyncio.run(seed())