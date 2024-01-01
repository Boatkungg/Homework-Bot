import platform
import re
import asyncio

import psutil
from discord import ApplicationContext, Embed
from discord.commands import SlashCommandGroup
from discord.ext import commands

from homework_bot import responses, utils


class U_UtilityAndMonitoring(commands.Cog):
    def __init__(self, bot, api_url):
        self.bot = bot
        self.api_url = api_url

    utility = SlashCommandGroup("utility", "Utility commands")

    @utility.command(description="Get bot's latency")
    @commands.is_owner()
    async def ping(self, ctx: ApplicationContext):
        await ctx.defer(ephemeral=True)
        await responses.normal_response(
            ctx,
            f"**Bot's latency** `{utils.pretty_time(self.bot.latency)}`",
            color=self.bot.main_color,
        )

    async def stat(self, ctx: ApplicationContext):
        await ctx.defer(ephemeral=True)

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
