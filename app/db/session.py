from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

sqlite_path = settings.sqlite_path.removeprefix("./")
database_url = f"sqlite+aiosqlite:///{sqlite_path}"

engine = create_async_engine(database_url, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
