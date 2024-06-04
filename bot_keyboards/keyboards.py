from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from src.utils import check_verification_admin


async def get_keyboard(message: Message) -> ReplyKeyboardMarkup:
    """
    Генерирует клавиатуру для главного меню.

    :return: Объект клавиатуры для главного меню.
    """
    buttons = [
        [KeyboardButton(text='\U0001F4CA Котировки'), KeyboardButton(text='\U0001F697 Катализаторы')],
        [KeyboardButton(text='\U0001F9EE Калькулятор'), KeyboardButton(text='\U0001F4D7 Каталог')],
    ]
    if await check_verification_admin(message=message):
        buttons.append([KeyboardButton(text='\U0001F4C3 Инструкции'), KeyboardButton(text='\U0001F4DC Регламенты')])
        buttons.append([KeyboardButton(text='\U0001F4BC Админка')])
    markup = ReplyKeyboardMarkup(
        keyboard=[*buttons], resize_keyboard=True, input_field_placeholder='выберите пункт меню'
    )
    return markup


async def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """
    Генерирует клавиатуру админа.

    :return: Объект клавиатуры админа.
    """
    buttons = [
        [KeyboardButton(text='\U0001F4DD Добавить пользователя')],
        [KeyboardButton(text='\U0001F4CB Посмотреть список пользователей')],
        [KeyboardButton(text='\U00002705 На главную')],
    ]
    markup = ReplyKeyboardMarkup(
        keyboard=[*buttons], resize_keyboard=True, input_field_placeholder='выберите пункт меню'
    )
    return markup


async def get_cancel_kb(handler: str) -> ReplyKeyboardMarkup:
    """
    Генерирует клавиатуру для отмены текущего действия.

    :param handler: Название хендлера для генерации сообщения для окна ввода.
    :return: Объект клавиатуры для отмены текущего действия.
    """
    if handler == 'calc':
        placeholder = 'Pt Pd Rh'
    elif handler == 'catalog':
        placeholder = 'высота ширина вес длинна(необязательный)'
    else:
        placeholder = 'поле ввода'
    markup = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='\U00002705 На главную')],
    ], resize_keyboard=True, input_field_placeholder=placeholder)
    return markup


async def get_cancel_admin_kb() -> ReplyKeyboardMarkup:
    """
    Генерирует клавиатуру для отмены текущего действия.

    :return: Объект клавиатуры для отмены текущего действия.
    """
    placeholder = 'введите id пользователя'
    markup = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='\U00002705 Отмена')],
    ], resize_keyboard=True, input_field_placeholder=placeholder)
    return markup
