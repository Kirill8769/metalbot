from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot_keyboards.keyboards import get_cancel_kb
from config import prices_list
from src.utils import check_verification_user, get_validate_input

router_calc = Router()


class Calculator(StatesGroup):
    """ Класс представляет группу состояний для операций с калькулятором. """
    amount_metals = State()


@router_calc.message(F.text == '\U0001F9EE Калькулятор')
async def calculator_input(message: types.Message, state: FSMContext) -> None:
    """
    Запуск работы с калькулятором и запрос веса металлов.

    :param message: Объект сообщения.
    :param state: Контекст состояния.
    :return: None
    """
    if not await check_verification_user(message):
        return
    await state.set_state(Calculator.amount_metals)
    await message.answer(
        text='\U00002757 Введите 3 показателя в граммах через пробел. Если металла нет, напишите 0\n\n'
             '\U00002705 Порядок металлов: Pt Pd Rh\n'
             '\U00002705 Пример: 2.3 4 1.2\n'
             '\U00002705 Пример: 4.2 0 0\n\n'
             '\U00002757 Для возврата к меню, нажмите кнопку - \U00002705 На главную',
        reply_markup=await get_cancel_kb(handler='calc')
    )


@router_calc.message(Calculator.amount_metals)
async def calculator_output(message: types.Message) -> None:
    """
    Обработка переданных весов металлов, получение информации и отображение результатов.

    :param message: Объект сообщения.
    :return: None
    """
    user_message = message.text
    data = await get_validate_input(user_message)
    if not data:
        await message.answer('Неправильный формат ввода. Повторите ввод, либо нажмите На главную, для возврата к меню')
        return
    pt = prices_list[0]['pt_ru']
    pd = prices_list[0]['pd_ru']
    rh = prices_list[0]['rh_ru']
    rate = 0.71
    result = round(pt * data[0] * rate + pd * data[1] * rate + rh * data[2] * rate, 2)
    await message.answer(
        text=f'Pt: {data[0]} г\nPd: {data[1]} г\nRh: {data[2]} г\n'
             f'Процент: {rate * 100}%\nРезультат расчёта: {result} руб'
    )
    return
