__all__ = ['cmd_start', 'handle_ai_query']

from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.utils.chat_action import ChatActionSender
import config
from modules.ai import search

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer('Привет! Я ИИ-бот, работающий на базе чатов.\nЗадай мне любой вопрос!')


@router.message()
async def handle_ai_query(message: types.Message):
    if not message.text:
        await message.answer('Отправьте текстовое сообщение.')
        return

    try:
        async with ChatActionSender.typing(bot=config.bot, chat_id=message.chat.id):
            answer = await search.search(message.text)

        await message.answer(answer)

    except Exception:
        await message.answer('Произошла ошибка. Попробуйте позже.')
