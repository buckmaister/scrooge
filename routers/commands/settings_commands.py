from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardRemove
from config.config import update_value
from keyboards.common_keyboards import *

router = Router(name=__name__)


class Form(StatesGroup):
    spreadsheet_id_state = State()
    attach_saving_path_state = State()
    service_account_file_state = State()
    worksheet_income_name_state = State()
    worksheet_expenses_name_state = State()
    skip_statement_firstline_state = State()
    income_start_row_state = State()
    expenses_start_row_state = State()
    split_income_expenses_state = State()
    retry_delay_state = State()
    max_retries_state = State()


# handle function for SPREADSHEET_ID
@router.message(F.text == SettingsBtn.SPREADSHEET_ID)
async def handle_spreadsheet_id_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.spreadsheet_id_state)
    await message.answer(
        text=f"Send me the new value",
        reply_markup=ReplyKeyboardRemove()
    )


# set function for SPREADSHEET_ID
@router.message(Form.spreadsheet_id_state)
async def set_spreadsheet_id(message: types.Message, state: FSMContext):
    new_value = message.text
    if new_value == "":
        await message.answer(
            text=f"The value entered does not seem correct, please try again!",
            reply_markup=get_back_to_menu_kb()
        )
        return

    update_value("SPREADSHEET.SPREADSHEET_ID", new_value)
    await state.clear()
    await message.answer(
        text=f"New value set correctly: {new_value}",
        reply_markup=get_back_to_menu_kb()
    )


# Handle function for ATTACH_SAVING_PATH
@router.message(F.text == SettingsBtn.ATTACH_SAVING_PATH)
async def handle_attach_saving_path_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.attach_saving_path_state)
    await message.answer(
        text="Send me the new ATTACH_SAVING_PATH value",
        reply_markup=ReplyKeyboardRemove()
    )


# Set function for ATTACH_SAVING_PATH
@router.message(Form.attach_saving_path_state)
async def set_attach_saving_path(message: types.Message, state: FSMContext):
    new_value = message.text
    if not new_value:  # Check for empty string or potentially validate the path
        await message.answer(
            text="The value entered does not seem correct, please try again!",
            reply_markup=get_back_to_menu_kb()
        )
        return

    update_value("SETTINGS.ATTACH_SAVING_PATH", new_value)
    await state.clear()
    await message.answer(
        text=f"New ATTACH_SAVING_PATH set correctly: {new_value}",
        reply_markup=get_back_to_menu_kb()
    )


@router.message(F.text == SettingsBtn.SERVICE_ACCOUNT_FILE)
async def handle_service_account_file_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.service_account_file_state)
    await message.answer(
        text="Send me the new SERVICE_ACCOUNT_FILE value",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(Form.service_account_file_state)
async def set_service_account_file(message: types.Message, state: FSMContext):
    new_value = message.text
    if not new_value:  #TODO: add validation
        await message.answer(
            text="The value entered does not seem correct, please try again!",
            reply_markup=get_back_to_menu_kb()
        )
        return

    update_value("SPREADSHEET.SERVICE_ACCOUNT_FILE", new_value)
    await state.clear()
    await message.answer(
        text=f"New SERVICE_ACCOUNT_FILE set correctly: {new_value}",
        reply_markup=get_back_to_menu_kb()
    )


# handle function for WORKSHEET_INCOME_NAME
@router.message(F.text == SettingsBtn.WORKSHEET_INCOME_NAME)
async def handle_worksheet_income_name_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.worksheet_income_name_state)
    await message.answer(
        text="Send me the new WORKSHEET_INCOME_NAME value",
        reply_markup=ReplyKeyboardRemove()
    )


# set function for WORKSHEET_INCOME_NAME
@router.message(Form.worksheet_income_name_state)
async def set_worksheet_income_name(message: types.Message, state: FSMContext):
    new_value = message.text
    if not new_value:  #TODO: add validation
        await message.answer(
            text="The value entered does not seem correct, please try again!",
            reply_markup=get_back_to_menu_kb()
        )
        return

    update_value("SPREADSHEET.WORKSHEET_INCOME_NAME", new_value)
    await state.clear()
    await message.answer(
        text=f"New WORKSHEET_INCOME_NAME set correctly: {new_value}",
        reply_markup=get_back_to_menu_kb()
    )


# handle function for WORKSHEET_EXPENSES_NAME
@router.message(F.text == SettingsBtn.WORKSHEET_EXPENSES_NAME)
async def handle_worksheet_expenses_name_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.worksheet_expenses_name_state)
    await message.answer(
        text="Send me the new WORKSHEET_EXPENSES_NAME value",
        reply_markup=ReplyKeyboardRemove()
    )


# set function for WORKSHEET_EXPENSES_NAME
@router.message(Form.worksheet_expenses_name_state)
async def set_worksheet_expenses_name(message: types.Message, state: FSMContext):
    new_value = message.text
    if not new_value:  #TODO: add validation
        await message.answer(
            text="The value entered does not seem correct, please try again!",
            reply_markup=get_back_to_menu_kb()
        )
        return

    update_value("SPREADSHEET.WORKSHEET_EXPENSES_NAME", new_value)
    await state.clear()
    await message.answer(
        text=f"New WORKSHEET_EXPENSES_NAME set correctly: {new_value}",
        reply_markup=get_back_to_menu_kb()
    )


# handle function for SKIP_STATEMENT_FIRSTLINE
@router.message(F.text == SettingsBtn.SKIP_STATEMENT_FIRSTLINE)
async def handle_skip_statement_firstline_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.skip_statement_firstline_state)
    await message.answer(
        text="Do you want to skip the first line of the statement? (Yes/No)",
        reply_markup=ReplyKeyboardRemove()
    )


