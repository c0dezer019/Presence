# Third party modules
from nextcord.ext.commands import Bot, Context, check


def user_is_bot_developer():
    def predicate(ctx: Context):
        dev_list = [102588778232705024]

        return ctx.message.author.id in dev_list

    return check(predicate)


def bot_only_command():
    def predicate(ctx: Context, bot: Bot):
        return ctx.message.author.bot

    return check(predicate)


def is_bot_or_developer():
    def predicate(ctx: Context, bot: Bot):
        return ctx.message.author.id == 102588778232705024 or ctx.message.author.bot

    return predicate
