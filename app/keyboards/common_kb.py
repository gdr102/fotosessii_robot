from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.system.lexicon import LEXICON_BUTTONS


async def menu_kb():
    """Создает клавиатуру с единственной кнопкой возврата в главное меню."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LEXICON_BUTTONS["btn_main_menu"], callback_data="main_menu")]
    ])
