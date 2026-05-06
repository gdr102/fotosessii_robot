from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.fsm.creative import CreativeStates
from app.database.requests import get_prompt_by_id, get_user_by_db_id
from app.keyboards.creative_kb import preview_style_kb
from app.system.lexicon import LEXICON_MESSAGES

router = Router()


async def handle_style_start(message: Message, prompt_id: int, state: FSMContext):
    """Обработка /start с аргументом prompt_id — применение стиля.
    Текст промпта скрыт от пользователя.
    """
    prompt_data = await get_prompt_by_id(prompt_id)

    if not prompt_data:
        return False

    author = await get_user_by_db_id(prompt_data.user_id)
    author_name = author.first_name if author else "Участник"

    caption = LEXICON_MESSAGES["style_author"].format(
        author_name=author_name,
        count_use=prompt_data.count_use
    )

    await state.set_state(CreativeStates.wait_photo)
    await state.update_data(prompt=prompt_data.text, shared_prompt_id=prompt_id)


    bot_msg = await message.answer_photo(
        photo=prompt_data.preview_file_id,
        caption=caption,
        parse_mode="HTML",
        reply_markup=await preview_style_kb()
    )
    await state.update_data(bot_msg_id=bot_msg.message_id)
    return True
