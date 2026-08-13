__all__ = ['main']

import argparse
import asyncio
from datetime import datetime
import logging

import config
from services.parser import run as parser_run
from services.qdrant import run as qdrant_run
from services.telegram import run as telegram_run

logger = logging.getLogger(__name__)


async def main(dt):
    try:
        qdrant_ok = await qdrant_run()
        if not qdrant_ok:
            logger.error('Qdrant failed to start')
            return

        config.get_embedder()

        await asyncio.gather(
            parser_run(dt),
            telegram_run(),
        )

    except asyncio.CancelledError:
        logger.info('Application finished')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chat Analyzer')
    parser.add_argument(
        '-dfdt',
        '--download_from_datetime',
        type=lambda s: datetime.strptime(s, '%Y-%m-%dT%H:%M:%S'),
        help='Дата по которую скачать сообщения. ФОРМАТ: yyyy-mm-ddThh:mm:ss',
    )
    args = parser.parse_args()

    asyncio.run(main(args.download_from_datetime))
