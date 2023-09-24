import discord
from discord.ext import commands
from confiq import MAIN_CATEGORY, TEMPLATE_CATEGORY, ADMIN_ROLES


def get_category_roles(ctx: discord.ApplicationContext, category: str = None, roles=["PC", "DM"]):
    category = ctx.channel.category.name if category is None else category
    droles = tuple([discord.utils.get(ctx.guild.roles, name=f"{category}-{role}") for role in roles])
    return droles

def get_category_roles_names(ctx: discord.ApplicationContext, category: str = None, roles=["PC", "DM"]):
    return [ role.name for role in get_category_roles(ctx, category, roles)]

async def is_campaign_category(ctx: discord.ApplicationContext):
    return any(get_category_roles(ctx))


async def is_not_campaign_category(ctx: discord.ApplicationContext):
    return not await is_campaign_category(ctx)


def has_roles(user, role_names):
    return any([role.name in role_names for role in user.roles])


class AllowedCategoryConverter(commands.Converter):
    async def convert(self, ctx, name):

        if name in [MAIN_CATEGORY, TEMPLATE_CATEGORY] and not has_roles(ctx.user, ADMIN_ROLES):
            raise commands.errors.UserInputError()
        channel = discord.utils.get(ctx.guild.categories, name=name)
        if channel is None:
            raise commands.errors.UserInputError()
        (dm_role,) = get_category_roles(ctx, name, ["DM"])
        if not has_roles(ctx.user, [*ADMIN_ROLES, dm_role.name]):
            raise commands.errors.UserInputError()
        return channel
