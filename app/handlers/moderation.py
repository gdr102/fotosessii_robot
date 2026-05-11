from aiogram import Bot, F, Router, types

from app.database.requests import (
    get_last_generation,
    share_last_user_prompt,
    update_balance,
    update_history_status,
)
from app.functions.request import request_gemini_text
from app.keyboards.common_kb import menu_kb
from app.keyboards.creative_kb import (
    admin_publish_kb,
    publish_choice_kb,
)
from app.system.config import (
    ADMIN_REFUND_CHAT_ID,
    ADMIN_PUBLIC_CHANNEL_ID,
    TOKEN_TG,
)
from app.system.lexicon import LEXICON_MESSAGES, LEXICON_BUTTONS

router = Router()




@router.callback_query(F.data == "rate_good")
async def rate_good_handler(callback: types.CallbackQuery):
    """Спрашивает пользователя о разрешении опубликовать его работу, если оценка 'Отлично'."""
    text = LEXICON_MESSAGES["pub_offer"]

    await callback.message.edit_caption(
        caption=text,
        reply_markup=await publish_choice_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "pub_confirm")
async def send_to_moderation(callback: types.CallbackQuery):
    """Формирует заявку на публикацию и отправляет администратору."""
    await callback.message.edit_caption(
        caption=LEXICON_MESSAGES["pub_sent"],
        reply_markup=await menu_kb()
    )

    user = callback.from_user
    username_str = f" (@{user.username})" if user.username else ""

    last_gen = await get_last_generation(user.id)
    prompt_text = last_gen.prompt_text if last_gen else "—"
    safe_prompt = prompt_text if len(prompt_text) <= 500 else prompt_text[:500] + "..."

    caption = LEXICON_MESSAGES["pub_admin_req"].format(
        first_name=user.first_name,
        username_str=username_str,
        user_id=user.id,
        safe_prompt=safe_prompt
    )

    await callback.bot.send_photo(
        chat_id=ADMIN_REFUND_CHAT_ID,
        photo=callback.message.photo[-1].file_id,
        caption=caption,
        parse_mode="HTML",
        reply_markup=await admin_publish_kb(callback.from_user.id)
    )




@router.callback_query(F.data.startswith("adm_pub_gen_"))
async def admin_publish_gen(callback: types.CallbackQuery, bot: Bot):
    """Администратор: запрашивает ИИ генерацию красивого описания для публикации."""
    user_id = int(callback.data.split("_")[3])
    await callback.answer(LEXICON_MESSAGES["pub_req_sent"])
    

    file_id = callback.message.photo[-1].file_id
    file = await bot.get_file(file_id)
    photo_url = f"https://api.telegram.org/file/bot{TOKEN_TG}/{file.file_path}"
    

    prompt = "Опиши фотографию для телеграм поста в 100-200 символов. Текст должен быть привлекательным, чтобы пользователь увидев фото и описание хотел тоже такое же фото, а сделать пользователь может такое фото через наш бот. Предоставь только один вариант без использования Markdown, чистый привлекательный текст со смайликами."
    
    ai_text = await request_gemini_text(prompt, photo_url)
    
    if not ai_text:
        await callback.answer(LEXICON_MESSAGES["pub_err_gen"], show_alert=True)
        return
    

    current_caption = callback.message.html_text
    
    import re
    if "✨ <b>AI Описание:</b>" in current_caption:
        new_caption = re.sub(
            r"✨ <b>AI Описание:</b>\n.*$", 
            f"✨ <b>AI Описание:</b>\n{ai_text}", 
            current_caption, 
            flags=re.DOTALL
        )
    else:
        if "📝 <b>Промпт:</b>" in current_caption:
            base_caption = current_caption.split("📝 <b>Промпт:</b>")[0]
            new_caption = base_caption + f"✨ <b>AI Описание:</b>\n{ai_text}"
        else:
            new_caption = current_caption + f"\n\n✨ <b>AI Описание:</b>\n{ai_text}"
    
    try:
        await callback.message.edit_caption(
            caption=new_caption,
            reply_markup=callback.message.reply_markup,
            parse_mode="HTML"
        )
    except Exception as e:
        if "message is not modified" in str(e):
            await callback.answer(LEXICON_MESSAGES["pub_text_not_changed"])
        else:
            raise e

@router.callback_query(F.data.startswith("adm_pub_yes_"))
async def admin_publish_final(callback: types.CallbackQuery):
    """Администратор: финальная публикация поста в публичный канал."""
    user_id_tg = int(callback.data.split("_")[3])
    file_id = callback.message.photo[-1].file_id
    caption = callback.message.html_text
    
    import re
    ai_match = re.search(r"✨ <b>AI Описание:</b>\n(.*)", caption, flags=re.DOTALL)
    ai_text = ai_match.group(1) if ai_match else "Посмотрите, какой крутой результат!"
    
    name_match = re.search(r"👤 (.*?) (?:[\(@]|\[)", caption)
    first_name = name_match.group(1) if name_match else "Пользователь"
    
    prompt_id = await share_last_user_prompt(user_id_tg, file_id)

    if not prompt_id:
        await callback.answer("Ошибка: не удалось найти промпт.")
        return

    post_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=LEXICON_BUTTONS["btn_pub_apply"],
                              url=f"https://t.me/FotosessII_robot?start={prompt_id}",
                              style="danger")]
    ])

    final_caption = LEXICON_MESSAGES["pub_final"].format(
        first_name=first_name,
        ai_text=ai_text
    )

    msg = await callback.bot.send_photo(
        chat_id=ADMIN_PUBLIC_CHANNEL_ID,
        photo=file_id,
        caption=final_caption,
        reply_markup=post_kb,
        parse_mode="HTML"
    )

    await callback.message.edit_caption(caption=LEXICON_MESSAGES["pub_success"], reply_markup=None)


@router.callback_query(F.data == "adm_pub_no")
async def admin_reject_pub(callback: types.CallbackQuery):
    """Администратор: отклонение публикации."""
    await callback.message.edit_caption(
        caption=callback.message.caption + LEXICON_MESSAGES["pub_rejected"],
        reply_markup=None,
        parse_mode="HTML"
    )
    await callback.answer("Отклонено")




@router.callback_query(F.data.startswith("adm_ref_"))
async def admin_refund_process(callback: types.CallbackQuery):
    """Администратор: одобрение или отклонение возврата 1 кредита за неудачную генерацию."""
    action = callback.data.split("_")[2]
    user_id = int(callback.data.split("_")[3])

    if action == "ok":
        await update_balance(user_id, 1)

        last_gen = await get_last_generation(user_id)
        if last_gen:
            await update_history_status(last_gen.id, 3)
        await callback.bot.send_message(
            user_id,
            LEXICON_MESSAGES["adm_refund_success"],
            reply_markup=await menu_kb()
        )
        await callback.message.edit_text(
            text=f"{callback.message.text}{LEXICON_MESSAGES['adm_refund_approved']}",
            reply_markup=None
        ) if not callback.message.photo else await callback.message.edit_caption(
            caption=f"{callback.message.caption}{LEXICON_MESSAGES['adm_refund_approved']}",
            reply_markup=None
        )
    else:
        await callback.message.edit_caption(caption=f"{callback.message.caption}{LEXICON_MESSAGES['adm_refund_rejected']}")
