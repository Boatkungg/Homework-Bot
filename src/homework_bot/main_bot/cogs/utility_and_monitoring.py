import asyncio
import logging
import platform
import re
import time
import traceback

import psutil
from cacheout import Cache
from discord import ApplicationContext, Colour, DiscordException, Embed
from discord.ext import commands
from httpx import ConnectError

from homework_bot import responses
from homework_bot.utils import pretty_time

logger = logging.getLogger(__name__)


@Cache(maxsize=1, ttl=60).memoize()
async def measure_api_latency(http_client, api_url):
    logger.info("Measuring API latency...")
    latency_list = []

    for _ in range(5):
        start = time.monotonic()
        try:
            await http_client.get(api_url)
        except ConnectError:
            return None
        latency_list.append(time.monotonic() - start)

    return sum(latency_list) / len(latency_list)


class UtilityAndMonitoring(commands.Cog):
    def __init__(self, bot, api_url):
        self.bot = bot
        self.api_url = api_url

    @commands.Cog.listener()
    async def on_application_command_error(
        self, ctx: ApplicationContext, error: DiscordException
    ):
        try:
            if isinstance(error, (commands.CheckFailure)):
                if isinstance(error, (commands.MissingPermissions, commands.NotOwner)):
                    return

                logger.error("An error occurred: %s", error)
                return

            if isinstance(error.__cause__, (ConnectError)):
                logger.warning("The API is down")
                await responses.normal_response(
                    ctx,
                    "**The API is down**\nPlease try again later",
                    color=Colour.red(),
                )
                return

            logger.error("An error occurred: %s", error)
            if error.__cause__ is None:
                logger.error("%s", "".join(traceback.format_tb(error.__traceback__)))
            else:
                logger.error(
                    "%s", "".join(traceback.format_tb(error.__cause__.__traceback__))
                )

            await responses.normal_response(
                ctx,
                f"**An internal error occurred**\n```py\n{error}```",
                color=Colour.red(),
            )
        except DiscordException:
            pass

    @commands.slash_command(description="Get the latency of systems")
    async def ping(self, ctx: ApplicationContext):
        api_latency = await measure_api_latency(self.bot.http_client, self.api_url)

        desc = f"""
        ```ml
        Websocket ::  {pretty_time(self.bot.latency)}
        API       ::  {pretty_time(api_latency) if api_latency is not None else "N/A"}
        ```
        """
        # remove tabs at the start of each line
        desc = re.sub(r"^\s+", "", desc, flags=re.MULTILINE)
        embed = Embed(title="Pong! Latencies", color=self.bot.main_color)
        embed.description = desc
        await ctx.respond(embed=embed)

    @commands.slash_command(description="Get the status of the bot")
    async def status(self, ctx: ApplicationContext):
        await ctx.defer()

        # make cpu_percent non-blocking
        psutil.cpu_percent()
        await asyncio.sleep(0.5)

        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent

        embed = Embed(
            title="server's stats",
            color=self.bot.main_color,
        )

        # info
        info = f"""
        **Python version** `{platform.python_version()}`
        **OS** `{platform.system()}`
        **CPU** `{platform.processor()}`
        **CPU count** `{psutil.cpu_count()}`
        **RAM** `{round(psutil.virtual_memory().total / (1024.0 **3))} GB`
        """

        # remove tabs at the start of each line
        info = re.sub(r"^\s+", "", info, flags=re.MULTILINE)

        embed.description = info

        # usage
        embed.add_field(name="CPU usage 🖥️", value=f"{cpu_usage}%")
        embed.add_field(name="RAM usage 💾", value=f"{ram_usage}%")

        await ctx.respond(embed=embed)
