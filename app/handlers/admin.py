import asyncio

from aiogram import Bot, F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
    CallbackQuery,
)

from app.database.requests import get_all_user_tg_ids, get_user, update_balance
from app.fsm.creative import AdminBroadcastStates, AdminPostStates, AdminCreditsStates
from app.system.config import ADMINS, ADMIN_PUBLIC_CHANNEL_ID, BOT_URL
from app.system.lexicon import LEXICON_MESSAGES, LEXICON_BUTTONS

router = Router()

POST_FOOTER = f'\n\n💬 <a href="https://t.me/+huj-lW23s0U2MTRi">Канал</a> | <a href="https://t.me/{BOT_URL}">Бот</a> 🤖'


def is_admin(user_id: int, chat_id: int) -> bool:
    return user_id in ADMINS and chat_id == user_id


async def admin_panel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LEXICON_BUTTONS["btn_adm_broadcast"], callback_data="adm_broadcast")],
        [InlineKeyboardButton(text=LEXICON_BUTTONS["btn_adm_post"], callback_data="adm_post")],
        [InlineKeyboardButton(text=LEXICON_BUTTONS["btn_adm_add_credits"], callback_data="adm_add_credits")],
        [InlineKeyboardButton(text=LEXICON_BUTTONS["btn_adm_remove_credits"], callback_data="adm_remove_credits")],
    ])


async def confirm_broadcast_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON_BUTTONS["btn_adm_start"], callback_data="adm_broadcast_go"),
            InlineKeyboardButton(text=LEXICON_BUTTONS["btn_adm_no"], callback_data="adm_cancel"),
        ]
    ])


async def confirm_post_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=LEXICON_BUTTONS["btn_adm_publish"], callback_data="adm_post_go"),
            InlineKeyboardButton(text=LEXICON_BUTTONS["btn_adm_no"], callback_data="adm_cancel"),
        ]
    ])


async def done_media_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LEXICON_BUTTONS["btn_adm_done_media"], callback_data="adm_post_media_done")]
    ])


# ─── /root ──────────────────────────────────────────────

@router.message(Command("root"))
async def root_cmd(message: Message):
    if not is_admin(message.from_user.id, message.chat.id):
        return

    await message.answer(
        LEXICON_MESSAGES["adm_panel"],
        reply_markup=await admin_panel_kb(),
        parse_mode="HTML"
    )


# ─── Отмена ─────────────────────────────────────────────

@router.callback_query(F.data == "adm_cancel")
async def adm_cancel_cb(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id, callback.message.chat.id):
        return
    await state.clear()
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await callback.message.answer(LEXICON_MESSAGES["adm_cancelled"])
    await callback.answer()


# ═══════════════════════════════════════════════════════════
# РАССЫЛКА В БОТ
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data == "adm_broadcast")
async def adm_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id, callback.message.chat.id):
        return
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await callback.message.answer(LEXICON_MESSAGES["adm_broadcast_text"])
    await state.set_state(AdminBroadcastStates.wait_text)
    await callback.answer()


@router.message(AdminBroadcastStates.wait_text)
async def adm_broadcast_text(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id, message.chat.id):
        return
    await state.update_data(broadcast_text=message.html_text)
    await message.answer(LEXICON_MESSAGES["adm_broadcast_media"])
    await state.set_state(AdminBroadcastStates.wait_media)


@router.message(AdminBroadcastStates.wait_media, F.photo)
async def adm_broadcast_photo(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id, message.chat.id):
        return
    file_id = message.photo[-1].file_id
    await state.update_data(broadcast_media_type="photo", broadcast_media_id=file_id)
    data = await state.get_data()

    await message.answer_photo(
        photo=file_id,
        caption=data["broadcast_text"],
        parse_mode="HTML"
    )
    await message.answer(
        LEXICON_MESSAGES["adm_broadcast_confirm"],
        reply_markup=await confirm_broadcast_kb()
    )
    await state.set_state(AdminBroadcastStates.confirm)


