# import shutil
#
# import aiofiles
# from aiogram import F, Bot, Router
# import cups
# import asyncio
# from aiogram.enums import ContentType
# from aiogram.types import Message, CallbackQuery
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from pathlib import Path
#
# from fluent.runtime import FluentLocalization
# from yookassa import Payment
# import subprocess
# from PyPDF2 import PdfReader
#
# from tgbot.database.requests import get_adjustments
# import tgbot.keyboards.user_kb.keyboards as kb
# from tgbot.handlers.user_handlers.payment import create_payment, cancel_payment_handler
#
# # from app.database.requests import get_adjustments
# # import app.user_kb.keyboards as kb
# # from app.user_handlers.payment import create_payment, cancel_payment_handler
#
# from concurrent.futures import ThreadPoolExecutor
#
# from tgbot.filters import IsUserFilter
#
# printer_router = Router()
# executor = ThreadPoolExecutor(max_workers=5)  # Определяем пул потоков
# # Применяем фильтр для всех хэндлеров на уровне роутера
# printer_router.message.filter(IsUserFilter(is_user=True))
# printer_router.callback_query.filter(IsUserFilter(is_user=True))
#
#
# class PrinterManager:
#     def __init__(self):
#         self.conn = cups.Connection()
#
#     # def get_printers(self):
#     #     return self.conn.getPrinters()
#     def get_printers(self) -> dict[str, str]:
#         """Возвращает словарь уникальных принтеров, исключая дубли с цифрами в конце."""
#         all_printers = self.conn.getPrinters()  # dict[str, dict]
#         unique_printers = {}
#         seen_base_names = set()
#
#         for printer_name, printer_attrs in all_printers.items():
#             import re
#
#             # Удаляем цифры в конце имени
#             base_name = re.sub(r"_?\d+$", "", printer_name).strip()
#
#             # Если базовое имя ещё не встречалось, добавляем принтер
#             if base_name not in seen_base_names:
#                 unique_printers[printer_name] = printer_attrs
#                 seen_base_names.add(base_name)
#             # Если это дубликат с цифрой, пропускаем его
#             # (оставляем первый встреченный вариант, обычно без цифры)
#
#         return unique_printers
#
#     def print_file(self, file_path, printer_name):
#         if not Path(file_path).is_file():
#             raise FileNotFoundError(f"Файл {file_path} не найден")
#         printer_name = printer_name.replace(" ", "_")
#         job_id = self.conn.printFile(printer_name, file_path, "Print Job", {})
#         return job_id
#
#     def get_job_attributes(self, job_id):
#         return self.conn.getJobAttributes(job_id)
#
#
# class Printer(StatesGroup):
#     document = State()
#     printer_selection = State()
#     payment = State()
#     status_payment = State()
#
#
# # libre_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"  # 'libreoffice'
# # libre_path = "/usr/bin/libreoffice"
#
#
# # async def convert_to_pdf(input_file, output_file):
# #     # process = subprocess.run([libre_path, '--headless', '--convert-to', 'pdf', '--outdir', '/tmp', input_file],
# #     #                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# #     process = subprocess.run(
# #         [
# #             "libreoffice",
# #             "--headless",
# #             "--convert-to",
# #             "pdf",
# #             "--outdir",
# #             "/tmp",
# #             input_file,
# #         ],
# #         stdout=subprocess.PIPE,
# #         stderr=subprocess.PIPE,
# #     )
# #     if process.returncode != 0:
# #         raise Exception(f"Ошибка конвертации файла в PDF: {process.stderr.decode()}")
# #     if not Path(output_file).is_file():
# #         raise FileNotFoundError(f"Файл {output_file} не найден после конвертации")
# #     return output_file
# async def convert_to_pdf(input_file, output_file):
#     libre_path = shutil.which("libreoffice")
#     if not libre_path:
#         raise Exception(
#             "LibreOffice не установлен на сервере. Печать .docx файлов временно недоступна."
#         )
#
#     process = subprocess.run(
#         [
#             libre_path,
#             "--headless",
#             "--convert-to",
#             "pdf",
#             "--outdir",
#             "/tmp",
#             input_file,
#         ],
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#     )
#     if process.returncode != 0:
#         raise Exception(f"Ошибка конвертации файла в PDF: {process.stderr.decode()}")
#     if not Path(output_file).is_file():
#         raise FileNotFoundError(f"Файл {output_file} не найден после конвертации")
#     return output_file
#
#
# async def count_pdf_pages(pdf_file_path):
#     try:
#         with open(pdf_file_path, "rb") as f:
#             pdf = PdfReader(f)
#             return len(pdf.pages)
#     except Exception as e:
#         raise Exception(f"Ошибка при подсчете страниц PDF: {e}")
#
#
# async def printing_cost(message, pdf_file_path):
#     adjustments = await get_adjustments()
#     printing_info = adjustments.get("printing_available")
#     # try:
#     page_count = await count_pdf_pages(pdf_file_path)
#     print_price = printing_info["value"]
#     total_cost = page_count * print_price
#     return page_count, total_cost
#     # except Exception as e:
#     #     await message.reply(f"Произошла ошибка при подсчете страниц PDF: {e}")
#     #     return
#
#
# printer_manager = PrinterManager()
#
#
# async def get_printers():
#     return printer_manager.get_printers()
#
#
# async def print_file(file_path, printer_name):
#     return printer_manager.print_file(file_path, printer_name)
#
#
# async def check_print_status(
#     message: Message,
#     chat_id: int,
#     job_id: int,
#     printer_name: str,
#     l10n: FluentLocalization,
# ):
#     while True:
#         job = printer_manager.get_job_attributes(job_id)
#         state = job.get("job-state")
#         if state == 9:  # 9 означает, что печать завершена
#             await message.bot.send_message(
#                 chat_id,
#                 f"Ваш документ был успешно распечатан на принтере: {printer_name.replace('_', ' ')}",
#                 reply_markup=await kb.user_main(l10n=l10n),
#             )
#             break
#         elif state in {5, 6, 7, 8}:  # 5-8 означают, что печать в процессе
#             await asyncio.sleep(5)
#         else:
#             await message.bot.send_message(
#                 chat_id,
#                 f"Произошла ошибка при печати на принтере: {printer_name.replace('_', ' ')}",
#                 reply_markup=await kb.user_main(l10n=l10n),
#             )
#             break
#
#
# @printer_router.callback_query(F.data == "print_doc")
# async def start_printing(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ):
#     adjustments = await get_adjustments()
#     printing_info = adjustments.get("printing_available")
#
#     if not printing_info["state"]:
#         await callback.answer("Функция печати сейчас недоступна.", show_alert=True)
#         return
#
#     printers = await get_printers()
#     # print(printers)
#     if not printers:
#         await callback.message.edit_text(
#             "Доступных принтеров нет.", reply_markup=await kb.user_main(l10n=l10n)
#         )
#         return
#
#     print_price = printing_info["value"]
#     await callback.message.edit_text(
#         f"Выберите принтер для печати\n" f"(стоимость - {print_price} руб/страница):",
#         reply_markup=await kb.printers_list(printers, l10n=l10n),
#     )
#     await state.set_state(Printer.printer_selection)
#
#
# @printer_router.callback_query(
#     F.data.startswith("select_printer"), Printer.printer_selection
# )
# async def select_printer(callback: CallbackQuery, state: FSMContext):
#     await callback.answer()
#     printer_name = callback.data.split(":")[1]
#     await state.update_data(printer_name=printer_name)
#     printer_name = printer_name.replace("_", " ")
#     await callback.message.edit_text(
#         f"Вы выбрали принтер: {printer_name}. Отправьте документ для печати."
#     )
#     await state.set_state(Printer.document)
#
#
# # @printer_router.message(F.content_type == ContentType.DOCUMENT, Printer.document)
# # async def print_docs_photo(
# #     message: Message, bot: Bot, state: FSMContext, l10n: FluentLocalization
# # ):
# #     adjustments = await get_adjustments()
# #     printing_info = adjustments.get("printing_available")
# #     free_printing_info = adjustments.get("free_printing_available")
# #
# #     data = await state.get_data()
# #     printer_name = data.get("printer_name")
# #
# #     document = message.document
# #     file_info = await bot.get_file(document.file_id)
# #     file_path = file_info.file_path
# #     downloaded_file = await bot.download_file(file_path)
# #     temp_file_path = f"/tmp/{document.file_name}"
# #     pdf_file_path = f"/tmp/{Path(document.file_name).stem}.pdf"
# #
# #     async with aiofiles.open(temp_file_path, "wb") as new_file:
# #         await new_file.write(downloaded_file.read())
# #
# #     if not Path(temp_file_path).is_file():
# #         await message.reply("Произошла ошибка при сохранении файла.")
# #         return
# #
# #     # try:
# #     if not temp_file_path.endswith(".pdf"):
# #         await convert_to_pdf(temp_file_path, pdf_file_path)
# #     else:
# #         pdf_file_path = temp_file_path
# #
# #     if free_printing_info["state"] or printing_info["value"] == 0:
# #         job_id = await print_file(pdf_file_path, printer_name)
# #         await state.update_data(job_id=job_id)
# #         await message.reply(
# #             f"Ваш файл был отправлен на печать на принтер: {printer_name.replace('_', ' ')}."
# #             f"\nПожалуйста, подождите..."
# #         )
# #         await asyncio.create_task(
# #             check_print_status(
# #                 message, message.chat.id, job_id, printer_name, l10n=l10n
# #             )
# #         )
# #         await state.clear()
# #     else:
# #         # try:
# #         page_count, total_cost = await printing_cost(message, pdf_file_path)
# #
# #         payment_id, confirmation_url = await create_payment(
# #             f"Печать документа {document.file_name} на {page_count} страниц",
# #             amount=total_cost,
# #             l10n=l10n,
# #         )
# #         # except Exception as e:
# #         #     await message.reply(f"Произошла ошибка при создании платежа: {e}")
# #         #     return
# #
# #         await state.update_data(
# #             payment_id=payment_id,
# #             temp_file_path=pdf_file_path,
# #             document_file_name=document.file_name,
# #             total_cost=total_cost,
# #         )
# #         payment_message = await message.reply(
# #             f"Пожалуйста, оплатите печать ({total_cost} руб.), нажав на кнопку ниже.",
# #             reply_markup=await kb.payment(
# #                 confirmation_url, amount=total_cost, l10n=l10n
# #             ),
# #         )
# #         await state.update_data(payment_message_id=payment_message.message_id)
# #         await state.set_state(Printer.payment)
# #
# #         # Начинаем процесс проверки статуса платежа
# #         await asyncio.create_task(poll_payment_status(message, state, l10n=l10n))
# #     # except Exception as e:
# #     #     await message.reply(f"Произошла ошибка при обработке файла: {e}")
# #     #     return
# @printer_router.message(F.content_type == ContentType.DOCUMENT, Printer.document)
# async def print_docs_photo(
#     message: Message, bot: Bot, state: FSMContext, l10n: FluentLocalization
# ):
#     adjustments = await get_adjustments()
#     printing_info = adjustments.get("printing_available")
#     free_printing_info = adjustments.get("free_printing_available")
#
#     data = await state.get_data()
#     printer_name = data.get("printer_name")
#
#     document = message.document
#     file_info = await bot.get_file(document.file_id)
#     file_path = file_info.file_path
#     downloaded_file = await bot.download_file(file_path)
#     temp_file_path = f"/tmp/{document.file_name}"
#     pdf_file_path = f"/tmp/{Path(document.file_name).stem}.pdf"
#
#     async with aiofiles.open(temp_file_path, "wb") as new_file:
#         await new_file.write(downloaded_file.read())
#
#     if not Path(temp_file_path).is_file():
#         await message.reply("Произошла ошибка при сохранении файла.")
#         return
#
#     try:
#         if not temp_file_path.endswith(".pdf"):
#             await convert_to_pdf(temp_file_path, pdf_file_path)
#         else:
#             pdf_file_path = temp_file_path
#
#         if free_printing_info["state"] or printing_info["value"] == 0:
#             job_id = await print_file(pdf_file_path, printer_name)
#             await state.update_data(job_id=job_id)
#             await message.reply(
#                 f"Ваш файл был отправлен на печать на принтер: {printer_name.replace('_', ' ')}."
#                 f"\nПожалуйста, подождите..."
#             )
#             await asyncio.create_task(
#                 check_print_status(
#                     message, message.chat.id, job_id, printer_name, l10n=l10n
#                 )
#             )
#             await state.clear()
#         else:
#             page_count, total_cost = await printing_cost(message, pdf_file_path)
#
#             payment_id, confirmation_url = await create_payment(
#                 f"Печать документа {document.file_name} на {page_count} страниц",
#                 amount=total_cost,
#                 l10n=l10n,
#             )
#
#             await state.update_data(
#                 payment_id=payment_id,
#                 temp_file_path=pdf_file_path,
#                 document_file_name=document.file_name,
#                 total_cost=total_cost,
#             )
#             payment_message = await message.reply(
#                 f"Пожалуйста, оплатите печать ({total_cost} руб.), нажав на кнопку ниже.",
#                 reply_markup=await kb.payment(
#                     confirmation_url, amount=total_cost, l10n=l10n
#                 ),
#             )
#             await state.update_data(payment_message_id=payment_message.message_id)
#             await state.set_state(Printer.payment)
#
#             await asyncio.create_task(poll_payment_status(message, state, l10n=l10n))
#     except Exception as e:
#         await message.reply(f"Произошла ошибка при обработке файла: {e}")
#         await state.clear()
#         return
#
#
# async def check_payment_status(payment_id: str) -> bool:
#     loop = asyncio.get_event_loop()
#     # try:
#     # Запускаем синхронный метод в пуле потоков
#     payment = await loop.run_in_executor(executor, Payment.find_one, payment_id)
#     return payment.status == "succeeded"
#     # except Exception as e:
#     #     return False
#
#
# async def poll_payment_status(
#     message: Message, state: FSMContext, l10n: FluentLocalization
# ):
#     delay = 5
#     data = await state.get_data()
#     payment_id = data.get("payment_id")
#     payment_message_id = data.get("payment_message_id")
#     temp_file_path = data.get("temp_file_path")
#     printer_name = data.get("printer_name")
#     while True:
#         payment_status = (await state.get_data()).get("payment_status")
#         if payment_status == "cancelled":
#             await state.clear()
#             break
#         if await check_payment_status(payment_id):
#             await message.bot.edit_message_text(
#                 text=f"Ваш файл был отправлен на печать на принтер: {printer_name.replace('_', ' ')}. "
#                 f"\nПожалуйста, подождите...",
#                 chat_id=message.chat.id,
#                 message_id=payment_message_id,
#             )
#             job_id = await print_file(temp_file_path, printer_name)
#             await asyncio.create_task(
#                 check_print_status(
#                     message, message.chat.id, job_id, printer_name, l10n=l10n
#                 )
#             )
#             await state.clear()
#             break
#         await asyncio.sleep(delay)
#
#
# @printer_router.callback_query(F.data == "cancel_pay", Printer.payment)
# async def cancel_payment(
#     callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
# ):
#     await cancel_payment_handler(callback, state, l10n=l10n)
# import asyncio
import logging
import io
import re

