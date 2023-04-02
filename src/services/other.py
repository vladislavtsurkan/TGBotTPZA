from loguru import logger

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


async def register_user(group_id: int, *, user_id: int, session: AsyncSession) -> bool:
    """Register user in database"""
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
