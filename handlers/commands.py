from states import *
# import db
import async_db
import os
import kb
from aiogram.fsm.context import FSMContext
from aiogram import types, F, Router, html
from aiogram.filters import CommandStart, Command, CommandObject

router = Router()


@router.message(CommandStart())
async def command_start(message: types.Message, state: FSMContext) -> None:

    if message.from_user.id == int(os.environ.get("admin_id")):

        await state.set_state(DialogState.switching)
        await message.answer(
            "Choose the person you want to send message:",
            reply_markup=await kb.get_kb_wth_users()
            )

    else:
        await state.set_state(DialogState.guest)
        await message.answer("Write the message to me bellow. I'll give you an answer as soon as possible")
    return


@router.message(Command("list"), F.from_user.id == int(os.environ.get("admin_id")))
async def list_users(message: types.Message, state: FSMContext) -> None:
    await message.answer("list_users")
    await state.clear()
    await message.answer(
        "Choose the person you want to send message:",
        reply_markup=await kb.get_kb_wth_users()
    )
    return


@router.message(Command("ban"), F.from_user.id == int(os.environ.get("admin_id")))
async def ban_user(message: types.Message, command: CommandObject, state: FSMContext) -> None:
    if command.args is None:
        await state.set_state(DialogState.switching)
        await message.answer(
            "Choose the person you want to ban:",
            reply_markup=await kb.get_users_to_ban_or_unban_kb(state=0)
            )
    else:
        try:
            user = int(command.args)
            assert await async_db.is_user_exists(user, await async_db.db_connection(os.environ.get("dbname")))
            await async_db.ban_unban_user(user, 1, await async_db.db_connection(os.environ.get("dbname")))
            await message.reply(f"User {html.bold(user)} has been banned!")
        except ValueError:
            await message.reply(f"Incorrect UID format\nPlease, use {html.code('/ban integer')}")
        except AssertionError:
            await message.reply(f"User with UID {html.bold(user)} does not exist!")


@router.message(Command("unban"), F.from_user.id == int(os.environ.get("admin_id")))
async def unban_user(message: types.Message, command: CommandObject, state: FSMContext) -> None:
    if command.args is None:
        await state.set_state(DialogState.switching)
        await message.answer(
            "Choose the person you want to unban:",
            reply_markup=await kb.get_users_to_ban_or_unban_kb(state=1)
            )
    else:
        try:
            user = int(command.args)
            assert await async_db.is_user_exists(user, await async_db.db_connection(os.environ.get("dbname")))
            await async_db.ban_unban_user(user, 0, await async_db.db_connection(os.environ.get("dbname")))
            await message.reply(f"User {html.bold(user)} has been unblocked!")
        except ValueError:
            await message.reply(f"Incorrect UID format\nPlease, use {html.code('/unban integer')}")
        except AssertionError:
            await message.reply(f"User with UID {html.bold(user)} does not exist!")