# from pathlib import Path
#
# import aiofiles
# from aiogram import F, Bot, Router
# from aiogram.enums import ContentType
from aiogram.exceptions import TelegramBadRequest

# from aiogram.types import Message, CallbackQuery
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from fluent.runtime import FluentLocalization
# from yookassa import Payment
# from PyPDF2 import PdfReader
# from concurrent.futures import ThreadPoolExecutor
#
# import cups

# from tgbot.database.requests import get_adjustments
# import tgbot.keyboards.user_kb as kb
# from tgbot.handlers.user_handlers.payment import create_payment, cancel_payment_handler
# from tgbot.filters.filters import IsUserFilter
import shutil

import aiofiles
from aiogram import F, Bot, Router
import cups
import asyncio
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from pathlib import Path

from fluent.runtime import FluentLocalization
from yookassa import Payment

import subprocess
from PyPDF2 import PdfReader

from tgbot.database.requests import get_adjustments
import tgbot.keyboards.user_kb.keyboards as kb
from tgbot.handlers.user_handlers.payment import create_payment, cancel_payment_handler

# from app.database.requests import get_adjustments
# import app.user_kb.keyboards as kb
# from app.user_handlers.payment import create_payment, cancel_payment_handler

from concurrent.futures import ThreadPoolExecutor

