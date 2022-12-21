from loguru import logger

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from database.models import User


async def register_user(db_session: sessionmaker, group_id: int, *, user_id: int) -> bool:
    """Register user in database"""
    async with db_session() as session:
        try:
            await session.merge(
                User(id=user_id, group_id=group_id, is_admin=False)
            )
            await session.commit()
        except SQLAlchemyError:
            logger.exception('Failed try save new User in database')
            return False
        else:
            return True
