from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.system.lexicon import LEXICON_BUTTONS

async def start_kb(tg_id):
    """Основная стартовая клавиатура: выбор стиля на канале, профиль или творческий режим."""
    start_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LEXICON_BUTTONS["btn_choose_style"], url="https://t.me/FotosessII_Pro", style="danger")],
        [InlineKeyboardButton(text=LEXICON_BUTTONS["btn_my_profile"], callback_data=f"profile_{tg_id}", style="primary")],
        [InlineKeyboardButton(text=LEXICON_BUTTONS["btn_creative_mode"], callback_data="creative_mode", style="success")]
    ])

    return start_kb
