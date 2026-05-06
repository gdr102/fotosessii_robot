import app.database.models as db

from sqlalchemy import desc, select, update
from sqlalchemy.orm import joinedload

from app.database.models import async_session
from app.functions.get_date import get_msk_time


async def create_user(**data):
    async with async_session() as session:
        user = await session.scalar(select(db.User).where(db.User.tg_id == data['tg_id']))

        if user:
            user.username = data.get('username')
            user.first_name = data.get('first_name')
            await session.commit()
            return user, False

        new_user = db.User(**data)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user, True


async def get_user(tg_id: int, include_generations: bool = False, include_orders: bool = False):
    async with async_session() as session:
        query = select(db.User).where(db.User.tg_id == tg_id)

        if include_generations:
            query = query.options(joinedload(db.User.history))
        if include_orders:
            query = query.options(joinedload(db.User.orders))

        result = await session.execute(query)
        return result.unique().scalar_one_or_none()


async def start_generation(tg_id: int, prompt: str, photo_orig: str):
    async with async_session() as session:
        query = select(db.User.id, db.User.credits).where(db.User.tg_id == tg_id)
        result = await session.execute(query)
        user_data = result.first()

        if not user_data:
            return None

        user_db_id, current_credits = user_data
        if current_credits < 1:
            return 'no_credits'

        new_history = db.History(
            user_id=user_db_id,
            prompt_text=prompt,
            photo_original=photo_orig,
            status=2,
            timestamp=get_msk_time()
        )
        session.add(new_history)

        await session.execute(
            update(db.User)
            .where(db.User.id == user_db_id)
            .values(credits=db.User.credits - 1)
        )

        await session.commit()
        await session.refresh(new_history)
        return new_history.id


async def update_history_result(history_id: int, photo_res: str, shared_prompt_id: int | None = None):
    async with async_session() as session:
        await session.execute(
            update(db.History)
            .where(db.History.id == history_id)
            .values(photo_result=photo_res, status=1)
        )

        if shared_prompt_id is not None:
            await session.execute(
                update(db.Prompt)
                .where(db.Prompt.id == shared_prompt_id)
                .values(count_use=db.Prompt.count_use + 1)
            )

        await session.commit()


async def update_history_status(history_id: int, status: int):
    async with async_session() as session:
        await session.execute(
            update(db.History)
            .where(db.History.id == history_id)
            .values(status=status)
        )
        await session.commit()


async def get_last_generation(tg_id: int):
    async with async_session() as session:
        query = (
            select(db.History)
            .join(db.User)
            .where(db.User.tg_id == tg_id)
            .order_by(desc(db.History.id))
            .limit(1)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def create_order(tg_id: int, stars: int, purchased_credits: int, payment_id: str):
    async with async_session() as session:
        user = await session.scalar(select(db.User).where(db.User.tg_id == tg_id))
        if not user:
            return None

        new_order = db.Order(
            user_id=user.id,
            payment_id=payment_id,
            purchased_credits=purchased_credits,
            spent=stars,
            status='pending',
            timestamp=get_msk_time()
        )
        session.add(new_order)
        await session.commit()
        await session.refresh(new_order)
        return new_order


async def get_pending_order(tg_id: int):
    async with async_session() as session:
        query = (
            select(db.Order)
            .join(db.User)
            .where(db.User.tg_id == tg_id, db.Order.status == 'pending')
            .order_by(desc(db.Order.id))
            .limit(1)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def get_order_by_payment_id(payment_id: str):
    async with async_session() as session:
        return await session.scalar(select(db.Order).where(db.Order.payment_id == payment_id))


async def get_order_by_id(order_id: int):
    async with async_session() as session:
        order = await session.scalar(
            select(db.Order)
            .options(joinedload(db.Order.user))
            .where(db.Order.id == order_id)
        )
        return order


async def refund_order_credits(order_id: int):
    """Возврат звёзд: помечает ордер refunded, списывает кредиты (минимум 0).
    Возвращает (provider_payment_charge_id, stars, tg_id) или None.
    """
    async with async_session() as session:
        order = await session.scalar(
            select(db.Order)
            .options(joinedload(db.Order.user))
            .where(db.Order.id == order_id)
        )
        if not order or order.status != 'completed':
            return None

        user = order.user
        provider_charge_id = order.provider_payment_charge_id
        stars = order.spent
        credits_to_deduct = min(order.purchased_credits, user.credits)
        tg_id = user.tg_id

        await session.execute(
            update(db.Order)
            .where(db.Order.id == order_id)
            .values(status='refunded')
        )
        await session.execute(
            update(db.User)
            .where(db.User.id == user.id)
            .values(credits=db.User.credits - credits_to_deduct)
        )
        await session.commit()
        return provider_charge_id, stars, tg_id


async def complete_order(payment_id: str, provider_payment_charge_id: str):
    async with async_session() as session:
        order = await session.scalar(select(db.Order).where(db.Order.payment_id == payment_id))
        if not order or order.status == 'completed':
            return None

        # Сохраняем значения ДО commit (после commit объект expires)
        purchased_credits = order.purchased_credits
        order_id = order.id
        user_id = order.user_id

        await session.execute(
            update(db.Order)
            .where(db.Order.id == order_id)
            .values(status='completed', provider_payment_charge_id=provider_payment_charge_id)
        )
        await session.execute(
            update(db.User)
            .where(db.User.id == user_id)
            .values(credits=db.User.credits + purchased_credits)
        )
        await session.commit()
        return purchased_credits


async def add_prompt(user_id: int, text: str):
    async with async_session() as session:
        new_prompt = db.Prompt(
            user_id=user_id,
            text=text,
            timestamp=get_msk_time()
        )
        session.add(new_prompt)
        await session.commit()
        await session.refresh(new_prompt)
        return new_prompt.id


async def update_balance(tg_id: int, amount: int):
    async with async_session() as session:
        await session.execute(
            update(db.User)
            .where(db.User.tg_id == tg_id)
            .values(credits=db.User.credits + amount)
        )
        await session.commit()


async def create_shared_prompt(user_id: int, text: str):
    async with async_session() as session:
        new_prompt = db.Prompt(
            user_id=user_id,
            text=text,
            count_use=0,
            timestamp=get_msk_time()
        )
        session.add(new_prompt)
        await session.commit()
        await session.refresh(new_prompt)
        return new_prompt.id


async def get_prompt_by_id(prompt_id: int):
    async with async_session() as session:
        return await session.get(db.Prompt, prompt_id)


async def get_user_by_db_id(user_db_id: int):
    async with async_session() as session:
        return await session.get(db.User, user_db_id)


async def share_last_user_prompt(tg_id: int, file_id: str):
    async with async_session() as session:
        query = (
            select(db.History)
            .join(db.User)
            .where(db.User.tg_id == tg_id)
            .order_by(desc(db.History.id))
            .limit(1)
        )
        result = await session.execute(query)
        history = result.scalar_one_or_none()

        if not history:
            return None

        new_prompt = db.Prompt(
            user_id=history.user_id,
            text=history.prompt_text,
            preview_file_id=file_id,
            count_use=0,
            timestamp=get_msk_time()
        )
        session.add(new_prompt)
        await session.commit()
        await session.refresh(new_prompt)
        return new_prompt.id
