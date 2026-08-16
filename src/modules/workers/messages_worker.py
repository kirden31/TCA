__all__ = ['run']

import asyncio
import logging

import config
from modules.message.messages import add_msgs

logger = logging.getLogger(__name__)


async def run():
    logger.info('Messages worker started')
    batch = []

    while True:
        try:
            point = await asyncio.wait_for(
                config.message_queue_raw.get(),
                timeout=config.BATCH_TIMEOUT,
            )

            batch.append(point)

            if len(batch) >= config.BATCH_SIZE:
                await add_msgs(batch)

                for _ in batch:
                    config.message_queue_raw.task_done()

                batch.clear()

        except asyncio.TimeoutError:
            if batch:
                await add_msgs(batch)

                for _ in batch:
                    config.message_queue_raw.task_done()

                batch.clear()