@router.message(AdminBroadcastStates.wait_media, F.video)
async def adm_broadcast_video(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id, message.chat.id):
        return
    file_id = message.video.file_id
    await state.update_data(broadcast_media_type="video", broadcast_media_id=file_id)
    data = await state.get_data()

    await message.answer_video(
        video=file_id,
        caption=data["broadcast_text"],
        parse_mode="HTML"
    )
    await message.answer(
        LEXICON_MESSAGES["adm_broadcast_confirm"],
        reply_markup=await confirm_broadcast_kb()
    )
    await state.set_state(AdminBroadcastStates.confirm)


@router.callback_query(F.data == "adm_broadcast_go", AdminBroadcastStates.confirm)
async def adm_broadcast_go(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not is_admin(callback.from_user.id, callback.message.chat.id):
        return
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    data = await state.get_data()
    await state.clear()

    text = data["broadcast_text"]
    media_type = data["broadcast_media_type"]
    media_id = data["broadcast_media_id"]

    user_ids = await get_all_user_tg_ids()
    total = len(user_ids)
    sent = 0

    for tg_id in user_ids:
        try:
            if media_type == "photo":
                await bot.send_photo(tg_id, photo=media_id, caption=text, parse_mode="HTML")
            else:
                await bot.send_video(tg_id, video=media_id, caption=text, parse_mode="HTML")
            sent += 1
        except Exception:
            pass
        await asyncio.sleep(0.05)

    await callback.message.answer(
        LEXICON_MESSAGES["adm_broadcast_done"].format(sent=sent, total=total)
    )
    await callback.answer()


# ═══════════════════════════════════════════════════════════
# ПОСТ В КАНАЛ
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data == "adm_post")
async def adm_post_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id, callback.message.chat.id):
        return
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await callback.message.answer(LEXICON_MESSAGES["adm_post_text"])
    await state.set_state(AdminPostStates.wait_text)
    await callback.answer()


@router.message(AdminPostStates.wait_text)
async def adm_post_text(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id, message.chat.id):
        return
    await state.update_data(post_text=message.html_text, post_media=[])
    await message.answer(
        LEXICON_MESSAGES["adm_post_media"],
        reply_markup=await done_media_kb()
    )
    await state.set_state(AdminPostStates.wait_media)


@router.message(AdminPostStates.wait_media, F.photo)
async def adm_post_photo(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id, message.chat.id):
        return
    data = await state.get_data()
    media_list = data.get("post_media", [])
    if len(media_list) >= 10:
        return
    media_list.append({"type": "photo", "file_id": message.photo[-1].file_id})
    await state.update_data(post_media=media_list)


@router.message(AdminPostStates.wait_media, F.video)
async def adm_post_video(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id, message.chat.id):
        return
    data = await state.get_data()
    media_list = data.get("post_media", [])
    if len(media_list) >= 10:
        return
    media_list.append({"type": "video", "file_id": message.video.file_id})
    await state.update_data(post_media=media_list)


