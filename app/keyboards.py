from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from app.database.requests import get_products, get_product_item, get_product_item_search, get_product_item_search_all

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🛒 Посмотреть каталог')],
    [KeyboardButton(text='🔎 Поиск товара')],
    [KeyboardButton(text='🚀 Использовать промокод')],
    [KeyboardButton(text='📋 Правила'), KeyboardButton(text='💬 Помощь')]
],
    resize_keyboard=True,
    input_field_placeholder='Пункт меню...')

main_old = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🛒Посмотреть каталог')]
],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню.')

settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Помощь', callback_data='help')]
])

main_admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🛒 Посмотреть каталог')],
    [KeyboardButton(text='🔎 Поиск товара')],
    [KeyboardButton(text='🚀 Использовать промокод')],
    [KeyboardButton(text='📋 Правила'), KeyboardButton(text='💬 Помощь')],
    [KeyboardButton(text='🛠️ Команды администратора 🛠️')],
],
    resize_keyboard=True,
    input_field_placeholder='Пункт меню...')

search = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='back_to_search')]
])



async def products():
    all_products = await get_products()
    keyboard = InlineKeyboardBuilder()
    for product in all_products:
        keyboard.add(InlineKeyboardButton(text=product.name, callback_data=f"product_{product.id}"))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(1).as_markup()


async def search_by_products():
    all_products = await get_products()
    keyboard = InlineKeyboardBuilder()
    for product in all_products:
        keyboard.add(InlineKeyboardButton(text=product.name, callback_data=f"search_product_{product.id}"))
    keyboard.add(InlineKeyboardButton(text='Поиск по всем каталогам', callback_data='search_all_catalog'))
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    return keyboard.adjust(1).as_markup()





async def items(product_id, page=1):
    all_items = await get_product_item(product_id)
    
    # Преобразуем в список (если это не список)
    all_items = list(all_items)

    # Разбиваем список на страницы по 10 элементов
    items_per_page = 10
    start_index = (page - 1) * items_per_page
    end_index = start_index + items_per_page
    page_items = all_items[start_index:end_index]

    keyboard = InlineKeyboardBuilder()

    # Добавляем элементы на текущей странице
    item_index_id = start_index + 1
    for item in page_items:
        keyboard.add(InlineKeyboardButton(text=f"{item_index_id}. {item.name}", callback_data=f"item_{item.id}"))
        item_index_id += 1

    # Навигация по страницам
    if page > 1:
        keyboard.add(InlineKeyboardButton(text="⬅  Предыдущая страница ", callback_data=f"items_{product_id}_{page-1}"))
    if end_index < len(all_items):
        keyboard.add(InlineKeyboardButton(text="Следующая страница  ➡", callback_data=f"items_{product_id}_{page+1}"))

    # Кнопка назад
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back_to_products'))
    # Кнопка на главную
    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))
    
    return keyboard.adjust(1).as_markup()


async def searched_items(product_id,query):
    all_items = await get_product_item_search(product_id,query)
    
    # Преобразуем в список (если это не список)
    all_items = list(all_items)


    keyboard = InlineKeyboardBuilder()

    item_index_id = 0
    for item in all_items:
        item_index_id += 1
        keyboard.add(InlineKeyboardButton(text=f"{item_index_id}", callback_data=f"searched_item_{item.id}"))
        

    
    return keyboard.adjust(5).as_markup()


async def searched_items_all(query):
    all_items = await get_product_item_search_all(query)
    
    # Преобразуем в список (если это не список)
    all_items = list(all_items)


    keyboard = InlineKeyboardBuilder()

    item_index_id = 0
    for item in all_items:
        item_index_id += 1
        keyboard.add(InlineKeyboardButton(text=f"{item_index_id}", callback_data=f"searched_item_{item.id}"))
        

    
    return keyboard.adjust(5).as_markup()






buy = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💰 Купить', callback_data='buy_item')]
])

payment_method = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='[ Halyk Bank ] (KZT)', callback_data='halyk')],
    [InlineKeyboardButton(text='✖ Отменить', callback_data='cancel_to_pay')]
])

i_paid = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Я оплатил', callback_data='i_paid_item')],
    [InlineKeyboardButton(text='✖ Отменить', callback_data='cancel_to_pay')]
])

i_paid2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад', callback_data='back_to_i_paid_halyk')],
    [InlineKeyboardButton(text='✖ Отменить', callback_data='cancel_to_pay')]
])

confirmation = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Подтвердить', callback_data='accept_pay')],
    [InlineKeyboardButton(text='✖ Отменить', callback_data='cancel')]
])  


cancel_add = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✖ Отменить', callback_data='cancel_to_add')]
])  


admin_commands = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='/add_new_item'), KeyboardButton(text='/add_new_material'), KeyboardButton(text='/get_document')],
    [KeyboardButton(text='/send_document'), KeyboardButton(text='/confirm_order'), KeyboardButton(text='/cancel_order')],
    [KeyboardButton(text='/get_photo'), KeyboardButton(text='/get_document'), KeyboardButton(text='/send_photo')],
    [KeyboardButton(text='/send_document'), KeyboardButton(text='/my_id'), KeyboardButton(text='/get_users')]

],
    resize_keyboard=True,
    input_field_placeholder='Меню команд...')
