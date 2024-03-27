from aiogram import F, Router, types
from aiogram.enums import ChatAction
from aiogram.types import ReplyKeyboardRemove

from keyboards.common_keyboards import ButtonText

router = Router(name=__name__)


@router.message()
async def echo_message(message: types.Message):
    if message.poll:
        await message.forward(chat_id=message.chat.id)
        return
    await message.answer(
        text="Unexpected, try again",
        parse_mode=None,
    )
