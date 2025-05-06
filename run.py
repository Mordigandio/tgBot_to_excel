"""Запуск Telegram-бота.

    Модуль инициализирует бота, подключает обработчики и запускает опрос сообщений

    Raises:
        ValueError: Если токен бота не найден в файле .env
    """

import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.handlers.file_handler import router
from dotenv import load_dotenv

async def main() -> None:
    """Инициализирует и запускает telegram-бота
    
        Загружает токен бота из файла .env, создает экземпляры Bot и Dispatcher.
        Подключает обработчики и запускает опрос сообщений.

    Returns:
        None
    """
    
    # Загружает переменные окружения
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN не найден, проверьте .env")
    
    # Инициализирует bot и dispatcher подключаем роутер
    bot = Bot(token=bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())