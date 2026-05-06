async def safe_navigate_text(callback, text, reply_markup=None, parse_mode=None):
    """Навигация к текстовому сообщению.
    Текст→Текст: edit_text. Фото→Текст: удалить + отправить новое.
    """
    if callback.message.photo:
        try:
            await callback.message.delete()
        except Exception:
            try:
                await callback.message.delete_reply_markup()
            except Exception:
                pass
        await callback.message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
    else:
        try:
            await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        except Exception:
            await callback.message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
