from aiogram import Router, types, F
from aiogram.filters import CommandStart
from bot.config import redis
from bot.keyboards.main_menu import main_menu
from bot.services.redis_service import get_welcome_text

router = Router()

# Ключ для хранения информации о пользователях
USER_KEY = "user:{user_id}"

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_key = USER_KEY.format(user_id=user_id)
    
    # Проверяем, есть ли пользователь в Redis
    user_exists = await redis.exists(user_key)
    
    if user_exists:
        # Пользователь уже существует - приветствуем с возвращением
        welcome_text = await get_welcome_text()
        welcome_back_text = f"👋 С возвращением! {welcome_text}"
        await message.answer(welcome_back_text, reply_markup=main_menu)
    else:
        # Новый пользователь - сохраняем и приветствуем
        user_data = {
            "id": user_id,
            "username": message.from_user.username or "",
            "first_name": message.from_user.first_name or "",
            "last_name": message.from_user.last_name or "",
            "joined_at": message.date.isoformat()
        }
        
        # Сохраняем пользователя в Redis
        await redis.hset(user_key, mapping=user_data)
        
        # Отправляем приветственное сообщение
        welcome_text = await get_welcome_text()
        await message.answer(welcome_text, reply_markup=main_menu)