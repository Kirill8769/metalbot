from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


class CustomersCallBack(CallbackData, prefix='customers'):
    service: str
    customer_id: str


async def get_inline_kb_customers(user_info: dict):
    """
    Создаёт инлайн клавиатуру для работы с пользователем.

    :param user_info: Словарь с информацией о пользователе.
    :return: Инлайн клавиатура.
    """
    builder = InlineKeyboardBuilder()
    if user_info['status']:
        button_text = "\U0000274E Заблокировать"
        service_name = 'deactivate'
    else:
        button_text = "\U00002705 Активировать"
        service_name = 'activate'
    builder.row(
        InlineKeyboardButton(
            text=button_text,
            callback_data=CustomersCallBack(service=service_name, customer_id=user_info['customer_id']).pack()
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text='\U000026D4 Удалить',
            callback_data=CustomersCallBack(
                service='delete',
                customer_id=user_info['customer_id']
            ).pack()
        ),
    )
    return builder.as_markup()