from tgbot.filters import IsUserFilter

logger = logging.getLogger(__name__)

printer_router = Router()
executor = ThreadPoolExecutor(max_workers=5)  # Пул потоков для синхронных операций

# Применяем фильтр для всех хэндлеров на уровне роутера
printer_router.message.filter(IsUserFilter(is_user=True))
printer_router.callback_query.filter(IsUserFilter(is_user=True))


class PrinterManager:
    def __init__(self):
        """Инициализация подключения к CUPS."""
        try:
            self.conn = cups.Connection()
            logger.debug("Подключение к CUPS успешно установлено")
        except Exception as e:
            logger.error("Ошибка подключения к CUPS: %s", str(e))
            raise

    def get_printers(self) -> dict[str, str]:
        """Возвращает словарь уникальных принтеров, исключая дубли с цифрами в конце."""
        all_printers = self.conn.getPrinters()  # dict[str, dict]
        unique_printers = {}
        seen_base_names = set()

        for printer_name, printer_attrs in all_printers.items():

            # Удаляем цифры в конце имени
            base_name = re.sub(r"_?\d+$", "", printer_name).strip()

            # Если базовое имя ещё не встречалось, добавляем принтер
            if base_name not in seen_base_names:
                unique_printers[printer_name] = printer_attrs
                seen_base_names.add(base_name)
            # Если это дубликат с цифрой, пропускаем его
            # (оставляем первый встреченный вариант, обычно без цифры)

        return unique_printers

    # def get_printers(self):
    #     """Получение списка доступных принтеров."""
    #     try:
    #         printers = self.conn.getPrinters()
    #         logger.debug("Получен список принтеров: %s", printers.keys())
    #         return printers
    #     except Exception as e:
    #         logger.error("Ошибка получения списка принтеров: %s", str(e))
    #         return {}

    def print_file(self, file_path: str, printer_name: str) -> int:
        """Отправка файла на печать."""
        if not Path(file_path).is_file():
            logger.error("Файл для печати не найден: %s", file_path)
            raise FileNotFoundError(f"Файл {file_path} не найден")
        printer_name = printer_name.replace(" ", "_")
        try:
            job_id = self.conn.printFile(printer_name, file_path, "Print Job", {})
            logger.debug(
                "Файл отправлен на печать: job_id=%s, printer=%s", job_id, printer_name
            )
            return job_id
        except Exception as e:
            logger.error(
                "Ошибка печати файла %s на принтере %s: %s",
                file_path,
                printer_name,
                str(e),
            )
            raise

    def get_job_attributes(self, job_id: int):
        """Получение атрибутов задания печати."""
        try:
            attrs = self.conn.getJobAttributes(job_id)
            logger.debug("Получены атрибуты задания %s: %s", job_id, attrs)
            return attrs
        except Exception as e:
            logger.error("Ошибка получения статуса задания %s: %s", job_id, str(e))
            raise


