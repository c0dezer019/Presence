# Third party modules
from nextcord import Guild
from nextcord.ext.commands import Bot, Cog, bot_has_guild_permissions
from nextcord.utils import find

# Internal modules
import utility.request_handler as rh
from main import redis


class Setup(Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @Cog.listener()
    async def on_guild_join(self, guild: Guild):
        general = find(lambda x: x.name == "general", guild.text_channels)
        sys_chan = guild.system_channel

        if sys_chan and sys_chan.permissions_for(guild.me).send_messages:
            await sys_chan.send(
                f"Hello {guild.name}! I am here to take names and drink coffee, but I am all out of coffee. Please "
                "wait while I get a refill."
            )
        else:
            await general.send(
                f"Hello {guild.name}! I am here to take names and drink coffee, but I am all out of coffee. Please "
                "wait while I get a refill."
            )

    @Cog.listener("on_guild_join")
    @bot_has_guild_permissions(administrator=True)
    async def setup(self, guild: Guild):
        sys_chan = guild.system_channel
        response = rh.guild(guild.id, guild.name)

        if response["code"] != 200:
            await sys_chan.send(
                "I couldn't find any coffee. I no workee without coffee. Please pass this code to my"
                f" owner: {response.status_code}"
            )
        else:
            if not redis.exists(f"guild:{guild.id}:meta"):
                meta = {
                    "guild_id": response["guild"]["guildId"],
                    "name": guild.name,
                    "status": response["guild"]["status"],
                    "settings": response["guild"]["settings"],
                    "date_added": response["guild"]["dateAdded"]
                }
                redis.hset(f"guild:{guild.id}:meta", mapping=meta)

                stats = {
                    "last_act": response["guild"]["lastAct"],
                    "idle_stats": response["guild"]["idleStats"],
                }
                redis.hset(f"guild:{guild.id}:stats", mapping=stats)

            await sys_chan.send("I'm now in business! Time to start collecting names")

            pipe = redis.pipeline()

            for member in guild.members:
                if member.bot:
                    continue

                m_response = rh.member(guild.id, member)

                if m_response["code"] != 200:
                    await sys_chan.send(
                        f"My pencil broke and I'm unable to write names. Received code {response['code']} from server."
                    )
                    break

                if not redis.sismember(f"guild:{guild.id}:members", member.id):
                    redis.sadd(f"guild:{guild.id}:members", member.id)
                    r_data = {
                        k: "" if v is None else str(v)
                        for k, v in m_response["member"].items()
                    }
                    r_data["name"] = member.display_name
                    pipe.hset(
                        f"guild:{guild.id}:member:{member.id}",
                        mapping=r_data,
                    )

            if len(pipe.command_stack) > 0:
                pipe.execute()

            await sys_chan.send(
                "Names have been collected, eyeglasses have been cleaned, and bunnies have been killed. Carry on"
            )


def setup(bot):
    bot.add_cog(Setup(bot))
