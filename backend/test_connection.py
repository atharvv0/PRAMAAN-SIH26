from sqlalchemy import text
from app.db.session import engine

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT current_database();"))
        print("Connected to database:", result.scalar())
except Exception as e:
    print("Database connection failed:")
    print(e)