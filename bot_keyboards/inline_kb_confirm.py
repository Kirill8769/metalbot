from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


class ConfirmCallBack(CallbackData, prefix='confirm'):
    choice: str
    customer_id: str = ''


async def get_inline_kb_confirm(customer_id: str):
    """
    Создаёт инлайн клавиатуру для подтверждения действия.

    :param customer_id: id пользователя.
    :return: Инлайн клавиатура.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='Вы уверены ?',
            callback_data=ConfirmCallBack(choice='Z').pack()
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text='\U00002705 Да',
            callback_data=ConfirmCallBack(choice='Y', customer_id=customer_id).pack()
        ),
        InlineKeyboardButton(
            text='\U0000274E Нет',
            callback_data=ConfirmCallBack(choice='N', customer_id=customer_id).pack()
        ),
    )
    return builder.as_markup()
