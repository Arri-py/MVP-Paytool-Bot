from bot.config import redis

WELCOME_KEY = "welcome_text"
USER_KEY = "user:{user_id}"
BONUS_KEY = "bonus:{user_id}"

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

# ---- User helpers ----
async def register_user(user_id: int, username: str, first_name: str, last_name: str, joined_at: str):
    user_key = USER_KEY.format(user_id=user_id)
    exists = await redis.exists(user_key)
    if not exists:
        mapping = {
            "id": str(user_id),
            "username": username or "",
            "first_name": first_name or "",
            "last_name": last_name or "",
            "joined_at": joined_at,
            "purchases": "0",
            "donates": "0"
        }
        await redis.hset(user_key, mapping=mapping)
        return True
    return False

async def get_user_info(user_id: int) -> dict:
    user_key = USER_KEY.format(user_id=user_id)
    return await redis.hgetall(user_key) or {}

async def get_user_purchases(user_id: int) -> int:
    user_key = USER_KEY.format(user_id=user_id)
    v = await redis.hget(user_key, "purchases")
    try:
        return int(v) if v is not None else 0
    except Exception:
        return 0

async def get_user_donates(user_id: int) -> int:
    user_key = USER_KEY.format(user_id=user_id)
    v = await redis.hget(user_key, "donates")
    try:
        return int(v) if v is not None else 0
    except Exception:
        return 0

async def add_donates(user_id: int, amount: int):
    user_key = USER_KEY.format(user_id=user_id)
    current = await get_user_donates(user_id)
    await redis.hset(user_key, "donates", current + amount)

async def increment_purchases(user_id: int, amount: int = 1):
    user_key = USER_KEY.format(user_id=user_id)
    current = await get_user_purchases(user_id)
    await redis.hset(user_key, "purchases", current + amount)

# ---- Bonus tracking ----
async def has_received_bonus(user_id: int) -> bool:
    key = BONUS_KEY.format(user_id=user_id)
    return await redis.exists(key)

async def mark_bonus_received(user_id: int):
    key = BONUS_KEY.format(user_id=user_id)
    await redis.set(key, "1")

# ---- Admin stats ----
async def get_user_count() -> int:
    keys = await redis.keys("user:*")
    return len(keys)
