
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from app.system.config import TOKEN_TG
from app.database.models import async_main
from app.handlers import start, profile, orders, history, creative, payment, moderation, menu, admin


def create_dispatcher() -> Dispatcher:
    storage = MemoryStorage()
    dispatcher = Dispatcher(storage=storage)
    dispatcher.include_routers(
        admin.router,
        payment.router,      
        start.router,
        profile.router,
        orders.router,
        history.router,
        creative.router,
        moderation.router,
        menu.router,      
    )
    return dispatcher


async def main() -> None:
    await async_main()

    bot = Bot(
        token=TOKEN_TG,
        default=DefaultBotProperties(parse_mode='HTML')
    )
    dispatcher = create_dispatcher()

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
