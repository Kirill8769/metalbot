import os
import sys
import time
from datetime import datetime
from random import randint

import pandas as pd
from aiogram import types

from config import PATH_PROJECT, admin_list, prices_list, user_list, wisdom_day
from data.instructions import instructions_dict
from data.regulations import regulations_dict
from data.wisdoms import wisdoms_dict
from loggers import logger
from src.parser_handler import Parser


def price_parsing() -> None:
    """
    Сбор всей необходимой для работы бота информации и её запись в глобальную переменную.

    :return: None
    """
    try:
        parser = Parser()
        logger.info('[+] Парсер начал сбор данных')

        error_count = 0
        while True:
            parser.get_soup()
            parser.get_queries()
            result = parser.get_platinum_palladium_price()
            if error_count >= 3:
                logger.info('[+] Данные Pt Pd не были собраны..')
                parser.prices['platinum'] = 1049
                parser.prices['palladium'] = 971
                logger.info(
                    f"[+] Цены проставлены вручную Pt:{parser.prices['platinum']} , Pd:{parser.prices['palladium']}"
                )
                break
            if not result:
                logger.info('[+] Ошибка сбора данных Pt Pd, спим 5 секунд и начинаем заново')
                error_count += 1
                time.sleep(5)
                continue
            break

        parser.get_rhodium_spot()
        
        # parser.get_currency_price('USD')
        parser.get_cars_metal()
        parser.prices['currency_price'] = float(parser.cars_metal['usd'])

        parser.metal_price_calculation()
        logger.info('[+] Парсер отработал успешно')

        prices_list.clear()
        prices_list.append(parser.prices)
        prices_list.append(parser.cars_metal)
        random_wisdom = wisdoms_dict[randint(1, len(wisdoms_dict))]
        wisdom_day.append(random_wisdom)
        logger.info(f'[+] Мудрость дня получена: {wisdom_day}')
        logger.info(f'[+] Собранные данные записаны и готовы к использованию\n{prices_list}')
    except Exception as ex:
        logger.info('[+] Ошибка парсера')
        logger.debug(f"{ex.__class__.__name__}: {ex}")


async def get_info_xlsm(parameters: list) -> list:
    """
    Функция ищет записи в каталоге по переданным размерам катализатора и возвращает результат поиска.

    :param parameters: Список с размерами катализатора.
    :return: Отфильтрованный список с данными катализаторов из каталога.
    """
    catalog_path = os.path.join(PATH_PROJECT, 'data', 'katalog.xlsm')
    data = pd.read_excel(catalog_path, sheet_name=1)
    result = []
    height = parameters[0]
    width = parameters[1]
    weight = parameters[2]
    if len(parameters) == 4:
        length = parameters[3]
    else:
        length = None
    for row in data.values[3:]:
        if (
                (height - 0.5) <= row[7] <= (height + 0.5) and
                (width - 0.5) <= row[8] <= (width + 0.5) and
                (weight - weight * 0.1) <= row[10] <= (weight + weight * 0.1) and
                ((length - 0.5) <= row[9] <= (length + 0.5) if length is not None else True)
        ):
            result.append(row)
    return result


async def get_validate_input(input_text: str) -> list:
    """
    Проверяет корректность введённых данных

    :param input_text: Текст для проверки
    :return: True если проверка удовлетворила требованиям, иначе False
    """
    result = []
    try:
        clear_input_text = input_text.strip().replace(',', '.')
        values = list(map(float, clear_input_text.split()))
        if len(values) in [3, 4]:
            result = values
    except ValueError:
        logger.error(f'Переданный текст: {input_text}')
    finally:
        return result


async def get_message_quotes(rate: str = '100') -> str:
    """
    Функция формирует сообщение на основании переданного процента.

    :param rate: Процент для расчёта.
    :return: Сгенерированное сообщение.
    """
    dict_quotes = prices_list[0]
    message = (f"USD: {dict_quotes['currency_price']} руб\n"
               f"Биржа Pt: {dict_quotes['platinum']} | Pd: {dict_quotes['palladium']} | Rh: {dict_quotes['rhodium']}")
    try:
        if isinstance(rate, str):
            for item in rate.split(','):
                int_item = int(item)
                round_rate = round(int_item / 100, 2)
                message += f"""\n\nПроцент: {item}%
Платина: {int(dict_quotes['pt_ru'] * round_rate)} руб/гр
Палладий: {int(dict_quotes['pd_ru'] * round_rate)} руб/гр
Родий: {int(dict_quotes['rh_ru'] * round_rate)} руб/гр"""
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}")
        message += '\n\nОшибка расчёта котировок'
    finally:
        return message


