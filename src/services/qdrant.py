__all__ = ['run']

import asyncio
import logging

import config
from modules.qdrant.qdrant_server import get_qdrant_server
from qdrant_client import AsyncQdrantClient, models

logger = logging.getLogger(__name__)


async def create_payload(field_name, field_schema):
    logger.info(f'Creating index for field "{field_name}" in collection {config.COLLECTION}...')
    await config.qdrant_client.create_payload_index(
        collection_name=config.COLLECTION,
        field_name=field_name,
        field_schema=field_schema,
    )


async def run():
    logger.info('Starting Qdrant server...')
    server = get_qdrant_server()
    success = server.start(timeout=30)

    if not success:
        return False

    config.qdrant_client = AsyncQdrantClient(url=config.QDRANT_URL)

    try:
        await config.qdrant_client.get_collection(collection_name=config.COLLECTION)
    except Exception:
        logger.info(f'Creating collection {config.COLLECTION}...')
        await config.qdrant_client.create_collection(
            collection_name=config.COLLECTION,
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
        )

        await create_payload('date', 'datetime')
        await create_payload('chat_id', 'text')

    return True


if __name__ == '__main__':
    asyncio.run(run())