@router.callback_query(F.data == "adm_post_media_done", AdminPostStates.wait_media)
async def adm_post_media_done(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not is_admin(callback.from_user.id, callback.message.chat.id):
        return
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    data = await state.get_data()
    media_list = data.get("post_media", [])
    text = data["post_text"]

    if not media_list:
        await callback.message.answer("❌ Медиа не отправлено. Отправьте хотя бы один файл.")
        await callback.answer()
        return

    caption_with_footer = text + POST_FOOTER

    if len(media_list) == 1:
        item = media_list[0]
        if item["type"] == "photo":
            await callback.message.answer_photo(
                photo=item["file_id"],
                caption=caption_with_footer,
                parse_mode="HTML"
            )
        else:
            await callback.message.answer_video(
                video=item["file_id"],
                caption=caption_with_footer,
                parse_mode="HTML"
            )
    else:
        group = []
        for i, item in enumerate(media_list):
            caption = caption_with_footer if i == 0 else None
            if item["type"] == "photo":
                group.append(InputMediaPhoto(media=item["file_id"], caption=caption, parse_mode="HTML" if caption else None))
            else:
                group.append(InputMediaVideo(media=item["file_id"], caption=caption, parse_mode="HTML" if caption else None))
        await bot.send_media_group(chat_id=callback.message.chat.id, media=group)

    await callback.message.answer(
        LEXICON_MESSAGES["adm_post_confirm"],
        reply_markup=await confirm_post_kb()
    )
    await state.set_state(AdminPostStates.confirm)
    await callback.answer()


@router.callback_query(F.data == "adm_post_go", AdminPostStates.confirm)
async def adm_post_go(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not is_admin(callback.from_user.id, callback.message.chat.id):
        return
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    data = await state.get_data()
    await state.clear()

    media_list = data.get("post_media", [])
    text = data["post_text"]
    caption_with_footer = text + POST_FOOTER

    if len(media_list) == 1:
        item = media_list[0]
        if item["type"] == "photo":
            await bot.send_photo(
                chat_id=ADMIN_PUBLIC_CHANNEL_ID,
                photo=item["file_id"],
                caption=caption_with_footer,
                parse_mode="HTML"
            )
        else:
            await bot.send_video(
                chat_id=ADMIN_PUBLIC_CHANNEL_ID,
                video=item["file_id"],
                caption=caption_with_footer,
                parse_mode="HTML"
            )
    else:
        group = []
        for i, item in enumerate(media_list):
            caption = caption_with_footer if i == 0 else None
            if item["type"] == "photo":
                group.append(InputMediaPhoto(media=item["file_id"], caption=caption, parse_mode="HTML" if caption else None))
            else:
                group.append(InputMediaVideo(media=item["file_id"], caption=caption, parse_mode="HTML" if caption else None))
        await bot.send_media_group(chat_id=ADMIN_PUBLIC_CHANNEL_ID, media=group)

    await callback.message.answer(LEXICON_MESSAGES["adm_post_done"])
    await callback.answer()


# ═══════════════════════════════════════════════════════════
# НАЧИСЛИТЬ / СПИСАТЬ КРЕДИТЫ
# ═══════════════════════════════════════════════════════════

@router.callback_query(F.data.in_({"adm_add_credits", "adm_remove_credits"}))
async def adm_credits_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id, callback.message.chat.id):
        return
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    action = "add" if callback.data == "adm_add_credits" else "remove"
    await state.update_data(credits_action=action)
    await callback.message.answer(LEXICON_MESSAGES["adm_credits_ask_id"])
    await state.set_state(AdminCreditsStates.wait_tg_id)
    await callback.answer()


@router.message(AdminCreditsStates.wait_tg_id)
async def adm_credits_tg_id(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id, message.chat.id):
        return

    if not message.text or not message.text.strip().isdigit():
        await message.answer(LEXICON_MESSAGES["adm_credits_invalid"])
        return

    tg_id = int(message.text.strip())
    user = await get_user(tg_id)
    if not user:
        await message.answer(LEXICON_MESSAGES["adm_credits_not_found"].format(tg_id=tg_id))
        await state.clear()
        return

    await state.update_data(credits_tg_id=tg_id)
    await message.answer(LEXICON_MESSAGES["adm_credits_ask_amount"])
    await state.set_state(AdminCreditsStates.wait_amount)


@router.message(AdminCreditsStates.wait_amount)
async def adm_credits_amount(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id, message.chat.id):
        return

    if not message.text or not message.text.strip().isdigit():
        await message.answer(LEXICON_MESSAGES["adm_credits_invalid"])
        return

    amount = int(message.text.strip())
    data = await state.get_data()
    await state.clear()

    tg_id = data["credits_tg_id"]
    action = data["credits_action"]

    if action == "add":
        await update_balance(tg_id, amount)
    else:
        await update_balance(tg_id, -amount)

    user = await get_user(tg_id)
    balance = user.credits if user else 0

    if action == "add":
        await message.answer(
            LEXICON_MESSAGES["adm_credits_added"].format(amount=amount, tg_id=tg_id, balance=balance)
        )
    else:
        await message.answer(
            LEXICON_MESSAGES["adm_credits_removed"].format(amount=amount, tg_id=tg_id, balance=balance)
        )
