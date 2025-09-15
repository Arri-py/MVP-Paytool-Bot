import asyncio
from bot.config import bot, dp
from bot.handlers.start import router as start_router
from bot.handlers.user import router as user_router
from bot.handlers.admin import router as admin_router

async def main():
    dp.include_router(start_router)
    dp.include_router(user_router)
    dp.include_router(admin_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())