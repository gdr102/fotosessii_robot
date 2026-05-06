from uuid import uuid4

from aiogram import F, Router, types
from aiogram.types import LabeledPrice, PreCheckoutQuery

from app.database.requests import (
    create_order,
    complete_order,
    get_order_by_payment_id,
    get_pending_order,
)
from app.functions.navigation import safe_navigate_text
from app.keyboards.common_kb import menu_kb
from app.keyboards.creative_kb import payment_options_kb
from app.system.config import PAYMENT_MIN_STARS
from app.system.lexicon import LEXICON_MESSAGES

router = Router()


@router.callback_query(F.data == "buy_credits")
async def buy_credits_start(callback: types.CallbackQuery):
    """Начинает процесс покупки: показывает список тарифов. 
    Блокирует создание нового заказа, если есть незавершенный."""
    pending_order = await get_pending_order(callback.from_user.id)
    if pending_order:
        await callback.answer(LEXICON_MESSAGES["pay_pending_exist"], show_alert=True)
        return

    await safe_navigate_text(
        callback,
        LEXICON_MESSAGES["pay_choose_amount"],
        reply_markup=await payment_options_kb()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("buy_credits_"))
async def buy_credits_amount(callback: types.CallbackQuery):
    """Обрабатывает выбор конкретного тарифа, создает инвойс Telegram Stars."""

    PRICE_TIERS = {
        50: 5,
        100: 10,
        200: 25,
        500: 65,
        1000: 150,
    }

    raw_amount = callback.data.split("_")[-1]
    stars = int(raw_amount)
    credits = PRICE_TIERS.get(stars)

    if not credits:
        await callback.answer(LEXICON_MESSAGES["pay_unknown_tier"], show_alert=True)
        return

    if stars < PAYMENT_MIN_STARS:
        await callback.answer(
            LEXICON_MESSAGES["pay_min_amount"].format(min_stars=PAYMENT_MIN_STARS),
            show_alert=True
        )
        return

    pending_order = await get_pending_order(callback.from_user.id)
    if pending_order:
        await callback.answer(LEXICON_MESSAGES["pay_pending_exist"], show_alert=True)
        return

    invoice_payload = f"topup:{callback.from_user.id}:{stars}:{uuid4().hex}"
    await create_order(callback.from_user.id, stars, credits, invoice_payload)


    prices = [LabeledPrice(label=f"Пополнение {stars} ⭐ ({credits} кредитов)", amount=stars)]

    try:
        await callback.message.answer_invoice(
            title=LEXICON_MESSAGES["pay_invoice_title"],
            description=LEXICON_MESSAGES["pay_invoice_desc"].format(stars=stars, credits=credits),
            prices=prices,
            provider_token="",
            payload=invoice_payload,
            currency="XTR",
        )
    except Exception as e:
        error_text = str(e)
        if "not available" in error_text or "PAYMENT_PROVIDER_INVALID" in error_text:
            await callback.message.answer(
                LEXICON_MESSAGES["pay_err_form"].format(error_text=error_text),
                reply_markup=await menu_kb()
            )
        else:
            await callback.message.answer(
                LEXICON_MESSAGES["pay_err_create"].format(error_text=error_text),
                reply_markup=await menu_kb()
            )
        return
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout_query_handler(pre_checkout_query: PreCheckoutQuery):
    """Проверяет валидность платежа перед финальным списанием средств."""
    payload = pre_checkout_query.invoice_payload
    order = await get_order_by_payment_id(payload)

    if not order or order.status != 'pending':
        await pre_checkout_query.answer(ok=False, error_message=LEXICON_MESSAGES["pay_err_invalid"])
        return

    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: types.Message):
    """Обработка успешной оплаты: начисление кредитов, обновление статуса ордера."""
    payment = message.successful_payment
    if not payment:
        return

    credits = await complete_order(payment.invoice_payload, payment.telegram_payment_charge_id)
    if not credits:
        await message.answer(
            LEXICON_MESSAGES["pay_already_processed"],
            reply_markup=await menu_kb()
        )
        return

    await message.answer(
        LEXICON_MESSAGES["pay_success"].format(credits=credits),
        reply_markup=await menu_kb(),
        message_effect_id="5159385139981059251"
    )
