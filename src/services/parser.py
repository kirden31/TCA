import argparse
import asyncio
import logging
from datetime import datetime

import config

logger = logging.getLogger(__name__)
from modules.message import bot
import modules.workers.qdrant_workers
import modules.workers.messages_worker


async def run(dt=None):
    try:
        if not config.client.is_connected():
            await config.client.start()

        logger.info('Activating passive parser...')

        async with asyncio.TaskGroup() as tg:
            tg.create_task(modules.workers.qdrant_workers.run())
            tg.create_task(modules.workers.messages_worker.run())

            if dt:
                result = await bot.download_history(dt)
                logger.debug(f'History download result: {result}')

            await config.client.run_until_disconnected()

    except asyncio.CancelledError:
        logger.info('Parser work finished')
        await config.client.disconnect()
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chat Analyzer')
    parser.add_argument(
        '-dfdt',
        '--download_from_datetime',
        type=lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%S'),
        help='Дата по которую скачать сообщения. ФОРМАТ: yyyy-mm-ddThh:mm:ss',
    )
    args = parser.parse_args()

    asyncio.run(run(args.download_from_datetime))
