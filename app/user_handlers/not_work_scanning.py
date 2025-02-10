# import pyinsane2
# from aiogram import Dispatcher, Bot, F, Router
# from aiogram.types import CallbackQuery, InputFile
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from pathlib import Path
#
# import app.user_kb.user_kb as kb
#
# from app.database.requests import get_adjustments
#
# scanner_router = Router()
#
#
# class ScanStates(StatesGroup):
#     waiting_for_scan_selection = State()
#     waiting_for_scan_confirmation = State()
#
#
# async def get_scanners():
#     pyinsane2.init()
#     devices = pyinsane2.get_devices()
#     scanners = [device.name for device in devices]
#     return scanners
#
#
# async def scan_document(scanner_name):
#     pyinsane2.init()
#     device = pyinsane2.Scanner(name=scanner_name)
#     device.options['mode'].value = 'Color'
#     device.options['resolution'].value = 300
#     scanned_image = device.scan()
#
#     scanned_file_path = f"/tmp/scanned_document_{scanner_name.replace('/', '_')}.png"
#     with open(scanned_file_path, 'wb') as f:
#         f.write(scanned_image)
#
#     if not Path(scanned_file_path).is_file():
#         raise FileNotFoundError(f"Не удалось отсканировать документ с помощью сканера: {scanner_name}")
#
#     return scanned_file_path
#
#
# @scanner_router.callback_query(F.data == "scan_document")
# async def start_scanning(callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
#     adjustments = await get_adjustments()
#     scanning_info = adjustments['scanning_available']
#     if not scanning_info["state"]:
#         await callback.answer("Функция сканирования сейчас недоступна.", show_alert=True)
#         return
#
#     await callback.answer()
#     scanners = await get_scanners()
#     if not scanners:
#         await callback.message.edit_text("Доступных сканеров нет.")
#         return
#     await callback.message.edit_text("Выберите сканер для сканирования:", reply_markup=await kb.scan_list(scanners, l10n=l10n))
#     await state.set_state(ScanStates.waiting_for_scan_selection)
#
#
# async def select_scanner(callback: CallbackQuery, state: FSMContext, l10n: FluentLocalization):
#     await callback.answer()
#     scanner_name = callback.data.split(":")[1]
#     await state.update_data(scanner_name=scanner_name)
#     await callback.message.edit_text(
#         f"Вы выбрали сканер: {scanner_name}. Нажмите 'Подтвердить' для начала сканирования.",
#         reply_markup=confirm_scan_keyboard(l10n=l10n))
#     await state.set_state(ScanStates.waiting_for_scan_confirmation)
#
#
# async def confirm_scan(callback: CallbackQuery, bot: Bot, state: FSMContext, l10n: FluentLocalization):
#     await callback.answer()
#     data = await state.get_data()
#     scanner_name = data.get("scanner_name")
#     if not scanner_name:
#         await callback.message.edit_text("Пожалуйста, выберите сканер.")
#         return
#
#     try:
#         scanned_file_path = await scan_document(scanner_name)
#         await callback.message.edit_text(f"Сканирование завершено. Отправка файла...")
#
#         await bot.send_document(callback.message.chat.id, InputFile(scanned_file_path))
#         await state.clear()
#     except Exception as e:
#         await callback.message.edit_text(f"Произошла ошибка при сканировании: {e}")
#         await state.clear()
#
#
# def register_scan_handler(dp: Dispatcher):
#     # dp.callback_query.register(start_scanning, F.data == "scan_document")
#     dp.callback_query.register(select_scanner, F.data.startswith("select_scanner:"))
#     dp.callback_query.register(confirm_scan, F.data == "confirm_scan")
