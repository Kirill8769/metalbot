from aiogram import F, Router, exceptions, types
from aiogram.filters.callback_data import CallbackQuery

from bot_keyboards.inline_kb_quotes import QuotesCallBack, get_inline_kb_quotes
from src.utils import check_verification_user, get_message_quotes

router_quotes = Router()


@router_quotes.message(F.text == '\U0001F4CA Котировки')
async def exchange_quotes(message: types.Message) -> None:
    """
    Обрабатывает запрос на получение биржевых котировок.

    :param message: Объект сообщения.
    :return: None
    """
    if not await check_verification_user(message):
        return
    text = await get_message_quotes(rate='71')
    await message.answer(text=text, reply_markup=await get_inline_kb_quotes(message))


@router_quotes.callback_query(QuotesCallBack.filter(F.label == 'rate'))
async def select_quotes(query: CallbackQuery, callback_data: QuotesCallBack) -> None:
    """
    Обрабатывает выбор пользователя в биржевых котировках.

    :param query: Колбэк запрос.
    :param callback_data: Данные колбэка.
    :return: None
    """
    text = await get_message_quotes(callback_data.rate)
    try:
        await query.message.edit_text(text=text, reply_markup=await get_inline_kb_quotes(query))
    except exceptions.TelegramBadRequest:
        await query.answer()


@router_quotes.callback_query(QuotesCallBack.filter(F.label == 'exit'))
async def select_quotes_cancel(query: CallbackQuery) -> None:
    """
    Обрабатывает кнопку Закрыть. Удаляет инлайн сообщение.

    :param query: Колбэк запрос.
    :return: None
    """
    await query.message.delete()
