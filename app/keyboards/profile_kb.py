from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.system.lexicon import LEXICON_BUTTONS

async def profile_kb(tg_id):
    """Клавиатура профиля: история, покупки, пополнение, возврат в меню."""
    profile_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LEXICON_BUTTONS["btn_gen_history"], callback_data=f"history_{tg_id}")],
        [InlineKeyboardButton(text=LEXICON_BUTTONS["btn_purchases_history"], callback_data=f"orders_{tg_id}")],
        [InlineKeyboardButton(text=LEXICON_BUTTONS["btn_topup_no_emoji"], callback_data="buy_credits")],
        [InlineKeyboardButton(text=LEXICON_BUTTONS["btn_back"], callback_data="main_menu")]
    ])

    return profile_kb
