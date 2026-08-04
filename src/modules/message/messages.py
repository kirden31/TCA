from uuid import uuid4

from qdrant_client.models import PointStruct

import config
import logging

logger = logging.getLogger(__name__)
import modules.utils


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
                    'from_id': sender.id,
                    'from_username': sender.username,
                },
            )
            points.append(point)

    try:
        await modules.utils.put(points, config.message_queue)
    except Exception as e:
        logger.error(f'Failed to add batch of messages to queue: {e}')
