from aiogram.utils.keyboard import InlineKeyboardBuilder
# import db
import async_db
import os
from aiogram import types


async def get_kb_wth_users() -> types.InlineKeyboardMarkup:
    users = await async_db.get_users(await async_db.db_connection(os.environ.get("dbname")))

    builder = InlineKeyboardBuilder()
    for user in users:
        builder.row(types.InlineKeyboardButton(
            text=f"{user[1]} [{user[0]}]",
            callback_data=f"{user[1]}:{user[0]}"
        ))
    return builder.as_markup(resize_keyboard=True)


async def get_users_to_ban_or_unban_kb(state: int) -> types.InlineKeyboardMarkup:
    users = await async_db.get_blocked_or_unblocked_users(await async_db.db_connection(os.environ.get("dbname")), state)
    action = "unban" if state else "ban"

    builder = InlineKeyboardBuilder()
    for user in users:
        builder.row(types.InlineKeyboardButton(
            text=f"{user[1]} [{user[0]}]",
            callback_data=f"{action}_{user[0]}"
        ))
    return builder.as_markup(resize_keyboard=True)