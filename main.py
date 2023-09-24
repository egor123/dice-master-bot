import discord
from dotenv import load_dotenv
import os
from rollcommand import add_roll_command
from campaignscommands import add_category_commands
from schedulecommand import add_schedule_command
from confiq import add_confiq

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

add_roll_command(bot)
add_schedule_command(bot)
add_category_commands(bot)

add_confiq(bot)

load_dotenv()
bot.run(os.environ["TOKEN"])
