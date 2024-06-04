import os

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot_keyboards.keyboards import get_cancel_kb, get_keyboard
from config import PATH_PROJECT
from loggers import logger
from src.utils import check_verification_user, get_info_xlsm, get_validate_input

router_catalog = Router()


class Catalog(StatesGroup):
    """ Класс представляет группу состояний для операций с каталогом. """
    parameters = State()


@router_catalog.message(F.text == '\U00002705 На главную')
async def catalog_cancel(message: types.Message, state: FSMContext) -> None:
    """
    Отмена операции с каталогом и возврат в главное меню.

    :param message: Объект сообщения.
    :param state: Контекст состояния.
    :return: None
    """
    if not await check_verification_user(message):
        return
    await state.clear()
    await message.answer('\U0001F4CC Главное меню', reply_markup=await get_keyboard(message))


@router_catalog.message(F.text == '\U0001F4D7 Каталог')
async def catalog_input(message: types.Message, state: FSMContext) -> None:
    """
    Запуск работы с каталогом и запрос размеров катализатора.

    :param message: Объект сообщения.
    :param state: Контекст состояния.
    :return: None
    """
    if not await check_verification_user(message):
        return
    await state.set_state(Catalog.parameters)
    await message.answer(
        text='\U00002757 Введите через пробел высоту, ширину,'
             'вес и длинну (необязательный параметр для продольных катализаторов)\n\n'
             '\U00002705 Порядок параметров: высота ширина вес длинна(необязательный)\n'
             '\U00002705 Пример с тремя показателями: 9 7.5 0.37\n'
             '\U00002705 Пример с четырьмя  показателями: 9 8 0.85 14\n\n'
             '\U00002757 Для возврата к меню, нажмите кнопку - \U00002705 На главную',
        reply_markup=await get_cancel_kb(handler='catalog')
    )


@router_catalog.message(Catalog.parameters)
async def catalog_output(message: types.Message) -> None:
    """
    Обработка параметров каталога, получение информации и отображение результатов.

    :param message: Объект сообщения.
    :return: None
    """
    user_message = message.text
    data = await get_validate_input(user_message)
    if not data:
        await message.answer('Неправильный формат ввода. Повторите ввод, либо нажмите На главную, для возврата к меню')
        return
    search_result = await get_info_xlsm(data)
    if search_result:
        for item in search_result:
            text = f"""Группа: {item[3]}
Особенности: {item[4]}
Тип: {item[5]}
Автомобиль: {item[6]}
Высота: {item[7]} см
Ширина: {item[8]} см
Длинна: {item[9]} см
Вес: {item[10]} кг"""
            file_path = os.path.join(PATH_PROJECT, 'images', f'{item[2]}.jpg')
            if os.path.isfile(file_path):
                await message.answer_photo(
                    photo=types.FSInputFile(path=file_path),
                    caption=text,
                )
            else:
                await message.answer(f'\U00002757Изображение отсутствует\n{text}')
                logger.warning('Изображение отсутствует: {item[2]}')
    else:
        await message.answer('\U0001F647По указанным параметрам ничего не найдено')
    return
