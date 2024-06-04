from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from src.utils import check_verification_admin


class CatalystsCallBack(CallbackData, prefix='catalysts'):
    label: str
    category: str


async def get_inline_kb_catalysts(message):
    """
    Создаёт инлайн клавиатуру с кнопками для демонстрации инструкций.

    :return: Инлайн клавиатура для демонстрации инструкций.
    """

    builder = InlineKeyboardBuilder()
    if await check_verification_admin(message):
        builder.row(
            InlineKeyboardButton(
                text='\U00002705 VIP',
                callback_data=CatalystsCallBack(label='catalyst', category='vip').pack()
            ),

            InlineKeyboardButton(
                text='\U00002705 ГО',
                callback_data=CatalystsCallBack(label='catalyst', category='go').pack()
            ),
        )
    builder.row(
        InlineKeyboardButton(
            text='\U000026D4 Закрыть',
            callback_data=CatalystsCallBack(label='exit', category='exit').pack()
        ),
    )
    return builder.as_markup()
