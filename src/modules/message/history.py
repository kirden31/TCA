import config
import modules.utils


async def save_history(chat_id, dt):
    c = 0

    async for msg in config.client.iter_messages(chat_id, offset_date=dt, reverse=True):
        if not msg.text:
            continue
        if msg.reply_to and msg.reply_to.forum_topic:
            msgr = msg.reply_to
            topic = msgr.reply_to_msg_id if not msgr.reply_to_top_id else msgr.reply_to_top_id
            if (msg.chat_id, topic) not in config.CHATS:
                continue

        await modules.utils.put([msg], config.message_queue_raw)

        c += 1

    return c
