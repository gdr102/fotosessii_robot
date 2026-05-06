from aiogram import F, Router
from aiogram.types import CallbackQuery, InputMediaPhoto

from app.database.requests import get_user
from app.keyboards.history_kb import history_kb
from app.system.lexicon import LEXICON_MESSAGES

router = Router()


@router.callback_query(F.data.startswith("history_"))
async def history_cb(callback: CallbackQuery):
    """Обработчик просмотра истории генераций.
    Отображает фото и статус. Включает навигацию по элементам."""
    data = callback.data.split("_")
    profile_tg_id = int(data[1])
    tg_id = callback.from_user.id

    # Блокируем просмотр чужой истории через пересланные сообщения
    if tg_id != profile_tg_id:
        await callback.answer(LEXICON_MESSAGES["err_foreign_history"])
        return

    current_index = int(data[2]) if len(data) > 2 else 0
    user_data = await get_user(tg_id, include_generations=True)

    if not user_data or not user_data.history:
        await callback.answer(
            text="У вас еще нет сгенерированных фото 📸",
            show_alert=False
        )
        return

    total_count = len(user_data.history)
    current_index %= total_count
    gen = user_data.history[current_index]

    if gen.status == 0:
        status = 'Ошибка'
    elif gen.status == 1:
        status = 'Успешно'
    elif gen.status == 2:
        status = 'В процессе'
    elif gen.status == 3:
        status = 'Возврат'
    else:
        status = 'Неизвестно'

    text = LEXICON_MESSAGES["history"].format(
        history_id=gen.id,
        status=status,
    )

    photo_source = gen.photo_result or gen.photo_original
    reply_markup = await history_kb(tg_id, current_index, total_count)

    if callback.message.photo:
        # Фото→Фото: редактируем медиа
        media = InputMediaPhoto(media=photo_source, caption=text)
        try:
            await callback.message.edit_media(media=media, reply_markup=reply_markup)
        except Exception:
            await callback.answer()
    else:
        # Текст→Фото: удаляем текст, отправляем фото
        try:
            await callback.message.delete()
        except Exception:
            try:
                await callback.message.delete_reply_markup()
            except Exception:
                pass
        await callback.message.answer_photo(
            photo=photo_source,
            caption=text,
            reply_markup=reply_markup
        )
        await callback.answer()