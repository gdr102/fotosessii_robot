from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.keyboards.start_kb import start_kb
from app.system.lexicon import LEXICON_MESSAGES
from app.functions.navigation import safe_navigate_text

router = Router()


from aiogram.fsm.context import FSMContext

@router.callback_query(F.data == "main_menu")
async def main_menu_cb(callback: CallbackQuery, state: FSMContext):
    """Сбрасывает текущее состояние (FSM) и возвращает пользователя в главное меню."""
    await state.clear()
    await callback.answer()
    await safe_navigate_text(
        callback,
        LEXICON_MESSAGES["welcome"],
        reply_markup=await start_kb(callback.from_user.id)
    )


@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()