# set function for SKIP_STATEMENT_FIRSTLINE
@router.message(Form.skip_statement_firstline_state)
async def set_skip_statement_firstline(message: types.Message, state: FSMContext):
    new_value = message.text.strip().lower()
    if new_value not in ["yes", "no"]:
        await message.answer(
            text="Invalid input. Please type 'Yes' to skip the first line or 'No' to include it.",
            reply_markup=get_back_to_menu_kb()
        )
        return

    # Converti la risposta in un valore booleano
    boolean_value = True if new_value == "yes" else False
    update_value("SPREADSHEET.SKIP_STATEMENT_FIRSTLINE", boolean_value)
    await state.clear()
    await message.answer(
        text=f"Setting to skip the first line of the statement has been set to: {'Yes' if boolean_value else 'No'}",
        reply_markup=get_back_to_menu_kb()
    )


# handle function for INCOME_START_ROW
@router.message(F.text == SettingsBtn.INCOME_START_ROW)
async def handle_income_start_row_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.income_start_row_state)
    await message.answer(
        text="Send me the new INCOME_START_ROW value (number)",
        reply_markup=ReplyKeyboardRemove()
    )


# set function for INCOME_START_ROW
@router.message(Form.income_start_row_state)
async def set_income_start_row(message: types.Message, state: FSMContext):
    new_value = message.text
    if not new_value.isdigit():
        await message.answer(
            text="The value entered is not a valid number. Please try again!",
            reply_markup=get_back_to_menu_kb()
        )
        return

    update_value("SPREADSHEET.INCOME_START_ROW", int(new_value))
    await state.clear()
    await message.answer(
        text=f"New INCOME_START_ROW set correctly: {new_value}",
        reply_markup=get_back_to_menu_kb()
    )


# handle function for EXPENSES_START_ROW
@router.message(F.text == SettingsBtn.EXPENSES_START_ROW)
async def handle_expenses_start_row_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.expenses_start_row_state)
    await message.answer(
        text="Send me the new EXPENSES_START_ROW value (number)",
        reply_markup=ReplyKeyboardRemove()
    )


# set function for EXPENSES_START_ROW
@router.message(Form.expenses_start_row_state)
async def set_expenses_start_row(message: types.Message, state: FSMContext):
    new_value = message.text
    if not new_value.isdigit():
        await message.answer(
            text="The value entered is not a valid number. Please try again!",
            reply_markup=get_back_to_menu_kb()
        )
        return

    update_value("SPREADSHEET.EXPENSES_START_ROW", int(new_value))
    await state.clear()
    await message.answer(
        text=f"New EXPENSES_START_ROW set correctly: {new_value}",
        reply_markup=get_back_to_menu_kb()
    )


# handle function for SPLIT_INCOME_EXPENSES
@router.message(F.text == SettingsBtn.SPLIT_INCOME_EXPENSES)
async def handle_split_income_expenses_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.split_income_expenses_state)
    await message.answer(
        text="Do you want to split income and expenses? (Yes/No)",
        reply_markup=ReplyKeyboardRemove()
    )


# set function for SPLIT_INCOME_EXPENSES
@router.message(Form.split_income_expenses_state)
async def set_split_income_expenses(message: types.Message, state: FSMContext):
    new_value = message.text.strip().lower()
    if new_value not in ["yes", "no"]:
        await message.answer(
            text="Invalid input. Please type 'Yes' to enable or 'No' to disable.",
            reply_markup=get_back_to_menu_kb()
        )
        return

    # Converti la risposta in un valore booleano
    boolean_value = True if new_value == "yes" else False
    update_value("SPREADSHEET.SPLIT_INCOME_EXPENSES", boolean_value)
    await state.clear()
    await message.answer(
        text=f"Setting to split income and expenses has been {'enabled' if boolean_value else 'disabled'}.",
        reply_markup=get_back_to_menu_kb()
    )


# handle function for RETRY_DELAY
@router.message(F.text == SettingsBtn.RETRY_DELAY)
async def handle_retry_delay_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.retry_delay_state)
    await message.answer(
        text="Send me the new RETRY_DELAY value in seconds",
        reply_markup=ReplyKeyboardRemove()
    )


# set function for RETRY_DELAY
@router.message(Form.retry_delay_state)
async def set_retry_delay(message: types.Message, state: FSMContext):
    new_value = message.text
    if not new_value.isdigit():
        await message.answer(
            text="The value entered is not a valid number. Please enter a numeric value in seconds.",
            reply_markup=get_back_to_menu_kb()
        )
        return

    update_value("SPREADSHEET.RETRY_DELAY", int(new_value))
    await state.clear()
    await message.answer(
        text=f"New RETRY_DELAY set correctly: {new_value} seconds",
        reply_markup=get_back_to_menu_kb()
    )


# handle function for MAX_RETRIES
@router.message(F.text == SettingsBtn.MAX_RETRIES)
async def handle_max_retries_btn(message: types.Message, state: FSMContext):
    await state.set_state(Form.max_retries_state)
    await message.answer(
        text="Send me the new MAX_RETRIES value (it should be a positive integer)",
        reply_markup=ReplyKeyboardRemove()
    )


# set function for MAX_RETRIES
@router.message(Form.max_retries_state)
async def set_max_retries(message: types.Message, state: FSMContext):
    new_value = message.text
    if not new_value.isdigit() or int(new_value) < 0:
        await message.answer(
            text="The value entered is not a valid positive integer. Please try again!",
            reply_markup=get_back_to_menu_kb()
        )
        return

    update_value("SPREADSHEET.MAX_RETRIES", int(new_value))
    await state.clear()
    await message.answer(
        text=f"New MAX_RETRIES set correctly: {new_value}",
        reply_markup=get_back_to_menu_kb()
    )
