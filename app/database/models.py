from datetime import datetime
from sqlalchemy import BigInteger, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

import os
from dotenv import load_dotenv

load_dotenv()
engine = create_async_engine(url=os.getenv('SQLALCHEMY_URL2'))

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    phone: Mapped[str] = mapped_column(default="")
    is_promo: Mapped[bool] = mapped_column(default=False)
    was_promo: Mapped[bool] = mapped_column(default=False)
    promocode: Mapped[str] = mapped_column(String(120),default="")


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(120))

class Item(Base):
    __tablename__ = 'items'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(250))
    photo: Mapped[str] = mapped_column(String(120))
    price: Mapped[int] = mapped_column()
    product: Mapped[int] = mapped_column(ForeignKey('products.id'))

class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[str] = mapped_column(String(100))
    user_id: Mapped[str] = mapped_column(String(120))
    name: Mapped[str] = mapped_column(String(120))
    username: Mapped[str] = mapped_column(String(120))
    item_id: Mapped[int] = mapped_column()
    item_name: Mapped[str] = mapped_column(String(120))
    price: Mapped[int] = mapped_column()
    proof_type: Mapped[str] = mapped_column(String(120))
    proof_id: Mapped[str] = mapped_column(String(120))

class Material(Base):
    __tablename__ = 'materials'

    id: Mapped[int] = mapped_column(primary_key=True)
    file_name: Mapped[str] = mapped_column(String(150))
    file_id: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(String(150))
    item: Mapped[int] = mapped_column(ForeignKey('items.id'))

class Promocode(Base):
    __tablename__ = 'promocodes'

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(150))
    discount: Mapped[int] = mapped_column()
    used_count: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

