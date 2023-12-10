import logging
import os
import re
import time
import traceback

import discord
from discord import ApplicationContext, Colour, DiscordException, Embed
from discord.ext import commands
from dotenv import load_dotenv
from httpx import ConnectError
from cacheout import Cache
from pycord.multicog import apply_multicog

from homework_bot import responses
from homework_bot.bot import MainBot
from homework_bot.cogs import (
    GuildConfig,
    HWInfo,
    HWList,
    HWManagement,
    HWNotify,
    HWStatistic,
)
from homework_bot.utils import pretty_time

logger = logging.getLogger("homework_bot")

load_dotenv()

API_URL = "http://localhost:5000"

key = os.getenv("KEY").encode("utf8")

main_bot = MainBot(
    status=discord.Status.dnd,
    activity=discord.Game("with your homework"),
    intents=discord.Intents.default(),
    debug_guilds=[856028294645153802],
)


@main_bot.event
async def on_application_command_error(
    ctx: ApplicationContext, error: DiscordException
):
    try:
        if isinstance(error, (commands.CheckFailure)):
            if isinstance(error, (commands.MissingPermissions)):
                return
            
            logger.error(f"An error occurred: {error}")
            return

        if isinstance(error.__cause__, (ConnectError)):
            logger.info("The API is down")
            await responses.normal_response(
                ctx,
                "**The API is down**\nPlease try again later",
                color=Colour.red(),
            )
            return

        logger.error(f"An error occurred: {error}")
        if error.__cause__ is None:
            logger.error(str().join(traceback.format_tb(error.__traceback__)))
        else:
            logger.error(str().join(traceback.format_tb(error.__cause__.__traceback__)))

        await responses.normal_response(
            ctx,
            f"**An internal error occurred**\n```py\n{error}```",
            color=Colour.red(),
        )
    except DiscordException:
        pass


@Cache(maxsize=1, ttl=60).memoize()
async def measure_api_latency():
    logger.info("Measuring API latency...")
    latency_list = []

    for _ in range(5):
        start = time.monotonic()
        try:
            await main_bot.http_client.get(API_URL)
        except ConnectError:
            return None
        latency_list.append(time.monotonic() - start)

    return sum(latency_list) / len(latency_list)


@main_bot.slash_command()
async def ping(ctx: ApplicationContext):
    api_latency = await measure_api_latency()

    desc = f"""
    ```ml
    Websocket ::  {pretty_time(main_bot.latency)}
    API       ::  {pretty_time(api_latency) if api_latency is not None else "N/A"}
    ```
    """
    # remove tabs at the start of each line
    desc = re.sub(r"^\s+", "", desc, flags=re.MULTILINE)
    embed = Embed(title="Pong! Latencies", color=main_bot.main_color)
    embed.description = desc
    await ctx.respond(embed=embed)


main_bot.add_cog(GuildConfig(main_bot, key))
main_bot.add_cog(HWList(main_bot, API_URL))
main_bot.add_cog(HWInfo(main_bot, API_URL))
main_bot.add_cog(HWNotify(main_bot, API_URL))
main_bot.add_cog(HWStatistic(main_bot, API_URL))
main_bot.add_cog(HWManagement(main_bot, key, API_URL))

apply_multicog(main_bot)

main_bot.run(os.getenv("TOKEN"))
