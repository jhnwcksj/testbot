import os
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from aiogram.types import Update
from aiohttp import web

from app.handlers import router
from app.database.models import async_main

load_dotenv()

bot = Bot(token=os.getenv('TOKEN2'))
dp = Dispatcher()

async def get_updates():
    updates = await bot.get_updates(offset=0, limit=100)
    for update in updates:
        await dp.process_update(update)
    return updates

async def main():
    await async_main()
    await bot.delete_webhook()
    await get_updates()
    dp.include_router(router)

app = web.Application()

if __name__ == '__main__':
    try:
        asyncio.run(main())
        web.run_app(app, host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        print('Exit')
