import asyncio

from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers import user_handlers
from data_bases.connect_data_base import connect_db, DB_NAME

# Функция конфигурирования и запуска бота
async def main():
    # Загружаем конфиг в переменную config
    config: Config = load_config()

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token)
    dp = Dispatcher()

    # Регистриуем роутеры в диспетчере
    dp.include_router(user_handlers.router)
    # dp.include_router(other_handlers.router)
    connect, cursor = connect_db(DB_NAME)
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                user_id INTENGER,
                user_name TEXT,
                mark1 INTENGER,
                mark2 INTENGER,
                club TEXT,
                offer_status TEXT,
                mark3 INTENGER,
                mark4 INTENGER,
                mark5 INTENGER,
                mark6 INTENGER)
                """)
    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())