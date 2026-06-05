import asyncio

from openai import AsyncOpenAI
from qdrant_client.http.models import FieldCondition, Filter, MatchAny

import config

client = AsyncOpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)


def embed_text(text: str):
    return config.embedder.encode([text], normalize_embeddings=True).tolist()[0]


def build_chat_filter(chat_ids):
    return Filter(
        must=[
            FieldCondition(
                key="chat_id",
                match=MatchAny(any=[str(cid) for cid in chat_ids]),
            )
        ]
    )


def format_context(results) -> str:
    chunks = []
    for p in results:
        payload = p.payload or {}
        text = payload.get("text", "")
        chat_id = payload.get("chat_id", "")
        date = payload.get("date", "")
        username = payload.get("from_username", "")
        if text:
            meta = f"[chat={chat_id} date={date} user={username}]"
            chunks.append(f"{meta}\n{text}")
    return "\n\n---\n\n".join(chunks)


async def llm_answer(question: str, context: str) -> str:
    resp = await client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": config.LLM_SYSTEM_PROMT,
            },
            {
                "role": "user",
                "content": f"Вопрос: {question}\n\nКонтекст:\n{context}",
            },
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content or ""


async def search(question: str, chat_ids=None, limit: int = 5):
    vec = embed_text(question)

    query_filter = build_chat_filter(chat_ids) if chat_ids else None

    results = await asyncio.to_thread(
        config.qdrant.search,
        collection_name=config.COLLECTION,
        query_vector=vec,
        limit=limit,
        query_filter=query_filter,
    )

    if not results:
        print("Ничего не найдено.")
        return

    context = format_context(results)
    answer = await llm_answer(question, context)

    print("Вопрос:", question)
    print("Ответ:", answer)


if __name__ == "__main__":
    q = input("Введите вопрос: ")
    asyncio.run(search(q))
