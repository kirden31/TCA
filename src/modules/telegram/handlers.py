__all__ = ['cmd_start', 'handle_ai_query']

import logging

import aiogram.filters
import aiogram.utils.chat_action
import config
import modules.ai.search
import modules.telegram.decorators as dec

router = aiogram.Router()

logger = logging.getLogger(__name__)


@router.message(aiogram.filters.CommandStart())
@dec.check_user_id
async def cmd_start(message: aiogram.types.Message):
    await message.answer('Привет! Я ИИ-бот, работающий на базе чатов.\nЗадай мне любой вопрос!')


@router.message()
@dec.check_user_id
async def handle_ai_query(message: aiogram.types.Message):
    if not message.text:
        await message.answer('Отправьте текстовое сообщение.')
        return

    try:
        async with aiogram.utils.chat_action.ChatActionSender.typing(
            bot=config.bot,
            chat_id=message.chat.id,
        ):
            answer = await modules.ai.search.search(message.text)

        await message.answer(answer)

    except Exception as e:
        logger.exception(f'Error sending response: {e}')
        await message.answer('Произошла ошибка. Попробуйте позже и/или сообщите админу.')
