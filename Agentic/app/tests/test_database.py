from sqlalchemy import text

from app.models.database import engine


def test_connection():
    with engine.connect() as connection:
        version = connection.execute(
            text("SELECT version();")
        )

        print("=" * 60)
        print("DATABASE CONNECTED")
        print("=" * 60)
        print(version.scalar())


if __name__ == "__main__":
    test_connection()