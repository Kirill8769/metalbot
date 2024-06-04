import asyncio
import os

import schedule
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot_handlers.admin_handler import router_admin
from bot_handlers.calc_handler import router_calc
from bot_handlers.catalyst_handler import router_catalyst
from bot_handlers.catalog_handler import router_catalog
from bot_handlers.instructions_handler import router_instructions
from bot_handlers.other_handler import router_other
from bot_handlers.quotes_handler import router_quotes
from bot_handlers.regulations_handler import router_regulations
from bot_handlers.main_handler import router_main
from db.db_handlers import UserDB
from loggers import logger
from src.services import send_message_all_customers
from src.utils import price_parsing, restart_program


async def main() -> None:
    """
    Основная функция программы.
    Запускает парсер, бота, создаёт таблицы в БД и расписание задач.

    :return: None
    """
    logger.info('[+] Start program')
    db = UserDB()
    await db.create_tables()
    await db.update_customers_lists()
    price_parsing()
    await asyncio.gather(start_bot(), schedule_tasks())  # , send_message_all_customers(bot=bot))


async def schedule_tasks() -> None:
    """
    Функция для управления расписанием задач.
    Парсер запускается каждый день в 05:00.

    :return: None
    """
    logger.info('[+] Schedule is running')
    schedule.every().day.at('05:10').do(restart_program)
    # schedule.every(10).seconds.do(price_parsing)  # test work
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


async def start_bot():
    """
    Функция для запуска бота.
    Использует токен из переменных среды, загружает роутеры и запускает бота.

    :return: None
    """
    dp.include_router(router=router_catalog)
    dp.include_router(router=router_calc)
    dp.include_router(router=router_admin)
    dp.include_router(router=router_instructions)
    dp.include_router(router=router_quotes)
    dp.include_router(router=router_catalyst)
    dp.include_router(router=router_regulations)
    dp.include_router(router=router_main)
    dp.include_router(router=router_other)
    logger.info("[+] Bot is started")
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        load_dotenv()
        token = os.getenv('TOKEN')
        dp = Dispatcher()
        bot = Bot(token)
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('[+] Exiting the program')
