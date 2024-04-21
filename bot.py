import asyncio
import os
import sys
from random import choices
import logging
from handlers import callbacks, commands, text_processing

from aiogram import Bot, Dispatcher, Router, types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from utils import midware

TOKEN = os.environ.get("TOKEN")
# Initialize Bot instance with a default parse mode which will be passed to all API calls
bot = Bot(TOKEN, parse_mode="HTML")
# Webserver settings
# bind localhost only to prevent any external access
WEB_SERVER_HOST = os.environ.get("WEB_SERVER_HOST")
# Port for incoming request from reverse proxy. Should be any available port
WEB_SERVER_PORT = int(os.environ.get("WEB_SERVER_PORT"))

# Path to webhook route, on which Telegram will send requests
WEBHOOK_PATH = "/webhook"
# Secret key to validate requests from Telegram (optional)
WEBHOOK_SECRET = "".join(x for x in choices("qazxswedcvfrtgbnhyujmkiolp", k=10))
# Base URL for webhook will be used to generate webhook URL for Telegram,
# in this example it is used public DNS with HTTPS support
BASE_WEBHOOK_URL = os.environ.get("BASE_WEBHOOK_URL")


async def setup_bot_commands():
    bot_commands = [
        types.BotCommand(command="/start", description="Start bot"),
        types.BotCommand(command="/list", description="List users"),
        types.BotCommand(command="/ban", description="Ban user"),
        types.BotCommand(command="/unban", description="Unban user")
    ]
    await bot.set_my_commands(bot_commands)


async def on_startup(bot: Bot) -> None:
    # If you have a self-signed SSL certificate, then you will need to send a public
    # certificate to Telegram
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}", secret_token=WEBHOOK_SECRET)


async def main_debug() -> None:
    router = Router()
    # Dispatcher is a root router
    dp = Dispatcher()
    dp.update.outer_middleware(middleware=midware.BlacklistMiddleware())
    # ... and all other routers should be attached to Dispatcher
    dp.include_routers(text_processing.router, callbacks.router, commands.router)
    await dp.start_polling(bot, skip_updates=True, on_startup=setup_bot_commands)


def main_prod() -> None:
    router = Router()
    # Dispatcher is a root router
    dp = Dispatcher()
    dp.update.outer_middleware(middleware=midware.BlacklistMiddleware())
    # ... and all other routers should be attached to Dispatcher
    dp.include_routers(text_processing.router, callbacks.router, commands.router)
    # Register startup hook to initialize webhook
    dp.startup.register(on_startup)

    if bool(int(os.environ.get("enabled_webhook"))):
        # Create aiohttp.web.Application instance
        app = web.Application()

        # Create an instance of request handler,
        # aiogram has few implementations for different cases of usage
        # In this example we use SimpleRequestHandler which is designed to handle simple cases
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
            secret_token=WEBHOOK_SECRET,
        )
        # Register webhook handler on application
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)

        # Mount dispatcher startup and shutdown hooks to aiohttp application
        setup_application(app, dp, bot=bot)

        # And finally start webserver
        web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    if bool(int(os.environ.get("debug"))):
        logging.basicConfig(format="%(levelname)s | %(asctime)s | %(message)s", level=logging.DEBUG, stream=sys.stdout)
        asyncio.run(main_debug())
    else:
        logging.basicConfig(format="%(levelname)s | %(asctime)s | %(message)s", filename="talk_bot.log", level=logging.DEBUG)
        asyncio.run(main_prod())
    logging.info("Bot starts")
