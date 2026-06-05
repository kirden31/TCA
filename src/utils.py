import asyncio

import config
import messages


async def collect_batch():
    batch = []

    first = await config.message_queue.get()
    batch.append(first)

    loop = asyncio.get_running_loop()
    start = loop.time()

    while len(batch) < config.BATCH_SIZE:
        elapsed = loop.time() - start
        remaining = config.BATCH_TIMEOUT - elapsed

        if remaining <= 0:
            break

        try:
            msg = await asyncio.wait_for(config.message_queue.get(), timeout=remaining)
            batch.append(msg)
        except asyncio.TimeoutError:
            break

    return batch


async def batch_worker():
    while True:
        batch = await collect_batch()
        try:
            await messages.process_batch(batch)
        except Exception as e:
            print(f"Batch worker error: {e}")
        finally:
            for _ in batch:
                config.message_queue.task_done()