# import db
import async_db
import os
from states import *
from aiogram.fsm.context import FSMContext
from aiogram import types, html, Router, F

router = Router()


@router.callback_query(~F.data.startswith('ban_'), ~F.data.startswith('unban_'))
async def callback_query_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.update_data(message_to=callback.data)
    await state.set_state(DialogState.talking)
    user = callback.data.split(':')
    await callback.message.answer(f"Write the message to user {html.bold(user[0])} [{html.code(user[1])}]")


@router.callback_query(F.data.startswith('ban_'))
async def ban_query_handler(callback: types.CallbackQuery) -> None:
    user = int(callback.data.split('_')[1])
    await async_db.ban_unban_user(user, 1, await async_db.db_connection(os.environ.get("dbname")))
    await callback.message.answer(f"User {html.bold(user)} has been banned! Press /list")


@router.callback_query(F.data.startswith('unban_'))
async def unban_query_handler(callback: types.CallbackQuery) -> None:
    user = int(callback.data.split('_')[1])
    await async_db.ban_unban_user(user, 0, await async_db.db_connection(os.environ.get("dbname")))
    await callback.message.answer(f"User {html.bold(user)} has been unblocked! Press /list")
