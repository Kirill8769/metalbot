from aiogram import F, Router, exceptions, types
from aiogram.filters.callback_data import CallbackQuery

from bot_keyboards.inline_kb_instructions import InstructionsCallBack, get_inline_kb_instructions
from src.utils import check_verification_admin, get_instruction

router_instructions = Router()


@router_instructions.message(F.text == '\U0001F4C3 Инструкции')
async def view_instructions(message: types.Message) -> None:
    """
    Обрабатывает запрос на получение инструкций.

    :param message: Объект сообщения.
    :return: None
    """
    if not await check_verification_admin(message):
        return
    text = '\U0001F4A1 Нажимайте на кнопки с инструкциями, для их отображения.'
    await message.answer(text=text, reply_markup=await get_inline_kb_instructions())


@router_instructions.callback_query(InstructionsCallBack.filter(F.label == 'instructions'))
async def select_instruction(query: CallbackQuery, callback_data: InstructionsCallBack) -> None:
    """
    Обрабатывает выбор инструкции пользователем.

    :param query: Колбэк запрос.
    :param callback_data: Данные колбэка.
    :return: None
    """
    if not await check_verification_admin(query):
        return
    text = await get_instruction(callback_data.page)
    try:
        await query.message.edit_text(text=text, reply_markup=await get_inline_kb_instructions())
    except exceptions.TelegramBadRequest:
        await query.answer()


@router_instructions.callback_query(InstructionsCallBack.filter(F.label == 'exit'))
async def select_instruction_exit(query: CallbackQuery) -> None:
    """
    Обрабатывает кнопку Закрыть. Удаляет инлайн сообщение.

    :param query: Колбэк запрос.
    :return: None
    """
    await query.message.delete()
