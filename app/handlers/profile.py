from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from app.database.requests import get_user, get_referral_stats
from app.keyboards.profile_kb import profile_kb
from app.functions.navigation import safe_navigate_text
from app.system.lexicon import LEXICON_MESSAGES, LEXICON_BUTTONS

router = Router()


@router.callback_query(F.data.startswith("profile_"))
async def profile_cb(callback: CallbackQuery):
    """Обработчик кнопки профиля. Показывает информацию о балансе пользователя."""
    tg_id = callback.from_user.id
    profile_tg_id = callback.data.split("_")[1]

    # Защита от просмотра чужого профиля через старые сообщения
    if tg_id != int(profile_tg_id):
        await callback.answer(LEXICON_MESSAGES["err_foreign_profile"], show_alert=True)
        return

    user_data = await get_user(tg_id)
    if not user_data:
        await callback.answer(LEXICON_MESSAGES["creative_user_not_found"], show_alert=True)
        return

    message_text = LEXICON_MESSAGES["profile"].format(
        first_name=user_data.first_name,
        credits=user_data.credits
    )


    # Если сообщение содержит фото (например, возврат из творческого режима),
    # редактировать текст нельзя, поэтому удаляем старое сообщение и шлем новое.
    if callback.message.photo:
        try:
            await callback.message.delete()
        except Exception:
            pass
        await callback.message.answer(message_text, reply_markup=await profile_kb(tg_id))
    else:
        try:
            await callback.message.edit_text(message_text, reply_markup=await profile_kb(tg_id))
        except Exception:
            await callback.message.answer(message_text, reply_markup=await profile_kb(tg_id))


@router.callback_query(F.data.startswith("referral_"))
async def referral_info_cb(callback: CallbackQuery):
    """Показывает реферальную ссылку и статистику приглашений."""
    tg_id = callback.from_user.id
    ref_tg_id = callback.data.split("_")[1]

    if tg_id != int(ref_tg_id):
        await callback.answer(LEXICON_MESSAGES["err_foreign_profile"], show_alert=True)
        return

    invited, bonus = await get_referral_stats(tg_id)

    text = LEXICON_MESSAGES["ref_link_info"].format(
        tg_id=tg_id,
        invited=invited,
        bonus=bonus
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=LEXICON_BUTTONS["btn_back_to_profile"], 
            callback_data=f"profile_{tg_id}"
        )]
    ])

    await safe_navigate_text(callback, text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()
