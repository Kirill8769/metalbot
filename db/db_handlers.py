import os

import asyncpg
from aiogram import types
from asyncpg import exceptions
from dotenv import load_dotenv

from config import admin_list, user_list
from loggers import logger


class UserDB:
    """
    Класс для взаимодействия с базой данных.
    """

    def __init__(self) -> None:
        load_dotenv()
        self._connection = None
        self.__admin = os.getenv("ADMIN")
        self.__host = os.getenv("HOST")
        self.__database = os.getenv("DATABASE")
        self.__user = os.getenv("USERNAME")
        self.__password = os.getenv("PASSWORD")
        logger.info("Database is activated")

    async def connect(self) -> None:
        """
        Устанавливает соединение с базой данных.
        """
        try:
            self._connection = await asyncpg.connect(
                host=self.__host, database=self.__database, user=self.__user, password=self.__password
            )
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)

    async def create_tables(self) -> None:
        """
        Создает таблицу в базе данных, если она не существует.
        """
        await self.connect()
        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS customers(
                ID SERIAL PRIMARY KEY,
                CUSTOMER_ID VARCHAR(16) UNIQUE NOT NULL,
                FIRST_NAME VARCHAR(256),
                LAST_NAME VARCHAR(256),
                USERNAME VARCHAR(256),
                IS_ADMIN BOOLEAN DEFAULT FALSE,
                STATUS BOOLEAN DEFAULT TRUE
            )
                                """
        )
        await self._connection.close()

    async def add_customer(self, customer_id: str) -> bool:
        """
        Добавляет нового пользователя в БД.

        :param customer_id: id пользователя
        :return: True, если пользователь добавлен, иначе False
        """
        status = False
        try:
            await self.connect()
            await self._connection.execute(
                "INSERT INTO customers (CUSTOMER_ID) VALUES ($1)", customer_id,
            )
            await self._connection.close()
            status = True
            await self.update_customers_lists()
            logger.info(f'Пользователь с ID {customer_id} успешно добавлен!')
        except exceptions.UniqueViolationError:
            logger.debug(f"Пользователь с ID {customer_id} уже существует!")
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            return status

    async def update_customer(self, message: types.Message) -> None:
        """
        Обновляет информацию пользователя.

        :param message: Объект сообщения.
        :return: None
        """
        await self.connect()
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        username = message.from_user.username
        customer_id = str(message.from_user.id)
        try:
            await self._connection.execute(
                "UPDATE customers SET FIRST_NAME = $1, LAST_NAME = $2, USERNAME = $3 WHERE CUSTOMER_ID = $4",
                first_name, last_name, username, customer_id
            )
            await self._connection.close()
            await self.update_customers_lists()
            logger.info(f'Данные пользователя {customer_id} успешно обновлены!')
        except Exception as ex:
            logger.error(f"Данные пользователя {customer_id} не были обновлены\n{ex.__class__.__name__}: {ex}")

    async def get_active_customers(self) -> list:
        """
        Получает список активных пользователей.

        :return: Список активных пользователей.
        """
        await self.connect()
        result = await self._connection.fetch('SELECT * FROM customers WHERE STATUS = $1', True)
        result_list = [item['customer_id'] for item in result] if result else []
        await self._connection.close()
        return result_list

    async def get_active_admins(self) -> list:
        """
        Получает список активных админов.

        :return: Список активных админов.
        """
        await self.connect()
        result = await self._connection.fetch(
            'SELECT * FROM customers WHERE STATUS = $1 AND IS_ADMIN = $2',
            True, True
        )
        result_list = [item['customer_id'] for item in result] if result else []
        await self._connection.close()
        return result_list

    async def get_customer_info(self, customer_id: str) -> dict:
        """
        Получает информацию о пользователе.

        :param customer_id: id пользователя.
        :return: Словарь с информацией пользователя.
        """
        await self.connect()
        user_info = await self._connection.fetchrow('SELECT * FROM customers WHERE CUSTOMER_ID = $1', customer_id)
        await self._connection.close()
        return user_info

    async def update_customers_lists(self) -> None:
        """
        Обновляет глобальные переменные активных пользователей и админов.

        :return: None
        """
        admin_list.clear()
        admin_list.extend(await self.get_active_admins())
        user_list.clear()
        user_list.extend(await self.get_active_customers())

    async def check_customer_status(self, customer_id: str, status: bool) -> dict:
        """
        Обновляет статус пользователя и возвращает обновлённую информацию.

        :param customer_id: id пользователя.
        :param status: Статус, для передачи в БД.
        :return: Словарь с информацией пользователя.
        """
        await self.connect()
        user_info = await self._connection.fetchrow(
            "UPDATE customers SET STATUS = $1 WHERE CUSTOMER_ID = $2 RETURNING *",
            status, customer_id
        )
        await self._connection.close()
        await self.update_customers_lists()
        return user_info

    async def get_all_customers_info(self) -> list:
        """
        Получает список информации по всем пользователям.

        :return: Список словарей с информацией по всем пользователям.
        """
        await self.connect()
        users_info = await self._connection.fetch("SELECT * FROM customers WHERE CUSTOMER_ID <> $1", self.__admin)
        await self._connection.close()
        return users_info

    async def delete_customer(self, customer_id: str) -> None:
        """
        Удаляет пользователя из БД.

        :param customer_id: id пользователя.
        :return: None
        """
        await self.connect()
        await self._connection.execute('DELETE FROM customers WHERE CUSTOMER_ID = $1', customer_id)
        await self._connection.close()
        await self.update_customers_lists()
        logger.info(f'Удалён пользователь - {customer_id}')
