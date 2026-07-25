from sqlalchemy import text

from app.models.database import engine


def create_table():
    sql = """
    CREATE EXTENSION IF NOT EXISTS vector;

    CREATE TABLE IF NOT EXISTS documents (

        id SERIAL PRIMARY KEY,

        document TEXT,

        metadata JSONB,

        embedding vector(3072)

    );
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    print("=" * 60)
    print("Vector table created successfully.")
    print("=" * 60)


if __name__ == "__main__":
    create_table()