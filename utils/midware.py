from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
import db
import os


class BlacklistMiddleware(BaseMiddleware):
    def is_user_banned(self, uid: int) -> bool:
        return True if uid in db.blocklist(db.db_connection(os.environ.get("dbname"))) else False

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        user = data["event_from_user"]
        # print(data)
        # print("------------------------------")
        # print(user)
        if not self.is_user_banned(user.id):
            return await handler(event, data)
        else:
            return
