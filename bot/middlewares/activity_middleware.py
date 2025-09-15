from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from datetime import datetime, timezone
from bot.services.redis_service import set_last_seen

class ActivityMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user = event.from_user if hasattr(event, "from_user") else None
        if user:
            try:
                await set_last_seen(user.id, datetime.now(timezone.utc).isoformat())
            except Exception:
                pass
        return await handler(event, data)
