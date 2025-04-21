
import random
from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


import app.keyboards as kb
import app.database.requests as rq

import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_ID = int(os.getenv('ADMIN_ID',0))
SUPPORT_ID = int(os.getenv('SUPPORT_ID',0))

router = Router()


class AddItem(StatesGroup):
    name = State()
    description = State()
    price = State()
    product = State()
    photo = State()
    item_file_id = State()
    confirm = State()

class AddMaterial(StatesGroup):
    name = State()
    description = State()
    file_id = State()
    item_id = State()

class GetDocument(StatesGroup):
    doc_id = State()

class SendDocument(StatesGroup):
    send_doc_id = State()

class GetPhoto(StatesGroup):
    photo_id = State()

class SendPhoto(StatesGroup):
    send_photo_id = State()

class BuyItem(StatesGroup):
    proof = State()

class GetMessage(StatesGroup):
    text_id = State()

class SearchItem(StatesGroup):
    search_id = State()
    search_name = State()

class SearchAllItem(StatesGroup):
    search_name_all = State()

class Promocode(StatesGroup):
    promocode = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    
    isNew = await rq.set_user(message.from_user.id)

    if isNew:
        await message.bot.send_message(
            ADMIN_ID,
            f"<b>Приветствуем нового пользователя:</b>\n\n"
            f"ID пользователя: {message.from_user.id}\n"
            f"Имя: {message.from_user.full_name}\n"
            f"Пользователь: @{message.from_user.username}",
            parse_mode="HTML"
        )

    if message.from_user.id == ADMIN_ID:
        await message.reply("Добро пожаловать администратор.",
                            parse_mode="HTML",
                            reply_markup=kb.main_admin)
        
    elif message.from_user.id == SUPPORT_ID:
        await message.reply("Добро пожаловать Support.",
                            parse_mode="HTML",
                            reply_markup=kb.main_admin)
    
    else:
        await message.answer_photo(photo='AgACAgIAAxkBAAMNZ9IEChbnZcD4iui7Whd_byZsz3gAAqTtMRviKJBKcE2KI1-H-8YBAAMCAAN5AAM2BA',
                        caption='👋<b>Добро пожаловать.</b>\n\nВпервые у нас? Тогда обязательно ознакомься 👇\n\nМы продаем материалы, которые будут полезны как и <b>для студентов</b>, так и <b>для начинающих программистов и дизайнеров</b> по <b>доступным ценам</b>. В клавиатуре снизу Вы можете воспользоваться меню.\n\n<b>🔥 Удачных покупок!</b>',
                         parse_mode="HTML", 
                         reply_markup=kb.main)




