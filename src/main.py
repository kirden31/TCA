import argparse
import asyncio

import bot
import config
import utils


async def main():
    parser = argparse.ArgumentParser(description='Telegram chat message downloader and monitor')
    parser.add_argument(
        '-H',
        '--download_history',
        action='store_true',
        default=False,
        help='Download chat history instead of monitoring new messages',
    )
    parser.add_argument(
        '--chats',
        nargs='+',
        type=int,
        default=None,
        help='Chat IDs to process (negative for groups/channels, e.g. -100123456789). '
        'Uses config default if not specified',
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of messages to download per chat',
    )
    args = parser.parse_args()

    await config.client.start()

    if args.download_history:
        if not args.limit:
            raise RuntimeError('You have to set LIMIT to download history.')
        chats = args.chats if args.chats else config.CHATS
        await bot.catch_history(chats, args.limit)

    print('Мониторинг новых сообщений... (нажмите Ctrl+C для остановки)')

    for _ in range(2):
        asyncio.create_task(utils.batch_worker())
    await config.client.run_until_disconnected()


if __name__ == '__main__':
    asyncio.run(main())
