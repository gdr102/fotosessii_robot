from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.system.lexicon import LEXICON_BUTTONS

# Кнопка отмены
async def cancel_kb():
    """Возвращает клавиатуру отмены для возврата в главное меню."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LEXICON_BUTTONS["btn_cancel_to_menu"], callback_data="main_menu")]
    ])

# Подтверждение параметров
async def confirm_kb():
    """Клавиатура подтверждения промпта перед началом генерации."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS["btn_yes_all_good"], callback_data="creative_yes"))
    builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS["btn_cancel_to_menu"], callback_data="main_menu"))
    return builder.as_markup()

# Оценка результата
async def quality_kb():
    """Клавиатура для оценки качества сгенерированного изображения."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=LEXICON_BUTTONS["btn_rate_good"], callback_data="rate_good"),
        InlineKeyboardButton(text=LEXICON_BUTTONS["btn_rate_bad"], callback_data="rate_bad")
    )
    return builder.as_markup()

# Запрос возврата
async def refund_request_kb():
    """Клавиатура для запроса возврата кредита, если результат не устроил пользователя."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LEXICON_BUTTONS["btn_refund_credit"], callback_data="refund_order")]
    ])

# Админ-кнопки (Возврат)
async def admin_refund_kb(user_id: int):
    """Клавиатура для администратора для принятия решения о возврате кредита за неудачную генерацию."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=LEXICON_BUTTONS["btn_adm_ref_ok"], callback_data=f"adm_ref_ok_{user_id}"),
        InlineKeyboardButton(text=LEXICON_BUTTONS["btn_adm_ref_no"], callback_data=f"adm_ref_no_{user_id}")
    )
    return builder.as_markup()

# Админ-кнопки (Публикация)
async def admin_publish_kb(user_id: int):
    """Клавиатура для модерации публикаций: генерация текста ИИ, публикация или отклонение."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=LEXICON_BUTTONS["btn_pub_gen"], callback_data=f"adm_pub_gen_{user_id}")
    )
    builder.row(
        InlineKeyboardButton(text=LEXICON_BUTTONS["btn_pub_yes"], callback_data=f"adm_pub_yes_{user_id}"),
        InlineKeyboardButton(text=LEXICON_BUTTONS["btn_pub_no"], callback_data="adm_pub_no")
    )
    return builder.as_markup()

# Кнопка для выбора публикации (Да/Нет)
async def publish_choice_kb():
    """Клавиатура запроса согласия пользователя на публикацию его результата."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON_BUTTONS["btn_yes"], callback_data="pub_confirm"),
            InlineKeyboardButton(text=LEXICON_BUTTONS["btn_no"], callback_data="main_menu")
        ]
    ])

async def payment_options_kb():
    """Клавиатура выбора тарифов для покупки звезд/кредитов."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS["btn_tier_50"], callback_data="buy_credits_50"))
    builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS["btn_tier_100"], callback_data="buy_credits_100"))
    builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS["btn_tier_200"], callback_data="buy_credits_200"))
    builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS["btn_tier_500"], callback_data="buy_credits_500"))
    builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS["btn_tier_1000"], callback_data="buy_credits_1000"))
    builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS["btn_main_menu"], callback_data="main_menu"))
    return builder.as_markup()

async def preview_style_kb():
    """Клавиатура для превью стиля, предлагающая пополнить баланс или вернуться в меню."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS["btn_topup_balance"], callback_data="buy_credits"))
    builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS["btn_main_menu"], callback_data="main_menu"))
    return builder.as_markup()