@router.message(F.text == "🛠️ Команды администратора 🛠️")
async def cmd_admin_commands(message : Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("У вас нет прав для этого действия.")
        return
    
    await message.answer('Список комманд:\n\n<code>/get_users</code> - Показать всех пользователей\n\n<code>/add_new_item</code> - Добавить новый товар\n\n<code>/add_new_material</code> - Добавить материал к товару\n\n<code>/get_document</code> - Получить документ по ID\n\n<code>/send_document</code> - Скидывать документ и получить его ID\n\n<code>/confirm_order [ID заказа]</code> - Подтвердить заказ по ID\n\n<code>/cancel_order [ID заказа]</code> - Отменить заказ по ID\n\n<code>/get_photo</code> - Получить фото по ID\n\n<code>/get_document</code> - Получить документ по ID\n\n<code>/send_photo</code> - Отправить фото и получить его ID\n\n<code>/send_document</code> - Отправить документ и получить его ID',
                         parse_mode="HTML",
                         reply_markup=kb.admin_commands)

@router.message(Command("get_users"))
async def get_users_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔️ У вас нет доступа к этой команде.")

    users = await rq.get_all_users()

    if not users:
        return await message.answer("В базе данных пока нет пользователей.")

    MAX_LENGTH = 4000
    text = "👥 <b>Список пользователей:</b>\n\n"
    messages_to_send = []

    for i, user in enumerate(users, 1):
        try:
            chat = await message.bot.get_chat(user.tg_id)
            username = f"@{chat.username}" if chat.username else "—"
            full_name = chat.full_name or "—"
        except Exception as e:
            username = "—"
            full_name = "—"

        user_info = (
            f"<b>{i}.</b> ID: <code>{user.tg_id}</code>\n"
            f"👤 Username: {username}\n"
            f"📝 Fullname: {full_name}\n"
            f"📞 Телефон: {user.phone or '—'}\n"
            f"🎁 Промо: {user.is_promo}\n"
            f"Был промо: {user.was_promo}\n"
            f"🔖 Промокод: {user.promocode or '—'}\n\n"
        )

        if len(text) + len(user_info) > MAX_LENGTH:
            messages_to_send.append(text)
            text = ""
        text += user_info

    if text:
        messages_to_send.append(text)

    for part in messages_to_send:
        await message.answer(part, parse_mode="HTML")



@router.message(Command('add_new_item'))
async def cmd_add_item(message: Message, state : FSMContext):

    if message.from_user.id != ADMIN_ID:
        await message.reply("У вас нет прав для этого действия.")
        return
    
    await state.set_state(AddItem.name)
    await message.reply("Назовите ваш товар", reply_markup=kb.cancel_add)

@router.message(AddItem.name)
async def name_of_item(message: Message, state: FSMContext):

    name_text = message.text

    if len(name_text) > 100:
        await message.answer("Описание слишком длинное. Пожалуйста, сократите его до 100 символов.")
        return 
    
    await state.update_data(name=message.text)
    await state.set_state(AddItem.description)
    await message.answer('Напишите описание для вашего товара', reply_markup=kb.cancel_add)

@router.message(AddItem.description)
async def description_of_item(message: Message, state: FSMContext):

    description_text = message.text

    if len(description_text) > 250:
        await message.answer("Описание слишком длинное. Пожалуйста, сократите его до 250 символов.")
        return 
    
    await state.update_data(description=message.text)
    await state.set_state(AddItem.price)
    await message.answer('Напишите цену для вашего товара', reply_markup=kb.cancel_add)

@router.message(AddItem.price)
async def price_of_item(message: Message, state: FSMContext):
    
    try:
        await state.update_data(price=int(message.text))
    except:
        await message.answer('Произошла ошибка. Попробуйте написать еще раз (цифру)')
        return
    
    all_products = await rq.get_products()
    product_name = ""
    for product in all_products:
        product_name = product_name + "["+str(product.id) + "]" + " " + product.name + "\n"
    
    await state.set_state(AddItem.product)
    await message.answer(f'Введите id для какого каталога принадлежит ваш товар\n\n{product_name}', reply_markup=kb.cancel_add)
    
@router.message(AddItem.product)
async def item_to_product(message : Message, state: FSMContext):
    
    try:
        await state.update_data(product=int(message.text))
    except:
        await message.answer('Произошла ошибка. Попробуйте написать еще раз')
        return

    await state.set_state(AddItem.photo)
    await message.answer('Предоставьте фото для вашего товара', reply_markup=kb.cancel_add)

# @router.message(AddItem.photo, F.photo)
# async def item_photo(message: Message, state: FSMContext):
#     if message.text == "Нету фото":
#         await state.update_data(photo="")
#     else:
#         try:
#             await state.update_data(photo=message.photo[-1].file_id)
#         except:
#             await message.answer('Произошла ошибка. Предоставьте фото еще раз')
#             return
#     data = await state.get_data()
#     await rq.set_item(data)
#     await message.answer(f'✅ Спасибо, товар успешно добавлен в базу.')
#     await state.clear()

@router.message(AddItem.photo, F.photo)
async def item_photo(message: Message, state: FSMContext):
    if message.text == "Нету фото":
        await state.update_data(photo="")
    else:
        try:
            await state.update_data(photo=message.photo[-1].file_id)
        except:
            await message.answer('Произошла ошибка. Предоставьте фото еще раз')
            return
    await state.set_state(AddItem.item_file_id)
    await message.answer('Предоставьте файл', reply_markup=kb.cancel_add)

@router.message(AddItem.item_file_id, F.document)
async def add_item_document_material(message: Message, state: FSMContext):
    # Получаем данные о текущем материале
    data = await state.get_data()
    # Создаем список для хранения file_id
    if 'file_ids' not in data:
        file_ids = []
    else:
        file_ids = data['file_ids']
    
    # Добавляем новый файл в список
    file_ids.append(message.document.file_id)
    await state.update_data(file_ids=file_ids)

    # Проверяем, если прислано несколько файлов, уведомляем пользователя
    if len(file_ids) == 1:
        await message.answer('Файл добавлен, если хотите добавить еще, отправьте еще файл.')
    else:
        await message.answer(f'Добавлено {len(file_ids)} файлов.')

    # Переходим к следующему состоянию (ID материала)
    await state.set_state(AddItem.confirm)
    await message.answer('Введите слово <code>Подтверждаю</code> для размещения товара', 
                         reply_markup=kb.cancel_add,
                         parse_mode="HTML")

@router.message(AddItem.confirm)
async def confirm_material(message:Message,state:FSMContext):
    if message.text == 'Подтверждаю':
        data = await state.get_data()
        await rq.set_item(data)
        get_item_last = await rq.get_item_to_add()
        await rq.set_item_material(data,get_item_last.id)
        await message.answer(f'✅ Спасибо, товар успешно добавлен в базу.')
        await state.clear()
    else:
        await message.answer('Введите слово <code>Подтверждаю</code> для размещения товара', 
                             reply_markup=kb.cancel_add,
                             parse_mode="HTML")


@router.message(Command('add_new_material'))
async def cmd_add_material(message: Message, state : FSMContext):

    if message.from_user.id != ADMIN_ID:
        await message.reply("У вас нет прав для этого действия.")
        return
    
    await state.set_state(AddMaterial.name)
    await message.reply("Имя материала", reply_markup=kb.cancel_add)

@router.message(AddMaterial.name)
async def name_of_material(message: Message, state: FSMContext):
    
    await state.update_data(name=message.text)
    await state.set_state(AddMaterial.description)
    await message.answer('Напишите описание для вашего материала', reply_markup=kb.cancel_add)

@router.message(AddMaterial.description)
async def name_of_item(message: Message, state: FSMContext):
    
    await state.update_data(description=message.text)
    await state.set_state(AddMaterial.file_id)
    await message.answer('Предоставьте файл', reply_markup=kb.cancel_add)

@router.message(AddMaterial.file_id, F.document)
async def document_material(message: Message, state: FSMContext):
    # Получаем данные о текущем материале
    data = await state.get_data()
    # Создаем список для хранения file_id
    if 'file_ids' not in data:
        file_ids = []
    else:
        file_ids = data['file_ids']
    
    # Добавляем новый файл в список
    file_ids.append(message.document.file_id)
    await state.update_data(file_ids=file_ids)

    # Проверяем, если прислано несколько файлов, уведомляем пользователя
    if len(file_ids) == 1:
        await message.answer('Файл добавлен, если хотите добавить еще, отправьте еще файл.')
    else:
        await message.answer(f'Добавлено {len(file_ids)} файлов.')

    # Переходим к следующему состоянию (ID материала)
    await state.set_state(AddMaterial.item_id)
    all_items = await rq.get_items()
    item_name = ""
    for item in all_items:
        item_name = item_name + "[" + str(item.id) + "]" + " " + item.name + "\n"
    
    await message.answer(f'Введите ID для которого подходит ваш материал\n\n{item_name}', reply_markup=kb.cancel_add)


@router.message(AddMaterial.item_id)
async def material_to_item(message : Message, state: FSMContext):
    await state.update_data(item=int(message.text))
    try:
        data = await state.get_data()
        await rq.set_material(data)
        await message.answer(f'✅ Спасибо, материал успешно добавлен в базу.')
        await state.clear()
    except:
        await message.answer('Произошла ошибка. Попробуйте написать еще раз', reply_markup=kb.cancel_add)
        return
    

@router.callback_query(F.data == 'cancel_to_add')
async def cancel_to_add(callback : CallbackQuery, state : FSMContext):
    await callback.message.delete()
    await state.clear()
    await callback.message.answer('Процесс успешно отменен! ✅')

    


@router.message(Command('confirm_order'))
async def confirm_order(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.reply("У вас нет прав для этого действия.")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        await message.reply("Использование команды: /confirm_order [order_id]")
        return

    order_id = command_parts[1] 

    orders, materials = await rq.get_order_and_material(order_id)

    if not orders:
        await message.reply(f"Заказ с ID {order_id} не найден.")
        return

    if not materials:
        await message.reply(f"Материал для заказа {order_id} не найден.")
        return

    user_id = orders[0].user_id  # Используем user_id из первого заказа
    await rq.set_user_used_promo_false(user_id)
    await message.bot.send_message(
        user_id,
        f"Ваш заказ на товар <b>{orders[0].item_name}</b> был подтвержден ✅\n\n<b>Вот ваш материал!</b>",
        parse_mode="HTML"
    )

    # Для каждого материала отправляем файл
    for material in materials:
        file_id = material.file_id  # Получаем file_id материала

        # Отправляем каждый материал
        await message.bot.send_document(
            user_id,  # Отправляем документ пользователю
            document=file_id,  # file_id материала
            caption="",  # Оставляем пустую подпись, так как текст отправляется выше
            parse_mode="HTML"
        )

    await message.reply(f"Материалы для заказа <b>{order_id}</b> отправлены пользователю ✅", parse_mode="HTML")

    # Удаляем заказ
    await rq.delete_order(order_id)

@router.message(Command('cancel_order'))
async def cancel_order(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.reply("У вас нет прав для этого действия.")
        return
    
    command_parts = message.text.split()
    if len(command_parts) != 2:
        await message.reply("Использование команды: /cancel_order [order_id]")
        return

    order_id = command_parts[1]  # Получаем order_id из текста команды

    # Получаем все заказы и материалы
    orders, materials = await rq.get_order_and_material(order_id)

    if not orders:
        await message.reply(f"Заказ с ID {order_id} не найден.")
        return

    if not materials:
        await message.reply(f"Материал для заказа {order_id} не найден.")
        return

    await message.reply(f"Заказ <b>{order_id}</b> успешно отменен ✅", parse_mode="HTML")

    # Удаляем заказ
    await rq.delete_order(order_id)


@router.message(Command('get_document'))
async def get_document(message : Message, state : FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.reply("У вас нет прав для этого действия.")
        return
    
    await state.set_state(GetDocument.doc_id)
    await message.reply('Напишите ID документа')

@router.message(GetDocument.doc_id)
async def get_document_by_id(message : Message, state: FSMContext):
    doc_data = message.text
    try:
        await message.answer_document(document=f"{doc_data}", caption=f"ID документа: <code>{doc_data}</code>",
                                      parse_mode="HTML")
    except:
        await message.answer('Не найдено, попробуйте еще раз')
    await state.clear()


@router.message(Command('send_document'))
async def send_document(message : Message, state : FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.reply("У вас нет прав для этого действия.")
        return
    
    await state.set_state(SendDocument.send_doc_id)
    await message.reply('Скидывайте файл')

@router.message(SendDocument.send_doc_id, F.document)
async def get_document_id(message : Message, state: FSMContext):
    doc_id = message.document.file_id
    try:
        await message.answer_document(document=f"{doc_id}",caption=f"ID документа: <code>{doc_id}</code>",
                                      parse_mode="HTML")
    except:
        await message.answer('Не найдено, попробуйте еще раз')
    await state.clear()



    
@router.message(Command('get_photo'))
async def get_photo(message : Message, state : FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.reply("У вас нет прав для этого действия.")
        return

    await state.set_state(GetPhoto.photo_id)
    await message.reply('Напишите ID фото')

@router.message(GetPhoto.photo_id)
async def get_photo_by_id(message : Message, state: FSMContext):
    photo_data = message.text
    try:
        await message.answer_photo(photo=f"{photo_data}",caption=f"ID фото: <code>{photo_data}</code>",
                                   parse_mode="HTML")
    except:
        await message.answer('Не найдено, попробуйте еще раз')
    await state.clear()

@router.message(Command('send_photo'))
async def get_document(message : Message, state : FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.reply("У вас нет прав для этого действия.")
        return
    
    await state.set_state(SendDocument.send_doc_id)
    await message.reply('Скидывайте фото')

@router.message(SendDocument.send_doc_id, F.photo)
async def get_photo_id(message : Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    try:
        await message.answer_photo(photo=f"{photo_id}",caption=f"ID фото: <code>{photo_id}</code>",
                                      parse_mode="HTML")
    except:
        await message.answer('Не найдено, попробуйте еще раз')
    await state.clear()
    


@router.message(Command('my_id'))
async def get_my_id(message : Message):
    await message.reply(f'Твой ID: {message.from_user.id}\nИмя: {message.from_user.first_name}\nПользователь: @{message.from_user.username}')





















@router.message(F.text == '🛒 Посмотреть каталог')
async def get_products(message : Message):
    await message.answer(text='Активные каталоги в магазине:', reply_markup=await kb.products())


@router.callback_query(F.data.startswith('product_'))
async def product(callback: CallbackQuery):
    await callback.answer("")
    product_id = callback.data.split('_')[1]
    await callback.message.edit_text('Выберите товар по каталогу', 
                                     reply_markup=await kb.items(product_id, page=1))


@router.callback_query(F.data.startswith('items_'))
async def items_page(callback: CallbackQuery):
    await callback.answer("")  # Ответ на запрос
    data = callback.data.split('_')
    product_id = int(data[1])  # Извлекаем id товара
    page = int(data[2])  # Извлекаем номер страницы
    
    # Отправляем клавиатуру для выбора элемента товара с нужной страницей
    await callback.message.edit_text('Выберите элемент товара',
                                      reply_markup=await kb.items(product_id, page))


@router.callback_query(F.data.startswith('item_'))
async def item(callback: CallbackQuery, state: FSMContext):
    item_data = await rq.get_item(callback.data.split('_')[1])
    await state.update_data(item=item_data)
    await callback.answer("")

    # Получаем состояние, чтобы удалить предыдущие сообщения товара
    state_data = await state.get_data()
    previous_message_id = state_data.get("last_item_message_id")

    if previous_message_id:
        try:
            await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=previous_message_id)
        except Exception as e:
            pass

    check_user = await rq.get_user_by_id(callback.from_user.id)
    if check_user.is_promo:
        try:
            if not item_data.photo:
                sent_message = await callback.message.answer(f'{item_data.name}\n\n<b>💰 Цена: <s>{item_data.price}</s> {item_data.price - 3000}тг (Промокод активирован!)</b>\n\nЧто вы получите:\n{item_data.description}', 
                                                        parse_mode="HTML",
                                                        reply_markup=kb.buy)
            else:
                sent_message = await callback.message.answer_photo(photo=item_data.photo,
                                                                caption=f'{item_data.name}\n\n<b>💰 Цена: <s>{item_data.price}</s> {item_data.price - 3000}тг (Промокод активирован!)</b>\n\nЧто вы получите:\n{item_data.description}', 
                                                                parse_mode="HTML",
                                                                reply_markup=kb.buy)

            # Сохраняем message_id нового сообщения товара
            await state.update_data(last_item_message_id=sent_message.message_id)
        
        except Exception as e:
            return
        
    else:
        try:
            if not item_data.photo:
                sent_message = await callback.message.answer(f'{item_data.name}\n\n<b>💰 Цена: {item_data.price}тг</b>\n\nЧто вы получите:\n{item_data.description}', 
                                                        parse_mode="HTML",
                                                        reply_markup=kb.buy)
            else:
                sent_message = await callback.message.answer_photo(photo=item_data.photo,
                                                                caption=f'{item_data.name}\n\n<b>💰 Цена: {item_data.price}тг</b>\n\nЧто вы получите:\n{item_data.description}', 
                                                                parse_mode="HTML",
                                                                reply_markup=kb.buy)

            # Сохраняем message_id нового сообщения товара
            await state.update_data(last_item_message_id=sent_message.message_id)
        
        except Exception as e:
            return

        
    
        
@router.callback_query(F.data == 'buy_item')
async def buy(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    item_data = user_data.get('item') 
    await callback.answer("")

    await callback.message.delete()
    check_user = await rq.get_user_by_id(callback.from_user.id)
    if check_user.is_promo:
        try:
            await callback.message.answer(f'Название: <b>{item_data.name}</b>\n\nЦена: <s>{item_data.price}</s> <b>{item_data.price - 3000}тг</b>\n\nВыберите способ оплаты: ',
                                    parse_mode="HTML",
                                    reply_markup=kb.payment_method)
        except:
            return
    else:
        try:
            await callback.message.answer(f'Название: <b>{item_data.name}</b>\n\nЦена: <b>{item_data.price}тг</b>\n\nВыберите способ оплаты: ',
                                    parse_mode="HTML",
                                    reply_markup=kb.payment_method)
        except:
            return
    
    

    
@router.callback_query(F.data == 'halyk')
async def payment_method(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    item_data = user_data.get('item') 
    check_user = await rq.get_user_by_id(callback.from_user.id)
    if check_user.is_promo:
        await callback.message.edit_text(f'Способ оплаты: [ Halyk Bank ] (KZT)\n\nСумма к оплате: <b>{item_data.price - 3000}тг</b>\n\nСчет Халык Банк:\n<code>4405 6397 2245 8955</code>\n\nПривет! Можешь перевести с любой банковской карты, на Халык Банк. После этого сделай скрин или файл и отправь мне. Обработка скриншота требует время. После проверки будет выдана доступ к материалу☺️⭐️\n\n<b>После оплаты обязательно нажми на кнопку снизу!</b> 👇',
                                     parse_mode="HTML",
                                     reply_markup=kb.i_paid)
    else:
        await callback.message.edit_text(f'Способ оплаты: [ Halyk Bank ] (KZT)\n\nСумма к оплате: <b>{item_data.price}тг</b>\n\nСчет Халык Банк:\n<code>4405 6397 2245 8955</code>\n\nПривет! Можешь перевести с любой банковской карты, на Халык Банк. После этого сделай скрин или файл и отправь мне. Обработка скриншота требует время. После проверки будет выдана доступ к материалу☺️⭐️\n\n<b>После оплаты обязательно нажми на кнопку снизу!</b> 👇',
                                     parse_mode="HTML",
                                     reply_markup=kb.i_paid)
    
@router.callback_query(F.data == 'i_paid_item')
async def proof_payment(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    item_data = user_data.get('item') 
    
    if not item_data:
        await callback.message.answer("Ошибка: данные о товаре не найдены.")
        return
    
    # Устанавливаем новое состояние
    await state.set_state(BuyItem.proof)
    
    await callback.message.edit_text(
        f'Отправь скриншот оплаты.\nБот обработает скриншот или файл и выдаст доступ к материалу',
        parse_mode="HTML",
        reply_markup=kb.i_paid2
    )


@router.message(BuyItem.proof, F.photo | F.document)
async def proof_item(message: Message, state: FSMContext):
    user_data = await state.get_data()
    item_data = user_data.get('item')

    if not item_data:
        await message.reply("Ошибка: данные о товаре не найдены.")
        return
    
    order_id = await rq.generate_unique_order_id()

    await rq.set_order(item_data, message, order_id)

    check_user = await rq.get_user_by_id(message.from_user.id)

    if message.photo:
        photo_id = message.photo[-1].file_id 
        file = await message.bot.get_file(photo_id)
        file_url = file.file_path
        
        await message.reply(f"Скриншот оплаты получен! После проверки бот выдаст вам материал к:\n<b>{item_data.name}</b>",
                            parse_mode="HTML")
        
        if check_user.is_promo:
            await message.bot.send_photo(
                ADMIN_ID, 
                photo=photo_id, 
                caption=f"Скриншот оплаты от пользователя\nНомер заказа: <code>{order_id}</code>\nID пользователя: <code>{message.from_user.id}</code>\nИмя: {message.from_user.full_name}\nПользователь: @{message.from_user.username}\nID Товара: {item_data.id}\nТовар: <b>{item_data.name}</b>\nЦена: <s>{item_data.price}</s> <b>{item_data.price - 3000}тг (Промокод: {check_user.promocode})</b>\n\n✅ Чтобы подтвердить оплату введите следующую команду:\n<code>/confirm_order {order_id}</code>\n\n❌ Чтобы отменить оплату введите следующую команду:\n<code>/cancel_order {order_id}</code>",
                parse_mode="HTML",
            )
        else:
            await message.bot.send_photo(
                ADMIN_ID, 
                photo=photo_id, 
                caption=f"Скриншот оплаты от пользователя\nНомер заказа: <code>{order_id}</code>\nID пользователя: <code>{message.from_user.id}</code>\nИмя: {message.from_user.full_name}\nПользователь: @{message.from_user.username}\nID Товара: {item_data.id}\nТовар: <b>{item_data.name}</b>\nЦена: <b>{item_data.price}тг</b>\n\n✅ Чтобы подтвердить оплату введите следующую команду:\n<code>/confirm_order {order_id}</code>\n\n❌ Чтобы отменить оплату введите следующую команду:\n<code>/cancel_order {order_id}</code>",
                parse_mode="HTML",
            )

    elif message.document:
        document_id = message.document.file_id
        file = await message.bot.get_file(document_id)
        file_url = file.file_path
        
        await message.reply(f"Файл оплаты получен! После проверки бот выдаст вам материал к:\n<b>{item_data.name}</b>",
                            parse_mode="HTML")
        if check_user.is_promo:
            await message.bot.send_document(
                ADMIN_ID,
                document=document_id,
                caption=f"Файл оплаты от пользователя\nНомер заказа: <code>{order_id}</code>\nID пользователя: <code>{message.from_user.id}</code>\nИмя: {message.from_user.full_name}\nПользователь: @{message.from_user.username}\nID Товара: {item_data.id}\nТовар: <b>{item_data.name}</b>\nЦена: <s>{item_data.price}</s> <b>{item_data.price - 3000}тг (Промокод: {check_user.promocode})</b>\n\n✅ Чтобы подтвердить оплату введите следующую команду:\n<code>/confirm_order {order_id}</code>\n\n❌ Чтобы отменить оплату введите следующую команду:\n<code>/cancel_order {order_id}</code>",
                parse_mode="HTML"
                )
        else:
            await message.bot.send_document(
                ADMIN_ID,
                document=document_id,
                caption=f"Файл оплаты от пользователя\nНомер заказа: <code>{order_id}</code>\nID пользователя: <code>{message.from_user.id}</code>\nИмя: {message.from_user.full_name}\nПользователь: @{message.from_user.username}\nID Товара: {item_data.id}\nТовар: <b>{item_data.name}</b>\nЦена: <b>{item_data.price}тг</b>\n\n✅ Чтобы подтвердить оплату введите следующую команду:\n<code>/confirm_order {order_id}</code>\n\n❌ Чтобы отменить оплату введите следующую команду:\n<code>/cancel_order {order_id}</code>",
                parse_mode="HTML"
                )
    await state.clear()



    
@router.callback_query(F.data == 'back_to_i_paid_halyk')
async def payment_method(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    item_data = user_data.get('item') 
    await callback.message.edit_text(f'Способ оплаты: [ Halyk Bank ] (KZT)\nСумма к оплате: <b>{item_data.price}тг</b>\n\nСчет Халык Банк:\n<code>2200701015340473</code>\n\nПривет! Можешь перевести с любой банковской карты, на Халык Банк. После этого сделай скрин или файл и отправь мне. Обработка скриншота требует время. После проверки будет выдана доступ к материалу☺️⭐️',
                                     parse_mode="HTML",
                                     reply_markup=kb.i_paid)
  
    
@router.callback_query(F.data == 'cancel_to_pay')
async def get_products(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.delete()





@router.callback_query(F.data == 'back_to_products')
async def back_to_products(callback : CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(text='Активные каталоги в магазине:', reply_markup=await kb.products())


@router.callback_query(F.data == 'to_main')
async def rules_agree(callback : CallbackQuery):
    await callback.answer('')

    await callback.message.delete()

    await callback.message.answer_photo(photo='AgACAgIAAxkBAAMNZ9IEChbnZcD4iui7Whd_byZsz3gAAqTtMRviKJBKcE2KI1-H-8YBAAMCAAN5AAM2BA',
                        caption='👋 <b>Добро пожаловать.</b>\n\nВпервые у нас? Тогда обязательно ознакомься 👇\n\nМы продаем материалы, которые буду полезны как и <b>для студентов</b>, так и <b>для начинающих программистов и дизайнеров</b> по <b>доступным ценам</b>. в клавиатуре снизу Вы можете воспользоваться меню.\n\n<b>🔥 Удачных покупок!</b>',
                         parse_mode="HTML", 
                         reply_markup=kb.main)




















@router.message(F.text == '🔎 Поиск товара')
async def search_item(message : Message):
    await message.answer('Выберите ниже по каталогу', reply_markup=await kb.search_by_products())


@router.callback_query(F.data.startswith('search_product_'))
async def search_by_product(callback: CallbackQuery, state: FSMContext):
    # Извлекаем product_id из данных callback'а
    product_id = callback.data.split('_')[2]

    # Асинхронно получаем продукт по его ID
    product = await rq.get_product(product_id)

    # Проверяем, что продукт найден
    if product:
        # Сохраняем выбранный продукт в состоянии
        await state.update_data(search_id=product_id)
        
        # Переходим к следующему состоянию поиска товара
        await state.set_state(SearchItem.search_name)
        
        # Отправляем пользователю сообщение с выбранным продуктом
        await callback.answer("")  # Очищаем ответ на callback

        # Отправляем сообщение о выбранном продукте
        await callback.message.edit_text(f'<b>Выбрано: {product.name}</b>\n\nНапишите слово для поиска товара',
                                         reply_markup=kb.search,
                                         parse_mode="HTML")
    else:
        # Если продукт не найден
        await callback.answer("Продукт не найден!")

@router.message(SearchItem.search_name)
async def search_name(message: Message, state: FSMContext):
    user_data = await state.get_data()
    product_id = user_data.get('search_id') 


    search_query = message.text.strip()

    search_results = await rq.get_product_item_search(product_id, search_query)

    search_results_list = search_results.all() if hasattr(search_results, 'all') else search_results

    index = 1
    response_text = f"🔍 Найдено <b>{len(search_results_list)}</b> результат(ов) по запросу:\n\n"
    for item in search_results_list:
        response_text += f"<b>{index}.</b> {item.name}\n"
        index += 1
        
    await message.answer(response_text, parse_mode="HTML",reply_markup=await kb.searched_items(product_id,search_query))
    
    await state.clear()




@router.callback_query(F.data == "search_all_catalog")
async def search_items_by_all_catalog(callback : CallbackQuery, state : FSMContext):
    await state.set_state(SearchAllItem.search_name_all)
    await callback.message.edit_text("<b>Выбрано: Поиск по всем каталогам</b>\n\nНапишите слово для поиска товара",
                                     reply_markup=kb.search,
                                     parse_mode="HTML")

@router.message(SearchAllItem.search_name_all)
async def search_name_all(message : Message, state : FSMContext):
    search_query = message.text.strip()

    search_results = await rq.get_product_item_search_all(search_query)

    search_results_list = search_results.all() if hasattr(search_results, 'all') else search_results

    index = 1
    response_text = f"🔍 Найдено <b>{len(search_results_list)}</b> результат(ов) по запросу:\n\n"
    for item in search_results_list:
        response_text += f"<b>{index}.</b> {item.name}\n"
        index += 1

    await message.answer(response_text, parse_mode="HTML",reply_markup=await kb.searched_items_all(search_query))
 
    await state.clear()

@router.callback_query(F.data == "back_to_search")
async def back_to_search(callback : CallbackQuery, state : FSMContext):
    await callback.message.edit_text('Выберите ниже по каталогу', reply_markup=await kb.search_by_products())
    await state.clear()
    

@router.callback_query(F.data.startswith('searched_item_'))
async def item(callback: CallbackQuery, state: FSMContext):
    item_data = await rq.get_item(callback.data.split('_')[2])
    await state.update_data(item=item_data)
    await callback.answer("")

    # Получаем состояние, чтобы удалить предыдущие сообщения товара
    state_data = await state.get_data()
    previous_message_id = state_data.get("last_item_message_id")

    if previous_message_id:
        # Удаляем старое сообщение товара, если оно существует
        try:
            await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=previous_message_id)
        except Exception as e:
            pass

    check_user = await rq.get_user_by_id(callback.from_user.id)

    if check_user.is_promo:
        try:
            if not item_data.photo:
                sent_message = await callback.message.answer(f'{item_data.name}\n\n<b>💰 Цена: <s>{item_data.price}</s> {item_data.price - 3000}тг (Промокод активирован!)</b>\n\nЧто вы получите:\n{item_data.description}', 
                                                        parse_mode="HTML",
                                                        reply_markup=kb.buy)
            else:
                sent_message = await callback.message.answer_photo(photo=item_data.photo,
                                                                caption=f'{item_data.name}\n\n<b>💰 Цена: <s>{item_data.price}</s> {item_data.price - 3000}тг (Промокод активирован!)</b>\n\nЧто вы получите:\n{item_data.description}', 
                                                                parse_mode="HTML",
                                                                reply_markup=kb.buy)

        # Сохраняем message_id нового сообщения товара
            await state.update_data(last_item_message_id=sent_message.message_id)
        
        except Exception as e:
            return
    else:
        try:
            if not item_data.photo:
                sent_message = await callback.message.answer(f'{item_data.name}\n\n<b>💰 Цена: {item_data.price}тг</b>\n\nЧто вы получите:\n{item_data.description}', 
                                                        parse_mode="HTML",
                                                        reply_markup=kb.buy)
            else:
                sent_message = await callback.message.answer_photo(photo=item_data.photo,
                                                                caption=f'{item_data.name}\n\n<b>💰 Цена: {item_data.price}тг</b>\n\nЧто вы получите:\n{item_data.description}', 
                                                                parse_mode="HTML",
                                                                reply_markup=kb.buy)

        # Сохраняем message_id нового сообщения товара
            await state.update_data(last_item_message_id=sent_message.message_id)
        
        except Exception as e:
            return










@router.message(F.text == 'Как дела?')
async def how_are_you(message : Message):
    await message.answer('Отлично, а у вас?')

@router.message(F.text == "Хорошо")
async def good(message : Message):
    await message.answer('Рад это слышать 😄')

@router.message(F.text == "Отлично")
async def good(message : Message):
    await message.answer('Рад это слышать 😄')

@router.message(F.text == "Круто")
async def good(message : Message):
    await message.answer('Рад это слышать 😄')









@router.message(F.text == '📋 Правила')
async def get_rule(message : Message):
    await message.answer(text='<b>1. Правила замены некорректного материала</b>\n\n1.1 Замена возможна в том случае, если:\n⚪️ Отсутствует или неверный материал. (В зависимости от типа товара)\n⚪️ Товар не соответствует описанию.\n⚪️ На товар не действует гарантия\n⚪️ В случае, если Вам уже оказали услугу замены в гарантийный срок товара, то повторный раз оказание услуги замены не предоставляется.\n\n1.2 Что необходимо для получения услуги замены невалидного товара:\n⚪️ Видеозапись или скриншоты с момента покупки нерабочего товара.\n⚪️ Гарантийный срок для замены - 12 часов с момента покупки товара в нашем сервисе.\n\n<b>2. Правила и условия работы нашего сервиса.</b>\n\n2.1 Правила работы:\n⚪️ Вернуть, обменять товар, если он вам как-то не подошел, не зашел и прочее - невозможно.\n⚪️ Если вы оплатили товар и товар вам не поступил (не успели доставить), деньги за него можно вернуть с 30% комиссией.\n⚪️ В случае обмана с вашей стороны - отказ в возврате средств, сотрудничестве, замене. Итог - блокировка в нашем сервисе.\n⚪️ Администрация сервиса вправе отказать в обслуживании и поддержке клиенту без объяснения причин.\n⚪️ Сервис не несет ответственность за ваши действия.\n⚪️ Магазин не несет ответственности за проблемы на стороне клиента, что влечет за собой невозможность авторизации/использования купленных данных (блокировка серверов властями, отсутствие драйверов и т.д.)\n⚪️ Совершая покупку вы автоматически соглашаетесь со ВСЕМИ правилами сервиса.\n\n<b>3. Магазин</b> @itdeals_bot <b>ПРЕДУПРЕЖДАЕТ!</b>\n⚪️ Магазин @itdeals_bot никого не взламывает, не обманывает, никак не влияет на материалы и их владельцев. Магазин @itdeals_bot сортирует материал по запрашиваемым критериям и продает (не неся ответственности за содержание информации), предупреждая, что в случае уничтожения, блокирования, модификации либо копировании данных может наступить ответственность.',
                         parse_mode="HTML")


@router.message(F.text == '💬 Помощь')
async def get_help(message : Message):
    await message.answer(text="❤️‍🔥 <b>Эти советы тебе пригодятся!</b>\n\n🎓 <b>Каталог курсов</b> 🎓\nВыбирайте из множества <b>актуальных</b> и <b>востребованных курсов</b>, которые помогут вам <b>прокачать навыки</b>, <b>освоить новую профессию</b> или <b>улучшить квалификацию</b>.\n<b>Гибкий формат обучения, практические задания и экспертные преподаватели</b> – всё, что нужно для вашего успеха!\n\nМы покупаем <b>дорогостоящие материалы</b>, и продаём их за <b>более низкую цену</b> чем у их авторов, но на <b>более обширную аудиторию!</b> 😎\n\n🗂️ <b>Готовые проекты</b> 🗂️\n<b>Надоело сидеть и делать проекты целую неделю или месяц?</b>\n\nНаши студенты создали множество <b>крутых проектов</b> и готовы делиться своими наработками! <b>Экономьте время и ресурсы</b>, используя <b>проверенные</b> и <b>качественные</b> решения, которые можно сразу внедрить в работу.\n<b>Оптимизированные процессы, современный дизайн и продуманные детали</b> – всё, что нужно для быстрого результата! 🔥\n\n📚 <b>Учебные материалы</b> 📚\nНаши студенты создали и собрали <b>ценные учебные материалы</b>, которые помогут вам быстрее освоить <b>новые навыки</b>.\n<b>Пошаговые инструкции, полезные примеры и проверенные методики</b> – всё в одном месте! Учитесь с удобством и применяйте знания на практике. 🚀\n\n<b>Появились вопросы?</b> Бот тех. поддержки - @helpme_line\n\n<b>Весь материал строго в ознакомительных целях!</b>",
                         parse_mode="HTML")
    




@router.message(F.text == '🚀 Использовать промокод')
async def use_promocode(message : Message, state : FSMContext):
    
    get_user = await rq.get_user_by_id(message.from_user.id)
    if get_user.was_promo:
        await message.answer(text="К сожалению, вы уже активировали промокод")
        return
    else:
        await state.set_state(Promocode.promocode)
        await message.answer(text="Введите промокод")
    

@router.message(Promocode.promocode)
async def check_promo(message : Message, state : FSMContext):
    await state.update_data(promocode=message.text)

    code = await rq.get_promo(message.text)

    if code:
        if code.is_active:
            await rq.set_promo_used_count(message.text)
            await rq.set_user_used_promo(message.from_user.id,message.text)
            await message.answer(text=f"✅ Поздравляем! Вы получили {code.discount}тг бонуса для первого заказа!")
            
        else:
            await message.answer("Данный промокод уже неактивен")
    else:
        await message.answer(text="Данный промокод не существует")
    await state.clear()


@router.message(F.text == "SPRING2025")
async def check_promo_message(message : Message):
    code = await rq.get_promo(message.text)
    get_user = await rq.get_user_by_id(message.from_user.id)
    if get_user.was_promo:
        await message.answer(text="К сожалению, вы уже активировали промокод")
        return
    else:
        if code.is_active:
            await rq.set_promo_used_count(message.text)
            await rq.set_user_used_promo(message.from_user.id,message.text)
            await message.answer(text=f"✅ Поздравляем! Вы получили {code.discount}тг бонуса для первого заказа!\n\n<b>Используйте его, чтобы приобрести товар по скидке!</b>",
                                 parse_mode="HTML")

            await message.bot.send_message(
                ADMIN_ID, 
                text=f"Данный пользователь активировал промокод\n\nID пользователя: <code>{message.from_user.id}</code>\nИмя: {message.from_user.full_name}\nПользователь: @{message.from_user.username}\nПромокод: <b>{message.text}</b>",
                parse_mode="HTML",
            )
        else:
            await message.answer("Данный промокод уже неактивен")

@router.message(F.text == "DL2025")
async def check_promo_message(message : Message):
    code = await rq.get_promo(message.text)
    get_user = await rq.get_user_by_id(message.from_user.id)
    if get_user.was_promo:
        await message.answer(text="К сожалению, вы уже активировали промокод")
        return
    else:
        if code.is_active:
            await rq.set_promo_used_count(message.text)
            await rq.set_user_used_promo(message.from_user.id,message.text)
            await message.answer(text=f"✅ Поздравляем! Вы получили {code.discount}тг бонуса для первого заказа!\n\n<b>Используйте его, чтобы приобрести товар по скидке!</b>",
                                 parse_mode="HTML")

            await message.bot.send_message(
                ADMIN_ID, 
                text=f"Данный пользователь активировал промокод\n\nID пользователя: <code>{message.from_user.id}</code>\nИмя: {message.from_user.full_name}\nПользователь: @{message.from_user.username}\nПромокод: <b>{message.text}</b>",
                parse_mode="HTML",
            )
        else:
            await message.answer("Данный промокод уже неактивен")

@router.message(F.text == "PYPSIK")
async def check_promo_message(message : Message):
    code = await rq.get_promo(message.text)
    get_user = await rq.get_user_by_id(message.from_user.id)
    if get_user.was_promo:
        await message.answer(text="К сожалению, вы уже активировали промокод")
        return
    else:
        if code.is_active:
            await rq.set_promo_used_count(message.text)
            await rq.set_user_used_promo(message.from_user.id,message.text)
            await message.answer(text=f"✅ Поздравляем! Вы получили {code.discount}тг бонуса для первого заказа!\n\n<b>Используйте его, чтобы приобрести товар по скидке!</b>",
                                 parse_mode="HTML")

            await message.bot.send_message(
                ADMIN_ID, 
                text=f"Данный пользователь активировал промокод\n\nID пользователя: <code>{message.from_user.id}</code>\nИмя: {message.from_user.full_name}\nПользователь: @{message.from_user.username}\nПромокод: <b>{message.text}</b>",
                parse_mode="HTML",
            )
        else:
            await message.answer("Данный промокод уже неактивен")
