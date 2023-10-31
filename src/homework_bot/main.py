import os
from typing import Optional, Union

import discord
from cryptography.fernet import Fernet
from discord import ApplicationContext
from dotenv import load_dotenv

from homework_bot.cogs import HWList, HWManagement, GuildConfig
from homework_bot.bot import MainBot

load_dotenv()

API_URL = "http://localhost:5000"

key = os.getenv("KEY").encode("utf8")

main_bot = MainBot(
    status=discord.Status.dnd,
    activity=discord.Game("with your homework"),
    intents=discord.Intents.default(),
    debug_guilds=[856028294645153802],
)


@main_bot.slash_command()
async def ping(ctx: ApplicationContext):
    # TODO: change the respond in future
    await ctx.respond(f"Pong! {main_bot.latency * 1000:.2f}ms")

main_bot.add_cog(HWManagement(main_bot, key, API_URL))
main_bot.add_cog(GuildConfig(main_bot, key))

main_bot.run(os.getenv("TOKEN"))
