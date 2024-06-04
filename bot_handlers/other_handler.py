from aiogram import F, Router, types

from bot_keyboards.keyboards import get_keyboard
from config import wisdom_day
from loggers import logger
from src.utils import check_verification_user

router_other = Router()


@router_other.message(F.text == 'id')
async def get_id(message: types.Message) -> None:
    """
    Функция возвращает id пользователя.

    :param message: Объект сообщения.
    :return: None
    """
    await message.answer(text=f'Ваш ID: {message.from_user.id}')


@router_other.message(F.text == '777')
async def get_wisdom(message: types.Message) -> None:
    """
    Функция возвращает мудрость дня.

    :param message: Объект сообщения.
    :return: None
    """
    if not await check_verification_user(message):
        return
    text = 'Мудрец сломался, обратитесь к администратору.'
    try:
        text = f'Мудрость дня \U0001F4A1\n\n{wisdom_day[0]}'
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}")
    finally:
        await message.answer(text=text, reply_markup=await get_keyboard(message))


@router_other.message()
async def clear(message: types.Message) -> None:
    """
    Функция удаляет нерегламентированные сообщения.

    :param message: Объект сообщения.
    :return: None
    """
    if not await check_verification_user(message):
        return
    await message.delete(reply_markup=await get_keyboard(message))
