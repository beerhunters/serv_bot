import logging
import ssl
from datetime import datetime

import aiohttp

from config import RUBITIME_API_KEY

url_create = "https://rubitime.ru/api2/create-record"
url_update = "https://rubitime.ru/api2/update-record"
url_get = "https://rubitime.ru/api2/get-record"
url_remove = "https://rubitime.ru/api2/remove-record"


# 'service_id' = > '', // id услуги
#     Большая Переговорная (на 10-12 человек) - 47900
#     Малая Переговорная (на 10-12 человек) - 47901
#     Опенспейс на день - 49414
#     Тестовый день - 47890
#     Амфитеатр (на 30-35 человек) - 50764


async def rubitime(method, extra_params):
    base_url = "https://rubitime.ru/api2/"

    # Получаем текущую дату и время в формате "ГГГГ-ММ-ДД ЧЧ:ММ:СС"
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Выбор URL и параметров на основе метода
    if method == "get_record":
        url = f"{base_url}get-record"
        # 'id' = > 79379, //
        params = {
            **extra_params,
        }
    elif method == "create_record":
        url = f"{base_url}create-record"
        # 'service_id' = > '', // id услуги
        #     Большая Переговорная (на 10-12 человек) - 47900
        #     Опенспейс на день - 49414
        #     Амфитеатр (на 30-35 человек) - 50764
        # 'name' = > 'Иванов Иван Иванович', // ФИО
        # 'email' = > 'test@test.ru', // email
        # 'phone' = > '+70000000000', // телефон
        # 'record' = > '2020-01-18 20:00', // на которое записан клиент
        params = {
            "branch_id": 12595,
            "cooperator_id": 25786,
            "created_at": current_datetime,
            "status": 0,
            "source": "Telegram",
            **extra_params,
        }
    elif method == "update_record":
        url = f"{base_url}update-record"
        params = {
            **extra_params,  # 'id'
        }
    elif method == "remove_record":
        url = f"{base_url}remove-record"
        params = {
            **extra_params,  # 'id'
        }
    else:
        logging.error("Неизвестный метод:", method)
        return

    params["rk"] = RUBITIME_API_KEY

    # Отключаем SSL-проверку
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Выполнение асинхронного запроса
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=params, ssl=ssl_context) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("status") == "ok":
                    if method == "create_record":
                        record_id = data.get("data", {}).get("id")
                        # print("ID записи:", record_id)
                        return record_id
                    else:
                        return
                else:
                    logging.error("Ошибка в ответе:", data.get("message"))
            else:
                logging.error("Ошибка:", response.status, await response.text())


# {
# 'status': 'ok',
# 'message': 'Record 5256040 found',
# 'data': {
# 'id': 5256040,
# 'parent_record': None,
# 'whom': 1,
# 'created_at': '2024-11-12 12:17:54',
# 'updated_at': None,
# 'record': '2024-11-13 10:00:00',
# 'name': 'Иван Иванов',
# 'price': '0',
# 'phone': '79643865768',
# 'email': 'Qwerty@qwerty.com',
# 'comment': '',
# 'status': 0,
# 'status_title': 'Записан',
# 'cooperator_id': 25786,
# 'cooperator_title': 'Коворкинг Parta',
# 'branch_id': 12595,
# 'branch_title': 'Санкт-Петербург, Малый проспект В. О., 55к1',
# 'service_id': 47900,
# 'service_title': 'Большая Переговорная (на 10-12 человек)',
# 'url': 'https://parta.rubitime.ru/widget/card/7859db6891cce4b5024c63c39e047bf9ebac5454b82453d186e0af86d0b11502',
# 'coupon': None,
# 'coupon_discount': None,
# 'source': 'Telegram',
# 'cancelReason': None,
# 'duration': '60',
# 'prepayment': None,
# 'prepayment_date': None,
# 'prepayment_url': None,
# 'reminder': None,
# 'custom_field1': None, }
# }
