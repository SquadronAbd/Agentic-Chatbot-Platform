from app.tools.sql_tool import SQLTool

tool = SQLTool()

rows = tool.query(
    "SELECT COUNT(*) FROM langchain_pg_embedding"
)

print(rows)