from aiogram import Router, types
from aiogram.filters import CommandStart
from bot.keyboards.main_menu import get_main_menu
from bot.services.redis_service import get_welcome_text, register_user
from bot.config import Config
from aiogram.types import FSInputFile

router = Router()

MAIN_SCREEN = (
    "🏠 Главное меню Задонатить.ру\n\n"
    "🎮 Пополнение Steam — быстро и безопасно\n"
    "🎁 Бонусы — получайте кэшбек за каждую покупку\n"
    "⭐️ Отзывы — мнения тысяч довольных клиентов\n"
    "🔒 Гарантии — юридическая защита и надежность\n\n"
    "💬 Поддержка 24/7 — всегда готовы помочь!\n"
    "🛍️ Широкий ассортимент — не только Steam"
)


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    user = message.from_user
    # Регистрируем пользователя при первом заходе
    try:
        await register_user(
            user_id=user.id,
            username=user.username or "",
            first_name=user.first_name or "",
            last_name=user.last_name or "",
            joined_at=message.date.isoformat()
        )
    except Exception as e:
        # лог — не мешаем пользователю
        print("Redis register_user error:", e)

    welcome_text = await get_welcome_text()
    welcome_message = (
        f"👋 {user.first_name}!\n\n"
        f"{welcome_text}\n\n"
        "Если вы впервые — нажмите «🎁 Получить 50 рублей на первую покупку», чтобы активировать бонус."
    )

    is_admin = user.id in Config.ADMIN_CACHE

    # Отправляем стартовую картинку (если есть)
    try:
        photo = FSInputFile("img/start.jpg")
        await message.answer_photo(photo, caption=welcome_message, reply_markup=get_main_menu(is_admin))
    except Exception as e:
        print("Start photo error:", e)
        await message.answer(welcome_message, reply_markup=get_main_menu(is_admin))
