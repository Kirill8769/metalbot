from aiogram import F, Router, types
from aiogram.filters.callback_data import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot_keyboards.inline_kb_confirm import ConfirmCallBack, get_inline_kb_confirm
from bot_keyboards.inline_kb_customers import CustomersCallBack, get_inline_kb_customers
from bot_keyboards.keyboards import get_admin_keyboard, get_cancel_admin_kb
from db.db_handlers import UserDB
from loggers import logger
from src.utils import check_verification_admin, get_message_customers

router_admin = Router()


class AddCustomer(StatesGroup):
    """ Класс представляет группу состояний для операций с каталогом. """
    customer_id = State()


@router_admin.message(F.text == '\U00002705 Отмена')
async def catalog_cancel(message: types.Message, state: FSMContext) -> None:
    """
    Отмена операции и возврат к меню администратора.

    :param message: Объект сообщения.
    :param state: Контекст состояния.
    :return: None
    """
    if not await check_verification_admin(message):
        return
    await state.clear()
    await message.answer('\U0001F4CC Меню администратора', reply_markup=await get_admin_keyboard())


@router_admin.message(F.text == '\U0001F4BC Админка')
async def admin_menu(message: types.Message) -> None:
    """
    Функция перехода к меню администратора.

    :param message: Объект сообщения.
    :return: None
    """
    if not await check_verification_admin(message):
        return
    await message.answer(
        text='\U0001F4BC Меню администратора\nВыберите пункт меню ↘',
        reply_markup=await get_admin_keyboard()
    )


@router_admin.message(F.text == '\U0001F4DD Добавить пользователя')
async def customer_input(message: types.Message, state: FSMContext) -> None:
    """
    Запуск состояния добавления пользователя.

    :param message: Объект сообщения.
    :param state: Контекст состояния.
    :return: None
    """
    if not await check_verification_admin(message):
        return
    await state.set_state(AddCustomer.customer_id)
    await message.answer(
        text='\U0001F4CC Введите ID пользователя\n'
             '\U00002757 Как узнать свой ID: отправить боту сообщение - id.\n\n'
             '\U00002705 Для возврата к меню, нажмите кнопку - \U00002705 Отмена',
        reply_markup=await get_cancel_admin_kb()
    )


@router_admin.message(AddCustomer.customer_id)
async def check_input(message: types.Message, state: FSMContext) -> None:
    """
    Обработка введённого ID и добавление его в БД.

    :param message: Объект сообщения.
    :param state: Контекст состояния.
    :return: None
    """
    customer_id = message.text
    try:
        if customer_id and customer_id.isdigit() and len(customer_id) < 17:
            db = UserDB()
            result = await db.add_customer(customer_id=customer_id)
            if result:
                await state.clear()
                await message.answer(
                    text=f'\U00002705 Пользователь с ID {customer_id} успешно добавлен!',
                    reply_markup=await get_admin_keyboard()
                )
            else:
                await state.clear()
                await message.answer(
                    text=f'\U00002757 Пользователь с ID {customer_id} уже существует!',
                    reply_markup=await get_admin_keyboard()
                )
        else:
            await message.answer('\U00002757 Ошибка! Повторите ввод\n'
                                 '\U00002705 Для возврата к меню, нажмите кнопку - \U00002705 Отмена')
            return
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)


@router_admin.message(F.text == '\U0001F4CB Посмотреть список пользователей')
async def get_users_display(message: types.Message):
    if not await check_verification_admin(message):
        return
    db = UserDB()
    list_users_info = await db.get_all_customers_info()
    if list_users_info:
        for user_info in list_users_info:
            text = await get_message_customers(user_info=user_info)
            await message.answer(text=text, reply_markup=await get_inline_kb_customers(user_info=user_info))
    else:
        await message.answer(text='Пользователей нет в базе')


@router_admin.callback_query(CustomersCallBack.filter(F.service.in_({'activate', 'deactivate'})))
async def change_status_user(query: CallbackQuery, callback_data: CustomersCallBack) -> None:
    status = True if callback_data.service == 'activate' else False
    db = UserDB()
    user_info = await db.check_customer_status(customer_id=callback_data.customer_id, status=status)
    text = await get_message_customers(user_info=user_info)
    await query.message.edit_text(text=text, reply_markup=await get_inline_kb_customers(user_info=user_info))


@router_admin.callback_query(CustomersCallBack.filter(F.service == 'delete'))
async def delete_user(query: CallbackQuery, callback_data: CustomersCallBack) -> None:
    await query.message.edit_reply_markup(
        query.id,
        reply_markup=await get_inline_kb_confirm(customer_id=callback_data.customer_id)
    )


@router_admin.callback_query(ConfirmCallBack.filter(F.choice.in_({'Y', 'N'})))
async def confirm_action(query: CallbackQuery, callback_data: ConfirmCallBack):
    db = UserDB()
    if callback_data.choice == 'Y':
        await db.delete_customer(customer_id=callback_data.customer_id)
        await query.message.delete()
    else:
        user_info = await db.get_customer_info(customer_id=callback_data.customer_id)
        await query.message.edit_reply_markup(
            query.id,
            reply_markup=await get_inline_kb_customers(user_info=user_info)
        )
