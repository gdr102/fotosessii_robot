from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.system.lexicon import LEXICON_BUTTONS

async def history_kb(tg_id, current_index, total_count):
    """Клавиатура для навигации по истории генераций (с зацикливанием)."""
    builder = InlineKeyboardBuilder()
    
    # Кнопки навигации
    # % - для зацикливания списка (чтобы после последнего шло первое)
    prev_index = (current_index - 1) % total_count
    next_index = (current_index + 1) % total_count
    
    builder.row(
        InlineKeyboardButton(text="◀️", callback_data=f"history_{tg_id}_{prev_index}"),
        InlineKeyboardButton(text=f"{current_index + 1}/{total_count}", callback_data="ignore"),
        InlineKeyboardButton(text="▶️", callback_data=f"history_{tg_id}_{next_index}")
    )
    builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS["btn_back_to_profile"], callback_data=f"profile_{tg_id}"))
    
    return builder.as_markup()