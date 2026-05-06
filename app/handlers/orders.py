from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext

from app.database.requests import get_user, get_order_by_id, refund_order_credits
from app.fsm.creative import RefundStates
from app.keyboards.common_kb import menu_kb
from app.keyboards.orders_kb import orders_kb, order_detail_kb, admin_order_refund_kb
from app.system.lexicon import LEXICON_MESSAGES
from app.system.config import ADMIN_REFUND_CHAT_ID

router = Router()




@router.callback_query(F.data.startswith("orders_"))
async def orders_cb(callback: types.CallbackQuery):
    """Отображает список покупок (ордеров) пользователя с пагинацией."""
    data = callback.data.split("_")
    tg_id = int(data[1])
    page = int(data[2]) if len(data) > 2 else 0

    if callback.from_user.id != tg_id:
        await callback.answer(LEXICON_MESSAGES["err_foreign_order"], show_alert=True)
        return

    user_data = await get_user(tg_id, include_orders=True)
    if not user_data:
        await callback.answer(LEXICON_MESSAGES["creative_user_not_found"], show_alert=True)
        return

    if not user_data.orders:
        await callback.answer(text=LEXICON_MESSAGES["order_no_history"], show_alert=False)
        return

    kb = await orders_kb(tg_id, page, user_data.orders)

    try:
        await callback.message.edit_text(text=LEXICON_MESSAGES["orders"], reply_markup=kb)
    except Exception:
        await callback.answer()




@router.callback_query(F.data.startswith("order_detail_"))
async def order_detail_cb(callback: types.CallbackQuery):
    """Показывает детальную информацию о конкретном заказе."""
    order_id = int(callback.data.split("_")[2])
    order = await get_order_by_id(order_id)

    if not order:
        await callback.answer(LEXICON_MESSAGES["order_not_found"], show_alert=True)
        return

    if order.user.tg_id != callback.from_user.id:
        await callback.answer(LEXICON_MESSAGES["err_foreign_order"], show_alert=True)
        return

    status_map = {
        "pending": "⏳ Ожидание",
        "completed": "✅ Оплачено",
        "refunded": "↩️ Возвращено",
    }

    text = LEXICON_MESSAGES["order_detail"].format(
        order_id=order.id,
        spent=order.spent,
        credits=order.purchased_credits,
        status=status_map.get(order.status, order.status),
        timestamp=order.timestamp
    )

    if order.provider_payment_charge_id:
        text += LEXICON_MESSAGES["order_detail_tx"].format(tx_id=order.provider_payment_charge_id)

    kb = await order_detail_kb(order.id, callback.from_user.id, order.status)

    try:
        await callback.message.edit_text(text=text, reply_markup=kb, parse_mode="HTML")
    except Exception:
        pass
    await callback.answer()




@router.callback_query(F.data.startswith("order_refund_"))
async def order_refund_start(callback: types.CallbackQuery, state: FSMContext):
    """Начинает процедуру возврата средств за заказ: запрашивает причину."""
    order_id = int(callback.data.split("_")[2])
    order = await get_order_by_id(order_id)

    if not order:
        await callback.answer(LEXICON_MESSAGES["order_not_found"], show_alert=True)
        return

    if order.status == "refunded":
        await callback.answer(LEXICON_MESSAGES["order_refund_already"], show_alert=True)
        return

    if order.status != "completed":
        await callback.answer(LEXICON_MESSAGES["order_refund_not_paid"], show_alert=True)
        return

    await state.set_state(RefundStates.wait_comment)
    await state.update_data(refund_order_id=order_id)

    try:
        await callback.message.edit_text(
            LEXICON_MESSAGES["order_refund_prompt"],
            reply_markup=None
        )
    except Exception:
        await callback.message.answer(LEXICON_MESSAGES["order_refund_prompt"])

    await callback.answer()




@router.message(RefundStates.wait_comment)
async def order_refund_comment(message: types.Message, state: FSMContext):
    """Получает комментарий-причину возврата и пересылает заявку администраторам."""
    data = await state.get_data()
    order_id = data.get('refund_order_id')
    await state.clear()

    order = await get_order_by_id(order_id)
    if not order:
        await message.answer(LEXICON_MESSAGES["order_not_found"], reply_markup=await menu_kb())
        return

    user = message.from_user
    username_str = f" (@{user.username})" if user.username else ""
    comment = message.text or "—"


    await message.answer(
        LEXICON_MESSAGES["order_refund_sent"],
        reply_markup=await menu_kb()
    )


    admin_text = LEXICON_MESSAGES["order_refund_admin_req"].format(
        first_name=user.first_name,
        username_str=username_str,
        user_id=user.id,
        order_id=order.id,
        spent=order.spent,
        credits=order.purchased_credits,
        tx_id=order.provider_payment_charge_id or "—",
        timestamp=order.timestamp,
        comment=comment
    )

    await message.bot.send_message(
        ADMIN_REFUND_CHAT_ID,
        admin_text,
        parse_mode="HTML",
        reply_markup=await admin_order_refund_kb(order.id, user.id)
    )


    try:
        await message.delete()
    except Exception:
        pass




@router.callback_query(F.data.startswith("adm_oref_"))
async def admin_order_refund_decision(callback: types.CallbackQuery, bot: Bot):
    """Обрабатывает решение администратора по возврату звезд: совершает возврат через Bot API."""
    parts = callback.data.split("_")
    action = parts[2]
    order_id = int(parts[3])
    user_tg_id = int(parts[4])

    if action == "ok":
        result = await refund_order_credits(order_id)
        if not result:
            await callback.answer("Ошибка: заказ не найден или уже возвращён.", show_alert=True)
            return

        provider_charge_id, stars, tg_id = result

        if not provider_charge_id:
            await callback.answer(
                LEXICON_MESSAGES["order_refund_err_tx"],
                show_alert=True
            )
            return


        try:
            await bot.refund_star_payment(
                user_id=tg_id,
                telegram_payment_charge_id=provider_charge_id
            )
        except Exception as e:
            await callback.answer(f"Ошибка возврата: {e}", show_alert=True)
            return

        await bot.send_message(
            tg_id,
            f"✅ Возврат одобрен!\n"
            f"💰 {stars} ⭐ возвращены на ваш счёт.\n"
            f"Соответствующие кредиты были списаны с баланса.",
            reply_markup=await menu_kb()
        )

        await callback.message.edit_text(
            text=f"{callback.message.text}\n\n✅ Возврат одобрен. {stars} ⭐ возвращены.",
            reply_markup=None,
            parse_mode="HTML"
        )
    else:
        await bot.send_message(
            user_tg_id,
            "❌ Ваш запрос на возврат отклонён.\n"
            "Если у вас есть вопросы — напишите администратору.",
            reply_markup=await menu_kb()
        )