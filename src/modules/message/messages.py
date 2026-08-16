__all__ = ['add_msgs']

import logging
from uuid import uuid4

import config
import modules.utils
from qdrant_client.models import PointStruct

logger = logging.getLogger(__name__)


async def add_msgs(msgs):
    texts = [msg.text for msg in msgs if msg.text]
    if not texts:
        return

    embeddings = await modules.utils.embed_texts(texts)
    points = []
    for i, msg in enumerate(msgs):
        if msg.text:
            sender = await msg.get_sender()
            point = PointStruct(
                id=str(uuid4()),
                vector=embeddings[i].tolist(),
                payload={
                    'text': msg.text,
                    'chat_id': str(msg.chat.id),
                    'message_id': msg.id,
                    'date': msg.date.isoformat(),
                    'from_id': getattr(sender, 'id', None),
                    'from_username': getattr(sender, 'username', None),
                },
            )
            points.append(point)

    try:
        await modules.utils.put(points, config.message_queue)
    except Exception as e:
        logger.error(f'Failed to add batch of messages to queue: {e}')
