from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from app.system.lexicon import LEXICON_BUTTONS

async def orders_kb(tg_id, page, orders_list):
    """Клавиатура списка покупок пользователя с постраничной навигацией."""
    builder = InlineKeyboardBuilder()

    per_page = 5
    total_count = len(orders_list)
    total_pages = (total_count + per_page - 1) // per_page

    # Срез для текущей страницы
    start_idx = page * per_page
    end_idx = start_idx + per_page
    current_orders = orders_list[start_idx:end_idx]

    # Кнопки с покупками — теперь кликабельные
    for order in current_orders:
        builder.row(InlineKeyboardButton(
            text=f"🗓 {order.timestamp} — {order.purchased_credits} кредитов",
            callback_data=f"order_detail_{order.id}"
        ))

    # ЛОГИКА ЗАЦИКЛИВАНИЯ
    # Если страниц больше одной, делаем бесконечную прокрутку
    prev_page = (page - 1) % total_pages
    next_page = (page + 1) % total_pages

    nav_row = [
        InlineKeyboardButton(text="◀️", callback_data=f"orders_{tg_id}_{prev_page}"),
        InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="ignore"),
        InlineKeyboardButton(text="▶️", callback_data=f"orders_{tg_id}_{next_page}")
    ]

    builder.row(*nav_row)
    builder.row(InlineKeyboardButton(text=LEXICON_BUTTONS["btn_back"], callback_data=f"profile_{tg_id}"))

    return builder.as_markup()


async def order_detail_kb(order_id: int, tg_id: int, status: str = "completed"):
    """Клавиатура деталей заказа: кнопка запроса возврата (если не возвращен) и назад."""
    builder = InlineKeyboardBuilder()
    if status != "refunded":
        builder.row(InlineKeyboardButton(
            text=LEXICON_BUTTONS["btn_refund_funds"],
            callback_data=f"order_refund_{order_id}"
        ))
    builder.row(InlineKeyboardButton(
        text=LEXICON_BUTTONS["btn_back"],
        callback_data=f"orders_{tg_id}"
    ))
    return builder.as_markup()


async def admin_order_refund_kb(order_id: int, user_tg_id: int):
    """Клавиатура для администратора: принять решение о возврате звезд (XTR) пользователю."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_BUTTONS["btn_adm_refund_approve"],
            callback_data=f"adm_oref_ok_{order_id}_{user_tg_id}"
        ),
        InlineKeyboardButton(
            text=LEXICON_BUTTONS["btn_adm_refund_reject"],
            callback_data=f"adm_oref_no_{order_id}_{user_tg_id}"
        )
    )
    return builder.as_markup()
