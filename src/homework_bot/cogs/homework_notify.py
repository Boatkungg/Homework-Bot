from dataclasses import dataclass
from typing import Optional, Literal
import datetime

import discord
from discord import ApplicationContext, Embed, Interaction, ui
from discord.commands import SlashCommandGroup
from discord.ext import commands, tasks

from homework_bot import api_operations, db_operations

timezone = datetime.timezone(datetime.timedelta(hours=7))


class HWNotify(commands.Cog):
    def __init__(self, bot, api_url):
        self.bot = bot
        self.api_url = api_url

    notify = SlashCommandGroup("notify", "Commands for notify")

    @commands.guild_only()
    @notify.command()
    async def set(self, ctx: ApplicationContext, schedule: Literal["disable", "all", "daily", "due"]):
        pass
    
    @commands.guild_only()
    @notify.command()
    async def setting(self, ctx: ApplicationContext, before_due: int):
        pass
    
    @tasks.loop(time=datetime.time(hour=18, tzinfo=timezone))
    async def send_notify(self):
        pass