import logging
import os

import discord
from dotenv import load_dotenv
from pycord.multicog import apply_multicog

from homework_bot.bot import MainBot
from homework_bot.main_bot.cogs import (
    GuildConfig,
    HWInfo,
    HWList,
    HWManagement,
    HWNotify,
    HWStatistic,
    UtilityAndMonitoring,
)

logger = logging.getLogger("homework_bot.main")

load_dotenv()

API_URL = os.getenv("API_URL")

key = os.getenv("KEY").encode("utf8")

main_bot = MainBot(
    status=discord.Status.dnd,
    activity=discord.Game("with your homework"),
    intents=discord.Intents.default(),
    debug_guilds=[856028294645153802],
)

# main bot
main_bot.add_cog(UtilityAndMonitoring(main_bot, API_URL))
main_bot.add_cog(GuildConfig(main_bot, key))
main_bot.add_cog(HWList(main_bot, API_URL))
main_bot.add_cog(HWInfo(main_bot, API_URL))
main_bot.add_cog(HWNotify(main_bot, API_URL))
main_bot.add_cog(HWStatistic(main_bot, API_URL))
main_bot.add_cog(HWManagement(main_bot, key, API_URL))

apply_multicog(main_bot)

main_bot.run(os.getenv("MAIN_TOKEN"))
