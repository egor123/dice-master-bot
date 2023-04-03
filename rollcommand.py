import discord
from discord.ext import commands
import random


def add_roll_command(bot):
    @bot.slash_command(description="Roll dices")
    @discord.option("dices", description="Example: 1d20, 6d6...")
    async def roll(ctx: discord.ApplicationContext, dices: str):
        (amount, dice) = roll_parse(dices)
        arr = [random.randint(1, dice) for _ in range(amount)]
        msg = f"{dices} = {arr[0]}" if amount == 1 \
            else f"{dices} = {' + '.join(map(str, arr))} = { sum(arr) }"
        await ctx.respond(f"```🎲 {msg} 🎲```")

    def roll_parse(dices):
        try:
            d = list(map(int, dices.lower().split('d')))
        except:
            raise commands.ArgumentParsingError()
        if (len(d) != 2 or d[0] <= 0 or d[1] <= 0):
            raise commands.ArgumentParsingError()
        return tuple(d)
