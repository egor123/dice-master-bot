import discord
from datetime import datetime
from discord.ext import commands
from confiq import MAIN_CATEGORY, TEMPLATE_CATEGORY, ADMIN_ROLES, TRUSTED_ROLES


class ConfirmationModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        self.confirmation = kwargs.pop('confirmation')
        self.resolve = kwargs.pop('resolve')
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(
            label=f"Enter \"{self.confirmation}\""))

    async def callback(self, interaction):
        if (self.children[0].value == self.confirmation):
            if self.resolve is not None:
                await self.resolve(interaction)
        else:
            await interaction.response.defer()


class DateModal(discord.ui.Modal):
    # TODO TIMEZONES??????!!!!!!!!!!!!!!!!!
    def __init__(self, *args, **kwargs) -> None:
        self.resolve = kwargs.pop('resolve')
        super().__init__(*args, **kwargs)
        self.add_item(discord.ui.InputText(label="Date \"%d.%m.%Y\"",
                      value=datetime.now().strftime("%d.%m.%Y")))
        self.add_item(discord.ui.InputText(label="Time \"%H.%M\"",
                      value=datetime.now().strftime("%H.%M")))

    async def callback(self, interaction):
        try:
            date = f"{self.children[0].value} {self.children[1].value}"
            stamp = datetime.strptime(date, "%d.%m.%Y %H.%M")
            date = f"({stamp.strftime('%a')}) {date}"
            await self.resolve(interaction, date)
        except:
            await interaction.response.defer()


def get_category_roles(ctx: discord.ApplicationContext, category: str = None, roles=["PC", "DM"]):
    category = ctx.channel.category.name if category is None else category
    return tuple([discord.utils.get(ctx.guild.roles, name=f"{category}-{role}") for role in roles])


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
