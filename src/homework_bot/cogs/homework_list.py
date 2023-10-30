from typing import Optional

from discord import ApplicationContext
from discord.ext import commands


class HWList(commands.Cog):
    def __init__(self, bot, api_url):
        self.bot = bot
        self.api_url = api_url

    @commands.guild_only()
    @commands.slash_command()
    async def list(
        self,
        ctx: ApplicationContext,
        assigned_before: Optional[str],
        assigned_after: Optional[str],
        due_before: Optional[str],
        due_after: Optional[str],
    ):
        pass
