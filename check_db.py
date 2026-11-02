from sqlalchemy import text
from app.database import engine

with engine.connect() as conn:
    print(conn.execute(text("SELECT email, role FROM users LIMIT 3")).all())