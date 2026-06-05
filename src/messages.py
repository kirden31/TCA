import asyncio

from qdrant_client.models import PointStruct

import config


async def process_batch(batch):
    texts = []
    valid_messages = []

    for msg in batch:
        text = msg.text
        if not text:
            continue
        texts.append(text)
        valid_messages.append(msg)

    if not valid_messages:
        return

    embeddings = await asyncio.to_thread(config.embedder.encode, texts)

    points = []
    for msg, emb, text in zip(valid_messages, embeddings, texts):
        sender = await msg.get_sender()
        point = PointStruct(
            id=int(f"{msg.chat.id}{msg.id}"),
            vector=emb.tolist(),
            payload={
                "text": text,
                "chat_id": str(msg.chat.id),
                "message_id": msg.id,
                "date": msg.date.isoformat(),
                "from_id": sender.id,
                "from_username": sender.username,
            },
        )
        points.append(point)
        print(f'{msg.date}: queued {text[:50]}...')

    await asyncio.to_thread(config.qdrant.upsert, config.COLLECTION, points=points)


async def save_history(chat_id, limit):
    count = 0

    async for msg in config.client.iter_messages(chat_id, limit=limit):
        if msg and msg.text:
            await config.message_queue.put(msg)
            count += 1

    return count
