from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

import config
from modules import utils
from modules.ai import prompts
import logging

logger = logging.getLogger(__name__)

client = AsyncOpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)


def embed_text(text: str):
    return config.embedder.encode([text], normalize_embeddings=True).tolist()[0]


def format_context(results) -> str:
    chunks = []
    for p in results:
        payload = p.payload or {}
        text = payload.get('text', '')
        chat_id = payload.get('chat_id', '')
        date = payload.get('date', '')
        username = payload.get('from_username', '')
        if text:
            meta = f'[chat={chat_id} date={date} user={username}]'
            chunks.append(f'{meta}\n{text}')
    return '\n\n---\n\n'.join(chunks)


async def llm_answer(question: str, context: str) -> str:
    content = f'Вопрос: {question}\n\nКонтекст:\n{context}'
    return await llm_request(prompts.LLM_ANSWER_PROMPT, content)


async def llm_question(question: str) -> str:
    logger.info('Генерирую запрос...')
    q = await llm_request(prompts.LLM_QUESTION_PROMPT, question)
    logger.debug(f'Запрос: {q}')
    return q


async def llm_request(system_content: str, content: str) -> str:
    messages = [
        ChatCompletionSystemMessageParam(
            role='system',
            content=system_content,
        ),
        ChatCompletionUserMessageParam(
            role='user',
            content=content,
        ),
    ]
    resp = await client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=messages,
        temperature=0.2,
    )
    return resp.choices[0].message.content or ''


async def search(question: str, limit: int = 50):
    try:
        normalize_question = await llm_question(question)
        vec = await utils.embed_text(normalize_question)

        results = await config.qdrant_client.search(
            collection_name=config.COLLECTION,
            query_vector=vec,
            limit=limit,
        )

        context = format_context(results)
        answer = await llm_answer(question, context)

        return answer
    except Exception as e:
        logger.error(f'Ошибка при поиске: {e}')
        return None
