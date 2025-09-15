from aiogram import Router, types, F
from bot.config import Config
from bot.services.redis_service import set_welcome_text, get_user_count

router = Router()

@router.message(F.text.startswith("/set_welcome"))
async def set_welcome(message: types.Message):
    if message.from_user.id not in Config.ADMIN_CACHE:
        return await message.answer("⛔ У вас нет доступа.")

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer("Введите новый текст после команды.\nПример: /set_welcome Привет, это новый текст!")

    new_text = parts[1]
    await set_welcome_text(new_text)
    await message.answer("✅ Приветственный текст обновлён!")

@router.message(F.text == "📊 Статистика")
async def stats_cmd(message: types.Message):
    if message.from_user.id not in Config.ADMIN_CACHE:
        return await message.answer("⛔ У вас нет доступа.")
    count = await get_user_count()
    await message.answer(f"📊 Статистика бота:\n👥 Пользователей: {count}")
