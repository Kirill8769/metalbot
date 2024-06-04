from aiogram import F, Router, exceptions, types
from aiogram.filters.callback_data import CallbackQuery

from bot_keyboards.inline_kb_regulations import RegulationsCallBack, get_inline_kb_regulations
from src.utils import check_verification_admin, check_verification_user, get_regulation

router_regulations = Router()


@router_regulations.message(F.text == '\U0001F4DC Регламенты')
async def view_regulations(message: types.Message) -> None:
    """
    Обрабатывает запрос на получение регламентов.

    :param message: Объект сообщения.
    :return: None
    """
    if not await check_verification_admin(message):
        return
    text = '\U0001F4A1 Нажимайте на кнопки с регламентами, для их отображения.'
    await message.answer(text=text, reply_markup=await get_inline_kb_regulations())


@router_regulations.callback_query(RegulationsCallBack.filter(F.label == 'regulations'))
async def select_regulation(query: CallbackQuery, callback_data: RegulationsCallBack) -> None:
    """
    Обрабатывает выбор регламента пользователем.

    :param query: Колбэк запрос.
    :param callback_data: Данные колбэка.
    :return: None
    """
    if not await check_verification_admin(query):
        return
    text = await get_regulation(callback_data.page)
    try:
        await query.message.edit_text(text=text, reply_markup=await get_inline_kb_regulations())
    except exceptions.TelegramBadRequest:
        await query.answer()


@router_regulations.callback_query(RegulationsCallBack.filter(F.label == 'exit'))
async def select_regulation_exit(query: CallbackQuery) -> None:
    """
    Обрабатывает кнопку Закрыть. Удаляет инлайн сообщение.

    :param query: Колбэк запрос.
    :return: None
    """
    await query.message.delete()
