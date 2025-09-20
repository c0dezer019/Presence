# Standard packages

# Standard modules
from typing import Optional

# Third party modules
from nextcord.ext.commands import CheckFailure, Cog, Context, command

# Internal modules
import utility.request_handler as rh
from utility.decorators.checks import user_is_bot_developer


class DevCommands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(hidden=True, help="")
    @user_is_bot_developer()
    async def sync(self, ctx: Context):
        if ctx.message.guild.id != 820891105322074113:
            await ctx.message.delete
        else:
            await ctx.guild.system_channel.send(ctx.message.channel.type)

    @command(
        hidden=True,
        help="If for some reason the need to start fresh occurs, this initiates the "
        "on_guild_join() procedures without having to kick and re-invite bot.",
    )
    @user_is_bot_developer()
    async def reset(self, ctx: Context):
        guild = ctx.guild
        sys_chan = guild.system_channel

        # Add guild
        response = rh.guild(guild.id)

        if response.status_code != 200:
            await sys_chan.send(
                "I couldn't find any coffee. I no workee without coffee. Please pass a this code to my"
                " owner: {0}".format(response.status_code)
            )
        else:
            await sys_chan.send("I'm now in business! Time to start collecting names")

        # Add members
        for member in guild.members:
            response = rh.member(guild.id, member)

        if response == 200:
            await sys_chan.send(
                "Names have been collected, eyeglasses have been cleaned, and bunnies have been killed. Carry on."
            )

    @command(
        hidden=True,
        help="Deletes things from the database in the event corresponding listeners "
        "fail to do their jobs.",
    )
    @user_is_bot_developer()
    async def delete(self, ctx, obj_type: str, obj_id: int):
        pass

    @command(
        hidden=True,
        help="Loads, reloads, or unloads an extension (cog). Only the developer can use"
        "this command.",
    )
    @user_is_bot_developer()
    async def reload(self, ctx: Context, cog: Optional[str]):
        # bot_guilds = ctx.bot.guilds

        await ctx.message.guild.system_channel.send("Cog reloaded.")

        # for guild in bot_guilds:
        # await guild.system_channel.send('Hello, I have been updated. Use ?changelog to see what\'s new!')

        await ctx.bot.reload_extension(f"cogs.{cog}")

    @reload.error
    async def reload_error(self, ctx: Context, error):
        if isinstance(error, CheckFailure):
            await ctx.reply("Sorry, but this is a command reserved for the developer.")

    @command(hidden=True, help="Sets up server in the database if there isn't one.")
    @user_is_bot_developer()
    async def setup(self, ctx: Context):
        await ctx.message.guild.system_channel.send('Guild initializing.')


def setup(bot):
    bot.add_cog(DevCommands(bot))
