__all__ = ['catch_message', 'download_history']

import asyncio
import logging

import config
from modules.message import history
import modules.utils
from telethon import events

logger = logging.getLogger(__name__)


@config.client.on(events.NewMessage(chats=[x[0] for x in config.CHATS]))
@config.client.on(events.MessageEdited(chats=[x[0] for x in config.CHATS]))
async def catch_message(event):
    msg = event.message
    try:
        if msg.text:
            if msg.reply_to and msg.reply_to.forum_topic:
                msgr = msg.reply_to
                topic = msgr.reply_to_msg_id if not msgr.reply_to_top_id else msgr.reply_to_top_id
                if (msg.chat_id, topic) not in config.CHATS:
                    return

        logger.debug(f'{msg.date}: added {msg.text[:50]} ...')

        await modules.utils.put([msg], config.message_queue_raw)

    except Exception as e:
        logger.error(f'Error processing message: {e}')


async def download_history(dt, chats=config.CHATS):
    unique_chats = {chat_id for chat_id, _ in chats}
    try:
        logger.info('Start downloading history')
        return await asyncio.gather(
            *[history.save_history(chat_id, dt) for chat_id in unique_chats],
        )
    except Exception as e:
        logger.error(f'Error downloading history: {e}')
