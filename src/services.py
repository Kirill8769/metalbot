import asyncio

from aiogram import Bot

from db.db_handlers import UserDB
from loggers import logger


async def send_message_all_customers(bot: Bot):
    """
    Отправляет сообщение всем активным пользователям бота.

    :param bot: Экземпляр бота.
    """
    await asyncio.sleep(2)
    user_db = UserDB()
    customers = await user_db.get_all_customers_info()
    active_customers = [customer for customer in customers if customer['status']]
    text = '\U00002757\U00002757\U00002757\nМы обновили бота!\nЧтобы применить изменения,\nнажмите /start.'
    for customer in active_customers:
        await bot.send_message(chat_id=customer['customer_id'], text=text)
        logger.info(f"[+] Уведомление отправлено id:{customer['customer_id']} username:{customer['username']}")
    else:
        logger.info(f'[+] Все сообщения отправлены')
