import logging
import os
import time
import traceback

import discord
from discord import ApplicationContext, Colour, DiscordException, Embed
from dotenv import load_dotenv
from httpx import ConnectError

from homework_bot import responses
from homework_bot.bot import MainBot
from homework_bot.cogs import GuildConfig, HWInfo, HWList, HWManagement, HWNotify
from homework_bot.utils import pretty_time

logger = logging.getLogger(__name__)

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
    logger.error(f"An error occurred: {error}")
    logger.error(traceback.extract_tb(error.__cause__.__traceback__))
    await responses.normal_response(
        ctx,
        f"**An internal error occurred**\n```py\n{error}```",
        color=Colour.red(),
    )


async def measure_api_latency():
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
    desc = "```\n"
    desc += f"Websocket :  {pretty_time(main_bot.latency)}\n"

    if api_latency is None:
        desc += "API: N/A"
    else:
        desc += f"API\t   :  {pretty_time(api_latency)}\n"

    desc += "```"
    embed = Embed(title="Pong! Latencies", color=main_bot.main_color)
    embed.description = desc
    await ctx.respond(embed=embed)


main_bot.add_cog(HWManagement(main_bot, key, API_URL))
main_bot.add_cog(GuildConfig(main_bot, key))
main_bot.add_cog(HWList(main_bot, API_URL))
main_bot.add_cog(HWInfo(main_bot, API_URL))
main_bot.add_cog(HWNotify(main_bot, API_URL))

main_bot.run(os.getenv("TOKEN"))
