import discord
from discord.ext import commands
import asyncio

MAIN_CATEGORY = "General"
TEMPLATE_CATEGORY = "Template"
ADMIN_ROLES = ["Admin", "Moderator"]
TRUSTED_ROLES = ["TrueRoller"]

def add_confiq(bot):
    @bot.event
    async def on_ready():
        print(f'We have logged in as {bot.user}')

    @bot.event
    async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.respond("```diff\n- CommandInvokeError\n```", delete_after=5)
        elif isinstance(error, commands.ArgumentParsingError):
            await ctx.respond("```diff\n- ArgumentParsingError\n```", delete_after=5)
        elif isinstance(error, asyncio.TimeoutError):
            await ctx.respond("```diff\n- TimeoutError\n```", delete_after=5)
        elif isinstance(error, discord.errors.CheckFailure):
            await ctx.respond("```diff\n- CheckFailure\n```", delete_after=5)
        else:
            await ctx.respond("```diff\n- Failure\n```", delete_after=5)
            raise error
