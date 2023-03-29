from loguru import logger

from sqlalchemy.exc import SQLAlchemyError

from database.base import get_session_db
from database.models import User


async def register_user(group_id: int, *, user_id: int) -> bool:
    """Register user in database"""
    session = await get_session_db()

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
