from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


class InstructionsCallBack(CallbackData, prefix='instructions'):
    label: str
    page: str


async def get_inline_kb_instructions():
    """
    Создаёт инлайн клавиатуру с кнопками для демонстрации инструкций.

    :return: Инлайн клавиатура для демонстрации инструкций.
    """

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='\U0001F4F2 Вход в Битрикс24',
            callback_data=InstructionsCallBack(label='instructions', page='enter_b24').pack()
        ),

        InlineKeyboardButton(
            text='\U0001F4F2 Настройка Bitrix OTP',
            callback_data=InstructionsCallBack(label='instructions', page='setting_otp').pack()
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text='\U0001F454 Jump Finance',
            callback_data=InstructionsCallBack(label='instructions', page='jump_finance').pack()
        ),

        InlineKeyboardButton(
            text='\U0001F5D2 Napoleon',
            callback_data=InstructionsCallBack(label='instructions', page='napoleon').pack()
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text='\U000026D4 Закрыть',
            callback_data=InstructionsCallBack(label='exit', page='exit').pack()
        ),
    )
    return builder.as_markup()
