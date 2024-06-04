from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


class RegulationsCallBack(CallbackData, prefix='regulations'):
    label: str
    page: str


async def get_inline_kb_regulations():
    """
    Создаёт инлайн клавиатуру с кнопками для демонстрации регламентов.

    :return: Инлайн клавиатура для демонстрации регламентов.
    """

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='\U0001F5C3 Документы ВМ на маршруте',
            callback_data=RegulationsCallBack(label='regulations', page='documents_vm').pack()
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text='\U0001F440 Меры безопасности',
            callback_data=RegulationsCallBack(label='regulations', page='security').pack()
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text='\U0001F46E Общение с гос.органами',
            callback_data=RegulationsCallBack(label='regulations', page='state_authorities').pack()
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text='\U0001F4E6 Регламент упаковки посылок',
            callback_data=RegulationsCallBack(label='regulations', page='sending_package').pack()
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text='\U000026D4 Закрыть',
            callback_data=RegulationsCallBack(label='exit', page='exit').pack()
        ),
    )
    return builder.as_markup()
