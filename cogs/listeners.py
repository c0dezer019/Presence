# Standard modules
import json

# Third party modules
import arrow
from nextcord import Guild, Member, Message, TextChannel, User
from nextcord.ext.commands import Bot, Cog
from nextcord.utils import get

# Internal modules
import utility.request_handler as rh
from main import redis
from utility.helpers import _check_time_idle


class Listeners(Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.ignore_list: tuple = ("?ping", "?reset", "?check", "?sync")

    @Cog.listener()
    async def on_member_join(self, member: Member):
        chan_index: int = self.bot.guilds.index(member.guild)

        general: TextChannel = get(member.guild.channels, name="general")
        sys_chan: TextChannel = member.guild.system_channel

        if (
            sys_chan
            and sys_chan.permissions_for(self.bot.guilds[chan_index].me).send_messages
        ):
            await sys_chan.send("Welcome {0.mention}!".format(member))
        else:
            await general.send("Welcome {0.mention}!".format(member))

        try:
            member = rh.member(member.guild.id, member)

            r_data = {k: "" if v is None else str(v) for k, v in member}
            r_data["name"] = member.display_name if not member.nick else member.nick
            r_data["status"] = member.status

            redis.hset(f"member:{member.id}@{member.guild.id}", mapping=r_data)

        except Exception:
            raise

    @Cog.listener()
    async def on_message(self, message: Message):
        hset = redis.hset

        if message.guild is not None and message.author.status != "invisible":
            if message.content.startswith(self.ignore_list):
                return

            if not message.author.bot:
                dt: arrow.Arrow = arrow.utcnow().datetime
                get_time_idle: dict = _check_time_idle(dt)
                idle_stats: dict[str, int | list] = json.loads(
                    redis.hget(f"guild_id:{message.guild.id}", "idleStats")
                )
                last_loc = json.loads(redis.hget(f"guild_id:{message.guild.id}", "lastAct"))
                last_loc["ch"] = message.channel.id
                last_loc["type"] = str(message.channel.type)
                last_loc["ts"] = arrow.utcnow().isoformat()

                hset(f"guild_id:{message.guild.id}", "last_loc", mapping=last_loc)

                idle_stats["timesIdle"].append(get_time_idle)

                if idle_stats["avgIdleTime"]:
                    idle_stats["prevAvgs"].append(idle_stats["avgIdleTime"])
                else:
                    pass

                idle_stats["avgIdleTime"] = sum(idle_stats["timesIdle"]) / len(
                    idle_stats["timesIdle"]
                )

                if len(idle_stats["timesIdle"]) > 50:
                    idle_stats["timesIdle"].remove(idle_stats["timesIdle"][0])

                if len(idle_stats["prevAvgs"]) > 50:
                    idle_stats["prevAvgs"].remove(idle_stats["prevAvgs"][0])

                hset(f"guild_id:{message.guild.id}", "idleStats", mapping=idle_stats)

        elif (
            not message.guild
            and str(message.channel.type) == "private"
            and not message.author.bot
        ):
            await message.channel.send(
                "Sorry, but I do not respond to DM's other than with this message. Try using me in a guild "
                "that I am in."
            )

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        try:
            if before.nick != after.nick:
                rh.update_member(after.id, **{"nickname": after.nick})
            else:
                pass

        except AttributeError:
            raise

    @Cog.listener()
    async def on_user_update(self, before: User, after: User):
        try:
            if before.name != after.name or before.discriminator != after.discriminator:
                username = f"{after.name}#{after.discriminator}"

                rh.update_member(after.id, **{"username": username})
            else:
                pass

        except Exception:
            raise

    """@Cog.listener()
    async def on_voice_state_update(
        self, member: Member, before: VoiceState, after: VoiceState
    ):

        with open("utility/storeTest.json", "rw") as file:
            data: Dict = json.load(file)

        guild_idx: int = next(
            (
                index
                for (index, d) in enumerate(data)
                if d["guild_id"] == member.guild.id
            ),
            None,
        )
        member_idx: int = next(
            (
                index
                for (index, d) in enumerate(data[guild_idx]["members"])
                if d["member_id"] == member.id
            ),
            None,
        )"""

    @Cog.listener()
    async def on_guild_update(self, before: Guild, after: Guild):
        try:
            if before.name != after.name:
                rh.update_guild(after.id, **{"name": after.name})
            else:
                pass
        except Exception:
            raise


def setup(bot):
    bot.add_cog(Listeners(bot))
