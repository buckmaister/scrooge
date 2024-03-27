import datetime
import os
from aiogram import F, Router, types, Bot
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils import markdown

from keyboards.common_keyboards import *
from sheets.statement_parser import StatementParser
from sheets.google_sheet_manager import GSpreadFinanceManager
import config.config as config
import importlib

router = Router(name=__name__)


class Form(StatesGroup):
    bank_selection = State()
    awaiting_file = State()


@router.message(CommandStart())
async def handle_start(message: types.Message):
    await message.answer(
        text=f"Hello, {markdown.hbold(message.from_user.full_name)}! Welcome to scrooge bot!\nIf this is your first use, you will find all the information for the initial setup in the HELP section.\n\n You can start from here: /menu",
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(F.text == ButtonText.MENU)
@router.message(F.text == ButtonText.BACK_TO_MENU)
@router.message(Command("menu", prefix="!/"))
async def handle_menu(message: types.Message):
    await message.answer(
        text=f"Choose an option:",
        parse_mode=ParseMode.HTML,
        reply_markup=get_on_start_kb(),
    )


@router.message(F.text == ButtonText.STATEMENT)
@router.message(Command("upload_statement", prefix="!/"))
async def handle_upload_statement_command(message: types.Message, state: FSMContext):
    await state.set_state(Form.bank_selection)
    markup = get_upload_statement_kb()
    await message.answer(
        text="Select the statement's bank:",
        reply_markup=markup,
    )


@router.message(F.text == ButtonText.BACK_TO_MENU)
@router.message(Command("back_to_menu", prefix="!/"))
async def handle_back_to_menu_command(message: types.Message):
    markup = get_on_start_kb()
    await message.answer(
        text="Choose an option from menu:",
        reply_markup=markup,
    )


@router.message(F.text == ButtonText.HELP)
@router.message(Command("help", prefix="!/"))
async def handle_help_command(message: types.Message):
    markup = get_help_kb()
    await message.answer(
        text="What do you need assistance with?",
        reply_markup=markup,
    )


@router.message(F.text == ButtonText.SETTINGS)
@router.message(Command("settings", prefix="!/"))
async def handle_help_command(message: types.Message):
    markup = get_settings_kb()
    importlib.reload(config)
    await message.answer(
        text=f"<b>YOUR CURRENT SETTINGS:</b>\n\n"
             f"<b>Saving path for statement</b> → <code>{config.CONFIG['SETTINGS']['ATTACH_SAVING_PATH']}</code>\n"
             f"<b>Service account file</b> → <code>{config.CONFIG['SPREADSHEET']['SERVICE_ACCOUNT_FILE']}</code>\n"
             f"<b>Spreadsheet ID</b> → <code>{config.CONFIG['SPREADSHEET']['SPREADSHEET_ID']}</code>\n"
             f"<b>Worksheet income name</b> → <code>{config.CONFIG['SPREADSHEET']['WORKSHEET_INCOME_NAME']}</code>\n"
             f"<b>Worksheet expenses name</b> → <code>{config.CONFIG['SPREADSHEET']['WORKSHEET_EXPENSES_NAME']}</code>\n"
             f"<b>Skip statement first line</b> → <code>{config.CONFIG['SPREADSHEET']['SKIP_STATEMENT_FIRSTLINE']}</code>\n"
             f"<b>Income start row</b> → <code>{config.CONFIG['SPREADSHEET']['INCOME_START_ROW']}</code>\n"
             f"<b>Expenses start row</b> → <code>{config.CONFIG['SPREADSHEET']['EXPENSES_START_ROW']}</code>\n"
             f"<b>Split income and expenses</b> → <code>{config.CONFIG['SPREADSHEET']['SPLIT_INCOME_EXPENSES']}</code>\n"
             f"<b>Retry delay</b> → <code>{config.CONFIG['SPREADSHEET']['RETRY_DELAY']}</code>\n"
             f"<b>Max retries</b> → <code>{config.CONFIG['SPREADSHEET']['MAX_RETRIES']}</code>\n"
             f"\nClick on the corresponding button to edit the value",
        parse_mode='HTML',  # with markdown there are problem with special char of SERVICE_ACCOUNT_FILE
        reply_markup=markup,
    )


@router.message(Form.awaiting_file, F.content_type.in_({'document'}))
async def handle_statement_file(message: types.Message, bot: Bot, state: FSMContext):
    # check state
    state_data = await state.get_data()

    mime_type = message.document.mime_type

    if mime_type not in ['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
        await message.reply("Please send a CSV or XLSX file.")
        return

    user_full_name = message.from_user.full_name.replace(" ", "_")
    file_id = message.document.file_id
    file_name = message.document.file_name

    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    new_file_name = f"{user_full_name}_{current_time}_{file_name}"

    data_folder = config.CONFIG['SETTINGS']['ATTACH_SAVING_PATH']
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    save_path = os.path.join(data_folder, new_file_name)

    file = await bot.get_file(file_id)
    file_path = file.file_path

    await bot.download_file(file_path, save_path)
    await message.answer("File received correctly! starting processing...")

    reader = StatementParser(save_path, state_data.get("bank"))
    transactions = reader.read_data()  # TODO: big crash if bank wrong

    gs_manager = GSpreadFinanceManager()

    # TODO: add a message when _add_row go sleep for exceed quote
    res = gs_manager.insert_incomes_and_expenses(transactions, ordered=False, resume_mode=True)
    await message.answer(
        f'Spreadsheet updated successfully!\nNumber of transaction added:\n\nIncomes {res[0]}\nExpenses {res[1]}')

    await state.clear()
    await message.answer("file parsed correctly!")


# --- bank type --- TODO: improv
@router.message(Form.bank_selection, F.text == ButtonText.REVOLUT)
async def select_revolut(message: types.Message, state: FSMContext):
    await state.set_state(Form.awaiting_file)
    await state.update_data(bank='revolut')
    await message.answer("Send me your Revolut statement as attachment!", reply_markup=get_back_to_menu_kb())


@router.message(Form.bank_selection, F.text == ButtonText.UNICREDIT)
async def select_unicredit(message: types.Message, state: FSMContext):
    await state.set_state(Form.awaiting_file)
    await state.update_data(bank='unicredit')
    await message.answer("Send me your Unicredit statement as attachment!", reply_markup=get_back_to_menu_kb())
