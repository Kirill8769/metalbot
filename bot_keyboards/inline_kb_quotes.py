from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from src.utils import check_verification_admin


class QuotesCallBack(CallbackData, prefix='quotes'):
    label: str
    rate: str


async def get_inline_kb_quotes(message):
    """
    Создаёт инлайн клавиатуру с кнопками процентов для расчёта.

    :return: Инлайн клавиатура для расчёта цен металлов.
    """
    rate_1 = 60
    rate_2 = 65
    rate_3 = 71
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='\U00002705 100',
            callback_data=QuotesCallBack(label='rate', rate='100').pack()
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=f'\U00002705 {rate_1}',
            callback_data=QuotesCallBack(label='rate', rate=f'{rate_1}').pack()
        ),
        InlineKeyboardButton(
            text=f'\U00002705 {rate_2}',
            callback_data=QuotesCallBack(label='rate', rate=f'{rate_2}').pack()
        ),
        InlineKeyboardButton(
            text=f'\U00002705 {rate_3}',
            callback_data=QuotesCallBack(label='rate', rate=f'{rate_3}').pack()
        ),
    )
    if await check_verification_admin(message=message):
        admin_rate_1 = 74
        admin_rate_2 = 76
        builder.row(
            InlineKeyboardButton(
                text=f'\U00002705 {admin_rate_1}',
                callback_data=QuotesCallBack(label='rate', rate=f'{admin_rate_1}').pack()
            ),
            InlineKeyboardButton(
                text=f'\U00002705 {admin_rate_2}',
                callback_data=QuotesCallBack(label='rate', rate=f'{admin_rate_2}').pack()
            ),
        )
    builder.row(
        InlineKeyboardButton(
            text=f'\U00002705 {rate_1} | {rate_2} | {rate_3} \U00002705',
            callback_data=QuotesCallBack(label='rate', rate=f'{rate_1},{rate_2},{rate_3}').pack()),
    )
    builder.row(
        InlineKeyboardButton(
            text='\U000026D4 Закрыть',
            callback_data=QuotesCallBack(label='exit', rate='0').pack()
        ),
    )
    return builder.as_markup()
