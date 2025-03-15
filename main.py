import os
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from aiogram.types import Update
from aiohttp import web
from aiogram.utils import web

from app.handlers import router
from app.database.models import async_main

load_dotenv()

WEBHOOK_HOST = 'https://scottshopbot.onrender.com/'
WEBHOOK_PATH = f'/webhook/{os.getenv("TOKEN2")}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=os.getenv('TOKEN2'))
dp = Dispatcher()

async def on_start_webhook(request):
    data = await request.json()
    update = Update(**data)
    await dp.process_update(update)
    return web.Response()

async def main():
    await async_main() 
    dp.include_router(router)
    await bot.set_webhook(WEBHOOK_URL) 
    webhook_info = await bot.get_webhook_info()
    print(webhook_info)

app = web.Application()
app.router.add_post('/webhook/{token}', on_start_webhook)

if __name__ == '__main__':
    try:
        web.run_app(app, host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        print('Exit')
