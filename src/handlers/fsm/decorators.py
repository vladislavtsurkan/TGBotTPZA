from aiogram import types

from services.utils import is_registered_user, is_user_admin
from handlers.fsm.registration import start_registration


class check_user_is_registered:
    """Check if user is registered (decorator)"""
    def __init__(
            self, func: callable = None, _initialized: bool = False, allow_function: bool = False
    ) -> None:
        self.func = func
        self.allow_function = allow_function
        self._initialized = _initialized

    def __call__(self, *args, **kwargs):
        if not self._initialized:
            if not self.func:
                # Decorator was initialized with arguments
                return self.__class__(args[0], allow_function=self.allow_function)
            return self.__class__(
                self.func,
                _initialized=True,
                allow_function=self.allow_function
            )(*args, **kwargs)

        async def wrapper(message: types.Message):
            if await is_registered_user(message):
                return await self.func(message)
            else:
                result = None
                if self.allow_function:
                    result = await self.func(message)
                await start_registration(message)
                return result

        return wrapper(args[0])


def check_user_is_admin(func: callable):
    """Check if user is admin (decorator)"""
    async def wrapper(msg: types.Message):
        if await is_user_admin(msg):
            return await func(msg)

    return wrapper
