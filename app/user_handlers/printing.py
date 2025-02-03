import aiofiles
from aiogram import F, Bot, Router
import cups
import asyncio
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from pathlib import Path

from yookassa import Payment
import subprocess
from PyPDF2 import PdfReader

from app.database.requests import get_adjustments
import app.user_kb.keyboards as kb
from app.user_handlers.payment import create_payment, cancel_payment_handler

from concurrent.futures import ThreadPoolExecutor

from filters import IsUserFilter

printer_router = Router()
executor = ThreadPoolExecutor(max_workers=5)  # Определяем пул потоков
# Применяем фильтр для всех хэндлеров на уровне роутера
printer_router.message.filter(IsUserFilter(is_user=True))
printer_router.callback_query.filter(IsUserFilter(is_user=True))


class PrinterManager:
    def __init__(self):
        self.conn = cups.Connection()

    def get_printers(self):
        return self.conn.getPrinters()

    def print_file(self, file_path, printer_name):
        if not Path(file_path).is_file():
            raise FileNotFoundError(f"Файл {file_path} не найден")
        printer_name = printer_name.replace(" ", "_")
        job_id = self.conn.printFile(printer_name, file_path, "Print Job", {})
        return job_id

    def get_job_attributes(self, job_id):
        return self.conn.getJobAttributes(job_id)


class Printer(StatesGroup):
    document = State()
    printer_selection = State()
    payment = State()
    status_payment = State()


libre_path = '/Applications/LibreOffice.app/Contents/MacOS/soffice'  # 'libreoffice'


async def convert_to_pdf(input_file, output_file):
    # process = subprocess.run([libre_path, '--headless', '--convert-to', 'pdf', '--outdir', '/tmp', input_file],
    #                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process = subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', '/tmp', input_file],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode != 0:
        raise Exception(f"Ошибка конвертации файла в PDF: {process.stderr.decode()}")
    if not Path(output_file).is_file():
        raise FileNotFoundError(f"Файл {output_file} не найден после конвертации")
    return output_file


async def count_pdf_pages(pdf_file_path):
    try:
        with open(pdf_file_path, 'rb') as f:
            pdf = PdfReader(f)
            return len(pdf.pages)
    except Exception as e:
        raise Exception(f"Ошибка при подсчете страниц PDF: {e}")


async def printing_cost(message, pdf_file_path):
    adjustments = await get_adjustments()
    printing_info = adjustments.get("printing_available")
    try:
        page_count = await count_pdf_pages(pdf_file_path)
        print_price = printing_info["value"]
        total_cost = page_count * print_price
        return page_count, total_cost
    except Exception as e:
        await message.reply(f"Произошла ошибка при подсчете страниц PDF: {e}")
        return


printer_manager = PrinterManager()


async def get_printers():
    return printer_manager.get_printers()


async def print_file(file_path, printer_name):
    return printer_manager.print_file(file_path, printer_name)


async def check_print_status(message: Message, chat_id: int, job_id: int, printer_name: str):
    while True:
        job = printer_manager.get_job_attributes(job_id)
        state = job.get("job-state")
        if state == 9:  # 9 означает, что печать завершена
            await message.bot.send_message(
                chat_id,
                f"Ваш документ был успешно распечатан на принтере: {printer_name.replace('_', ' ')}",
                reply_markup=await kb.user_main()
            )
            break
        elif state in {5, 6, 7, 8}:  # 5-8 означают, что печать в процессе
            await asyncio.sleep(5)
        else:
            await message.bot.send_message(
                chat_id,
                f"Произошла ошибка при печати на принтере: {printer_name.replace('_', ' ')}",
                reply_markup=await kb.user_main()
            )
            break


@printer_router.callback_query(F.data == 'print_doc')
async def start_printing(callback: CallbackQuery, state: FSMContext):
    adjustments = await get_adjustments()
    printing_info = adjustments.get("printing_available")

    if not printing_info["state"]:
        await callback.answer("Функция печати сейчас недоступна.", show_alert=True)
        return

    printers = await get_printers()
    if not printers:
        await callback.message.edit_text("Доступных принтеров нет.", reply_markup=await kb.user_main())
        return

    print_price = printing_info["value"]
    await callback.message.edit_text(f"Выберите принтер для печати\n"
                                     f"(стоимость - {print_price} руб/страница):",
                                     reply_markup=await kb.printers_list(printers))
    await state.set_state(Printer.printer_selection)


