import json
import os
from typing import Any

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from loggers import logger


class Parser:
    """ Класс предназначен для парсинга данных о ценах на драгоценные металлы и валюту. """

    def __init__(self) -> None:
        load_dotenv()
        self.json_soup: Any = ''
        self.queries: list[dict] = []
        self.prices = {
            'rhodium_bid': 0.0,
            'rhodium_ask': 0.0,
            'platinum': 0.0,
            'palladium': 0.0,
            'currency_price': 0.0,
        }
        self.__cars_metal_url = os.getenv('CARS_METAL_URL')
        self.cars_metal = {}

    def get_soup(self) -> None:
        """
        Получает JSON-структуру страницы.

        :return: None
        """
        url = 'https://www.kitco.com/price/precious-metals'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                json_div = soup.find('script', id='__NEXT_DATA__')
                if json_div:
                    json_content = json_div.string
                    self.json_soup = json.loads(json_content)
                    logger.info('[+] Данные с сайта kitko получены')
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)

    def get_queries(self) -> None:
        """
        Получает запросы для получения цен на металлы.

        :return: None
        """
        try:
            if self.json_soup:
                self.queries = self.json_soup['props']['pageProps']['dehydratedState']['queries']
                logger.info('[+] Данные с сайта kitko отфильтрованы')
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)

    def get_rhodium_spot(self) -> None:
        """
        Получает текущие цены на родий.

        :return: None
        """
        try:
            for data in self.queries:
                query_hash = data.get('queryHash', '')
                if 'USD' in query_hash and 'allMetalsQuote' in query_hash:
                    self.prices['rhodium_bid'] = data['state']['data']['rhodium']['results'][0]['bid']
                    self.prices['rhodium_ask'] = data['state']['data']['rhodium']['results'][0]['ask']
                    self.prices['rhodium'] = int((self.prices['rhodium_bid'] + self.prices['rhodium_ask']) / 2)
                    logger.info('[+] Стоимость Родия получена')
                    break
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)

    def get_platinum_palladium_price(self) -> bool:
        """
        Получает текущие цены на платину и палладий.

        :return: Если данные собраны успешно, возвращает True, иначе False.
        """
        status = True
        try:
            for data in self.queries:
                if 'londonFix' in data.get('queryKey', ''):
                    results = data['state']['data']['londonFixUSD']['results']

                    for item in results:
                        self.prices['platinum'] = item.get('platinumPM', 0)
                        if self.prices['platinum']:
                            logger.info('[+] Стоимость Платины получены PM')
                            break
                        else:
                            self.prices['platinum'] = item.get('platinumAM', 0)
                        if self.prices['platinum']:
                            logger.info('[+] Стоимость Платины получены AM')
                            break
                    else:
                        status = False

                    for item in results:
                        self.prices['palladium'] = item.get('palladiumPM', 0)
                        if self.prices['palladium']:
                            logger.info('[+] Стоимость Палладия получены PM')
                            break
                        else:
                            self.prices['palladium'] = item.get('palladiumAM', 0)
                        if self.prices['palladium']:
                            logger.info('[+] Стоимость Палладия получены AM')
                            break
                    else:
                        status = False
                    break
            else:
                status = False
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
            status = False
        finally:
            return status

    def get_currency_price(self, currency: str) -> None:
        """
        Получает текущий курс валюты.

        :param currency: Валюта, курс которой требуется получить.
        :return: None
        """
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                currency_info = response.json()
                self.prices['currency_price'] = round(currency_info["Valute"][currency]["Value"], 2)
                logger.info('[+] Стоимость валюты получена')
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)

    def get_cars_metal(self) -> None:
        """
        Получает данные по ценам катализаторов.

        :return: None
        """
        cookies = {'beget': 'begetok'}
        try:
            response = requests.get(url=self.__cars_metal_url, cookies=cookies)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                rows = soup.find_all('tr')
                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) == 2:
                        key = columns[0].text.strip()
                        value = columns[1].text.strip()
                        self.cars_metal[key] = value
                else:
                    logger.info('[+] Данные по ценам катализаторов собраны')
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)

    def metal_price_calculation(self) -> None:
        """
        Пересчитывает вес металлов из унции в граммы и цену в рубли.

        :return: None
        """
        try:
            pt = self.prices['platinum']
            pd = self.prices['palladium']
            rh = round((self.prices['rhodium_bid'] + self.prices['rhodium_ask']) / 2, 2)
            self.prices['pt_ru'] = round(pt / 31.1035 * self.prices['currency_price'], 2)
            self.prices['pd_ru'] = round(pd / 31.1035 * self.prices['currency_price'], 2)
            self.prices['rh_ru'] = round(rh / 31.1035 * self.prices['currency_price'], 2)
            logger.info('[+] Цены на металлы пересчитаны в рубли')
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
