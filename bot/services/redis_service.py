from bot.config import redis

WELCOME_KEY = "welcome_text"
USER_KEY = "user:{user_id}"

async def get_welcome_text() -> str:
    text = await redis.get(WELCOME_KEY)
    if not text:
        return (
            "Привет! Добро пожаловать в бот пополнения Steam ٩(◕‿◕｡)۶\n\n"
            "Здесь можно пополнить Steam по логину. Подходит для аккаунтов: "
            "России 🇷🇺, Казахстана 🇰🇿 и стран СНГ\n\n"
            "Почему Задонатить.ру?\n"
            "— Одна из самых низких комиссий\n"
            "— Круглосуточная поддержка\n"
            "— Более 65 000 успешных пополнений\n"
            "— Система лояльности 🍩"
        )
    return text

async def set_welcome_text(text: str):
    await redis.set(WELCOME_KEY, text)

async def get_user_count() -> int:
    """Получить количество зарегистрированных пользователей"""
    keys = await redis.keys("user:*")
    return len(keys)

async def get_user_info(user_id: int) -> dict:
    """Получить информацию о пользователе"""
    user_key = USER_KEY.format(user_id=user_id)
    return await redis.hgetall(user_key)