class Printer(StatesGroup):
    """Состояния для процесса печати документа."""

    document = State()
    printer_selection = State()
    payment = State()
    status_payment = State()


printer_manager = PrinterManager()


# async def convert_to_pdf(input_file: str, output_file: str) -> str:
#     """Конвертация файла в PDF с использованием LibreOffice."""
#     try:
#         process = await asyncio.create_subprocess_exec(
#             "libreoffice",
#             "--headless",
#             "--convert-to",
#             "pdf",
#             "--outdir",
#             "/tmp",
#             input_file,
#             stdout=asyncio.subprocess.PIPE,
#             stderr=asyncio.subprocess.PIPE,
#         )
#         stdout, stderr = await process.communicate()
#         if process.returncode != 0:
#             error_msg = stderr.decode()
#             logger.error("Ошибка конвертации %s в PDF: %s", input_file, error_msg)
#             raise Exception(f"Ошибка конвертации файла в PDF: {error_msg}")
#         if not Path(output_file).is_file():
#             logger.error("PDF-файл %s не создан после конвертации", output_file)
#             raise FileNotFoundError(f"Файл {output_file} не найден после конвертации")
#         logger.debug("Файл успешно сконвертирован: %s -> %s", input_file, output_file)
#         return output_file
#     except Exception as e:
#         logger.error("Ошибка в процессе конвертации: %s", str(e))
#         raise
async def convert_to_pdf(input_file, output_file):
    libre_path = shutil.which("libreoffice")
    if not libre_path:
        raise Exception(
            "LibreOffice не установлен на сервере. Печать .docx файлов временно недоступна."
        )

    process = subprocess.run(
        [
            libre_path,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            "/tmp",
            input_file,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.returncode != 0:
        raise Exception(f"Ошибка конвертации файла в PDF: {process.stderr.decode()}")
    if not Path(output_file).is_file():
        raise FileNotFoundError(f"Файл {output_file} не найден после конвертации")
    return output_file


async def count_pdf_pages(pdf_file_path: str) -> int:
    """Подсчёт страниц в PDF-файле."""
    try:
        async with aiofiles.open(pdf_file_path, "rb") as f:
            content = await f.read()
            pdf = PdfReader(io.BytesIO(content))
            page_count = len(pdf.pages)
            logger.debug("Подсчитано страниц в %s: %s", pdf_file_path, page_count)
            return page_count
    except Exception as e:
        logger.error("Ошибка подсчёта страниц в %s: %s", pdf_file_path, str(e))
        raise


async def printing_cost(pdf_file_path: str) -> tuple[int, float]:
    """Вычисление стоимости печати документа."""
    try:
        adjustments = await get_adjustments()
        printing_info = adjustments.get("printing_available", {})
        if not printing_info or "value" not in printing_info:
            logger.error("Неверные настройки печати: %s", adjustments)
            raise ValueError("Настройки печати недоступны")
        page_count = await count_pdf_pages(pdf_file_path)
        print_price = printing_info["value"]
        total_cost = page_count * print_price
        logger.debug(
            "Стоимость печати: страницы=%s, цена/стр=%s, итого=%s",
            page_count,
            print_price,
            total_cost,
        )
        return page_count, total_cost
    except Exception as e:
        logger.error(
            "Ошибка вычисления стоимости печати для %s: %s", pdf_file_path, str(e)
        )
        raise


async def get_printers():
    """Получение списка принтеров."""
    return printer_manager.get_printers()


async def print_file(file_path: str, printer_name: str) -> int:
    """Отправка файла на печать."""
    return printer_manager.print_file(file_path, printer_name)


async def check_print_status(
    message: Message,
    chat_id: int,
    job_id: int,
    printer_name: str,
    l10n: FluentLocalization,
) -> None:
    """Проверка статуса печати задания."""
    printer_display_name = printer_name.replace("_", " ")
    while True:
        try:
            job = printer_manager.get_job_attributes(job_id)
            state = job.get("job-state")
            if state == 9:  # Завершено
                await message.bot.send_message(
                    chat_id,
                    l10n.format_value(
                        "print_success", {"printer": printer_display_name}
                    ),
                    reply_markup=await kb.user_main(l10n=l10n),
                )
                break
            elif state in {5, 6, 7, 8}:  # В процессе
                await asyncio.sleep(5)
            else:
                await message.bot.send_message(
                    chat_id,
                    l10n.format_value("print_error", {"printer": printer_display_name}),
                    reply_markup=await kb.user_main(l10n=l10n),
                )
                break
        except TelegramBadRequest as e:
            logger.error(
                "Не удалось отправить статус печати для job_id %s: %s", job_id, str(e)
            )
            break
        except Exception as e:
            logger.error("Ошибка проверки статуса печати job_id %s: %s", job_id, str(e))
            await message.bot.send_message(
                chat_id,
                l10n.format_value("print_error", {"printer": printer_display_name}),
                reply_markup=await kb.user_main(l10n=l10n),
            )
            break


@printer_router.callback_query(F.data == "print_doc")
async def start_printing(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Начало процесса печати документа."""
    # await callback.answer("Временно недоступно", show_alert=True)
    try:
        adjustments = await get_adjustments()
        printing_info = adjustments.get("printing_available", {})
        if not printing_info.get("state", False):
            await callback.answer(
                l10n.format_value("printing_unavailable"), show_alert=True
            )
            return
        printers = await get_printers()
        if not printers:
            await callback.message.edit_text(
                l10n.format_value("no_printers_available"),
                reply_markup=await kb.user_main(l10n=l10n),
            )
            return
        print_price = printing_info.get("value", 0)
        await callback.message.edit_text(
            l10n.format_value("select_printer", {"price": print_price}),
            reply_markup=await kb.printers_list(printers, l10n=l10n),
        )
        await state.set_state(Printer.printer_selection)
    except TelegramBadRequest as e:
        logger.error("Не удалось обновить сообщение в start_printing: %s", str(e))
    except Exception as e:
        logger.error("Ошибка начала печати: %s", str(e))
        await callback.answer(l10n.format_value("printing_error"), show_alert=True)


@printer_router.callback_query(
    F.data.startswith("select_printer"), Printer.printer_selection
)
async def select_printer(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Выбор принтера для печати."""
    try:
        printer_name = callback.data.split(":")[1]
        await state.update_data(printer_name=printer_name)
        printer_display_name = printer_name.replace("_", " ")
        await callback.message.edit_text(
            l10n.format_value("printer_selected", {"printer": printer_display_name})
        )
        await callback.answer()
        await state.set_state(Printer.document)
    except IndexError:
        logger.error("Некорректный формат данных принтера: %s", callback.data)
        await callback.answer(l10n.format_value("invalid_printer"), show_alert=True)
    except TelegramBadRequest as e:
        logger.error("Не удалось обновить сообщение в select_printer: %s", str(e))


@printer_router.message(F.content_type == ContentType.DOCUMENT, Printer.document)
async def print_docs_photo(
    message: Message, bot: Bot, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Обработка документа для печати."""
    try:
        data = await state.get_data()
        printer_name = data.get("printer_name")
        if not printer_name:
            logger.error("Printer_name отсутствует в состоянии")
            await message.reply(l10n.format_value("printer_not_selected"))
            return

        adjustments = await get_adjustments()
        printing_info = adjustments.get("printing_available", {})
        free_printing_info = adjustments.get("free_printing_available", {})
        if "value" not in printing_info or "state" not in free_printing_info:
            logger.error("Неверные настройки печати: %s", adjustments)
            await message.reply(l10n.format_value("printing_config_error"))
            return

        document = message.document
        file_info = await bot.get_file(document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        temp_file_path = f"/tmp/{document.file_name}"
        pdf_file_path = f"/tmp/{Path(document.file_name).stem}.pdf"

        try:
            async with aiofiles.open(temp_file_path, "wb") as new_file:
                await new_file.write(downloaded_file.read())
            if not Path(temp_file_path).is_file():
                logger.error("Файл %s не сохранён", temp_file_path)
                await message.reply(l10n.format_value("file_save_error"))
                return

            if not temp_file_path.endswith(".pdf"):
                await convert_to_pdf(temp_file_path, pdf_file_path)
            else:
                pdf_file_path = temp_file_path

            if free_printing_info["state"] or printing_info["value"] == 0:
                job_id = await print_file(pdf_file_path, printer_name)
                await state.update_data(job_id=job_id)
                await message.reply(
                    l10n.format_value(
                        "file_sent_to_print",
                        {"printer": printer_name.replace("_", " ")},
                    ),
                    reply_markup=await kb.user_main(l10n=l10n),
                )
                await asyncio.create_task(
                    check_print_status(
                        message, message.chat.id, job_id, printer_name, l10n
                    )
                )
                await state.clear()
            else:
                page_count, total_cost = await printing_cost(pdf_file_path)
                payment_id, confirmation_url = await create_payment(
                    l10n.format_value(
                        "payment_description",
                        {"filename": document.file_name, "pages": page_count},
                    ),
                    int(total_cost),
                    l10n=l10n,
                )
                await state.update_data(
                    payment_id=payment_id,
                    temp_file_path=pdf_file_path,
                    document_file_name=document.file_name,
                    total_cost=total_cost,
                )
                payment_message = await message.reply(
                    l10n.format_value("payment_request", {"cost": total_cost}),
                    reply_markup=await kb.payment(
                        confirmation_url, amount=int(total_cost), l10n=l10n
                    ),
                )
                await state.update_data(payment_message_id=payment_message.message_id)
                await state.set_state(Printer.payment)
                await asyncio.create_task(poll_payment_status(message, state, l10n))
        finally:
            # Очистка временных файлов
            for file in (temp_file_path, pdf_file_path):
                if Path(file).is_file():
                    Path(file).unlink()
                    logger.debug("Удалён временный файл: %s", file)
    except Exception as e:
        logger.error("Ошибка обработки документа для печати: %s", str(e))
        await message.reply(l10n.format_value("printing_error"))
        await state.clear()


async def check_payment_status(payment_id: str) -> bool:
    """Проверка статуса платежа в YooKassa."""
    loop = asyncio.get_event_loop()
    try:
        payment = await loop.run_in_executor(executor, Payment.find_one, payment_id)
        status = payment.status == "succeeded"
        logger.debug(
            "Статус платежа %s: %s", payment_id, "успешно" if status else payment.status
        )
        return status
    except Exception as e:
        logger.error("Ошибка проверки статуса платежа %s: %s", payment_id, str(e))
        return False


async def poll_payment_status(
    message: Message, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Проверка статуса платежа в цикле."""
    delay = 5
    data = await state.get_data()
    payment_id = data.get("payment_id")
    payment_message_id = data.get("payment_message_id")
    temp_file_path = data.get("temp_file_path")
    printer_name = data.get("printer_name")
    printer_display_name = printer_name.replace("_", " ")

    while True:
        payment_status = (await state.get_data()).get("payment_status")
        if payment_status == "cancelled":
            if Path(temp_file_path).is_file():
                Path(temp_file_path).unlink()
                logger.debug("Удалён временный файл после отмены: %s", temp_file_path)
            await state.clear()
            break
        if await check_payment_status(payment_id):
            try:
                await message.bot.edit_message_text(
                    text=l10n.format_value(
                        "file_sent_to_print", {"printer": printer_display_name}
                    ),
                    chat_id=message.chat.id,
                    message_id=payment_message_id,
                )
                job_id = await print_file(temp_file_path, printer_name)
                await asyncio.create_task(
                    check_print_status(
                        message, message.chat.id, job_id, printer_name, l10n
                    )
                )
            except TelegramBadRequest as e:
                logger.error("Не удалось обновить сообщение о печати: %s", str(e))
            except Exception as e:
                logger.error("Ошибка отправки файла на печать: %s", str(e))
                await message.bot.send_message(
                    message.chat.id,
                    l10n.format_value("print_error", {"printer": printer_display_name}),
                    reply_markup=await kb.user_main(l10n=l10n),
                )
            finally:
                if Path(temp_file_path).is_file():
                    Path(temp_file_path).unlink()
                    logger.debug(
                        "Удалён временный файл после печати: %s", temp_file_path
                    )
                await state.clear()
            break
        await asyncio.sleep(delay)


@printer_router.callback_query(F.data == "cancel_pay", Printer.payment)
async def cancel_payment(
    callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization
) -> None:
    """Отмена платежа для печати."""
    try:
        await cancel_payment_handler(callback, state, l10n)
    except Exception as e:
        logger.error("Ошибка отмены платежа: %s", str(e))
        await callback.answer(
            l10n.format_value("payment_cancel_error"), show_alert=True
        )
