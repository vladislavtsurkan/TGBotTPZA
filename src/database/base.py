from typing import TypeAlias

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from config_loader import load_config_db, DatabaseConfig

sqlalchemy_url: TypeAlias = str


def get_sqlalchemy_url() -> sqlalchemy_url:
    """Get SQLAlchemy URL for work with database from config"""
    config_db: DatabaseConfig = load_config_db()
    return (
        f'postgresql+asyncpg://{config_db.user}:{config_db.password}@'
        f'{config_db.host}/{config_db.db_name}'
    )


engine = create_async_engine(
    get_sqlalchemy_url(),
    future=True
)

sessionmaker_async = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


class Base(DeclarativeBase):
    pass


async def get_session_db() -> AsyncSession:
    async with sessionmaker_async() as session:
        try:
            yield session
        finally:
            session.close()
