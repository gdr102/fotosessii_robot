from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.database.requests import get_user
from app.keyboards.profile_kb import profile_kb
from app.system.lexicon import LEXICON_MESSAGES

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
