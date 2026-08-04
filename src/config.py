import asyncio
import os
import logging
from pathlib import Path

import aiogram

file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[file_handler, stream_handler],
)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
from qdrant_client import AsyncQdrantClient
from sentence_transformers import SentenceTransformer
from telethon import TelegramClient, functions

load_dotenv()


def parse_chats(chats_env):
    chats = []

    for chat in chats_env.split():
        parts = chat.split('_')

        if len(parts) == 2:
            chat_id, topic_id = parts
            chats.append((int(chat_id), int(topic_id)))
        elif len(parts) == 1:
            chats.append((int(parts[0]), None))
        else:
            logger.debug(f'Unexpected format in CHATS: {parts}')
            raise ValueError(f'Invalid CHATS data format: "{chat}"')

    return chats


API_ID = int(os.getenv('API_ID', ''))

API_HASH = os.getenv('API_HASH', '')

qdrant_url = os.getenv('QDRANT_URL') or 'http://localhost:6333'
qdrant_volume_path = Path.cwd() / 'qdrant_storage'
COLLECTION = os.getenv('QDRANT_COLLECTION')

BATCH_SIZE = 64
BATCH_TIMEOUT = 0.5

LLM_BASE_URL = os.getenv('LLM_BASE_URL')
LLM_API_KEY = os.getenv('LLM_API_KEY')
LLM_MODEL = os.getenv('LLM_MODEL')

CHATS = parse_chats(os.getenv('CHATS', ''))

message_queue_raw = asyncio.Queue()
message_queue = asyncio.Queue()

client = TelegramClient(
    'tg-parser',
    api_id=API_ID,
    api_hash=API_HASH,
)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
bot = aiogram.Bot(token=TELEGRAM_TOKEN)

qdrant_client = AsyncQdrantClient(url=qdrant_url)
embedder = SentenceTransformer('intfloat/e5-small', device='cpu')
