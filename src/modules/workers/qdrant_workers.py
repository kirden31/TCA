import asyncio
import logging

import config

logger = logging.getLogger(__name__)


async def flush(batch, retries=3):
    for attempt in range(retries):
        try:
            await config.qdrant_client.upsert(
                collection_name=config.COLLECTION,
                points=batch,
                wait=True,
            )
            return True

        except Exception as e:
            logger.error(f'Error upserting message to Qdrant: {e}')

            await asyncio.sleep(2**attempt)

    return False


async def run():
    batch = []

    while True:
        try:
            point = await asyncio.wait_for(
                config.message_queue.get(),
                timeout=config.BATCH_TIMEOUT,
            )

            batch.append(point)

            if len(batch) >= config.BATCH_SIZE:
                await flush(batch)

                for _ in batch:
                    config.message_queue.task_done()

                batch.clear()

        except asyncio.TimeoutError:
            if batch:
                await flush(batch)

                for _ in batch:
                    config.message_queue.task_done()

                batch.clear()
