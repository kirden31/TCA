__all__ = ['get_embedder']

import asyncio
import logging
import os
from pathlib import Path

import aiogram.client.default
from dotenv import load_dotenv
from qdrant_client import AsyncQdrantClient
from telethon import TelegramClient

load_dotenv()

LOGS_DIR = Path(os.getenv('LOGS_DIR', Path.cwd())) / 'app.log'
LOGS_LEVEL_FILE = os.getenv('LOGS_LEVEL_FILE', 'INFO').upper()
LOGS_LEVEL_CONSOLE = os.getenv('LOGS_LEVEL_CONSOLE', 'WARNING').upper()

file_handler = logging.FileHandler(LOGS_DIR)
file_handler.setLevel(LOGS_LEVEL_FILE)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(LOGS_LEVEL_CONSOLE)

logging.basicConfig(
    level=LOGS_LEVEL_FILE,
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

if os.getenv('QDRANT_VOLUME_PATH'):
    QDRANT_VOLUME_PATH = Path(os.getenv('QDRANT_VOLUME_PATH', '')) / 'qdrant_storage'
else:
    QDRANT_VOLUME_PATH = Path.cwd() / 'qdrant_storage'

COLLECTION = os.getenv('QDRANT_COLLECTIONS', 'chat_analyzer_collection')

BATCH_SIZE = 64
BATCH_TIMEOUT = 0.5

LLM_BASE_URL = os.getenv('LLM_BASE_URL')
LLM_API_KEY = os.getenv('LLM_API_KEY', '')
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
bot = aiogram.Bot(
    token=TELEGRAM_TOKEN,
    default=aiogram.client.default.DefaultBotProperties(
        parse_mode='HTML',
    ),
)

qdrant_client = AsyncQdrantClient(url=QDRANT_URL)

embedder = None


def get_embedder():
    global embedder

    if embedder is None:
        from sentence_transformers import SentenceTransformer

        embedder = SentenceTransformer(
            'intfloat/multilingual-e5-base',
            device='cpu',
        )

    return embedder
