__all__ = ['run']

import asyncio
import logging

from aiogram import Dispatcher
import config
from modules.telegram.handlers import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run():
    if not config.TELEGRAM_TOKEN:
        logger.error('TELEGRAM_TOKEN did not found')
        return

    dp = Dispatcher()

    dp.include_router(router)

    logger.info('Starting Telegram bot...')
    await dp.start_polling(config.bot)


if __name__ == '__main__':
    asyncio.run(run())
