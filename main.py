# Standard modules
import logging
import os
import traceback
from logging.handlers import RotatingFileHandler

# Third party modules
from dotenv import load_dotenv
from nextcord import Game, Intents
from nextcord.ext.commands import Bot

# Internal modules
from utility.redis import create_redis_connection

load_dotenv()
TOKEN = os.getenv("TOKEN")

redis = create_redis_connection()

description = """Got idle? Have no more"""
intents = Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
intents.voice_states = True

bot = Bot(description=description, intents=intents, command_prefix="?")

extensions = [
    "cogs.admin_cmds",
    "cogs.dev_cmds",
    "cogs.listeners",
    "cogs.setup",
    "cogs.user_cmds",
]
ignore_list: tuple = ("?ping", "?reset", "?check")


@bot.event
async def on_ready():
    global redis

    if redis is None:
        try:
            redis = create_redis_connection()
        except Exception as e:
            logging.error("Still cannot connect to Redis: %s", e)

    print(f"{bot.user} is connected to the following guilds:")

    for guild in bot.guilds:
        health = (
            "\033[32mOK\033[0m"
            if redis.exists(f"guild:{guild.id}:meta")
            else "\033[31mX\033[0m"
        )

        print(
            f"\033[4;35m{guild.name}\033[0m (id: \033[1;34m{guild.id}\033[0m), \033[32mhealth:\033[0m {health}"
        )

    print()  # An empty line for formatting.

    await bot.sync_application_commands()

    await bot.change_presence(activity=Game("Cops and Robbers"))


@bot.event
async def on_error(event, *args, **kwargs):
    if args:
        ctx = args[0]

        if hasattr(ctx, "guild") and ctx.guild is not None:
            await ctx.guild.system_channel.send(
                "I have encountered an error but do not worry, I will alert my owner."
            )
    logging.error(f"Error happened within {event}: {traceback.format_exc()}")


@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


if __name__ == "__main__":
    logging.basicConfig()
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler("bot_log.txt", maxBytes=500000, backupCount=5)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(process)d - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    for cog in extensions:
        bot.load_extension(cog)

    bot.run(TOKEN, reconnect=True)
