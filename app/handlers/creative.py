import asyncio

from aiogram import Bot, Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import URLInputFile

from app.functions.request import request_api
from app.fsm.creative import CreativeStates
from app.database.requests import (
    start_generation,
    update_balance,
    update_history_result,
    update_history_status,
)
from app.keyboards.common_kb import menu_kb
from app.keyboards.creative_kb import (
    cancel_kb,
    confirm_kb,
    payment_options_kb,
    quality_kb,
    refund_request_kb,
)
from app.system.config import TOKEN_TG
from app.system.lexicon import LEXICON_MESSAGES

router = Router()




async def run_generation(
    user_id: int, prompt: str, photo_orig: str,
    target_msg: types.Message, bot: Bot,
    shared_prompt_id: int | None = None
):
    """Запуск генерации: списание кредита, таймер 0-59 сек, API, результат."""
    history_id = await start_generation(user_id, prompt, photo_orig)

    if history_id is None:
        await target_msg.answer(LEXICON_MESSAGES["creative_user_not_found"], reply_markup=await menu_kb())
        return
    if history_id == 'no_credits':
        await target_msg.answer(
            LEXICON_MESSAGES["creative_no_credits"],
            reply_markup=await payment_options_kb()
        )
        return


    msg = await target_msg.answer(LEXICON_MESSAGES["creative_magic"].format(elapsed=0))


    file = await bot.get_file(photo_orig)
    photo_url = f"https://api.telegram.org/file/bot{TOKEN_TG}/{file.file_path}"


    api_task = asyncio.create_task(request_api(prompt, photo_url))


    for elapsed in range(5, 60, 5):
        if api_task.done():
            break
        await asyncio.sleep(5)
        try:
            await msg.edit_text(LEXICON_MESSAGES["creative_magic"].format(elapsed=elapsed))
        except Exception:
            pass


    if api_task.done():
        response = api_task.result()
    else:
        try:
            await msg.edit_text(
                LEXICON_MESSAGES["creative_delay"],
                reply_markup=await menu_kb()
            )
        except Exception:
            pass
        try:
            response = await asyncio.wait_for(api_task, timeout=240)
        except (asyncio.TimeoutError, Exception):
            response = None

    if response is None:
        await update_history_status(history_id, 0)
        await update_balance(user_id, 1)
        await target_msg.answer(
            LEXICON_MESSAGES["creative_err_timeout"],
            reply_markup=await menu_kb()
        )
        return

    if response.get('status') == 'completed':
        try:
            res_url = response['data'][0]['url']
            result_photo = await target_msg.answer_photo(
                photo=URLInputFile(res_url),
                caption=LEXICON_MESSAGES["creative_ready"],
                reply_markup=await quality_kb()
            )
            await update_history_result(
                history_id,
                result_photo.photo[-1].file_id,
                shared_prompt_id
            )
        except (KeyError, IndexError):
            await update_history_status(history_id, 0)
            await update_balance(user_id, 1)
            await target_msg.answer(
                LEXICON_MESSAGES["creative_err_api"],
                reply_markup=await menu_kb()
            )
    else:
        await update_history_status(history_id, 0)
        await update_balance(user_id, 1)
        status = response.get('status', 'unknown')
        await target_msg.answer(
            LEXICON_MESSAGES["creative_err_status"].format(status=status),
            reply_markup=await menu_kb()
        )


# ─── 1. Вход в творческий режим ───

@router.callback_query(F.data == "creative_mode")
async def creative_start(callback: types.CallbackQuery, state: FSMContext):
    """Инициализация творческого режима. Пользователь должен ввести промпт."""
    await state.set_state(CreativeStates.wait_prompt)
    try:
        await callback.message.edit_text(
            LEXICON_MESSAGES["creative_prompt_req"],
            reply_markup=await cancel_kb()
        )
        bot_msg_id = callback.message.message_id
    except Exception:
        result = await callback.message.answer(
            LEXICON_MESSAGES["creative_prompt_req"],
            reply_markup=await cancel_kb()
        )
        bot_msg_id = result.message_id
    await state.update_data(bot_msg_id=bot_msg_id)
    await callback.answer()


# ─── 2. Получение промпта ───

@router.message(CreativeStates.wait_prompt)
async def get_prompt(message: types.Message, state: FSMContext):
    """Получает текстовый промпт от пользователя и запрашивает фото."""
    data = await state.get_data()

    # Сначала отправляем ответ, потом удаляем старые сообщения
    await state.update_data(prompt=message.text)
    await state.set_state(CreativeStates.wait_photo)
    result = await message.answer(
        LEXICON_MESSAGES["creative_photo_req"],
        reply_markup=await cancel_kb()
    )
    await state.update_data(bot_msg_id=result.message_id)

    # Удаляем сообщение бота "Отправьте промпт..." и сообщение пользователя
    bot_msg_id = data.get('bot_msg_id')
    if bot_msg_id:
        try:
            await message.bot.delete_message(message.chat.id, bot_msg_id)
        except Exception:
            pass
    try:
        await message.delete()
    except Exception:
        pass


# ─── 3. Получение фото ───

