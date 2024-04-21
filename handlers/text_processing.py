from bot import bot, Router
from states import *
# import db
import async_db
import os
from aiogram.fsm.context import FSMContext
from aiogram import types, F, html
from aiogram.exceptions import TelegramForbiddenError
import logging


router = Router()


@router.message(DialogState.talking, ~F.text.startswith("/"))
async def talk(message: types.Message, state: FSMContext) -> None:
    if message.reply_to_message:
        raw = await async_db.get_message_entity(await async_db.db_connection(os.environ.get("dbname")), int(message.reply_to_message.message_id))
        data = {'message_to': f'{message.from_user.full_name}:{raw[2]}'}
    else:
        data = await state.get_data()

    if data:
        user = data["message_to"]
        logging.info(f"Sending message to {user.split(':')[-1]}")
        try:
            match message.content_type:
                case types.ContentType.TEXT:
                    bot_msg = await bot.send_message(user.split(':')[-1], message.text)
                case types.ContentType.STICKER:
                    await bot.send_sticker(user.split(':')[-1], message.sticker.file_id)
                case types.ContentType.DOCUMENT:
                    bot_msg = await bot.send_document(user.split(':')[-1], message.document.file_id)
                case types.ContentType.PHOTO:
                    bot_msg = await bot.send_photo(user.split(':')[-1], message.photo[0].file_id)
                case types.ContentType.ANIMATION:
                    bot_msg = await bot.send_animation(user.split(':')[-1], message.animation.file_id)
                case types.ContentType.AUDIO:
                    bot_msg = await bot.send_audio(user.split(':')[-1], message.audio.file_id)
                case types.ContentType.VIDEO:
                    bot_msg = await bot.send_video(user.split(':')[-1], message.video.file_id)
                case types.ContentType.VOICE:
                    bot_msg = await bot.send_voice(user.split(':')[-1], message.voice.file_id)
                case _:
                    text = f"Doesn't support content type {message.content_type}"
                    await message.answer(text)
                    raise TypeError(text)

            await async_db.add_message_entity(
                await async_db.db_connection(os.environ.get("dbname")),
                message.message_id,
                bot_msg.message_id,
                message.chat.id,
                bot_msg.chat.id,
            )

        except TelegramForbiddenError:
            await message.reply(f"Bot was blocked by user {user.split(':')[-1]}. Removing contact from db. Press /list")
            await state.set_state(DialogState.switching)
            logging.warning(f"Bot was blocked by user {user.split(':')[-1]}")
            proc = await async_db.delete_user(user.split(':')[-1], await async_db.db_connection(os.environ.get("dbname")))
            logging.info(f"User {user.split(':')[-1]} has been removed from db" if proc else f"Can't remove user {user.split(':')[-1]}")
        except Exception as _e:
            logging.critical(f"Error while {_e}")
    else:
        await message.answer("You don't have any contacts")
        await state.set_state(DialogState.switching)


@router.message(DialogState.guest)
async def guest_process_message(message: types.Message) -> None:
    if not await async_db.is_user_exists(message.from_user.id, await async_db.db_connection(os.environ.get("dbname"))):
        await async_db.add_user(await async_db.db_connection(os.environ.get("dbname")), message.from_user.id, message.from_user.full_name)

    form = get_user_info_form(message.from_user)

    try:
        bot_msg = await bot.send_message(os.environ.get("admin_id"), form + html.blockquote(message.text) if message.text else form)

        if message.content_type == types.ContentType.TEXT:
            pass
        elif message.content_type == types.ContentType.STICKER:
            bot_msg = await bot.send_sticker(os.environ.get("admin_id"), message.sticker.file_id)
        elif message.content_type == types.ContentType.DOCUMENT:
            bot_msg = await bot.send_document(os.environ.get("admin_id"), message.document.file_id,
                                              caption=message.caption)
        elif message.content_type == types.ContentType.PHOTO:
            bot_msg = await bot.send_photo(os.environ.get("admin_id"), message.photo[0].file_id,
                                           caption=message.caption)
        elif message.content_type == types.ContentType.ANIMATION:
            bot_msg = await bot.send_animation(os.environ.get("admin_id"), message.animation.file_id,
                                               caption=message.caption)
        elif message.content_type == types.ContentType.AUDIO:
            bot_msg = await bot.send_audio(os.environ.get("admin_id"), message.audio.file_id, caption=message.caption)
        elif message.content_type == types.ContentType.VIDEO:
            bot_msg = await bot.send_video(os.environ.get("admin_id"), message.video.file_id, caption=message.caption)
        elif message.content_type == types.ContentType.VOICE:
            bot_msg = await bot.send_voice(os.environ.get("admin_id"), message.voice.file_id, caption=message.caption)
        else:
            raise TypeError(f"Doesn't support content type {message.content_type}")

        await async_db.add_message_entity(
            await async_db.db_connection(os.environ.get("dbname")),
            message.message_id,
            bot_msg.message_id,
            message.chat.id,
            bot_msg.chat.id,
        )

    except TypeError as e:
        await message.reply(str(e))

    # await message.answer("Message has been received")


def get_user_info_form(user: types.User) -> str:
    if user.username:
        form = (html.link(html.bold(user.full_name),
                          f"<a href='https://t.me/{user.username}'>" + " " + html.code(user.id) + ":"))
    else:
        form = html.bold(user.full_name) + " [" + html.code(user.id) + "]:"

    return form


@router.message(~F.text.startswith("/"))
async def on_bot_reboot(message: types.Message, state: FSMContext) -> None:
    if message.from_user.id != int(os.environ.get("admin_id")):
        await state.set_state(DialogState.guest)
        await guest_process_message(message)
    else:
        await message.answer("Bot has been rebooted, press /list")


@router.edited_message()
async def edited_message_handler(message: types.Message) -> None:
    if message.chat.id == int(os.environ.get("admin_id")):
        raw = await async_db.get_message_entity(await async_db.db_connection(os.environ.get("dbname")), int(message.message_id))
        await bot.edit_message_text(message.text, raw[-1], raw[1])
    else:
        raw = await async_db.get_message_entity(await async_db.db_connection(os.environ.get("dbname")), int(message.message_id))
        await bot.edit_message_text(get_user_info_form(message.from_user) + html.blockquote(message.text), raw[-1], raw[1])


@router.message_reaction()
async def reaction_message_handler(message: types.Message) -> None:
    raw = await async_db.get_message_entity(await async_db.db_connection(os.environ.get("dbname")), int(message.message_id))
    if raw is not None and message.chat.id == raw[-1]:
        await bot.set_message_reaction(raw[-2], raw[0], message.new_reaction)