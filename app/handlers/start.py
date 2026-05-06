from aiogram import Bot, F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from app.keyboards.common_kb import menu_kb
from app.keyboards.start_kb import start_kb
from app.database.requests import create_user
from app.functions.get_date import get_msk_time
from app.system.lexicon import LEXICON_MESSAGES, LEXICON_BUTTONS
from app.system.config import ADMIN_PUBLIC_CHANNEL_ID
from app.handlers.style import handle_style_start

router = Router()

REQUIRED_CHANNEL_URL = "https://t.me/+mEm7tZSp-rBhNTVi"


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    """Проверяет, подписан ли пользователь на обязательный канал."""
    try:
        member = await bot.get_chat_member(ADMIN_PUBLIC_CHANNEL_ID, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False


async def subscribe_kb(args: str | None = None, is_new: bool = False):
    """Клавиатура с кнопками подписки и проверки. Отображается, когда пользователь не подписан."""
    new_flag = "1" if is_new else "0"
    cb_data = f"check_sub_{new_flag}_{args}" if args else f"check_sub_{new_flag}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=LEXICON_BUTTONS["btn_sub"], url=REQUIRED_CHANNEL_URL)],
        [InlineKeyboardButton(text=LEXICON_BUTTONS["btn_sub_check"], callback_data=cb_data)]
    ])


async def run_start_logic(message: Message, user_id: int, args: str | None, state: FSMContext):
    """Основная логика /start после проверки подписки."""
    await state.clear()
    if args and args.isdigit():
        prompt_id = int(args)
        handled = await handle_style_start(message, prompt_id, state)
        if handled:
            return

    await message.answer(
        LEXICON_MESSAGES["welcome"],
        reply_markup=await start_kb(user_id)
    )


@router.message(CommandStart())
async def start_cmd(message: Message, command: CommandObject, state: FSMContext, bot: Bot):
    user_data = {
        "tg_id": message.from_user.id,
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "register_date": get_msk_time()
    }
    _, is_new = await create_user(**user_data)


    # Если пользователь не подписан на обязательный канал, блокируем доступ
    # и выводим кнопку для подписки, передавая аргументы (например, ID стиля)
    if not await is_subscribed(bot, message.from_user.id):
        await message.answer(
            LEXICON_MESSAGES["sub_required"],
            reply_markup=await subscribe_kb(command.args, is_new)
        )
        return

    # Если пользователь новый и уже подписан, начисляем приветственный бонус
    if is_new:
        await message.answer(
            LEXICON_MESSAGES["sub_bonus"],
            reply_markup=await menu_kb()
        )

    await run_start_logic(message, message.from_user.id, command.args, state)


@router.callback_query(F.data.startswith("check_sub"))
async def check_sub_cb(callback: CallbackQuery, bot: Bot, state: FSMContext):
    """Обрабатывает нажатие на кнопку 'Проверить подписку'."""
    if not await is_subscribed(bot, callback.from_user.id):
        await callback.answer(LEXICON_MESSAGES["sub_not_found"], show_alert=True)
        return

    # Парсим параметры: нужно ли дать бонус (is_new) и нужно ли применить стиль (args)
    parts = callback.data.split("_")
    is_new = parts[2] == "1" if len(parts) > 2 else False
    args = parts[3] if len(parts) > 3 else None

    # Удаляем сообщение с требованием подписки, чтобы не засорять чат
    try:
        await callback.message.delete()
    except Exception:
        pass

    if is_new:
        await callback.message.answer(
            LEXICON_MESSAGES["sub_bonus"],
            reply_markup=await menu_kb()
        )

    await run_start_logic(callback.message, callback.from_user.id, args, state)
    await callback.answer()