@printer_router.callback_query(F.data.startswith('select_printer'), Printer.printer_selection)
async def select_printer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    printer_name = callback.data.split(":")[1]
    await state.update_data(printer_name=printer_name)
    printer_name = printer_name.replace("_", " ")
    await callback.message.edit_text(f"Вы выбрали принтер: {printer_name}. Отправьте документ для печати.")
    await state.set_state(Printer.document)


@printer_router.message(F.content_type == ContentType.DOCUMENT, Printer.document)
async def print_docs_photo(message: Message, bot: Bot, state: FSMContext):
    adjustments = await get_adjustments()
    printing_info = adjustments.get("printing_available")
    free_printing_info = adjustments.get("free_printing_available")

    data = await state.get_data()
    printer_name = data.get("printer_name")

    document = message.document
    file_info = await bot.get_file(document.file_id)
    file_path = file_info.file_path
    downloaded_file = await bot.download_file(file_path)
    temp_file_path = f"/tmp/{document.file_name}"
    pdf_file_path = f"/tmp/{Path(document.file_name).stem}.pdf"

    async with aiofiles.open(temp_file_path, 'wb') as new_file:
        await new_file.write(downloaded_file.read())

    if not Path(temp_file_path).is_file():
        await message.reply("Произошла ошибка при сохранении файла.")
        return

    try:
        if not temp_file_path.endswith(".pdf"):
            await convert_to_pdf(temp_file_path, pdf_file_path)
        else:
            pdf_file_path = temp_file_path

        if free_printing_info["state"] or printing_info["value"] == 0:
            job_id = await print_file(pdf_file_path, printer_name)
            await state.update_data(job_id=job_id)
            await message.reply(f"Ваш файл был отправлен на печать на принтер: {printer_name.replace('_', ' ')}."
                                f"\nПожалуйста, подождите...")
            await asyncio.create_task(check_print_status(message, message.chat.id, job_id, printer_name))
            await state.clear()
        else:
            try:
                page_count, total_cost = await printing_cost(message, pdf_file_path)

                payment_id, confirmation_url = await create_payment(
                    f"Печать документа {document.file_name} на {page_count} страниц",
                    amount=total_cost)
            except Exception as e:
                await message.reply(f"Произошла ошибка при создании платежа: {e}")
                return

            await state.update_data(payment_id=payment_id,
                                    temp_file_path=pdf_file_path,
                                    document_file_name=document.file_name,
                                    total_cost=total_cost)
            payment_message = await message.reply(
                f"Пожалуйста, оплатите печать ({total_cost} руб.), нажав на кнопку ниже.",
                reply_markup=await kb.payment(confirmation_url, amount=total_cost))
            await state.update_data(payment_message_id=payment_message.message_id)
            await state.set_state(Printer.payment)

            # Начинаем процесс проверки статуса платежа
            await asyncio.create_task(poll_payment_status(message, state))
    except Exception as e:
        await message.reply(f"Произошла ошибка при обработке файла: {e}")
        return


async def check_payment_status(payment_id: str) -> bool:
    loop = asyncio.get_event_loop()
    try:
        # Запускаем синхронный метод в пуле потоков
        payment = await loop.run_in_executor(executor, Payment.find_one, payment_id)
        return payment.status == 'succeeded'
    except Exception as e:
        return False


async def poll_payment_status(message: Message, state: FSMContext):
    delay = 5
    data = await state.get_data()
    payment_id = data.get('payment_id')
    payment_message_id = data.get('payment_message_id')
    temp_file_path = data.get('temp_file_path')
    printer_name = data.get('printer_name')
    while True:
        payment_status = (await state.get_data()).get("payment_status")
        if payment_status == "cancelled":
            await state.clear()
            break
        if await check_payment_status(payment_id):
            await message.bot.edit_message_text(
                text=f"Ваш файл был отправлен на печать на принтер: {printer_name.replace('_', ' ')}. "
                     f"\nПожалуйста, подождите...",
                chat_id=message.chat.id,
                message_id=payment_message_id,
            )
            job_id = await print_file(temp_file_path, printer_name)
            await asyncio.create_task(check_print_status(message, message.chat.id, job_id, printer_name))
            await state.clear()
            break
        await asyncio.sleep(delay)


@printer_router.callback_query(F.data == "cancel_pay", Printer.payment)
async def cancel_payment(callback: CallbackQuery, state: FSMContext):
    await cancel_payment_handler(callback, state)
