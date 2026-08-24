![CI](https://github.com/kirden31/TCA/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)
![Qdrant](https://img.shields.io/badge/Qdrant-vector%20DB-orange)

# Chat-Analyzer

Сервер для анализа **Telegram-чатов**: семантический поиск по истории сообщений, векторная БД (**[Qdrant](https://qdrant.tech/)**) и **LLM** для генерации ответов. Написан на **асинхронном [Python](https://www.python.org/)** с использованием **[Telethon](https://docs.telethon.dev/)** (userbot) для сбора данных и **[aiogram](https://docs.aiogram.dev/)** (bot) для взаимодействия с пользователем.

---

## Возможности

- **Семантический поиск** — эмбеддинг [`intfloat/multilingual-e5-base`](https://huggingface.co/intfloat/multilingual-e5-base) находит смысл, а не просто ключевые слова
- **Контекстные ответы** — **LLM** синтезирует ответ из найденных сообщений с цитированием, оценкой достоверности и комментарием к качеству данных
- **Telegram-интеграция** — **[Telethon](https://docs.telethon.dev/)** (userbot) для индексации + **[aiogram](https://docs.aiogram.dev/)** (bot) для запросов пользователей
- **Асинхронные воркеры** — конвейер: сырые сообщения → эмбеддинги → батчевые **upsert** в Qdrant
- **Загрузка истории** — однокомандная выкачка истории от заданной даты с поддержкой **тем форумов**
- **Контроль доступа** — **whitelist** пользователей для бота
- **Автоматическое управление Qdrant** — **Docker-контейнер**, схема коллекции и **payload-индексы** поднимаются автоматически

---

## Архитектура

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Telegram API   │────▶│  Telethon Client │────▶│  Raw Queue      │
│  (Userbot)      │     │  (Parser)        │     │  (asyncio.Queue)│
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                    ┌──────────────────┐                  │
                    │  Messages Worker │◀─────────────────┘
                    │  (Embedding)     │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Qdrant Queue    │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Qdrant Workers  │──▶ Qdrant Vector DB
                    │  (Batched Upsert)│
                    └──────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  aiogram Bot     │◀── User Queries
                    │  (Search + LLM)  │
                    └──────────────────┘
```

**Слои приложения:**

| Слой | Модуль | Ответственность |
|------|--------|-----------------|
| **Entry** | `main.py` | Оркестрация: запуск Qdrant, эмбеддера, парсера и бота |
| **Config** | `config.py` | Настройки из **env**, логирование, глобальные клиенты |
| **Services** | `services/*.py` | Высокоуровневые раннеры: `parser`, `telegram`, `qdrant`, `ai` |
| **Modules** | `modules/*` | Доменная логика: AI, сообщения, Telegram, Qdrant, воркеры |
| **Workers** | `modules/workers/*` | Асинхронные батч-процессоры с обработкой **бэкпрешера** |

---

## Технологический стек

| Категория | Технология                                                                                                                                                  |
|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Язык** | [Python 3.10–3.12](https://www.python.org/downloads/)                                                                                                       |
| **Async runtime** | `asyncio` + `aioconsole`                                                                                                                                    |
| **Telegram (userbot)** | [Telethon 1.44](https://docs.telethon.dev/)                                                                                                                 |
| **Telegram (bot)** | [aiogram 3.28](https://docs.aiogram.dev/)                                                                                                                   |
| **Vector DB** | [Qdrant 1.12](https://qdrant.tech/) (Docker)                                                                                                                |
| **Embeddings** | [sentence-transformers](https://www.sbert.net/) — `intfloat/multilingual-e5-base`                                                                           |
| **LLM** | OpenAI-совместимый API ([LM Studio](https://lmstudio.ai/), [vLLM](https://vllm.ai/), [Ollama](https://ollama.com/), [OpenAI](https://platform.openai.com/)) |
| **Code quality** | [black](https://black.readthedocs.io/), [flake8](https://flake8.pycqa.org/) + плагины                                                       |

---

## Установка

### Требования

- **[Docker](https://docs.docker.com/engine/install/)** (для Qdrant)
- **[Python 3.10+](https://www.python.org/downloads/)**
- **Telegram API credentials** ([my.telegram.org](https://my.telegram.org))
- **Bot Token** ([@BotFather](https://t.me/BotFather))
- **LLM endpoint** (OpenAI-совместимый — локальный или удалённый)

### Быстрый старт

```bash
# 1. Клонирование
git clone https://github.com/kirden31/TCA.git
cd TCA

# 2. Виртуальное окружение
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# 3. Зависимости
pip install -r requirements/prod.txt

# 4. Конфигурация
cp templates.env .env
# Отредактируйте .env (см. раздел ниже)

# 5. Запуск
cd src
python3 -m main
```

> Приложение само поднимет Qdrant в Docker. Убедитесь, что Docker daemon запущен.

---

## Конфигурация

Все настройки — в `.env` (скопируйте из `templates.env`):

```bash
# --- Telegram (Userbot) ---
API_ID=12345678                    # Из my.telegram.org
API_HASH=abcdef123456...           # Из my.telegram.org
PHONE_NUMBER=+79001234567          # Для авторизации Telethon (только первый запуск)

# --- Telegram (Bot) ---
TELEGRAM_BOT_TOKEN=123456:ABC...   # От @BotFather

# --- Qdrant ---
QDRANT_URL=http://localhost:6333
QDRANT_VOLUME_PATH=/path/to/storage  # Опционально, по умолчанию ./qdrant_storage
QDRANT_COLLECTIONS=chat_analyzer_collection # Название колекции

# --- LLM (OpenAI-совместимый) ---
LLM_BASE_URL=http://localhost:1234/v1  # LM Studio, vLLM, Ollama и т.д.
LLM_API_KEY=sk-...                     # Для локальных серверов обычно может быть любым
LLM_MODEL=qwen/qwen3.5-9b              # Идентификатор модели

# --- Чаты и доступ ---
CHATS=-1001234567890 -100987654321_42  # chat_id [ _topic_id ] через пробел
ALLOWED_USERS=123456789 987654321      # ID пользователей, которым разрешен бот

# --- Логирование ---
LOGS_LEVEL_FILE=INFO                   # Уровень логов в файле
LOGS_LEVEL_CONSOLE=WARNING             # Уровень логов в консоли
LOGS_DIR=/var/log/chat-analyzer        # Опционально, по умолчанию cwd
```

### Формат `CHATS`

```
CHATS=<chat_id> [<chat_id>_<topic_id>] ...
```

- **Личка / группа / канал**: `-1001234567890`
- **Тема форума**: `-1001234567890_42` (chat_id + topic_id)
- Несколько записей разделяются пробелом

---

## Использование

### Запуск сервера

```bash
cd src
python3 -m main
```

Опционально — загрузка истории от конкретной даты:

```bash
python3 -m main --download-from-datetime [-dfd] 2024-01-20T00:00:00
```

### CLI-консоль (для отладки)

```bash
cd src
python3 -m services.ai
# Вводите вопросы, "CLOSE AI APP" — выход
```

### Отдельные компоненты

```bash
# Только Qdrant (поднимет Docker, создаст коллекцию и индексы)
python3 -m services.qdrant

# Только парсер (индексация + воркеры)
python3 -m services.parser

# Бот, Qdrant и LLM (aiogram polling)
# !! Qdrant необходимо запускать отдельно !!
python3 -m services.telegram
```

---

## Структура проекта

```
Chat-Analyzer/
├── .github/workflows/ci.yml      # CI: black + flake8
├── requirements/
│   ├── prod.txt                  # Runtime зависимости
│   └── dev.txt                   # Dev зависимости (линтеры, форматтеры)
├── templates.env                 # Пример конфигурации
├── pyproject.toml                # Настройки black
├── README.md
└── src/
    ├── main.py                   # Точка входа
    ├── config.py                 # Настройки, логирование, клиенты
    ├── services/                 # Сервисные раннеры
    │   ├── ai.py                 # Интерактивная AI-консоль
    │   ├── qdrant.py             # Жизненный цикл Qdrant + схема
    │   ├── parser.py             # Telethon + оркестрация воркеров
    │   └── telegram.py           # aiogram-бот + хендлеры
    └── modules/                  # Доменные модули
        ├── ai/
        │   ├── prompts.py        # Системные промпты (RAG + query rewrite)
        │   └── search.py         # Семантический поиск + синтез ответа LLM
        ├── message/
        │   ├── bot.py            # Event handlers (catch_message, download_history)
        │   ├── history.py        # Итерация исторических сообщений
        │   └── messages.py       # Сообщение → вектор + payload
        ├── telegram/
        │   ├── decorators.py     # Auth middleware (allowlist)
        │   └── handlers.py       # Хендлеры команд и сообщений бота
        ├── qdrant/
        │   └── qdrant_server.py  # Управление Docker-контейнером
        ├── workers/
        │   ├── messages_worker.py  # Raw → embeddings → Qdrant queue
        │   └── qdrant_workers.py   # Батчевые upsert в Qdrant
        └── utils.py              # Утилиты эмбеддингов и очередей
```

---

## Разработка

### Стиль кода

```bash
pip install -r requirements/dev.txt

# Форматирование
black .

# Линтинг
flake8 .
```

### CI Pipeline

[GitHub Actions workflow](.github/workflows/ci.yml) запускается на каждый push:

1. **Black** — проверка форматирования
2. **Flake8** — стиль и сложность (21 плагин: bugbear, comprehensions, imports и др.)

---

## Docker (только Qdrant)

Приложение управляет Qdrant автоматически. Ручной контроль:

```bash
# Запуск
docker run -d -p 6333:6333 -p 6334:6334 \
  -v /path/to/storage:/qdrant/storage:z \
  --name chat_analyzer_qdrant qdrant/qdrant

# Остановка
docker stop chat_analyzer_qdrant

# Логи
docker logs chat_analyzer_qdrant
```

См. **[Docker Docs](https://docs.docker.com/engine/reference/commandline/run/)** для деталей по параметрам.

---

## Лицензия

**[MIT](https://opensource.org/licenses/MIT)**

---

## Участие в разработке

1. Форкнате репу
2. Пишите issue
3. Перед коммитом выполните `black . && flake8 --verbose`
4. Откройте Pull Request
5. ^&_%^

---