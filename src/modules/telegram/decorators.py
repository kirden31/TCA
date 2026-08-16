__all__ = ['check_user_id']

import functools

import aiogram
import config


def check_user_id(func):
    @functools.wraps(func)
    async def wrapper(message: aiogram.types.Message, *args, **kwargs):
        if message.from_user:
            if str(message.from_user.id) not in config.ALLOWED_USERS:
                await message.answer('У вас нет доступа.')
                return False

            return await func(message, *args, **kwargs)

        return False

    return wrapper
