# app/database/db.py
# import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# DATABASE_URL = os.getenv(
#     "DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/botdb"
# )

DATABASE_URL = "sqlite+aiosqlite:///db.sqlite3"

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