@router.message(CreativeStates.wait_photo, F.photo)
async def get_photo(message: types.Message, state: FSMContext, bot: Bot):
    """Получает исходное фото от пользователя и формирует превью-подтверждение."""
    data = await state.get_data()
    prompt = data.get('prompt')

    if not prompt:
        await message.answer(
            LEXICON_MESSAGES["creative_err_no_prompt"],
            reply_markup=await cancel_kb()
        )
        return

    file_id = message.photo[-1].file_id
    shared_prompt_id = data.get('shared_prompt_id')

    # Если это стиль по ссылке — сразу запускаем генерацию, промпт скрыт
    if shared_prompt_id:
        await state.clear()
        # Сначала запускаем генерацию, потом удаляем
        gen_coro = run_generation(
            user_id=message.from_user.id,
            prompt=prompt,
            photo_orig=file_id,
            target_msg=message,
            bot=bot,
            shared_prompt_id=shared_prompt_id
        )
        # Удаляем старые сообщения
        bot_msg_id = data.get('bot_msg_id')
        if bot_msg_id:
            try:
                await message.bot.delete_message(message.chat.id, bot_msg_id)
            except Exception:
                pass
        try:
            await message.delete()
        except Exception:
            pass
        await gen_coro
        return

    # Творческий режим — показываем промпт и просим подтверждение
    safe_prompt = prompt if len(prompt) <= 900 else prompt[:900] + '...'
    await state.update_data(photo_orig=file_id, safe_prompt=safe_prompt)
    await state.set_state(CreativeStates.confirm)

    caption = LEXICON_MESSAGES["creative_confirm"].format(prompt=safe_prompt)
    confirm_msg = await message.answer_photo(
        photo=file_id,
        caption=caption,
        parse_mode="HTML",
        reply_markup=await confirm_kb()
    )

    # Удаляем старые сообщения после отправки подтверждения
    bot_msg_id = data.get('bot_msg_id')
    if bot_msg_id:
        try:
            await message.bot.delete_message(message.chat.id, bot_msg_id)
        except Exception:
            pass
    try:
        await message.delete()
    except Exception:
        pass


# ─── 4. Подтверждение (только творческий режим) ───

@router.callback_query(CreativeStates.confirm, F.data == "creative_yes")
async def process_creative_generation(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Обработчик подтверждения параметров. Запускает генерацию ИИ."""
    data = await state.get_data()
    await state.clear()

    prompt = data.get('prompt')
    photo_orig = data.get('photo_orig')

    if not prompt or not photo_orig:
        await callback.answer(LEXICON_MESSAGES["creative_err_data"], show_alert=True)
        return

    # Отвечаем на callback СРАЗУ, до генерации (иначе timeout через 30 сек)
    await callback.answer()

    # Убираем кнопки с превью
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await run_generation(
        user_id=callback.from_user.id,
        prompt=prompt,
        photo_orig=photo_orig,
        target_msg=callback.message,
        bot=bot,
        shared_prompt_id=data.get('shared_prompt_id')
    )


# ─── 5. Оценка «Ужасно» → запрос возврата ───

@router.callback_query(F.data == "rate_bad")
async def rate_bad(callback: types.CallbackQuery):
    """Меняет клавиатуру на возможность запроса возврата средств за неудачный результат."""
    await callback.message.edit_reply_markup(reply_markup=await refund_request_kb())
    await callback.answer()


@router.callback_query(F.data == "refund_order")
async def refund_order(callback: types.CallbackQuery):
    from aiogram.types import InputMediaPhoto
    from app.keyboards.creative_kb import admin_refund_kb
    from app.system.config import ADMIN_REFUND_CHAT_ID
    from app.database.requests import get_last_generation

    user = callback.from_user
    username_str = f" (@{user.username})" if user.username else ""

    last_gen = await get_last_generation(user.id)
    prompt_text = last_gen.prompt_text if last_gen else "—"
    safe_prompt = prompt_text if len(prompt_text) <= 800 else prompt_text[:800] + "..."

    caption = LEXICON_MESSAGES["creative_refund_req"].format(
        first_name=user.first_name,
        username_str=username_str,
        user_id=user.id,
        safe_prompt=safe_prompt
    )

    # Отправляем оригинал + результат в медиагруппу
    if last_gen and last_gen.photo_original and last_gen.photo_result:
        media = [
            InputMediaPhoto(media=last_gen.photo_original, caption=LEXICON_MESSAGES["creative_refund_orig"]),
            InputMediaPhoto(media=last_gen.photo_result, caption=caption, parse_mode="HTML")
        ]
        await callback.bot.send_media_group(ADMIN_REFUND_CHAT_ID, media=media)
        # Кнопки отдельным сообщением (media_group не поддерживает reply_markup)
        await callback.bot.send_message(
            ADMIN_REFUND_CHAT_ID,
            LEXICON_MESSAGES["creative_refund_admin_btn"].format(first_name=user.first_name, user_id=user.id),
            parse_mode="HTML",
            reply_markup=await admin_refund_kb(callback.from_user.id)
        )
    else:
        await callback.bot.send_photo(
            ADMIN_REFUND_CHAT_ID,
            photo=callback.message.photo[-1].file_id,
            caption=caption,
            parse_mode="HTML",
            reply_markup=await admin_refund_kb(callback.from_user.id)
        )

    # Заменяем кнопку «Вернуть кредит» на «В меню»
    await callback.message.edit_reply_markup(reply_markup=await menu_kb())
    await callback.answer(LEXICON_MESSAGES["creative_refund_sent"], show_alert=True)
