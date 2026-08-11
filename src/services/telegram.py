__all__ = ['run']

import asyncio
import logging

import aiogram
import config
import modules.telegram.handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run():
    if not config.TELEGRAM_TOKEN:
        logger.error('TELEGRAM_TOKEN did not found')
        return

    dp = aiogram.Dispatcher()

    dp.include_router(modules.telegram.handlers.router)

    logger.info('Starting Telegram bot...')
    await dp.start_polling(config.bot)


if __name__ == '__main__':
    asyncio.run(run())
