# Standard modules
import logging
import os
import traceback
from logging.handlers import RotatingFileHandler

# Third party modules
from dotenv import load_dotenv
from nextcord import Intents
from nextcord.ext.commands import Bot
from redis import Redis

redis = Redis(host=os.getenv("REDIS_HOST", "redis"), port=os.getenv("REDIS_PORT", 6379), decode_responses=True)

load_dotenv()
TOKEN = os.getenv("TOKEN")

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
