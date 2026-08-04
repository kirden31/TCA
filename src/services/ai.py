import asyncio
import aioconsole
import logging

from modules.ai import search

logger = logging.getLogger(__name__)


async def run():
    try:
        print('Модуль с ИИ запущен (для вопросов по БД)')
        print('Введите ваш вопрос:')

        while True:
            try:
                question = await aioconsole.ainput('\nВопрос ("CLOSE AI APP" для выхода): ')
                question = question.strip()

                if not question:
                    continue

                if question == 'CLOSE AI APP':
                    return

                print('[ai] Поиск по базе...')
                answer = await search.search(question)

                if answer:
                    print(f'[ai] Ответ: {answer}')
                else:
                    print('[ai] Не удалось найти ответ.')
            except Exception as e:
                print(f'[ai] Ошибка при обработке вопроса: {e}')
    except asyncio.CancelledError:
        logging.info('Закрытие модуля ИИ')
        raise


if __name__ == '__main__':
    asyncio.run(run())
