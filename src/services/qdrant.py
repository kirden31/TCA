import config
import logging
from modules.qdrant.qdrant_server import get_qdrant_server
from qdrant_client import AsyncQdrantClient, models
import asyncio

logger = logging.getLogger(__name__)


async def run():
    logger.info('Starting Qdrant server...')
    server = get_qdrant_server()
    success = server.start(timeout=30)

    if not success:
        return False

    config.qdrant_client = AsyncQdrantClient(url=config.qdrant_url)

    try:
        await config.qdrant_client.get_collection(collection_name=config.COLLECTION)
    except Exception:
        logger.info(f'Creating collection {config.COLLECTION}...')
        await config.qdrant_client.create_collection(
            collection_name=config.COLLECTION,
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        )
        logger.info(f'Creating index for field "date" in collection {config.COLLECTION}...')
        await config.qdrant_client.create_payload_index(
            collection_name=config.COLLECTION, field_name='date', field_schema='datetime'
        )

    return True


if __name__ == '__main__':
    asyncio.run(run())
