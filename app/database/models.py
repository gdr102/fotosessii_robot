from typing import List
from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from app.system.config import ENGINE, ECHO

engine = create_async_engine(url=ENGINE, echo=ECHO)
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

# Модель пользователя
class User(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    username: Mapped[str | None] = mapped_column(String)
    first_name: Mapped[str | None] = mapped_column(String)
    credits: Mapped[int] = mapped_column(default=2)
    register_date: Mapped[str] = mapped_column(nullable=False)

    orders: Mapped[List["Order"]] = relationship(
        back_populates="user",
        order_by="desc(Order.id)",
        cascade="all, delete-orphan"
    )
    prompts: Mapped[List["Prompt"]] = relationship(
        back_populates="user",
        order_by="desc(Prompt.id)",
        cascade="all, delete-orphan"
    )
    history: Mapped[List["History"]] = relationship(
        back_populates="user",
        order_by="desc(History.id)",
        cascade="all, delete-orphan"
    )

class Prompt(Base):
    __tablename__ = 'prompts'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    text: Mapped[str] = mapped_column(String, nullable=False)
    preview_file_id: Mapped[str] = mapped_column(String)
    count_use: Mapped[int] = mapped_column(default=0)
    timestamp: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(back_populates="prompts")

class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    payment_id: Mapped[str] = mapped_column(String, nullable=False)
    provider_payment_charge_id: Mapped[str | None] = mapped_column(String, nullable=True)
    purchased_credits: Mapped[int] = mapped_column(default=0)
    spent: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String, default="pending")
    timestamp: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(back_populates="orders")

class History(Base):
    __tablename__ = 'history'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    prompt_text: Mapped[str] = mapped_column(String)
    photo_original: Mapped[str] = mapped_column(String)
    photo_result: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[int] = mapped_column(default=2)
    timestamp: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(back_populates="history")

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
