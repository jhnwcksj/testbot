import random

from app.database.models import async_session
from app.database.models import User, Product, Item, Material, Promocode, Order
from sqlalchemy import select, update, delete
from sqlalchemy import and_


async def get_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == int(tg_id)))


async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == int(tg_id)))

        if not user:
            session.add(User(tg_id = tg_id))
            await session.commit()

async def set_item(data):
    async with async_session() as session:
        session.add(Item(name = data["name"],description = data["description"], photo = data["photo"], price = data["price"], product = data["product"]))
        await session.commit()

async def set_item_material(data,item_id):
    async with async_session() as session:
        # session.add(Item(name = data["name"],description = data["description"], photo = data["photo"], price = data["price"], product = data["product"]))
        # await session.commit()
        for file_id in data["file_ids"]:
            session.add(Material(file_name=data["name"], 
                                 file_id=file_id, 
                                 description=data["name"], 
                                 item=item_id))
        await session.commit()

# async def set_material(data):
#     async with async_session() as session:
#         session.add(Material(file_name = data["name"], file_id = data["file_id"], description = data["description"], item = data["item"]))
#         await session.commit()


async def set_material(data):
    async with async_session() as session:
        for file_id in data["file_ids"]:
            # Добавляем каждый файл в базу данных
            session.add(Material(file_name=data["name"], 
                                 file_id=file_id, 
                                 description=data["description"], 
                                 item=data["item"]))
        await session.commit()


async def generate_unique_order_id():
    while True:
        # Генерация случайного 8-значного числа
        order_id = random.randint(10000000, 99999999)


        # Проверяем, существует ли уже такой order_id в базе данных
        async with async_session() as session:
            result = await session.scalar(select(Order).where(Order.order_id == str(order_id)))
            # existing_order = result.scalars().first()

            # Если такого order_id нет, возвращаем его
            if not result:
                return order_id

async def set_order(item_data, message, order_id):
    async with async_session() as session:
        user_name = message.from_user.username
        if not user_name:
            user_name = ""
        # Создаем новый заказ
        new_order = Order(
            order_id=str(order_id),  # Уникальный order_id
            user_id=str(message.from_user.id),  # ID пользователя
            name=message.from_user.full_name,  # Имя пользователя
            username=user_name,  # Юзернейм пользователя
            item_id=item_data.id,  # ID товара
            item_name=item_data.name,  # Название товара
            price=item_data.price,  # Цена товара
            proof_type=message.content_type,  # Тип доказательства (фото/документ)
            proof_id=message.photo[-1].file_id if message.photo else message.document.file_id  # ID фото или документа
        )

        # Добавляем заказ в сессию и сохраняем в базе данных
        session.add(new_order)
        await session.commit()

async def delete_order(id):
    async with async_session() as session:
        # Выполняем удаление с помощью запроса
        result = await session.execute(select(Order).filter(Order.order_id == id))
        order = result.scalars().first()

        await session.delete(order)  # Удаляем заказ
        await session.commit()  # Подтверждаем изменения в базе данных
        


# Запрос на получение продукта по ID
async def get_product(product_id):
    async with async_session() as session:
        # Извлекаем результат с помощью scalar_one_or_none, чтобы получить сам продукт
        result = await session.execute(select(Product).where(Product.id == int(product_id)))
        return result.scalar_one_or_none()  # Получаем объект Product или None, если не найден

    
async def get_products():
    async with async_session() as session:
        return await session.scalars(select(Product))
    
async def get_items():
    async with async_session() as session:
        return await session.scalars(select(Item))
    
async def get_item_to_add():
    async with async_session() as session:
        return await session.scalar(select(Item).order_by(Item.id.desc()).limit(1))

async def get_product_item(product_id):
    
    async with async_session() as session:
        return await session.scalars(select(Item).where(Item.product == int(product_id)))

async def get_product_item_search(product_id, name):
    
    async with async_session() as session:
        return await session.scalars(select(Item).where(
            Item.name.ilike(f"%{name}%") | Item.description.ilike(f"%{name}%")
            ).where(Item.product == int(product_id)))
    
async def get_product_item_search_all(name):
    
    async with async_session() as session:
        return await session.scalars(select(Item).where(
            Item.name.ilike(f"%{name}%") | Item.description.ilike(f"%{name}%")
            )
        )
    

    
async def get_item(item_id):
    async with async_session() as session:
        return await session.scalar(select(Item).where(Item.id == int(item_id)))
    
async def get_item_material(item_id):
    async with async_session() as session:
        return await session.scalars(select(Material).where(Material.item == int(item_id)))
    

async def get_order_and_material(order_id: str):
    async with async_session() as session:
        # Выполняем запрос, чтобы найти заказ по order_id
        result = await session.execute(select(Order).filter(Order.order_id == str(order_id)))
        orders = result.scalars().all()

        if not orders:
            return None, None  # Если заказ не найден, возвращаем None для заказа и материала

        # Ищем материал по item_id заказа
        materials = []
        for order in orders:
            # Ищем все материалы для каждого item_id заказа
            result = await session.execute(select(Material).filter(Material.item == int(order.item_id)))
            materials_for_order = result.scalars().all()  # Получаем все материалы для каждого заказа
            materials.extend(materials_for_order)  # Добавляем найденные материалы в общий список


        return orders, materials  # Возвращаем заказ и найденный материал
    

async def get_user_by_id(tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))
    
async def get_promo(code):
    async with async_session() as session:
        return await session.scalar(select(Promocode).where(Promocode.code == code))
    
    
async def set_user_used_promo(tg_id,code):
    async with async_session() as session: 
        async with session.begin():  
            result = await session.execute(select(User).filter_by(tg_id=tg_id))
            user = result.scalars().first()  

            if user:
                user.is_promo = True 
                user.was_promo = True
                user.promocode = code
                await session.commit()
                return True 
            else:
                return False 
            
async def set_user_used_promo_false(tg_id):
    async with async_session() as session: 
        async with session.begin():  
            result = await session.execute(select(User).filter_by(tg_id=int(tg_id)))
            user = result.scalars().first()  

            if user:
                user.is_promo = False
                await session.commit()
                return True 
            else:
                return False 
            
async def set_promo_used_count(code):
    async with async_session() as session:
        async with session.begin():  
            result = await session.execute(select(Promocode).filter_by(code=code))
            promo = result.scalars().first()  

            if promo:
                promo.used_count += 1
                await session.commit()
                return True 
            else:
                return False 
