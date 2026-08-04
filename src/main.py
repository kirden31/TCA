import asyncio
import logging
import argparse
from datetime import datetime

from services.telegram import run as telegram_run
from services.parser import run as parser_run
from services.qdrant import run as qdrant_run

logger = logging.getLogger(__name__)


def run_parser(dt):
    asyncio.run(parser_run(dt))


def run_telegram_bot():
    asyncio.run(telegram_run())


def main(dt):
    try:
        qdrant_ok = asyncio.run(qdrant_run())
        if not qdrant_ok:
            logger.error('Qdrant failed to start')
            return

        run_parser(dt)
        run_telegram_bot()

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

    main(args.download_from_datetime)
