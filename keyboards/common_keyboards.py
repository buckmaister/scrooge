from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


class ButtonText:
    STATEMENT = "Upload statement"
    SETTINGS = "Settings"
    HELP = "Help"
    BACK_TO_MENU = "Back to menu"
    MENU = "Menu"
    REVOLUT = "Revolut"
    UNICREDIT = "Unicredit"


class SettingsBtn:
    SPREADSHEET_ID = "Spreadsheet ID"
    WORKSHEET_INCOME_NAME = "Worksheet income name"
    WORKSHEET_EXPENSES_NAME = "Worksheet expenses name"
    SKIP_STATEMENT_FIRSTLINE = "Skip statement first line"
    INCOME_START_ROW = "Income start row"
    EXPENSES_START_ROW = "Expenses start row"
    SPLIT_INCOME_EXPENSES = "Split income and expenses"
    RETRY_DELAY = "Retry delay"
    MAX_RETRIES = "Max retries"
    SERVICE_ACCOUNT_FILE = "Service account file"
    ATTACH_SAVING_PATH = "Saving path for statement"


def get_on_start_kb() -> ReplyKeyboardMarkup:
    button_statement = KeyboardButton(text=ButtonText.STATEMENT)
    button_settings = KeyboardButton(text=ButtonText.SETTINGS)
    button_help = KeyboardButton(text=ButtonText.HELP)
    buttons_first_row = [button_statement]
    buttons_last_row = [button_settings, button_help]
    markup = ReplyKeyboardMarkup(
        keyboard=[buttons_first_row, buttons_last_row],
        resize_keyboard=True,
        # one_time_keyboard=True,
    )
    return markup


def get_upload_statement_kb() -> ReplyKeyboardMarkup:
    btn_unicredit = KeyboardButton(text="Unicredit")
    btn_revolut = KeyboardButton(text="Revolut")
    btn_back_to_menu = KeyboardButton(text="Back to menu")

    row_first = [btn_unicredit, btn_revolut]
    row_last = [btn_back_to_menu]
    markup = ReplyKeyboardMarkup(
        keyboard=[row_first, row_last],
        resize_keyboard=True,
        # one_time_keyboard=True,
    )
    return markup


def get_back_to_menu_kb() -> ReplyKeyboardMarkup:
    btn_back_to_menu = KeyboardButton(text="Back to menu")
    row_last = [btn_back_to_menu]
    markup = ReplyKeyboardMarkup(
        keyboard=[row_last],
        resize_keyboard=True,
        # one_time_keyboard=True,
    )
    return markup


def get_help_kb() -> ReplyKeyboardMarkup:
    btn_first_setup = KeyboardButton(text="First setup")
    btn_bank_supported = KeyboardButton(text="Bank supported")
    btn_back_to_menu = KeyboardButton(text="Back to menu")

    row_first = [btn_first_setup]
    row_second = [btn_bank_supported]
    row_last = [btn_back_to_menu]

    markup = ReplyKeyboardMarkup(
        keyboard=[row_first, row_second, row_last],
        resize_keyboard=True,
        # one_time_keyboard=True,
    )
    return markup


def get_settings_kb() -> ReplyKeyboardMarkup:
    # settings of my spreadsheet
    btn_SPREADSHEET_ID = KeyboardButton(text="Spreadsheet ID")
    btn_WORKSHEET_INCOME_NAME = KeyboardButton(text="Worksheet income name")
    btn_WORKSHEET_EXPENSES_NAME = KeyboardButton(text="Worksheet expenses name")
    btn_SKIP_STATEMENT_FIRSTLINE = KeyboardButton(text="Skip statement first line")
    btn_INCOME_START_ROW = KeyboardButton(text="Income start row")
    btn_EXPENSES_START_ROW = KeyboardButton(text="Expenses start row")
    btn_SPLIT_INCOME_EXPENSES = KeyboardButton(text="Split income and expenses")

    # general settings
    btn_RETRY_DELAY = KeyboardButton(text="Retry delay")
    btn_MAX_RETRIES = KeyboardButton(text="Max retries")
    btn_SERVICE_ACCOUNT_FILE = KeyboardButton(text="Service account file")
    btn_SAVING_PATH = KeyboardButton(text="Saving path for statement")

    btn_BACK_TO_MENU = KeyboardButton(text="Back to menu")

    row_1 = [btn_SPREADSHEET_ID]
    row_2 = [btn_WORKSHEET_INCOME_NAME, btn_WORKSHEET_EXPENSES_NAME]
    row_3 = [btn_SKIP_STATEMENT_FIRSTLINE]
    row_4 = [btn_INCOME_START_ROW, btn_EXPENSES_START_ROW]
    row_5 = [btn_SPLIT_INCOME_EXPENSES]
    row_6 = [btn_RETRY_DELAY, btn_MAX_RETRIES]
    row_7 = [btn_SERVICE_ACCOUNT_FILE, btn_SAVING_PATH]
    row_8 = [btn_BACK_TO_MENU]

    markup = ReplyKeyboardMarkup(
        keyboard=[row_1, row_2, row_3, row_4, row_5, row_6, row_7, row_8],
        resize_keyboard=True,
        # one_time_keyboard=True,
    )
    return markup
