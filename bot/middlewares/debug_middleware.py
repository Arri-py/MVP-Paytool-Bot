from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable

class DebugMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if hasattr(event, 'text') and event.text:
            print(f"Получено сообщение: {event.text}")
            print(f"User ID: {event.from_user.id}")
        return await handler(event, data)