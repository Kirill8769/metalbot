from aiogram import Router, types
from aiogram.filters import CommandStart

from bot_keyboards.keyboards import get_keyboard
from db.db_handlers import UserDB
from src.utils import check_verification_user

router_main = Router()


@router_main.message(CommandStart())
async def cmd_start(message: types.Message) -> None:
    """
    Обрабатывает команду /start.

    :param message: Объект сообщения.
    :return: None
    """
    if not await check_verification_user(message):
        return
    db = UserDB()
    await db.update_customer(message)
    await message.answer(
        text=f'Добрый день, {message.from_user.first_name} \U0001F44B\nВыберите пункт меню ↘',
        reply_markup=await get_keyboard(message)
    )
