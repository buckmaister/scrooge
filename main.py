import asyncio
import logging

from aiogram import Bot
from aiogram import Dispatcher

from config.config import CONFIG
from routers import router as main_router


async def main():
    dp = Dispatcher()
    dp.include_router(main_router)

    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=CONFIG['TELEGRAM']['TELEGRAM_TOKEN'])
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())