import os

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.base import get_sqlalchemy_url, Base


@pytest_asyncio.fixture
async def get_sessionmaker():
    os.environ['DB_HOST'] = '127.0.0.1'
    os.environ['DB_NAME'] = 'schedule_bot_test_db'
    os.environ['DB_USER'] = 'vlad_mysql'
    os.environ['DB_PASS'] = ''
    os.environ['LOGURU_LEVEL'] = 'WARNING'

    engine = create_async_engine(
        get_sqlalchemy_url(),
        future=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_sessionmaker = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    return async_sessionmaker