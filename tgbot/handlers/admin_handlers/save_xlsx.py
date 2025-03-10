from datetime import datetime
import os
from openpyxl.workbook import Workbook
from sqlalchemy.orm import class_mapper


async def format_time_spent(seconds):
    if seconds is None:
        return "Нет данных"
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24

    hours = hours % 24  # Остаток после деления на дни
    minutes = minutes % 60  # Остаток после деления на часы

    if days > 0:
        return f"{days} д. {hours} ч. {minutes} мин."
    elif hours > 0:
        return f"{hours} ч. {minutes} мин."
    else:
        return f"{minutes} мин."


async def save_report_to_excel(model, list_name, items, first_day=None):
    if first_day is not None:
        # Преобразуем первый день в объект datetime, чтобы извлечь название месяца и год
        first_day_date = datetime.strptime(first_day, "%d.%m.%Y")
        # Название файла по формату месяц+год
        file_name = f"{model.__tablename__}_{first_day_date.strftime('%B_%Y')}.xlsx"
    else:
        file_name = f"{model.__tablename__}.xlsx"

    # Создаем книгу и лист
    wb = Workbook()
    ws = wb.active
    ws.title = list_name

    # Получаем названия колонок динамически из модели
    column_names = [column.key for column in class_mapper(model).columns]

    # Извлекаем читаемые заголовки из модели
    column_headers = getattr(model, "__labels__", {})
    readable_column_names = [column_headers.get(col, col) for col in column_names]

    # Добавляем заголовки колонок
    ws.append(readable_column_names)

    # Заполняем данные
    for item in items:
        row_data = []
        for column in column_names:
            if column == "user_tg_id":
                value = item.user.name if item.user else "Нет данных"
            elif column == "admin_id":
                value = item.admin.tg_username if item.admin else "Нет данных"
            elif column == "tariff_id":
                value = item.tariff.name if item.tariff else "Нет данных"
            elif column == "promocode_id":
                value = item.promocode.name if item.promocode else "Нет данных"
            else:
                value = getattr(item, column)
                if column == "state":
                    value = "Завершен" if value else "В работе"
                if column == "photo_id" or column == "finish_photo_id":
                    value = "Есть фото" if value else "Без фото"
                if column == "paid":
                    value = "Оплачен" if value else "Не оплачен"
                if column == "time_spent":
                    value = await format_time_spent(value)
                if column == "removed":
                    value = "Удален" if value else "-"
                if column == "confirmed":
                    value = "Подтвержден" if value else "Не подтвержден"
            row_data.append(value)
        ws.append(row_data)

    # Сохраняем файл в текущей директории
    file_path = os.path.join(os.getcwd(), file_name)
    wb.save(file_path)

    return file_path


import csv
import os
from datetime import datetime


async def save_report_to_csv(model, list_name, items, first_day=None):
    if first_day is not None:
        # Преобразуем первый день в объект datetime, чтобы извлечь название месяца и год
        first_day_date = datetime.strptime(first_day, "%d.%m.%Y")
        # Название файла по формату месяц+год
        file_name = f"{model.__tablename__}_{first_day_date.strftime('%B_%Y')}.csv"
    else:
        file_name = f"{model.__tablename__}.csv"

    # Путь для сохранения файла
    file_path = os.path.join(os.getcwd(), file_name)

    # Получаем названия колонок напрямую из модели (без читаемых заголовков)
    column_names = [column.key for column in class_mapper(model).columns]

    # Записываем данные в CSV
    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Записываем заголовки как есть (имена полей модели)
        writer.writerow(column_names)

        # Заполняем данные без дополнительного форматирования
        for item in items:
            row_data = []
            for column in column_names:
                value = getattr(item, column)
                if isinstance(value, datetime):
                    value = value.isoformat() if value else ""  # Даты в формате ISO
                elif value is None:
                    value = ""  # NULL заменяем на пустую строку
                row_data.append(value)
            writer.writerow(row_data)

    return file_path
