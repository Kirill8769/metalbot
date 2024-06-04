from aiogram import F, Router, exceptions, types
from aiogram.filters.callback_data import CallbackQuery

from bot_keyboards.inline_kb_catalyst import CatalystsCallBack, get_inline_kb_catalysts
from src.utils import check_verification_user, get_catalyst_prices

router_catalyst = Router()


@router_catalyst.message(F.text == '\U0001F697 Катализаторы')
async def catalyst_prices(message: types.Message) -> None:
    """
    Обрабатывает запрос на получение цен на катализаторы и вызывает инлайн клавиатуру.

    :param message: Объект сообщения.
    :return: None
    """
    if not await check_verification_user(message):
        return
    text = await get_catalyst_prices(category='vip')
    await message.answer(text=text, reply_markup=await get_inline_kb_catalysts(message))


@router_catalyst.callback_query(CatalystsCallBack.filter(F.label == 'catalyst'))
async def select_catalyst(query: CallbackQuery, callback_data: CatalystsCallBack) -> None:
    """
    Обрабатывает выбор пользователя цен на катализаторы.

    :param query: Колбэк запрос.
    :param callback_data: Данные колбэка.
    :return: None
    """
    text = await get_catalyst_prices(category=callback_data.category)
    try:
        await query.message.edit_text(text=text, reply_markup=await get_inline_kb_catalysts(query))
    except exceptions.TelegramBadRequest:
        await query.answer()


@router_catalyst.callback_query(CatalystsCallBack.filter(F.label == 'exit'))
async def select_catalyst_exit(query: CallbackQuery) -> None:
    """
    Обрабатывает кнопку Закрыть. Удаляет инлайн сообщение.

    :param query: Колбэк запрос.
    :return: None
    """
    await query.message.delete()
