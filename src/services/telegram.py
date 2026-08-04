import logging
import asyncio
from aiogram import Dispatcher

import config
from modules.telegram.handlers import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run():
    if not config.TELEGRAM_TOKEN:
        logger.error('Ошибка: TELEGRAM_TOKEN не найден в переменных окружения!')
        return

    dp = Dispatcher()

    dp.include_router(router)

    logger.info('Запуск Telegram бота...')
    await dp.start_polling(config.bot)


if __name__ == '__main__':
    asyncio.run(run())
