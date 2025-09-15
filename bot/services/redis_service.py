from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from bot.config import redis

WELCOME_TEXT_KEY = "welcome_text"
USERS_SET_KEY = "users:all"

def _user_key(user_id: int, suffix: str) -> str:
    return f"user:{user_id}:{suffix}"

# Приветственный текст
async def set_welcome_text(text: str) -> None:
    await redis.set(WELCOME_TEXT_KEY, text)

async def get_welcome_text() -> str:
    default = (
        "🏠 Главное меню Задонатить.ру\n\n"
        "🎮 Пополнение Steam — быстро и безопасно\n"
        "🎁 Бонусы — получайте кэшбек за каждую покупку\n"
        "⭐️ Отзывы — мнения тысяч довольных клиентов\n"
        "🔒 Гарантии — юридическая защита и надежность\n\n"
        "💬 Поддержка 24/7 — всегда готовы помочь!\n"
        "🛍️ Широкий ассортимент — не только Steam"
    )
    return await redis.get(WELCOME_TEXT_KEY) or default

# Пользователи / статистика
async def register_user(user_id: int, username: str, first_name: str, last_name: str, joined_at: str) -> None:
    key = _user_key(user_id, "profile")
    await redis.hset(key, mapping={
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "joined_at": joined_at
    })
    await redis.sadd(USERS_SET_KEY, user_id)

async def get_user_count() -> int:
    return await redis.scard(USERS_SET_KEY)

# Покупки / донаты / бонусы
async def get_user_purchases(user_id: int) -> int:
    val = await redis.get(_user_key(user_id, "purchases"))
    return int(val or 0)

async def get_user_donates(user_id: int) -> int:
    val = await redis.get(_user_key(user_id, "donates"))
    return int(val or 0)

async def add_donates(user_id: int, amount: int) -> int:
    return await redis.incrby(_user_key(user_id, "donates"), amount)

async def has_received_bonus(user_id: int) -> bool:
    return (await redis.get(_user_key(user_id, "bonus_received"))) == "1"

async def mark_bonus_received(user_id: int) -> None:
    await redis.set(_user_key(user_id, "bonus_received"), "1")

# Активность пользователей
async def set_last_seen(user_id: int, iso_ts: str) -> None:
    await redis.set(_user_key(user_id, "last_seen"), iso_ts)

async def get_last_seen(user_id: int) -> Optional[str]:
    return await redis.get(_user_key(user_id, "last_seen"))

async def set_last_purchase_at(user_id: int, iso_ts: str) -> None:
    await redis.set(_user_key(user_id, "last_purchase_at"), iso_ts)

async def get_last_purchase_at(user_id: int) -> Optional[str]:
    return await redis.get(_user_key(user_id, "last_purchase_at"))

async def get_joined_at(user_id: int) -> Optional[str]:
    return await redis.hget(_user_key(user_id, "profile"), "joined_at")

# Рассылки
# Храним список id кампаний и детальные хэши
CAMPAIGNS_SET = "campaigns:all"      # set of campaign ids
CAMPAIGN_SEQ = "campaigns:seq"       # increment for id
def _cmp_key(c_id: str) -> str:
    return f"campaign:{c_id}"
def _cmp_stats_key(c_id: str) -> str:
    return f"campaign:{c_id}:stats"

async def create_campaign(data: Dict[str, Any]) -> str:
    # data: title, text, button_text?, button_url?, media_type?, file_id?, audience, type, schedule_at?
    cid = str(await redis.incr(CAMPAIGN_SEQ))
    key = _cmp_key(cid)
    data_to_store = {k: ("" if v is None else v) for k, v in data.items()}
    data_to_store["id"] = cid
    data_to_store["status"] = "scheduled" if data.get("type") == "scheduled" else "pending"
    await redis.hset(key, mapping=data_to_store)
    await redis.sadd(CAMPAIGNS_SET, cid)
    # init stats
    await redis.hset(_cmp_stats_key(cid), mapping={"sent": 0, "failed": 0, "total": 0, "started_at": "", "finished_at": ""})
    return cid

async def get_campaign(cid: str) -> Dict[str, str] | None:
    data = await redis.hgetall(_cmp_key(cid))
    return data or None

async def list_campaigns() -> List[Dict[str, str]]:
    ids = list(await redis.smembers(CAMPAIGNS_SET))
    ids.sort(key=lambda x: int(x))  # by numeric id
    result: List[Dict[str, str]] = []
    for cid in ids:
        d = await get_campaign(cid)
        if d:
            result.append(d)
    return result

async def update_campaign_status(cid: str, status: str) -> None:
    await redis.hset(_cmp_key(cid), "status", status)

async def set_campaign_started(cid: str) -> None:
    await redis.hset(_cmp_key(cid), "status", "sending")
    await redis.hset(_cmp_stats_key(cid), "started_at", datetime.now(timezone.utc).isoformat())

async def set_campaign_finished(cid: str) -> None:
    await redis.hset(_cmp_key(cid), "status", "done")
    await redis.hset(_cmp_stats_key(cid), "finished_at", datetime.now(timezone.utc).isoformat())

async def incr_campaign_stat(cid: str, field: str, by: int = 1) -> None:
    await redis.hincrby(_cmp_stats_key(cid), field, by)

async def get_campaign_stats(cid: str) -> Dict[str, str]:
    return await redis.hgetall(_cmp_stats_key(cid))

# --------- Отбор аудитории ---------
async def get_all_user_ids() -> List[int]:
    raw = await redis.smembers(USERS_SET_KEY)
    return [int(u) for u in raw]

async def filter_users(audience: Dict[str, Any]) -> List[int]:
    """
    audience dict supports keys:
      - kind: all | new | has_purchases | no_purchases | purchased_last_days | opened_last_days | ids_list
      - days: int   (for purchased_last_days / opened_last_days)
      - ids: List[int] (for ids_list)
    """
    users = await get_all_user_ids()
    kind = audience.get("kind", "all")
    now = datetime.now(timezone.utc)

    if kind == "ids_list":
        ids = set(map(int, audience.get("ids", [])))
        return [uid for uid in users if uid in ids]

    filtered: List[int] = []
    for uid in users:
        if kind == "all":
            filtered.append(uid)
            continue

        if kind in ("has_purchases", "no_purchases", "purchased_last_days"):
            purchases = await get_user_purchases(uid)
        if kind in ("new",):
            joined = await get_joined_at(uid)
        if kind in ("opened_last_days",):
            last_seen = await get_last_seen(uid)
        if kind in ("purchased_last_days",):
            last_purchase = await get_last_purchase_at(uid)

        if kind == "has_purchases" and purchases > 0:
            filtered.append(uid)
        elif kind == "no_purchases" and purchases == 0:
            filtered.append(uid)
        elif kind == "new":
            if joined:
                try:
                    jdt = datetime.fromisoformat(joined)
                    # считаем новым, если зарегистрировался за последние 7 дней
                    if (now - jdt) <= timedelta(days=7):
                        filtered.append(uid)
                except Exception:
                    pass
        elif kind == "opened_last_days":
            days = int(audience.get("days", 7))
            if last_seen:
                try:
                    ldt = datetime.fromisoformat(last_seen)
                    if (now - ldt) <= timedelta(days=days):
                        filtered.append(uid)
                except Exception:
                    pass
        elif kind == "purchased_last_days":
            days = int(audience.get("days", 30))
            if last_purchase:
                try:
                    pdt = datetime.fromisoformat(last_purchase)
                    if (now - pdt) <= timedelta(days=days):
                        filtered.append(uid)
                except Exception:
                    pass
    return filtered
