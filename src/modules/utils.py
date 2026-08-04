import asyncio

import config

embed_sem = asyncio.Semaphore(5)


async def embed_texts(texts: list[str]):
    async with embed_sem:
        return await asyncio.to_thread(
            config.embedder.encode,
            texts,
            normalize_embeddings=True,
        )


async def embed_text(text: str):
    return (await embed_texts([text]))[0]


async def put(msgs: list, queue: asyncio.Queue):
    for msg in msgs:
        await queue.put(msg)
