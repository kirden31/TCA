import asyncio
import aioconsole
import logging

from modules.ai import search

logger = logging.getLogger(__name__)


async def run():
    try:
        logger.info('AI module started (for DB questions)')
        logger.info('Enter your question:')

        while True:
            try:
                question = await aioconsole.ainput('\nQuestion ("CLOSE AI APP" to exit): ')
                question = question.strip()

                if not question:
                    continue

                if question == 'CLOSE AI APP':
                    return

                logger.info('Searching database...')
                answer = await search.search(question)

                if answer:
                    logger.info(f'Answer: {answer}')
                else:
                    logger.warning('No answer found.')
            except Exception as e:
                logger.error(f'Error processing question: {e}')
    except asyncio.CancelledError:
        logging.info('Closing AI module')
        raise


if __name__ == '__main__':
    asyncio.run(run())
