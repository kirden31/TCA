from telethon import events
import asyncio

import config
import messages


@config.client.on(events.NewMessage(chats=[x[0] for x in config.CHATS]))
async def catch_message(event):
    msg = event.message
    try:
        text = msg.text

        if (
            not text
            or (event.chat_id, getattr(msg.reply_to, 'reply_to_msg_id', None)) not in config.CHATS
        ):
            return

        await config.message_queue.put(msg)

    except Exception as e:
        print(f"Error processing message: {e}")


async def catch_history(chats, limit):
    """Скачивание истории сообщений из чатов."""
    await asyncio.gather(*(messages.save_history(chat_id, limit) for chat_id in chats))
