__all__ = []

import asyncio
import logging
import os
from pathlib import Path

import aiogram
from dotenv import load_dotenv
from qdrant_client import AsyncQdrantClient
from sentence_transformers import SentenceTransformer
from telethon import TelegramClient

load_dotenv()

log_levels = {
    'BEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
}

file_handler = logging.FileHandler('app.log')
file_handler.setLevel(log_levels[os.getenv('LOG_LEVEL', 'INFO').upper()])

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[file_handler, stream_handler],
)
logger = logging.getLogger(__name__)


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

QDRANT_URL = os.getenv('QDRANT_URL') or 'http://localhost:6333'
QDRANT_VOLUME_PATH = Path(os.getenv('QDRANT_VOLUME_PATH', Path.cwd())) / 'qdrant_storage'
COLLECTION = os.getenv('QDRANT_COLLECTION')

BATCH_SIZE = 64
BATCH_TIMEOUT = 0.5

LLM_BASE_URL = os.getenv('LLM_BASE_URL')
LLM_API_KEY = os.getenv('LLM_API_KEY')
LLM_MODEL = os.getenv('LLM_MODEL')

CHATS = parse_chats(os.getenv('CHATS', ''))
ALLOWED_USERS = os.getenv('ALLOWED_USERS', '')

message_queue_raw = asyncio.Queue()
message_queue = asyncio.Queue()

client = TelegramClient(
    'tg-parser',
    api_id=API_ID,
    api_hash=API_HASH,
)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
bot = aiogram.Bot(token=TELEGRAM_TOKEN)

qdrant_client = AsyncQdrantClient(url=QDRANT_URL)
embedder = SentenceTransformer('intfloat/multilingual-e5-base', device='cpu')
