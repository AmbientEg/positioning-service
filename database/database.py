from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import DATABASE_URL

# Create engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base model
Base = declarative_base()


# Dependency for FastAPI
async def get_db_session():
    async with AsyncSessionLocal() as session:
        yield session