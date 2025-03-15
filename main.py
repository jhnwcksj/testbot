import os
import asyncio
from aiogram import Bot
from aiogram.bot import Application
from dotenv import load_dotenv
from aiohttp import web
from aiogram.types import Update

load_dotenv()

WEBHOOK_HOST = 'https://scottshopbot.onrender.com'
WEBHOOK_PATH = f'/webhook/{os.getenv("TOKEN2")}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=os.getenv('TOKEN2'))
app = Application(bot)

async def set_webhook():
    webhook_info = await bot.get_webhook_info()
    print("Webhook info:", webhook_info)
    await bot.set_webhook(WEBHOOK_URL)

async def on_start_webhook(request):
    data = await request.json()
    update = Update(**data)
    await app.process_update(update)
    return web.Response()

async def main():
    await set_webhook()
    app.include_router(router)

app_web = web.Application()
app_web.router.add_post('/webhook/{token}', on_start_webhook)

if __name__ == '__main__':
    try:
        asyncio.run(main())
        web.run_app(app_web, host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        print('Exit')
