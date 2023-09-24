import discord
from discord.ext import commands
from utils import AllowedCategoryConverter, get_category_roles, get_category_roles_names, is_campaign_category, is_not_campaign_category, has_roles
from confiq import MAIN_CATEGORY, TEMPLATE_CATEGORY, ADMIN_ROLES, TRUSTED_ROLES


def add_category_commands(bot):

    class NonExistingCategoryNameConverter(commands.Converter):
        async def convert(self, ctx, name):
            if discord.utils.get(ctx.guild.categories, name=name) is not None:
                raise commands.CommandError()
            return name

    async def clone_role(ctx: discord.ApplicationContext, role: discord.Role, name: str) -> discord.Role:
        return await ctx.guild.create_role(name=name, colour=role.colour, permissions=role.permissions, hoist=role.hoist, mentionable=role.mentionable)

    async def replace_roles(channel, old_role: discord.Role, new_role: discord.Role):
        await channel.set_permissions(new_role, overwrite=channel.overwrites_for(old_role))
        await channel.set_permissions(old_role, overwrite=None)

    @bot.slash_command(description="Creates new category")
    @commands.check(is_not_campaign_category)
    @commands.has_any_role(*ADMIN_ROLES, *TRUSTED_ROLES)
    @commands.cooldown(1, 30, commands.BucketType.user)
    @discord.option("name", description="Category name: <name> and roles: <name>-DM, <name>-PC", min_length=3)
    async def create_new_category(ctx: discord.ApplicationContext, name: NonExistingCategoryNameConverter):
        await ctx.respond(f"Creating category \"{name}\"...")
        templ = discord.utils.get(ctx.guild.categories, name=TEMPLATE_CATEGORY)
        (templ_pc_role, templ_dm_role) = get_category_roles(ctx, TEMPLATE_CATEGORY)
        dm_role = await clone_role(ctx, templ_dm_role, f"{name}-DM")
        pc_role = await clone_role(ctx, templ_pc_role, f"{name}-PC")
        await ctx.user.add_roles(dm_role)
        await ctx.user.add_roles(pc_role)
        category = await templ.clone(name=name)
        await replace_roles(category, templ_dm_role, dm_role)
        await replace_roles(category, templ_pc_role, pc_role)
        for channel in templ.channels:
            clone = await channel.clone(name=channel.name)
            await clone.edit(category=category)
            await replace_roles(clone, templ_dm_role, dm_role)
            await replace_roles(clone, templ_pc_role, pc_role)

    @bot.slash_command(description="Deletes category")
    @commands.check(is_not_campaign_category)
    @commands.has_any_role(*ADMIN_ROLES, *TRUSTED_ROLES)
    @commands.cooldown(1, 30, commands.BucketType.user)
    @discord.option("category", description="Category name")
    async def delete_category(ctx: discord.ApplicationContext, category: AllowedCategoryConverter):
        await ctx.respond(f"Deleting category \"{category.name}\"...")
        for channel in category.channels:
            await channel.delete()
        for role in get_category_roles(ctx, category.name):
            await role.delete()
        await category.delete()

    @bot.slash_command(description="Renames category")
    @commands.check(is_not_campaign_category)
    @commands.has_any_role(*ADMIN_ROLES, *TRUSTED_ROLES)
    @commands.cooldown(1, 30, commands.BucketType.user)
    @discord.option("category", description="Old category name")
    @discord.option("new_name", description="New category name")
    async def rename_category(ctx: discord.ApplicationContext, category: AllowedCategoryConverter, new_name: NonExistingCategoryNameConverter):
        await ctx.respond(f"Renaming category \"{category.name}\"...")
        (pc_role, dm_role) = get_category_roles(ctx, category.name)
        await category.edit(name=new_name)
        await dm_role.edit(name=f"{new_name}-DM")
        await pc_role.edit(name=f"{new_name}-PC")

    @bot.slash_command(description="Invites/removes users from category")
    @commands.check(is_campaign_category)
    @commands.check(lambda ctx: has_roles(ctx.user, [*ADMIN_ROLES, *get_category_roles_names(ctx, roles=["DM"])]))
    @discord.option("user")
    @discord.option("action", choices=["add_role", "remove_role"])
    @discord.option("role", choices=["PC", "DM"])
    async def manage_roles(ctx: discord.ApplicationContext, user: discord.Member, action: str, role: str):
        (drole,) = get_category_roles(ctx, roles=[role])
        match(action):
            case "add_role":
                await user.add_roles(drole)
                await ctx.respond(f"Added role \"{drole.name}\" to user {user.mention}")
            case "remove_role":
                await user.remove_roles(drole)
                await ctx.respond(f"Removed role \"{drole.name}\" from user {user.mention}")

    @bot.slash_command(description="Leave category")
    @commands.check(is_campaign_category)
    async def leave(ctx: discord.ApplicationContext):
        for role in get_category_roles(ctx):
            await ctx.user.remove_roles(role)
        await ctx.respond(f"{ctx.user.mention} leaved \"{ctx.channel.category.name}\"")