async def check_verification_user(message: types.Message):
    """
    Проверяет, верифицирован ли пользователь.

    :param message: Объект сообщения.
    :return: True, если пользователь верифицирован, иначе False.
    """
    user_id = str(message.from_user.id)
    if user_id in user_list:
        return True
    await message.delete()
    await message.answer(text='Доступ запрещён')
    return False


async def check_verification_admin(message: types.Message | types.CallbackQuery):
    """
    Верификация админа.

    :param message: Объект сообщения.
    :return: True, если админ верифицирован, иначе False.
    """
    admin_id = str(message.from_user.id)
    if admin_id in admin_list:
        return True
    return False


async def get_message_customers(user_info: dict) -> str:
    """
    Функция собирает сообщение для инлайн кнопки.

    :param user_info: Информация о пользователе.
    :return: Сформированное сообщение
    """
    message = 'Ошибка сбора информации пользователя'
    try:
        first_name = user_info['first_name'] if user_info['first_name'] is not None else ''
        last_name = user_info['last_name'] if user_info['last_name'] is not None else ''
        status = 'Активен' if user_info['status'] else 'Заблокирован'
        is_admin = 'Да' if user_info['is_admin'] else 'Нет'
        message = (f"ID: {user_info['customer_id']}\n"
                   f"Логин: {user_info['username']}\n"
                   f"ФИО: {last_name} {first_name}\n"
                   f"Статус: {status}\n"
                   f"Администратор: {is_admin}")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}")
    return message


async def get_instruction(page: str) -> str:
    """
    Функция получает из файла запрашиваемую инструкцию и возвращает её пользователю.

    :param page: page из инлайн кнопки, должен быть таким же как название инструкции в файле.
    :return: Запрашиваемая инструкция.
    """
    message = 'Произошла ошибка при запросе инструкции, обратитесь к администратору.'
    try:
        message = instructions_dict[page]
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}")
    return message


async def get_regulation(page: str) -> str:
    """
    Функция получает из файла запрашиваемый регламент и возвращает его пользователю.

    :param page: page из инлайн кнопки, должен быть таким же как название регламента в файле.
    :return: Запрашиваемый регламент.
    """
    message = 'Произошла ошибка при запросе регламента, обратитесь к администратору.'
    try:
        message = regulations_dict[page]
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}")
    return message


async def round_to(value: int | float, rate: int) -> int:
    """
    Функция делает округление числа.

    :param value: Число.
    :param rate: Значение до которого округляем.
    :return: Возвращаем результат округления.
    """
    return round(value / rate) * rate


async def get_catalyst_prices(category: str) -> str:
    """
    Функция считает цены на катализаторы опираясь на выбранную категорию.

    :param category: Категория из инлайн кнопки, для расчета стоимости .
    :return: Сформированное сообщение.
    """
    message = 'Произошла ошибка при расчёте стоимости, обратитесь к администратору.'
    try:
        dict_price = prices_list[1]
        format_date = datetime.strptime(dict_price['date'], '%Y-%m-%d').strftime('%d.%m.%Y')
        coefficient = 1.25 if category == 'go' else 1
        name = 'ГО' if category == 'go' else 'VIP' if category == 'vip' else 'Несуществующая категория'
        message = (f"Дата: {format_date}\n\n"
                   f"Категория: {name}\n"
                   f"Импорт: {await round_to(int(dict_price['metforvip']) * coefficient, 50)} руб/кг\n"
                   f"БМВ: {await round_to(int(dict_price['metbmwvip']) * coefficient, 50)} руб/кг\n"
                   f"Лексус: {await round_to(int(dict_price['metlexvip']) * coefficient, 50)} руб/кг\n"
                   f"Инфинити: {await round_to(int(dict_price['metinfvip']) * coefficient, 50)} руб/кг\n"
                   f"Ланос: {await round_to(int(dict_price['metlanosvip']) * coefficient, 50)} руб/кг\n"
                   f"Россия: {await round_to(int(dict_price['metrusvip']) * coefficient, 50)} руб/кг\n"
                   f"Коммерция: {await round_to(int(dict_price['metcomvip']) * coefficient, 50)} руб/кг")
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}")
    return message


def restart_program():
    """ Функция перезапускает программу """
    logger.warning("Перезапускаем сервис")
    try:
        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception as ex:
        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
