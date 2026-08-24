__all__ = ['process_question', 'get_next_question', 'run']

import asyncio
import logging

import aioconsole
import config
from modules.ai import search

logger = logging.getLogger(__name__)


async def process_question(question):
    try:
        answer = await search.search(question)

        if answer:
            logger.info(f'Answer: {answer}')
        else:
            logger.warning('No answer found.')
    except Exception as e:
        logger.exception(f'Error processing question: {e}')


async def get_next_question():
    while True:
        try:
            question = await aioconsole.ainput('\nQuestion ("CLOSE AI APP" to exit): ')
            question = question.strip()

            if not question:
                continue

            if question == 'CLOSE AI APP':
                return None

            await process_question(question)
        except Exception as e:
            logger.exception(f'Error processing question: {e}')
            return None


async def run():
    try:
        config.get_embedder()

        logger.info('AI module started (for DB questions)')

        while True:
            question = await get_next_question()
            if question is None:
                break
    except asyncio.CancelledError:
        logging.info('Closing AI module')
        raise


if __name__ == '__main__':
    asyncio.run(run())
