from sqlalchemy import text

from app.models.database import engine


class SQLTool:
    """
    Executes SQL queries.
    """

    def query(self, sql: str):

        with engine.connect() as conn:

            result = conn.execute(text(sql))

            rows = result.fetchall()

            return rows