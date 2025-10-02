# Third party modules
import arrow
from nextcord import Guild, Member, Message, TextChannel, User
from nextcord.ext.commands import Bot, Cog
from nextcord.utils import get

# Internal modules
import utility.request_handler as rh
from main import redis
from lib.typings import Member as GQLMember


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
            db_member: GQLMember = rh.member(member.guild.id, member)

            r_data = {
                "name": member.display_name if not member.nick else member.nick,
                "status": db_member.status if db_member is not None else "new",
                "admin_access": db_member.admin_access if db_member is not None else False,
                "flags": db_member.flags if db_member is not None else [],
                "discord_status": member.status
            }

            redis.hset(f"member:{member.id}:{member.guild.id}:meta", mapping=r_data)

        except Exception:
            raise

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.guild is not None and message.author.status != "invisible":
            if message.content.startswith(self.ignore_list):
                return

            if not message.author.bot:
                expire_at: arrow.Arrow = arrow.utcnow().shift(minutes=10)
                block_key = f"session:{message.author.id}:{message.guild.id}:expires_at"

                await redis.hset(f"member:{message.author.id}:{message.guild.id}:meta", "idles_at", expire_at.int_timestamp)

                if await redis.exists(block_key):
                    await redis.hexpireat(block_key, expire_at)
                else:
                    await redis.setex(block_key, expire_at, expire_at)

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
