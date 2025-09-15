import asyncio
from datetime import datetime, timezone
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter, TelegramForbiddenError
from bot.config import bot, dp
from bot.handlers.start import router as start_router
from bot.handlers.user import router as user_router
from bot.handlers.admin import router as admin_router
from bot.handlers.admin_broadcast import router as broadcast_router
from bot.middlewares.debug_middleware import DebugMiddleware
from bot.middlewares.activity_middleware import ActivityMiddleware
from bot.services.redis_service import (
    list_campaigns, update_campaign_status, filter_users,
    set_campaign_started, set_campaign_finished, incr_campaign_stat, get_campaign
)
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def sender_for_campaign(cid: str, camp: dict):
    # наивный парсинг через eval/ast
    import ast
    try:
        audience = ast.literal_eval(camp.get("audience","{}"))
        if not isinstance(audience, dict):
            audience = {"kind":"all"}
    except Exception:
        audience = {"kind":"all"}

    users = await filter_users(audience)
    await incr_campaign_stat(cid, "total", len(users))
    await set_campaign_started(cid)

    kb = None
    btxt, burl = camp.get("button_text",""), camp.get("button_url","")
    if btxt and burl:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=btxt, url=burl)]])

    text = camp.get("text","")
    media_type = camp.get("media_type","")
    file_id = camp.get("file_id","")

    for uid in users:
        try:
            if media_type == "photo":
                await bot.send_photo(uid, file_id, caption=text, reply_markup=kb, parse_mode="HTML")
            elif media_type == "video":
                await bot.send_video(uid, file_id, caption=text, reply_markup=kb, parse_mode="HTML")
            elif media_type == "document":
                await bot.send_document(uid, file_id, caption=text, reply_markup=kb, parse_mode="HTML")
            else:
                await bot.send_message(uid, text, reply_markup=kb, parse_mode="HTML")
            await incr_campaign_stat(cid, "sent", 1)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 0.5)
        except (TelegramBadRequest, TelegramForbiddenError):
            await incr_campaign_stat(cid, "failed", 1)
        except Exception:
            await incr_campaign_stat(cid, "failed", 1)
            await asyncio.sleep(0.05)

    await set_campaign_finished(cid)

async def scheduler_loop():
    while True:
        try:
            camps = await list_campaigns()
            now = datetime.now(timezone.utc)
            for c in camps:
                status = c.get("status")
                ctype = c.get("type")
                cid = c.get("id")
                sched = c.get("schedule_at","")
                if status in ("done", "sending"):
                    continue
                if status == "pending":
                    # немедленная отправка
                    await update_campaign_status(cid, "sending")
                    await sender_for_campaign(cid, c)
                elif status == "scheduled" and ctype == "scheduled" and sched:
                    try:
                        when = datetime.fromisoformat(sched)
                        if when <= now:
                            await update_campaign_status(cid, "sending")
                            await sender_for_campaign(cid, c)
                    except Exception:
                        # если померло время — лучше отправить сразу
                        await update_campaign_status(cid, "sending")
                        await sender_for_campaign(cid, c)
        except Exception as e:
            print("Scheduler error:", e)
        await asyncio.sleep(10)

async def main():
    # Middleware: лог + активность
    dp.message.middleware.register(DebugMiddleware())
    dp.message.middleware.register(ActivityMiddleware())
    dp.callback_query.middleware.register(ActivityMiddleware())

    # Роутеры
    dp.include_router(start_router)
    dp.include_router(user_router)
    dp.include_router(admin_router)
    dp.include_router(broadcast_router)

    print("Бот запущен!")
    # Pланировщик
    asyncio.create_task(scheduler_loop())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
