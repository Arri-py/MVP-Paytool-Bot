import asyncio
from bot.config import bot, dp
from bot.handlers.start import router as start_router
from bot.handlers.user import router as user_router
from bot.handlers.admin import router as admin_router
from bot.middlewares.debug_middleware import DebugMiddleware

async def main():
    # Добавляем middleware для отладки
    dp.message.middleware(DebugMiddleware())
    
    # Включаем все роутеры
    dp.include_router(start_router)
    dp.include_router(user_router)
    dp.include_router(admin_router)

    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())